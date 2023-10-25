import os
import json

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
  
