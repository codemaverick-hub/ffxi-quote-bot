# 📜 FFXI Quote Bot — Vana'diel Speaks

A Discord bot that drops authentic Final Fantasy XI quotes based on server activity.

---

## Features

| Trigger | Behavior |
|---|---|
| User **joins a voice channel** | Posts a random quote in the first available text channel |
| User **sends a message** | 10% chance to reply with a random quote |
| User **joins the server** | Welcomes them with a quote in the system/general channel |
| `/ffxi` slash command | Returns a random quote on demand |
| `/ffxi_category` slash command | Returns a quote from a chosen category |

### Quote Categories
- **NPC / Story** — Prishe, Shantotto, Lion, Cait Sith, Bahamut, and more
- **Battle Cries** — Job ability callouts for all 22 jobs
- **Moogle Quips** — Kupo-filled Mog House wisdom
- **Player Emote Flavor** — /cry, /panic, /joy, /slap, and other classics

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
   - Bot Permissions: `Send Messages`, `Read Messages/View Channels`
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
✅ Logged in as Vana'diel Herald#1234 (ID: ...)
📜 FFXI Quote Bot is ready — Vana'diel awaits!
```

---

## Customization

- **Quote chance on messages** — Edit the `0.10` value in `bot.py` (`on_message`) to adjust frequency (0.0–1.0)
- **Add more quotes** — Open `quotes.py` and append tuples to any of the four lists
- **Restrict to specific channels** — Add a channel name/ID check inside `on_message`

---

## File Structure

```
ffxi_bot/
├── bot.py           # Discord bot logic & event handlers
├── quotes.py        # All FFXI quotes, organized by category
├── requirements.txt # Python dependencies
├── .env.example     # Token template
└── README.md        # This file
```
