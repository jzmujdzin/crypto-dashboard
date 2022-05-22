import pandas as pd, sys, os
from sqlalchemy import create_engine

try:
    from configs import credentials as cred
except ModuleNotFoundError:
    sys.path.append(os.path.join(os.path.join(os.path.normpath(sys.path[0]), ".."), "configs"))


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
