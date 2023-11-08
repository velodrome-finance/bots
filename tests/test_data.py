import pytest

from dotenv import load_dotenv

load_dotenv(".env.example")

from bots.settings import TOKEN_ADDRESS  # noqa
from bots.data import Token, Price, LiquidityPool  # noqa


@pytest.mark.asyncio
async def test_get_by_token_address():
    t = await Token.get_by_token_address(TOKEN_ADDRESS)
    assert t.token_address == TOKEN_ADDRESS
    assert t.listed is True


@pytest.mark.asyncio
async def test_get_prices():
    prices = await Price.get_prices([await Token.get_by_token_address(TOKEN_ADDRESS)])
    assert len(prices) == 1
    [price] = prices
    assert price.pretty_price != 0


@pytest.mark.asyncio
async def test_tvl():
    pools = await LiquidityPool.get_pools()
    tvl = await LiquidityPool.tvl(pools)
    assert tvl != 0


@pytest.mark.asyncio
async def test_fees():
    pools = await LiquidityPool.get_pools()
    fees = sum(map(lambda p: p.total_fees, pools))
    assert fees != 0
