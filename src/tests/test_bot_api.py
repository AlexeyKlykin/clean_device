from pytest import mark
from src.bot_api import APIBotDb
from src.schema_for_validation import (
    OutputDeviceCompanyTable,
    OutputDeviceTable,
    StockBrokenDeviceData,
)


@mark.usefixtures("db_connect")
@mark.api_bot
class TestAPIBotDb:
    """Тест api взаимодействия бота с базой"""

    def test_bot_device_from_stockpile(self):
        """тест: выборки прибора со склада"""

        api = APIBotDb(db_name="clean_device_test.db")
        data = {"stock_device_id": "1", "device_name": "Laser Beam"}
        device = api.bot_device_from_stockpile(where_data=data)

        assert device == {
            "stock_device_id": 1,
            "device_name": "Laser Beam",
            "company_name": "Light Craft",
            "type_title": "Beam",
            "at_clean_date": "27-4-2025",
        }

    def test_bot_device(self):
        """тест: выборка прибора по имени"""

        api = APIBotDb(db_name="clean_device_test.db")
        device_name = "Laser Beam"
        device = api.bot_device(device_name)

        assert device == {
            "device_id": 4,
            "device_name": "Laser Beam",
            "company_name": "Light Craft",
            "type_title": "Beam",
        }

    def test_bot_company(self):
        """тест: выборка компании из базы"""

        api = APIBotDb(db_name="clean_device_test.db")
        company_name = "Light Craft"
        company = api.bot_company(company_name)

        assert company == {
            "company_id": 2,
            "company_name": "Light Craft",
            "producer_country": "Russia",
            "description_company": "https://light-craft.ru/",
        }

    def test_bot_device_type(self):
        """тест: выборка типа прибора из бд"""

        api = APIBotDb(db_name="clean_device_test.db")
        type_title = "Beam"
        type_device = api.bot_device_type(type_title)

        assert type_device == {
            "type_device_id": 1,
            "type_title": "Beam",
            "type_description": "Световые приборы типа Beam (в переводе «луч») создают мощный, узконаправленный световой поток. Их основная цель — акцентное освещение различных динамических эффектов, которых нельзя достичь с помощью приборов типа spot. 1\nНекоторые характеристики световых приборов Beam:\n\n    Мощность. Широкий диапазон мощности, адаптированный к различным масштабам мероприятий.\n    Источник света. Большинство современных приборов Beam используют светодиодные (LED) источники света для высокой светоотдачи, энергоэффективности и длительного срока службы.\n    Угол луча. Определяет степень концентрации света. Узкий угол создаёт более чёткий и сфокусированный луч, а широкий — более рассеянный эффект.\n    Цветовая температура. Определяет оттенок белого света, излучаемого прибором Beam. Множество приборов позволяют регулировать цветовую температуру для создания различных атмосфер.\n    Панорамирование и наклон. Многие световые приборы Beam оснащены моторизованным панорамированием и наклоном, обеспечивая операторам точную направленность луча.\n\nПриборы Beam подходят для освещения просторных помещений или создания эффектных иллюминаций на открытом воздухе.",
        }

    def test_bot_lst_broken_device_from_stockpile(self):
        """тест: выборка всех приборов на ремонте"""

        api = APIBotDb(db_name="clean_device_test.db")
        where_data = {"at_clean_date": "30-4-2025"}
        broken_devices = api.bot_lst_broken_device_from_stockpile(where_data)

        assert broken_devices == [
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
        ]

    def test_bot_lst_device(self):
        """тест: выборка всех приборов их бд"""

        api = APIBotDb(db_name="clean_device_test.db")
        lst_device = api.bot_lst_device()

        assert lst_device == [
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
        """тест: возврата списка компаний через api бота"""

        api = APIBotDb(db_name="clean_device_test.db")
        lst_company = api.bot_lst_company()

        assert lst_company == [
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

    def test_bot_device_id(self):
        """тест: возвращает id прбора по имени через api бота"""

        api = APIBotDb(db_name="clean_device_test.db")
        device_name = "Arolla"
        device_id = api.bot_device_id(device_name)

        assert device_id == "6"

    def test_bot_company_id(self):
        """тест: возвращает id компании"""

        api = APIBotDb(db_name="clean_device_test.db")
        company_name = "Clay Paky"
        company_id = api.bot_company_id(company_name=company_name)

        assert company_id == "1"

    def test_bot_type_id(self):
        """тест: возвращает id тип прибора по имени"""

        api = APIBotDb(db_name="clean_device_test.db")
        type_title = "Spot"
        type_id = api.bot_device_type(type_title)

        assert type_id == {
            "type_device_id": 2,
            "type_title": "Spot",
            "type_description": "Spot \u2014 \u0442\u0438\u043f \u0441\u0432\u0435\u0442\u043e\u0432\u043e\u0433\u043e \u043f\u0440\u0438\u0431\u043e\u0440\u0430 \u0441 \u044d\u0444\u0444\u0435\u043a\u0442\u043e\u043c \u043d\u0430\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u043d\u043e\u0433\u043e \u043b\u0443\u0447\u0430. \u0413\u043b\u0430\u0432\u043d\u0430\u044f \u043e\u0441\u043e\u0431\u0435\u043d\u043d\u043e\u0441\u0442\u044c \u2014 \u043d\u0430\u043b\u0438\u0447\u0438\u0435 GOBO (\u0442\u0440\u0430\u0444\u0430\u0440\u0435\u0442\u0430 \u0438\u0437 \u043f\u043b\u0430\u0441\u0442\u0438\u043a\u0430 \u0438\u043b\u0438 \u043c\u0435\u0442\u0430\u043b\u043b\u0430), \u0441 \u043f\u043e\u043c\u043e\u0449\u044c\u044e \u043a\u043e\u0442\u043e\u0440\u043e\u0433\u043e \u0441\u043e\u0437\u0434\u0430\u0451\u0442\u0441\u044f \u044f\u0440\u043a\u043e\u0435 \u0441\u0432\u0435\u0442\u043e\u0432\u043e\u0435 \u043f\u044f\u0442\u043d\u043e \u0441 \u0432\u043e\u0437\u043c\u043e\u0436\u043d\u043e\u0441\u0442\u044c\u044e \u0441\u043b\u0435\u0436\u0435\u043d\u0438\u044f.\n\u041d\u0435\u043a\u043e\u0442\u043e\u0440\u044b\u0435 \u0445\u0430\u0440\u0430\u043a\u0442\u0435\u0440\u0438\u0441\u0442\u0438\u043a\u0438 \u0438 \u043f\u0440\u0435\u0438\u043c\u0443\u0449\u0435\u0441\u0442\u0432\u0430 \u043f\u043e\u0432\u043e\u0440\u043e\u0442\u043d\u044b\u0445 \u0433\u043e\u043b\u043e\u0432 \u0442\u0438\u043f\u0430 SPOT:\n    \u0431\u044b\u0441\u0442\u0440\u043e\u0435 \u043f\u0440\u043e\u0435\u0446\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435 \u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0439 \u043d\u0430 \u0433\u043e\u0440\u0438\u0437\u043e\u043d\u0442\u0430\u043b\u044c\u043d\u044b\u0435 \u0438 \u0432\u0435\u0440\u0442\u0438\u043a\u0430\u043b\u044c\u043d\u044b\u0435 \u043f\u043e\u0432\u0435\u0440\u0445\u043d\u043e\u0441\u0442\u0438;\n    \u0432\u0440\u0430\u0449\u0430\u044e\u0449\u0435\u0435\u0441\u044f \u0438 \u0438\u0437\u043c\u0435\u043d\u044f\u0435\u043c\u043e\u0435 \u0433\u043e\u0431\u043e;\n    \u0434\u0438\u043c\u043c\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435 \u0438 \u0440\u0430\u0437\u043c\u044b\u0432\u0430\u043d\u0438\u0435 \u043b\u0443\u0447\u0430;\n    \u044d\u0444\u0444\u0435\u043a\u0442 \u0440\u0430\u0434\u0443\u0433\u0438, \u0441\u043c\u0435\u043d\u0430 \u0446\u0432\u0435\u0442\u043e\u0432;\n    \u043f\u043e\u0432\u043e\u0440\u043e\u0442\u043d\u0430\u044f \u043f\u0440\u0438\u0437\u043c\u0430 \u0438 \u0438\u0440\u0438\u0441;\n    \u0440\u0435\u0433\u0443\u043b\u0438\u0440\u0443\u0435\u043c\u044b\u0435 \u043f\u0443\u043b\u044c\u0441\u0438\u0440\u0443\u044e\u0449\u0438\u0439 \u0438 \u0441\u0442\u0440\u043e\u0431\u043e\u0441\u043a\u043e\u043f\u0438\u0447\u0435\u0441\u043a\u0438\u0439 \u044d\u0444\u0444\u0435\u043a\u0442\u044b;\n    \u0431\u0435\u0437\u0437\u0432\u0443\u0447\u043d\u043e\u0441\u0442\u044c.\n\n\u0412\u0440\u0430\u0449\u0430\u044e\u0449\u0438\u0435\u0441\u044f \u0433\u043e\u043b\u043e\u0432\u044b \u0442\u0438\u043f\u0430 SPOT \u043f\u0440\u0438\u043c\u0435\u043d\u044f\u044e\u0442\u0441\u044f, \u043a\u043e\u0433\u0434\u0430 \u043d\u0435\u043e\u0431\u0445\u043e\u0434\u0438\u043c\u043e \u043e\u0431\u043e\u0440\u0443\u0434\u043e\u0432\u0430\u043d\u0438\u0435 \u0441 \u0442\u043e\u0447\u043d\u044b\u043c \u043f\u043e\u0437\u0438\u0446\u0438\u043e\u043d\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0435\u043c \u0438 \u0431\u044b\u0441\u0442\u0440\u043e\u0439 \u0441\u043c\u0435\u043d\u043e\u0439 \u0440\u0435\u0436\u0438\u043c\u043e\u0432. 2",
        }

    def test_bot_check_device_from_stockpile(self):
        """тест: проверяет наличие прибора на складе"""

        api = APIBotDb(db_name="clean_device_test.db")
        where_data = {"stock_device_id": "1", "device_name": "Laser Beam"}
        check = api.bot_check_device_from_stockpile(where_data)

        assert check

    def test_bot_check_device(self):
        """тест: проверяет наличие прибора в бд через api"""

        api = APIBotDb(db_name="clean_device_test.db")
        device_name = "K20"
        check = api.bot_check_device(device_name)

        assert check

    def test_bot_check_company(self):
        """тест: проверяет наличие компании в бд через api"""

        api = APIBotDb(db_name="clean_device_test.db")
        device_company = "Clay Paky"
        check = api.bot_check_company(device_company)

        assert check

    def test_bot_check_type(self):
        """тест: проверяет наличие типа устройства в базе через api"""

        api = APIBotDb(db_name="clean_device_test.db")
        device_type = "Beam"
        check = api.bot_check_type(device_type)

        assert check

    def test_bot_change_device_status(self):
        """тест: меняет статус прибора на складе"""

        api = APIBotDb(db_name="clean_device_test.db")
        where_data = {"stock_device_id": "1", "device_name": "Laser Beam", "mark": "0"}
        api.bot_change_device_status(where_data)

        res = api.bot_lst_broken_device_from_stockpile()

        assert res == [
            StockBrokenDeviceData(
                stock_device_id=1, device_name="Laser Beam", at_clean_date="3-5-2025"
            ),
        ]

    def test_bot_set_device_from_stockpile_by_name_and_id_to_db(self):
        """тест: добавление прибора на склад через api"""

        api = APIBotDb(db_name="clean_device_test.db")
        set_data = {"stock_device_id": "50", "device_name": "Laser Beam"}
        api.bot_set_device_from_stockpile_by_name_and_id_to_db(set_data)

        where_data = {"stock_device_id": "50", "device_name": "Laser Beam"}
        check = api.bot_check_device_from_stockpile(where_data)

        assert check

    def test_bot_set_device_type(self):
        """тест: добавление типа прибора в базу через api"""

        api = APIBotDb(db_name="clean_device_test.db")
        set_data = {"type_title": "Seam", "type_description": "description seam"}
        api.bot_set_device_type(set_data)

        where_data = "Seam"
        check = api.bot_check_type(where_data)

        assert check

    def test_bot_set_device_company(self):
        """тест: добавления компании производителя в базу через api"""

        api = APIBotDb(db_name="clean_device_test.db")
        set_data = {
            "company_name": "Craft",
            "producer_country": "Spany",
            "description_company": "description spany Craft",
        }
        api.bot_set_device_company(set_data)

        check = api.bot_check_company("Craft")

        assert check

    def test_bot_set_device(self):
        """тест: добавление прибора в базу через api"""

        api = APIBotDb(db_name="clean_device_test.db")
        set_data = {
            "device_name": "K70",
            "company_name": "Clay Paky",
            "type_title": "Beam",
        }
        api.bot_set_device(set_data)

        check = api.bot_check_device("K70")

        assert check

    def test_bot_update_devices_stock_clearence_date(self):
        """тест: обновление даты чистого прибора"""

        api = APIBotDb(db_name="clean_device_test.db")
        set_data = {"stock_device_id": "4", "device_name": "Laser Beam"}
        date = "30-4-2025"
        res = api.bot_update_devices_stock_clearence_date(set_data, date)

        assert res == "Данные прибора - Laser Beam обновлены"
