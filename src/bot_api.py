"""
Модуль для инициализации бота
"""

import logging
import os
from enum import StrEnum
from typing import Dict, Generic, List, Tuple
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

from src.data_handler import DatabaseQueryHandler, BotHandlerException
from src.scheme_for_validation import (
    Lamp,
    MessageInput,
    OutputDeviceCompanyTable,
    OutputDeviceTable,
    OutputDeviceTypeTable,
    StockBrokenDeviceData,
    StockDeviceData,
)
from src.secret import secrets
from src.utils import modificate_date_to_str, validate_date
from src.database_interface import Table
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


class APIBotDb(Generic[Table, TableScheme]):
    def __init__(self, db_name: str) -> None:
        self.db_name = db_name

    def bot_device_from_stockpile(
        self, where_data: Dict[str, str]
    ) -> StockDeviceData | str:
        """метод для получение прибора со склада по id и названию"""

        api = DatabaseQueryHandler(self.db_name, QuerySchemeForStockDevice())

        match where_data:
            case {
                "stock_device_id": str(stock_device_id),
                "device_name": str(device_name),
            }:
                row_where = MessageInput(
                    {
                        ("sd", "stock_device_id"): stock_device_id,
                        ("d", "device_name"): device_name,
                    }
                )
                stock_device = api.database_get_item(extra_where_data=row_where)

                if isinstance(stock_device, StockDeviceData):
                    return stock_device

                else:
                    return f"Прибор с id {stock_device_id} и названием {device_name} не найден в базе"

            case _:
                return f"Данные {where_data} не прошли валидацию"

    def bot_device(self, device_name: str | None) -> OutputDeviceTable | str:
        """метод для получения прибора по имени"""

        api = DatabaseQueryHandler(self.db_name, QuerySchemeForDevice())

        if device_name:
            row_where = MessageInput({("d", "device_name"): device_name})
            device = api.database_get_item(extra_where_data=row_where)

            if isinstance(device, OutputDeviceTable):
                return device

            else:
                return f"Прибор с названием {device_name} не найден в базе"

        else:
            raise APIBotDbException("Не переданы аргументы")

    def bot_company(self, company_name: str | None) -> OutputDeviceCompanyTable | str:
        """метод для получения данных о компании производителе"""

        api = DatabaseQueryHandler(self.db_name, QuerySchemeForDeviceCompany())

        if company_name:
            row_where = MessageInput({("dc", "company_name"): company_name})
            company = api.database_get_item(extra_where_data=row_where)

            if isinstance(company, OutputDeviceCompanyTable):
                return company

            else:
                return f"Компания с названием {company_name} не найден в базе"

        else:
            raise APIBotDbException("Не переданы аргументы")

    def bot_device_type(self, type_title: str | None) -> OutputDeviceTypeTable | str:
        """метод для получения данных о типе прибора"""

        api = DatabaseQueryHandler(self.db_name, QuerySchemeForDeviceType())

        if type_title:
            row_where = MessageInput({("dt", "type_title"): type_title})
            device_type = api.database_get_item(extra_where_data=row_where)

            if isinstance(device_type, OutputDeviceTypeTable):
                return device_type

            else:
                return f"Тип прибор с названием {type_title} не найден в базе"

        else:
            raise APIBotDbException("Не переданы аргументы")

    def bot_lst_broken_device_from_stockpile(
        self, where_data: Dict[str, str] | None = None
    ) -> List[StockBrokenDeviceData] | str:
        """метод для получения всех приборов со склада"""

        api = DatabaseQueryHandler(self.db_name, QuerySchemeForStockDevice())

        if where_data and validate_date(where_data["at_clean_date"]):
            row_where = MessageInput(
                {
                    ("sd", "at_clean_date"): where_data["at_clean_date"],
                    ("sd", "stock_device_status"): "0",
                }
            )
            stock_devices = api.database_get_search_by_row(extra_where_data=row_where)

            if stock_devices:
                return stock_devices

            else:
                return f"Не найдено не одного прибора в ремонте за эту дату {where_data['at_clean_date']}"

        else:
            date = modificate_date_to_str()
            row_where = MessageInput(
                {
                    ("sd", "at_clean_date"): date,
                    ("sd", "stock_device_status"): "0",
                }
            )
            stock_devices = api.database_get_search_by_row(extra_where_data=row_where)

            if stock_devices:
                return stock_devices

            else:
                return f"Не найдено не одного прибора в ремонте за эту дату {date}"

    def bot_get_devices_at_date(
        self, where_data: Dict[str, str]
    ) -> List[StockBrokenDeviceData] | str:
        """метод получения чистых приборов по дате"""

        api = DatabaseQueryHandler(self.db_name, QuerySchemeForStockDevice())

        if validate_date(where_data["at_clean_date"]):
            row_where = MessageInput(
                {
                    ("sd", "at_clean_date"): where_data["at_clean_date"],
                    ("sd", "stock_device_status"): "1",
                }
            )
            stock_devices = api.database_get_search_by_row(row_where)

            if stock_devices:
                return stock_devices

            else:
                return "Нет приборов в эту дату"

        else:
            date = modificate_date_to_str()
            row_where = MessageInput(
                {
                    ("sd", "at_clean_date"): date,
                    ("sd", "stock_device_status"): "1",
                }
            )
            stock_devices = api.database_get_search_by_row(extra_where_data=row_where)

            if stock_devices and all(
                isinstance(item, StockBrokenDeviceData) for item in stock_devices
            ):
                return stock_devices

            else:
                return "Нет приборов в эту дату"

    def bot_lst_device(self) -> List[OutputDeviceTable] | str:
        """метод для получения всего списка приборов"""

        api = DatabaseQueryHandler(self.db_name, QuerySchemeForDevice())
        devices = api.database_get_items()

        if devices and all(isinstance(item, OutputDeviceTable) for item in devices):
            return [item for item in devices if isinstance(item, OutputDeviceTable)]

        else:
            return "Приборы не найдены"

    def bot_lst_company(self) -> List[OutputDeviceCompanyTable] | str:
        """метод для получения всех компаний производителей"""

        api = DatabaseQueryHandler(self.db_name, QuerySchemeForDeviceCompany())
        companys = api.database_get_items()

        if companys and all(
            isinstance(item, OutputDeviceCompanyTable) for item in companys
        ):
            return [
                item for item in companys if isinstance(item, OutputDeviceCompanyTable)
            ]

        else:
            return "Производитель не найден"

    def bot_lst_device_type(self) -> List[OutputDeviceTypeTable] | str:
        """метод получения всех типов приборов"""

        api = DatabaseQueryHandler(self.db_name, QuerySchemeForDeviceType())
        device_types = api.database_get_items()

        if device_types and all(
            isinstance(item, OutputDeviceTypeTable) for item in device_types
        ):
            return [
                item for item in device_types if isinstance(item, OutputDeviceTypeTable)
            ]

        else:
            return "Типы приборов не найдены"

    def bot_device_id(self, device_name: str | None) -> str:
        """метод для получения id прибора"""

        api = DatabaseQueryHandler(self.db_name, QuerySchemeForDevice())

        if device_name:
            row_where = MessageInput({("d", "device_name"): device_name})
            device = api.database_get_item(extra_where_data=row_where)

            if isinstance(device, OutputDeviceTable):
                return str(device.device_id)

            else:
                return f"В списке приборов по имени {device_name} не чего не нашлось"

        else:
            raise APIBotDbException("Не переданы аргументы")

    def bot_company_id(self, company_name: str | None) -> str:
        """метод для получения id компании производителя"""

        api = DatabaseQueryHandler(self.db_name, QuerySchemeForDeviceCompany())

        if company_name:
            row_where = MessageInput({("dc", "company_name"): company_name})
            company = api.database_get_item(extra_where_data=row_where)

            if isinstance(company, OutputDeviceCompanyTable):
                return str(company.company_id)

            else:
                return f"В списке компаний по имени {company_name} не чего не найдено"

        else:
            raise APIBotDbException("Не переданы аргументы")

    def bot_type_id(self, type_title: str | None) -> str:
        """метод для получения всех типов приборов по названию типа"""

        api = DatabaseQueryHandler(self.db_name, QuerySchemeForDeviceType())

        if type_title:
            row_where = MessageInput({("dt", "type_title"): type_title})
            device_type = api.database_get_item(extra_where_data=row_where)

            if isinstance(device_type, OutputDeviceTypeTable):
                return str(device_type.type_device_id)

            else:
                return f"В списке типов по названию {type_title} не чего не найдено"

        else:
            raise APIBotDbException("Не переданы аргументы")

    def is_availability_device_from_stockpile(self, where_data: Dict[str, str]) -> bool:
        """метод проверки наличия прибора на складе"""

        api = DatabaseQueryHandler(self.db_name, QuerySchemeForStockDevice())
        check = False

        match where_data:
            case {
                "stock_device_id": str(stock_device_id),
                "device_name": str(device_name),
            }:
                row_where = MessageInput(
                    {
                        ("sd", "stock_device_id"): stock_device_id,
                        ("d", "device_name"): device_name,
                    }
                )
                stock_device = api.database_get_item(extra_where_data=row_where)

                if isinstance(stock_device, StockDeviceData):
                    check = True

            case _:
                raise APIBotDbException(f"Данные {where_data} не прошли валидацию")

        return check

    def is_availability_device(self, device_name: str | None) -> bool:
        """метод проверки наличия прибора в базе"""

        api = DatabaseQueryHandler(self.db_name, QuerySchemeForDevice())
        check = False

        if device_name:
            row_where = MessageInput({("d", "device_name"): device_name})
            device = api.database_get_item(extra_where_data=row_where)

            if isinstance(device, OutputDeviceTable):
                check = True

        else:
            raise APIBotDbException("Не переданы аргументы")

        return check

    def is_availability_company(self, company_name: str | None) -> bool:
        """метод проверки наличия компании в базе"""

        api = DatabaseQueryHandler(self.db_name, QuerySchemeForDeviceCompany())
        check = False

        if company_name:
            row_where = MessageInput({("dc", "company_name"): company_name})
            company = api.database_get_item(extra_where_data=row_where)

            if isinstance(company, OutputDeviceCompanyTable):
                check = True

        else:
            raise APIBotDbException("Не переданы аргументы")

        return check

    def is_availability_type(self, type_title: str | None) -> bool:
        """метод проверки наличия типа устройства в списке"""

        api = DatabaseQueryHandler(self.db_name, QuerySchemeForDeviceType())
        check = False

        if type_title:
            row_where = MessageInput({("dt", "type_title"): type_title})
            device_type = api.database_get_item(extra_where_data=row_where)

            if isinstance(device_type, OutputDeviceTypeTable):
                check = True

        else:
            raise APIBotDbException("Не переданы аргументы")

        return check

    def bot_options_to_add_or_update(
        self, where_data: Dict[str, str]
    ) -> str | Tuple[Lamp | str, str]:
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
                    return "update", result_job

                elif self.is_availability_device(device_name=device_name):
                    lamp_type = self.is_LED_lamp_type_by_device_name(device_name)

                    if lamp_type:
                        result_job = (
                            self.bot_set_device_from_stockpile_by_name_and_id_to_db(
                                where_data
                            )
                        )
                        logger.warning(result_job)
                        return "LED", result_job

                    else:
                        return "FIL", str(where_data)

                else:
                    return f"В базе отсутсвуют записи о приборе {device_name}"

            case _:
                return "Данные не прошли валидацию"

    def is_LED_lamp_type_by_device_name(self, device_name: str) -> bool | str:
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

    def bot_set_device_from_stockpile_by_name_and_id_to_db(
        self, set_data: Dict[str, str]
    ) -> str:
        """метод добавления данных о приборе со склада в базу"""

        api = DatabaseQueryHandler(self.db_name, QuerySchemeForStockDevice())

        match set_data:
            case {
                "stock_device_id": str(stock_device_id),
                "device_name": str(device_name),
                "max_lamp_hours": str(max_lamp_hours),
            }:
                device_id = self.bot_device_id(device_name)

                if device_id:
                    item = (
                        stock_device_id,
                        device_id,
                        max_lamp_hours,
                        modificate_date_to_str(),
                    )
                    api.database_set_item(extra_set_data=item)
                    return f"Прибор с именем {device_name} с id {stock_device_id} и часами лампы {max_lamp_hours} добавлен в базу данных"

                else:
                    return (
                        f"Прибора с именем - {device_name} не существует в базе данных"
                    )

            case {
                "stock_device_id": str(stock_device_id),
                "device_name": str(device_name),
            }:
                device_id = self.bot_device_id(device_name)

                if device_id:
                    item = (stock_device_id, device_id, 0, modificate_date_to_str())
                    api.database_set_item(extra_set_data=item)
                    return f"Прибор с именем {device_name} с id {stock_device_id} добавлен в базу данных"

                else:
                    return (
                        f"Прибора с именем - {device_name} не существует в базе данных"
                    )

            case _:
                return f"Данные - {set_data} не прошли валидацию"

    def bot_set_device_type(self, set_data: Dict[str, str]) -> str:
        """метод добавляет тип прибора в базу данных"""

        api = DatabaseQueryHandler(self.db_name, QuerySchemeForDeviceType())

        match set_data:
            case {
                "type_title": str(type_title),
                "type_description": str(type_description),
                "lamp_type": str(lamp_type),
            }:
                item = (type_title, type_description, lamp_type)
                api.database_set_item(extra_set_data=item)
                return f"Тип прибора с названием {type_title} добавлен в бд"

            case _:
                return f"Данные - {set_data} не прошли валидацию"

    def bot_set_device_company(self, set_data: Dict[str, str]) -> str:
        """метод добавляет информацию о компании в базу данных"""

        api = DatabaseQueryHandler(self.db_name, QuerySchemeForDeviceCompany())

        match set_data:
            case {
                "company_name": str(company_name),
                "producer_country": str(producer_coutry),
                "description_company": str(description_company),
            }:
                item = (company_name, producer_coutry, description_company)
                api.database_set_item(extra_set_data=item)
                return f"Компания с названием {company_name} добавлена в базу"

            case _:
                return f"Данные - {set_data} не прошли валидацию"

    def bot_set_device(self, set_data: Dict[str, str]) -> str:
        """метод добавлеяет информацию о приборе в бд"""

        api = DatabaseQueryHandler(self.db_name, QuerySchemeForDevice())

        match set_data:
            case {
                "device_name": str(device_name),
                "company_name": str(company_name),
                "type_title": str(type_title),
            }:
                company_id = self.bot_company_id(company_name)
                type_device_id = self.bot_type_id(type_title)
                item = (device_name, company_id, type_device_id)
                api.database_set_item(extra_set_data=item)
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

        api = DatabaseQueryHandler(self.db_name, QuerySchemeForStockDevice())

        match where_data:
            case {
                "stock_device_id": str(stock_device_id),
                "device_name": str(device_name),
                "max_lamp_hours": str(max_lamp_hours),
            }:
                device_id = self.bot_device_id(device_name)

                if device_id:
                    row_where = MessageInput(
                        {
                            ("sd", "stock_device_id"): stock_device_id,
                            ("sd", "device_id"): device_id,
                        }
                    )
                    row_set = MessageInput({"max_lamp_hours": max_lamp_hours})

                    try:
                        api.database_update_item(
                            extra_set_data=row_set, extra_where_data=row_where
                        )
                        return f"Лампа для прибора {device_name} c id {stock_device_id} удачно заменена"

                    except BotHandlerException:
                        return f"{BotHandlerException('Ошибка замены лампы в приборе')}"

                else:
                    return f"Прибор {device_name} не найден в базе"

            case _:
                return f"Данные {where_data} не прошли валидацию"

    def bot_change_device_status(self, where_data: Dict[str, str]) -> str | None:
        """метод смены статуса прибора"""

        api = DatabaseQueryHandler(self.db_name, QuerySchemeForStockDevice())

        match where_data:
            case {
                "stock_device_id": str(stock_device_id),
                "device_name": str(device_name),
                "mark": str(mark),
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
                        row_set = MessageInput(
                            {
                                "stock_device_status": mark,
                                "at_clean_date": modificate_date_to_str(),
                            }
                        )
                        row_where = MessageInput(
                            {
                                ("sd", "stock_device_id"): stock_device_id,
                                ("sd", "device_id"): device_id,
                            }
                        )
                        api.database_update_item(
                            extra_set_data=row_set, extra_where_data=row_where
                        )
                        logger.warning(
                            f"Прибор {device_name} с id {stock_device_id} добавлен в ремонт"
                        )

                    else:
                        return f"Прибора с таким названием {device_name} нет в базе"

                else:
                    return f"Прибора с таким id {stock_device_id} нет на складе"

            case _:
                return f"Переданные данные {where_data} не прошли валидацию"

    def bot_update_devices_stock_clearence_date(
        self, where_data: Dict[str, str], date: str | None = None
    ) -> str:
        api = DatabaseQueryHandler(self.db_name, QuerySchemeForStockDevice())

        match where_data:
            case {
                "stock_device_id": str(stock_device_id),
                "device_name": str(device_name),
            }:
                device_id = self.bot_device_id(device_name)

                if device_id:
                    row_where = MessageInput(
                        {
                            ("sd", "stock_device_id"): stock_device_id,
                            ("sd", "device_id"): device_id,
                        }
                    )

                    if isinstance(date, str) and validate_date(date):
                        set_mogrif_data = MessageInput({"at_clean_date": date})
                        api.database_update_item(
                            extra_where_data=row_where,
                            extra_set_data=set_mogrif_data,
                        )
                        return f"Данные прибора - {device_name} обновлены"

                    else:
                        set_mogrif_data = MessageInput(
                            {"at_clean_date": modificate_date_to_str()}
                        )
                        api.database_update_item(
                            extra_set_data=set_mogrif_data, extra_where_data=row_where
                        )
                        return f"Данные прибора - {device_name} обновлены"

                else:
                    return f"Прибор {device_name} не найден"

            case _:
                return f"Данные - {where_data} не прошли валидацию"

    def bot_keyboard_company_name_lst(self) -> List[str]:
        companys = self.bot_lst_company()

        return [
            item.company_name
            for item in companys
            if isinstance(item, OutputDeviceCompanyTable)
        ]

    def bot_keyboard_device_type_lst(self) -> List[str]:
        device_type = self.bot_lst_device_type()

        return [
            item.type_title
            for item in device_type
            if isinstance(item, OutputDeviceTypeTable)
        ]

    def bot_keyboard_device_lst(self) -> List[str]:
        device = self.bot_lst_device()

        return [
            item.device_name for item in device if isinstance(item, OutputDeviceTable)
        ]

    def bot_lst_device_by_type_lamp_fil(self) -> List[OutputDeviceTable]:
        """возвращаем приборы по типу лампа накаливания"""

        where_data = MessageInput({("dt", "lamp_type"): "FIL"})
        api = DatabaseQueryHandler(self.db_name, QuerySchemeForDevice())
        devices = api.database_get_items(extra_where_data=where_data)

        if devices and all(isinstance(item, OutputDeviceTable) for item in devices):
            return [item for item in devices if isinstance(item, OutputDeviceTable)]

        else:
            raise BotHandlerException("Не найдены приборы с лампой накаливания")

    def bot_keyboard_device_lst_from_fil(self) -> List[str]:
        devices = self.bot_lst_device_by_type_lamp_fil()

        if isinstance(devices, list):
            return [
                item.device_name
                for item in devices
                if isinstance(item, OutputDeviceTable)
            ]

        else:
            raise BotHandlerException("Нет данных для клавиатуры")

    def bot_inline_kb(self, marker: Marker) -> InlineKeyboardMarkup:
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
