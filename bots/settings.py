import os
from dotenv import load_dotenv

from .helpers import load_local_json_as_string, normalize_address

load_dotenv()

LP_SUGAR_ABI = load_local_json_as_string("abi/lp_sugar.json")
PRICE_ORACLE_ABI = load_local_json_as_string("abi/price_oracle.json")

DISCORD_TOKEN_PRICING = os.environ["DISCORD_TOKEN_PRICING"]
DISCORD_TOKEN_TVL = os.environ["DISCORD_TOKEN_TVL"]
DISCORD_TOKEN_FEES = os.environ["DISCORD_TOKEN_FEES"]
DISCORD_TOKEN_REWARDS = os.environ["DISCORD_TOKEN_REWARDS"]
DISCORD_TOKEN_COMMANDER = os.environ["DISCORD_TOKEN_COMMANDER"]

WEB3_PROVIDER_URI = os.environ["WEB3_PROVIDER_URI"]
LP_SUGAR_ADDRESS = os.environ["LP_SUGAR_ADDRESS"]
PRICE_ORACLE_ADDRESS = os.environ["PRICE_ORACLE_ADDRESS"]
PRICE_BATCH_SIZE = int(os.environ["PRICE_BATCH_SIZE"])

PROTOCOL_NAME = os.environ["PROTOCOL_NAME"]
APP_BASE_URL = os.environ["APP_BASE_URL"]

# token we are converting from
TOKEN_ADDRESS = normalize_address(os.environ["TOKEN_ADDRESS"])

CONNECTOR_TOKENS_ADDRESSES = list(
    map(
        lambda a: normalize_address(a),
        os.environ["CONNECTOR_TOKENS_ADDRESSES"].split(","),
    )
)

# token we are converting to
STABLE_TOKEN_ADDRESS = os.environ["STABLE_TOKEN_ADDRESS"]

BOT_TICKER_INTERVAL_MINUTES = int(os.environ["BOT_TICKER_INTERVAL_MINUTES"])
SUGAR_TOKENS_CACHE_MINUTES = int(os.environ["SUGAR_TOKENS_CACHE_MINUTES"])
SUGAR_LPS_CACHE_MINUTES = int(os.environ["SUGAR_LPS_CACHE_MINUTES"])
ORACLE_PRICES_CACHE_MINUTES = int(os.environ["ORACLE_PRICES_CACHE_MINUTES"])

GOOD_ENOUGH_PAGINATION_LIMIT = 2000

UI_POOL_STATS_THUMBNAIL = os.environ["UI_POOL_STATS_THUMBNAIL"]
