import logging
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove

from src.bot.keyboard.keyboard_start import kb_start
from src.run_bot import DBotAPI

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
    device_name = State()


bot_api_db = DBotAPI()


@stock_device_router.message(F.text == "/add_stock_device")
async def add_stock_device_id(message: Message, state: FSMContext):
    await message.answer(
        text="Введите номер прибора на складе",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(AddStockDevice.stock_device_id)


@stock_device_router.message(AddStockDevice.stock_device_id)
async def add_device_id_for_stock_device(message: Message, state: FSMContext):
    await state.update_data(stock_device_id=message.text)
    await message.answer(text="Введите название прибора")
    await state.set_state(AddStockDevice.device_name)


@stock_device_router.message(AddStockDevice.device_name)
async def add_stock_device(message: Message, state: FSMContext):
    await state.update_data(device_name=message.text)
    stock_device_data = await state.get_data()
    stock_device_id = stock_device_data["stock_device_id"]
    device_name = stock_device_data["device_name"]

    if bot_api_db.check_stock_device(stock_device_id, device_name):
        bot_api_db.update_stock_device(stock_device_id, device_name)
        await message.answer(
            text=f"Данные прибора по {stock_device_id} обновленны",
            reply_markup=kb_start,
        )
    elif bot_api_db.check_device_id(device_name):
        bot_api_db.save_stock_device_into_db_from_bot(stock_device_data)
        await message.answer(
            text=f"Данные прибора по {stock_device_id} сохранены", reply_markup=kb_start
        )
    else:
        await message.answer(
            text=f"В базе отсутствет запись об {device_name}", reply_markup=kb_start
        )
    await state.clear()
