from src.schema_for_validate import (
    RowValue,
    TableRow,
)


class TestQuery:
    """Тест интерфейсов генерации запросов"""

    def test_query_to_retrieve_all_broken_devices_at_date(self, query_interface):
        """тест: строкового запроса для всех приборов в ремонте"""

        clean_date = "at_clean_date=30-4-25"

        assert (
            query_interface.query_to_retrieve_all_broken_devices_at_date(clean_date)
            == "SELECT sd.stock_device_id, d.device_name, sd.at_clean_date\nFROM device_type sd\nLEFT JOIN device d ON d.device_id = sd.device_id\nWHERE at_clean_date=30-4-25 and sd.stock_device_status = '0'\n"
        )

    def test_query_mark_device(self, query_interface):
        """тест: строкового запроса передачи марки для устройства"""

        stock_device_id: str = "stock_device_id=35"
        device_id: str = "device_id=1"
        mark: str = "0"
        assert (
            query_interface.query_mark_device(stock_device_id, device_id, mark)
            == "UPDATE device_type SET stock_device_status = '0'\nWHERE stock_device_id=35 and device_id=1\n"
        )

    def test_query_update_data_by_two_arg(self, query_interface):
        """тест: строкового запроса об обновлении данныз в таблице"""

        raw_set_data = {TableRow("stock_device_id"): RowValue("26")}
        raw_where_data_one = {TableRow("stock_device_id"): RowValue("25")}
        raw_where_data_two = {TableRow("device_id"): RowValue("1")}

        assert (
            query_interface.query_update_data_by_two_arg(
                raw_set_data, raw_where_data_one, raw_where_data_two
            )
            == "UPDATE device_type SET stock_device_id='26' WHERE stock_device_id='25' and device_id='1'"
        )

    def test_query_get_stock_device(self, query_interface):
        """тест: строкового запроса о получении собранных данных о приборе на складе"""

        stock_device_id = 1
        device_name = "k20"
        assert (
            query_interface.query_get_stock_device(stock_device_id, device_name)
            == "SELECT sd.stock_device_id, d.device_name, dc.company_name, dt.type_title, sd.at_clean_date\nFROM stock_device sd\nLEFT JOIN device d ON d.device_id = sd.device_id\nLEFT JOIN device_company dc ON dc.company_id = d.company_id\nLEFT JOIN device_type dt ON dt.type_device_id = d.type_device_id\nWHERE sd.stock_device_id = '1' and d.device_name = 'k20'\n"
        )

    def test_query_get_data_by_value_for_type_device(self, query_interface):
        """тест: получения строкового запроса на выполнение получения
        данных по параметрам в таблице типов приборов"""

        where_data = {TableRow("type_id"): RowValue("1")}

        assert (
            query_interface.query_get_data_by_value(where_data)
            == "SELECT type_title, type_description FROM device_type WHERE type_id='1'"
        )

    def test_query_set_data_for_type_device(self, query_interface):
        """тест: получение строкового запроса
        для добавления данных в таблице типо приборов"""

        assert (
            query_interface.query_set()
            == "INSERT INTO device_type(type_title, type_description) VALUES (?, ?)"
        )

    def test_query_get_all_for_type_device(self, query_interface):
        """тест: строковый запрос на получение
        всех данных в таблице типов приборов"""

        assert (
            query_interface.query_get_all()
            == "SELECT type_title, type_description FROM device_type"
        )

    def test_query_update_type_device(self, query_interface):
        """тест: строковый запрос на апдейт данных в таблице типов приборов"""

        raw_set_data = {TableRow("type_title"): RowValue("beam")}
        raw_where_data = {TableRow("type_id"): RowValue("1")}

        assert (
            query_interface.query_update(
                raw_set_data=raw_set_data, raw_where_data=raw_where_data
            )
            == "UPDATE device_type SET type_title='beam' WHERE type_id='1'"
        )
