import requests
import pandas as pd
import os

session = requests.Session()

def run_request(link):
    finished = False
    while not finished:
        try:
            response = session.get(link)
            finished = True
        except:
            finished = False
            continue
    return response.json()


def get_active_tokens(data):
    key_name = 'active_token_query_id'
    # Get all active tokens
    url = f"https://api.dune.com/api/v1/query/{data[key_name]}/results?api_key=" + os.environ.get('DUNE_KEY')
    print(url)
    print(f"Query used for fetching active tokens :  https://dune.com/queries/{data[key_name]}" )
    response = pd.DataFrame(run_request(url))
    actual_data = response.loc['rows', 'result']
    df = pd.DataFrame.from_dict(actual_data)
    df.set_index('token', inplace=True)
    return df