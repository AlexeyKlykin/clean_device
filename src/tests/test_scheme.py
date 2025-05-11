from src.query_scheme import QuerySchemeForStockDevice
from src.scheme_for_validation import (
    DeviceTypeTable,
    RowValue,
    StockBrokenDeviceData,
    TableRow,
    DataForQuery,
)


def test_scheme_class():
    d = DeviceTypeTable(type_title="Beams", type_description="description beams")
    assert d.class_mro() == DeviceTypeTable


def test_entry_struct_in_lst(db_connect):
    cleane_date = DataForQuery(
        prefix="sd",
        table_row=TableRow("at_clean_date"),
        row_value=RowValue("30-4-2025"),
    )
    status = DataForQuery(
        prefix="sd",
        table_row=TableRow("stock_device_status"),
        row_value=RowValue("1"),
    )

    query = QuerySchemeForStockDevice().query_get_search_with_device(
        where_data=[cleane_date, status]
    )

    cursor = db_connect.row_factory_for_connection(query[1])
    stock_devices = db_connect.get_all(query=query[0], cursor=cursor)

    assert all(isinstance(item, StockBrokenDeviceData) for item in stock_devices)


def test_where_data_for_query():
    data = DataForQuery(
        prefix="sd",
        table_row=TableRow("at_clean_date"),
        row_value=RowValue("30-4-2025"),
    )
    data_two = DataForQuery(
        prefix="d",
        table_row=TableRow("device_name"),
        row_value=RowValue("k20"),
    )
    where_data = [data, data_two]
    res = " and ".join([item.build for item in where_data])

    assert res == "sd.at_clean_date='30-4-2025' and d.device_name='k20'"
