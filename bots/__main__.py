import asyncio
import logging

from .settings import (
    DISCORD_TOKEN_PRICING,
    DISCORD_TOKEN_TVL,
    DISCORD_TOKEN_FEES,
    DISCORD_TOKEN_REWARDS,
    DISCORD_TOKEN_COMMANDER,
    TOKEN_ADDRESS,
    STABLE_TOKEN_ADDRESS,
    PROTOCOL_NAME,
)
from .data import Token
from .helpers import (
    LOGGING_HANDLER,
    LOGGING_LEVEL,
)
from .price import PriceBot
from .tvl import TVLBot
from .fees import FeesBot
from .rewards import RewardsBot
from .commander import CommanderBot


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
    fees_bot = FeesBot(protocol_name=PROTOCOL_NAME)
    rewards_bot = RewardsBot(protocol_name=PROTOCOL_NAME)
    commander_bot = CommanderBot()

    await asyncio.gather(
        price_bot.start(DISCORD_TOKEN_PRICING),
        fees_bot.start(DISCORD_TOKEN_FEES),
        tvl_bot.start(DISCORD_TOKEN_TVL),
        rewards_bot.start(DISCORD_TOKEN_REWARDS),
        commander_bot.start(DISCORD_TOKEN_COMMANDER),
    )


if __name__ == "__main__":
    asyncio.run(main())
