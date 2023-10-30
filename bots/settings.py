import os
from dotenv import load_dotenv

from .helpers import load_local_json_as_string, normalize_address

load_dotenv()

LP_SUGAR_ABI = load_local_json_as_string("abi/lp_sugar.json")
PRICE_ORACLE_ABI = load_local_json_as_string("abi/price_oracle.json")

DISCORD_TOKEN_PRICING = os.environ["DISCORD_TOKEN_PRICING"]
WEB3_PROVIDER_URI = os.environ["WEB3_PROVIDER_URI"]
LP_SUGAR_ADDRESS = os.environ["LP_SUGAR_ADDRESS"]
PRICE_ORACLE_ADDRESS = os.environ["PRICE_ORACLE_ADDRESS"]

# token we are converting from
TOKEN_ADDRESS = normalize_address(os.environ["TOKEN_ADDRESS"])

CONNECTOR_TOKENS_ADDRESSES = list(
    map(
        lambda a: normalize_address(a),
        os.environ["CONNECTOR_TOKENS_ADDRESSES"].split(","),
    )
)

# token we are converting to
STABLE_TOKEN_SYMBOL = os.environ["STABLE_TOKEN_SYMBOL"]
STABLE_TOKEN_ADDRESS = os.environ["STABLE_TOKEN_ADDRESS"]

BOT_TICKER_INTERVAL_MINUTES = int(os.environ["BOT_TICKER_INTERVAL_MINUTES"])
SUGAR_TOKENS_CACHE_MINUTES = int(os.environ["SUGAR_TOKENS_CACHE_MINUTES"])
ORACLE_PRICES_CACHE_MINUTES = int(os.environ["ORACLE_PRICES_CACHE_MINUTES"])
