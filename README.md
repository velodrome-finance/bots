# bots

## Pre-reqs

- [Poetry](https://python-poetry.org/)
- [Nox](https://nox.thea.codes/en/stable/)

## Running locally

- `cp .env.example .env`
- set `DISCORD_TOKEN` for your bot
- `poetry install`
- `poetry run python -m bots.__main__`

## Before you push

```bash
poetry run nox
```

Got issues with formatting?

```bash
poetry run nox -rs black
```

## Setting up Bots on Discord

- head to [Discord Developer Portal](https://discord.com/developers/applications)
- click `New Application` (top right corner)
- come up with a sensible name for the bot, accept TOS, click `Create`
- click `Bot` in the left hand side panel
- click `Reset Token`
- copy newly created token and keep it to share with your trusted dev
- click `OAuth2` in the left had side panel
- click `URL Generator` in the sub menu
- in `Scopes`, select `bot`
- in `Bot Permissions`, select `Change Nickname`
- copy `Generated URL` and open it in a new tab to add bot to a server you control
