"""
Модуль для инициализации бота
"""

from abc import ABC, abstractmethod
from enum import StrEnum
import logging
import os
from typing import Dict, Generic, List, Tuple
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


from src.scheme_for_validation import (
    DataForQuery,
    Lamp,
    OutputDeviceCompanyTable,
    OutputDeviceTable,
    OutputDeviceTypeTable,
    RowValue,
    StockBrokenDeviceData,
    StockDeviceData,
    TableRow,
)
from src.secret import secrets
from src.utils import modificate_date_to_str, validate_date
from src.database_interface import DataBaseInterface, Table
from src.query_scheme import (
    QuerySchemeForDeviceType,
    QuerySchemeForDevice,
    QuerySchemeForStockDevice,
    QuerySchemeForDeviceCompany,
    TableScheme,
)


logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


class TokenError(Exception): ...


class BotHandlerException(Exception):
    def __init__(self, *args: object) -> None:
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self) -> str:
        return f"BotHandlerException, {0}".format(self.message)


class APIBotDbException(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        return "APIBotDbException, {0}".format(self.message)


class Marker(StrEnum):
    DCOMPANY = "device_company"
    DTYPE = "device_type"
    DEVICE = "device"
    GET_DEVICE = "get_device"
    MARKING_DEVICES = "marking_devices"
    LAMP = "lamp_type"
    DEVICE_FIL = "device_fil"
    REPLACEMENT_LAMP = "replacement_lamp"


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


class DeviceFILCallback(CallbackData, prefix="device_fill"):
    text_search: str
    fil_device: str


class DeviceTypeCallback(CallbackData, prefix="device_type"):
    text_search: str
    type_title: str


class DeviceCompanyCallback(CallbackData, prefix="device_company"):
    text_search: str
    company_name: str


class DeviceCallback(CallbackData, prefix="device"):
    text_search: str
    device_name: str


class LampTypeCallback(CallbackData, prefix="lamp_type"):
    text_search: str
    lamp_type: str


class AbstractAPIBotDb(Generic[Table, TableScheme], ABC):
    @abstractmethod
    def bot_replacement_lamp(self, where_data: Dict[str, str]) -> str: ...

    @abstractmethod
    def bot_keyboard_device_lst_from_fil(self) -> List[str] | None: ...

    @abstractmethod
    def bot_lst_device_by_type_lamp_fil(self) -> List[OutputDeviceTable] | None: ...

    @abstractmethod
    def bot_lamp_hour_calculate(
        self, where_data: Dict[str, str]
    ) -> Tuple[str, bool]: ...

    @abstractmethod
    def bot_options_to_add_or_update(self, where_data: Dict[str, str]) -> str: ...

    @abstractmethod
    def is_LED_lamp_type_by_device_name(self, device_name: str) -> bool | str: ...

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
    ) -> StockDeviceData | str: ...

    @abstractmethod
    def bot_device(self, device_name: str | None) -> OutputDeviceTable | str: ...

    @abstractmethod
    def bot_company(self, company_name: str) -> OutputDeviceCompanyTable | str: ...

    @abstractmethod
    def bot_device_type(self, type_title: str) -> OutputDeviceTypeTable | str: ...

    @abstractmethod
    def bot_lst_broken_device_from_stockpile(
        self, where_data: Dict[str, str] | None = None
    ) -> List[StockBrokenDeviceData] | str: ...

    @abstractmethod
    def bot_lst_device(self) -> List[OutputDeviceTable] | str: ...

    @abstractmethod
    def bot_lst_company(self) -> List[OutputDeviceCompanyTable] | str: ...

    @abstractmethod
    def bot_lst_device_type(self) -> List[OutputDeviceTypeTable] | str: ...

    @abstractmethod
    def bot_device_id(self, device_name: str | None) -> str: ...

    @abstractmethod
    def bot_company_id(self, company_name: str | None) -> str: ...

    @abstractmethod
    def bot_type_id(self, type_title: str | None) -> str: ...

    @abstractmethod
    def is_availability_device_from_stockpile(
        self, where_data: Dict[str, str]
    ) -> bool: ...

    @abstractmethod
    def is_availability_device(self, device_name: str | None) -> bool: ...

    @abstractmethod
    def is_availability_company(self, company_name: str | None) -> bool: ...

    @abstractmethod
    def is_availability_type(self, type_title: str | None) -> bool: ...

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
        self, where_data: Dict[str, str], date: str | None = None
    ) -> str: ...

    @abstractmethod
    def bot_get_devices_at_date(
        self, where_data: Dict[str, str]
    ) -> List[StockBrokenDeviceData] | str: ...

    @abstractmethod
    def database_get_items(
        self,
        query: TableScheme,
        where_data: DataForQuery | List[DataForQuery] | None = None,
    ) -> List[Table] | None: ...

    @abstractmethod
    def database_get_item(
        self,
        query: TableScheme,
        where_data: DataForQuery | List[DataForQuery] | None = None,
    ) -> Table | None: ...

    @abstractmethod
    def database_set_item(self, query: TableScheme, set_data: tuple): ...

    @abstractmethod
    def database_update_item(
        self,
        query: TableScheme,
        set_data: DataForQuery | List[DataForQuery],
        where_data: DataForQuery | List[DataForQuery],
    ): ...


class APIBotDb(AbstractAPIBotDb):
    def __init__(self, db_name: str) -> None:
        self.db_name = db_name

    def database_update_item(
        self,
        query,
        set_data,
        where_data,
    ):
        """метод обновляющий данные в базе"""

        query = query.query_update(set_data=set_data, where_data=where_data)

        with DataBaseInterface(db_name=self.db_name) as conn:
            cursor = conn.row_factory_for_connection(query[1])
            conn.update(query=query[0], cursor=cursor)

    def database_set_item(self, query, set_data):
        query = query.query_set()

        with DataBaseInterface(db_name=self.db_name) as conn:
            cursor = conn.row_factory_for_connection(query[1])
            conn.set(query=query[0], set_data=set_data, cursor=cursor)

    def database_get_items(self, query, where_data=None):
        if where_data:
            query = query.query_get(where_data=where_data)

        else:
            query = query.query_get()

        with DataBaseInterface(db_name=self.db_name) as conn:
            cursor = conn.row_factory_for_connection(query[1])
            return conn.get_all(query=query[0], cursor=cursor)

    def database_get_item(self, query, where_data=None):
        if where_data:
            query = query.query_get(where_data=where_data)

        else:
            query = query.query_get()

        with DataBaseInterface(db_name=self.db_name) as conn:
            cursor = conn.row_factory_for_connection(query[1])
            return conn.get(query=query[0], cursor=cursor)

    def bot_get_devices_at_date(self, where_data):
        with DataBaseInterface(db_name=self.db_name) as conn:
            if validate_date(where_data["at_clean_date"]):
                where_mogrif_data = DataForQuery(
                    prefix="sd",
                    table_row=TableRow("at_clean_date"),
                    row_value=RowValue(where_data["at_clean_date"]),
                )
                query = QuerySchemeForStockDevice().query_get_search_with_device(
                    where_data=where_mogrif_data
                )
                cursor = conn.row_factory_for_connection(query[1])
                stock_devices = conn.get_all(query=query[0], cursor=cursor)

                if stock_devices and all(
                    isinstance(item, StockBrokenDeviceData) for item in stock_devices
                ):
                    return stock_devices

                else:
                    return "Нет приборов в эту дату"

            else:
                where_mogrif_data = DataForQuery(
                    prefix="sd",
                    table_row=TableRow("at_clean_date"),
                    row_value=RowValue(modificate_date_to_str()),
                )
                query = QuerySchemeForStockDevice().query_get_search_with_device(
                    where_data=where_mogrif_data
                )
                cursor = conn.row_factory_for_connection(query[1])
                stock_devices = conn.get_all(query=query[0], cursor=cursor)

                if stock_devices and all(
                    isinstance(item, StockBrokenDeviceData) for item in stock_devices
                ):
                    return stock_devices

                else:
                    return "Нет приборов в эту дату"

    def bot_device_from_stockpile(self, where_data):
        """метод для получение прибора со склада по id и названию"""

        query = QuerySchemeForStockDevice()

        match where_data:
            case {
                "stock_device_id": str(stock_device_id),
                "device_name": str(device_name),
            }:
                row_stock_device_id = DataForQuery(
                    prefix="sd",
                    table_row=TableRow("stock_device_id"),
                    row_value=RowValue(stock_device_id),
                )
                row_device_name = DataForQuery(
                    prefix="d",
                    table_row=TableRow("device_name"),
                    row_value=RowValue(device_name),
                )
                where_mogrif_data = [row_stock_device_id, row_device_name]
                stock_device = self.database_get_item(
                    where_data=where_mogrif_data, query=query
                )

                if isinstance(stock_device, StockDeviceData):
                    return stock_device

                else:
                    return f"Прибор с id {stock_device_id} и названием {device_name} не найден в базе"

            case _:
                return f"Данные {where_data} не прошли валидацию"

    def bot_device(self, device_name):
        """метод для получения прибора по имени"""

        query = QuerySchemeForDevice()

        if device_name:
            where_data = {TableRow("device_name"): RowValue(device_name)}
            where_data = DataForQuery(
                prefix="d",
                table_row=TableRow("device_name"),
                row_value=RowValue(device_name),
            )
            device = self.database_get_item(where_data=where_data, query=query)

            if isinstance(device, OutputDeviceTable):
                return device

            else:
                return f"Прибор с названием {device_name} не найден в базе"

        else:
            raise APIBotDbException("Не переданы аргументы")

    def bot_company(self, company_name):
        """метод для получения данных о компании производителе"""

        query = QuerySchemeForDeviceCompany()

        if company_name:
            where_data = DataForQuery(
                prefix="dc",
                table_row=TableRow("company_name"),
                row_value=RowValue(company_name),
            )
            company = self.database_get_item(where_data=where_data, query=query)

            if isinstance(company, OutputDeviceCompanyTable):
                return company

            else:
                return f"Компания с названием {company_name} не найден в базе"

        else:
            raise APIBotDbException("Не переданы аргументы")

    def bot_device_type(self, type_title):
        """метод для получения данных о типе прибора"""

        query = QuerySchemeForDeviceType()

        if type_title:
            where_data = DataForQuery(
                prefix="dt",
                table_row=TableRow("type_title"),
                row_value=RowValue(type_title),
            )
            device_type = self.database_get_item(where_data=where_data, query=query)

            if isinstance(device_type, OutputDeviceTypeTable):
                return device_type

            else:
                return f"Тип прибор с названием {type_title} не найден в базе"

        else:
            raise APIBotDbException("Не переданы аргументы")

    def bot_lst_broken_device_from_stockpile(self, where_data=None):
        """метод для получения всех приборов со склада"""

        with DataBaseInterface(db_name=self.db_name) as conn:
            if where_data and validate_date(where_data["at_clean_date"]):
                row_at_clean_date = DataForQuery(
                    prefix="sd",
                    table_row=TableRow("at_clean_date"),
                    row_value=RowValue(where_data["at_clean_date"]),
                )
                row_status_0 = DataForQuery(
                    prefix="sd",
                    table_row=TableRow("stock_device_status"),
                    row_value=RowValue("0"),
                )
                where_mogrif_data = [row_at_clean_date, row_status_0]

                query = QuerySchemeForStockDevice().query_get_search_with_device(
                    where_data=where_mogrif_data
                )
                cursor = conn.row_factory_for_connection(query[1])
                stock_devices = conn.get_all(query=query[0], cursor=cursor)

                if stock_devices and all(
                    isinstance(item, StockBrokenDeviceData) for item in stock_devices
                ):
                    return stock_devices

                else:
                    return f"Не найдено не одного прибора в ремонте за эту дату {where_data['at_clean_date']}"

            else:
                date = modificate_date_to_str()
                row_at_clean_date = DataForQuery(
                    prefix="sd",
                    table_row=TableRow("at_clean_date"),
                    row_value=RowValue(date),
                )
                row_status_0 = DataForQuery(
                    prefix="sd",
                    table_row=TableRow("stock_device_status"),
                    row_value=RowValue("0"),
                )
                where_mogrif_data = [row_at_clean_date, row_status_0]
                query = QuerySchemeForStockDevice().query_get_search_with_device(
                    where_data=where_mogrif_data
                )
                cursor = conn.row_factory_for_connection(query[1])
                stock_devices = conn.get_all(query=query[0], cursor=cursor)

                if stock_devices and all(
                    isinstance(item, StockBrokenDeviceData) for item in stock_devices
                ):
                    return stock_devices

                else:
                    return f"Не найдено не одного прибора в ремонте за эту дату {date}"

    def bot_lst_device(self):
        """метод для получения всего списка приборов"""

        query = QuerySchemeForDevice()
        devices = self.database_get_items(query=query)

        if devices and all(isinstance(item, OutputDeviceTable) for item in devices):
            return devices

        else:
            return "Приборы не найдены"

    def bot_lst_company(self):
        """метод для получения всех компаний производителей"""

        query = QuerySchemeForDeviceCompany()
        companys = self.database_get_items(query=query)

        if companys and all(
            isinstance(item, OutputDeviceCompanyTable) for item in companys
        ):
            return companys

        else:
            return "Производитель не найден"

    def bot_lst_device_type(self):
        """метод получения всех типов приборов"""

        query = QuerySchemeForDeviceType()
        device_types = self.database_get_items(query=query)

        if device_types and all(
            isinstance(item, OutputDeviceTypeTable) for item in device_types
        ):
            return device_types

        else:
            return "Типы приборов не найдены"

    def bot_device_id(self, device_name):
        """метод для получения id прибора"""

        query = QuerySchemeForDevice()

        if device_name:
            where_data = DataForQuery(
                prefix="d",
                table_row=TableRow("device_name"),
                row_value=RowValue(device_name),
            )
            device = self.database_get_item(where_data=where_data, query=query)

            if isinstance(device, OutputDeviceTable):
                return str(device.device_id)

            else:
                return f"В списке приборов по имени {device_name} не чего не нашлось"

        else:
            raise APIBotDbException("Не переданы аргументы")

    def bot_company_id(self, company_name):
        """метод для получения id компании производителя"""

        query = QuerySchemeForDeviceCompany()

        if company_name:
            where_data = DataForQuery(
                prefix="dc",
                table_row=TableRow("company_name"),
                row_value=RowValue(company_name),
            )
            company = self.database_get_item(where_data=where_data, query=query)

            if isinstance(company, OutputDeviceCompanyTable):
                return str(company.company_id)

            else:
                return f"В списке компаний по имени {company_name} не чего не найдено"

        else:
            raise APIBotDbException("Не переданы аргументы")

    def bot_type_id(self, type_title):
        """метод для получения всех типов приборов по названию типа"""

        query = QuerySchemeForDeviceType()

        if type_title:
            where_data = DataForQuery(
                prefix="dt",
                table_row=TableRow("type_title"),
                row_value=RowValue(type_title),
            )
            device_type = self.database_get_item(where_data=where_data, query=query)

            if isinstance(device_type, OutputDeviceTypeTable):
                return str(device_type.type_device_id)

            else:
                return f"В списке типов по названию {type_title} не чего не найдено"

        else:
            raise APIBotDbException("Не переданы аргументы")

    def is_availability_device_from_stockpile(self, where_data):
        """метод проверки наличия прибора на складе"""

        check = False
        query = QuerySchemeForStockDevice()

        match where_data:
            case {
                "stock_device_id": str(stock_device_id),
                "device_name": str(device_name),
            }:
                row_stock_device_id = DataForQuery(
                    prefix="sd",
                    table_row=TableRow("stock_device_id"),
                    row_value=RowValue(stock_device_id),
                )
                row_device_name = DataForQuery(
                    prefix="d",
                    table_row=TableRow("device_name"),
                    row_value=RowValue(device_name),
                )
                where_mogrif_data = [row_stock_device_id, row_device_name]
                stock_device = self.database_get_item(
                    where_data=where_mogrif_data, query=query
                )

                if isinstance(stock_device, StockDeviceData):
                    check = True

            case _:
                raise APIBotDbException(f"Данные {where_data} не прошли валидацию")

        return check

    def is_availability_device(self, device_name):
        """метод проверки наличия прибора в базе"""

        check = False
        query = QuerySchemeForDevice()

        if device_name:
            where_data = DataForQuery(
                prefix="d",
                table_row=TableRow("device_name"),
                row_value=RowValue(device_name),
            )
            device = self.database_get_item(where_data=where_data, query=query)

            if isinstance(device, OutputDeviceTable):
                check = True

        else:
            raise APIBotDbException("Не переданы аргументы")

        return check

    def is_availability_company(self, company_name):
        """метод проверки наличия компании в базе"""

        check = False
        query = QuerySchemeForDeviceCompany()

        if company_name:
            where_data = DataForQuery(
                prefix="dc",
                table_row=TableRow("company_name"),
                row_value=RowValue(company_name),
            )
            company = self.database_get_item(where_data=where_data, query=query)

            if isinstance(company, OutputDeviceCompanyTable):
                check = True

        else:
            raise APIBotDbException("Не переданы аргументы")

        return check

    def is_availability_type(self, type_title):
        """метод проверки наличия типа устройства в списке"""

        check = False
        query = QuerySchemeForDeviceType()

        if type_title:
            where_data = DataForQuery(
                prefix="dt",
                table_row=TableRow("type_title"),
                row_value=RowValue(type_title),
            )
            device_type = self.database_get_item(where_data=where_data, query=query)

            if isinstance(device_type, OutputDeviceTypeTable):
                check = True

        else:
            raise APIBotDbException("Не переданы аргументы")

        return check

    def bot_options_to_add_or_update(self, where_data) -> Lamp | str:
        match where_data:
            case {
                "stock_device_id": str(),
                "device_name": str(device_name),
            }:
                if self.is_availability_device_from_stockpile(where_data):
                    result_job = self.bot_update_devices_stock_clearence_date(
                        where_data
                    )
                    logger.warning(result_job)
                    return "update"

                elif self.is_availability_device(device_name=device_name):
                    lamp_type = self.is_LED_lamp_type_by_device_name(device_name)

                    if lamp_type:
                        result_job = (
                            self.bot_set_device_from_stockpile_by_name_and_id_to_db(
                                where_data
                            )
                        )
                        logger.warning(result_job)
                        return "LED"

                    else:
                        return "FIL"

                else:
                    return f"В базе отсутсвуют записи о приборе {device_name}"

            case _:
                return "Данные не прошли валидацию"

    def is_LED_lamp_type_by_device_name(self, device_name) -> bool | str:
        """метод возвращает тип лампы"""

        led = False
        device = self.bot_device(device_name=device_name)

        if isinstance(device, OutputDeviceTable):
            device_type = self.bot_device_type(device.type_title)

            if (
                isinstance(device_type, OutputDeviceTypeTable)
                and device_type.lamp_type == "LED"
            ):
                print(device_type.lamp_type)
                led = True

        return led

    def bot_set_device_from_stockpile_by_name_and_id_to_db(self, set_data):
        """метод добавления данных о приборе со склада в базу"""

        query = QuerySchemeForStockDevice()

        match set_data:
            case {
                "stock_device_id": str(stock_device_id),
                "device_name": str(device_name),
                "max_lamp_hours": str(max_lamp_hours),
            }:
                date = modificate_date_to_str()
                device_id = self.bot_device_id(device_name)

                if device_id:
                    item = (stock_device_id, device_id, max_lamp_hours, date)
                    self.database_set_item(set_data=item, query=query)
                    return f"Прибор с именем {device_name} с id {stock_device_id} и часами лампы {max_lamp_hours} добавлен в базу данных"

                else:
                    return (
                        f"Прибора с именем - {device_name} не существует в базе данных"
                    )

            case {
                "stock_device_id": str(stock_device_id),
                "device_name": str(device_name),
            }:
                date = modificate_date_to_str()
                device_id = self.bot_device_id(device_name)

                if device_id:
                    item = (stock_device_id, device_id, 0, date)
                    self.database_set_item(set_data=item, query=query)
                    return f"Прибор с именем {device_name} с id {stock_device_id} добавлен в базу данных"

                else:
                    return (
                        f"Прибора с именем - {device_name} не существует в базе данных"
                    )

            case _:
                return f"Данные - {set_data} не прошли валидацию"

    def bot_set_device_type(self, set_data):
        """метод добавляет тип прибора в базу данных"""

        query = QuerySchemeForDeviceType()

        match set_data:
            case {
                "type_title": str(type_title),
                "type_description": str(type_description),
                "lamp_type": str(lamp_type),
            }:
                item = (type_title, type_description, lamp_type)
                self.database_set_item(set_data=item, query=query)
                return f"Тип прибора с названием {type_title} добавлен в бд"

            case _:
                return f"Данные - {set_data} не прошли валидацию"

    def bot_set_device_company(self, set_data):
        """метод добавляет информацию о компании в базу данных"""

        query = QuerySchemeForDeviceCompany()

        match set_data:
            case {
                "company_name": str(company_name),
                "producer_country": str(producer_coutry),
                "description_company": str(description_company),
            }:
                item = (company_name, producer_coutry, description_company)
                self.database_set_item(set_data=item, query=query)
                return f"Компания с названием {company_name} добавлена в базу"

            case _:
                return f"Данные - {set_data} не прошли валидацию"

    def bot_set_device(self, set_data):
        """метод добавлеяет информацию о приборе в бд"""

        query = QuerySchemeForDevice()

        match set_data:
            case {
                "device_name": str(device_name),
                "company_name": str(company_name),
                "type_title": str(type_title),
            }:
                company_id = self.bot_company_id(company_name)
                type_device_id = self.bot_type_id(type_title)
                item = (device_name, company_id, type_device_id)
                self.database_set_item(set_data=item, query=query)
                return f"Прибор с именем {device_name} добавлен в базу"

            case _:
                return f"Данные - {set_data} не прошли валидацию"

    def bot_lamp_hour_calculate(self, where_data: Dict[str, str]) -> Tuple[str, bool]:
        """метод вычисляет отработанные часы у лампы"""

        its_time_for_change = False

        match where_data:
            case {
                "stock_device_id": str(stock_device_id),
                "device_name": str(device_name),
                "current_hours": str(current_hours),
            }:
                stock_device = self.bot_device_from_stockpile(where_data=where_data)

                if stock_device and isinstance(stock_device, StockDeviceData):
                    max_hour = stock_device.max_lamp_hours

                    try:
                        current_hours = int(current_hours)

                        if current_hours >= max_hour:
                            its_time_for_change = True
                            return (
                                f"Лампу пора менять. Максимальный ресурс лампы {max_hour}",
                                its_time_for_change,
                            )

                        elif current_hours < max_hour:
                            its_time_for_change = True
                            hour_calculate = max_hour - current_hours
                            return (
                                f"Оставшийся ресурс лампы {hour_calculate}",
                                its_time_for_change,
                            )

                        else:
                            return "Лампа новая", its_time_for_change

                    except ValueError:
                        return (
                            f"{current_hours} введено не верно. Должно быть число",
                            its_time_for_change,
                        )

                    except BotHandlerException as err:
                        raise err

                else:
                    return (
                        f"Нет приборов с именем {device_name} и id {stock_device_id} в базе",
                        its_time_for_change,
                    )

            case _:
                return (
                    f"Данные в bot_lamp_hour_calculate {where_data} не прошли валидацию",
                    its_time_for_change,
                )

    def bot_replacement_lamp(self, where_data: Dict[str, str]) -> str:
        """метод замены лампы в приборе"""

        match where_data:
            case {
                "stock_device_id": str(stock_device_id),
                "device_name": str(device_name),
                "max_lamp_hours": str(max_lamp_hours),
            }:
                device_id = self.bot_device_id(device_name)

                if device_id:
                    query = QuerySchemeForStockDevice()
                    row_stock_device_id = DataForQuery(
                        prefix="sd",
                        table_row=TableRow("stock_device_id"),
                        row_value=RowValue(stock_device_id),
                    )
                    row_device_id = DataForQuery(
                        prefix="d",
                        table_row=TableRow("device_id"),
                        row_value=RowValue(device_id),
                    )
                    where_mogrif_data = [row_stock_device_id, row_device_id]
                    set_data = DataForQuery(
                        prefix="sd",
                        table_row=TableRow("max_lamp_hours"),
                        row_value=RowValue(max_lamp_hours),
                    )

                    try:
                        self.database_update_item(
                            query=query, set_data=set_data, where_data=where_mogrif_data
                        )
                        return f"Лампа для прибора {device_name} c id {stock_device_id} удачно заменена"

                    except BotHandlerException:
                        return f"{BotHandlerException('Ошибка замены лампы в приборе')}"

                else:
                    return f"Прибор {device_name} не найден в базе"

            case _:
                return f"Данные {where_data} не прошли валидацию"

    def bot_change_device_status(self, where_data):
        """метод смены статуса прибора"""

        match where_data:
            case {
                "stock_device_id": str(stock_device_id),
                "device_name": str(device_name),
                "mark": "0" as mark,
            }:
                where_check_stock_device_id = {
                    "stock_device_id": stock_device_id,
                    "device_name": device_name,
                }

                if self.is_availability_device_from_stockpile(
                    where_check_stock_device_id
                ):
                    device_id = self.bot_device_id(device_name)

                    if device_id:
                        row_stock_device_status = DataForQuery(
                            prefix="sd",
                            table_row=TableRow("stock_device_status"),
                            row_value=RowValue(mark),
                        )
                        row_at_clean_date = DataForQuery(
                            prefix="sd",
                            table_row=TableRow("at_clean_date"),
                            row_value=RowValue(modificate_date_to_str()),
                        )
                        row_stock_device_id = DataForQuery(
                            prefix="sd",
                            table_row=TableRow("stock_device_id"),
                            row_value=RowValue(stock_device_id),
                        )
                        row_device_id = DataForQuery(
                            prefix="sd",
                            table_row=TableRow("device_id"),
                            row_value=RowValue(device_id),
                        )
                        set_data = [row_stock_device_status, row_at_clean_date]
                        where_mogrif_data = [row_stock_device_id, row_device_id]
                        query = QuerySchemeForStockDevice()
                        self.database_update_item(
                            query=query, set_data=set_data, where_data=where_mogrif_data
                        )
                        logger.warning(
                            f"Прибор {device_name} с id {stock_device_id} добавлен в ремонт"
                        )

                    else:
                        return f"Прибора с таким названием {device_name} нет в базе"

                else:
                    return f"Прибора с таким id {stock_device_id} нет на складе"

            case {
                "stock_device_id": str(stock_device_id),
                "device_name": str(device_name),
                "mark": "1" as mark,
            }:
                where_check_stock_device_id = {
                    "stock_device_id": stock_device_id,
                    "device_name": device_name,
                }

                if self.is_availability_device_from_stockpile(
                    where_check_stock_device_id
                ):
                    device_id = self.bot_device_id(device_name)

                    if device_id:
                        row_stock_device_status = DataForQuery(
                            prefix="sd",
                            table_row=TableRow("stock_device_status"),
                            row_value=RowValue(mark),
                        )
                        row_at_clean_date = DataForQuery(
                            prefix="sd",
                            table_row=TableRow("at_clean_date"),
                            row_value=RowValue(modificate_date_to_str()),
                        )
                        row_stock_device_id = DataForQuery(
                            prefix="sd",
                            table_row=TableRow("stock_device_id"),
                            row_value=RowValue(stock_device_id),
                        )
                        row_device_id = DataForQuery(
                            prefix="sd",
                            table_row=TableRow("device_id"),
                            row_value=RowValue(device_id),
                        )
                        where_mogrif_data = [row_stock_device_id, row_device_id]
                        set_data = [row_stock_device_status, row_at_clean_date]

                        query = QuerySchemeForStockDevice()
                        self.database_update_item(
                            query=query, set_data=set_data, where_data=where_mogrif_data
                        )

                    else:
                        return f"Прибора с таким названием {device_name} нет в базе"

                else:
                    return f"Прибора с таким id {stock_device_id} нет на складе"

            case _:
                return f"Переданные данные {where_data} не прошли валидацию"

    def bot_update_devices_stock_clearence_date(self, where_data, date=None):
        match where_data:
            case {
                "stock_device_id": str(stock_device_id),
                "device_name": str(device_name),
            }:
                device_id = self.bot_device_id(device_name)

                if device_id:
                    row_stock_device_id = DataForQuery(
                        prefix="sd",
                        table_row=TableRow("stock_device_id"),
                        row_value=RowValue(stock_device_id),
                    )
                    row_device_id = DataForQuery(
                        prefix="sd",
                        table_row=TableRow("device_id"),
                        row_value=RowValue(device_id),
                    )
                    where_mogrif_data = [row_stock_device_id, row_device_id]

                    if isinstance(date, str) and validate_date(date):
                        set_mogrif_data = DataForQuery(
                            table_row=TableRow("at_clean_date"),
                            row_value=RowValue(date),
                        )
                        query = QuerySchemeForStockDevice()
                        self.database_update_item(
                            query=query,
                            set_data=set_mogrif_data,
                            where_data=where_mogrif_data,
                        )
                        return f"Данные прибора - {device_name} обновлены"

                    else:
                        date = modificate_date_to_str()
                        set_mogrif_data = DataForQuery(
                            table_row=TableRow("at_clean_date"),
                            row_value=RowValue(date),
                        )
                        query = QuerySchemeForStockDevice()
                        self.database_update_item(
                            query=query,
                            set_data=set_mogrif_data,
                            where_data=where_mogrif_data,
                        )
                        return f"Данные прибора - {device_name} обновлены"

                else:
                    return f"Прибор {device_name} не найден"

            case _:
                return f"Данные - {where_data} не прошли валидацию"

    def bot_keyboard_company_name_lst(self):
        companys = self.bot_lst_company()

        return [
            item.company_name
            for item in companys
            if isinstance(item, OutputDeviceCompanyTable)
        ]

    def bot_keyboard_device_type_lst(self):
        device_type = self.bot_lst_device_type()

        return [
            item.type_title
            for item in device_type
            if isinstance(item, OutputDeviceTypeTable)
        ]

    def bot_keyboard_device_lst(self):
        device = self.bot_lst_device()

        return [
            item.device_name for item in device if isinstance(item, OutputDeviceTable)
        ]

    def bot_lst_device_by_type_lamp_fil(self):
        """возвращаем приборы по типу лампа накаливания"""

        where_data = DataForQuery(
            prefix="dt", table_row=TableRow("lamp_type"), row_value=RowValue("FIL")
        )
        query = QuerySchemeForDevice()
        devices = self.database_get_items(query=query, where_data=where_data)

        if devices and all(isinstance(item, OutputDeviceTable) for item in devices):
            return [item for item in devices]

        else:
            logger.warning("Не найдены приборы с лампой накаливания")

    def bot_keyboard_device_lst_from_fil(self):
        devices = self.bot_lst_device_by_type_lamp_fil()

        if isinstance(devices, list):
            return [
                item.device_name
                for item in devices
                if isinstance(item, OutputDeviceTable)
            ]

        else:
            raise BotHandlerException("Нет данных для клавиатуры")

    def bot_inline_kb(self, marker):
        kb_builder = InlineKeyboardBuilder()
        kb_builder.button(text="/cancel", callback_data="/cancel")

        match marker:
            case Marker.DEVICE_FIL:
                [
                    kb_builder.button(
                        text=item,
                        callback_data=DeviceFILCallback(
                            text_search="fil_" + item, fil_device=item
                        ),
                    )
                    for item in self.bot_keyboard_device_lst_from_fil()
                ]

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

            case Marker.LAMP:
                [
                    kb_builder.button(
                        text=item,
                        callback_data=LampTypeCallback(
                            text_search=item, lamp_type=item
                        ),
                    )
                    for item in ["LED", "FIL"]
                ]

            case Marker.REPLACEMENT_LAMP:
                [
                    kb_builder.button(
                        text=item,
                        callback_data=DeviceFILCallback(
                            text_search="replace_" + item, fil_device=item
                        ),
                    )
                    for item in self.bot_keyboard_device_lst_from_fil()
                ]

        kb_builder.adjust(3)
        return kb_builder.as_markup()


def run_api() -> APIBotDb:
    db_name = ""
    if os.environ.get("DB_NAME"):
        db_name = os.environ["DB_NAME"]
    else:
        db_name = "clean_device.db"

    api = APIBotDb(db_name=db_name)

    return api
