from pytest import mark
from src.data_resolve_interface import DatabaseTableHandlerInterface
from src.schema_for_validation import (
    DeviceCompanyTable,
    DeviceTable,
    DeviceTypeTable,
    OutputDeviceCompanyTable,
    OutputDeviceTable,
    OutputDeviceTypeTable,
    RowValue,
    StockBrokenDeviceData,
    StockDeviceData,
    StockDeviceTable,
    TableRow,
)
from src.utils import modificate_date_to_str

testdata = [
    (
        StockDeviceTable,
        (RowValue("1"), RowValue("2"), modificate_date_to_str()),
        StockDeviceData,
        {TableRow("stock_device_id"): RowValue("1")},
        StockDeviceData(
            stock_device_id=1,
            device_name="Laser Beam",
            company_name="Light Craft",
            type_title="Beam",
            at_clean_date="27-4-2025",
        ),
    ),
    (
        DeviceTable,
        (RowValue("k50"), RowValue("1"), RowValue("2")),
        OutputDeviceTable,
        {
            TableRow("d.device_id"): RowValue("4"),
            TableRow("d.device_name"): RowValue("Laser Beam"),
        },
        OutputDeviceTable(
            device_id=4,
            device_name="Laser Beam",
            company_name="Light Craft",
            type_title="Beam",
        ),
    ),
    (
        DeviceTypeTable,
        (RowValue("Profile MP"), RowValue("Profile Description")),
        OutputDeviceTypeTable,
        {TableRow("type_title"): RowValue("Profile MP")},
        OutputDeviceTypeTable(
            type_device_id=5,
            type_title="Profile MP",
            type_description="Profile Description",
        ),
    ),
    (
        DeviceCompanyTable,
        (RowValue("Clay Taky"), RowValue("Spany"), RowValue("www.clay_paky.spain")),
        OutputDeviceCompanyTable,
        {TableRow("company_name"): RowValue("Clay Taky")},
        OutputDeviceCompanyTable(
            company_id=3,
            company_name="Clay Taky",
            producer_country="Spany",
            description_company="www.clay_paky.spain",
        ),
    ),
]

testdatamany = [
    (
        StockDeviceTable,
        [
            (RowValue("1"), RowValue("2"), modificate_date_to_str()),
            (RowValue("2"), RowValue("2"), modificate_date_to_str()),
        ],
        StockBrokenDeviceData,
        {
            TableRow("sd.at_clean_date"): RowValue("30-4-2025"),
        },
        StockBrokenDeviceData(
            stock_device_id=87,
            device_name="Prima Mythos",
            at_clean_date="30-4-2025",
        ),
    ),
    (
        DeviceTable,
        [
            (RowValue("k50"), RowValue("1"), RowValue("2")),
            (RowValue("k60"), RowValue("1"), RowValue("2")),
        ],
        OutputDeviceTable,
        {TableRow("device_name"): RowValue("k50")},
        OutputDeviceTable(
            device_id=2,
            device_name="K20",
            company_name="Clay Paky",
            type_title="Hybrid",
        ),
    ),
    (
        DeviceTypeTable,
        [
            (RowValue("Profile MP"), RowValue("Profile Description")),
            (RowValue("Profile MPs"), RowValue("Profile mps Description")),
        ],
        OutputDeviceTypeTable,
        (),
        OutputDeviceTypeTable(
            type_device_id=5,
            type_title="Profile MP",
            type_description="Profile Description",
        ),
    ),
    (
        DeviceCompanyTable,
        [
            (RowValue("Clay Taky"), RowValue("Spany"), RowValue("www.clay_paky.spain")),
            (RowValue("Play Taky"), RowValue("Kpany"), RowValue("www.Klay_paky.spain")),
        ],
        OutputDeviceCompanyTable,
        (),
        OutputDeviceCompanyTable(
            company_id=3,
            company_name="Clay Taky",
            producer_country="Spany",
            description_company="www.clay_paky.spain",
        ),
    ),
]

testdataupdate = [
    (
        StockDeviceTable,
        {
            TableRow("at_clean_date"): RowValue("02-5-2025"),
            TableRow("stock_device_status"): RowValue("0"),
        },
        {
            TableRow("stock_device_id"): RowValue("1"),
            TableRow("device_id"): RowValue("2"),
        },
        StockDeviceData,
        {
            TableRow("stock_device_id"): RowValue("1"),
            TableRow("device_name"): RowValue("Laser Beam"),
        },
        StockDeviceData(
            stock_device_id=1,
            device_name="Laser Beam",
            company_name="Light Craft",
            type_title="Beam",
            at_clean_date="27-4-2025",
        ),
    ),
]


@mark.db_table
class TestDatabaseTableHandlerInterface:
    """Тест обработка запросов к базе данных"""

    @mark.parametrize(
        "set_table, set_data, where_data, get_table, where_value, expected",
        testdataupdate,
    )
    def test_update_item(
        self,
        set_table,
        set_data,
        where_data,
        get_table,
        where_value,
        expected,
        db_interface,
    ):
        """тест: обновить один объект из базы"""

        db_interface.schema = set_table
        db_interface.update_item(set_data=set_data, where_data=where_data)

        db_interface.schema = get_table
        res = db_interface.get_item(where_data=where_value)

        assert res == expected

    @mark.parametrize("set_table, set_value, get_table, get_value, expected", testdata)
    def test_set_item(
        self, set_table, set_value, get_table, get_value, expected, db_interface
    ):
        """тест: добавления данных в бд"""

        db_interface.schema = set_table
        db_interface.set_item(set_value)

        db_interface.schema = get_table
        res = db_interface.get_item(where_data=get_value)

        assert res == expected

    @mark.parametrize(
        "set_table, set_value, get_table, get_value, expected", testdatamany
    )
    def test_set_items(
        self, set_table, set_value, get_table, get_value, expected, db_interface
    ):
        """тест: массовой вставки данных в таблицу"""

        db_interface.schema = set_table
        db_interface.set_items(set_value)

        db_interface.schema = get_table

        if get_value:
            res = db_interface.get_items(where_data=get_value)
        else:
            res = db_interface.get_items()

        assert expected in res
