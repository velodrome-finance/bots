import asyncio
import logging

import discord

from .settings import (
    DISCORD_TOKEN_PRICING,
    TOKEN_ADDRESS,
    STABLE_TOKEN_ADDRESS,
)
from .data import Token
from .helpers import LOGGING_HANDLER, LOGGING_LEVEL
from .price import PriceBot


async def main():
    """Main function."""

    # configure discord logging handler
    discord_logger = logging.getLogger("discord")
    discord_logger.setLevel(LOGGING_LEVEL)
    discord_logger.addHandler(LOGGING_HANDLER)

    token = await Token.get_by_token_address(TOKEN_ADDRESS)
    stable = await Token.get_by_token_address(STABLE_TOKEN_ADDRESS)

    bot = PriceBot(
        source_token=token, target_token=stable, intents=discord.Intents.default()
    )
    await bot.start(DISCORD_TOKEN_PRICING)


if __name__ == "__main__":
    asyncio.run(main())
