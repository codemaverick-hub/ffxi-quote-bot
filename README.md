# 📜 FFXI Quote Bot — Vana'diel Speaks

A Discord bot that drops authentic Final Fantasy XI quotes based on server activity. Over 300 quotes spanning all major expansions, jobs, avatars, notorious monsters, and city NPCs.

---

## Features

| Trigger | Behavior |
|---|---|
| User **joins a voice channel** | Posts a random quote in the first available text channel |
| User **sends a message** | 1% chance to reply with a random quote |
| User **joins the server** | Welcomes them with a quote in the system/general channel |
| `/ffxi` slash command | Returns a random quote on demand |
| `/ffxi_category` slash command | Returns a quote from a chosen category |

---

## Quote Categories

Use `/ffxi_category` to pull from a specific pool:

| Category | Value | Description |
|---|---|---|
| NPC / Story Quotes | `npc` | Prishe, Shantotto, Lion, Bahamut, Promathia, Iroha, Zeid, Gilgamesh, and more — all 5 expansions |
| Battle Cries & Job Abilities | `battle` | Ability callouts for all 22 jobs, 3–5 per job |
| Moogle Quips | `moogle` | Kupo-filled Mog House wisdom, delivery chaos, and moogle observations |
| Player Emote Flavor | `emote` | /cry, /panic, /joy, /slap, /pray, /angry and 20+ other classic emotes |
| Avatar & Summon Quotes | `avatar` | All 14 avatars — Ifrit through Atomos — with ability lines and personality quotes |
| Notorious Monsters | `nm` | AV, Pandemonium Warden, Nidhogg, Fafnir, Kirin, Cerberus, Dynamis Lord and more taunting your party |
| City & NPC Flavor | `city` | Gate guards, blacksmiths, Tarutaru scholars, pirates, pioneers, and settlers across Vana'diel |

---

## Setup

### 1. Create a Discord Bot
1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. Click **New Application** → name it (e.g. `Vana'diel Herald`)
3. Go to **Bot** → click **Add Bot**
4. Under **Token**, click **Reset Token** and copy it
5. Under **Privileged Gateway Intents**, enable:
   - ✅ Server Members Intent
   - ✅ Message Content Intent
6. Go to **OAuth2 → URL Generator**
   - Scopes: `bot`, `applications.commands`
   - Bot Permissions: `Send Messages`, `Read Messages/View Channels`, `Read Message History`
7. Open the generated URL to invite the bot to your server

### 2. Install & Configure

```bash
# Clone or copy the bot files into a folder
cd ffxi_bot

# Install dependencies
pip install -r requirements.txt

# Set up your token
cp .env.example .env
# Edit .env and paste your bot token
```

### 3. Run

```bash
python bot.py
```

You should see:
```
✅ Logged in as Vana'diel Herald#XXXX (ID: ...)
📜 FFXI Quote Bot is ready — Vana'diel awaits!
```

---

## Deploying on Railway

1. Push this repo to GitHub
2. Go to [railway.app](https://railway.app) → **New Project → Deploy from GitHub repo**
3. Select your repo — Railway auto-detects the `Procfile` and sets up the worker
4. Go to **Variables** tab → add `DISCORD_TOKEN` with your bot token
5. Click **Deploy** — the bot will be online in under a minute

Any future `git push` to `main` will auto-redeploy.

---

## Customization

- **Quote chance on messages** — Edit the `0.01` value in `bot.py` (`on_message`) to adjust frequency (0.0–1.0). Currently set to 1%.
- **Add more quotes** — Open `quotes.py` and append tuples to any of the seven lists
- **Add a new category** — Add a new list to `quotes.py`, add it to the `categories` dict in `get_quote_by_category`, and add a new `app_commands.Choice` in `bot.py`
- **Restrict to specific channels** — Add a channel name/ID check inside `on_message`

---

## File Structure

```
ffxi_bot/
├── bot.py           # Discord bot logic, event handlers & slash commands
├── quotes.py        # 300+ FFXI quotes organized across 7 categories
├── requirements.txt # Python dependencies
├── .env.example     # Token config template
├── Procfile         # Railway worker process definition
├── railway.toml     # Railway build & deploy config
└── README.md        # This file
```

---

## Quote Count (approximate)

| Category | Quotes |
|---|---|
| NPC / Story | ~65 |
| Battle Cries | ~95 |
| Moogle Quips | ~22 |
| Emote Flavor | ~26 |
| Avatar & Summon | ~80 |
| Notorious Monsters | ~25 |
| City & NPC Flavor | ~22 |
| **Total** | **~335** |
