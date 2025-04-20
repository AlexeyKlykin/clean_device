import logging
import sqlite3


logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

CREATE_TABLE_DEVICE_COMPANY = """CREATE TABLE IF NOT EXISTS device_company
    (company_id integer primary key AUTOINCREMENT,
    company_name text not null unique,
    producer_country text not null unique,
    description_company text)
"""

CREATE_TABLE_DEVICE_TYPE = """CREATE TABLE IF NOT EXISTS device_type
    (type_device_id integer primary key AUTOINCREMENT,
    type_title text not null unique,
    description_type text)
"""

CREATE_TABLE_DEVICE = """CREATE TABLE IF NOT EXISTS device
    (device_id integer primary key AUTOINCREMENT,
    device_name text not null unique,
    company_id integer,
    type_device_id integer,
    foreign key(company_id) references device_company(company_id),
    foreign key(type_device_id) references device_type(type_device_id))
"""

CREATE_TABLE_STOCK_DEVICE = """CREATE TABLE IF NOT EXISTS stock_device
    (stock_device_id integer primary key,
    at_clean_date text not null,
    device_id integer,
    foreign key(device_id) references device(device_id))
"""


class DBSqlite:
    def __init__(self, db_name: str) -> None:
        self.db_name = db_name

    def __enter__(self):
        create_table_list = [
            CREATE_TABLE_STOCK_DEVICE,
            CREATE_TABLE_DEVICE,
            CREATE_TABLE_DEVICE_COMPANY,
            CREATE_TABLE_DEVICE_TYPE,
        ]

        try:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.autocommit = True
            [self.conn.execute(item) for item in create_table_list]
            return self.conn

        except ConnectionError as err:
            raise err

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.conn:
                self.conn.close()

        except Exception:
            raise Exception(exc_type, exc_val, exc_tb)
