import logging
import os
import sys


from web3 import Web3
from async_lru import alru_cache


def cache_in_seconds(seconds: int):
  return alru_cache(ttl=seconds)

def normalize_address(address: str) -> str:
  return Web3.to_checksum_address(address.lower())

def load_local_json_as_string(relative_path: str) -> str:
  result = ""
  with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), relative_path)) as f:
    result = f.read()
  
  return result

# logging
LOGGING_LEVEL=os.getenv('LOGGING_LEVEL', 'DEBUG')
LOGGING_HANDLER = logging.StreamHandler(sys.stdout)
LOGGING_HANDLER.setFormatter(logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', '%Y-%m-%d %H:%M:%S', style='{'))
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(LOGGING_HANDLER)
LOGGER.setLevel(LOGGING_LEVEL)
