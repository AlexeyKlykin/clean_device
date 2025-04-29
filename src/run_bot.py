"""
Модуль для инициализации бота
"""

import logging
import os
import sqlite3
from typing import Dict, List
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.data_resolve_interface import InterfaceConnectDB
from src.db_app import DBSqlite

from src.query_interface import QueryInterface
from src.schema_for_validate import (
    DeviceCompanyTable,
    DeviceTable,
    DeviceTypeTable,
    OutputDeviceCompanyTable,
    OutputDeviceTable,
    OutputDeviceTypeTable,
    RowValue,
    StockBrockenDeviceData,
    StockDeviceData,
    StockDeviceTable,
    TableRow,
    company_factory,
    device_factory,
    device_type_factory,
    output_brocket_device_factory,
    output_company_factory,
    output_device_factory,
    output_device_type_factory,
    repr_stock_device_factory,
    stock_device_factory,
)
from src.secret import secrets
from src.utils import modificate_date_to_str


logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


class TokenError(Exception): ...


if os.environ.get("TOKEN"):
    token = os.environ["TOKEN"]
else:
    token = secrets["TOKEN"]


if token:
    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

else:
    raise TokenError("Ошибка подключения бота. Неверный токен")


class StockDeviceCallback(CallbackData, prefix="add_stock_device"):
    reaction_text: str
    stock_device_id: str


class DeviceCallback(CallbackData, prefix="add_device"):
    reaction_text: str
    device_name: str


class CompanyCallback(CallbackData, prefix="add_company"):
    reaction_text: str
    company_name: str


class DeviceTypeCallback(CallbackData, prefix="add_type"):
    reaction_text: str
    device_type: str


# тест
class DBotAPI:
    def __init__(self) -> None:
        if os.environ.get("DB_NAME"):
            self.db_name = os.environ["DB_NAME"]
        else:
            self.db_name = secrets["DB_NAME"]

    def set_full_data(self):
        fp_lst = [
            "stock_device_202504282233.sql",
            "device_202504282234.sql",
            "device_company_202504282234.sql",
            "device_type_202504282235.sql",
        ]

        if isinstance(self.db_name, str):
            with DBSqlite(self.db_name) as conn:
                for fp in fp_lst:
                    with open(fp, "r") as file:
                        conn.executescript(file.read())

        else:
            raise TypeError("Не передано название базы данных")

    def add_mark_device(
        self, stock_device_id: str | None, device_name: str | None, mark: str | None
    ):
        if isinstance(self.db_name, str):
            with DBSqlite(self.db_name) as conn:
                interface = InterfaceConnectDB(
                    conn,
                    row_factory=output_device_factory,
                    query=QueryInterface(table=StockDeviceData),
                )

                if stock_device_id and device_name and mark:
                    device_id = self.get_device_id(device_name=device_name)
                    interface.mark_device(
                        stock_device_id=(
                            TableRow("stock_device_id"),
                            RowValue(stock_device_id),
                        ),
                        device_id=(TableRow("device_id"), RowValue(device_id)),
                        mark=mark,
                    )
        else:
            raise TypeError("Не передано название базы данных")

    def get_broken_stock_device_at_date(
        self, date: str | None = None
    ) -> List[StockBrockenDeviceData] | str:
        stock_devices = []

        if isinstance(self.db_name, str):
            with DBSqlite(self.db_name) as conn:
                interface = InterfaceConnectDB(
                    conn,
                    row_factory=output_brocket_device_factory,
                    query=QueryInterface(table=StockBrockenDeviceData),
                )

                if date:
                    stock_devices = (
                        interface.get_to_retrieve_all_broken_devices_at_date(
                            (TableRow("at_clean_date"), RowValue(date)),
                        )
                    )

                else:
                    stock_devices = (
                        interface.get_to_retrieve_all_broken_devices_at_date(
                            (
                                TableRow("d.at_clean_date"),
                                RowValue(modificate_date_to_str()),
                            ),
                        )
                    )

        return stock_devices

    def get_stock_device_id(
        self, stock_device_id: str | None, stock_device_name: str | None
    ) -> dict | str:
        if isinstance(self.db_name, str):
            with DBSqlite(self.db_name) as conn:
                interface = InterfaceConnectDB(
                    conn,
                    row_factory=repr_stock_device_factory,
                    query=QueryInterface(table=StockDeviceData),
                )

                if (stock_device_id and stock_device_name) and self.check_stock_device(
                    stock_device_id, stock_device_name
                ):
                    try:
                        stock_device = interface.get_repr_stock_data(
                            int(stock_device_id), stock_device_name
                        )
                        if stock_device:
                            return stock_device.model_dump()
                        else:
                            return "Прибора не существует в базе"

                    except ValueError:
                        raise ValueError((f"{stock_device_id} должен быть числом"))

                else:
                    logger.warning(
                        f"Прибор с id-{stock_device_id} и названием {stock_device_name} не существует в базе"
                    )
                    return f"Прибор с id-{stock_device_id} и названием {stock_device_name} не существует в базе"

        else:
            raise TypeError("Не передано название базы данных")

    def check_type_id(self, type_title: str | None) -> bool:
        if isinstance(self.db_name, str):
            with DBSqlite(self.db_name) as conn:
                interface = InterfaceConnectDB(
                    conn,
                    row_factory=device_type_factory,
                    query=QueryInterface(table=DeviceTypeTable),
                )

                if type_title:
                    device_type = interface.get_once_data(
                        row="type_title", val=type_title
                    )

                    if device_type:
                        return True
                    else:
                        return False
                else:
                    raise ValueError

        else:
            raise TypeError("Не передано название базы данных")

    def check_company_id(self, company_name: str | None) -> bool:
        if isinstance(self.db_name, str):
            with DBSqlite(self.db_name) as conn:
                interface = InterfaceConnectDB(
                    conn,
                    row_factory=company_factory,
                    query=QueryInterface(table=DeviceCompanyTable),
                )

                if company_name:
                    company = interface.get_once_data(
                        row="company_name", val=company_name
                    )

                    if company:
                        return True
                    else:
                        return False
                else:
                    raise ValueError
        else:
            raise TypeError("Не передано название базы данных")

    def save_stock_device_into_db_from_bot(self, data: Dict[str, str]):
        if isinstance(self.db_name, str):
            with DBSqlite(self.db_name) as conn:
                interface = InterfaceConnectDB(
                    conn,
                    row_factory=stock_device_factory,
                    query=QueryInterface(table=StockDeviceTable),
                )
                date = modificate_date_to_str()

                match data:
                    case {
                        "stock_device_id": str(stock_device_id),
                        "device_name": str(device_name),
                    }:
                        device_id = self.get_device_id(device_name)
                        set_data = (
                            RowValue(stock_device_id),
                            RowValue(device_id),
                            RowValue(date),
                        )
                        interface.set_data(set_data)

                    case _:
                        raise ValueError
        else:
            raise TypeError("Не передано название базы данных")

    def get_device_id(self, device_name: str | None) -> str:
        if isinstance(self.db_name, str):
            with DBSqlite(self.db_name) as conn:
                interface = InterfaceConnectDB(
                    conn,
                    row_factory=output_device_factory,
                    query=QueryInterface(table=OutputDeviceTable),
                )

                if device_name:
                    device = interface.get_once_data(row="device_name", val=device_name)
                    if device:
                        return str(device.device_id)
                    else:
                        raise ValueError(f"Устройства {device_name} не найдено")
                else:
                    raise ValueError
        else:
            raise TypeError("Не передано название базы данных")

    def check_device_id(self, device_name: str | None) -> bool:
        if isinstance(self.db_name, str):
            with DBSqlite(self.db_name) as conn:
                interface = InterfaceConnectDB(
                    conn,
                    row_factory=device_factory,
                    query=QueryInterface(table=DeviceTable),
                )

                if device_name:
                    device = interface.get_once_data(row="device_name", val=device_name)
                    if device:
                        return True
                    else:
                        return False
                else:
                    raise ValueError
        else:
            raise TypeError("Не передано название базы данных")

    def check_stock_device(
        self, stock_device_id: str | None, device_name: str | None
    ) -> bool:
        if isinstance(self.db_name, str):
            if self.check_stock_device_id(stock_device_id) and self.check_device_id(
                device_name
            ):
                return True
            else:
                return False
        else:
            raise TypeError("Не передано название базы данных")

    def update_stock_device(self, stock_device_id: str | None, device_name: str | None):
        if isinstance(self.db_name, str):
            with DBSqlite(self.db_name) as conn:
                interface = InterfaceConnectDB(
                    conn,
                    row_factory=stock_device_factory,
                    query=QueryInterface(table=StockDeviceTable),
                )
                date = modificate_date_to_str()

                if (
                    self.check_device_id(device_name)
                    and self.check_stock_device_id(stock_device_id)
                    and device_name
                    and stock_device_id
                ):
                    device_id = self.get_device_id(device_name)
                    set_data = (TableRow("at_clean_date"), RowValue(date))
                    one_data = (TableRow("stock_device_id"), RowValue(stock_device_id))
                    two_data = (TableRow("device_id"), RowValue(device_id))
                    interface.update_data(set_data, one_data, two_data)
                else:
                    raise ValueError
        else:
            raise TypeError("Не передано название базы данных")

    def check_stock_device_id(self, stock_device_id: str | None) -> bool:
        if isinstance(self.db_name, str):
            with DBSqlite(self.db_name) as conn:
                interface = InterfaceConnectDB(
                    conn,
                    row_factory=stock_device_factory,
                    query=QueryInterface(table=StockDeviceTable),
                )
                if stock_device_id:
                    stock_device = interface.get_once_data(
                        row="stock_device_id", val=stock_device_id
                    )

                    if stock_device:
                        return True
                    else:
                        return False
                else:
                    raise ValueError
        else:
            raise TypeError("Не передано название базы данных")

    def save_device_type_from_bot_into_db(self, data: Dict[str, str]):
        if isinstance(self.db_name, str):
            with DBSqlite(self.db_name) as conn:
                interface = InterfaceConnectDB(
                    conn,
                    row_factory=device_type_factory,
                    query=QueryInterface(table=DeviceTypeTable),
                )
                interface.set_data(set_data=tuple(data.values()))

        else:
            raise TypeError("Не передано название базы данных")

    def save_company_from_bot_into_db(self, data: Dict[str, str]):
        if isinstance(self.db_name, str):
            with DBSqlite(self.db_name) as conn:
                interface = InterfaceConnectDB(
                    conn,
                    row_factory=company_factory,
                    query=QueryInterface(table=DeviceCompanyTable),
                )
                interface.set_data(set_data=tuple(data.values()))

        else:
            raise TypeError("Не передано название базы данных")

    def get_company_id(self, company_name: str | None) -> str:
        if isinstance(self.db_name, str):
            with DBSqlite(self.db_name) as conn:
                interface = InterfaceConnectDB(
                    conn,
                    row_factory=output_company_factory,
                    query=QueryInterface(table=OutputDeviceCompanyTable),
                )
                if company_name:
                    company = interface.get_once_data(
                        row="company_name", val=company_name
                    )

                    if company:
                        return str(company.company_id)
                    else:
                        raise ValueError
                else:
                    raise ValueError
        else:
            raise TypeError("Не передано название базы данных")

    def get_type_id(self, type_title: str | None) -> str:
        if isinstance(self.db_name, str):
            with DBSqlite(self.db_name) as conn:
                interface = InterfaceConnectDB(
                    conn,
                    row_factory=output_device_type_factory,
                    query=QueryInterface(table=OutputDeviceTypeTable),
                )
                if type_title:
                    type_device = interface.get_once_data(
                        row="type_title", val=type_title
                    )

                    if type_device:
                        return str(type_device.type_device_id)
                    else:
                        raise ValueError
                else:
                    raise ValueError
        else:
            raise TypeError("Не передано название базы данных")

    def save_device_from_bot_into_db(self, data: Dict[str, str]):
        if isinstance(self.db_name, str):
            with DBSqlite(self.db_name) as conn:
                interface = InterfaceConnectDB(
                    conn,
                    row_factory=device_factory,
                    query=QueryInterface(table=DeviceTable),
                )

                match data:
                    case {
                        "device_name": str(device_name),
                        "company_name": str(company_name),
                        "type_title": str(type_title),
                    }:
                        company_id = self.get_company_id(company_name)
                        device_type_id = self.get_type_id(type_title)
                        item = (device_name, company_id, device_type_id)
                        interface.set_data(item)

                    case _:
                        raise ValueError
        else:
            raise TypeError("Не передано название базы данных")

    def get_all_stock_device_id(self) -> List[str]:
        lst_stock_device_id = []
        if isinstance(self.db_name, str):
            with DBSqlite(self.db_name) as conn:
                interface = InterfaceConnectDB(
                    conn,
                    row_factory=stock_device_factory,
                    query=QueryInterface(table=StockDeviceTable),
                )
                lst_stock_device_id: List[str] = []

                for stock_device in interface.get_all_data():
                    lst_stock_device_id.append(stock_device.stock_device_id)

            if len(lst_stock_device_id) == 0:
                logger.warning("Список пустой")
        else:
            raise TypeError("Не передано название базы данных")

        return lst_stock_device_id

    def get_all_devices(self) -> List[str]:
        lst_device_name = []

        if isinstance(self.db_name, str):
            with DBSqlite(self.db_name) as conn:
                interface = InterfaceConnectDB(
                    conn,
                    row_factory=device_factory,
                    query=QueryInterface(table=DeviceTable),
                )
                lst_device_name = []

                for device in interface.get_all_data():
                    if device:
                        lst_device_name.append(device.device_name)
                    else:
                        raise ValueError("Нет данных для передачи")

            if len(lst_device_name) == 0:
                logger.warning("Список пуст")
        else:
            raise TypeError("Не передано название базы данных")

        return lst_device_name

    def get_all_company(self) -> List[str]:
        lst_company_name = []

        if isinstance(self.db_name, str):
            with DBSqlite(self.db_name) as conn:
                interface = InterfaceConnectDB(
                    conn,
                    row_factory=company_factory,
                    query=QueryInterface(table=DeviceCompanyTable),
                )

                for company in interface.get_all_data():
                    lst_company_name.append(company.company_name)

            if len(lst_company_name) == 0:
                logger.warning("Список пуст")
        else:
            raise TypeError("Не передано название базы данных")

        return lst_company_name

    def get_all_type(self) -> List[str]:
        lst_type_device_title = []

        if isinstance(self.db_name, str):
            with DBSqlite(self.db_name) as conn:
                interface = InterfaceConnectDB(
                    conn,
                    row_factory=device_type_factory,
                    query=QueryInterface(table=DeviceTypeTable),
                )

                for type_device in interface.get_all_data():
                    lst_type_device_title.append(type_device.type_title)

            if len(lst_type_device_title) == 0:
                logger.warning("Список пуст")
        else:
            raise TypeError("Не передано название базы данных")

        return lst_type_device_title

    def gen_inline_kb_for_get_request(
        self, type_request_list: str
    ) -> InlineKeyboardMarkup:
        kb_builder = InlineKeyboardBuilder()
        kb_builder.button(text="Cancel", callback_data="/cancel")

        try:
            match type_request_list:
                case "mark":
                    [
                        kb_builder.button(
                            text=item,
                            callback_data=DeviceCallback(
                                reaction_text=f"mark_device_{item}",
                                device_name=item,
                            ),
                        )
                        for item in self.get_all_devices()
                    ]

                case "stock_device":
                    [
                        kb_builder.button(
                            text=item,
                            callback_data=StockDeviceCallback(
                                reaction_text=f"get_stock_device_{item}",
                                stock_device_id=item,
                            ),
                        )
                        for item in self.get_all_stock_device_id()
                    ]

                case "device":
                    [
                        kb_builder.button(
                            text=item,
                            callback_data=DeviceCallback(
                                reaction_text=f"get_device_{item}", device_name=item
                            ),
                        )
                        for item in self.get_all_devices()
                    ]

                case "company":
                    [
                        kb_builder.button(
                            text=item,
                            callback_data=CompanyCallback(
                                reaction_text=item, company_name=item
                            ),
                        )
                        for item in self.get_all_company()
                    ]

                case "device_type":
                    [
                        kb_builder.button(
                            text=item,
                            callback_data=DeviceTypeCallback(
                                reaction_text=f"get_device_type_{item}",
                                device_type=item,
                            ),
                        )
                        for item in self.get_all_type()
                    ]
                case _:
                    raise ValueError(
                        f"{type_request_list} должен быть одним из [stock_device, device, company]"
                    )

        except sqlite3.Error as err:
            raise err

        kb_builder.adjust(3)
        return kb_builder.as_markup()

    def gen_inline_kb(self, type_request_list: str) -> InlineKeyboardMarkup:
        kb_builder = InlineKeyboardBuilder()
        kb_builder.button(text="Cancel", callback_data="/cancel")

        try:
            match type_request_list:
                case "stock_device":
                    [
                        kb_builder.button(
                            text=item,
                            callback_data=StockDeviceCallback(
                                reaction_text=item, stock_device_id=item
                            ),
                        )
                        for item in self.get_all_stock_device_id()
                    ]

                case "device":
                    [
                        kb_builder.button(
                            text=item,
                            callback_data=DeviceCallback(
                                reaction_text=item, device_name=item
                            ),
                        )
                        for item in self.get_all_devices()
                    ]

                case "company":
                    [
                        kb_builder.button(
                            text=item,
                            callback_data=CompanyCallback(
                                reaction_text=item, company_name=item
                            ),
                        )
                        for item in self.get_all_company()
                    ]

                case "device_type":
                    [
                        kb_builder.button(
                            text=item,
                            callback_data=DeviceTypeCallback(
                                reaction_text=item, device_type=item
                            ),
                        )
                        for item in self.get_all_type()
                    ]
                case _:
                    raise ValueError(
                        f"{type_request_list} должен быть одним из [stock_device, device, company]"
                    )

        except sqlite3.Error as err:
            raise err

        kb_builder.adjust(3)
        return kb_builder.as_markup()
