# 📜 Vana'diel Herald — FFXI Quote Bot v2

A fully-featured Discord bot delivering authentic Final Fantasy XI quotes, a guild economy, games, and server-level configuration — all powered by PostgreSQL.

---

## Features at a Glance

| Feature | Description |
|---|---|
| 📜 Auto-quotes | 1% message trigger with 5-min channel cooldown |
| 🎤 Voice join | Quote posted when anyone joins a voice channel |
| 🌟 Server join | Welcome quote for new members |
| 🔑 Keyword triggers | Mentions of "kupo", "ifrit", "absolute virtue" etc. fire relevant quotes |
| 📅 Quote of the Day | Scheduled daily quote posted to a designated channel |
| 🎲 Guess the Speaker | Game where users earn gil by naming the quote's speaker |
| 👍/👎 Quote voting | React to rate bot quotes |
| 📜 React-to-quote | React with 📜 on any message for a random quote |
| 🏆 Leaderboard | Top earners by gil balance and correct guesses |
| 🏦 Guild Bank | Spend earned gil on server rewards fulfilled by admins |
| 🌀 No-repeat memory | Last 30 quotes per server are excluded from the random pool |
| ⚖️ Weighted pool | NMs and Abyssea quotes appear less often — they feel rare |
| 🎄 Seasonal quotes | Special pools for Starlight (Dec), Harvest (Oct), Valentione's (Feb) |
| ⚙️ Per-server config | Admins control channel, frequency, QOTD, and blacklists via slash commands |

---

## Slash Commands

### User Commands

| Command | Description |
|---|---|
| `/ffxi` | Random quote from the weighted pool |
| `/ffxi_category` | Quote from a specific category |
| `/ffxi_expansion` | Quote from a specific expansion |
| `/ffxi_about` | Bot info, quote counts, current server settings |
| `/ffxi_guess` | Start a 60-second Guess the Speaker game |
| `/leaderboard` | Top 10 players by gil and correct guesses |
| `/bank_balance` | Your current gil balance |
| `/bank_shop` | Browse available Guild Bank items |
| `/bank_buy <id>` | Purchase a Guild Bank item |

### Admin Commands (Manage Server permission required)

| Command | Description |
|---|---|
| `/set_quotes_channel` | Restrict bot to one channel (leave blank to allow all) |
| `/set_frequency <1-20>` | Set message trigger % chance |
| `/set_qotd <channel> <HH:MM>` | Enable Quote of the Day |
| `/blacklist_channel` | Prevent bot from posting in a channel |
| `/unblacklist_channel` | Re-enable bot in a channel |
| `/bank_add_item` | Add a reward to the Guild Bank shop |
| `/bank_remove_item` | Remove an item from the shop |
| `/bank_pending` | View unfulfilled purchases |
| `/bank_fulfill <id>` | Mark a purchase as complete (notifies buyer via DM) |
| `/give_points <user> <amount>` | Manually give or deduct gil |

---

## Quote Categories

Use `/ffxi_category`:

| Value | Description |
|---|---|
| `npc` | NPC & story quotes from all 5 expansions |
| `battle` | Job ability callouts for all 22 jobs |
| `moogle` | Kupo-filled Mog House wisdom |
| `emote` | /cry, /panic, /joy, /slap and 25+ more |
| `avatar` | All 14 avatars with ability lines and personality |
| `nm` | Notorious Monsters taunting your party |
| `city` | Gate guards, merchants, pirates, pioneers |
| `player` | Anonymous party member /say flavor |
| `abyssea` | Abyssea NPCs, visitants, and atmosphere |

Use `/ffxi_expansion`:

`zilart` · `cop` · `toau` · `wotg` · `soa` · `rov` · `abyssea`

---

## Guild Bank Economy

- Users earn **gil** by winning **Guess the Speaker** games (10 gil per correct guess)
- Admins can manually adjust balances with `/give_points`
- Items are configured by admins and fulfilled manually — the bot tracks and notifies

**Default shop items (configurable):**

| Item | Cost | Description |
|---|---|---|
| Adventurer's Title | 50 gil | Custom role recognition |
| Linkshell Pearl | 100 gil | Featured in the next QOTD post |
| Claim Flag | 150 gil | Bot announces your NM claim |
| Mog Bonanza Ticket | 300 gil | Admin-run raffle entry |
| Dynamis Access | 500 gil | Legendary "Dynamis Veteran" recognition |

---

## Deployment

### 1. Add PostgreSQL on Railway
In your Railway project → **New** → **Database** → **PostgreSQL**. Railway auto-injects `DATABASE_URL` — no extra config needed.

### 2. Update your files
Replace `bot.py`, `database.py`, `quotes.py`, and `requirements.txt` with v2 versions.

### 3. Push to GitHub
Railway auto-deploys on push. The bot creates all database tables on first startup.

---

## File Structure

```
ffxi_bot/
├── bot.py           # All Discord logic, events, and slash commands
├── database.py      # Async PostgreSQL helper (asyncpg)
├── quotes.py        # 370+ quotes across 9 categories + seasonal pools
├── requirements.txt # discord.py, python-dotenv, asyncpg
├── .env.example     # Token template
├── Procfile         # Railway worker definition
├── railway.toml     # Railway build config
└── README.md        # This file
```

---

## Quote Count

| Category | Approx. |
|---|---|
| NPC / Story | ~65 |
| Battle Cries | ~95 |
| Moogle Quips | ~22 |
| Emote Flavor | ~26 |
| Avatar & Summon | ~80 |
| Notorious Monsters | ~25 |
| City & NPC Flavor | ~22 |
| Player /say | ~21 |
| Abyssea | ~15 |
| Seasonal (Dec/Oct/Feb) | ~21 |
| **Total** | **~390+** |
