import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.types import ReplyKeyboardRemove

from src.bot.keyboard.keyboard_start import kb_start, kb_add
from src.bot.states import AddDevice
from src.bot_api import (
    DeviceTypeCallback,
    DeviceCompanyCallback,
    run_api,
    Marker,
)
from src.data_handler import BotHandlerException
from src.message_handler import MessageDescription

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


device_router = Router()

bot_api_db = run_api()


companys_cache = set()
device_types_cache = set()


@device_router.message(F.text == "/add_device")
async def device(message: Message, state: FSMContext):
    mes_des = MessageDescription(message.text)
    await message.answer(text=mes_des.description(), reply_markup=ReplyKeyboardRemove())
    await state.set_state(AddDevice.device_name)
    companys_cache.update(bot_api_db.bot_keyboard_company_name_lst())
    device_types_cache.update(bot_api_db.bot_keyboard_device_type_lst())


@device_router.message(AddDevice.device_name)
async def device_name(message: Message, state: FSMContext):
    await state.update_data(device_name=message.text)
    mes_des = MessageDescription("device_name")
    await message.reply(
        text=mes_des.description(),
        reply_markup=bot_api_db.bot_inline_kb(Marker.DCOMPANY),
    )


@device_router.callback_query(
    DeviceCompanyCallback.filter(F.text_search.in_(companys_cache))
)
async def company_for_device(
    callback: CallbackQuery, callback_data: DeviceCompanyCallback, state: FSMContext
):
    await callback.answer()
    device_data = await state.get_data()
    device_data["company_name"] = callback_data.company_name
    await state.set_data(device_data)
    mes_des = MessageDescription("company_for_device")

    if callback.message:
        await callback.message.answer(
            text=mes_des.description(),
            reply_markup=bot_api_db.bot_inline_kb(Marker.DTYPE),
        )


@device_router.callback_query(
    DeviceTypeCallback.filter(F.text_search.in_(device_types_cache))
)
async def type_for_device(
    callback: CallbackQuery, callback_data: DeviceTypeCallback, state: FSMContext
):
    await callback.answer()
    device_data = await state.get_data()
    device_data["type_title"] = callback_data.type_title
    mes_des = MessageDescription("type_for_device")

    if callback.message:
        try:
            result_job = bot_api_db.bot_set_device(device_data)
            mes_des.message_data = result_job
            await callback.message.answer(
                text=mes_des.description(),
                reply_markup=kb_start,
            )

        except BotHandlerException:
            logger.warning(BotHandlerException())
            await callback.message.answer(
                text=mes_des.description(), reply_markup=kb_add
            )

        finally:
            await state.clear()
