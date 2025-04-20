from pytest import fixture

from src.db_app import DBSqlite
from src.interface import (
    DeviceCompanyInterface,
    DeviceInterface,
    DeviceTypeInterface,
    StockDevicesInterface,
)


table_list = ["device", "device_type", "device_company", "stock_device"]


@fixture
def db_connect():
    with DBSqlite("clean_device_test.db") as conn:
        yield conn
        for table in table_list:
            conn.execute(
                "UPDATE `sqlite_sequence` SET `seq` = 0 WHERE `name` = '%s'" % table
            )
            conn.execute("DELETE FROM '%s'" % table)


@fixture
def stock_device_connect():
    data_type_device = {
        "type_title": "Beam",
        "description_type": "вращающиеся головы, которые имеют узконаправленный источник света. Угол раскрытия луча у приборов данного вида колеблется от 2 до 10 градусов.",
    }
    data_company = {
        "company_name": "Clay Paky",
        "producer_country": "Itali",
        "description_company": "https://www.claypaky.it/",
    }
    data_device = {"device_name": "k20", "company_id": "1", "type_device_id": "1"}
    stock_device = {
        "stock_device_id": "25",
        "device_id": "1",
        "at_clean_date": "2025-04-19",
    }

    with DBSqlite("clean_device_test.db") as conn:
        company_interface = DeviceCompanyInterface(conn)
        company_interface.insert(data_company)

        type_interface = DeviceTypeInterface(conn)
        type_interface.insert(data_type_device)

        device_input = DeviceInterface(conn)
        device_input.insert(data_device)

        stock_devices = StockDevicesInterface(conn)
        stock_devices.insert(stock_device)

        yield stock_devices

        for table in table_list:
            conn.execute(
                "UPDATE `sqlite_sequence` SET `seq` = 0 WHERE `name` = '%s'" % table
            )
            conn.execute("DELETE FROM '%s'" % table)


@fixture
def device_connect():
    data_type_device = {
        "type_title": "Beam",
        "description_type": "вращающиеся головы, которые имеют узконаправленный источник света. Угол раскрытия луча у приборов данного вида колеблется от 2 до 10 градусов.",
    }
    data_company = {
        "company_name": "Clay Paky",
        "producer_country": "Itali",
        "description_company": "https://www.claypaky.it/",
    }
    data_device = {"device_name": "k20", "company_id": 1, "type_device_id": 1}

    with DBSqlite("clean_device_test.db") as conn:
        company_interface = DeviceCompanyInterface(conn)
        company_interface.insert(data_company)

        type_interface = DeviceTypeInterface(conn)
        type_interface.insert(data_type_device)

        device_input = DeviceInterface(conn)
        device_input.insert(data_device)

        yield device_input

        for table in table_list[:-2]:
            conn.execute(
                "UPDATE `sqlite_sequence` SET `seq` = 0 WHERE `name` = '%s'" % table
            )
            conn.execute("DELETE FROM '%s'" % table)


@fixture
def company_connect():
    data_company = {
        "company_name": "Clay Paky",
        "producer_country": "Itali",
        "description_company": "https://www.claypaky.it/",
    }

    with DBSqlite("clean_device_test.db") as conn:
        company_interface = DeviceCompanyInterface(conn)
        company_interface.insert(data_company)

        yield company_interface

        conn.execute(
            "UPDATE `sqlite_sequence` SET `seq` = 0 WHERE `name` = '%s'"
            % "device_company"
        )
        conn.execute("DELETE FROM '%s'" % "device_company")


@fixture
def type_connect():
    data_type_device = {
        "type_title": "Beam",
        "description_type": "вращающиеся головы, которые имеют узконаправленный источник света. Угол раскрытия луча у приборов данного вида колеблется от 2 до 10 градусов.",
    }

    with DBSqlite("clean_device_test.db") as conn:
        type_interface = DeviceTypeInterface(conn)
        type_interface.insert(data_type_device)

        yield type_interface

        conn.execute(
            "UPDATE `sqlite_sequence` SET `seq` = 0 WHERE `name` = '%s'" % "device_type"
        )
        conn.execute("DELETE FROM '%s'" % "device_type")
