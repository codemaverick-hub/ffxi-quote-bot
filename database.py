import asyncpg
import os
from datetime import date
from typing import Optional


class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(os.getenv("DATABASE_URL"), min_size=1, max_size=5)
        await self._setup_tables()

    async def _setup_tables(self):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS server_config (
                    guild_id             BIGINT PRIMARY KEY,
                    quotes_channel_id    BIGINT   DEFAULT NULL,
                    qotd_channel_id      BIGINT   DEFAULT NULL,
                    qotd_time            VARCHAR(5) DEFAULT '09:00',
                    message_frequency    FLOAT    DEFAULT 0.01,
                    meme_ratio           FLOAT    DEFAULT 0.15,
                    blacklisted_channels BIGINT[] DEFAULT ARRAY[]::BIGINT[],
                    last_qotd_date       DATE     DEFAULT NULL,
                    created_at           TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            await conn.execute("ALTER TABLE server_config ADD COLUMN IF NOT EXISTS meme_ratio FLOAT DEFAULT 0.15")
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS user_scores (
                    guild_id         BIGINT NOT NULL,
                    user_id          BIGINT NOT NULL,
                    points           INT    DEFAULT 0,
                    correct_guesses  INT    DEFAULT 0,
                    PRIMARY KEY (guild_id, user_id)
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS recent_quotes (
                    id         SERIAL PRIMARY KEY,
                    guild_id   BIGINT NOT NULL,
                    quote_hash VARCHAR(16) NOT NULL,
                    shown_at   TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_recent_quotes_guild
                ON recent_quotes(guild_id, shown_at DESC)
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS quote_votes (
                    guild_id   BIGINT NOT NULL,
                    quote_hash VARCHAR(16) NOT NULL,
                    upvotes    INT DEFAULT 0,
                    downvotes  INT DEFAULT 0,
                    PRIMARY KEY (guild_id, quote_hash)
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS quote_verifications (
                    quote_hash  VARCHAR(16) NOT NULL,
                    guild_id    BIGINT      NOT NULL,
                    speaker     VARCHAR(100),
                    quote_text  TEXT,
                    source_tag  VARCHAR(50),
                    confirmed   INT  DEFAULT 0,
                    disputed    INT  DEFAULT 0,
                    PRIMARY KEY (quote_hash, guild_id)
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS bank_items (
                    id          SERIAL PRIMARY KEY,
                    name        VARCHAR(100) NOT NULL,
                    description TEXT         NOT NULL,
                    cost        INT          NOT NULL,
                    active      BOOLEAN      DEFAULT TRUE,
                    created_at  TIMESTAMPTZ  DEFAULT NOW()
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS bank_purchases (
                    id           SERIAL PRIMARY KEY,
                    guild_id     BIGINT       NOT NULL,
                    user_id      BIGINT       NOT NULL,
                    item_id      INT          NOT NULL,
                    item_name    VARCHAR(100) NOT NULL,
                    cost         INT          NOT NULL,
                    fulfilled    BOOLEAN      DEFAULT FALSE,
                    purchased_at TIMESTAMPTZ  DEFAULT NOW()
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS memes (
                    id         SERIAL PRIMARY KEY,
                    guild_id   BIGINT       NOT NULL,
                    url        TEXT         NOT NULL,
                    title      VARCHAR(200) DEFAULT NULL,
                    active     BOOLEAN      DEFAULT TRUE,
                    added_at   TIMESTAMPTZ  DEFAULT NOW()
                )
            """)
            # NOTE: No default bank items seeded — use /bank_add_item to add custom rewards

    # Server Config
    async def get_server_config(self, guild_id: int) -> dict:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM server_config WHERE guild_id = $1", guild_id)
            return dict(row) if row else {"guild_id": guild_id, "message_frequency": 0.01, "meme_ratio": 0.15}

    async def upsert_server_config(self, guild_id: int, **kwargs):
        if not kwargs: return
        cols    = ", ".join(kwargs.keys())
        vals    = ", ".join(f"${i+2}" for i in range(len(kwargs)))
        updates = ", ".join(f"{k} = EXCLUDED.{k}" for k in kwargs.keys())
        await self.pool.execute(
            f"INSERT INTO server_config (guild_id, {cols}) VALUES ($1, {vals}) "
            f"ON CONFLICT (guild_id) DO UPDATE SET {updates}",
            guild_id, *kwargs.values()
        )

    async def add_blacklist_channel(self, guild_id: int, channel_id: int):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO server_config (guild_id, blacklisted_channels) VALUES ($1, ARRAY[$2]::BIGINT[])
                ON CONFLICT (guild_id) DO UPDATE
                SET blacklisted_channels = array_append(
                    COALESCE(server_config.blacklisted_channels, ARRAY[]::BIGINT[]), $2
                )
                WHERE NOT ($2 = ANY(COALESCE(server_config.blacklisted_channels, ARRAY[]::BIGINT[])))
            """, guild_id, channel_id)

    async def remove_blacklist_channel(self, guild_id: int, channel_id: int):
        await self.pool.execute(
            "UPDATE server_config SET blacklisted_channels = array_remove(blacklisted_channels, $2) WHERE guild_id = $1",
            guild_id, channel_id
        )

    # QOTD
    async def get_qotd_configs(self) -> list[dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM server_config WHERE qotd_channel_id IS NOT NULL")
            return [dict(r) for r in rows]

    async def mark_qotd_posted(self, guild_id: int, today: date):
        await self.pool.execute("UPDATE server_config SET last_qotd_date = $2 WHERE guild_id = $1", guild_id, today)

    async def get_pending_linkshell_user(self, guild_id: int) -> Optional[int]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT user_id FROM bank_purchases
                WHERE guild_id = $1 AND item_name = 'Linkshell Pearl' AND fulfilled = FALSE
                ORDER BY purchased_at ASC LIMIT 1
            """, guild_id)
            return row["user_id"] if row else None

    async def fulfill_linkshell_pearl(self, guild_id: int, user_id: int):
        await self.pool.execute("""
            UPDATE bank_purchases SET fulfilled = TRUE
            WHERE guild_id = $1 AND user_id = $2 AND item_name = 'Linkshell Pearl' AND fulfilled = FALSE
        """, guild_id, user_id)

    # Recent Quotes
    async def get_recent_hashes(self, guild_id: int, limit: int = 30) -> set[str]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT quote_hash FROM recent_quotes WHERE guild_id = $1 ORDER BY shown_at DESC LIMIT $2
            """, guild_id, limit)
            return {r["quote_hash"] for r in rows}

    async def add_recent_quote(self, guild_id: int, quote_hash: str):
        async with self.pool.acquire() as conn:
            await conn.execute("INSERT INTO recent_quotes (guild_id, quote_hash) VALUES ($1, $2)", guild_id, quote_hash)
            await conn.execute("""
                DELETE FROM recent_quotes WHERE id IN (
                    SELECT id FROM recent_quotes WHERE guild_id = $1 ORDER BY shown_at DESC OFFSET 50
                )
            """, guild_id)

    # Quote Votes
    async def add_vote(self, guild_id: int, quote_hash: str, is_upvote: bool):
        col = "upvotes" if is_upvote else "downvotes"
        await self.pool.execute(f"""
            INSERT INTO quote_votes (guild_id, quote_hash, {col}) VALUES ($1, $2, 1)
            ON CONFLICT (guild_id, quote_hash) DO UPDATE SET {col} = quote_votes.{col} + 1
        """, guild_id, quote_hash)

    # Source Verifications
    async def ensure_verification_record(self, quote_hash: str, guild_id: int, speaker: str, quote_text: str, source_tag: str):
        await self.pool.execute("""
            INSERT INTO quote_verifications (quote_hash, guild_id, speaker, quote_text, source_tag)
            VALUES ($1, $2, $3, $4, $5) ON CONFLICT (quote_hash, guild_id) DO NOTHING
        """, quote_hash, guild_id, speaker, quote_text, source_tag)

    async def add_verification(self, quote_hash: str, guild_id: int, is_confirm: bool):
        col = "confirmed" if is_confirm else "disputed"
        await self.pool.execute(f"""
            INSERT INTO quote_verifications (quote_hash, guild_id, {col}) VALUES ($1, $2, 1)
            ON CONFLICT (quote_hash, guild_id) DO UPDATE SET {col} = quote_verifications.{col} + 1
        """, quote_hash, guild_id)

    async def get_verification_counts(self, quote_hash: str, guild_id: int) -> dict:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT confirmed, disputed FROM quote_verifications WHERE quote_hash = $1 AND guild_id = $2",
                quote_hash, guild_id
            )
            return dict(row) if row else {"confirmed": 0, "disputed": 0}

    async def get_disputed_quotes(self, guild_id: int, limit: int = 15) -> list[dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM quote_verifications WHERE guild_id = $1 AND disputed > 0
                ORDER BY disputed DESC, confirmed ASC LIMIT $2
            """, guild_id, limit)
            return [dict(r) for r in rows]

    async def get_verified_quotes(self, guild_id: int, limit: int = 15) -> list[dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM quote_verifications WHERE guild_id = $1 AND confirmed >= 3
                ORDER BY confirmed DESC LIMIT $2
            """, guild_id, limit)
            return [dict(r) for r in rows]

    # User Scores
    async def get_user_score(self, guild_id: int, user_id: int) -> Optional[dict]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM user_scores WHERE guild_id = $1 AND user_id = $2", guild_id, user_id)
            return dict(row) if row else None

    async def add_points(self, guild_id: int, user_id: int, points: int, correct: bool = False):
        await self.pool.execute("""
            INSERT INTO user_scores (guild_id, user_id, points, correct_guesses) VALUES ($1, $2, $3, $4)
            ON CONFLICT (guild_id, user_id) DO UPDATE
            SET points = GREATEST(0, user_scores.points + $3),
                correct_guesses = user_scores.correct_guesses + $4
        """, guild_id, user_id, points, 1 if correct else 0)

    async def get_user_balance(self, guild_id: int, user_id: int) -> int:
        val = await self.pool.fetchval("SELECT points FROM user_scores WHERE guild_id = $1 AND user_id = $2", guild_id, user_id)
        return val or 0

    async def get_leaderboard(self, guild_id: int, limit: int = 10) -> list[dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT user_id, points, correct_guesses FROM user_scores
                WHERE guild_id = $1 ORDER BY points DESC LIMIT $2
            """, guild_id, limit)
            return [dict(r) for r in rows]

    # Guild Bank
    async def get_bank_items(self) -> list[dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM bank_items WHERE active = TRUE ORDER BY cost ASC")
            return [dict(r) for r in rows]

    async def get_bank_item(self, item_id: int) -> Optional[dict]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM bank_items WHERE id = $1", item_id)
            return dict(row) if row else None

    async def add_bank_item(self, name: str, description: str, cost: int) -> int:
        return await self.pool.fetchval(
            "INSERT INTO bank_items (name, description, cost) VALUES ($1, $2, $3) RETURNING id",
            name, description, cost
        )

    async def toggle_bank_item(self, item_id: int, active: bool):
        await self.pool.execute("UPDATE bank_items SET active = $2 WHERE id = $1", item_id, active)

    async def purchase_item(self, guild_id: int, user_id: int, item_id: int, item_name: str, cost: int) -> int:
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE user_scores SET points = points - $3 WHERE guild_id = $1 AND user_id = $2",
                guild_id, user_id, cost
            )
            return await conn.fetchval("""
                INSERT INTO bank_purchases (guild_id, user_id, item_id, item_name, cost)
                VALUES ($1, $2, $3, $4, $5) RETURNING id
            """, guild_id, user_id, item_id, item_name, cost)

    async def get_pending_purchases(self, guild_id: int) -> list[dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM bank_purchases WHERE guild_id = $1 AND fulfilled = FALSE ORDER BY purchased_at ASC
            """, guild_id)
            return [dict(r) for r in rows]

    async def fulfill_purchase(self, purchase_id: int, guild_id: int) -> Optional[dict]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                UPDATE bank_purchases SET fulfilled = TRUE
                WHERE id = $1 AND guild_id = $2 AND fulfilled = FALSE RETURNING *
            """, purchase_id, guild_id)
            return dict(row) if row else None

    # Memes
    async def get_memes(self, guild_id: int) -> list[dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM memes WHERE guild_id = $1 AND active = TRUE ORDER BY added_at ASC", guild_id)
            return [dict(r) for r in rows]

    async def add_meme(self, guild_id: int, url: str, title: str = None) -> int:
        return await self.pool.fetchval(
            "INSERT INTO memes (guild_id, url, title) VALUES ($1, $2, $3) RETURNING id",
            guild_id, url, title
        )

    async def remove_meme(self, meme_id: int, guild_id: int) -> bool:
        result = await self.pool.execute(
            "UPDATE memes SET active = FALSE WHERE id = $1 AND guild_id = $2", meme_id, guild_id
        )
        return result == "UPDATE 1"

    async def get_meme_list(self, guild_id: int) -> list[dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM memes WHERE guild_id = $1 ORDER BY active DESC, added_at ASC", guild_id)
            return [dict(r) for r in rows]
