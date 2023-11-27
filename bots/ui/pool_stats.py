from typing import Sequence
import discord
from ..data import LiquidityPool, LiquidityPoolEpoch
from ..helpers import format_percentage, format_currency, make_app_url
from ..settings import APP_BASE_URL, UI_POOL_STATS_THUMBNAIL, PROTOCOL_NAME
from .emojis import Emojis


class PoolStats:
    """Pool stats embded UI to visualize a pool;
    for it to look nice make sure you load custom emojis to your Discord server"""

    def __init__(self, emojis: Sequence[discord.Emoji]):
        self.emojis = Emojis(emojis)

    async def render(
        self, pool: LiquidityPool, tvl: float, pool_epoch: LiquidityPoolEpoch
    ) -> discord.Embed:
        """renders pool stats into a discord.Embed

        Returns:
            discord.Embed: discord embed UI ready to be sent
        """
        token0_fees = pool.token0_fees.amount_in_stable if pool.token0_fees else 0
        token1_fees = pool.token1_fees.amount_in_stable if pool.token1_fees else 0

        apr = pool.apr(tvl)

        deposit_url = make_app_url(
            APP_BASE_URL,
            "/deposit",
            {
                "token0": pool.token0.token_address.lower(),
                "token1": pool.token1.token_address.lower(),
                "stable": str(pool.is_stable).lower(),
            },
        )

        emojis = {
            "dashgrey": self.emojis.get("dashgrey", "·"),
            "dashwhite": self.emojis.get("dashwhite", "●"),
            "volume": self.emojis.get("volume", ":droplet:"),
            "apr": self.emojis.get("apr", ":chart_with_upwards_trend:"),
            "incentives": self.emojis.get("incentives", ":carrot:"),
            "emissions": self.emojis.get("emissions", ":zap:"),
            "space": self.emojis.get("space", " "),
            "deposit": self.emojis.get("deposit", ":pig2:"),
            "coinplaceholder": self.emojis.get("coinplaceholder", ":coin:"),
        }

        token0_volume_coin = format_currency(
            pool.reserve0.amount if pool.reserve0 else 0,
            symbol=pool.token0.symbol,
            prefix=False,
        )
        token0_volume_stable = format_currency(
            pool.reserve0.amount_in_stable if pool.reserve0 else 0
        )
        token1_volume_coin = format_currency(
            pool.reserve1.amount if pool.reserve1 else 0,
            symbol=pool.token1.symbol,
            prefix=False,
        )
        token1_volume_stable = format_currency(
            pool.reserve1.amount_in_stable if pool.reserve1 else 0
        )
        emissions_coin = format_currency(
            pool.emissions.amount, symbol=pool.emissions.token.symbol, prefix=False
        )
        emissions_stable = format_currency(pool.emissions.amount_in_stable)

        embed = discord.Embed()

        embed.set_thumbnail(url=UI_POOL_STATS_THUMBNAIL)

        # Header row with pool symbol
        # and TVL + Fee Below
        fee_percentage_str = format_percentage(pool.pool_fee_percentage)
        embed.add_field(
            name=f"{pool.symbol}",
            value=f"TVL {format_currency(tvl)} · Fee: {fee_percentage_str}",
            inline=False,
        )

        # vertical space
        embed.add_field(name="", value=f"{emojis['space']}", inline=False)

        token0_coin_icon = self.emojis.get(
            pool.token0.symbol.lower(), emojis["coinplaceholder"]
        )

        # token0 reserve: top row in coin
        # bottom row in stable
        embed.add_field(
            name=f"{token0_coin_icon} {token0_volume_coin}{emojis['space'] * 3}",
            value=f"{emojis['dashgrey']} _~{token0_volume_stable}_",
            inline=True,
        )

        token1_coin_icon = self.emojis.get(
            pool.token1.symbol.lower(), emojis["coinplaceholder"]
        )

        # token1 reserve: top row in coin
        # bottom row in stable
        embed.add_field(
            name=f"{token1_coin_icon} {token1_volume_coin}",
            value=f"{emojis['dashgrey']} _~{token1_volume_stable}_",
            inline=True,
        )

        # vertical space
        embed.add_field(name="", value="", inline=False)

        # Volume
        # top row: pool volume
        # bottom row: fees
        volume_str = format_currency(pool.volume)
        volume_with_fees_str = format_currency(token0_fees + token1_fees)
        embed.add_field(
            name=f"{emojis['volume']} Volume",
            value=" ".join(
                [
                    f"{emojis['dashwhite']} {volume_str}\n{emojis['dashgrey']}",
                    f"_{volume_with_fees_str} in fees_",
                ]
            ),
            inline=True,
        )

        # Incentives
        # top row: total bribes
        # bottom row: total bribes + total fees
        # XX: this seems OFF, should we pull this from LiquidityPoolEpoch instead?
        incentives_str = format_currency(pool_epoch.total_bribes)
        incentives_with_fees_str = format_currency(
            pool_epoch.total_bribes + pool_epoch.total_fees
        )
        embed.add_field(
            name=f"{emojis['incentives']} Incentives",
            value="\n".join(
                [
                    f"{emojis['dashwhite']} {incentives_str}",
                    f"{emojis['dashgrey']} _{incentives_with_fees_str} with fees_",
                ]
            ),
            inline=True,
        )

        # vertical space
        embed.add_field(name="", value="", inline=False)

        # Emissions
        # top row: emissions in coin
        # bottom row: emissions in stable
        embed.add_field(
            name=f"{emojis['emissions']} Emissions",
            value="\n".join(
                [
                    f"{emojis['dashwhite']} {emissions_coin}",
                    f"{emojis['dashgrey']} _~{emissions_stable}_",
                ]
            ),
            inline=True,
        )

        # APR
        # APR in percent
        embed.add_field(
            name=f"{emojis['apr']} APR",
            value=f"{emojis['dashwhite']} {format_percentage(apr)}",
            inline=True,
        )

        # vertical space
        embed.add_field(name="", value="", inline=False)

        # link to deposit page
        embed.add_field(
            name="",
            value=f"{emojis['deposit']} [Deposit on {PROTOCOL_NAME}]({deposit_url})",
            inline=False,
        )

        return embed
