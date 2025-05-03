from src.db_app import DBSqlite
from src.schema_for_validation import (
    FabricRowFactory,
    OutputDeviceCompanyTable,
    StockDeviceTable,
    TableRow,
)


def test_work_connect_db_sqlite():
    """тест: работы DBSqlite"""

    sql_query_select = "SELECT name FROM sqlite_master WHERE type='table'"

    with DBSqlite("clean_device_test.db") as conn:
        conn.execute(sql_query_select)
        cursor = conn.cursor()
        cursor.execute(sql_query_select)
        res = cursor.fetchall()

        assert res == [
            ("stock_device",),
            ("sqlite_sequence",),
            ("device",),
            ("device_company",),
            ("device_type",),
        ]


def test_row_factory(db_connect):
    """тест: доступа к фабрике строк в бд"""
    fabric = FabricRowFactory()
    fabric.choice_row_factory = StockDeviceTable
    db_connect.row_factory = fabric.choice_row_factory

    assert db_connect.row_factory.__name__ == "stock_device_factory"


def test_set_work():
    s = {
        TableRow("stock_device_id"),
        TableRow("device_id"),
        TableRow("stock_device_id"),
    }

    assert s == {TableRow("stock_device_id"), TableRow("device_id")}
    assert isinstance(s, set)


def test_table_rows_method():
    sdbd = OutputDeviceCompanyTable.table_rows()

    assert sdbd == [
        "company_id",
        "company_name",
        "producer_country",
        "description_company",
    ]
