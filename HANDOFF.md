# HANDOFF — FFXI Quote Bot (Vana'diel Herald)

Public repo: [codemaverick-hub/ffxi-quote-bot](https://github.com/codemaverick-hub/ffxi-quote-bot). This file is the pick-up brief for Claude or ChatGPT.

## What it is

A Discord bot that posts authentic Final Fantasy XI quotes, plus a guild economy, games, and per-server config, backed by PostgreSQL. README title: **Vana'diel Herald — FFXI Quote Bot v2**.

## Tech stack

- Python, discord.py, python-dotenv, asyncpg
- PostgreSQL (Railway injects `DATABASE_URL`)
- Deployed on Railway (`Procfile`, `railway.toml`); auto-deploys on push to this repo

## Where it lives

- GitHub: this repository (`bot.py`, `database.py`, `quotes.py`, `requirements.txt`)
- Runtime: Railway (not a copy on Nagi as of this handoff)
- Owning bot: **FFXI Quote Bot**

## How to run, build, and install

Locally:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # set DISCORD token and DATABASE_URL locally
python bot.py
```

On Railway: set the token and Postgres in the service's environment. Do not put secrets in the repo. Railway auto-deploys on push; tables are created on first startup.

## Current state (as of 23 Nov 2026, America/New_York)

- Public repo, last pushed 21 Aug 2026.
- v2 feature set as described in README: auto-quotes, voice/server join quotes, keyword triggers, Quote of the Day, Guess the Speaker, voting, guild bank, slash commands, ~390 quotes.
- The owning Grok Bot has not been doing recent code work on this repo.

## Known bugs / watch-outs

- Keep `.env` and Railway variables out of git (`.gitignore` already covers typical secrets).
- This repo is **public**. Never add tokens, connection strings, or private character/account data.

## Next steps

- When changing quotes or commands, update README counts if they drift.
- If you take a task, note it here when you finish.

## Rules

- **No secrets.** Public repository.
- **Lumen's files are off-limits to other tools.**
- When you finish a task, update this HANDOFF.md.
