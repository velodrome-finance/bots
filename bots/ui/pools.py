import discord
from ..data import LiquidityPool
from typing import List, Callable, Awaitable

intents = discord.Intents.default()
intents.message_content = True


def build_select_option(pool: LiquidityPool) -> discord.SelectOption:
    return discord.SelectOption(label=pool.symbol, value=pool.lp, emoji="🏊‍♀️")


class _PoolsDropdown(discord.ui.Select):
    def __init__(
        self,
        pools: List[LiquidityPool],
        callback: Callable[[discord.InteractionResponse, str], Awaitable[None]],
    ):
        options = list(map(build_select_option, pools))
        super().__init__(
            placeholder="Which pool are you intersted in...",
            min_values=1,
            max_values=1,
            options=options,
        )
        self._callback = callback

    async def callback(self, interaction: discord.Interaction):
        await self._callback(interaction.response, self.values[0])


class PoolsDropdown(discord.ui.View):
    def __init__(self, pools: List[LiquidityPool], callback):
        super().__init__()
        self.add_item(_PoolsDropdown(pools=pools, callback=callback))
