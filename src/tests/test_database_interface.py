from pytest import mark

from src.database_interface import DataBaseInterface

from src.query_scheme import (
    QuerySchemeForDevice,
    QuerySchemeForDeviceCompany,
    QuerySchemeForDeviceType,
    QuerySchemeForStockDevice,
)
from src.schema_for_validation import (
    DeviceCompanyTable,
    DeviceTable,
    DeviceTypeTable,
    OutputDeviceCompanyTable,
    OutputDeviceTable,
    OutputDeviceTypeTable,
    RowValue,
    StockDeviceTable,
    StockDeviceData,
    TableRow,
)


row_factory_for_conn_data = [
    (StockDeviceTable, "StockDeviceTable"),
    (StockDeviceData, "StockDeviceData"),
    (OutputDeviceTypeTable, "OutputDeviceTypeTable"),
    (OutputDeviceTable, "OutputDeviceTable"),
    (OutputDeviceCompanyTable, "OutputDeviceCompanyTable"),
    (DeviceTypeTable, "DeviceTypeTable"),
    (DeviceTable, "DeviceTable"),
    (DeviceCompanyTable, "DeviceCompanyTable"),
]

database_set_data = [
    (
        QuerySchemeForDeviceType(),
        DeviceTypeTable(type_title="Beams", type_description="description beams"),
        "select * from device_type where type_title='Beams'",
    ),
    (
        QuerySchemeForDeviceCompany(),
        DeviceCompanyTable(
            company_name="Clay Baky",
            producer_country="Spany",
            description_company="description company Clay Baky",
        ),
        "select * from device_company where company_name='Clay Baky'",
    ),
    (
        QuerySchemeForDevice(),
        DeviceTable(device_name="K60", company_id=1, type_device_id=1),
        "select * from device where device_name='K60'",
    ),
    (
        QuerySchemeForStockDevice(),
        StockDeviceTable(
            stock_device_id=9000,
            device_id=8,
            max_lamp_hours=1200,
            at_clean_date="30-4-2025",
        ),
        "select * from stock_device where stock_device_id='9000'",
    ),
]

database_get_data = [
    (QuerySchemeForDeviceType(), None, OutputDeviceTypeTable),
    (
        QuerySchemeForDeviceType(),
        {TableRow("type_title"): RowValue("Beam")},
        OutputDeviceTypeTable,
    ),
    (QuerySchemeForDeviceCompany(), None, OutputDeviceCompanyTable),
    (
        QuerySchemeForDeviceCompany(),
        {TableRow("company_name"): RowValue("Clay Paky")},
        OutputDeviceCompanyTable,
    ),
    (QuerySchemeForDevice(), None, OutputDeviceTable),
    (
        QuerySchemeForDevice(),
        {TableRow("device_name"): RowValue("K20")},
        OutputDeviceTable,
    ),
    (QuerySchemeForStockDevice(), None, StockDeviceData),
    (
        QuerySchemeForStockDevice(),
        {TableRow("stock_device_id"): RowValue("1")},
        StockDeviceData,
    ),
]

database_update_data = [
    (
        QuerySchemeForDeviceType(),
        {TableRow("type_title"): RowValue("Beams")},
        {TableRow("type_title"): RowValue("Beam")},
        "select * from device_type where type_title='Beams'",
        DeviceTypeTable,
    ),
    (
        QuerySchemeForDeviceCompany(),
        {TableRow("company_name"): RowValue("Clay Paku")},
        {TableRow("company_name"): RowValue("Clay Paky")},
        "select * from device_company where company_name='Clay Paku'",
        DeviceCompanyTable,
    ),
    (
        QuerySchemeForDevice(),
        {TableRow("device_name"): RowValue("K60")},
        {TableRow("device_name"): RowValue("K20")},
        "select * from device where device_name='K60'",
        DeviceTable,
    ),
    (
        QuerySchemeForStockDevice(),
        {TableRow("stock_device_id"): RowValue("8000")},
        {TableRow("stock_device_id"): RowValue("1")},
        "select * from stock_device where stock_device_id='8000'",
        StockDeviceTable,
    ),
]


@mark.database_interface
class TestDatabaseInterface:
    """Класс работы с базой данных"""

    @mark.parametrize("scheme, expected", row_factory_for_conn_data)
    def test_row_factory_for_connection(self, scheme, expected):
        """тест: подключения фабрики строк к базе"""

        with DataBaseInterface("clean_device_test.db") as conn:
            cursor = conn.row_factory_for_connection(scheme)

            assert cursor.row_factory.__name__ == expected  # type: ignore

    @mark.parametrize("query, set_data, query_result", database_set_data)
    def test_set(self, query, set_data, query_result, db_connect):
        """тест: добавление данных в базу"""

        raw_query = query.query_set()
        cursor = db_connect.row_factory_for_connection(raw_query[1])
        db_connect.set(
            cursor=cursor,
            query=raw_query[0],
            set_data=tuple(set_data.model_dump().values()),
        )
        cur = db_connect.conn.cursor()
        cur.execute(query_result)
        result = cur.fetchone()

        assert result == set_data

    @mark.parametrize("query, where_data, expected", database_get_data)
    def test_get(self, query, where_data, expected, db_connect):
        """тест: получения данных из базы"""

        raw_query = query.query_get(where_data=where_data)
        cursor = db_connect.row_factory_for_connection(raw_query[1])
        result = db_connect.get(cursor=cursor, query=raw_query[0])

        assert isinstance(result, expected)

    @mark.parametrize(
        "query, set_data, where_data, query_result, expected", database_update_data
    )
    def test_update(
        self, query, set_data, where_data, query_result, expected, db_connect
    ):
        """тест: обновления данных в таблицах"""

        raw_query = query.query_update(set_data=set_data, where_data=where_data)
        cursor = db_connect.row_factory_for_connection(raw_query[1])
        db_connect.update(
            cursor=cursor,
            query=raw_query[0],
        )
        cur = db_connect.conn.cursor()
        cur.execute(query_result)
        result = cur.fetchone()

        assert isinstance(result, expected)
