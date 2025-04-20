"""
Модуль для инициализации бота
"""

import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode


from src.db_app import DBSqlite
from src.interface import DeviceCompanyInterface, DeviceInterface, StockDevicesInterface
from src.secret import secrets


logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


class TokenError(Exception): ...


# тест
def request_stock_device_interface() -> StockDevicesInterface:
    db_name = secrets["DB_NAME"]
    if isinstance(db_name, str):
        with DBSqlite(db_name) as conn:
            return StockDevicesInterface(conn)
    else:
        raise TypeError("Не передано название базы данных")


# тест
def request_device_interface() -> DeviceInterface:
    db_name = secrets["DB_NAME"]
    if isinstance(db_name, str):
        with DBSqlite(db_name) as conn:
            return DeviceInterface(conn)
    else:
        raise TypeError("Не передано название базы данных")


# тест
def request_company_interface() -> DeviceCompanyInterface:
    db_name = secrets["DB_NAME"]
    if isinstance(db_name, str):
        with DBSqlite(db_name) as conn:
            return DeviceCompanyInterface(conn)
    else:
        raise TypeError("Не передано название базы данных")


token = secrets["TOKEN"]

if token:
    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

else:
    raise TokenError("Ошибка подключения бота. Неверный токен")
