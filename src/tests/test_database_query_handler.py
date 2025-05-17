from pytest import mark
from src.scheme_for_validation import (
    DataForQuery,
    MessageInput,
    StockBrokenDeviceData,
    StockDeviceTable,
)
from src.utils import modificate_date_to_str


@mark.usefixtures("db_connect")
@mark.query_handler
class TestDatabaseQueryHandler:
    """Тест обработчика запросов к базе данных"""

    def test_transform_dict_from_data_query(self, db_query_handler):
        """тест: превращения словаря сырых данны в результат запроса"""

        data_from_bot = MessageInput(
            {("sd", "stock_device_id"): "99", ("d", "device_name"): "Laser Beam"}
        )
        result = db_query_handler.transform_dict_from_data_query(data_from_bot)

        assert result == [
            DataForQuery(
                prefix="sd",
                table_row="stock_device_id",
                row_value="99",
                build="stock_device_id='99'",  # type: ignore
            ),
            DataForQuery(
                prefix="d",
                table_row="device_name",
                row_value="Laser Beam",
                build="device_name='Laser Beam'",  # type: ignore
            ),
        ]

    def test_database_get_search_by_row(self, db_query_handler):
        """тест: запрос к базе данных для поиска строки"""

        data_from_bot = MessageInput(
            {("sd", "stock_device_id"): "1", ("d", "device_name"): "Laser Beam"}
        )
        result = db_query_handler.database_get_search_by_row(data_from_bot)

        assert result == [
            StockBrokenDeviceData(
                stock_device_id=1, device_name="Laser Beam", at_clean_date="27-4-2025"
            )
        ]

    def test_database_set_item(self, db_query_handler):
        """тест: запроса для добавления данных в бд"""

        data_from_bot = tuple(
            StockDeviceTable(
                stock_device_id=1, device_id=4, at_clean_date=modificate_date_to_str()
            )
            .model_dump()
            .values()
        )
        serch_item = MessageInput(
            {("sd", "stock_device_id"): "1", ("d", "device_name"): "Laser Beam"}
        )
        db_query_handler.database_set_item(data_from_bot)
        result = db_query_handler.database_get_search_by_row(serch_item)

        assert result == [
            StockBrokenDeviceData(
                stock_device_id=1, device_name="Laser Beam", at_clean_date="27-4-2025"
            )
        ]
