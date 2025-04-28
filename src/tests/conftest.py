from pytest import fixture
from src.db_app import DBSqlite
from src.interface import (
    DeviceCompanyTable,
    DeviceTable,
    DeviceTypeTable,
    InterfaceConnectDB,
    QueryInterface,
    StockDeviceTable,
    company_factory,
    device_factory,
    device_type_factory,
    stock_device_factory,
)
from src.run_bot import DBotAPI
from src.secret import secrets

table_list = ["device", "device_type", "device_company", "stock_device"]


@fixture
def bot_api():
    db_name = secrets["DB_TEST"]
    bot = DBotAPI()
    if db_name:
        bot.db_name = db_name
        yield bot


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
def company_connect():
    with DBSqlite("clean_device_test.db") as conn:
        interface = InterfaceConnectDB(
            conn,
            row_factory=company_factory,
            query=QueryInterface(table=DeviceCompanyTable),
        )
        set_data = [
            ("Clay Paky", "Itali", "https://www.claypaky.it/"),
            (
                "Light Craft",
                "Russia",
                "https://light-craft.ru/",
            ),
        ]
        interface.set_many_data(set_data)

        yield interface

        conn.execute(
            "UPDATE `sqlite_sequence` SET `seq` = 0 WHERE `name` = '%s'"
            % "device_company"
        )
        conn.execute("DELETE FROM '%s'" % "device_company")


@fixture
def type_connect():
    with DBSqlite("clean_device_test.db") as conn:
        interface = InterfaceConnectDB(
            conn,
            row_factory=device_type_factory,
            query=QueryInterface(table=DeviceTypeTable),
        )
        set_data = [
            ("beam", "Light device not spot"),
            ("spot", "light device not beam"),
        ]
        interface.set_many_data(set_data)

        yield interface

        conn.execute(
            "UPDATE `sqlite_sequence` SET `seq` = 0 WHERE `name` = '%s'" % "device_type"
        )
        conn.execute("DELETE FROM '%s'" % "device_type")


@fixture
def stock_device_connect():
    type_device_data = [
        ("beam", "Light device not spot"),
        ("spot", "light device not beam"),
    ]
    company_device = [
        ("Clay Paky", "Itali", "https://www.claypaky.it/"),
        (
            "Light Craft",
            "Russia",
            "https://light-craft.ru/",
        ),
    ]
    data_device = [("k20", 1, 1), ("laser beam", 2, 1)]

    stock_device = [("25", "1", "2025-04-19"), ("35", "2", "2025-04-29")]

    with DBSqlite("clean_device_test.db") as conn:
        company_interface = InterfaceConnectDB(
            conn,
            row_factory=company_factory,
            query=QueryInterface(table=DeviceCompanyTable),
        )
        company_interface.set_many_data(company_device)

        type_interface = InterfaceConnectDB(
            conn,
            row_factory=device_type_factory,
            query=QueryInterface(table=DeviceTypeTable),
        )
        type_interface.set_many_data(type_device_data)

        device_input = InterfaceConnectDB(
            conn, row_factory=device_factory, query=QueryInterface(table=DeviceTable)
        )
        device_input.set_many_data(data_device)

        stock_devices = InterfaceConnectDB(
            conn,
            row_factory=stock_device_factory,
            query=QueryInterface(table=StockDeviceTable),
        )
        stock_devices.set_many_data(stock_device)

        yield stock_devices

        for table in table_list:
            conn.execute(
                "UPDATE `sqlite_sequence` SET `seq` = 0 WHERE `name` = '%s'" % table
            )
            conn.execute("DELETE FROM '%s'" % table)


@fixture
def device_connect():
    type_device_data = [
        ("beam", "Light device not spot"),
        ("spot", "light device not beam"),
    ]
    company_device = [
        ("Clay Paky", "Itali", "https://www.claypaky.it/"),
        (
            "Light Craft",
            "Russia",
            "https://light-craft.ru/",
        ),
    ]
    data_device = [("k20", 1, 1), ("laser beam", 2, 1)]

    with DBSqlite("clean_device_test.db") as conn:
        company_interface = InterfaceConnectDB(
            conn,
            row_factory=company_factory,
            query=QueryInterface(table=DeviceCompanyTable),
        )
        company_interface.set_many_data(company_device)

        type_interface = InterfaceConnectDB(
            conn,
            row_factory=device_type_factory,
            query=QueryInterface(table=DeviceTypeTable),
        )
        type_interface.set_many_data(type_device_data)

        device_input = InterfaceConnectDB(
            conn, row_factory=device_factory, query=QueryInterface(table=DeviceTable)
        )
        device_input.set_many_data(data_device)

        yield device_input

        for table in table_list:
            conn.execute(
                "UPDATE `sqlite_sequence` SET `seq` = 0 WHERE `name` = '%s'" % table
            )
            conn.execute("DELETE FROM '%s'" % table)


@fixture
def query_interface():
    tdqi = QueryInterface(DeviceTypeTable)
    yield tdqi
