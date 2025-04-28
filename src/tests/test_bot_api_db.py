class TestBotAPI:
    """Тест api взаимодействия бота с базой"""

    def test_get_stock_device_id(self, stock_device_connect, bot_api):
        """тест: получаем складское устройство по имени через api"""

        device_id = "25"
        company_name = "k20"
        res = bot_api.get_stock_device_id(device_id, company_name)

        assert res == {
            "stock_device_id": 25,
            "device_name": "k20",
            "company_name": "Clay Paky",
            "type_title": "beam",
            "at_clean_date": "2025-04-19",
        }

    def test_check_company_id(self, company_connect, bot_api):
        """тест: проверяем наличие компании через api"""

        company_name = "Clay Paky"
        res = bot_api.check_company_id(company_name)

        assert res

    def test_check_type_id(self, type_connect, bot_api):
        """тест: проверяем наличие типа прибора через api"""

        type_title = "beam"
        res = bot_api.check_type_id(type_title)

        assert res

    def test_get_all_type(self, type_connect, bot_api):
        """тест: возвращает все типы приборов через api"""

        res = bot_api.get_all_type()

        assert res == ["beam", "spot"]

    def test_get_all_company(self, company_connect, bot_api):
        """тест: возвращает данные о компании через api"""

        res = bot_api.get_all_company()

        assert res == ["Clay Paky", "Light Craft"]

    def test_get_all_devices(self, device_connect, bot_api):
        """тест: возвращает данные об устройствах через api"""

        res = bot_api.get_all_devices()

        assert res == ["k20", "laser beam"]

    def test_get_all_stock_device_id(self, stock_device_connect, bot_api):
        """тест: возвращает все id приборов на складе через api"""

        res = bot_api.get_all_stock_device_id()

        assert res == [25, 35]

    def test_save_stock_device_into_db_from_bot(self, stock_device_connect, bot_api):
        """тест: сохраняет данные из бота в базе через api"""

        data = {"stock_device_id": "55", "device_name": "k20"}
        after_update = bot_api.check_stock_device_id("55")
        bot_api.save_stock_device_into_db_from_bot(data)
        before_update = bot_api.check_stock_device_id("55")

        assert after_update != before_update

    def test_get_device_id(self, device_connect, bot_api):
        """тест: возвращения id прибора из базы по имени через api"""

        device_name = "k20"
        res = bot_api.get_device_id(device_name)

        assert res == "1"

    def test_check_device_id(self, device_connect, bot_api):
        """тест: проверяем наличие прибора в базе по id через api"""

        device_name = "k20"
        res = bot_api.check_device_id(device_name)

        assert res

    def test_update_stock_device(self, stock_device_connect, bot_api):
        """тест: обновляем запись о приборе на складе
        который был почищен"""

        stock_device_id = "25"
        after_update = stock_device_connect.get_once_data(
            row="stock_device_id", val=stock_device_id
        )
        stock_device_id_update = "35"
        device_name = "k20"
        bot_api.update_stock_device(stock_device_id, device_name)
        before_update = stock_device_connect.get_once_data(
            row="stock_device_id", val=stock_device_id_update
        )

        assert after_update != before_update

    def test_check_stock_device_id(self, stock_device_connect, bot_api):
        """тест: проверяем наличие складского прибора по id"""

        stock_device_id = "25"
        res = bot_api.check_stock_device_id(stock_device_id)

        assert res

    def test_save_device_from_bot_into_db(self, device_connect, bot_api):
        """тест: сохранение прибора в базе через api"""

        data = {"device_name": "k50", "company_name": "Clay Paky", "type_title": "beam"}
        bot_api.save_device_from_bot_into_db(data)
        device = device_connect.get_once_data(row="device_name", val="k50")

        assert device.device_name == "k50"

    def test_get_company_id(self, company_connect, bot_api):
        """тест: получения id компании через api"""

        company_name = "Clay Paky"
        company_id = bot_api.get_company_id(company_name=company_name)

        assert company_id == "1"

    def test_get_type_id(self, type_connect, bot_api):
        """тест: получение id типа прибора через api"""

        type_title = "beam"
        type_id = bot_api.get_type_id(type_title=type_title)

        assert type_id == "1"

    def test_save_company_from_bot_into_db(self, company_connect, bot_api):
        """тест: сохранение данных компании в базе через api"""

        data = {
            "company_name": "laser jet",
            "producer_company": "France",
            "description_company": "link to site",
        }
        bot_api.save_company_from_bot_into_db(data)
        company = company_connect.get_once_data(row="company_name", val="laser jet")

        assert company.company_name == "laser jet"

    def test_save_device_type_from_bot_into_db(self, type_connect, bot_api):
        """тест: сохранение типа прибора в бд через api"""

        data = {"type_title": "bums", "type_description": "beams description"}
        bot_api.save_device_type_from_bot_into_db(data)
        type_device = type_connect.get_once_data(row="type_title", val="bums")

        assert type_device.type_title == "bums"
