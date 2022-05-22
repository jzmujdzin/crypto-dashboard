from abc import ABC, abstractmethod


class GetExchangeData(ABC):

    @abstractmethod
    def get_ticker_info(self):
        pass

    @abstractmethod
    def get_ticker_info_url(self):
        pass

    @abstractmethod
    def get_start_time(self):
        pass

    @abstractmethod
    def get_interval(self):
        pass

    @abstractmethod
    def get_column_mapping(self):
        pass

