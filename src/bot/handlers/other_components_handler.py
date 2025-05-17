import logging
from aiogram import Router, F
from aiogram.types import Message

from src.bot_api import run_api
from src.bot.keyboard.keyboard_start import kb_start
from src.message_handler import MessageDescription

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
    mes_des = MessageDescription(message.text)
    mes_des.message_data = devices

    if devices:
        await message.answer(
            text=mes_des.description(),
            reply_markup=kb_start,
        )

    else:
        await message.answer(text=f"<b>{devices}</b>", reply_markup=kb_start)


@other_components_router.message(F.text == "/get_companies")
async def get_companies(message: Message):
    companies = bot_api_db.bot_lst_company()
    mes_des = MessageDescription(message.text)
    mes_des.message_data = companies

    if companies:
        await message.answer(
            text=mes_des.description(),
            reply_markup=kb_start,
        )
    else:
        await message.answer(text=f"<b>{companies}</b>", reply_markup=kb_start)


@other_components_router.message(F.text == "/get_types")
async def get_device_types(message: Message):
    device_types = bot_api_db.bot_lst_device_type()
    mes_des = MessageDescription(message.text)
    mes_des.message_data = device_types

    if device_types:
        await message.answer(
            text=mes_des.description(),
            reply_markup=kb_start,
        )
    else:
        await message.answer(text=f"<b>{device_types}</b>", reply_markup=kb_start)
