import os

from src.db_app import (
    CREATE_TABLE_DEVICE,
    CREATE_TABLE_DEVICE_COMPANY,
    CREATE_TABLE_DEVICE_TYPE,
    CREATE_TABLE_STOCK_DEVICE,
    DBSqlite,
)
from src.secret import secrets


def set_full_data():
    fp_lst = [
        "stock_device.sql",
        "device.sql",
        "device_company.sql",
        "device_type.sql",
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

    except Exception as err:
        raise err


if __name__ == "__main__":
    set_full_data()
