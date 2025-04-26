import logging
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.types import ReplyKeyboardRemove

from src.bot.keyboard.keyboard_start import kb_start
from src.run_bot import (
    CompanyCallback,
    DBotAPI,
    DeviceCallback,
    DeviceTypeCallback,
    StockDeviceCallback,
)

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


stock_device_router = Router()


class AddStockDevice(StatesGroup):
    stock_device_id = State()
    device_id = State()


bot_api_db = DBotAPI()


# активировали хранилище прибора на складе
@stock_device_router.message(F.text == "/add_stock_device")
async def start_stock_device(message: Message):
    await message.answer(
        text="Добавить чистый прибор/обновить текущий",
        reply_markup=ReplyKeyboardRemove(),
    )
