import pandas as pd
from sqlalchemy import create_engine
import credentials as cred


class ConnectionClient:
    def __init__(self):
        self.postgres()

    @staticmethod
    def db_string():
        return f'postgresql://{cred.postgres_cred[0]}:{cred.postgres_cred[1]}@{cred.postgres_address}:5432/postgres'

    def postgres(self):
        return create_engine(self.db_string())


if __name__ == '__main__':
    q = 'select * from public.global_crypto_data'
    print(pd.read_sql_query(q, con=ConnectionClient().postgres()))