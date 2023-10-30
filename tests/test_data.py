import pytest

from dotenv import load_dotenv
load_dotenv(".env.example")

from bots.settings import TOKEN_ADDRESS, STABLE_TOKEN_ADDRESS
from bots.data import Token, Price

@pytest.mark.asyncio
async def test_get_by_token_address():
    t = await Token.get_by_token_address(TOKEN_ADDRESS)
    assert t.token_address == TOKEN_ADDRESS
    assert t.listed == True

@pytest.mark.asyncio
async def test_get_prices():
    prices = await Price.get_prices([await Token.get_by_token_address(TOKEN_ADDRESS)])
    assert len(prices) == 1
    [price] = prices
    assert price.pretty_price != 0