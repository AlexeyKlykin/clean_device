import logging
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.run_bot import DBotAPI
from src.bot.keyboard.keyboard_start import kb_start

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


get_stock_device_router = Router()

bot_api_db = DBotAPI()


class GetStockDevice(StatesGroup):
    stock_device_id = State()
    stock_device_name = State()


@get_stock_device_router.message(F.text == "/get_stock_device")
async def send_stock_device_id(message: Message, state: FSMContext):
    await message.answer(text="Введите номер устройства со склада")
    await state.set_state(GetStockDevice.stock_device_id)


@get_stock_device_router.message(GetStockDevice.stock_device_id)
async def send_stock_device_name(message: Message, state: FSMContext):
    await state.update_data(stock_device_id=message.text)
    await message.answer(text="Введите название устройства")
    await state.set_state(GetStockDevice.stock_device_name)


@get_stock_device_router.message(GetStockDevice.stock_device_name)
async def get_stock_device(message: Message, state: FSMContext):
    await state.update_data(stock_device_name=message.text)
    device_data = await state.get_data()
    stock_device = bot_api_db.get_stock_device_id(
        device_data["stock_device_id"], device_data["stock_device_name"]
    )
    await message.answer(
        text=f"""Id прибора: {stock_device["stock_device_id"]}
Название прибора: {stock_device["device_name"]}
Компания производитель прибора: {stock_device["company_name"]}
Тип прибора: {stock_device["type_title"]}
Дата последней очистки: {stock_device["at_clean_date"]}""",
        reply_markup=kb_start,
    )
