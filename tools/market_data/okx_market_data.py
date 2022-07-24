import requests, sys, os
import pandas as pd
from datetime import datetime, timedelta

try:
    from tools.market_data.abstract_market_data import GetExchangeData
except ModuleNotFoundError:
    sys.path.append(
        os.path.join(os.path.join(os.path.normpath(sys.path[0]), ".."), "market_data")
    )
    from tools.market_data.abstract_market_data import GetExchangeData


class GetOKXData(GetExchangeData):
    def get_ticker_info(self, base, quote, interval, days_back):
        df = pd.DataFrame(
            requests.get(
                self.get_ticker_info_url(base, quote, interval, days_back)
            ).json()["data"]
        )
        df = df.apply(pd.to_numeric)
        df[0] = pd.to_datetime(df[0], unit="ms")
        return df.rename(columns=self.get_column_mapping()).sort_values(by="date_time")

    def get_ticker_info_url(self, base, quote, interval, days_back):
        return f"https://www.okx.com/api/v5/market/candles?instId={base}-{quote}&bar={self.get_interval(interval)}&before={self.get_start_time(days_back)}"

    def get_start_time(self, days_back=0, minutes_back=0):
        return (
            str(
                (
                    datetime.now() - timedelta(days=days_back, minutes=minutes_back)
                ).timestamp()
            ).split(".")[0]
            + "000"
        )

    def get_interval(self, interval):
        return interval.upper()

    def get_column_mapping(self):
        return {
            0: "date_time",
            1: "open",
            2: "high",
            3: "low",
            4: "close",
            5: "volumeBase",
            6: "volume",
        }
