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
    get_seasonal_pool,
)

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ─────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────

CHANNEL_COOLDOWN  = 300   # seconds between auto-quotes per channel
GUESS_TIMEOUT     = 60    # seconds before guess game expires
GUESS_POINTS      = 10    # gil awarded for correct guess
REACT_QUOTE_EMOJI = "📜"
VOTE_UP_EMOJI     = "👍"
VOTE_DOWN_EMOJI   = "👎"

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
channel_cooldowns:    dict[int, datetime] = {}   # channel_id -> last quote time
active_guess_games:   dict[int, dict]     = {}   # channel_id -> game state
voted_message_hashes: dict[int, str]      = {}   # message_id -> quote_hash

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


async def get_guild_quote(guild_id: int) -> tuple[str, str]:
    """Weighted, no-repeat quote selection."""
    seasonal = get_seasonal_pool()
    pool     = list(WEIGHTED_POOL)
    if seasonal:
        pool += seasonal * 3

    recent   = await db.get_recent_hashes(guild_id)
    filtered = [(s, q) for s, q in pool if get_hash(s, q) not in recent]
    if not filtered:
        filtered = pool  # fallback when all quotes exhausted

    speaker, quote = random.choice(filtered)
    await db.add_recent_quote(guild_id, get_hash(speaker, quote))
    return speaker, quote


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


async def send_quote(channel: discord.TextChannel, speaker: str, quote: str):
    """Send a formatted quote with voting reactions and register it for the hash map."""
    msg = await channel.send(format_quote(speaker, quote))
    h   = get_hash(speaker, quote)
    voted_message_hashes[msg.id] = h
    if len(voted_message_hashes) > 1000:
        # Evict oldest entry to prevent unbounded growth
        oldest = next(iter(voted_message_hashes))
        del voted_message_hashes[oldest]
    await msg.add_reaction(VOTE_UP_EMOJI)
    await msg.add_reaction(VOTE_DOWN_EMOJI)
    return msg


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

        last = cfg.get("last_qotd_date")
        today = now.date()
        if last and last >= today:
            continue  # already posted today

        channel = bot.get_channel(cfg["qotd_channel_id"])
        if not channel:
            continue

        guild_id      = cfg["guild_id"]
        speaker, quote = await get_guild_quote(guild_id)
        featured_uid  = await db.get_pending_linkshell_user(guild_id)

        content  = f"🌅 **Quote of the Day — Vana'diel {now.strftime('%B %d')}**\n"
        if featured_uid:
            content += f"*(Featured spot courtesy of <@{featured_uid}>)*\n"
        content += format_quote(speaker, quote)

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

    # Always process active guess games regardless of other settings
    if channel_id in active_guess_games:
        if await _process_guess(message):
            await bot.process_commands(message)
            return  # Don't fire another quote right after a win

    # Skip blacklisted channels
    if is_blacklisted(config, channel_id):
        await bot.process_commands(message)
        return

    # Honour quotes-channel restriction
    qc = config.get("quotes_channel_id")
    if qc and channel_id != qc:
        await bot.process_commands(message)
        return

    # Keyword trigger (always fires if off cooldown, regardless of % setting)
    if off_cooldown(channel_id):
        for category, keywords in KEYWORD_MAP.items():
            if any(kw in content_lc for kw in keywords):
                speaker, quote = get_quote_by_category(category)
                await send_quote(message.channel, speaker, quote)
                set_cooldown(channel_id)
                await bot.process_commands(message)
                return

    # Random frequency trigger
    freq = config.get("message_frequency", 0.01)
    if random.random() < freq and off_cooldown(channel_id):
        speaker, quote = await get_guild_quote(guild_id)
        await send_quote(message.channel, speaker, quote)
        set_cooldown(channel_id)

    await bot.process_commands(message)


async def _process_guess(message: discord.Message) -> bool:
    """Returns True if the guess was correct and the game ended."""
    game = active_guess_games.get(message.channel.id)
    if not game:
        return False

    if not check_guess(message.content, game["speaker"]):
        return False

    # ✅ Correct guess
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
        speaker, quote = await get_guild_quote(guild_id)
        await channel.send(
            f"🎺 *{member.display_name} joined **{after.channel.name}**!*\n"
            + format_quote(speaker, quote)
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
        speaker, quote = await get_guild_quote(guild_id)
        await target.send(
            f"🌟 *{member.mention} has arrived in Vana'diel!*\n"
            + format_quote(speaker, quote)
        )


@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    if user.bot or not reaction.message.guild:
        return

    emoji      = str(reaction.emoji)
    msg        = reaction.message
    guild_id   = msg.guild.id

    # 📜 — react-to-quote
    if emoji == REACT_QUOTE_EMOJI:
        speaker, quote = await get_guild_quote(guild_id)
        await msg.channel.send(format_quote(speaker, quote))
        return

    # 👍 / 👎 — vote on bot quote messages
    if emoji in (VOTE_UP_EMOJI, VOTE_DOWN_EMOJI) and msg.author == bot.user:
        q_hash = voted_message_hashes.get(msg.id)
        if q_hash:
            await db.add_vote(guild_id, q_hash, emoji == VOTE_UP_EMOJI)


# ─────────────────────────────────────────────
#  Quote Commands
# ─────────────────────────────────────────────

@tree.command(name="ffxi", description="Get a random FFXI quote from Vana'diel!")
async def ffxi_quote(interaction: discord.Interaction):
    speaker, quote = await get_guild_quote(interaction.guild_id)
    await interaction.response.send_message(format_quote(speaker, quote))
    sent = await interaction.original_response()
    voted_message_hashes[sent.id] = get_hash(speaker, quote)
    await sent.add_reaction(VOTE_UP_EMOJI)
    await sent.add_reaction(VOTE_DOWN_EMOJI)


@tree.command(name="ffxi_category", description="Get an FFXI quote from a specific category.")
@app_commands.describe(category="Choose a quote category")
@app_commands.choices(category=[
    app_commands.Choice(name="NPC / Story Quotes",          value="npc"),
    app_commands.Choice(name="Battle Cries & Job Abilities", value="battle"),
    app_commands.Choice(name="Moogle Quips",                value="moogle"),
    app_commands.Choice(name="Player Emote Flavor",         value="emote"),
    app_commands.Choice(name="Avatar & Summon Quotes",      value="avatar"),
    app_commands.Choice(name="Notorious Monsters",          value="nm"),
    app_commands.Choice(name="City & NPC Flavor",           value="city"),
    app_commands.Choice(name="Player /say Flavor",          value="player"),
    app_commands.Choice(name="Abyssea",                     value="abyssea"),
])
async def ffxi_category(interaction: discord.Interaction, category: app_commands.Choice[str]):
    speaker, quote = get_quote_by_category(category.value)
    await interaction.response.send_message(format_quote(speaker, quote))


@tree.command(name="ffxi_expansion", description="Get an FFXI quote from a specific expansion.")
@app_commands.describe(expansion="Choose an expansion")
@app_commands.choices(expansion=[
    app_commands.Choice(name="Rise of the Zilart",          value="zilart"),
    app_commands.Choice(name="Chains of Promathia",         value="cop"),
    app_commands.Choice(name="Treasures of Aht Urhgan",    value="toau"),
    app_commands.Choice(name="Wings of the Goddess",        value="wotg"),
    app_commands.Choice(name="Seekers of Adoulin",          value="soa"),
    app_commands.Choice(name="Rhapsodies of Vana'diel",     value="rov"),
    app_commands.Choice(name="Abyssea",                     value="abyssea"),
])
async def ffxi_expansion(interaction: discord.Interaction, expansion: app_commands.Choice[str]):
    pool = EXPANSION_QUOTES.get(expansion.value)
    if not pool:
        await interaction.response.send_message("No quotes found for that expansion yet!", ephemeral=True)
        return
    speaker, quote = random.choice(pool)
    await interaction.response.send_message(format_quote(speaker, quote))


@tree.command(name="ffxi_about", description="Show bot info, quote counts, and current server settings.")
async def ffxi_about(interaction: discord.Interaction):
    config   = await db.get_server_config(interaction.guild_id)
    freq     = config.get("message_frequency", 0.01)
    qc       = config.get("quotes_channel_id")
    qotd_ch  = config.get("qotd_channel_id")
    qotd_t   = config.get("qotd_time", "09:00")
    bl       = config.get("blacklisted_channels") or []
    seasonal = get_seasonal_pool()

    embed = discord.Embed(
        title="📜 Vana'diel Herald — Bot Info",
        color=0x7b5ea7,
        description="Authentic FFXI quotes delivered to your Discord server."
    )
    embed.add_field(name="📊 Quote Pool", value=(
        "NPC / Story: ~65\nBattle Cries: ~95\nMoogle Quips: ~22\n"
        "Emote Flavor: ~26\nAvatar & Summon: ~80\nNotorious Monsters: ~25\n"
        "City & NPC: ~22\nPlayer /say: ~21\nAbyssea: ~15\n**Total: ~370+**"
    ), inline=True)
    embed.add_field(name="⚙️ Server Settings", value=(
        f"Message trigger: **{int(freq*100)}%**\n"
        f"Quotes channel: {f'<#{qc}>' if qc else 'Any channel'}\n"
        f"QOTD channel: {f'<#{qotd_ch}> at {qotd_t} UTC' if qotd_ch else 'Not set'}\n"
        f"Blacklisted: {len(bl)} channel(s)\n"
        f"Seasonal pool: {'✅ Active' if seasonal else '—'}\n"
        f"Channel cooldown: {CHANNEL_COOLDOWN//60} min"
    ), inline=True)
    embed.add_field(name="🎮 Commands", value=(
        "`/ffxi` · `/ffxi_category` · `/ffxi_expansion`\n"
        "`/ffxi_guess` — Start a guessing game\n"
        "`/leaderboard` — Top guessers & gil\n"
        "`/bank_balance` · `/bank_shop` · `/bank_buy`\n"
        "React 📜 to any message for a random quote\n"
        "React 👍/👎 to rate bot quotes"
    ), inline=False)
    await interaction.response.send_message(embed=embed)


# ─────────────────────────────────────────────
#  Guess the Speaker
# ─────────────────────────────────────────────

@tree.command(name="ffxi_guess", description="Start a Guess the Speaker game! First correct answer wins gil.")
async def ffxi_guess(interaction: discord.Interaction):
    cid = interaction.channel_id

    if cid in active_guess_games:
        await interaction.response.send_message(
            "⚔️ A game is already running here! Type your guess as a message.", ephemeral=True
        )
        return

    # Pick a quote with a named speaker
    pool = [(s, q) for s, q in ALL_QUOTES if s not in ("Adventurer",)]
    speaker, quote = random.choice(pool)

    embed = discord.Embed(
        title="🎲 Guess the Speaker!",
        description=(
            f'*"{quote}"*\n\n'
            f"**Who said this?** Type your answer in this channel!\n"
            f"⏱ You have **{GUESS_TIMEOUT} seconds** · Prize: **{GUESS_POINTS} gil** 🪙"
        ),
        color=0xf0c060
    )
    embed.set_footer(text="Partial names accepted if they're at least 4 characters and unambiguous.")
    await interaction.response.send_message(embed=embed)

    async def timeout():
        await asyncio.sleep(GUESS_TIMEOUT)
        if cid in active_guess_games:
            del active_guess_games[cid]
            await interaction.channel.send(
                f"⏰ Time's up! The speaker was **{speaker}**. Better luck next time, kupo!"
            )

    task = asyncio.create_task(timeout())
    active_guess_games[cid] = {"speaker": speaker, "quote": quote, "task": task}


# ─────────────────────────────────────────────
#  Leaderboard
# ─────────────────────────────────────────────

@tree.command(name="leaderboard", description="Show the top Guess the Speaker scorers and their gil balance.")
async def leaderboard(interaction: discord.Interaction):
    rows = await db.get_leaderboard(interaction.guild_id)
    if not rows:
        await interaction.response.send_message(
            "No scores yet! Start a game with `/ffxi_guess`.", ephemeral=True
        )
        return

    medals = ["🥇", "🥈", "🥉"]
    lines  = []
    for i, row in enumerate(rows):
        medal  = medals[i] if i < 3 else f"**{i+1}.**"
        member = interaction.guild.get_member(row["user_id"])
        name   = member.display_name if member else f"User {row['user_id']}"
        lines.append(
            f"{medal} **{name}** — {row['points']} gil 🪙 · {row['correct_guesses']} correct"
        )

    embed = discord.Embed(title="🏆 Vana'diel Herald Leaderboard", color=0xf0c060)
    embed.description = "\n".join(lines)
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
        f"🪙 **{interaction.user.display_name}'s Account**\n"
        f"Balance: **{balance} gil**\n"
        f"Correct guesses: **{correct}**\n"
        f"*Spend your gil at `/bank_shop`!*",
        ephemeral=True
    )


@tree.command(name="bank_shop", description="Browse the Guild Bank shop.")
async def bank_shop(interaction: discord.Interaction):
    items   = await db.get_bank_items()
    balance = await db.get_user_balance(interaction.guild_id, interaction.user.id)

    if not items:
        await interaction.response.send_message(
            "The Guild Bank is empty. Admins can add items with `/bank_add_item`.", ephemeral=True
        )
        return

    embed = discord.Embed(
        title="🏦 Guild Bank — Shop",
        description=f"Your balance: **{balance} gil** 🪙\nUse `/bank_buy <item_id>` to purchase.",
        color=0xc8821a
    )
    for item in items:
        can_afford = "✅" if balance >= item["cost"] else "❌"
        embed.add_field(
            name=f"`#{item['id']}` {item['name']} — {item['cost']} gil {can_afford}",
            value=item["description"],
            inline=False
        )
    embed.set_footer(text="Items are fulfilled by server admins. Use /bank_pending to check status.")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="bank_buy", description="Purchase an item from the Guild Bank.")
@app_commands.describe(item_id="The item ID shown in /bank_shop")
async def bank_buy(interaction: discord.Interaction, item_id: int):
    guild_id = interaction.guild_id
    user_id  = interaction.user.id

    item = await db.get_bank_item(item_id)
    if not item or not item["active"]:
        await interaction.response.send_message("Item not found or no longer available.", ephemeral=True)
        return

    balance = await db.get_user_balance(guild_id, user_id)
    if balance < item["cost"]:
        await interaction.response.send_message(
            f"❌ Not enough gil! You have **{balance}** but need **{item['cost']}**.", ephemeral=True
        )
        return

    purchase_id  = await db.purchase_item(guild_id, user_id, item_id, item["name"], item["cost"])
    new_balance  = await db.get_user_balance(guild_id, user_id)

    await interaction.response.send_message(
        f"✅ **Purchase successful!**\n"
        f"Item: **{item['name']}**\n"
        f"Cost: **{item['cost']} gil**\n"
        f"Remaining balance: **{new_balance} gil**\n\n"
        f"*An admin will fulfill your order. Purchase ID: `#{purchase_id}`*",
        ephemeral=True
    )

    # Notify admins in the quotes channel if set
    config = await db.get_server_config(guild_id)
    notify_ch = interaction.guild.get_channel(config.get("quotes_channel_id") or 0)
    if notify_ch:
        await notify_ch.send(
            f"🏦 **New Guild Bank Purchase!**\n"
            f"{interaction.user.mention} purchased **{item['name']}** (Purchase ID `#{purchase_id}`).\n"
            f"*Admins: use `/bank_fulfill {purchase_id}` to mark as complete.*"
        )


# ─────────────────────────────────────────────
#  Admin Commands
# ─────────────────────────────────────────────

def admin_check():
    async def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.manage_guild
    return app_commands.check(predicate)


@tree.command(name="set_quotes_channel", description="[Admin] Set the channel for auto-quotes and bot notifications.")
@app_commands.describe(channel="Target channel (leave empty to allow all channels)")
@admin_check()
async def set_quotes_channel(interaction: discord.Interaction, channel: discord.TextChannel = None):
    await db.upsert_server_config(interaction.guild_id, quotes_channel_id=channel.id if channel else None)
    msg = f"✅ Quotes channel set to {channel.mention}." if channel else "✅ Quotes channel cleared — bot will post in any channel."
    await interaction.response.send_message(msg, ephemeral=True)


@tree.command(name="set_frequency", description="[Admin] Set the auto-quote message trigger frequency.")
@app_commands.describe(percent="Chance per message in % (1–20)")
@admin_check()
async def set_frequency(interaction: discord.Interaction, percent: int):
    if not 1 <= percent <= 20:
        await interaction.response.send_message("❌ Enter a value between 1 and 20.", ephemeral=True)
        return
    await db.upsert_server_config(interaction.guild_id, message_frequency=percent / 100)
    await interaction.response.send_message(f"✅ Message trigger set to **{percent}%**.", ephemeral=True)


@tree.command(name="set_qotd", description="[Admin] Set the Quote of the Day channel and post time.")
@app_commands.describe(channel="Channel to post in", time="Post time in HH:MM UTC (e.g. 09:00)")
@admin_check()
async def set_qotd(interaction: discord.Interaction, channel: discord.TextChannel, time: str = "09:00"):
    try:
        h, m = map(int, time.split(":"))
        assert 0 <= h <= 23 and 0 <= m <= 59
    except Exception:
        await interaction.response.send_message("❌ Invalid time. Use HH:MM format (e.g. 09:00).", ephemeral=True)
        return
    await db.upsert_server_config(interaction.guild_id, qotd_channel_id=channel.id, qotd_time=time)
    await interaction.response.send_message(
        f"✅ Quote of the Day set to {channel.mention} at **{time} UTC** daily.", ephemeral=True
    )


@tree.command(name="blacklist_channel", description="[Admin] Stop the bot from posting in a channel.")
@app_commands.describe(channel="Channel to blacklist")
@admin_check()
async def blacklist_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    await db.add_blacklist_channel(interaction.guild_id, channel.id)
    await interaction.response.send_message(f"✅ {channel.mention} blacklisted.", ephemeral=True)


@tree.command(name="unblacklist_channel", description="[Admin] Re-enable the bot in a blacklisted channel.")
@app_commands.describe(channel="Channel to unblacklist")
@admin_check()
async def unblacklist_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    await db.remove_blacklist_channel(interaction.guild_id, channel.id)
    await interaction.response.send_message(f"✅ {channel.mention} removed from blacklist.", ephemeral=True)


@tree.command(name="bank_add_item", description="[Admin] Add an item to the Guild Bank shop.")
@app_commands.describe(name="Item name", description="What the buyer receives", cost="Cost in gil")
@admin_check()
async def bank_add_item(interaction: discord.Interaction, name: str, description: str, cost: int):
    if cost <= 0:
        await interaction.response.send_message("❌ Cost must be greater than 0.", ephemeral=True)
        return
    item_id = await db.add_bank_item(name, description, cost)
    await interaction.response.send_message(
        f"✅ Added **{name}** to the shop for **{cost} gil** (ID `#{item_id}`).", ephemeral=True
    )


@tree.command(name="bank_remove_item", description="[Admin] Remove an item from the Guild Bank shop.")
@app_commands.describe(item_id="Item ID to remove")
@admin_check()
async def bank_remove_item(interaction: discord.Interaction, item_id: int):
    await db.toggle_bank_item(item_id, active=False)
    await interaction.response.send_message(f"✅ Item `#{item_id}` removed from the shop.", ephemeral=True)


@tree.command(name="bank_pending", description="[Admin] View unfulfilled Guild Bank purchases.")
@admin_check()
async def bank_pending(interaction: discord.Interaction):
    purchases = await db.get_pending_purchases(interaction.guild_id)
    if not purchases:
        await interaction.response.send_message("✅ No pending purchases!", ephemeral=True)
        return

    embed = discord.Embed(title="🏦 Pending Guild Bank Purchases", color=0xf87171)
    for p in purchases:
        member = interaction.guild.get_member(p["user_id"])
        name   = member.display_name if member else f"User {p['user_id']}"
        embed.add_field(
            name=f"`#{p['id']}` {p['item_name']} — {p['cost']} gil",
            value=f"Buyer: **{name}** · {p['purchased_at'].strftime('%Y-%m-%d %H:%M UTC')}\n`/bank_fulfill {p['id']}`",
            inline=False
        )
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="bank_fulfill", description="[Admin] Mark a Guild Bank purchase as fulfilled.")
@app_commands.describe(purchase_id="Purchase ID from /bank_pending")
@admin_check()
async def bank_fulfill(interaction: discord.Interaction, purchase_id: int):
    purchase = await db.fulfill_purchase(purchase_id, interaction.guild_id)
    if not purchase:
        await interaction.response.send_message("❌ Purchase not found or already fulfilled.", ephemeral=True)
        return

    member = interaction.guild.get_member(purchase["user_id"])
    await interaction.response.send_message(
        f"✅ Purchase `#{purchase_id}` (**{purchase['item_name']}**) fulfilled"
        f"{f' for {member.mention}' if member else ''}.",
        ephemeral=True
    )
    if member:
        try:
            await member.send(
                f"🏦 **Guild Bank — Order Fulfilled!**\n"
                f"Your purchase of **{purchase['item_name']}** has been fulfilled by the admins of "
                f"**{interaction.guild.name}**. Kupo! Enjoy your reward!"
            )
        except discord.Forbidden:
            pass


@tree.command(name="give_points", description="[Admin] Give or deduct gil from a user.")
@app_commands.describe(user="Target user", points="Amount (use negative to deduct)")
@admin_check()
async def give_points(interaction: discord.Interaction, user: discord.Member, points: int):
    await db.add_points(interaction.guild_id, user.id, points)
    balance = await db.get_user_balance(interaction.guild_id, user.id)
    action  = "Gave" if points >= 0 else "Deducted"
    await interaction.response.send_message(
        f"✅ {action} **{abs(points)} gil** {'to' if points >= 0 else 'from'} {user.mention}. "
        f"New balance: **{balance} gil**.",
        ephemeral=True
    )


# ─────────────────────────────────────────────
#  Run
# ─────────────────────────────────────────────

if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN not set in .env file!")
    bot.run(TOKEN)
