import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.types import ReplyKeyboardRemove

from src.bot.keyboard.keyboard_start import kb_start, kb_add, kb_get
from src.bot_api import (
    DeviceFILCallback,
    run_api,
    Marker,
)
from src.bot.states import SourceLampState, ReplacementLamp
from src.data_handler import BotHandlerException
from src.message_handler import MessageDescription

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


bot_api_db = run_api()

lamp_router = Router()


@lamp_router.message(F.text == "/replacement_lamp")
async def start_replacement_lamp(message: Message, state: FSMContext):
    mes_des = MessageDescription(message.text)
    await message.answer(text=mes_des.description(), reply_markup=ReplyKeyboardRemove())
    await state.set_state(ReplacementLamp.stock_device_id)


@lamp_router.message(ReplacementLamp.stock_device_id)
async def stock_device_id_from_lamp(message: Message, state: FSMContext):
    await state.update_data(stock_device_id=message.text)
    mes_des = MessageDescription("stock_device_id_from_lamp")
    await message.reply(
        text=mes_des.description(),
        reply_markup=bot_api_db.bot_inline_kb(Marker.REPLACEMENT_LAMP),
    )


@lamp_router.callback_query(
    DeviceFILCallback.filter(F.text_search.contains("replace_"))
)
async def device_name_from_lamp(
    callback: CallbackQuery, callback_data: DeviceFILCallback, state: FSMContext
):
    await callback.answer()
    data = await state.get_data()
    data["device_name"] = callback_data.fil_device
    mes_des = MessageDescription("device_name_from_lamp")

    if callback.message:
        if bot_api_db.is_availability_device_from_stockpile(data):
            await callback.message.answer(text=mes_des.description())
            await state.set_data(data)
            await state.set_state(ReplacementLamp.max_lamp_hours)

        else:
            await callback.message.answer(
                text=f"<b>Нет прибора с такими данными</b> <code>{data}</code>",
                reply_markup=kb_add,
            )
            await state.clear()


@lamp_router.message(ReplacementLamp.max_lamp_hours)
async def max_lamp_hours(message: Message, state: FSMContext):
    await state.update_data(max_lamp_hours=message.text)
    data = await state.get_data()
    mes_des = MessageDescription("max_lamp_hours")

    try:
        message_result = bot_api_db.bot_replacement_lamp(data)
        mes_des.message_data = message_result
        await message.answer(text=mes_des.description(), reply_markup=kb_add)

    except BotHandlerException:
        logger.warning(BotHandlerException("Ошибка в замене лампы"))
        await message.answer(text=mes_des.description(), reply_markup=kb_start)

    finally:
        await state.clear()


@lamp_router.message(F.text == "/check_lamp_hours")
async def start_check_lamp_hours(message: Message, state: FSMContext):
    mes_des = MessageDescription(message.text)
    await message.answer(text=mes_des.description())
    await state.set_state(SourceLampState.stock_device_id)


@lamp_router.message(SourceLampState.stock_device_id)
async def check_device_name(message: Message, state: FSMContext):
    await state.update_data(stock_device_id=message.text)
    mes_des = MessageDescription("check_device_name")
    await message.reply(
        text=mes_des.description(),
        reply_markup=bot_api_db.bot_inline_kb(Marker.DEVICE_FIL),
    )


@lamp_router.callback_query(DeviceFILCallback.filter(F.text_search.contains("fil_")))
async def check_device_FIL(
    callback: CallbackQuery, callback_data: DeviceFILCallback, state: FSMContext
):
    await callback.answer()
    data = await state.get_data()
    data["device_name"] = callback_data.fil_device
    mes_des = MessageDescription("check_device_FIL")
    if callback.message:
        if bot_api_db.is_availability_device_from_stockpile(data):
            await state.set_data(data)
            await callback.message.answer(text=mes_des.description())
            await state.set_state(SourceLampState.current_lamp_hours)

        else:
            mes_des = MessageDescription("device_FIL_none")
            mes_des.message_data = data
            await callback.message.answer(
                text=mes_des.description(),
                reply_markup=kb_get,
            )
            await state.clear()


@lamp_router.message(SourceLampState.current_lamp_hours)
async def check_lamp_hours(message: Message, state: FSMContext):
    await state.update_data(current_hours=message.text)
    data = await state.get_data()
    result = bot_api_db.bot_lamp_hour_calculate(data)
    mes_des = MessageDescription("check_lamp_hours")
    mes_des.message_data = result[0]

    if result[1]:
        await message.answer(text=mes_des.description(), reply_markup=kb_start)

    else:
        await message.answer(text=mes_des.description(), reply_markup=kb_get)

    await state.clear()
