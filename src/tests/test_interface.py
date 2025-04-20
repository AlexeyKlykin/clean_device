from src.interface import (
    DeviceCompany,
    DeviceOutput,
    DeviceType,
    StockDevicesOutput,
    device_output_factory,
    stock_device_output_factory,
)


class TestDeviceTypeWorkAPI:
    """Тест работы api манипуляции с типами приборов"""

    def test_get_data_about_device_type_by_id(self, type_connect):
        """тест: получение данных о типе устройства по id"""

        res = type_connect.get(1)

        assert res == DeviceType(
            type_title="Beam",
            description_type="вращающиеся головы, которые имеют узконаправленный источник света. Угол раскрытия луча у приборов данного вида колеблется от 2 до 10 градусов.",
        )

    def test_check_type_by_id(self, type_connect):
        """тест: проверка тип по id"""

        res = type_connect.check_by_id(1)

        assert res

    def test_insert_device_type_into_table(self, type_connect):
        """тест: добавление типа приборов в таблицу"""

        cursor = type_connect.conn.cursor()
        cursor.execute("SELECT type_title, description_type FROM device_type")
        res = cursor.fetchone()

        assert res == DeviceType(
            type_title="Beam",
            description_type="вращающиеся головы, которые имеют узконаправленный источник света. Угол раскрытия луча у приборов данного вида колеблется от 2 до 10 градусов.",
        )

    def test_uniq_type_device_title(self, type_connect):
        """тест: отказа в добавлении уникальных имен типов приборов"""

        data_type_device = {
            "type_title": "Beam",
            "description_type": "вращающиеся головы, которые имеют узконаправленный источник света. Угол раскрытия луча у приборов данного вида колеблется от 2 до 10 градусов.",
        }

        res = type_connect.insert(data_type_device)

        assert not res

    def test_check_type_title_is_present_in_the_table(self, type_connect):
        """тест: проверка наличия названия компании в таблице"""

        valid_type_title = "Beam"
        invalid_type_title = "Veam"

        res = type_connect.check_by_title(valid_type_title)

        assert res

        res = type_connect.check_by_title(invalid_type_title)

        assert not res

    def test_deleting_record_in_the_type_device_table(self, type_connect):
        """тест: удаления записи из таблици компании"""

        type_title = "Beam"

        type_connect.deleting_record_by_title(type_title)

        cursor = type_connect.conn.cursor()
        cursor.execute(
            "SELECT type_title, description_type FROM device_type WHERE type_title = '%s'"
            % type_title
        )
        result = cursor.fetchone()
        assert result is None


class TestDeviceCompanyWorkApi:
    """Тест работы api манипуляции с бд"""

    def test_get_data_about_device_company_by_id(self, company_connect):
        """тест: получение данных о компании по Id"""

        res = company_connect.get(1)

        assert res == DeviceCompany(
            company_name="Clay Paky",
            producer_country="Itali",
            description_company="https://www.claypaky.it/",
        )

    def test_check_device_company_by_id(self, company_connect):
        """тест: проверка на то что существует компания по id"""

        res = company_connect.check_by_id(1)

        assert res

    def test_insert_company_into_device_company_interface_(self, company_connect):
        """тест: работы интерфейса добавления компании производителя приборов"""

        cursor = company_connect.conn.cursor()
        cursor.execute(
            "SELECT company_name, producer_country, description_company FROM device_company"
        )
        res = cursor.fetchone()

        assert res == DeviceCompany(
            company_name="Clay Paky",
            producer_country="Itali",
            description_company="https://www.claypaky.it/",
        )

    def test_uniq_company_data(self, company_connect):
        """тест: отказ в добавлении уже существующего названия компании"""

        data_company = {
            "company_name": "Clay Paky",
            "producer_country": "Itali",
            "description_company": "https://www.claypaky.it/",
        }

        res = company_connect.insert(data_company)

        assert not res

    def test_check_company_name_is_present_in_the_table(self, company_connect):
        """тест: проверка наличия названия компании в таблице"""

        valid_name_company = "Clay Paky"
        invalid_name_company = "Lay Paku"

        res = company_connect.check_by_title(valid_name_company)

        assert res

        res = company_connect.check_by_title(invalid_name_company)

        assert not res

    def test_deleting_record_in_the_company_table(self, company_connect):
        """тест: удаления записи из таблици компании"""

        name_company = "Clay Paky"

        company_connect.deleting_record_by_title(name_company)

        cursor = company_connect.conn.cursor()
        cursor.execute(
            "SELECT company_name, producer_country, description_company FROM device_company WHERE company_name = '%s'"
            % name_company
        )
        result = cursor.fetchone()
        assert result is None


class TestDeviceWorkAPI:
    """Тест работы api манипуляции с таблицей приборов"""

    def test_get_data_about_device_by_id(self, device_connect):
        """тест: получение данных об устройстве по id"""

        res = device_connect.get(1)

        assert res == DeviceOutput(
            device_name="k20", company_name="Clay Paky", type_title="Beam"
        )

    def test_get_by_id_device_by_device_name(self, device_connect):
        """тест: получение Id прибора по имени"""

        res = device_connect.get_id_by_name("k20")
        assert res == 1

    def test_insert_device_table(self, device_connect):
        """тест: добавление приборов в таблицу"""

        query_select = """SELECT d.device_name, dc.company_name, dt.type_title from device d
left join device_company dc on dc.company_id = d.company_id
left join device_type dt on dt.type_device_id = d.type_device_id"""

        device_connect.conn.row_factory = device_output_factory
        cursor = device_connect.conn.cursor()
        cursor.execute(query_select)
        res = cursor.fetchone()

        assert res == DeviceOutput(
            device_name="k20", company_name="Clay Paky", type_title="Beam"
        )

    def test_uniq_device_title(self, device_connect):
        """тест: отказа в добавлении уникальных имен приборов"""

        data_device = {"device_name": "k20", "company_id": 1, "type_device_id": 1}

        device_connect.insert(data_device)
        res = device_connect.insert(data_device)

        assert not res

    def test_check_device_title_is_present_in_the_table(self, device_connect):
        """тест: проверка наличия названия прибора в таблице"""

        valid_device_title = "k20"
        invalid_device_title = "v20"

        res = device_connect.check_by_title(valid_device_title)

        assert res

        res = device_connect.check_by_title(invalid_device_title)

        assert not res

    def test_deleting_record_in_the_device_table(self, device_connect):
        """тест: удаления записи из таблици компании"""

        device_name = "k20"

        device_connect.deleting_record_by_title(device_name)

        cursor = device_connect.conn.cursor()
        cursor.execute(
            "SELECT device_name, company_id, type_device_id FROM device WHERE device_name = '%s'"
            % device_name
        )
        res = cursor.fetchone()

        assert not res


class TestStockDeviceWorkAPI:
    """Тест работы api таблицы приборов на складе"""

    def test_get_data_about_stock_device_by_id(self, stock_device_connect):
        """тест: получение данных о приборах на складах по id"""

        res = stock_device_connect.get(25)

        assert res == StockDevicesOutput(
            stock_device_id=25,
            device_name="k20",
            company_name="Clay Paky",
            type_title="Beam",
            at_clean_date="2025-04-19",
        )

    def test_insert_stock_device_table(self, stock_device_connect):
        """тест: добавление приборов в таблицу"""

        query_select = """select sd.stock_device_id, d.device_name, dc.company_name, dt.type_title, sd.at_clean_date
from stock_device sd
left join device d on d.device_id = sd.device_id
left join device_company dc on dc.company_id = d.company_id
left join device_type dt on dt.type_device_id = d.type_device_id;"""

        stock_device_connect.conn.row_factory = stock_device_output_factory
        cursor = stock_device_connect.conn.cursor()
        cursor.execute(query_select)
        res = cursor.fetchone()

        assert res == StockDevicesOutput(
            device_name="k20",
            company_name="Clay Paky",
            type_title="Beam",
            stock_device_id=25,
            at_clean_date="2025-04-19",
        )

    def test_deleting_record_in_the_device_table(self, stock_device_connect):
        """тест: удаления записи из таблици компании"""

        title = "25"

        stock_device_connect.deleting_record_by_title(title)

        cursor = stock_device_connect.conn.cursor()
        cursor.execute(
            "SELECT stock_device_id from stock_device where stock_device_id = 25"
        )
        res = cursor.fetchone()

        assert not res
