from src.interface import (
    DeviceCompanyTable,
    DeviceTable,
    DeviceTypeTable,
    RowValue,
    StockDeviceData,
    StockDeviceTable,
    TableRow,
    repr_stock_device_factory,
)


class TestConnectionInterfaceStockDevice:
    """Тест интерфейса обработки данных о приборе на складе"""

    def test_get_all_data_stock_device(self, stock_device_connect):
        """тест: интерфейс для получения данных всех приборов на складе"""

        res = stock_device_connect.get_all_data()
        assert list(res) == [
            [
                StockDeviceTable(
                    stock_device_id=25, device_id=1, at_clean_date="2025-04-19"
                ),
                StockDeviceTable(
                    stock_device_id=35, device_id=2, at_clean_date="2025-04-29"
                ),
            ]
        ]

    def test_get_once_data_stock_device(self, stock_device_connect):
        """тест: интерфейс для получения данных одного прибора на складе"""

        row = "stock_device_id"
        val = "25"
        res = stock_device_connect.get_once_data(row, val)

        assert res == StockDeviceTable(
            stock_device_id=25, device_id=1, at_clean_date="2025-04-19"
        )

    def test_set_data_stock_device(self, stock_device_connect):
        """тест: интерфейс для записи данных в бд"""

        set_data = ("45", "1", "2025-05-19")
        stock_device_connect.set_data(set_data)

        row = "stock_device_id"
        val = "45"

        res = stock_device_connect.get_once_data(row, val)

        assert res == StockDeviceTable(
            stock_device_id=45, device_id=1, at_clean_date="2025-05-19"
        )

    def test_update_data_type_device(self, stock_device_connect):
        """тест: интерфейс для обновления данных пробора на складе"""

        set_data = (TableRow("stock_device_id"), RowValue("55"))
        where_data = (TableRow("stock_device_id"), RowValue("25"))

        res = stock_device_connect.get_once_data(where_data[0], where_data[1])
        res_title = res.stock_device_id

        stock_device_connect.update_data(set_data, where_data)

        res_two = stock_device_connect.get_once_data(set_data[0], set_data[1])
        res_two_title = res_two.stock_device_id

        assert res_title != res_two_title

    def test_get_repr_stock_device(self, stock_device_connect):
        """тест: интерфейс для показа полных данных прибора на складе по id"""

        device_id = 25
        device_name = "k20"
        stock_device_connect.conn.row_factory = repr_stock_device_factory
        res = stock_device_connect.get_repr_stock_data(device_id, device_name)

        assert res == StockDeviceData(
            stock_device_id=25,
            device_name="k20",
            company_name="Clay Paky",
            type_title="beam",
            at_clean_date="2025-04-19",
        )


class TestConnectionInterfaceDevice:
    """Тест интерфейса обработки данных о приборе"""

    def test_get_all_data_device(self, device_connect):
        """тест: интерфейс для получения данных всех приборов"""

        res = device_connect.get_all_data()
        assert list(res) == [
            [
                DeviceTable(device_name="k20", company_id=1, type_device_id=1),
                DeviceTable(device_name="laser beam", company_id=2, type_device_id=1),
            ]
        ]

    def test_get_once_data_device(self, device_connect):
        """тест: интерфейс для получения данных одного прибора"""

        row = "device_id"
        val = "1"
        res = device_connect.get_once_data(row, val)

        assert res == DeviceTable(device_name="k20", company_id=1, type_device_id=1)

    def test_set_data_device(self, device_connect):
        """тест: интерфейс для записи данных в бд"""

        set_data = ("prima mythos", 1, 1)
        device_connect.set_data(set_data)

        row = "device_id"
        val = "3"

        res = device_connect.get_once_data(row, val)

        assert res == DeviceTable(
            device_name="prima mythos", company_id=1, type_device_id=1
        )

    def test_update_data_type_device(self, device_connect):
        """тест: интерфейс для обновления данных типа пробора"""

        set_data = (TableRow("device_name"), RowValue("k30"))
        where_data = (TableRow("device_id"), RowValue("1"))

        res = device_connect.get_once_data(where_data[0], where_data[1])
        res_title = res.device_name

        device_connect.update_data(set_data, where_data)

        res_two = device_connect.get_once_data(where_data[0], where_data[1])
        res_two_title = res_two.device_name

        assert res_title != res_two_title


class TestConnectionInterfaceDeviceCompany:
    """Тест интерфейса обработки данных компании"""

    def test_get_all_data_device_company(self, company_connect):
        """тест: интерфейс для получения данных всех типов приборов"""

        res = company_connect.get_all_data()
        assert list(res) == [
            [
                DeviceCompanyTable(
                    company_name="Clay Paky",
                    producer_country="Itali",
                    description_company="https://www.claypaky.it/",
                ),
                DeviceCompanyTable(
                    company_name="Light Craft",
                    producer_country="Russia",
                    description_company="https://light-craft.ru/",
                ),
            ]
        ]

    def test_get_once_data_device_company(self, company_connect):
        """тест: интерфейс для получения данных одного прибора"""

        row = "company_id"
        val = "1"
        res = company_connect.get_once_data(row, val)

        assert res == DeviceCompanyTable(
            company_name="Clay Paky",
            producer_country="Itali",
            description_company="https://www.claypaky.it/",
        )

    def test_set_data_device_company(self, company_connect):
        """тест: интерфейс для записи данных в бд"""
        set_data = ("Antari", "Taiwan", "https://antari.com/")
        company_connect.set_data(set_data)

        row = "company_id"
        val = "3"

        res = company_connect.get_once_data(row, val)

        assert res == DeviceCompanyTable(
            company_name="Antari",
            producer_country="Taiwan",
            description_company="https://antari.com/",
        )

    def test_update_data_type_device(self, company_connect):
        """тест: интерфейс для обновления данных типа пробора"""

        set_data = (TableRow("company_name"), RowValue("Clay Puky"))
        where_data = (TableRow("company_id"), RowValue("1"))

        res = company_connect.get_once_data(where_data[0], where_data[1])
        res_title = res.company_name

        company_connect.update_data(set_data, where_data)

        res_two = company_connect.get_once_data(where_data[0], where_data[1])
        res_two_title = res_two.company_name

        assert res_title != res_two_title


class TestConnectionInterfaceTypeDevice:
    """Тест интерфейса обработки данных типов приборов"""

    def test_get_all_data_type_device(self, type_connect):
        """тест: интерфейс для получения данных всех типов приборов"""

        res = type_connect.get_all_data()
        assert list(res) == [
            [
                DeviceTypeTable(
                    type_title="beam",
                    type_description="Light device not spot",
                ),
                DeviceTypeTable(
                    type_title="spot",
                    type_description="light device not beam",
                ),
            ]
        ]

    def test_get_once_data_type_device(self, type_connect):
        """тест: интерфейс для получения данных одного прибора"""

        row = "type_device_id"
        val = "1"
        res = type_connect.get_once_data(row, val)

        assert res == DeviceTypeTable(
            type_title="beam",
            type_description="Light device not spot",
        )

    def test_set_data_type_device(self, type_connect):
        """тест: интерфейс для записи данных в бд"""
        set_data = ("beamsi", "Light device not spot")
        type_connect.set_data(set_data)

        row = "type_device_id"
        val = "3"

        res = type_connect.get_once_data(row, val)

        assert res == DeviceTypeTable(
            type_title="beamsi",
            type_description="Light device not spot",
        )

    def test_update_data_type_device(self, type_connect):
        """тест: интерфейс для обновления данных типа пробора"""

        set_data = (TableRow("type_title"), RowValue("Boom"))
        where_data = (TableRow("type_device_id"), RowValue("1"))

        res = type_connect.get_once_data(where_data[0], where_data[1])
        res_title = res.type_title

        type_connect.update_data(set_data, where_data)

        res_two = type_connect.get_once_data(where_data[0], where_data[1])
        res_two_title = res_two.type_title

        assert res_title != res_two_title
