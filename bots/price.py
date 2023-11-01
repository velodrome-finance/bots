from discord.ext import tasks

from .settings import BOT_TICKER_INTERVAL_MINUTES
from .data import Token, Price
from .helpers import LOGGER
from .ticker import TickerBot


class PriceBot(TickerBot):
    def __init__(self, *args, source_token: Token, target_token: Token, **kwargs):
        """Create price bot for specific source token to target token

        Args:
            source_token (Token): token to convert from
            target_token (Token): token to conver to
        """
        super().__init__(*args, **kwargs)
        self.source_token = source_token
        self.target_token = target_token

    async def on_ready(self):
        LOGGER.debug(f"Logged in as {self.user} (ID: {self.user.id})")
        LOGGER.debug("------")
        await self.update_presence(self.source_token.symbol)

    @tasks.loop(seconds=BOT_TICKER_INTERVAL_MINUTES * 60)
    async def ticker(self):
        try:
            [source_token_price] = await Price.get_prices([self.source_token])
            await self.update_nick_for_all_servers(
                f"{self.target_token.symbol} {source_token_price.pretty_price}"
            )
        except Exception as ex:
            LOGGER.error(f"Ticker failed with {ex}")
