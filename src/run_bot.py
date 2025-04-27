"""
Модуль для инициализации бота
"""

from datetime import datetime
import logging
import sqlite3
from typing import Dict, Generator, List, Tuple
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.db_app import DBSqlite
from src.interface import (
    OutputDeviceCompanyTable,
    OutputDeviceTable,
    OutputDeviceTypeTable,
    QueryInterface,
    InterfaceConnectDB,
    DeviceTable,
    DeviceTypeTable,
    DeviceCompanyTable,
    RowValue,
    StockDeviceTable,
    TableRow,
    company_factory,
    device_factory,
    device_type_factory,
    output_company_factory,
    output_device_factory,
    output_device_type_factory,
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
    stock_device_id: int


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
        self.db_name = secrets["DB_NAME"]

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

    def update_stock_device(self, stock_device_id: str | None):
        if isinstance(self.db_name, str):
            with DBSqlite(self.db_name) as conn:
                interface = InterfaceConnectDB(
                    conn,
                    row_factory=stock_device_factory,
                    query=QueryInterface(table=StockDeviceTable),
                )
                date = modificate_date_to_str()

                if stock_device_id:
                    set_data = (TableRow("at_clean_date"), RowValue(date))
                    where_data = (
                        TableRow("stock_device_id"),
                        RowValue(stock_device_id),
                    )
                    interface.update_data(set_data, where_data)
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
        if isinstance(self.db_name, str):
            with DBSqlite(self.db_name) as conn:
                interface = InterfaceConnectDB(
                    conn,
                    row_factory=stock_device_factory,
                    query=QueryInterface(table=StockDeviceTable),
                )
                lst_stock_device_id: List[str] = []

                for stock_device in interface.get_all_data():
                    if stock_device:
                        [
                            lst_stock_device_id.append(device.stock_device_id)
                            for device in stock_device
                        ]
                    else:
                        raise ValueError("Нет данных для передачи")

                if lst_stock_device_id:
                    return lst_stock_device_id
                else:
                    raise ValueError("Список пуст")
        else:
            raise TypeError("Не передано название базы данных")

    def get_all_devices(self) -> List[str]:
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
                        [
                            lst_device_name.append(device.device_name)
                            for device in device
                        ]
                    else:
                        raise ValueError("Нет данных для передачи")

                if lst_device_name:
                    return lst_device_name
                else:
                    raise ValueError("Список пуст")
        else:
            raise TypeError("Не передано название базы данных")

    def get_all_company(self) -> List[str]:
        if isinstance(self.db_name, str):
            with DBSqlite(self.db_name) as conn:
                interface = InterfaceConnectDB(
                    conn,
                    row_factory=company_factory,
                    query=QueryInterface(table=DeviceCompanyTable),
                )
                lst_company_name = []

                for companys in interface.get_all_data():
                    if companys:
                        [
                            lst_company_name.append(company.company_name)
                            for company in companys
                        ]
                    else:
                        raise ValueError("Нет данных для передачи")

                if lst_company_name:
                    return lst_company_name
                else:
                    raise ValueError("Список пуст")
        else:
            raise TypeError("Не передано название базы данных")

    def get_all_type(self) -> List[str]:
        if isinstance(self.db_name, str):
            with DBSqlite(self.db_name) as conn:
                interface = InterfaceConnectDB(
                    conn,
                    row_factory=device_type_factory,
                    query=QueryInterface(table=DeviceTypeTable),
                )
                lst_type_device_title = []

                for type_devices in interface.get_all_data():
                    if type_devices:
                        [
                            lst_type_device_title.append(type_device.type_title)
                            for type_device in type_devices
                        ]
                    else:
                        raise ValueError("Нет данных для передачи")

                if lst_type_device_title:
                    return lst_type_device_title
                else:
                    raise ValueError("Список пуст")
        else:
            raise TypeError("Не передано название базы данных")

    def gen_inline_kb(self, type_request_list: str) -> InlineKeyboardMarkup:
        lst_btn = []

        try:
            match type_request_list:
                case "stock_device":
                    device_list = self.get_all_stock_device_id()
                    lst_btn = [
                        [
                            InlineKeyboardButton(
                                text=str(item),
                                callback_data=StockDeviceCallback(
                                    reaction_text=str(item),
                                    stock_device_id=int(item),
                                ).pack(),
                            )
                            for item in device_list
                        ],
                    ]
                    lst_btn.append(
                        [
                            InlineKeyboardButton(
                                text="/add_stock_device",
                                callback_data="add_stock_device",
                            )
                        ]
                    )
                case "device":
                    device_list = self.get_all_devices()
                    lst_btn = [
                        [
                            InlineKeyboardButton(
                                text=str(item),
                                callback_data=DeviceCallback(
                                    reaction_text=str(item),
                                    device_name=str(item),
                                ).pack(),
                            )
                            for item in device_list
                        ]
                    ]
                    lst_btn.append(
                        [
                            InlineKeyboardButton(
                                text="/add_device",
                                callback_data="add_device",
                            )
                        ]
                    )

                case "company":
                    device_list = self.get_all_company()
                    lst_btn = [
                        [
                            InlineKeyboardButton(
                                text=item,
                                callback_data=CompanyCallback(
                                    reaction_text=item,
                                    company_name=item,
                                ).pack(),
                            )
                            for item in device_list
                        ]
                    ]
                    lst_btn.append(
                        [
                            InlineKeyboardButton(
                                text="/add_device_company",
                                callback_data="add_device_company",
                            )
                        ]
                    )

                case "device_type":
                    device_list = self.get_all_type()
                    lst_btn = [
                        [
                            InlineKeyboardButton(
                                text=item,
                                callback_data=DeviceTypeCallback(
                                    reaction_text=(item),
                                    device_type=str(item),
                                ).pack(),
                            )
                            for item in device_list
                        ]
                    ]
                    lst_btn.append(
                        [
                            InlineKeyboardButton(
                                text="/add_device_type",
                                callback_data="add_device_type",
                            )
                        ]
                    )

                case _:
                    raise ValueError(
                        f"{type_request_list} должен быть одним из [stock_device, device, company]"
                    )

        except sqlite3.Error as err:
            raise err

        return InlineKeyboardMarkup(inline_keyboard=lst_btn)
