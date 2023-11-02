import asyncio
import logging

from .settings import (
    DISCORD_TOKEN_PRICING,
    DISCORD_TOKEN_TVL,
    TOKEN_ADDRESS,
    STABLE_TOKEN_ADDRESS,
    PROTOCOL_NAME,
)
from .data import Token
from .helpers import LOGGING_HANDLER, LOGGING_LEVEL
from .price import PriceBot
from .tvl import TVLBot


async def main():
    """Main function."""

    # configure discord logging handler
    discord_logger = logging.getLogger("discord")
    discord_logger.setLevel(LOGGING_LEVEL)
    discord_logger.addHandler(LOGGING_HANDLER)

    token = await Token.get_by_token_address(TOKEN_ADDRESS)
    stable = await Token.get_by_token_address(STABLE_TOKEN_ADDRESS)

    price_bot = PriceBot(source_token=token, target_token=stable)
    tvl_bot = TVLBot(protocol_name=PROTOCOL_NAME)

    await asyncio.gather(
        price_bot.start(DISCORD_TOKEN_PRICING), tvl_bot.start(DISCORD_TOKEN_TVL)
    )


if __name__ == "__main__":
    asyncio.run(main())
