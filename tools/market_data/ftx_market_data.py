import requests
import pandas as pd
from abstract_market_data import GetExchangeData
from datetime import datetime, timedelta


class GetFTXData(GetExchangeData):

    def get_ticker_info(self, base, quote, interval, days_back):
        df = pd.DataFrame(requests.get(self.get_ticker_info_url(base, quote, interval, days_back)).json()['result'])
        df = df.apply(pd.to_numeric)
        df['startTime'] = pd.to_datetime(df.startTime)
        return df.rename(columns=self.get_column_mapping())

    def get_ticker_info_url(self, base, quote, interval, days_back):
        return f'https://ftx.com/api/markets/{base}/{quote}/candles?resolution={self.get_interval(interval)}&start_time={self.get_start_time(days_back)}'

    def get_start_time(self, days_back=0, minutes_back=0):
        return str((datetime.now() - timedelta(days=days_back, minutes=minutes_back)).timestamp()).split('.')[0]

    def get_interval(self, interval):
        if interval[-1:] == 's':
            return int(interval[:-1])
        elif interval[-1:] == 'm':
            return int(interval[:-1]) * 60
        elif interval[-1:] == 'h':
            return int(interval[:-1]) * 3600

    def get_column_mapping(self):
        return {"startTime": "date_time", "time": "timestamp"}