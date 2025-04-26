import logging
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.types import ReplyKeyboardRemove

from src.bot.keyboard.keyboard_start import kb_start
from src.run_bot import (
    DBotAPI,
)

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


device_router = Router()

bot_api_db = DBotAPI()


class AddDevice(StatesGroup):
    device_name = State()
    company_name = State()
    type_title = State()


@device_router.message(F.text == "/add_device")
async def add_device_name(message: Message, state: FSMContext):
    await message.answer(
        text="Введите название устройства", reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AddDevice.device_name)


@device_router.message(AddDevice.device_name)
async def add_company_id_for_device(message: Message, state: FSMContext):
    await state.update_data(device_name=message.text)
    await message.answer(text="Введите компанию производитель прибора")
    await state.set_state(AddDevice.company_name)


@device_router.message(AddDevice.company_name)
async def add_type_id_for_device(message: Message, state: FSMContext):
    await state.update_data(company_name=message.text)
    await message.answer(text="Введите название типа прибора")
    await state.set_state(AddDevice.type_title)


@device_router.message(AddDevice.type_title)
async def add_device(message: Message, state: FSMContext):
    await state.update_data(type_title=message.text)
    data = await state.get_data()
    bot_api_db.save_device_from_bot_into_db(data)
    await message.answer(text="Данные прибора записаны в бд", reply_markup=kb_start)
    await state.clear()
