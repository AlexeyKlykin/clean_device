import os
import sqlite3
import logging

from src.query_scheme import (
    CREATE_TABLE_DEVICE,
    CREATE_TABLE_DEVICE_COMPANY,
    CREATE_TABLE_DEVICE_TYPE,
    CREATE_TABLE_STOCK_DEVICE,
    DBSqlite,
)
from src.secret import secrets

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


def set_full_data():
    fp_lst = [
        "data_cache/stock_device.sql",
        "data_cache/device.sql",
        "data_cache/device_company.sql",
        "data_cache/device_type.sql",
    ]

    create_table_list = [
        CREATE_TABLE_STOCK_DEVICE,
        CREATE_TABLE_DEVICE,
        CREATE_TABLE_DEVICE_COMPANY,
        CREATE_TABLE_DEVICE_TYPE,
    ]

    try:
        if os.environ.get("DB_NAME"):
            db_name = os.environ["DB_NAME"]
        else:
            db_name = secrets["DB_NAME"]

        if isinstance(db_name, str):
            with DBSqlite(db_name) as conn:
                [conn.execute(item) for item in create_table_list]
                conn.commit()

                for fp in fp_lst:
                    with open(fp, "r") as file:
                        conn.executescript(file.read())

    except sqlite3.IntegrityError:
        logger.warning("Данные уже есть в дб")


if __name__ == "__main__":
    set_full_data()
