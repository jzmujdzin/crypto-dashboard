import requests, sys, os
import pandas as pd
from datetime import datetime, timedelta
try:
    from tools.market_data.abstract_market_data import GetExchangeData
except ModuleNotFoundError:
    sys.path.append(os.path.join(os.path.join(os.path.normpath(sys.path[0]), ".."), "market_data"))
    from tools.market_data.abstract_market_data import GetExchangeData


class GetBinanceData(GetExchangeData):

    def get_ticker_info(self, base, quote, interval, days_back):
        df = pd.DataFrame(requests.get(self.get_ticker_info_url(base, quote, interval, days_back)).json())
        df = df.apply(pd.to_numeric)
        df[0] = pd.to_datetime(df[0], unit='ms')
        return df.rename(columns=self.get_column_mapping())

    def get_ticker_info_url(self, base, quote, interval, days_back):
        return f'https://api.binance.com/api/v3/klines?symbol={base}{quote}&interval={self.get_interval(interval)}&startTime={self.get_start_time(days_back)}'

    def get_start_time(self, days_back=0, minutes_back=0):
        return str((datetime.now() - timedelta(days=days_back, minutes=minutes_back)).timestamp()).split('.')[0] + '000'

    def get_interval(self, interval):
        return interval

    def get_column_mapping(self):
        return {0: 'date_time', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume', 6: 'close_timestamp',
                7: 'quote_volume', 8: 'trades_count', 9: 'taker_base', 10: 'taker_quote', 11: 'excess_col'}