from src.schema_for_validation import (
    DeviceTypeTable,
    StockBrokenDeviceData,
)
from src.utils import validate_date


def test_device_type_table_rows():
    assert DeviceTypeTable.table_rows() == [
        "type_title",
        "type_description",
    ]


def test_count_rows_table_type():
    assert len(DeviceTypeTable.table_rows()) == 2


def test_broken_model():
    sbdd = StockBrokenDeviceData.table_alias()
    assert sbdd == ["sd.stock_device_id", "d.device_name", "sd.at_clean_date"]


def test_valid_date():
    date_one = "11-04-2025"
    date_two = "01-4-2025"
    date_three = "01-433-20256"

    res_one = validate_date(date_one)
    res_two = validate_date(date_two)
    res_three = validate_date(date_three)

    assert res_one
    assert res_two
    assert not res_three
