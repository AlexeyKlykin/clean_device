"""
Модуль для инициализации бота
"""

import logging
from typing import Dict
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.filters.callback_data import CallbackData

from src.db_app import DBSqlite
from src.interface import (
    OutputDeviceCompanyTable,
    OutputDeviceTypeTable,
    QueryInterface,
    InterfaceConnectDB,
    DeviceTable,
    DeviceTypeTable,
    DeviceCompanyTable,
    company_factory,
    device_factory,
    device_type_factory,
    output_company_factory,
    output_device_type_factory,
)
from src.secret import secrets


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

    # def check_stock_device_by_id(self, device_id: int) -> bool:
    #     if isinstance(self.db_name, str):
    #         with DBSqlite(self.db_name) as conn:
    #             interface = StockDevicesInterface(conn)
    #             return interface.check_device_by_id(device_id=device_id)
    #
    #     else:
    #         raise TypeError("Не передано название базы данных")
    #
    # def update_stock_device_by_id(self, device_id: int):
    #     if isinstance(self.db_name, str):
    #         with DBSqlite(self.db_name) as conn:
    #             interface = StockDevicesInterface(conn)
    #             return interface.update_stock_device_date(device_id=device_id)
    #
    #     else:
    #         raise TypeError("Не передано название базы данных")
    #
    # def check_device_by_title(self, device_name: str) -> bool:
    #     if isinstance(self.db_name, str):
    #         with DBSqlite(self.db_name) as conn:
    #             interface = DeviceInterface(conn)
    #             return interface.check_by_title(device_name)
    #
    #     else:
    #         raise TypeError("Не передано название базы данных")
    #
    # def get_device_id_by_name(self, device_name: str) -> int:
    #     if isinstance(self.db_name, str):
    #         with DBSqlite(self.db_name) as conn:
    #             interface = DeviceInterface(conn)
    #             return interface.get_id_by_name(device_name=device_name)
    #
    #     else:
    #         raise TypeError("Не передано название базы данных")
    #
    # def get_device_type_id_by_name(self, device_type_name: str) -> int:
    #     if isinstance(self.db_name, str):
    #         with DBSqlite(self.db_name) as conn:
    #             interface = DeviceTypeInterface(conn)
    #             return interface.get_id_by_title(device_type_name)
    #
    #     else:
    #         raise TypeError("Не передано название базы данных")
    #
    # def check_company_by_title(self, device_company: str) -> bool:
    #     if isinstance(self.db_name, str):
    #         with DBSqlite(self.db_name) as conn:
    #             interface = DeviceCompanyInterface(conn)
    #             return interface.check_by_title(device_company)
    #
    #     else:
    #         raise TypeError("Не передано название базы данных")
    #
    # def get_company_id_by_name(self, device_company: str) -> int:
    #     if isinstance(self.db_name, str):
    #         with DBSqlite(self.db_name) as conn:
    #             interface = DeviceCompanyInterface(conn)
    #             return interface.get_id_by_name(device_company)
    #
    #     else:
    #         raise TypeError("Не передано название базы данных")
    #
    # def get_all_device_type(self) -> List[str]:
    #     if isinstance(self.db_name, str):
    #         with DBSqlite(self.db_name) as conn:
    #             interface = DeviceTypeInterface(conn)
    #             return interface.get_all_type()
    #
    #     else:
    #         raise TypeError("Не передано название базы данных")
    #
    # def save_device_from_bot_into_db(self, data: Dict[str, str]):
    #     try:
    #         if isinstance(self.db_name, str):
    #             with DBSqlite(self.db_name) as conn:
    #                 interface = DeviceInterface(conn)
    #                 interface.insert(data)
    #
    #         else:
    #             raise TypeError("Не передано название базы данных")
    #     except Exception as err:
    #         raise err
    #     # with open("temp_stock_device.json", "w") as js:
    #     #     json.dump(obj=data, fp=js)
    #
    # def save_company_from_bot_into_db(self, data: Dict[str, str]):
    #     try:
    #         if isinstance(self.db_name, str):
    #             with DBSqlite(self.db_name) as conn:
    #                 interface = DeviceCompanyInterface(conn)
    #                 interface.insert(data)
    #
    #         else:
    #             raise TypeError("Не передано название базы данных")
    #     except Exception as err:
    #         raise err
    #
    # def save_device_type_from_bot_into_db(self, data: Dict[str, str]):
    #     try:
    #         if isinstance(self.db_name, str):
    #             with DBSqlite(self.db_name) as conn:
    #                 interface = DeviceTypeInterface(conn)
    #                 interface.insert(data)
    #
    #         else:
    #             raise TypeError("Не передано название базы данных")
    #
    #     except Exception as err:
    #         raise err
    #
    # def save_stock_device_from_bot_into_db(self, data: Dict[str, str]):
    #     try:
    #         if isinstance(self.db_name, str):
    #             with DBSqlite(self.db_name) as conn:
    #                 interface = StockDevicesInterface(conn)
    #                 interface.insert(data)
    #
    #         else:
    #             raise TypeError("Не передано название базы данных")
    #     except Exception as err:
    #         raise err
    #
    # def get_all_stock_device_id(self) -> List[int]:
    #     if isinstance(self.db_name, str):
    #         with DBSqlite(self.db_name) as conn:
    #             interface = StockDevicesInterface(conn)
    #             return interface.get_all_stock_device_id()
    #
    #     else:
    #         raise TypeError("Не передано название базы данных")
    #
    # def get_all_devices_name(self) -> List[str]:
    #     if isinstance(self.db_name, str):
    #         with DBSqlite(self.db_name) as conn:
    #             interface = DeviceInterface(conn)
    #             return interface.get_all_device_name()
    #
    #     else:
    #         raise TypeError("Не передано название базы данных")
    #
    # def get_all_company_name(self) -> List[str]:
    #     if isinstance(self.db_name, str):
    #         with DBSqlite(self.db_name) as conn:
    #             interface = DeviceCompanyInterface(conn)
    #             return interface.get_all_company()
    #
    #     else:
    #         raise TypeError("Не передано название базы данных")
    #
    # def get_now_date(self) -> str:
    #     template = "{day}-{month}-{year}"
    #     date = datetime.now()
    #     return template.format(day=date.day, month=date.month, year=date.year)
    #
    # def request_list_items(self, type_request_list: str) -> InlineKeyboardMarkup:
    #     lst_btn = []
    #
    #     try:
    #         if isinstance(self.db_name, str):
    #             with DBSqlite(self.db_name) as conn:
    #                 match type_request_list:
    #                     case "stock_device":
    #                         interface = StockDevicesInterface(conn)
    #                         device_list = interface.get_all_stock_device_id()
    #                         lst_btn = [
    #                             [
    #                                 InlineKeyboardButton(
    #                                     text=str(item),
    #                                     callback_data=StockDeviceCallback(
    #                                         reaction_text=str(item),
    #                                         stock_device_id=item,
    #                                     ).pack(),
    #                                 )
    #                                 for item in device_list
    #                                 if isinstance(item, str | int)
    #                             ],
    #                         ]
    #                         lst_btn.append(
    #                             [
    #                                 InlineKeyboardButton(
    #                                     text="/add_stock_device",
    #                                     callback_data="add_stock_device",
    #                                 )
    #                             ]
    #                         )
    #                     case "device":
    #                         interface = DeviceInterface(conn)
    #                         device_list = interface.get_all_devices()
    #                         lst_btn = [
    #                             [
    #                                 InlineKeyboardButton(
    #                                     text=str(item[0]),
    #                                     callback_data=DeviceCallback(
    #                                         reaction_text=str(item[0]),
    #                                         device_name=str(item[1]),
    #                                     ).pack(),
    #                                 )
    #                                 for item in device_list
    #                                 if isinstance(item, tuple)
    #                             ]
    #                         ]
    #                         lst_btn.append(
    #                             [
    #                                 InlineKeyboardButton(
    #                                     text="/add_device",
    #                                     callback_data="add_device",
    #                                 )
    #                             ]
    #                         )
    #
    #                     case "company":
    #                         interface = DeviceCompanyInterface(conn)
    #                         device_list = interface.get_all_company()
    #                         lst_btn = [
    #                             [
    #                                 InlineKeyboardButton(
    #                                     text=item,
    #                                     callback_data=CompanyCallback(
    #                                         reaction_text=item,
    #                                         company_name=item,
    #                                     ).pack(),
    #                                 )
    #                                 for item in device_list
    #                             ]
    #                         ]
    #                         lst_btn.append(
    #                             [
    #                                 InlineKeyboardButton(
    #                                     text="/add_device_company",
    #                                     callback_data="add_device_company",
    #                                 )
    #                             ]
    #                         )
    #
    #                     case "device_type":
    #                         interface = DeviceTypeInterface(conn)
    #                         device_list = interface.get_all_type()
    #                         lst_btn = [
    #                             [
    #                                 InlineKeyboardButton(
    #                                     text=item,
    #                                     callback_data=DeviceTypeCallback(
    #                                         reaction_text=(item),
    #                                         device_type=str(item),
    #                                     ).pack(),
    #                                 )
    #                                 for item in device_list
    #                             ]
    #                         ]
    #                         lst_btn.append(
    #                             [
    #                                 InlineKeyboardButton(
    #                                     text="/add_device_type",
    #                                     callback_data="add_device_type",
    #                                 )
    #                             ]
    #                         )
    #
    #                     case _:
    #                         raise ValueError(
    #                             f"{type_request_list} должен быть одним из [stock_device, device, company]"
    #                         )
    #
    #     except Error as err:
    #         raise err
    #
    #     return InlineKeyboardMarkup(inline_keyboard=lst_btn)
