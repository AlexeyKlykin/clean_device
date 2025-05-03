from pytest import fixture
from src.db_app import (
    CREATE_TABLE_DEVICE,
    CREATE_TABLE_DEVICE_COMPANY,
    CREATE_TABLE_DEVICE_TYPE,
    CREATE_TABLE_STOCK_DEVICE,
    DBSqlite,
)
from src.query_interface import QueryInterface
from src.schema_for_validation import (
    DeviceCompanyTable,
    DeviceTable,
    DeviceTypeTable,
    OutputDeviceCompanyTable,
    OutputDeviceTable,
    OutputDeviceTypeTable,
    RowValue,
    StockBrokenDeviceData,
    StockDeviceTable,
    TableRow,
)

table_list = ["device", "device_type", "device_company", "stock_device"]

all_tables = (
    StockDeviceTable,
    DeviceTypeTable,
    DeviceTable,
    DeviceCompanyTable,
    OutputDeviceCompanyTable,
    OutputDeviceTable,
    OutputDeviceTypeTable,
    StockBrokenDeviceData,
)


@fixture
def db_connect():
    fp_lst = [
        "stock_device_test.sql",
        "device_test.sql",
        "device_company_test.sql",
        "device_type_test.sql",
    ]

    create_table_list = [
        CREATE_TABLE_STOCK_DEVICE,
        CREATE_TABLE_DEVICE,
        CREATE_TABLE_DEVICE_COMPANY,
        CREATE_TABLE_DEVICE_TYPE,
    ]

    with DBSqlite("clean_device_test.db") as conn:
        [conn.execute(item) for item in create_table_list]
        conn.commit()

        for fp in fp_lst:
            with open(fp, "r") as file:
                conn.executescript(file.read())
        conn.commit()

        yield conn

        for table in table_list:
            conn.execute(
                "UPDATE `sqlite_sequence` SET `seq` = 0 WHERE `name` = '%s'" % table
            )
            conn.execute("DELETE FROM '%s'" % table)
            conn.commit()


@fixture
def query_connect():
    qi = QueryInterface()
    qi.table = StockBrokenDeviceData
    return qi


@fixture
def data_from_query_connect():
    data_one = {TableRow("at_clean_date"): RowValue("30-4-2025")}
    return data_one
