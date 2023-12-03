from .data import LiquidityPool, LiquidityPoolEpoch
from .helpers import is_address
from .ui import PoolsDropdown, PoolStats

import discord
from discord.ext import commands


class _CommanderBot(commands.Bot):
    """Commander bot instance to handle / commands"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="/", intents=intents)

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")
        await bot.tree.sync()


bot = _CommanderBot()


def CommanderBot() -> commands.Bot:
    # keep our commander as a singleton
    return bot


async def on_select_pool(
    interaction: discord.Interaction,
    address_or_pool: str | LiquidityPool,
):
    """Handle pool selection and reply with a pool stats embed

    Args:
        interaction (discord.Interaction): chat interaction
        address_or_pool (str | LiquidityPool): pool address or instance
    """
    pool = (
        await LiquidityPool.by_address(address_or_pool)
        if isinstance(address_or_pool, str)
        else address_or_pool
    )
    tvl = await LiquidityPool.tvl([pool])
    pool_epoch = await LiquidityPoolEpoch.fetch_for_pool(pool.lp)
    await interaction.response.send_message(
        embed=await PoolStats(interaction.client.emojis).render(pool, tvl, pool_epoch)
    )


@bot.tree.command(name="pool", description="Get data for specific pool")
@discord.app_commands.describe(
    address_or_query="Pool address or search query",
)
async def pool(interaction: discord.Interaction, address_or_query: str):
    """Pool command handler: show specific pool or pool selector

    Args:
        interaction (discord.Interaction): chat interaction
        address_or_query (str): command input
    """
    if is_address(address_or_query):
        # if /pool receives specific pool address,
        # show the pool immediately or show an error
        # message if it does not exist

        pool = await LiquidityPool.by_address(address_or_query)

        if pool is not None:
            await on_select_pool(interaction, pool)
        else:
            await interaction.response.send_message(
                f"No pool found with this address: {address_or_query}"
            )
        return

    pools = await LiquidityPool.search(address_or_query)

    if len(pools) == 1:
        # got exact match, show the pool
        await on_select_pool(interaction, pools[0])
        return

    # search returned several pools, show them in a dropdown
    await interaction.response.send_message(
        "Choose a pool:",
        view=PoolsDropdown(
            interaction=interaction, pools=pools, callback=on_select_pool
        ),
    )
