import time
from datetime import datetime
from json import JSONDecodeError

import logging
import os
import pandas as pd
import requests
import sys
import numpy as np

try:
    from connection import ConnectionClient
except ModuleNotFoundError:
    sys.path.append(os.path.join(os.path.join(os.path.normpath(sys.path[0]), ".."), "tools"))
    from connection import ConnectionClient

logger = logging.getLogger('tipper')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class GetCoingeckoSymbolsData:
    def __init__(self):
        self.get_symbols_data()
        self.push_to_db()

    def get_symbols_data(self) -> pd.DataFrame:
        return pd.DataFrame([self.fetch_symbol_data_from_coingecko(row_id)
                             for row_id in self.get_symbols_data().id]).dropna()

    def fetch_symbol_data_from_coingecko(self, id_num) -> list:
        req = requests.get(self.get_symbol_url(id_num))
        try:
            resp = req.json()
        except JSONDecodeError:
            logger.info(f'''{datetime.now()} too many requests. waiting for new rate limits. currently at {id_num} need to wait {req.headers['Retry-After']} s.''')
            time.sleep(int(req.headers['Retry-After']))
            resp = requests.get(self.get_symbol_url(id_num)).json()
        try:
            return [resp['id'], resp['symbol'], resp['name'],  resp['sentiment_votes_up_percentage'],
                    resp['sentiment_votes_down_percentage'], resp['market_cap_rank'],
                    resp['market_data']['current_price']['usd'], resp['market_data']['market_cap']['usd']]
        except KeyError:
            return [np.nan] * 8

    @staticmethod
    def get_symbol_url(id_num) -> str:
        return f'https://api.coingecko.com/api/v3/coins/{id_num}?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false'

    def get_all_symbols(self) -> pd.DataFrame:
        return pd.DataFrame(
            requests.get(self.all_symbols_url()).json(),
            columns=['id', 'symbol', 'name'])

    @staticmethod
    def all_symbols_url() -> str:
        return 'https://api.coingecko.com/api/v3/coins/list'

    def push_to_db(self):
        df = self.get_symbols_data()


if __name__ == '__main__':
    symbols = GetCoingeckoSymbolsData()

