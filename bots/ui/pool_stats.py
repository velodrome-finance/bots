from ..data import LiquidityPool
from ..helpers import format_percentage, format_currency, make_app_url
from ..settings import APP_BASE_URL


class PoolStats:
    async def render(self, pool: LiquidityPool, tvl: float) -> str:
        token0_fees = pool.token0_fees.amount_in_stable if pool.token0_fees else 0
        token1_fees = pool.token1_fees.amount_in_stable if pool.token1_fees else 0

        template_args = {
            "pool_symbol": pool.symbol,
            "pool_fee_percentage": format_percentage(pool.pool_fee_percentage),
            "apr": format_percentage(pool.apr(tvl)),
            "tvl": format_currency(tvl),
            "token0_volume": format_currency(
                pool.reserve0.amount if pool.reserve0 else 0,
                symbol=pool.token0.symbol,
                prefix=False,
            ),
            "token1_volume": format_currency(
                pool.reserve1.amount if pool.reserve1 else 0,
                symbol=pool.token1.symbol,
                prefix=False,
            ),
            "volume": format_currency(pool.volume),
            "fees": format_currency(token0_fees + token1_fees),
            "deposit_url": make_app_url(
                APP_BASE_URL,
                "/deposit",
                {
                    "token0": pool.token0.token_address,
                    "token1": pool.token1.token_address,
                    "stable": str(pool.is_stable).lower(),
                },
            ),
            "incentivize_url": make_app_url(
                APP_BASE_URL, "/incentivize", {"pool": pool.lp}
            ),
        }

        return """
> **{pool_symbol} ● Fee {pool_fee_percentage} ● {apr} APR**
> - ~{tvl} TVL
>   - {token0_volume}
>   - {token1_volume}
> - ~{volume} volume this epoch
> - ~{fees} fees this epoch
>
> [Deposit 🐖]({deposit_url}) ● [Incentivize 🙋]({incentivize_url})
""".format(
            **template_args
        )
