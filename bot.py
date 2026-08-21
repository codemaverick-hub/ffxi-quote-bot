import os
import random
import asyncio
import hashlib
from datetime import datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv

from database import Database
from quotes import (
    get_quote_by_category, format_quote,
    ALL_QUOTES, WEIGHTED_POOL, EXPANSION_QUOTES,
    get_seasonal_pool, FAN,
)

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ─────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────

CHANNEL_COOLDOWN   = 300
GUESS_TIMEOUT      = 60
GUESS_POINTS       = 10
REACT_QUOTE_EMOJI  = "📜"
VOTE_UP_EMOJI      = "👍"
VOTE_DOWN_EMOJI    = "👎"
VERIFY_EMOJI       = "🔍"
CONFIRM_EMOJI      = "✅"
DISPUTE_EMOJI      = "❌"
DEFAULT_MEME_RATIO = 0.15

KEYWORD_MAP: dict[str, list[str]] = {
    "moogle":  ["kupo", "mog house", "mog garden", "moogle", "moghouse"],
    "city":    ["jeuno", "bastok", "windurst", "sandoria", "san d'oria", "whitegate", "adoulin", "norg", "selbina", "rabao"],
    "avatar":  ["ifrit", "shiva", "ramuh", "titan", "leviathan", "garuda", "fenrir", "diabolos",
                "carbuncle", "alexander", "odin", "phoenix", "bahamut", "atomos", "avatar", "summon"],
    "nm":      ["absolute virtue", "pandemonium warden", "nidhogg", "fafnir", "kirin",
                "behemoth", "notorious monster", "nm pop", "placeholder"],
    "battle":  ["weaponskill", " ws ", "exp party", "merit", "skillchain", "magic burst", "two-hour"],
    "npc":     ["prishe", "shantotto", "lion", "lilisette", "iroha", "zeid", "gilgamesh", "aphmau"],
    "abyssea": ["abyssea", "atma", "cruor", "visitant", "cavernous maw", "primeval brew"],
    "player":  ["need whm", "need blm", "need brd", "lfp", "looking for party", "seeking"],
}

# ─────────────────────────────────────────────
#  State
# ─────────────────────────────────────────────

db = Database()
channel_cooldowns:    dict[int, datetime] = {}
active_guess_games:   dict[int, dict]     = {}
voted_message_hashes: dict[int, dict]     = {}

# ─────────────────────────────────────────────
#  Bot Setup
# ─────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True
intents.members         = True
intents.voice_states    = True
intents.reactions       = True

bot  = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

def get_hash(speaker: str, quote: str) -> str:
    return hashlib.md5(f"{speaker}:{quote}".encode()).hexdigest()[:16]


async def get_guild_quote(guild_id: int) -> tuple[str, str, str]:
    seasonal = get_seasonal_pool()
    pool     = list(WEIGHTED_POOL)
    if seasonal:
        pool += seasonal * 3
    recent   = await db.get_recent_hashes(guild_id)
    filtered = [(s, q, src) for s, q, src in pool if get_hash(s, q) not in recent]
    if not filtered:
        filtered = pool
    speaker, quote, source = random.choice(filtered)
    await db.add_recent_quote(guild_id, get_hash(speaker, quote))
    return speaker, quote, source


def off_cooldown(channel_id: int) -> bool:
    last = channel_cooldowns.get(channel_id)
    return last is None or (datetime.now() - last).total_seconds() >= CHANNEL_COOLDOWN


def set_cooldown(channel_id: int):
    channel_cooldowns[channel_id] = datetime.now()


def is_blacklisted(config: dict, channel_id: int) -> bool:
    return channel_id in (config.get("blacklisted_channels") or [])


def check_guess(guess: str, speaker: str) -> bool:
    g, s = guess.strip().lower(), speaker.strip().lower()
    return g == s or (len(g) >= 4 and s.startswith(g))


def format_frequency(freq: float) -> str:
    pct = freq * 100
    return f"{pct:.1f}%" if pct < 1 else f"{int(pct)}%"


async def send_quote(channel: discord.abc.Messageable, speaker: str, quote: str, source: str = FAN):
    msg = await channel.send(format_quote(speaker, quote, source))
    h   = get_hash(speaker, quote)
    voted_message_hashes[msg.id] = {"hash": h, "source": source, "speaker": speaker, "quote": quote}
    if len(voted_message_hashes) > 1000:
        del voted_message_hashes[next(iter(voted_message_hashes))]
    await msg.add_reaction(VOTE_UP_EMOJI)
    await msg.add_reaction(VOTE_DOWN_EMOJI)
    await msg.add_reaction(VERIFY_EMOJI)
    return msg


async def send_meme(channel: discord.abc.Messageable, meme: dict):
    embed = discord.Embed(color=0x7b5ea7)
    embed.set_image(url=meme["url"])
    if meme.get("title"):
        embed.title = f"😄 {meme['title']}"
    embed.set_footer(text="React 👍/👎 to rate • /ffxi_meme for another")
    await channel.send(embed=embed)


async def auto_trigger(channel: discord.abc.Messageable, guild_id: int, config: dict,
                        keyword_category: str = None):
    """Post a quote or meme. Uses keyword_category hint if provided."""
    memes      = await db.get_memes(guild_id)
    meme_ratio = config.get("meme_ratio", DEFAULT_MEME_RATIO)
    if memes and random.random() < meme_ratio:
        await send_meme(channel, random.choice(memes))
    elif keyword_category:
        speaker, quote, source = get_quote_by_category(keyword_category)
        await send_quote(channel, speaker, quote, source)
    else:
        speaker, quote, source = await get_guild_quote(guild_id)
        await send_quote(channel, speaker, quote, source)

# ─────────────────────────────────────────────
#  Background Task: Quote of the Day
# ─────────────────────────────────────────────

@tasks.loop(minutes=1)
async def qotd_task():
    now     = datetime.now(timezone.utc)
    configs = await db.get_qotd_configs()
    for cfg in configs:
        try:
            h, m = map(int, (cfg.get("qotd_time") or "09:00").split(":"))
        except Exception:
            continue
        if now.hour != h or now.minute != m:
            continue
        last  = cfg.get("last_qotd_date")
        today = now.date()
        if last and last >= today:
            continue
        channel = bot.get_channel(cfg["qotd_channel_id"])
        if not channel:
            continue
        guild_id            = cfg["guild_id"]
        speaker, quote, src = await get_guild_quote(guild_id)
        featured_uid        = await db.get_pending_linkshell_user(guild_id)
        content = f"🌅 **Quote of the Day — Vana'diel {now.strftime('%B %d')}**\n"
        if featured_uid:
            content += f"*(Featured spot courtesy of <@{featured_uid}>)*\n"
        content += format_quote(speaker, quote, src)
        await channel.send(content)
        await db.mark_qotd_posted(guild_id, today)
        if featured_uid:
            await db.fulfill_linkshell_pearl(guild_id, featured_uid)


@qotd_task.before_loop
async def before_qotd():
    await bot.wait_until_ready()

# ─────────────────────────────────────────────
#  Events
# ─────────────────────────────────────────────

@bot.event
async def on_ready():
    await db.connect()
    await tree.sync()
    qotd_task.start()
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    print("📜 Vana'diel Herald is ready — all systems online!")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or not message.guild:
        return

    guild_id   = message.guild.id
    channel_id = message.channel.id
    content_lc = message.content.lower()
    config     = await db.get_server_config(guild_id)

    # Always process active guess games
    if channel_id in active_guess_games:
        if await _process_guess(message):
            await bot.process_commands(message)
            return

    if is_blacklisted(config, channel_id):
        await bot.process_commands(message)
        return

    qc = config.get("quotes_channel_id")
    if qc and channel_id != qc:
        await bot.process_commands(message)
        return

    # ── Frequency gate applies to ALL triggers ──────────────────────────────
    # Keyword hits influence WHAT quote shows, but frequency controls WHETHER
    # anything shows at all. This ensures set_frequency is respected always.
    freq = config.get("message_frequency", 0.01)

    if off_cooldown(channel_id) and random.random() < freq:
        # Check for keyword match to pick a smarter category
        matched_category = None
        for category, keywords in KEYWORD_MAP.items():
            if any(kw in content_lc for kw in keywords):
                matched_category = category
                break

        await auto_trigger(message.channel, guild_id, config, matched_category)
        set_cooldown(channel_id)

    await bot.process_commands(message)


async def _process_guess(message: discord.Message) -> bool:
    game = active_guess_games.get(message.channel.id)
    if not game or not check_guess(message.content, game["speaker"]):
        return False
    guild_id = message.guild.id
    user_id  = message.author.id
    await db.add_points(guild_id, user_id, GUESS_POINTS, correct=True)
    balance = await db.get_user_balance(guild_id, user_id)
    game["task"].cancel()
    del active_guess_games[message.channel.id]
    await message.channel.send(
        f"✅ **{message.author.display_name}** got it!\n"
        f"The speaker was **{game['speaker']}**!\n"
        f"🪙 +**{GUESS_POINTS} gil** earned! Balance: **{balance} gil**"
    )
    return True


@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    if before.channel is not None or after.channel is None:
        return
    config   = await db.get_server_config(member.guild.id)
    guild_id = member.guild.id
    qc_id    = config.get("quotes_channel_id")
    channel  = member.guild.get_channel(qc_id) if qc_id else None
    if channel is None:
        for ch in member.guild.text_channels:
            if ch.permissions_for(member.guild.me).send_messages and not is_blacklisted(config, ch.id):
                channel = ch
                break
    if channel:
        speaker, quote, source = await get_guild_quote(guild_id)
        await channel.send(
            f"🎺 *{member.display_name} joined **{after.channel.name}**!*\n"
            + format_quote(speaker, quote, source)
        )


@bot.event
async def on_member_join(member: discord.Member):
    config   = await db.get_server_config(member.guild.id)
    guild_id = member.guild.id
    qc_id    = config.get("quotes_channel_id")
    target   = member.guild.get_channel(qc_id) if qc_id else member.guild.system_channel
    if target is None or not target.permissions_for(member.guild.me).send_messages:
        for ch in member.guild.text_channels:
            if ch.permissions_for(member.guild.me).send_messages and not is_blacklisted(config, ch.id):
                target = ch
                break
    if target:
        speaker, quote, source = await get_guild_quote(guild_id)
        await target.send(
            f"🌟 *{member.mention} has arrived in Vana'diel!*\n"
            + format_quote(speaker, quote, source)
        )


@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    if user.bot or not reaction.message.guild:
        return
    emoji    = str(reaction.emoji)
    msg      = reaction.message
    guild_id = msg.guild.id

    if emoji == REACT_QUOTE_EMOJI:
        speaker, quote, source = await get_guild_quote(guild_id)
        await msg.channel.send(format_quote(speaker, quote, source))
        return

    if msg.author != bot.user:
        return

    data = voted_message_hashes.get(msg.id)
    if not data:
        return

    q_hash  = data["hash"]
    source  = data["source"]
    speaker = data["speaker"]
    quote   = data["quote"]

    if emoji in (VOTE_UP_EMOJI, VOTE_DOWN_EMOJI):
        await db.add_vote(guild_id, q_hash, emoji == VOTE_UP_EMOJI)
        return

    if emoji == VERIFY_EMOJI:
        counts = await db.get_verification_counts(q_hash, guild_id)
        await db.ensure_verification_record(q_hash, guild_id, speaker, quote, source)
        source_explanations = {
            "📖 Game Dialogue": "This quote was sourced from confirmed FFXI in-game text or community-verified transcripts.",
            "✍️ Fan Written": "This quote was written in the character's style by the bot author. It is not a direct game transcript.",
            "😄 Community": "This is community-created content — a meme, joke, or fan creation.",
        }
        explanation = source_explanations.get(source, "Source unknown.")
        confirmed, disputed = counts["confirmed"], counts["disputed"]
        if confirmed >= 3:
            status = f"✅ **Community verified** by {confirmed} members"
        elif disputed > confirmed and disputed >= 2:
            status = f"⚠️ **Source disputed** ({disputed} disputed · {confirmed} confirmed)"
        elif confirmed > 0 or disputed > 0:
            status = f"🔍 {confirmed} confirmed · {disputed} disputed"
        else:
            status = "🔍 Not yet verified by the community"
        embed = discord.Embed(
            title="🔍 Source Information", color=0x7b5ea7,
            description=(
                f"**Speaker:** {speaker}\n**Source Tag:** {source}\n\n{explanation}\n\n{status}\n\n"
                f"**React on the original message to vote:**\n"
                f"✅ — Confirm this source tag is accurate\n❌ — Dispute this source tag"
            )
        )
        embed.set_footer(text="Only you can see this. Disappears in 30 seconds.")
        try:
            await msg.channel.send(embed=embed, delete_after=30, reference=msg, mention_author=False)
        except Exception:
            pass
        return

    if emoji == CONFIRM_EMOJI:
        await db.ensure_verification_record(q_hash, guild_id, speaker, quote, source)
        await db.add_verification(q_hash, guild_id, is_confirm=True)
        return

    if emoji == DISPUTE_EMOJI:
        await db.ensure_verification_record(q_hash, guild_id, speaker, quote, source)
        await db.add_verification(q_hash, guild_id, is_confirm=False)
        return

# ─────────────────────────────────────────────
#  Quote Commands
# ─────────────────────────────────────────────

@tree.command(name="ffxi", description="Get a random FFXI quote from Vana'diel!")
async def ffxi_quote(interaction: discord.Interaction):
    speaker, quote, source = await get_guild_quote(interaction.guild_id)
    await interaction.response.send_message(format_quote(speaker, quote, source))
    sent = await interaction.original_response()
    voted_message_hashes[sent.id] = {"hash": get_hash(speaker, quote), "source": source, "speaker": speaker, "quote": quote}
    await sent.add_reaction(VOTE_UP_EMOJI)
    await sent.add_reaction(VOTE_DOWN_EMOJI)
    await sent.add_reaction(VERIFY_EMOJI)


@tree.command(name="ffxi_category", description="Get an FFXI quote from a specific category.")
@app_commands.describe(category="Choose a quote category")
@app_commands.choices(category=[
    app_commands.Choice(name="NPC / Story Quotes",           value="npc"),
    app_commands.Choice(name="Battle Cries & Job Abilities", value="battle"),
    app_commands.Choice(name="Moogle Quips",                 value="moogle"),
    app_commands.Choice(name="Player Emote Flavor",          value="emote"),
    app_commands.Choice(name="Avatar & Summon Quotes",       value="avatar"),
    app_commands.Choice(name="Notorious Monsters",           value="nm"),
    app_commands.Choice(name="City & NPC Flavor",            value="city"),
    app_commands.Choice(name="Player /say Flavor",           value="player"),
    app_commands.Choice(name="Abyssea",                      value="abyssea"),
])
async def ffxi_category(interaction: discord.Interaction, category: app_commands.Choice[str]):
    speaker, quote, source = get_quote_by_category(category.value)
    await interaction.response.send_message(format_quote(speaker, quote, source))


@tree.command(name="ffxi_expansion", description="Get an FFXI quote from a specific expansion.")
@app_commands.describe(expansion="Choose an expansion")
@app_commands.choices(expansion=[
    app_commands.Choice(name="Rise of the Zilart",       value="zilart"),
    app_commands.Choice(name="Chains of Promathia",      value="cop"),
    app_commands.Choice(name="Treasures of Aht Urhgan", value="toau"),
    app_commands.Choice(name="Wings of the Goddess",     value="wotg"),
    app_commands.Choice(name="Seekers of Adoulin",       value="soa"),
    app_commands.Choice(name="Rhapsodies of Vana'diel",  value="rov"),
    app_commands.Choice(name="Abyssea",                  value="abyssea"),
])
async def ffxi_expansion(interaction: discord.Interaction, expansion: app_commands.Choice[str]):
    pool = EXPANSION_QUOTES.get(expansion.value)
    if not pool:
        await interaction.response.send_message("No quotes found for that expansion yet!", ephemeral=True)
        return
    speaker, quote, source = random.choice(pool)
    await interaction.response.send_message(format_quote(speaker, quote, source))


@tree.command(name="ffxi_meme", description="Get a random FFXI community meme!")
async def ffxi_meme(interaction: discord.Interaction):
    memes = await db.get_memes(interaction.guild_id)
    if not memes:
        await interaction.response.send_message(
            "😄 No memes yet! Admins can add them with `/meme_add <url> <title>`.", ephemeral=True
        )
        return
    meme  = random.choice(memes)
    embed = discord.Embed(color=0x7b5ea7)
    embed.set_image(url=meme["url"])
    if meme.get("title"):
        embed.title = f"😄 {meme['title']}"
    embed.set_footer(text="React 👍/👎 to rate • /ffxi_meme for another")
    await interaction.response.send_message(embed=embed)


@tree.command(name="ffxi_sources", description="Show community source verification stats.")
async def ffxi_sources(interaction: discord.Interaction):
    disputed = await db.get_disputed_quotes(interaction.guild_id)
    verified = await db.get_verified_quotes(interaction.guild_id)
    embed = discord.Embed(
        title="🔍 Source Verification Report", color=0x7b5ea7,
        description=(
            "Community votes on quote accuracy.\nReact 🔍 on any quote to see source info and vote.\n\n"
            "📖 Game Dialogue — sourced from in-game text\n"
            "✍️ Fan Written — written in character by bot author\n"
            "😄 Community — memes and fan content"
        )
    )
    if verified:
        embed.add_field(
            name="✅ Community Verified (3+ votes)",
            value="\n".join(f"✅ **{q['speaker']}** — {q['source_tag']} ({q['confirmed']} confirmed)" for q in verified[:8]),
            inline=False
        )
    if disputed:
        embed.add_field(
            name="⚠️ Disputed Sources",
            value="\n".join(f"⚠️ **{q['speaker']}** — {q['source_tag']} ({q['disputed']} disputed · {q['confirmed']} confirmed)" for q in disputed[:8]),
            inline=False
        )
    if not verified and not disputed:
        embed.add_field(name="No votes yet", value="React 🔍 on any quote to get started!", inline=False)
    embed.set_footer(text="3+ confirmations = Verified • More disputes than confirms = Disputed")
    await interaction.response.send_message(embed=embed)


@tree.command(name="ffxi_about", description="Show bot info, quote counts, and current server settings.")
async def ffxi_about(interaction: discord.Interaction):
    config   = await db.get_server_config(interaction.guild_id)
    freq     = config.get("message_frequency", 0.01)
    mr       = config.get("meme_ratio", DEFAULT_MEME_RATIO)
    qc       = config.get("quotes_channel_id")
    qotd_ch  = config.get("qotd_channel_id")
    qotd_t   = config.get("qotd_time", "09:00")
    bl       = config.get("blacklisted_channels") or []
    seasonal = get_seasonal_pool()
    memes    = await db.get_memes(interaction.guild_id)
    embed = discord.Embed(title="📜 Vana'diel Herald — Bot Info", color=0x7b5ea7,
                          description="Authentic FFXI quotes delivered to your Discord server.")
    embed.add_field(name="📊 Quote Pool", value=(
        "NPC / Story: ~75 📖✍️\nBattle Cries: ~95 ✍️\nMoogle Quips: ~30 📖✍️\n"
        "Emote Flavor: ~26 ✍️\nAvatar & Summon: ~80 ✍️\nNMs: ~25 ✍️\n"
        "City & NPC: ~35 📖✍️\nPlayer /say: ~21 ✍️\nAbyssea: ~15 ✍️\n"
        f"Memes: **{len(memes)}** 😄\n**Total: ~400+**"
    ), inline=True)
    embed.add_field(name="⚙️ Server Settings", value=(
        f"Message trigger: **{format_frequency(freq)}**\n"
        f"Meme ratio: **{int(mr*100)}%** of triggers\n"
        f"Quotes channel: {f'<#{qc}>' if qc else 'Any channel'}\n"
        f"QOTD: {f'<#{qotd_ch}> at {qotd_t} UTC' if qotd_ch else 'Not set'}\n"
        f"Blacklisted: {len(bl)} channel(s)\n"
        f"Seasonal: {'✅ Active' if seasonal else '—'}\n"
        f"Cooldown: {CHANNEL_COOLDOWN//60} min per channel"
    ), inline=True)
    embed.add_field(name="🏷️ Source Tags", value=(
        "📖 Game Dialogue — confirmed in-game text\n"
        "✍️ Fan Written — written in character\n"
        "😄 Community — memes & fan content\n\n"
        "React 🔍 on quotes to see source + vote ✅/❌"
    ), inline=False)
    await interaction.response.send_message(embed=embed)

# ─────────────────────────────────────────────
#  Guess the Speaker
# ─────────────────────────────────────────────

@tree.command(name="ffxi_guess", description="Start a Guess the Speaker game! First correct answer wins gil.")
async def ffxi_guess(interaction: discord.Interaction):
    cid = interaction.channel_id
    if cid in active_guess_games:
        await interaction.response.send_message("⚔️ A game is already running here!", ephemeral=True)
        return
    pool           = [(s, q) for s, q, _ in ALL_QUOTES if s not in ("Adventurer",)]
    speaker, quote = random.choice(pool)
    embed = discord.Embed(
        title="🎲 Guess the Speaker!",
        description=(f'*"{quote}"*\n\n**Who said this?** Type your answer!\n⏱ **{GUESS_TIMEOUT}s** · Prize: **{GUESS_POINTS} gil** 🪙'),
        color=0xf0c060
    )
    embed.set_footer(text="Partial names accepted if at least 4 characters.")
    await interaction.response.send_message(embed=embed)

    async def timeout():
        await asyncio.sleep(GUESS_TIMEOUT)
        if cid in active_guess_games:
            del active_guess_games[cid]
            await interaction.channel.send(f"⏰ Time's up! The speaker was **{speaker}**. Kupo!")

    active_guess_games[cid] = {"speaker": speaker, "quote": quote, "task": asyncio.create_task(timeout())}

# ─────────────────────────────────────────────
#  Leaderboard
# ─────────────────────────────────────────────

@tree.command(name="leaderboard", description="Show the top Guess the Speaker scorers.")
async def leaderboard(interaction: discord.Interaction):
    rows = await db.get_leaderboard(interaction.guild_id)
    if not rows:
        await interaction.response.send_message("No scores yet! Start with `/ffxi_guess`.", ephemeral=True)
        return
    medals = ["🥇", "🥈", "🥉"]
    lines  = []
    for i, r in enumerate(rows):
        medal  = medals[i] if i < 3 else f"**{i+1}.**"
        member = interaction.guild.get_member(r["user_id"])
        name   = member.display_name if member else f"User {r['user_id']}"
        lines.append(f"{medal} **{name}** — {r['points']} gil 🪙 · {r['correct_guesses']} correct")
    embed = discord.Embed(title="🏆 Vana'diel Herald Leaderboard", color=0xf0c060, description="\n".join(lines))
    embed.set_footer(text="Earn gil by winning Guess the Speaker. Spend it at /bank_shop.")
    await interaction.response.send_message(embed=embed)

# ─────────────────────────────────────────────
#  Guild Bank
# ─────────────────────────────────────────────

@tree.command(name="bank_balance", description="Check your gil balance.")
async def bank_balance(interaction: discord.Interaction):
    balance = await db.get_user_balance(interaction.guild_id, interaction.user.id)
    score   = await db.get_user_score(interaction.guild_id, interaction.user.id)
    correct = score.get("correct_guesses", 0) if score else 0
    await interaction.response.send_message(
        f"🪙 **{interaction.user.display_name}'s Account**\nBalance: **{balance} gil**\n"
        f"Correct guesses: **{correct}**", ephemeral=True
    )


@tree.command(name="bank_shop", description="Browse the Guild Bank shop.")
async def bank_shop(interaction: discord.Interaction):
    items   = await db.get_bank_items()
    balance = await db.get_user_balance(interaction.guild_id, interaction.user.id)
    if not items:
        await interaction.response.send_message("The Guild Bank shop is currently empty. Check back soon!", ephemeral=True)
        return
    embed = discord.Embed(title="🏦 Guild Bank — Shop",
                          description=f"Your balance: **{balance} gil** 🪙\nUse `/bank_buy <item_id>` to purchase.",
                          color=0xc8821a)
    for item in items:
        embed.add_field(name=f"`#{item['id']}` {item['name']} — {item['cost']} gil {'✅' if balance >= item['cost'] else '❌'}",
                        value=item["description"], inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="bank_buy", description="Purchase an item from the Guild Bank.")
@app_commands.describe(item_id="The item ID from /bank_shop")
async def bank_buy(interaction: discord.Interaction, item_id: int):
    guild_id, user_id = interaction.guild_id, interaction.user.id
    item = await db.get_bank_item(item_id)
    if not item or not item["active"]:
        await interaction.response.send_message("Item not found or unavailable.", ephemeral=True)
        return
    balance = await db.get_user_balance(guild_id, user_id)
    if balance < item["cost"]:
        await interaction.response.send_message(f"❌ Need **{item['cost']} gil**, you have **{balance}**.", ephemeral=True)
        return
    purchase_id = await db.purchase_item(guild_id, user_id, item_id, item["name"], item["cost"])
    new_balance = await db.get_user_balance(guild_id, user_id)
    await interaction.response.send_message(
        f"✅ Purchased **{item['name']}** for **{item['cost']} gil**!\nRemaining: **{new_balance} gil** · ID `#{purchase_id}`",
        ephemeral=True
    )
    config    = await db.get_server_config(guild_id)
    notify_ch = interaction.guild.get_channel(config.get("quotes_channel_id") or 0)
    if notify_ch:
        await notify_ch.send(f"🏦 {interaction.user.mention} purchased **{item['name']}** (`#{purchase_id}`). Admins: `/bank_fulfill {purchase_id}`")

# ─────────────────────────────────────────────
#  Admin Commands
# ─────────────────────────────────────────────

def admin_check():
    async def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.manage_guild
    return app_commands.check(predicate)


@tree.command(name="set_quotes_channel", description="[Admin] Set the channel for auto-quotes.")
@app_commands.describe(channel="Target channel (leave empty to allow all)")
@admin_check()
async def set_quotes_channel(interaction: discord.Interaction, channel: discord.TextChannel = None):
    await db.upsert_server_config(interaction.guild_id, quotes_channel_id=channel.id if channel else None)
    await interaction.response.send_message(f"✅ Quotes channel {'set to ' + channel.mention if channel else 'cleared'}.", ephemeral=True)


@tree.command(name="set_frequency", description="[Admin] Set the auto-quote trigger frequency (0.1%–20%).")
@app_commands.describe(percent="Chance per message as a percentage. Decimals allowed e.g. 0.5, 0.1")
@admin_check()
async def set_frequency(interaction: discord.Interaction, percent: str):
    try:
        value = float(percent)
    except ValueError:
        await interaction.response.send_message("❌ Enter a number e.g. `0.1`, `0.5`, `1`.", ephemeral=True)
        return
    if not 0.1 <= value <= 20:
        await interaction.response.send_message("❌ Value must be between **0.1** and **20**.", ephemeral=True)
        return
    freq = value / 100
    await db.upsert_server_config(interaction.guild_id, message_frequency=freq)
    await interaction.response.send_message(f"✅ Frequency set to **{format_frequency(freq)}** per message.", ephemeral=True)


@tree.command(name="set_meme_ratio", description="[Admin] Set how often memes appear vs quotes (0–50%).")
@app_commands.describe(percent="Percentage of auto-triggers that show a meme (0–50)")
@admin_check()
async def set_meme_ratio(interaction: discord.Interaction, percent: int):
    if not 0 <= percent <= 50:
        await interaction.response.send_message("❌ Value must be 0–50.", ephemeral=True)
        return
    await db.upsert_server_config(interaction.guild_id, meme_ratio=percent / 100)
    await interaction.response.send_message(
        f"✅ {'Memes disabled.' if percent == 0 else f'Meme ratio set to **{percent}%**.'}", ephemeral=True
    )


@tree.command(name="set_qotd", description="[Admin] Set the Quote of the Day channel and time.")
@app_commands.describe(channel="Channel to post in", time="Post time HH:MM UTC")
@admin_check()
async def set_qotd(interaction: discord.Interaction, channel: discord.TextChannel, time: str = "09:00"):
    try:
        h, m = map(int, time.split(":"))
        assert 0 <= h <= 23 and 0 <= m <= 59
    except Exception:
        await interaction.response.send_message("❌ Use HH:MM format (e.g. 09:00).", ephemeral=True)
        return
    await db.upsert_server_config(interaction.guild_id, qotd_channel_id=channel.id, qotd_time=time)
    await interaction.response.send_message(f"✅ QOTD set to {channel.mention} at **{time} UTC**.", ephemeral=True)


@tree.command(name="blacklist_channel", description="[Admin] Stop the bot from posting in a channel.")
@app_commands.describe(channel="Channel to blacklist")
@admin_check()
async def blacklist_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    await db.add_blacklist_channel(interaction.guild_id, channel.id)
    await interaction.response.send_message(f"✅ {channel.mention} blacklisted.", ephemeral=True)


@tree.command(name="unblacklist_channel", description="[Admin] Re-enable the bot in a channel.")
@app_commands.describe(channel="Channel to unblacklist")
@admin_check()
async def unblacklist_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    await db.remove_blacklist_channel(interaction.guild_id, channel.id)
    await interaction.response.send_message(f"✅ {channel.mention} unblacklisted.", ephemeral=True)


@tree.command(name="meme_add", description="[Admin] Add a meme image URL to the pool.")
@app_commands.describe(url="Direct image URL", title="Optional title")
@admin_check()
async def meme_add(interaction: discord.Interaction, url: str, title: str = None):
    if not url.startswith("http"):
        await interaction.response.send_message("❌ URL must start with http(s)://", ephemeral=True)
        return
    meme_id = await db.add_meme(interaction.guild_id, url, title)
    await interaction.response.send_message(f"✅ Meme added! (ID `#{meme_id}`) — **{title or 'Untitled'}**", ephemeral=True)


@tree.command(name="meme_remove", description="[Admin] Remove a meme from the pool.")
@app_commands.describe(meme_id="Meme ID from /meme_list")
@admin_check()
async def meme_remove(interaction: discord.Interaction, meme_id: int):
    success = await db.remove_meme(meme_id, interaction.guild_id)
    await interaction.response.send_message(f"{'✅ Removed' if success else '❌ Not found'} meme `#{meme_id}`.", ephemeral=True)


@tree.command(name="meme_list", description="[Admin] List all memes in the pool.")
@admin_check()
async def meme_list(interaction: discord.Interaction):
    memes = await db.get_meme_list(interaction.guild_id)
    if not memes:
        await interaction.response.send_message("No memes yet. Use `/meme_add <url>`.", ephemeral=True)
        return
    embed = discord.Embed(title="😄 Meme Pool", color=0x7b5ea7)
    for m in memes[:20]:
        embed.add_field(name=f"`#{m['id']}` {'✅' if m['active'] else '❌'} {m['title'] or 'Untitled'}",
                        value=m["url"][:60] + "..." if len(m["url"]) > 60 else m["url"], inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="bank_add_item", description="[Admin] Add an item to the Guild Bank shop.")
@app_commands.describe(name="Item name", description="What the buyer receives", cost="Cost in gil")
@admin_check()
async def bank_add_item(interaction: discord.Interaction, name: str, description: str, cost: int):
    if cost <= 0:
        await interaction.response.send_message("❌ Cost must be > 0.", ephemeral=True)
        return
    item_id = await db.add_bank_item(name, description, cost)
    await interaction.response.send_message(f"✅ Added **{name}** for **{cost} gil** (ID `#{item_id}`).", ephemeral=True)


@tree.command(name="bank_remove_item", description="[Admin] Remove an item from the Guild Bank shop.")
@app_commands.describe(item_id="Item ID to remove")
@admin_check()
async def bank_remove_item(interaction: discord.Interaction, item_id: int):
    await db.toggle_bank_item(item_id, active=False)
    await interaction.response.send_message(f"✅ Item `#{item_id}` removed.", ephemeral=True)


@tree.command(name="bank_pending", description="[Admin] View unfulfilled Guild Bank purchases.")
@admin_check()
async def bank_pending(interaction: discord.Interaction):
    purchases = await db.get_pending_purchases(interaction.guild_id)
    if not purchases:
        await interaction.response.send_message("✅ No pending purchases!", ephemeral=True)
        return
    embed = discord.Embed(title="🏦 Pending Purchases", color=0xf87171)
    for p in purchases:
        member = interaction.guild.get_member(p["user_id"])
        name   = member.display_name if member else f"User {p['user_id']}"
        embed.add_field(name=f"`#{p['id']}` {p['item_name']} — {p['cost']} gil",
                        value=f"**{name}** · {p['purchased_at'].strftime('%Y-%m-%d %H:%M UTC')}\n`/bank_fulfill {p['id']}`", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="bank_fulfill", description="[Admin] Mark a Guild Bank purchase as fulfilled.")
@app_commands.describe(purchase_id="Purchase ID from /bank_pending")
@admin_check()
async def bank_fulfill(interaction: discord.Interaction, purchase_id: int):
    purchase = await db.fulfill_purchase(purchase_id, interaction.guild_id)
    if not purchase:
        await interaction.response.send_message("❌ Not found or already fulfilled.", ephemeral=True)
        return
    member = interaction.guild.get_member(purchase["user_id"])
    await interaction.response.send_message(
        f"✅ Purchase `#{purchase_id}` (**{purchase['item_name']}**) fulfilled{f' for {member.mention}' if member else ''}.", ephemeral=True
    )
    if member:
        try:
            await member.send(f"🏦 Your purchase of **{purchase['item_name']}** has been fulfilled by **{interaction.guild.name}**. Kupo!")
        except discord.Forbidden:
            pass


@tree.command(name="give_points", description="[Admin] Give or deduct gil from a user.")
@app_commands.describe(user="Target user", points="Amount (negative to deduct)")
@admin_check()
async def give_points(interaction: discord.Interaction, user: discord.Member, points: int):
    await db.add_points(interaction.guild_id, user.id, points)
    balance = await db.get_user_balance(interaction.guild_id, user.id)
    await interaction.response.send_message(
        f"✅ {'Gave' if points >= 0 else 'Deducted'} **{abs(points)} gil** {'to' if points >= 0 else 'from'} {user.mention}. Balance: **{balance} gil**.", ephemeral=True
    )

# ─────────────────────────────────────────────
#  Run
# ─────────────────────────────────────────────

if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN not set in .env file!")
    bot.run(TOKEN)
