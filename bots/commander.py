from .data import LiquidityPool
from .helpers import is_address
from .ui import PoolsDropdown, PoolStats

import discord
from discord.ext import commands


class _CommanderBot(commands.Bot):
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
    return bot


async def on_select_pool(
    response: discord.InteractionResponse,
    address_or_pool: str | LiquidityPool,
):
    pool = (
        await LiquidityPool.by_address(address_or_pool)
        if isinstance(address_or_pool, str)
        else address_or_pool
    )
    tvl = await LiquidityPool.tvl([pool])
    await response.send_message(
        await PoolStats().render(pool, tvl), suppress_embeds=True
    )


@bot.tree.command(name="pool", description="Get data for specific pool")
@discord.app_commands.describe(
    address_or_query="Pool address or search query",
)
async def pool(interaction: discord.Interaction, address_or_query: str):
    if is_address(address_or_query):
        pool = await LiquidityPool.by_address(address_or_query)

        if pool is not None:
            await on_select_pool(interaction.response, pool)
        else:
            await interaction.response.send_message(
                f"No pool found with this address: {address_or_query}"
            )
        return

    pools = await LiquidityPool.search(address_or_query)

    await interaction.response.send_message(
        "Choose a pool:", view=PoolsDropdown(pools=pools, callback=on_select_pool)
    )
