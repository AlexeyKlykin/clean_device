import logging
import os
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.types import ReplyKeyboardRemove

from src.bot.handlers.add_company_handler import AddDeviceCompany
from src.bot.handlers.add_type_device_handler import AddDeviceType
from src.bot.keyboard.keyboard_start import kb_start
from src.bot.handlers.add_device_handler import AddDevice
from src.db_app import ApiTempJS
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

temp_stock_js = ApiTempJS("temp_stock_device.json")
temp_device_js = ApiTempJS("temp_device.json")


@stock_device_router.message(F.text == "/add_stock_device")
async def add_stock_device_id(message: Message, state: FSMContext):
    await message.answer(
        text="Введите номер прибора на складе",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(AddStockDevice.stock_device_id)


@stock_device_router.message(AddStockDevice.stock_device_id)
async def add_device_id_for_stock_device(message: Message, state: FSMContext):
    stock_device_id = message.text

    if bot_api_db.check_stock_device_id(stock_device_id):
        bot_api_db.update_stock_device(stock_device_id)
        await message.answer(
            text="Данные о приборе на складе обновлены", reply_markup=kb_start
        )
        await state.clear()

    else:
        await state.update_data(stock_device_id=stock_device_id)
        await message.answer(text="Введите название прибора")
        await state.set_state(AddStockDevice.device_name)


@stock_device_router.message(AddStockDevice.device_name)
async def add_stock_device(message: Message, state: FSMContext):
    device_name = message.text
    await state.update_data(device_name=device_name)
    stock_device_data = await state.get_data()

    if bot_api_db.check_device_id(device_name):
        bot_api_db.save_stock_device_into_db_from_bot(stock_device_data)
        await message.answer(
            text="Данные складского прибора сохранены в бд", reply_markup=kb_start
        )

    else:
        temp_stock_js.write(stock_device_data)

        await message.answer(
            text=f"Устройства нет в базе данных. Нужно добавить\n{device_name}.",
            reply_markup=bot_api_db.gen_inline_kb("device"),
        )

    await state.clear()


@stock_device_router.callback_query(F.data == "add_device")
async def add_device_name(message: Message, state: FSMContext):
    if os.path.exists("temp_stock_device.json"):
        device = temp_stock_js.read()
        if "device_name" in device.keys():
            device_name = device["device_name"]
            await state.set_data({"device_name": device_name})
            await message.answer(text="Введите название компании")
            await state.set_state(AddDevice.company_name)
        else:
            logger.warning("Ключа device_name не существует")
    else:
        logger.warning("temp_stock_device.json файла по этому пути не сущестует")


@stock_device_router.message(AddDevice.company_name)
async def add_company_name_for_device(message: Message, state: FSMContext):
    company_name = message.text
    await state.update_data(company_name=company_name)

    if bot_api_db.check_company_id(company_name):
        await message.answer(text="Введите название типа устройства")
        await state.set_state(AddDevice.type_title)

    else:
        device_data = await state.get_data()
        temp_device_js.write(device_data)

        await message.answer(
            text=f"Название компании {company_name} не найдено в базе данных",
            reply_markup=bot_api_db.gen_inline_kb("company"),
        )
        await state.clear()


@stock_device_router.message(AddDevice.type_title)
async def add_device(message: Message, state: FSMContext):
    type_title = message.text

    if bot_api_db.check_type_id(type_title):
        await state.update_data(type_title=type_title)
        device_data = await state.get_data()
        bot_api_db.save_device_from_bot_into_db(device_data)
        await message.answer(
            text="Данные прибора добавлены в бд", reply_markup=kb_start
        )
        temp_stock_js.clean()
        temp_device_js.clean()

    else:
        device_data = await state.get_data()
        temp_device_js.write(device_data)

        await message.answer(
            text=f"Названия типа прибора {type_title} не найдено в бд",
            reply_markup=bot_api_db.gen_inline_kb("device_type"),
        )

    await state.clear()


@stock_device_router.callback_query(F.data == "add_device_company")
async def add_company_name(message: Message, state: FSMContext):
    company = temp_device_js.read()
    if "company_name" in company.keys():
        await state.set_data({"company_name": company["company_name"]})
        await message.answer(text="Введите страну производства")
        await state.set_state(AddDeviceCompany.producer_country)


@stock_device_router.message(AddDeviceCompany.producer_country)
async def add_producer_country(message: Message, state: FSMContext):
    await state.update_data(producer_country=message.text)
    await message.answer(text="Введите адрес сайта или другие данные компании")
    await state.set_state(AddDeviceCompany.description_company)


@stock_device_router.message(AddDeviceCompany.description_company)
async def add_company(message: Message, state: FSMContext):
    await state.update_data(description_company=message.text)
    company_data = await state.get_data()
    bot_api_db.save_company_from_bot_into_db(company_data)
    await message.answer(text="Данные компании записаны", reply_markup=kb_start)
    temp_stock_js.clean()
    temp_device_js.clean()
    await state.clear()


@stock_device_router.callback_query(F.data == "add_device_type")
async def add_type_title(message: Message, state: FSMContext):
    device_type = temp_device_js.read()
    if "type_title" in device_type.keys():
        await state.set_data({"type_title": device_type["type_title"]})
        await message.answer(text="Введите описание типа")
        await state.set_state(AddDeviceType.description_type)

    else:
        await message.answer(text="Введите название типа")
        await state.set_state(AddDeviceType.type_title)


@stock_device_router.message(AddDeviceType.type_title)
async def add_description_type(message: Message, state: FSMContext):
    await state.update_data(type_title=message.text)
    await message.answer("Введите описание типа прибора")
    await state.set_state(AddDeviceType.description_type)


@stock_device_router.message(AddDeviceType.description_type)
async def add_device_type(message: Message, state: FSMContext):
    await state.update_data(description_type=message.text)
    type_data = await state.get_data()
    bot_api_db.save_device_type_from_bot_into_db(type_data)
    await message.answer(text="Данные типа прибора записаны", reply_markup=kb_start)
    temp_stock_js.clean()
    temp_device_js.clean()
    await state.clear()


@stock_device_router.callback_query(F.data == "cancel")
async def cancel(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    temp_stock_js.clean()
    temp_device_js.clean()
    await state.clear()
