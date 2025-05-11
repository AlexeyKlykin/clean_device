from src.query_scheme import QuerySchemeForStockDevice
from src.scheme_for_validation import (
    DeviceTypeTable,
    RowValue,
    StockBrokenDeviceData,
    TableRow,
)


def test_scheme_class():
    d = DeviceTypeTable(type_title="Beams", type_description="description beams")
    assert d.class_mro() == DeviceTypeTable


def test_entry_struct_in_lst(db_connect):
    where_mogrif_data = {TableRow("sd.at_clean_date"): RowValue("30-4-2025")}

    query = QuerySchemeForStockDevice().query_get_device_by_status(
        where_data=where_mogrif_data, status="0"
    )

    cursor = db_connect.row_factory_for_connection(query[1])
    stock_devices = db_connect.get_all(query=query[0], cursor=cursor)

    assert all(isinstance(item, StockBrokenDeviceData) for item in stock_devices)
