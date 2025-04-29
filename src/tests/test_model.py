from src.schema_for_validate import (
    DeviceTypeTable,
)


def test_device_type_table_rows():
    assert DeviceTypeTable.table_rows() == [
        "type_title",
        "type_description",
    ]


def test_count_rows_table_type():
    assert len(DeviceTypeTable.table_rows()) == 2
