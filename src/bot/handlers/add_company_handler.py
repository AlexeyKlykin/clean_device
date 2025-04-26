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


device_company_router = Router()


class AddDeviceCompany(StatesGroup):
    company_name = State()
    producer_country = State()
    description_company = State()


db_bot_api = DBotAPI()


@device_company_router.message(F.text == "/add_device_company")
async def add_device_company_name(message: Message, state: FSMContext):
    await message.answer(
        "Введите название компании", reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AddDeviceCompany.company_name)


@device_company_router.message(AddDeviceCompany.company_name)
async def add_producer_country(message: Message, state: FSMContext):
    await state.update_data(company_name=message.text)
    await message.answer("Введите название страны производителя")
    await state.set_state(AddDeviceCompany.producer_country)


@device_company_router.message(AddDeviceCompany.producer_country)
async def add_description_company(message: Message, state: FSMContext):
    await state.update_data(producer_country=message.text)
    await message.answer("Введите описание или адрес сайта")
    await state.set_state(AddDeviceCompany.description_company)


@device_company_router.message(AddDeviceCompany.description_company)
async def add_device_company(message: Message, state: FSMContext):
    await state.update_data(description_company=message.text)

    data = await state.get_data()

    try:
        db_bot_api.save_company_from_bot_into_db(data)
        await message.answer(f"Данные {data} записаны", reply_markup=kb_start)

    except Exception as err:
        logger.warning(err)
        await message.answer(f"Данные {data} не записаны", reply_markup=kb_start)

    await state.clear()
