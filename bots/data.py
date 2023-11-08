import functools
import asyncio
from web3 import AsyncWeb3, AsyncHTTPProvider
from web3.constants import ADDRESS_ZERO
from dataclasses import dataclass
from typing import Tuple, List, Dict

from .settings import (
    WEB3_PROVIDER_URI,
    LP_SUGAR_ADDRESS,
    LP_SUGAR_ABI,
    PRICE_ORACLE_ADDRESS,
    PRICE_ORACLE_ABI,
    CONNECTOR_TOKENS_ADDRESSES,
    STABLE_TOKEN_ADDRESS,
    SUGAR_TOKENS_CACHE_MINUTES,
    ORACLE_PRICES_CACHE_MINUTES,
    PRICE_BATCH_SIZE,
    GOOD_ENOUGH_PAGINATION_LIMIT,
)
from .helpers import cache_in_seconds, normalize_address, chunk

w3 = AsyncWeb3(AsyncHTTPProvider(WEB3_PROVIDER_URI))


@dataclass(frozen=True)
class Token:
    """Data class for Token

    based on:
    https://github.com/velodrome-finance/sugar/blob/v2/contracts/LpSugar.vy#L17
    """

    token_address: str
    symbol: str
    decimals: int
    listed: bool

    def value_from_bigint(self, value: float) -> float:
        return value / 10**self.decimals

    @classmethod
    def from_tuple(cls, t: Tuple) -> "Token":
        (token_address, symbol, decimals, _, listed) = t
        return Token(
            token_address=normalize_address(token_address),
            symbol=symbol,
            decimals=decimals,
            listed=listed,
        )

    @classmethod
    @cache_in_seconds(SUGAR_TOKENS_CACHE_MINUTES * 60)
    async def get_all_listed_tokens(cls) -> List["Token"]:
        sugar = w3.eth.contract(address=LP_SUGAR_ADDRESS, abi=LP_SUGAR_ABI)
        tokens = await sugar.functions.tokens(
            GOOD_ENOUGH_PAGINATION_LIMIT, 0, ADDRESS_ZERO
        ).call()
        return list(
            filter(lambda t: t.listed, map(lambda t: Token.from_tuple(t), tokens))
        )

    @classmethod
    async def get_by_token_address(cls, token_address: str) -> "Token":
        """Get details for specific token

        Args:
            token_address (str): token address

        Returns:
            Token: target token or None
        """
        normalized_address = normalize_address(token_address)
        tokens = await cls.get_all_listed_tokens()
        return next(t for t in tokens if t.token_address == normalized_address)


@dataclass(frozen=True)
class Price:
    """Data class for Token Price

    based on:
    https://github.com/velodrome-finance/oracle/blob/main/contracts/VeloOracle.sol
    """

    token: Token
    price: float

    @property
    def pretty_price(self) -> float:
        return round(self.price, 5)

    @classmethod
    @cache_in_seconds(ORACLE_PRICES_CACHE_MINUTES * 60)
    async def _get_prices(
        cls, tokens: Tuple[Token], stable_token: str, connector_tokens: Tuple[str]
    ):
        price_oracle = w3.eth.contract(
            address=PRICE_ORACLE_ADDRESS, abi=PRICE_ORACLE_ABI
        )
        pricing_token_list = (
            list(map(lambda t: t.token_address, tokens))
            + list(connector_tokens)
            + [stable_token]
        )
        prices = await price_oracle.functions.getManyRatesWithConnectors(
            len(tokens), pricing_token_list
        ).call()

        results = []

        for cnt, price in enumerate(prices):
            # XX: decimals are auto set to 18
            # see
            # https://github.com/velodrome-finance/oracle/blob/main/contracts/VeloOracle.sol#L126
            results.append(Price(token=tokens[cnt], price=price / 10**18))

        return results

    @classmethod
    async def get_prices(
        cls,
        tokens: List[Token],
        stable_token: str = STABLE_TOKEN_ADDRESS,
        connector_tokens: List[str] = CONNECTOR_TOKENS_ADDRESSES,
    ) -> List["Price"]:
        """Get prices for tokens in target stable token

        Args:
            tokens (List[Token]): tokens to get prices for
            stable_token (str, optional): stable token to price in.
            Defaults to STABLE_TOKEN_ADDRESS.
            connector_tokens (List[str], optional): connector tokens to use for pricing.
            Defaults to CONNECTOR_TOKENS_ADDRESSES.

        Returns:
            List: list of Price objects
        """
        batches = await asyncio.gather(
            *map(
                lambda ts: cls._get_prices(
                    # XX: lists are not cacheable, convert them to tuples so lru cache is happy
                    tuple(ts),
                    stable_token,
                    tuple(connector_tokens),
                ),
                list(chunk(tokens, PRICE_BATCH_SIZE)),
            )
        )
        return functools.reduce(lambda l1, l2: l1 + l2, batches, [])


@dataclass(frozen=True)
class Amount:
    token: Token
    amount: float
    price: Price

    @classmethod
    def build(
        cls,
        address: str,
        amount: float,
        tokens: Dict[str, Token],
        prices: Dict[str, "Price"],
    ) -> "Amount":
        address = normalize_address(address)

        if address not in tokens or address not in prices:
            return None

        token = tokens[address]

        return Amount(
            token=token, amount=token.value_from_bigint(amount), price=prices[address]
        )

    @property
    def amount_in_stable(self) -> float:
        return self.amount * self.price.price


@dataclass(frozen=True)
class LiquidityPool:
    """Data class for Liquidity Pool

    based on:
    https://github.com/velodrome-finance/sugar/blob/v2/contracts/LpSugar.vy#L31
    """

    lp: str
    symbol: str
    token0: Token
    reserve0: float
    token1: Token
    reserve1: float
    token0_fees: Amount
    token1_fees: Amount

    @classmethod
    def from_tuple(
        cls, t: Tuple, tokens: Dict[str, Token], prices: Dict[str, Price]
    ) -> "LiquidityPool":
        token0 = normalize_address(t[5])
        token1 = normalize_address(t[8])
        token0_fees = t[23]
        token1_fees = t[24]

        return LiquidityPool(
            lp=normalize_address(t[0]),
            symbol=t[1],
            token0=tokens.get(token0),
            reserve0=t[6],
            token1=tokens.get(token1),
            reserve1=t[9],
            token0_fees=Amount.build(token0, token0_fees, tokens, prices),
            token1_fees=Amount.build(token1, token1_fees, tokens, prices),
        )

    @classmethod
    async def get_pools(cls) -> List["LiquidityPool"]:
        tokens = await Token.get_all_listed_tokens()
        prices = await Price.get_prices(tokens)

        tokens = {t.token_address: t for t in tokens}
        prices = {price.token.token_address: price for price in prices}

        sugar = w3.eth.contract(address=LP_SUGAR_ADDRESS, abi=LP_SUGAR_ABI)
        pools = await sugar.functions.all(
            GOOD_ENOUGH_PAGINATION_LIMIT, 0, ADDRESS_ZERO
        ).call()
        return list(
            filter(
                lambda p: p is not None,
                map(lambda p: LiquidityPool.from_tuple(p, tokens, prices), pools),
            )
        )

    @classmethod
    async def tvl(cls, pools) -> float:
        result = 0

        tokens = await Token.get_all_listed_tokens()
        prices = await Price.get_prices(tokens)
        prices = {price.token.token_address: price for price in prices}

        for pool in pools:
            t0 = pool.token0
            t1 = pool.token1

            if t0:
                result += (
                    t0.value_from_bigint(pool.reserve0) * prices[t0.token_address].price
                )

            if t1:
                result += (
                    t1.value_from_bigint(pool.reserve1) * prices[t1.token_address].price
                )

        return result

    @property
    def total_fees(self) -> float:
        result = 0

        if self.token0_fees:
            result += self.token0_fees.amount_in_stable
        if self.token1_fees:
            result += self.token1_fees.amount_in_stable

        return result
