from discord.ext import tasks

from .settings import BOT_TICKER_INTERVAL_MINUTES
from .data import LiquidityPool
from .helpers import LOGGER
from .ticker import TickerBot


class FeesBot(TickerBot):
    def __init__(self, *args, protocol_name: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.protocol_name = protocol_name

    async def on_ready(self):
        LOGGER.debug(f"Logged in as {self.user} (ID: {self.user.id})")
        LOGGER.debug("------")
        await self.update_presence(f"Watching fees for {self.protocol_name}")

    @tasks.loop(seconds=BOT_TICKER_INTERVAL_MINUTES * 60)
    async def ticker(self):
        try:
            pools = await LiquidityPool.get_pools()
            fees = sum(map(lambda p: p.total_fees, pools))

            await self.update_nick_for_all_servers(f"Fees: {round(fees/1000, 2)}K")
            await self.update_presence(f"{len(pools)} pools")
        except Exception as ex:
            LOGGER.error(f"Ticker failed with {ex}")
