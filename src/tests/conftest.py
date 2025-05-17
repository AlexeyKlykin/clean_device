from pytest import fixture
from src.data_handler import DatabaseQueryHandler
from src.database_interface import DataBaseInterface
from src.query_scheme import (
    CREATE_TABLE_DEVICE,
    CREATE_TABLE_DEVICE_COMPANY,
    CREATE_TABLE_DEVICE_TYPE,
    CREATE_TABLE_STOCK_DEVICE,
    QuerySchemeForStockDevice,
)

table_list = ["device", "device_type", "device_company", "stock_device"]
fp_lst = [
    "data_cache/stock_device_test.sql",
    "data_cache/device_test.sql",
    "data_cache/device_company_test.sql",
    "data_cache/device_type_test.sql",
]
create_table_list = [
    CREATE_TABLE_STOCK_DEVICE,
    CREATE_TABLE_DEVICE,
    CREATE_TABLE_DEVICE_COMPANY,
    CREATE_TABLE_DEVICE_TYPE,
]


@fixture
def db_connect():
    with DataBaseInterface("clean_device_test.db") as conn:
        conn.fill_in_the_table(fp_lst=fp_lst, create_table_list=create_table_list)

        yield conn

        conn.clean_table(table_list=table_list)


@fixture
def db_query_handler():
    dqh = DatabaseQueryHandler(
        db_name="clean_device_test.db", query_handler=QuerySchemeForStockDevice()
    )
    yield dqh
