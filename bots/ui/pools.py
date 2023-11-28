from typing import List, Callable, Awaitable
import discord
from ..data import LiquidityPool
from .emojis import Emojis

intents = discord.Intents.default()
intents.message_content = True


def build_select_option(
    interaction: discord.Interaction, pool: LiquidityPool
) -> discord.SelectOption:
    emojis = Emojis(interaction.client.emojis)
    return discord.SelectOption(
        label=pool.symbol, value=pool.lp, emoji=emojis.get("pool", "🏊‍♀️")
    )


class _PoolsDropdown(discord.ui.Select):
    def __init__(
        self,
        interaction: discord.Interaction,
        pools: List[LiquidityPool],
        callback: Callable[[discord.Interaction, str], Awaitable[None]],
    ):
        options = list(map(lambda p: build_select_option(interaction, p), pools))
        super().__init__(
            placeholder="Which pool are you intersted in...",
            min_values=1,
            max_values=1,
            options=options,
        )
        self._callback = callback

    async def callback(self, interaction: discord.Interaction):
        await self._callback(interaction, self.values[0])


class PoolsDropdown(discord.ui.View):
    """Pool dropdown UI to present available pools to Discord users"""

    def __init__(
        self, interaction: discord.Interaction, pools: List[LiquidityPool], callback
    ):
        """Builds a pool dropdown

        Args:
            interaction (discord.Interaction): interaction object from the chat
            pools (List[LiquidityPool]): pools to display
            callback (function): callback for when a pool is selected
        """
        super().__init__()
        self.add_item(
            _PoolsDropdown(interaction=interaction, pools=pools, callback=callback)
        )
