import asyncio
import logging

from .settings import (
    DISCORD_TOKEN_PRICING,
    DISCORD_TOKEN_TVL,
    DISCORD_TOKEN_FEES,
    DISCORD_TOKEN_REWARDS,
    TOKEN_ADDRESS,
    STABLE_TOKEN_ADDRESS,
    PROTOCOL_NAME,
)
from .data import Token, LiquidityPool
from .helpers import LOGGING_HANDLER, LOGGING_LEVEL, format_currency, format_percentage
from .price import PriceBot
from .tvl import TVLBot
from .fees import FeesBot
from .rewards import RewardsBot


import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True


# Defines a custom Select containing colour options
# that the user can choose. The callback function
# of this class is called when the user changes their choice
class Dropdown(discord.ui.Select):
    def __init__(self):
        # Set the options that will be presented inside the dropdown
        options = [
            discord.SelectOption(
                label="Red", description="Your favourite colour is red", emoji="🟥"
            ),
            discord.SelectOption(
                label="Green", description="Your favourite colour is green", emoji="🟩"
            ),
            discord.SelectOption(
                label="Blue", description="Your favourite colour is blue", emoji="🟦"
            ),
        ]

        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the dropdown options. We defined this above
        super().__init__(
            placeholder="Choose your favourite colour...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        # Use the interaction object to send a response message containing
        # the user's favourite colour or choice. The self object refers to the
        # Select object, and the values attribute gets a list of the user's
        # selected options. We only want the first one.
        await interaction.response.send_message(
            f"Your favourite colour is {self.values[0]}"
        )


class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(Dropdown())


bot = commands.Bot(command_prefix=commands.when_mentioned_or("/"), intents=intents)


@bot.command()
async def pool(ctx, *args):
    print(">>>>>>>>>>>>>>>>>> test command")

    # Create the view containing our dropdown
    view = DropdownView()

    # Sending a message containing our view
    await ctx.send("Choose your pool:", view=view)

    if len(args) == 0:
        await ctx.send("Missing pool address: should be /pool POOL_ADDRESS_HERE")
    else:
        pool = await LiquidityPool.by_address(args[0])
        if pool is None:
            await ctx.send("Nothing found")
        else:
            print(pool)
            tvl = await LiquidityPool.tvl([pool])
            embedVar = discord.Embed(
                title=f"{pool.symbol}",
                description=" | ".join(
                    [
                        f"{'Stable Pool' if pool.is_stable else 'Volatile Pool'}",
                        f"Trading fee: {format_percentage(pool.pool_fee_percentage)}",
                        f"TVL: ~{format_currency(tvl)}",
                        f"APR: {format_percentage(pool.apr(tvl))}",
                    ]
                ),
                color=0xFFFFFF,
            )

            embedVar.add_field(name="", value="", inline=False)

            # Volume

            embedVar.add_field(name="Volume", value="", inline=False)
            embedVar.add_field(
                name="  ",
                value=format_currency(pool.volume),
                inline=True,
            )
            embedVar.add_field(
                name="  ",
                value=format_currency(
                    pool.token0_volume, symbol=pool.token0.symbol, prefix=False
                ),
                inline=True,
            )
            embedVar.add_field(
                name="  ",
                value=format_currency(
                    pool.token1_volume, symbol=pool.token1.symbol, prefix=False
                ),
                inline=True,
            )
            embedVar.add_field(name="", value="", inline=False)

            # Fees

            embedVar.add_field(name="Fees", value="", inline=False)
            embedVar.add_field(
                name="  ",
                value=format_currency(
                    pool.token0_fees.amount_in_stable
                    + pool.token1_fees.amount_in_stable
                ),
                inline=True,
            )
            embedVar.add_field(
                name="  ",
                value=format_currency(
                    pool.token0_fees.amount, symbol=pool.token0.symbol, prefix=False
                ),
                inline=True,
            )
            embedVar.add_field(
                name="  ",
                value=format_currency(
                    pool.token1_fees.amount, symbol=pool.token1.symbol, prefix=False
                ),
                inline=True,
            )
            embedVar.add_field(name="", value="", inline=False)

            # Pool balance

            embedVar.add_field(name="Pool Balance", value="", inline=False)
            embedVar.add_field(
                name="  ",
                value=format_currency(
                    pool.reserve0.amount, symbol=pool.token0.symbol, prefix=False
                ),
                inline=True,
            )
            embedVar.add_field(
                name="  ",
                value=format_currency(
                    pool.reserve1.amount, symbol=pool.token1.symbol, prefix=False
                ),
                inline=True,
            )

            await ctx.send(embed=embedVar)


async def main():
    """Main function."""

    # configure discord logging handler
    discord_logger = logging.getLogger("discord")
    discord_logger.setLevel(LOGGING_LEVEL)
    discord_logger.addHandler(LOGGING_HANDLER)

    token = await Token.get_by_token_address(TOKEN_ADDRESS)
    stable = await Token.get_by_token_address(STABLE_TOKEN_ADDRESS)

    # price_bot = PriceBot(source_token=token, target_token=stable)
    tvl_bot = TVLBot(protocol_name=PROTOCOL_NAME)
    # fees_bot = FeesBot(protocol_name=PROTOCOL_NAME)
    # rewards_bot = RewardsBot(protocol_name=PROTOCOL_NAME)

    # await bot.start(DISCORD_TOKEN_REWARDS)

    await asyncio.gather(
        bot.start(DISCORD_TOKEN_TVL),
        # price_bot.start(DISCORD_TOKEN_PRICING),
        # fees_bot.start(DISCORD_TOKEN_FEES),
        # tvl_bot.start(DISCORD_TOKEN_TVL),
        #    rewards_bot.start(DISCORD_TOKEN_REWARDS),
    )


if __name__ == "__main__":
    asyncio.run(main())
