import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.types import ReplyKeyboardRemove

from src.bot.keyboard.keyboard_start import kb_start, kb_add
from src.bot_api import (
    BotHandlerException,
    DeviceFILCallback,
    run_api,
    Marker,
)
from src.bot.states import SourceLampState, ReplacementLamp

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
    await message.answer(
        text="<b>Введите номер прибора</b>", reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(ReplacementLamp.stock_device_id)


@lamp_router.message(ReplacementLamp.stock_device_id)
async def stock_device_id_from_lamp(message: Message, state: FSMContext):
    await state.update_data(stock_device_id=message.text)
    await message.answer(
        text="<b>Выберите имя прибора</b>",
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

    if callback.message:
        if bot_api_db.is_availability_device_from_stockpile(data):
            await callback.message.answer(text="<b>Введите числовой ресурс лампы</b>")
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

    try:
        message_result = bot_api_db.bot_replacement_lamp(data)
        await message.answer(text=f"<b>{message_result}</b>", reply_markup=kb_start)

    except BotHandlerException:
        logger.warning(BotHandlerException("Ошибка в замене лампы"))

    finally:
        await state.clear()


@lamp_router.message(F.text == "/check_lamp_hours")
async def start_check_lamp_hours(message: Message, state: FSMContext):
    await message.answer(text="<b>Старт проверки ресурса лампы. Введите id прибора</b>")
    await state.set_state(SourceLampState.stock_device_id)


@lamp_router.message(SourceLampState.stock_device_id)
async def check_device_name(message: Message, state: FSMContext):
    await state.update_data(stock_device_id=message.text)
    await message.answer(
        text="<b>Выберите название прибора</b>",
        reply_markup=bot_api_db.bot_inline_kb(Marker.DEVICE_FIL),
    )


@lamp_router.callback_query(DeviceFILCallback.filter(F.text_search.contains("fil_")))
async def check_device_FIL(
    callback: CallbackQuery, callback_data: DeviceFILCallback, state: FSMContext
):
    await callback.answer()
    data = await state.get_data()
    data["device_name"] = callback_data.fil_device
    if callback.message:
        if bot_api_db.is_availability_device_from_stockpile(data):
            await state.set_data(data)
            await callback.message.answer(
                text="<b>Введите текущее количество часов на приборе</b>"
            )
            await state.set_state(SourceLampState.current_lamp_hours)

        else:
            await callback.message.answer(
                text=f"<b>Данный прибор</b> <code>{data}</code> <b>не найден</b>",
                reply_markup=kb_start,
            )
            await state.clear()


@lamp_router.message(SourceLampState.current_lamp_hours)
async def check_lamp_hours(message: Message, state: FSMContext):
    await state.update_data(current_hours=message.text)
    data = await state.get_data()
    result = bot_api_db.bot_lamp_hour_calculate(data)
    await message.answer(text=f"{result[0]}", reply_markup=kb_start)
    await state.clear()
