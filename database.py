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
                    blacklisted_channels BIGINT[] DEFAULT ARRAY[]::BIGINT[],
                    last_qotd_date       DATE     DEFAULT NULL,
                    created_at           TIMESTAMPTZ DEFAULT NOW()
                )
            """)
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
                    id          SERIAL PRIMARY KEY,
                    guild_id    BIGINT       NOT NULL,
                    user_id     BIGINT       NOT NULL,
                    item_id     INT          NOT NULL,
                    item_name   VARCHAR(100) NOT NULL,
                    cost        INT          NOT NULL,
                    fulfilled   BOOLEAN      DEFAULT FALSE,
                    purchased_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            # Seed default bank items once
            count = await conn.fetchval("SELECT COUNT(*) FROM bank_items")
            if count == 0:
                await conn.executemany(
                    "INSERT INTO bank_items (name, description, cost) VALUES ($1, $2, $3)",
                    [
                        ("Adventurer's Title",
                         "Receive the honorary 'Famous Adventurer' title — admins will assign you a special role.",
                         50),
                        ("Linkshell Pearl",
                         "Your name gets featured in the next Quote of the Day post.",
                         100),
                        ("Claim Flag",
                         "Bot announces that you have claimed an NM of your choice. Glory is yours.",
                         150),
                        ("Mog Bonanza Ticket",
                         "Enter a raffle for a prize chosen by your server admins. Kupo!",
                         300),
                        ("Dynamis Access",
                         "Receive the legendary 'Dynamis Veteran' recognition — admins will honor you.",
                         500),
                    ]
                )

    # ── Server Config ──────────────────────────────────────────────────────────

    async def get_server_config(self, guild_id: int) -> dict:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM server_config WHERE guild_id = $1", guild_id
            )
            return dict(row) if row else {"guild_id": guild_id, "message_frequency": 0.01}

    async def upsert_server_config(self, guild_id: int, **kwargs):
        if not kwargs:
            return
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
                INSERT INTO server_config (guild_id, blacklisted_channels)
                VALUES ($1, ARRAY[$2]::BIGINT[])
                ON CONFLICT (guild_id) DO UPDATE
                SET blacklisted_channels = array_append(
                    COALESCE(server_config.blacklisted_channels, ARRAY[]::BIGINT[]), $2
                )
                WHERE NOT ($2 = ANY(COALESCE(server_config.blacklisted_channels, ARRAY[]::BIGINT[])))
            """, guild_id, channel_id)

    async def remove_blacklist_channel(self, guild_id: int, channel_id: int):
        await self.pool.execute(
            "UPDATE server_config SET blacklisted_channels = array_remove(blacklisted_channels, $2) "
            "WHERE guild_id = $1",
            guild_id, channel_id
        )

    # ── QOTD ──────────────────────────────────────────────────────────────────

    async def get_qotd_configs(self) -> list[dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM server_config WHERE qotd_channel_id IS NOT NULL"
            )
            return [dict(r) for r in rows]

    async def mark_qotd_posted(self, guild_id: int, today: date):
        await self.pool.execute(
            "UPDATE server_config SET last_qotd_date = $2 WHERE guild_id = $1",
            guild_id, today
        )

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
            WHERE guild_id = $1 AND user_id = $2
              AND item_name = 'Linkshell Pearl' AND fulfilled = FALSE
        """, guild_id, user_id)

    # ── Recent Quotes (no-repeat memory) ──────────────────────────────────────

    async def get_recent_hashes(self, guild_id: int, limit: int = 30) -> set[str]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT quote_hash FROM recent_quotes
                WHERE guild_id = $1 ORDER BY shown_at DESC LIMIT $2
            """, guild_id, limit)
            return {r["quote_hash"] for r in rows}

    async def add_recent_quote(self, guild_id: int, quote_hash: str):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO recent_quotes (guild_id, quote_hash) VALUES ($1, $2)",
                guild_id, quote_hash
            )
            # Keep only last 50 per guild
            await conn.execute("""
                DELETE FROM recent_quotes WHERE id IN (
                    SELECT id FROM recent_quotes WHERE guild_id = $1
                    ORDER BY shown_at DESC OFFSET 50
                )
            """, guild_id)

    # ── Quote Voting ───────────────────────────────────────────────────────────

    async def add_vote(self, guild_id: int, quote_hash: str, is_upvote: bool):
        col = "upvotes" if is_upvote else "downvotes"
        await self.pool.execute(f"""
            INSERT INTO quote_votes (guild_id, quote_hash, {col})
            VALUES ($1, $2, 1)
            ON CONFLICT (guild_id, quote_hash) DO UPDATE
            SET {col} = quote_votes.{col} + 1
        """, guild_id, quote_hash)

    # ── User Scores & Gil ─────────────────────────────────────────────────────

    async def get_user_score(self, guild_id: int, user_id: int) -> Optional[dict]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM user_scores WHERE guild_id = $1 AND user_id = $2",
                guild_id, user_id
            )
            return dict(row) if row else None

    async def add_points(self, guild_id: int, user_id: int, points: int, correct: bool = False):
        await self.pool.execute("""
            INSERT INTO user_scores (guild_id, user_id, points, correct_guesses)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (guild_id, user_id) DO UPDATE
            SET points          = GREATEST(0, user_scores.points + $3),
                correct_guesses = user_scores.correct_guesses + $4
        """, guild_id, user_id, points, 1 if correct else 0)

    async def get_user_balance(self, guild_id: int, user_id: int) -> int:
        val = await self.pool.fetchval(
            "SELECT points FROM user_scores WHERE guild_id = $1 AND user_id = $2",
            guild_id, user_id
        )
        return val or 0

    async def get_leaderboard(self, guild_id: int, limit: int = 10) -> list[dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT user_id, points, correct_guesses FROM user_scores
                WHERE guild_id = $1 ORDER BY points DESC LIMIT $2
            """, guild_id, limit)
            return [dict(r) for r in rows]

    # ── Guild Bank ────────────────────────────────────────────────────────────

    async def get_bank_items(self) -> list[dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM bank_items WHERE active = TRUE ORDER BY cost ASC"
            )
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
        await self.pool.execute(
            "UPDATE bank_items SET active = $2 WHERE id = $1", item_id, active
        )

    async def purchase_item(self, guild_id: int, user_id: int, item_id: int,
                             item_name: str, cost: int) -> int:
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
                SELECT * FROM bank_purchases
                WHERE guild_id = $1 AND fulfilled = FALSE
                ORDER BY purchased_at ASC
            """, guild_id)
            return [dict(r) for r in rows]

    async def fulfill_purchase(self, purchase_id: int, guild_id: int) -> Optional[dict]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                UPDATE bank_purchases SET fulfilled = TRUE
                WHERE id = $1 AND guild_id = $2 AND fulfilled = FALSE
                RETURNING *
            """, purchase_id, guild_id)
            return dict(row) if row else None
