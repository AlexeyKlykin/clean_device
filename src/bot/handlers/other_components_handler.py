import logging
from aiogram import Router, F
from aiogram.types import Message

from src.bot_api import run_api
from src.bot.keyboard.keyboard_start import kb_start
from src.schema_for_validation import (
    OutputDeviceCompanyTable,
    OutputDeviceTable,
    OutputDeviceTypeTable,
)

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


other_components_router = Router()


bot_api_db = run_api()


@other_components_router.message(F.text == "/get_devices")
async def get_devices(message: Message):
    devices = bot_api_db.bot_lst_device()

    if devices:
        await message.answer(
            text="\n".join(
                [
                    f"""Название модели прибора: <code>{item.device_name}</code>
Название компании производителя: <code>{item.company_name}</code>
Название типа прибора: <code>{item.type_title}</code>\n"""
                    for item in devices
                    if isinstance(item, OutputDeviceTable)
                ]
            ),
            reply_markup=kb_start,
        )

    else:
        await message.answer(text=f"<b>{devices}</b>", reply_markup=kb_start)


@other_components_router.message(F.text == "/get_companies")
async def get_companies(message: Message):
    companies = bot_api_db.bot_lst_company()

    if companies:
        await message.answer(
            text="\n".join(
                [
                    f"""Название компании: <code>{item.company_name}</code>
Страна производитель: <code>{item.producer_country}</code>
Сайт компании: <code>{item.description_company}</code>\n"""
                    for item in companies
                    if isinstance(item, OutputDeviceCompanyTable)
                ]
            ),
            reply_markup=kb_start,
        )
    else:
        await message.answer(text=f"<b>{companies}</b>", reply_markup=kb_start)


@other_components_router.message(F.text == "/get_types")
async def get_device_types(message: Message):
    device_types = bot_api_db.bot_lst_device_type()

    if device_types:
        await message.answer(
            text="\n".join(
                [
                    f"""Название типа прибора: <code>{item.type_title}</code>
Описание типа прибора: <code>{item.type_description:.150}</code>
Тип лампы: <code>{item.lamp_type}</code>"""
                    for item in device_types
                    if isinstance(item, OutputDeviceTypeTable)
                ]
            ),
            reply_markup=kb_start,
        )
    else:
        await message.answer(text=f"<b>{device_types}</b>", reply_markup=kb_start)
