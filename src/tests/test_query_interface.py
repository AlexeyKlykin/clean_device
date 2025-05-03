from pytest import mark
from src.schema_for_validation import (
    RowValue,
    TableRow,
)

## не протестировано на всех типах запросов


@mark.query
class TestQuery:
    """Тест интерфейсов генерации запросов"""

    def test_transform_where_data(self, query_connect):
        """тест: вспомогательного метода для преобразования из словаря в строку"""

        all_item = {
            TableRow("d.device_id"): RowValue("1"),
            TableRow("d.device_name"): RowValue("k50"),
        }
        res = query_connect.transform_where_data(all_item)

        assert res == "d.device_id='1' and d.device_name='k50'"

        two_items = {
            TableRow("data_id"): RowValue("1"),
            TableRow("data_title"): RowValue("Clay"),
        }
        res = query_connect.transform_where_data(two_items)

        assert res == "data_id='1' and data_title='Clay'"

    def test_transform_list_rows(self, query_connect):
        """тест: вспомогательного метода для преобразования множества в строку"""

        one_item = {
            TableRow("data_id"),
        }
        res = query_connect.transform_list_rows(one_item)

        assert res == "data_id"

        two_items = [
            TableRow("data_id"),
            TableRow("data_title"),
        ]
        res = query_connect.transform_list_rows(two_items)

        assert res == "data_id, data_title"

    def test_query_show_all_broken_stock_devices_at_date(
        self, query_connect, data_from_query_connect
    ):
        """тест: строкового запроса для всех приборов в ремонте"""

        assert (
            query_connect.query_show_all_broken_stock_devices_at_date(
                data_from_query_connect
            )
            == "SELECT sd.stock_device_id, d.device_name, sd.at_clean_date \nFROM stock_device as sd\nLEFT JOIN device d ON d.device_id = sd.device_id\nWHERE at_clean_date='30-4-2025' and sd.stock_device_status = '0'\n"
        )

    def test_query_show_devices(self, query_connect, data_from_query_connect):
        """тест: строкового запроса всех приборов"""

        assert (
            query_connect.query_show_devices(where_data=data_from_query_connect)
            == "SELECT sd.stock_device_id, d.device_name, sd.at_clean_date\nFROM stock_device as sd\nLEFT JOIN device_company as dc ON dc.company_id = d.company_id\nLEFT JOIN device_type as dt ON dt.type_device_id = d.type_device_id\nWHERE at_clean_date='30-4-2025'"
        )

    def test_query_show_stock_devices(self, query_connect, data_from_query_connect):
        """тест: строкового запроса всех приборов на складе"""

        assert (
            query_connect.query_show_stock_devices(data_from_query_connect)
            == "SELECT sd.stock_device_id, d.device_name, sd.at_clean_date\nFROM stock_device as sd\nLEFT JOIN device d ON d.device_id = sd.device_id\nLEFT JOIN device_company dc ON dc.company_id = d.company_id\nLEFT JOIN device_type dt ON dt.type_device_id = d.type_device_id\nWHERE at_clean_date='30-4-2025'\n"
        )

    def test_query_get_data_by_value(self, query_connect, data_from_query_connect):
        """тест: строкового запроса получения данных по значению"""

        assert (
            query_connect.query_get_data_by_value(data_from_query_connect)
            == "SELECT stock_device_id, device_name, at_clean_date FROM stock_device as sd WHERE at_clean_date='30-4-2025'"
        )

    def test_query_update(self, query_connect):
        """тест: строкового запроса обновления данных"""

        where_data = {TableRow("type_id"): RowValue("1")}
        set_data = {TableRow("at_clean_date"): RowValue("30-4-2025")}

        assert (
            query_connect.query_update(where_data, set_data)
            == "UPDATE stock_device as sd SET type_id='1' WHERE at_clean_date='30-4-2025'"
        )

    def test_query_set(self, query_connect):
        """тест: строкового запроса добавления данных"""

        assert (
            query_connect.query_set()
            == "INSERT INTO stock_device as sd(stock_device_id, device_name, at_clean_date) VALUES (?, ?, ?)"
        )

    def test_query_get_all(self, query_connect):
        """тест: строкового запроса для получения всех данных"""

        assert (
            query_connect.query_get_all()
            == "SELECT stock_device_id, device_name, at_clean_date FROM stock_device as sd"
        )
