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
    """Run configured bots"""

    # configure discord logging handler
    discord_logger = logging.getLogger("discord")
    discord_logger.setLevel(LOGGING_LEVEL)
    discord_logger.addHandler(LOGGING_HANDLER)

    token = await Token.get_by_token_address(TOKEN_ADDRESS)
    stable = await Token.get_by_token_address(STABLE_TOKEN_ADDRESS)

    bot_specs = [
        (DISCORD_TOKEN_PRICING, PriceBot(source_token=token, target_token=stable)),
        (DISCORD_TOKEN_TVL, TVLBot(protocol_name=PROTOCOL_NAME)),
        (DISCORD_TOKEN_FEES, FeesBot(protocol_name=PROTOCOL_NAME)),
        (DISCORD_TOKEN_REWARDS, RewardsBot(protocol_name=PROTOCOL_NAME)),
        (DISCORD_TOKEN_COMMANDER, CommanderBot()),
    ]

    # only run bots that have discord tokens configured
    tasks = list(
        map(
            lambda spec: spec[1].start(spec[0]),
            filter(lambda spec: spec[0], bot_specs),
        )
    )

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
