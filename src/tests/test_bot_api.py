from pytest import mark

from src.bot_api import APIBotDb
from src.schema_for_validation import (
    OutputDeviceCompanyTable,
    OutputDeviceTable,
    OutputDeviceTypeTable,
    StockBrokenDeviceData,
    StockDeviceData,
)
from src.utils import modificate_date_to_str


date = modificate_date_to_str()
data_lst_device_from_stockpile = [
    (
        {"at_clean_date": "30-4-2025"},
        [
            StockBrokenDeviceData(
                stock_device_id=87,
                device_name="Prima Mythos",
                at_clean_date="30-4-2025",
            ),
            StockBrokenDeviceData(
                stock_device_id=128,
                device_name="Prima Mythos",
                at_clean_date="30-4-2025",
            ),
        ],
    ),
    (None, f"Не найдено не одного прибора в ремонте за эту дату {date}"),
]


@mark.usefixtures("db_connect")
@mark.api_bot
class TestAPIBotDb:
    """Тест api взаимодействия бота с базой данных"""

    def test_bot_get_devices_at_date(self):
        """тест: api бота для получения данных о приборе по дате"""

        api = APIBotDb("clean_device_test.db")
        where_data = {"at_clean_date": "30-4-2025"}
        result = api.bot_get_devices_at_date(where_data=where_data)

        assert result == [
            StockBrokenDeviceData(
                stock_device_id=35, device_name="K20", at_clean_date="30-4-2025"
            ),
            StockBrokenDeviceData(
                stock_device_id=43, device_name="K20", at_clean_date="30-4-2025"
            ),
            StockBrokenDeviceData(
                stock_device_id=32, device_name="Arolla", at_clean_date="30-4-2025"
            ),
        ]

    def test_bot_get_devices_at_date_invalid(self):
        """тест: api бота для не получения данных о приборе по дате"""

        api = APIBotDb("clean_device_test.db")
        where_data = {"at_clean_date": "-2025"}
        result = api.bot_get_devices_at_date(where_data=where_data)

        assert result == "Нет приборов в эту дату"

    def test_bot_device_from_stockpile(self):
        """тест: api бота для получения данных о приборе со склада"""

        api = APIBotDb("clean_device_test.db")
        where_data = {
            "stock_device_id": "1",
            "device_name": "Laser Beam",
        }
        result = api.bot_device_from_stockpile(where_data=where_data)

        assert result == StockDeviceData(
            stock_device_id=1,
            device_name="Laser Beam",
            company_name="Light Craft",
            type_title="Beam",
            at_clean_date="27-4-2025",
        )

    def test_bot_device_from_stockpile_invalid(self):
        """тест: api бота для не получения данных о приборе со склада"""

        api = APIBotDb("clean_device_test.db")
        where_data = {
            "stock_device_id": "20000",
            "device_name": "Laser",
        }
        result = api.bot_device_from_stockpile(where_data=where_data)

        assert result == "Прибор с id 20000 и названием Laser не найден в базе"

    def test_bot_device(self):
        """тест: api бота для получения данных о приборе"""

        api = APIBotDb("clean_device_test.db")
        result = api.bot_device("Laser Beam")

        assert result == OutputDeviceTable(
            device_id=4,
            device_name="Laser Beam",
            company_name="Light Craft",
            type_title="Beam",
        )

    def test_bot_device_invalid(self):
        """тест: api бота для не получения данных о приборе"""

        api = APIBotDb("clean_device_test.db")
        result = api.bot_device("Laser Keam")

        assert result == "Прибор с названием Laser Keam не найден в базе"

    def test_bot_company(self):
        """тест: api бота для получения данных о компании"""

        api = APIBotDb("clean_device_test.db")
        result = api.bot_company(company_name="Light Craft")

        assert result == OutputDeviceCompanyTable(
            company_id=2,
            company_name="Light Craft",
            producer_country="Russia",
            description_company="https://light-craft.ru/",
        )

    def test_bot_company_invalid(self):
        """тест: api бота для получения данных о компании"""

        api = APIBotDb("clean_device_test.db")
        result = api.bot_company(company_name="Sight Praft")

        assert result == "Компания с названием Sight Praft не найден в базе"

    def test_bot_device_type(self):
        """тест: api бота для получения данных о типе прибора"""

        api = APIBotDb("clean_device_test.db")
        result = api.bot_device_type("Beam")

        assert isinstance(result, OutputDeviceTypeTable)

    def test_bot_device_type_invalid(self):
        """тест: api бота для не получения данных о типе прибора"""

        api = APIBotDb("clean_device_test.db")
        result = api.bot_device_type("Keam")

        assert result == "Тип прибор с названием Keam не найден в базе"

    @mark.parametrize("where_data, expect", data_lst_device_from_stockpile)
    def test_bot_lst_broken_device_from_stockpile(self, where_data, expect):
        """тест: api бота для получения списка приборов в ремонте"""

        api = APIBotDb("clean_device_test.db")
        result = api.bot_lst_broken_device_from_stockpile(where_data=where_data)

        assert result == expect

    def test_bot_lst_device(self):
        """тест: api бота для получения списка приборов"""

        api = APIBotDb("clean_device_test.db")
        result = api.bot_lst_device()

        assert result == [
            OutputDeviceTable(
                device_id=1,
                device_name="Sharpy",
                company_name="Clay Paky",
                type_title="Beam",
            ),
            OutputDeviceTable(
                device_id=2,
                device_name="K20",
                company_name="Clay Paky",
                type_title="Hybrid",
            ),
            OutputDeviceTable(
                device_id=3,
                device_name="Prima Mythos",
                company_name="Clay Paky",
                type_title="Hybrid",
            ),
            OutputDeviceTable(
                device_id=4,
                device_name="Laser Beam",
                company_name="Light Craft",
                type_title="Beam",
            ),
            OutputDeviceTable(
                device_id=5,
                device_name="7x40",
                company_name="Light Craft",
                type_title="Beam",
            ),
            OutputDeviceTable(
                device_id=6,
                device_name="Arolla",
                company_name="Clay Paky",
                type_title="Spot",
            ),
            OutputDeviceTable(
                device_id=7,
                device_name="Scenius unico",
                company_name="Clay Paky",
                type_title="Hybrid",
            ),
        ]

    def test_bot_lst_company(self):
        """тест: api бота получения списка компаний"""

        api = APIBotDb("clean_device_test.db")
        result = api.bot_lst_company()

        assert result == [
            OutputDeviceCompanyTable(
                company_id=1,
                company_name="Clay Paky",
                producer_country="Italy",
                description_company="https://www.claypaky.it/",
            ),
            OutputDeviceCompanyTable(
                company_id=2,
                company_name="Light Craft",
                producer_country="Russia",
                description_company="https://light-craft.ru/",
            ),
        ]

    def test_bot_lst_device_type(self):
        """тест: api бота получения списка типов приборов"""

        api = APIBotDb("clean_device_test.db")
        result = api.bot_lst_device_type()

        assert result

    def test_bot_device_id(self):
        """тест: api бота для получения id прибора"""

        api = APIBotDb("clean_device_test.db")
        result = api.bot_device_id("Laser Beam")

        assert result == "4"

    def test_bot_company_id(self):
        """тест: api бота для получения id компании"""

        api = APIBotDb("clean_device_test.db")
        result = api.bot_company_id("Clay Paky")

        assert result == "1"

    def test_bot_type_id(self):
        """тест: api бота для получения id типа прибора"""

        api = APIBotDb("clean_device_test.db")
        result = api.bot_type_id("Beam")

        assert result == "1"

    def test_is_availability_device_from_stockpile(self):
        """тест: api бота для проверки наличия прибора на складе"""

        api = APIBotDb("clean_device_test.db")
        where_data = {"stock_device_id": "1", "device_name": "Laser Beam"}

        assert api.is_availability_device_from_stockpile(where_data=where_data)

    def test_is_availability_device(self):
        """тест: api бота для проверки наличи прибора в базе"""

        api = APIBotDb("clean_device_test.db")

        assert api.is_availability_device("Laser Beam")

    def test_is_availability_company(self):
        """тест: api бота для проверки наличия компании в базе"""

        api = APIBotDb("clean_device_test.db")

        assert api.is_availability_company("Clay Paky")

    def test_is_availability_type(self):
        """тест: api бота для проверки наличия типа прибора в базе"""

        api = APIBotDb("clean_device_test.db")

        assert api.is_availability_type("Beam")

    def test_not_is_availability_device_from_stockpile(self):
        """тест: api бота для проверки не наличия прибора на складе"""

        api = APIBotDb("clean_device_test.db")
        where_data = {"stock_device_id": "9000", "device_name": "Laser Swin"}

        assert not api.is_availability_device_from_stockpile(where_data=where_data)

    def test_not_is_availability_device(self):
        """тест: api бота для проверки не наличи прибора в базе"""

        api = APIBotDb("clean_device_test.db")

        assert not api.is_availability_device("Laser Sweam")

    def test_not_is_availability_company(self):
        """тест: api бота для проверки не наличия компании в базе"""

        api = APIBotDb("clean_device_test.db")

        assert not api.is_availability_company("Clay Saky")

    def test_not_is_availability_type(self):
        """тест: api бота для проверки не наличия типа прибора в базе"""

        api = APIBotDb("clean_device_test.db")

        assert not api.is_availability_type("Seam")

    def test_bot_change_device_status_broken(self):
        """тест: api бота для смены статуса прибора на складе"""

        api = APIBotDb("clean_device_test.db")
        where_data = {"stock_device_id": "35", "device_name": "K20", "mark": 0}
        api.bot_change_device_status(where_data=where_data)

        device_data = {"stock_device_id": "35", "device_name": "K20"}
        device = api.bot_device_from_stockpile(where_data=device_data)

        at_cleare = {"at_clean_date": "30-4-2025"}
        result = api.bot_get_devices_at_date(where_data=at_cleare)

        if isinstance(device, StockDeviceData):
            assert device.stock_device_id not in [
                item.device_name
                for item in result
                if isinstance(item, StockBrokenDeviceData)
            ]

    def test_bot_change_device_status_clean(self):
        """тест: api бота для смены статуса прибора на складе"""

        api = APIBotDb("clean_device_test.db")
        where_data = {"stock_device_id": "35", "device_name": "K20", "mark": 1}
        api.bot_change_device_status(where_data=where_data)

        device_data = {"stock_device_id": "35", "device_name": "K20"}
        device = api.bot_device_from_stockpile(where_data=device_data)

        at_cleare = {"at_clean_date": "30-4-2025"}
        result = api.bot_get_devices_at_date(where_data=at_cleare)

        if isinstance(device, StockDeviceData):
            assert device.stock_device_id in [
                item.stock_device_id
                for item in result
                if isinstance(item, StockBrokenDeviceData)
            ]

    def test_bot_set_device_from_stockpile_by_name_and_id_to_db(self):
        """тест: api бота для добавления данных о приборе на складе"""

        api = APIBotDb("clean_device_test.db")
        set_data = {"stock_device_id": "1000", "device_name": "K20"}
        api.bot_set_device_from_stockpile_by_name_and_id_to_db(set_data=set_data)

        where_data = {"stock_device_id": "1000", "device_name": "K20"}
        check = api.is_availability_device_from_stockpile(where_data=where_data)

        assert check

    def test_bot_set_device_type(self):
        """тест: api бот для добавления данных о типе прибора в базу"""

        api = APIBotDb("clean_device_test.db")
        set_data = {
            "type_title": "Beams",
            "type_description": "device type description Beams",
        }
        api.bot_set_device_type(set_data=set_data)

        check = api.is_availability_type("Beams")

        assert check

    def test_bot_set_device_company(self):
        """тест: api бота для добавления данных о компании в базу"""

        api = APIBotDb("clean_device_test.db")
        set_data = {
            "company_name": "Clay Baky",
            "producer_country": "Spain",
            "description_company": "Company Clay Baky from Spain description",
        }
        api.bot_set_device_company(set_data=set_data)

        check = api.is_availability_company("Clay Baky")

        assert check

    def test_bot_set_device(self):
        """тест: api бота для добавлении данных о приборе в базу"""

        api = APIBotDb("clean_device_test.db")
        set_data = {
            "device_name": "k60",
            "company_name": "Clay Paky",
            "type_title": "Beam",
        }
        api.bot_set_device(set_data=set_data)

        check = api.is_availability_device("k60")

        assert check

    def test_bot_update_devices_stock_clearence_date(self):
        """тест: api бота для обновления данных по очещенному прибору"""

        api = APIBotDb("clean_device_test.db")
        set_data = {"stock_device_id": "1", "device_name": "Laser Beam"}
        res = api.bot_update_devices_stock_clearence_date(where_data=set_data)

        assert res == "Данные прибора - Laser Beam обновлены"
