"""
Модуль для инициализации бота
"""

from abc import ABC, abstractmethod
from enum import StrEnum
import logging
import os
from typing import Dict, List, Literal
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

from src.data_resolve_interface import DatabaseTableHandlerInterface
from src.db_app import DBSqlite
from src.schema_for_validation import (
    DeviceCompanyTable,
    DeviceTable,
    DeviceTypeTable,
    OutputDeviceCompanyTable,
    OutputDeviceTable,
    OutputDeviceTypeTable,
    RowValue,
    StockBrokenDeviceData,
    StockDeviceData,
    StockDeviceTable,
    StockDeviceTableStatus,
    TableRow,
)
from src.secret import secrets
from src.utils import modificate_date_to_str, validate_date


logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


class TokenError(Exception): ...


class Marker(StrEnum):
    DCOMPANY = "device_company"
    DTYPE = "device_type"
    DEVICE = "device"
    GET_DEVICE = "get_device"
    MARKING_DEVICES = "marking_devices"


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


class DeviceTypeCallback(CallbackData, prefix="device_type"):
    text_search: str
    type_title: str


class DeviceCompanyCallback(CallbackData, prefix="device_company"):
    text_search: str
    company_name: str


class DeviceCallback(CallbackData, prefix="device"):
    text_search: str
    device_name: str


type Status = Literal["0", "1"]


class AbstractAPIBotDb(ABC):
    @abstractmethod
    def bot_keyboard_device_lst(self) -> List[str] | str: ...

    @abstractmethod
    def bot_keyboard_device_type_lst(self) -> List[str] | str: ...

    @abstractmethod
    def bot_keyboard_company_name_lst(self) -> List[str] | str: ...

    @abstractmethod
    def bot_inline_kb(self, marker: Marker) -> InlineKeyboardMarkup: ...

    @abstractmethod
    def bot_device_from_stockpile(
        self, where_data: Dict[str, str]
    ) -> Dict[str, str] | str: ...

    @abstractmethod
    def bot_device(self, device_name: str | None) -> Dict[str, str] | str: ...

    @abstractmethod
    def bot_company(self, company_name: str) -> Dict[str, str] | str: ...

    @abstractmethod
    def bot_device_type(self, type_title: str) -> Dict[str, str] | str: ...

    @abstractmethod
    def bot_lst_broken_device_from_stockpile(
        self, where_data: Dict[str, str] | None = None
    ) -> List[StockBrokenDeviceData] | str: ...

    @abstractmethod
    def bot_lst_device(self) -> List[Dict[str, str]] | str: ...

    @abstractmethod
    def bot_lst_company(self) -> List[Dict[str, str]] | str: ...

    @abstractmethod
    def bot_lst_device_type(self) -> List[Dict[str, str]]: ...

    @abstractmethod
    def bot_device_id(self, device_name: str | None) -> str: ...

    @abstractmethod
    def bot_company_id(self, company_name: str | None) -> str: ...

    @abstractmethod
    def bot_type_id(self, type_title: str | None) -> str: ...

    @abstractmethod
    def bot_check_device_from_stockpile(self, where_data: Dict[str, str]) -> bool: ...

    @abstractmethod
    def bot_check_device(self, device_name: str | None) -> bool: ...

    @abstractmethod
    def bot_check_company(self, company_name: str | None) -> bool: ...

    @abstractmethod
    def bot_check_type(self, type_title: str | None) -> bool: ...

    @abstractmethod
    def bot_change_device_status(self, where_data: Dict[str, str]) -> str | None: ...

    @abstractmethod
    def bot_set_device_from_stockpile_by_name_and_id_to_db(
        self, set_data: Dict[str, str]
    ) -> str: ...

    @abstractmethod
    def bot_set_device_type(self, set_data: Dict[str, str]) -> str: ...

    @abstractmethod
    def bot_set_device_company(self, set_data: Dict[str, str]) -> str: ...

    @abstractmethod
    def bot_set_device(self, set_data: Dict[str, str]) -> str: ...

    @abstractmethod
    def bot_update_devices_stock_clearence_date(
        self, set_data: Dict[str, str], date: str | None = None
    ) -> str: ...


class APIBotDb(AbstractAPIBotDb):
    def __init__(self, db_name: str | None = None) -> None:
        if db_name:
            self.db_name = db_name
        else:
            db_name = secrets["DB_NAME"]
            if isinstance(db_name, str):
                self.db_name = db_name
            else:
                self.db_name = os.environ.get("DB_NAME")

    def bot_device_from_stockpile(
        self, where_data: Dict[str, str]
    ) -> Dict[str, str] | str:
        """метод для получение прибора со склада по id и названию"""

        match where_data:
            case {
                "stock_device_id": str(stock_device_id),
                "device_name": str(device_name),
            }:
                where_mogrif_data = {
                    TableRow("sd.stock_device_id"): RowValue(stock_device_id),
                    TableRow("d.device_name"): RowValue(device_name),
                }

                if self.db_name:
                    with DBSqlite(self.db_name) as conn:
                        interface = DatabaseTableHandlerInterface(conn)
                        interface.schema = StockDeviceData
                        stock_device = interface.get_item(where_data=where_mogrif_data)
                        try:
                            return stock_device.model_dump()

                        except AttributeError as err:
                            logger.warning(err)
                            return f"Прибор с названием {device_name} не найден в базе"

                else:
                    raise Exception("Не верно указана база данных")

            case _:
                return f"Данные {where_data} не прошли валидацию"

    def bot_device(self, device_name: str | None) -> Dict[str, str] | str:
        """метод для получения прибора по имени"""

        if device_name:
            where_data = {TableRow("device_name"): RowValue(device_name)}

            if self.db_name:
                with DBSqlite(self.db_name) as conn:
                    interface = DatabaseTableHandlerInterface(conn)
                    interface.schema = OutputDeviceTable
                    device = interface.get_item(where_data=where_data)
                    try:
                        return device.model_dump()

                    except AttributeError as err:
                        logger.warning(err)
                        return f"Прибор с названием {device_name} не найден в базе"

            else:
                raise Exception("Не верно указана база данных")

        else:
            raise Exception("Не переданы аргументы")

    def bot_company(self, company_name: str) -> Dict[str, str] | str:
        """метод для получения данных о компании производителе"""

        if company_name:
            where_data = {TableRow("company_name"): RowValue(company_name)}

            if self.db_name:
                with DBSqlite(self.db_name) as conn:
                    interface = DatabaseTableHandlerInterface(conn)
                    interface.schema = OutputDeviceCompanyTable
                    company = interface.get_item(where_data=where_data)
                    try:
                        return company.model_dump()

                    except AttributeError as err:
                        logger.warning(err)
                        return f"Компания с названием {company_name} не найден в базе"

            else:
                raise Exception("Не верно указана база данных")

        else:
            raise Exception("Не переданы аргументы")

    def bot_device_type(self, type_title: str) -> Dict[str, str] | str:
        """метод для получения данных о типе прибора"""

        if type_title:
            where_data = {TableRow("type_title"): RowValue(type_title)}

            if self.db_name:
                with DBSqlite(self.db_name) as conn:
                    interface = DatabaseTableHandlerInterface(conn)
                    interface.schema = OutputDeviceTypeTable
                    device_type = interface.get_item(where_data=where_data)
                    try:
                        return device_type.model_dump()

                    except AttributeError as err:
                        logger.warning(err)
                        return f"Тип прибор с названием {type_title} не найден в базе"

            else:
                raise Exception("Не верно указана база данных")

        else:
            raise Exception("Не переданы аргументы")

    def bot_lst_broken_device_from_stockpile(
        self, where_data: Dict[str, str] | None = None
    ) -> List[StockBrokenDeviceData] | str:
        """метод для получения всех приборов со склада"""

        if self.db_name:
            with DBSqlite(self.db_name) as conn:
                interface = DatabaseTableHandlerInterface(conn)
                interface.schema = StockBrokenDeviceData

                match where_data:
                    case {"at_clean_date": str(at_clean_date)}:
                        where_mogrif_data = {
                            TableRow("sd.at_clean_date"): RowValue(at_clean_date),
                        }

                        stock_device = interface.get_items(where_data=where_mogrif_data)
                        try:
                            return [
                                item
                                for item in stock_device
                                if isinstance(item, StockBrokenDeviceData)
                            ]

                        except AttributeError:
                            return f"Не найдено не одного прибора в ремонте за эту дату {at_clean_date}"

                    case _:
                        date = modificate_date_to_str()
                        where_mogrif_data = {
                            TableRow("sd.at_clean_date"): RowValue(date),
                        }
                        stock_device = interface.get_items(where_data=where_mogrif_data)

                        try:
                            return [
                                item
                                for item in stock_device
                                if isinstance(item, StockBrokenDeviceData)
                            ]

                        except AttributeError:
                            return f"Не найден не один прибор за эту дату {date}"
        else:
            raise Exception("Не верно указана база данных")

    def bot_lst_device(self) -> List[Dict[str, str]] | str:
        """метод для получения всего списка приборов"""

        if self.db_name:
            with DBSqlite(self.db_name) as conn:
                interface = DatabaseTableHandlerInterface(conn)
                interface.schema = OutputDeviceTable
                device = interface.get_items()

                try:
                    return [item.model_dump() for item in device]

                except AttributeError:
                    return "Не найдены приборы"

        else:
            raise Exception("Не верно указана база данных")

    def bot_lst_company(self) -> List[Dict[str, str]] | str:
        """метод для получения всех компаний производителей"""

        if self.db_name:
            with DBSqlite(self.db_name) as conn:
                interface = DatabaseTableHandlerInterface(conn)
                interface.schema = OutputDeviceCompanyTable
                company = interface.get_items()

                try:
                    return [item.model_dump() for item in company]

                except AttributeError:
                    return "Не найден прибор"

        else:
            raise Exception("Не верно указана база данных")

    def bot_lst_device_type(self) -> List[Dict[str, str]]:
        """метод получения всех типов приборов"""

        if self.db_name:
            with DBSqlite(self.db_name) as conn:
                interface = DatabaseTableHandlerInterface(conn)
                interface.schema = OutputDeviceTypeTable
                device_type = interface.get_items()
                return [item.model_dump() for item in device_type]

        else:
            raise Exception("Не верно указана база данных")

    def bot_device_id(self, device_name: str | None) -> str:
        """метод для получения id прибора"""

        if device_name:
            where_data = {TableRow("device_name"): RowValue(device_name)}

            if self.db_name:
                with DBSqlite(self.db_name) as conn:
                    interface = DatabaseTableHandlerInterface(conn)
                    interface.schema = OutputDeviceTable
                    device = interface.get_item(where_data=where_data)

                    if isinstance(device, OutputDeviceTable):
                        return str(device.device_id)

                    else:
                        return f"В списке приборов по имени {device_name} не чего не нашлось"

            else:
                raise Exception("Не верно указана база данных")

        else:
            raise Exception("Не переданы аргументы")

    def bot_company_id(self, company_name: str | None) -> str:
        """метод для получения id компании производителя"""

        if company_name:
            where_data = {TableRow("company_name"): RowValue(company_name)}

            if self.db_name:
                with DBSqlite(self.db_name) as conn:
                    interface = DatabaseTableHandlerInterface(conn)
                    interface.schema = OutputDeviceCompanyTable
                    company = interface.get_item(where_data=where_data)

                    if isinstance(company, OutputDeviceCompanyTable):
                        return str(company.company_id)
                    else:
                        return f"В списке компаний по имени {company_name} не чего не найдено"

            else:
                raise Exception("Не верно указана база данных")

        else:
            raise Exception("Не переданы аргументы")

    def bot_type_id(self, type_title: str | None) -> str:
        """метод для получения всех типов приборов по названию типа"""

        if type_title:
            where_data = {TableRow("type_title"): RowValue(type_title)}

            if self.db_name:
                with DBSqlite(self.db_name) as conn:
                    interface = DatabaseTableHandlerInterface(conn)
                    interface.schema = OutputDeviceTypeTable
                    device_type = interface.get_item(where_data=where_data)

                    if isinstance(device_type, OutputDeviceTypeTable):
                        return str(device_type.type_device_id)
                    else:
                        return f"В списке типов по названию {type_title} не чего не найдено"

            else:
                raise Exception("Не верно указана база данных")

        else:
            raise Exception("Не переданы аргументы")

    def bot_check_device_from_stockpile(self, where_data: Dict[str, str]) -> bool:
        """метод проверки наличия прибора на складе"""

        check = False
        match where_data:
            case {
                "stock_device_id": str(stock_device_id),
                "device_name": str(device_name),
            }:
                where_mogrif_data = {
                    TableRow("stock_device_id"): RowValue(stock_device_id),
                    TableRow("device_name"): RowValue(device_name),
                }

                if self.db_name:
                    with DBSqlite(self.db_name) as conn:
                        interface = DatabaseTableHandlerInterface(conn)
                        interface.schema = StockDeviceData
                        stock_device = interface.get_item(where_data=where_mogrif_data)

                        if isinstance(stock_device, StockDeviceData):
                            check = True

                else:
                    raise Exception("Не верно указана база данных")

            case _:
                raise Exception(f"Данные {where_data} не прошли валидацию")

        return check

    def bot_check_device(self, device_name: str | None) -> bool:
        """метод проверки наличия прибора в базе"""

        check = False

        if device_name:
            where_data = {TableRow("device_name"): RowValue(device_name)}

            if self.db_name:
                with DBSqlite(self.db_name) as conn:
                    interface = DatabaseTableHandlerInterface(conn)
                    interface.schema = OutputDeviceTable
                    device = interface.get_item(where_data=where_data)

                    if isinstance(device, OutputDeviceTable):
                        check = True

            else:
                raise Exception("Не верно указана база данных")

        else:
            raise Exception("Не переданы аргументы")

        return check

    def bot_check_company(self, company_name: str | None) -> bool:
        """метод проверки наличия компании в базе"""

        if company_name:
            where_data = {TableRow("company_name"): RowValue(company_name)}

            if self.db_name:
                with DBSqlite(self.db_name) as conn:
                    interface = DatabaseTableHandlerInterface(conn)
                    interface.schema = OutputDeviceCompanyTable
                    company = interface.get_item(where_data=where_data)

                    if isinstance(company, OutputDeviceCompanyTable):
                        return True
                    else:
                        return False

            else:
                raise Exception("Не верно указана база данных")

        else:
            raise Exception("Не переданы аргументы")

    def bot_check_type(self, type_title: str | None) -> bool:
        """метод проверки наличия типа устройства в списке"""

        if type_title:
            where_data = {TableRow("type_title"): RowValue(type_title)}

            if self.db_name:
                with DBSqlite(self.db_name) as conn:
                    interface = DatabaseTableHandlerInterface(conn)
                    interface.schema = OutputDeviceTypeTable
                    device_type = interface.get_item(where_data=where_data)

                    if isinstance(device_type, OutputDeviceTypeTable):
                        return True
                    else:
                        return False

            else:
                raise Exception("Не верно указана база данных")

        else:
            raise Exception("Не переданы аргументы")

    def bot_change_device_status(self, where_data: Dict[str, str]) -> str | None:
        """метод смены статуса прибора"""

        if self.db_name:
            with DBSqlite(self.db_name) as conn:
                interface = DatabaseTableHandlerInterface(conn)
                interface.schema = StockDeviceTableStatus

                match where_data:
                    case {
                        "stock_device_id": str(stock_device_id),
                        "device_name": str(device_name),
                        "mark": "0" as mark,
                    }:
                        device_id = self.bot_device_id(device_name)
                        if device_id:
                            set_data = {
                                TableRow("stock_device_status"): RowValue(mark),
                                TableRow("at_clean_date"): RowValue(
                                    modificate_date_to_str()
                                ),
                            }
                            where_mogrif_data = {
                                TableRow("stock_device_id"): RowValue(stock_device_id),
                                TableRow("device_id"): RowValue(device_id),
                            }

                            interface.change_device_status(
                                set_data=set_data, where_data=where_mogrif_data
                            )

                    case {
                        "stock_device_id": str(stock_device_id),
                        "device_name": str(device_name),
                        "mark": "1" as mark,
                    }:
                        device_id = self.bot_device_id(device_name)
                        if device_id:
                            set_data = {
                                TableRow("sd.stock_device_status"): RowValue(mark),
                                TableRow("sd.at_clean_date"): RowValue(
                                    modificate_date_to_str()
                                ),
                            }
                            where_mogrif_data = {
                                TableRow("sd.stock_device_id"): RowValue(
                                    stock_device_id
                                ),
                                TableRow("sd.device_id"): RowValue(device_id),
                            }

                            interface.change_device_status(
                                set_data=set_data, where_data=where_mogrif_data
                            )

                    case _:
                        return f"Переданные данные {where_data} не прошли валидацию"

        else:
            raise Exception("Не верно указана база данных")

    def bot_set_device_from_stockpile_by_name_and_id_to_db(
        self, set_data: Dict[str, str]
    ) -> str:
        """метод добавления данных о приборе со склада в базу"""

        match set_data:
            case {
                "stock_device_id": str(stock_device_id),
                "device_name": str(device_name),
            }:
                date = modificate_date_to_str()
                device_id = self.bot_device_id(device_name)
                if device_id:
                    item = (stock_device_id, device_id, date)
                    if self.db_name:
                        with DBSqlite(self.db_name) as conn:
                            interface = DatabaseTableHandlerInterface(conn)
                            interface.schema = StockDeviceTable
                            interface.set_item(item)
                            return f"Прибор с именем {device_name} с id {stock_device_id} добавлен в базу данных"

                    else:
                        raise Exception("Не верно указана база данных")

                else:
                    return (
                        f"Прибора с именем - {device_name} не существует в базе данных"
                    )

            case _:
                return f"Данные - {set_data} не прошли валидацию"

    def bot_set_device_type(self, set_data: Dict[str, str]) -> str:
        """метод добавляет тип прибора в базу данных"""

        match set_data:
            case {
                "type_title": str(type_title),
                "type_description": str(type_description),
            }:
                item = (type_title, type_description)
                if self.db_name:
                    with DBSqlite(self.db_name) as conn:
                        interface = DatabaseTableHandlerInterface(conn)
                        interface.schema = DeviceTypeTable
                        interface.set_item(item)
                        return f"Тип прибора с названием {type_title} добавлен в бд"

                else:
                    raise Exception("Не верно указана база данных")

            case _:
                return f"Данные - {set_data} не прошли валидацию"

    def bot_set_device_company(self, set_data: Dict[str, str]) -> str:
        """метод добавляет информацию о компании в базу данных"""

        match set_data:
            case {
                "company_name": str(company_name),
                "producer_country": str(producer_coutry),
                "description_company": str(description_company),
            }:
                item = (company_name, producer_coutry, description_company)
                if self.db_name:
                    with DBSqlite(self.db_name) as conn:
                        interface = DatabaseTableHandlerInterface(conn)
                        interface.schema = DeviceCompanyTable
                        interface.set_item(item)
                        return f"Компания с названием {company_name} добавлена в базу"

                else:
                    raise Exception("Не верно указана база данных")

            case _:
                return f"Данные - {set_data} не прошли валидацию"

    def bot_set_device(self, set_data: Dict[str, str]) -> str:
        """метод добавлеяет информацию о приборе в бд"""

        match set_data:
            case {
                "device_name": str(device_name),
                "company_name": str(company_name),
                "type_title": str(type_title),
            }:
                company_id = self.bot_company_id(company_name)
                type_device_id = self.bot_type_id(type_title)
                item = (device_name, company_id, type_device_id)

                if self.db_name:
                    with DBSqlite(self.db_name) as conn:
                        interface = DatabaseTableHandlerInterface(conn)
                        interface.schema = DeviceTable
                        interface.set_item(item)
                        return f"Прибор с именем {device_name} добавлен в базу"

                else:
                    raise Exception("Не верно указана база данных")

            case _:
                return f"Данные - {set_data} не прошли валидацию"

    def bot_update_devices_stock_clearence_date(
        self, set_data: Dict[str, str], date: str | None = None
    ) -> str:
        if self.db_name:
            with DBSqlite(self.db_name) as conn:
                interface = DatabaseTableHandlerInterface(conn)
                interface.schema = StockDeviceTable

                match set_data:
                    case {
                        "stock_device_id": str(stock_device_id),
                        "device_name": str(device_name),
                    }:
                        device_id = self.bot_device_id(device_name)
                        if device_id:
                            where_data = {
                                TableRow("stock_device_id"): RowValue(stock_device_id),
                                TableRow("device_id"): RowValue(device_id),
                            }

                            if isinstance(date, str) and validate_date(date):
                                set_mogrif_data = {
                                    TableRow("at_clean_date"): RowValue(date)
                                }
                                interface.update_item(
                                    set_data=set_mogrif_data, where_data=where_data
                                )
                                return f"Данные прибора - {device_name} обновлены"

                            else:
                                date = modificate_date_to_str()
                                set_mogrif_data = {
                                    TableRow("at_clean_date"): RowValue(date)
                                }

                                interface.update_item(
                                    set_data=set_mogrif_data, where_data=where_data
                                )
                                return f"Данные прибора - {device_name} обновлены"
                        else:
                            logger.warning(f"Прибор {device_name} не найден")
                            return f"Прибор {device_name} не найден"

                    case _:
                        logger.warning(f"Данные - {set_data} не прошли валидацию")
                        return f"Данные - {set_data} не прошли валидацию"

        else:
            raise Exception("Не верно указана база данных")

    def bot_keyboard_company_name_lst(self) -> List[str] | str:
        if self.db_name:
            with DBSqlite(self.db_name) as conn:
                interface = DatabaseTableHandlerInterface(conn)
                interface.schema = OutputDeviceCompanyTable
                company = interface.get_items()

                try:
                    return [
                        item.company_name
                        for item in company
                        if isinstance(item, OutputDeviceCompanyTable)
                    ]

                except AttributeError:
                    logger.warning("Список компаний пуст")
                    return "/add_company"

        else:
            raise Exception("Не верно указана база данных")

    def bot_keyboard_device_type_lst(self) -> List[str] | str:
        if self.db_name:
            with DBSqlite(self.db_name) as conn:
                interface = DatabaseTableHandlerInterface(conn)
                interface.schema = OutputDeviceTypeTable
                device_type = interface.get_items()
                try:
                    return [
                        item.type_title
                        for item in device_type
                        if isinstance(item, OutputDeviceTypeTable)
                    ]

                except AttributeError:
                    logger.warning("Список типов пуст")
                    return "/add_device_type"

        else:
            raise Exception("Не верно указана база данных")

    def bot_keyboard_device_lst(self) -> List[str] | str:
        if self.db_name:
            with DBSqlite(self.db_name) as conn:
                interface = DatabaseTableHandlerInterface(conn)
                interface.schema = OutputDeviceTable
                device = interface.get_items()

                try:
                    return [
                        item.device_name
                        for item in device
                        if isinstance(item, OutputDeviceTable)
                    ]

                except AttributeError:
                    logger.warning("Не найдены приборы")
                    return "/add_device"

        else:
            raise Exception("Не верно указана база данных")

    def bot_inline_kb(self, marker: Marker) -> InlineKeyboardMarkup:
        kb_builder = InlineKeyboardBuilder()
        kb_builder.button(text="/cancel", callback_data="/cancel")

        match marker:
            case Marker.DCOMPANY:
                [
                    kb_builder.button(
                        text=item,
                        callback_data=DeviceCompanyCallback(
                            text_search=item, company_name=item
                        ),
                    )
                    for item in self.bot_keyboard_company_name_lst()
                ]

            case Marker.DTYPE:
                [
                    kb_builder.button(
                        text=item,
                        callback_data=DeviceTypeCallback(
                            text_search=item, type_title=item
                        ),
                    )
                    for item in self.bot_keyboard_device_type_lst()
                ]
            case Marker.DEVICE:
                [
                    kb_builder.button(
                        text=item,
                        callback_data=DeviceCallback(
                            text_search=item, device_name=item
                        ),
                    )
                    for item in self.bot_keyboard_device_lst()
                ]
            case Marker.GET_DEVICE:
                [
                    kb_builder.button(
                        text=item,
                        callback_data=DeviceCallback(
                            text_search=f"get_{item}", device_name=item
                        ),
                    )
                    for item in self.bot_keyboard_device_lst()
                ]
            case Marker.MARKING_DEVICES:
                [
                    kb_builder.button(
                        text=item,
                        callback_data=DeviceCallback(
                            text_search=f"mark_{item}", device_name=item
                        ),
                    )
                    for item in self.bot_keyboard_device_lst()
                ]

        kb_builder.adjust(3)
        return kb_builder.as_markup()
