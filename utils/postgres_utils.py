import pandas as pd
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine
from typing import List, Dict


def create_postgres_engine(host: str, port: int, dbname: str, user: str, password: str) -> Engine:
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
    engine = create_engine(url)
    return engine


def list_postgres_tables(engine: Engine) -> List[str]:
    inspector = inspect(engine)
    return inspector.get_table_names()


def extract_table_data(engine: Engine, table_name: str, limit: int = 10000) -> pd.DataFrame:
    # Limit to 10k rows by default for safety
    query = f'SELECT * FROM "{table_name}" LIMIT {limit}'
    df = pd.read_sql(query, engine)
    return df 