import discord
from ..data import LiquidityPool
from ..helpers import format_percentage, format_currency


class PoolStats:
    async def render(self, pool: LiquidityPool, tvl: float):
        embed = discord.Embed(
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

        embed.add_field(name="", value="", inline=False)

        # Volume

        embed.add_field(name="Volume", value="", inline=False)
        embed.add_field(
            name="  ",
            value=format_currency(pool.volume),
            inline=True,
        )
        embed.add_field(
            name="  ",
            value=format_currency(
                pool.token0_volume, symbol=pool.token0.symbol, prefix=False
            ),
            inline=True,
        )
        embed.add_field(
            name="  ",
            value=format_currency(
                pool.token1_volume, symbol=pool.token1.symbol, prefix=False
            ),
            inline=True,
        )
        embed.add_field(name="", value="", inline=False)

        # Fees

        embed.add_field(name="Fees", value="", inline=False)
        embed.add_field(
            name="  ",
            value=format_currency(
                pool.token0_fees.amount_in_stable + pool.token1_fees.amount_in_stable
            ),
            inline=True,
        )
        embed.add_field(
            name="  ",
            value=format_currency(
                pool.token0_fees.amount, symbol=pool.token0.symbol, prefix=False
            ),
            inline=True,
        )
        embed.add_field(
            name="  ",
            value=format_currency(
                pool.token1_fees.amount, symbol=pool.token1.symbol, prefix=False
            ),
            inline=True,
        )
        embed.add_field(name="", value="", inline=False)

        # Pool balance

        embed.add_field(name="Pool Balance", value="", inline=False)
        embed.add_field(
            name="  ",
            value=format_currency(
                pool.reserve0.amount, symbol=pool.token0.symbol, prefix=False
            ),
            inline=True,
        )
        embed.add_field(
            name="  ",
            value=format_currency(
                pool.reserve1.amount, symbol=pool.token1.symbol, prefix=False
            ),
            inline=True,
        )

        return embed
