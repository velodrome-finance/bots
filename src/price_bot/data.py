from web3 import AsyncWeb3, AsyncHTTPProvider
from web3.constants import ADDRESS_ZERO
from dataclasses import dataclass
from typing import Tuple, List

from .settings import WEB3_PROVIDER_URI, LP_SUGAR_ADDRESS, LP_SUGAR_ABI, PRICE_ORACLE_ADDRESS, PRICE_ORACLE_ABI, CONNECTOR_TOKENS_ADDRESSES, STABLE_TOKEN_ADDRESS, SUGAR_TOKENS_CACHE_MINUTES, ORACLE_PRICES_CACHE_MINUTES
from .helpers import cache_in_seconds, normalize_address

w3 = AsyncWeb3(AsyncHTTPProvider(WEB3_PROVIDER_URI))

@dataclass(frozen=True)
class Token:
  """Data class for Token

  based on: https://github.com/velodrome-finance/sugar/blob/v2/contracts/LpSugar.vy#L17
  """

  token_address: str
  symbol: str
  decimals: int
  listed: bool

  @classmethod
  def from_tuple(cls, t: Tuple):
    (token_address, symbol, decimals, _, listed) = t
    return Token(token_address=normalize_address(token_address), symbol=symbol, decimals=decimals, listed=listed)

  @classmethod
  @cache_in_seconds(SUGAR_TOKENS_CACHE_MINUTES * 60)
  async def get_all_listed_tokens(cls):
    print("calling get_all_listed_tokens")
    sugar = w3.eth.contract(address=LP_SUGAR_ADDRESS, abi=LP_SUGAR_ABI)
    tokens = await sugar.functions.tokens(2000, 0, ADDRESS_ZERO).call()
    return list(filter(lambda t: t.listed, map(lambda t: Token.from_tuple(t), tokens)))

  @classmethod
  async def get_by_token_address(cls, token_address: str):
    normalized_address = normalize_address(token_address)
    tokens = await cls.get_all_listed_tokens()
    return next(t for t in tokens if t.token_address == normalized_address)


@dataclass(frozen=True)
class Price:
  """Data class for Token Price

  based on: https://github.com/velodrome-finance/oracle/blob/main/contracts/VeloOracle.sol
  """

  token: Token
  price: float

  @property
  def pretty_price(self) -> float:
    return round(self.price, 5)

  @classmethod
  @cache_in_seconds(ORACLE_PRICES_CACHE_MINUTES * 60)
  async def _get_prices(cls, tokens: Tuple[Token], stable_token: str, connector_tokens: Tuple[str]):
    print("calling pricer")
    price_oracle = w3.eth.contract(address=PRICE_ORACLE_ADDRESS, abi=PRICE_ORACLE_ABI)
    pricing_token_list = list(map(lambda t: t.token_address, tokens)) + list(connector_tokens) + [stable_token]
    prices = await price_oracle.functions.getManyRatesWithConnectors(len(tokens), pricing_token_list).call()

    results = []

    for cnt, price in enumerate(prices):
      # XX: decimals are auto set to 18
      # see https://github.com/velodrome-finance/oracle/blob/main/contracts/VeloOracle.sol#L126
      results.append(Price(token=tokens[cnt], price=price / 10**18))

    return results

  @classmethod
  async def get_prices(cls, tokens: List[Token], stable_token: str = STABLE_TOKEN_ADDRESS, connector_tokens: List[str] = CONNECTOR_TOKENS_ADDRESSES):
    # XX: lists are not cacheable, convert them to tuples so cache is happy
    return await cls._get_prices(tuple(tokens), stable_token, tuple(connector_tokens))