from pytest import mark

from src.query_scheme import (
    QuerySchemeForDevice,
    QuerySchemeForDeviceCompany,
    QuerySchemeForDeviceType,
    QuerySchemeForStockDevice,
)
from src.scheme_for_validation import DataForQuery, RowValue, TableRow


data_for_table_stock_device = [
    (
        None,
        "SELECT sd.stock_device_id, d.device_name, dc.company_name, dt.type_title, sd.max_lamp_hours, sd.at_clean_date\nFROM stock_device as sd\nLEFT JOIN device d ON d.device_id = sd.device_id\nLEFT JOIN device_company dc ON dc.company_id = d.company_id\nLEFT JOIN device_type dt ON dt.type_device_id = d.type_device_id\n",
    ),
    (
        DataForQuery(
            prefix="sd",
            table_row=TableRow("at_clean_date"),
            row_value=RowValue("30-4-2025"),
        ),
        "SELECT sd.stock_device_id, d.device_name, dc.company_name, dt.type_title, sd.max_lamp_hours, sd.at_clean_date\nFROM stock_device as sd\nLEFT JOIN device d ON d.device_id = sd.device_id\nLEFT JOIN device_company dc ON dc.company_id = d.company_id\nLEFT JOIN device_type dt ON dt.type_device_id = d.type_device_id\nWHERE sd.at_clean_date='30-4-2025'\n",
    ),
    (
        None,
        "SELECT sd.stock_device_id, d.device_name, dc.company_name, dt.type_title, sd.max_lamp_hours, sd.at_clean_date\nFROM stock_device as sd\nLEFT JOIN device d ON d.device_id = sd.device_id\nLEFT JOIN device_company dc ON dc.company_id = d.company_id\nLEFT JOIN device_type dt ON dt.type_device_id = d.type_device_id\n",
    ),
]

data_for_table_device = [
    (
        None,
        "SELECT device_id, device_name, company_name, type_title\nFROM device as d\nLEFT JOIN device_company dc ON dc.company_id = d.company_id\nLEFT JOIN device_type dt ON dt.type_device_id = d.type_device_id\n",
    ),
    (
        DataForQuery(
            prefix="dc",
            table_row=TableRow("company_name"),
            row_value=RowValue("Clay Paky"),
        ),
        "SELECT d.device_id, d.device_name, dc.company_name, dt.type_title\nFROM device as d\nLEFT JOIN device_company dc ON dc.company_id = d.company_id\nLEFT JOIN device_type dt ON dt.type_device_id = d.type_device_id\nWHERE dc.company_name='Clay Paky'\n",
    ),
    (
        None,
        "SELECT device_id, device_name, company_name, type_title\nFROM device as d\nLEFT JOIN device_company dc ON dc.company_id = d.company_id\nLEFT JOIN device_type dt ON dt.type_device_id = d.type_device_id\n",
    ),
]

data_for_table_device_company = [
    (
        DataForQuery(
            prefix="dc",
            table_row=TableRow("company_name"),
            row_value=RowValue("Clay Paky"),
        ),
        "SELECT company_id, company_name, producer_country, description_company \nFROM device_company as dc\nWHERE dc.company_name='Clay Paky'\n",
    ),
    (
        None,
        "SELECT company_id, company_name, producer_country, description_company FROM device_company as dc",
    ),
]

data_for_table_type_device = [
    (
        DataForQuery(
            prefix="dt", table_row=TableRow("type_title"), row_value=RowValue("Beam")
        ),
        "SELECT type_device_id, type_title, type_description, lamp_type \nFROM device_type as dt\nWHERE dt.type_title='Beam'\n",
    ),
    (
        None,
        "SELECT type_device_id, type_title, type_description, lamp_type FROM device_type as dt",
    ),
]

data_device_by_status = [
    (
        [
            DataForQuery(
                prefix="sd",
                table_row=TableRow("at_clean_date"),
                row_value=RowValue("30-4-2025"),
            ),
            DataForQuery(
                prefix="sd",
                table_row=TableRow("stock_device_status"),
                row_value=RowValue("1"),
            ),
        ],
        "SELECT sd.stock_device_id, d.device_name, sd.at_clean_date\nFROM stock_device as sd\nLEFT JOIN device d ON d.device_id = sd.device_id\nWHERE sd.stock_device_status='1' and sd.at_clean_date='30-4-2025'",
    ),
    (
        [
            DataForQuery(
                prefix="sd",
                table_row=TableRow("at_clean_date"),
                row_value=RowValue("30-4-2025"),
            ),
            DataForQuery(
                prefix="sd",
                table_row=TableRow("stock_device_status"),
                row_value=RowValue("0"),
            ),
        ],
        "SELECT sd.stock_device_id, d.device_name, sd.at_clean_date\nFROM stock_device as sd\nLEFT JOIN device d ON d.device_id = sd.device_id\nWHERE sd.stock_device_status='0' and sd.at_clean_date='30-4-2025'",
    ),
]


@mark.query_table
class TestQuerySchemeForStockDevice:
    """Класс тест для схемы приборов на складе"""

    def test_query_get_search_with_device_type(self):
        """тест: запроса прибора на складе по типу"""

        query = QuerySchemeForStockDevice()
        dn = DataForQuery(
            prefix="d", table_row=TableRow("device_name"), row_value=RowValue("K20")
        )
        dt = DataForQuery(
            prefix="dt",
            table_row=TableRow("type_title"),
            row_value=RowValue("Beam"),
        )
        where_data = [dn, dt]
        result = query.query_get_search_with_device_type(where_data)

        assert (
            result[0]
            == "SELECT sd.stock_device_id, d.device_name, sd.at_clean_date\nFROM stock_device as sd\nLEFT JOIN device d ON d.device_id = sd.device_id\nLEFT JOIN device_type dt ON dt.type_device_id = d.type_device_id\nWHERE d.device_name='K20' and dt.type_title='Beam'"
        )

    def test_query_get_search_with_device_company(self):
        """тест: запроса прибора на складе по компании"""

        query = QuerySchemeForStockDevice()

        dn = DataForQuery(
            prefix="d", table_row=TableRow("device_name"), row_value=RowValue("K20")
        )
        dc = DataForQuery(
            prefix="dc",
            table_row=TableRow("company_name"),
            row_value=RowValue("Clay Paky"),
        )
        where_data = [dn, dc]
        result = query.query_get_search_with_device_company(where_data)

        assert (
            result[0]
            == "SELECT sd.stock_device_id, d.device_name, sd.at_clean_date\nFROM stock_device as sd\nLEFT JOIN device d ON d.device_id = sd.device_id\nLEFT JOIN device_company dc ON dc.company_id = d.company_id\nWHERE d.device_name='K20' and dc.company_name='Clay Paky'"
        )

    @mark.parametrize("where_data, expected", data_for_table_stock_device)
    def test_query_get(self, where_data, expected):
        """тест: формирования запросов для приборов на складе"""

        query = QuerySchemeForStockDevice()
        result = query.query_get(where_data=where_data)

        assert result[0] == expected

    def test_query_set(self):
        """тест: формирования запроса для вставки данных"""

        query = QuerySchemeForStockDevice()
        result = query.query_set()

        assert (
            result[0]
            == "INSERT INTO stock_device as sd (stock_device_id, device_id, max_lamp_hours, at_clean_date) VALUES (?, ?, ?, ?)"
        )

    def test_query_update(self):
        """тест: формирования запроса для обновления данных"""

        query = QuerySchemeForStockDevice()
        sdi = DataForQuery(
            prefix="sd",
            table_row=TableRow("stock_device_id"),
            row_value=RowValue("1"),
        )
        dn = DataForQuery(
            prefix="d",
            table_row=TableRow("device_name"),
            row_value=RowValue("K20"),
        )
        cd = DataForQuery(
            prefix="sd",
            table_row=TableRow("at_clean_date"),
            row_value=RowValue("30-4-2025"),
        )
        where_data = [sdi, dn]
        result = query.query_update(where_data=where_data, set_data=cd)

        assert (
            result[0]
            == "UPDATE stock_device as sd SET sd.at_clean_date='30-4-2025' WHERE sd.stock_device_id='1' and d.device_name='K20'"
        )

    @mark.parametrize("where_data, expected", data_device_by_status)
    def query_get_search_with_device(self, where_data, expected):
        """тест: формирование строкового запроса для получения данных склодского прибора по статусу"""

        query = QuerySchemeForStockDevice()
        result = query.query_get_search_with_device(where_data=where_data)

        assert result[0] == expected


@mark.query_table
class TestQuerySchemeForDevice:
    """Класс тест для схемы приборов"""

    @mark.parametrize("where_data, expected", data_for_table_device)
    def test_query_get(self, where_data, expected):
        """тест: формирования запросов для приборов на складе"""

        query = QuerySchemeForDevice()
        result = query.query_get(where_data=where_data)

        assert result[0] == expected

    def test_query_set(self):
        """тест: формирования запроса для вставки данных"""

        query = QuerySchemeForDevice()
        result = query.query_set()

        assert (
            result[0]
            == "INSERT INTO device as d (device_name, company_id, type_device_id) VALUES (?, ?, ?)"
        )

    def test_query_update(self):
        """тест: формирования запроса для обновления данных"""

        query = QuerySchemeForDevice()
        where_data = DataForQuery(
            prefix="d", table_row=TableRow("device_name"), row_value=RowValue("K20")
        )
        set_data = DataForQuery(
            prefix="d", table_row=TableRow("device_name"), row_value=RowValue("K30")
        )
        result = query.query_update(where_data=where_data, set_data=set_data)

        assert (
            result[0]
            == "UPDATE device as d SET d.device_name='K30' WHERE d.device_name='K20'"
        )


@mark.query_table
class TestQuerySchemeForDeviceCompany:
    """Класс тест для схемы компании производителя"""

    @mark.parametrize("where_data, expected", data_for_table_device_company)
    def test_query_get(self, where_data, expected):
        """тест: формирования запросов для компании производителя"""

        query = QuerySchemeForDeviceCompany()
        result = query.query_get(where_data=where_data)

        assert result[0] == expected

    def test_query_set(self):
        """тест: формирования запроса для вставки данных"""

        query = QuerySchemeForDeviceCompany()
        result = query.query_set()

        assert (
            result[0]
            == "INSERT INTO device_company as dc (company_name, producer_country, description_company) VALUES (?, ?, ?)"
        )

    def test_query_update(self):
        """тест: формирования запроса для обновления данных"""

        query = QuerySchemeForDeviceCompany()
        where_data = DataForQuery(
            prefix="dc",
            table_row=TableRow("company_name"),
            row_value=RowValue("Clay Paky"),
        )
        set_data = DataForQuery(
            prefix="dc",
            table_row=TableRow("company_name"),
            row_value=RowValue("Light Craft"),
        )
        result = query.query_update(where_data=where_data, set_data=set_data)

        assert (
            result[0]
            == "UPDATE device_company as dc SET dc.company_name='Light Craft' WHERE dc.company_name='Clay Paky'"
        )


@mark.query_table
class TestQuerySchemeForTypeDevice:
    """Класс тест для схемы типа прибора"""

    @mark.parametrize("where_data, expected", data_for_table_type_device)
    def test_query_get(self, where_data, expected):
        """тест: формирования запросов для типов прибора"""

        query = QuerySchemeForDeviceType()
        result = query.query_get(where_data=where_data)

        assert result[0] == expected

    def test_query_set(self):
        """тест: формирования запроса для вставки данных"""

        query = QuerySchemeForDeviceType()
        result = query.query_set()

        assert (
            result[0]
            == "INSERT INTO device_type as dt (type_title, type_description, lamp_type) VALUES (?, ?, ?)"
        )

    def test_query_update(self):
        """тест: формирования запроса для обновления данных"""

        query = QuerySchemeForDeviceType()
        where_data = DataForQuery(
            prefix="dt", table_row=TableRow("type_title"), row_value=RowValue("Beam")
        )
        set_data = DataForQuery(
            prefix="dt", table_row=TableRow("type_title"), row_value=RowValue("Beams")
        )
        result = query.query_update(where_data=where_data, set_data=set_data)

        assert (
            result[0]
            == "UPDATE device_type as dt SET dt.type_title='Beams' WHERE dt.type_title='Beam'"
        )
