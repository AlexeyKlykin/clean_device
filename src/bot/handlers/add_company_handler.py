import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove

from src.bot.keyboard.keyboard_start import kb_start
from src.bot.states import AddDeviceCompany
from src.bot_api import run_api, BotHandlerException

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


device_company_router = Router()


db_bot_api = run_api()


@device_company_router.message(F.text == "/add_device_company")
async def add_device_company_name(message: Message, state: FSMContext):
    await message.answer(
        "<i>Введите название компании</i>", reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AddDeviceCompany.company_name)


@device_company_router.message(AddDeviceCompany.company_name)
async def add_producer_country(message: Message, state: FSMContext):
    await state.update_data(company_name=message.text)
    await message.answer("<i>Введите название страны производителя</i>")
    await state.set_state(AddDeviceCompany.producer_country)


@device_company_router.message(AddDeviceCompany.producer_country)
async def add_description_company(message: Message, state: FSMContext):
    await state.update_data(producer_country=message.text)
    await message.answer("<i>Введите описание или адрес сайта</i>")
    await state.set_state(AddDeviceCompany.description_company)


@device_company_router.message(AddDeviceCompany.description_company)
async def add_device_company(message: Message, state: FSMContext):
    await state.update_data(description_company=message.text)
    data = await state.get_data()

    try:
        result_job = db_bot_api.bot_set_device_company(data)
        await message.answer(f"<b>{result_job}</b>", reply_markup=kb_start)

    except BotHandlerException as err:
        logger.warning(err)

    finally:
        await state.clear()
