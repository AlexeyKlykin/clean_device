from src.run_bot import DBotAPI
from src.secret import secrets

# 'get_company_id', 'get_type_id', 'save_company_from_bot_into_db', 'save_device_from_bot_into_db', 'save_device_type_from_bot_into_db'


class TestBotAPI:
    """Тест api взаимодействия бота с базой"""

    def test_save_device_from_bot_into_db(self, device_connect):
        """тест: сохранение прибора в базе через api"""

        db_name = secrets["DB_TEST"]
        bot = DBotAPI()
        bot.db_name = db_name

        data = {"device_name": "k50", "company_name": "Clay Paky", "type_title": "beam"}

        bot.save_device_from_bot_into_db(data)

        device = device_connect.get_once_data(row="device_name", val="k50")

        assert device.device_name == "k50"

    def test_get_company_id(self, company_connect):
        """тест: получения id компании через api"""

        db_name = secrets["DB_TEST"]
        bot = DBotAPI()
        bot.db_name = db_name
        company_name = "Clay Paky"

        company_id = bot.get_company_id(company_name=company_name)

        assert company_id == "1"

    def test_get_type_id(self, type_connect):
        """тест: получение id типа прибора через api"""

        db_name = secrets["DB_TEST"]
        bot = DBotAPI()
        bot.db_name = db_name
        type_title = "beam"

        type_id = bot.get_type_id(type_title=type_title)

        assert type_id == "1"

    def test_save_company_from_bot_into_db(self, company_connect):
        """тест: сохранение данных компании в базе через api"""

        db_name = secrets["DB_TEST"]
        bot = DBotAPI()
        bot.db_name = db_name

        data = {
            "company_name": "laser jet",
            "producer_company": "France",
            "description_company": "link to site",
        }
        bot.save_company_from_bot_into_db(data)

        company = company_connect.get_once_data(row="company_name", val="laser jet")

        assert company.company_name == "laser jet"

    def test_save_device_type_from_bot_into_db(self, type_connect):
        """тест: сохранение типа прибора в бд через api"""

        db_name = secrets["DB_TEST"]
        bot = DBotAPI()
        bot.db_name = db_name

        data = {"type_title": "bums", "type_description": "beams description"}
        bot.save_device_type_from_bot_into_db(data)

        type_device = type_connect.get_once_data(row="type_title", val="bums")

        assert type_device.type_title == "bums"
