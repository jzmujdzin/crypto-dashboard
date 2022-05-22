import pandas as pd
import requests
from tools.connection import ConnectionClient
import logging
from datetime import datetime
import psycopg2

logger = logging.getLogger('tipper')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class GetCoingeckoGlobalCryptoData:
    def __init__(self):
        self.push_to_db()

    def get_global_crypto_data(self):
        """Returns dataframe with the most important crypto market data"""
        logger.info(f'{datetime.now()} Requesting coingecko data')
        gcd = requests.get(self.get_global_crypto_data_url()).json()['data']
        logger.info(f'{datetime.now()} Creating dataframe from coingecko data')
        return pd.DataFrame({'timestamp': [pd.to_datetime(gcd['updated_at'], unit='s')],
                             'total_volume_usd': [gcd['total_volume']['usd']],
                             'active_cryptocurrencies': [gcd['active_cryptocurrencies']],
                             'market_cap_usd': [gcd['total_market_cap']['usd']],
                             'btc_market_cap_perc': [gcd['market_cap_percentage']['btc']],
                             'eth_market_cap_perc': [gcd['market_cap_percentage']['eth']],
                             'alts_market_cap_perc': [100 - gcd['market_cap_percentage']['btc']
                                                      - gcd['market_cap_percentage']['eth']]})

    def push_to_db(self):
        """Pushes new data to DB if that data was not already sent"""
        try:
            self.get_global_crypto_data().\
                to_sql('global_crypto_data', ConnectionClient().postgres(), if_exists='append', index=False, schema='public')
            logger.info(f'{datetime.now()} Sent data to postgres')
        except psycopg2.errors.UniqueViolation:
            logger.info(f'{datetime.now()} Data with that timestamp is already present in postgres')

    @staticmethod
    def get_global_crypto_data_url():
        """Returns URL to Global section of coingecko api"""
        return 'https://api.coingecko.com/api/v3/global'


if __name__ == '__main__':
    GetCoingeckoGlobalCryptoData()
