import logging
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.types import ReplyKeyboardRemove

from src.bot.keyboard.keyboard_start import kb_start, kb_add
from src.bot_api import (
    BotHandlerException,
    DeviceFILCallback,
    run_api,
    DeviceCallback,
    Marker,
)

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
    max_lamp_hours = State()


class SourceLamp(StatesGroup):
    stock_device_id = State()
    current_lamp_hours = State()


class ReplacementLamp(StatesGroup):
    stock_device_id = State()
    max_lamp_hours = State()


bot_api_db = run_api()

devices_cache = set()
device_fil_cache = set()
replacement_lamp_cache = set()


@stock_device_router.message(F.text == "/replacement_lamp")
async def start_replacement_lamp(message: Message, state: FSMContext):
    await message.answer(
        text="Введите номер прибора", reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(ReplacementLamp.stock_device_id)
    replacement_lamp_cache.update(
        ["replace_" + item for item in bot_api_db.bot_keyboard_device_lst_from_fil()]
    )


@stock_device_router.message(ReplacementLamp.stock_device_id)
async def stock_device_id_from_lamp(message: Message, state: FSMContext):
    await state.update_data(stock_device_id=message.text)
    await message.answer(
        text="Выберите имя прибора",
        reply_markup=bot_api_db.bot_inline_kb(Marker.REPLACEMENT_LAMP),
    )


@stock_device_router.callback_query(
    DeviceFILCallback.filter(F.text_search.in_(replacement_lamp_cache))
)
async def device_name_from_lamp(
    callback: CallbackQuery, callback_data: DeviceFILCallback, state: FSMContext
):
    await callback.answer()
    data = await state.get_data()
    data["device_name"] = callback_data.fil_device

    if callback.message:
        if bot_api_db.is_availability_device_from_stockpile(data):
            await callback.message.answer(text="Введите числовой ресурс лампы")
            await state.set_data(data)
            await state.set_state(ReplacementLamp.max_lamp_hours)

        else:
            await callback.message.answer(
                text=f"Нет прибора с такими данными {data}", reply_markup=kb_add
            )
            await state.clear()


@stock_device_router.message(ReplacementLamp.max_lamp_hours)
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


@stock_device_router.message(F.text == "/check_lamp_hours")
async def start_check_lamp_hours(message: Message, state: FSMContext):
    await message.answer(text="Старт проверки ресурса лампы. Введите id прибора")
    await state.set_state(SourceLamp.stock_device_id)
    device_fil_cache.update(
        "fil_" + item for item in bot_api_db.bot_keyboard_device_lst_from_fil()
    )


@stock_device_router.message(SourceLamp.stock_device_id)
async def check_device_name(message: Message, state: FSMContext):
    await state.update_data(stock_device_id=message.text)
    await message.answer(
        text="Выберите название прибора",
        reply_markup=bot_api_db.bot_inline_kb(Marker.DEVICE_FIL),
    )


@stock_device_router.callback_query(
    DeviceFILCallback.filter(F.text_search.in_(device_fil_cache))
)
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
                text="Введите текущее количество часов на приборе"
            )
            await state.set_state(SourceLamp.current_lamp_hours)

        else:
            await callback.message.answer(
                text=f"Данный прибор {data} не найден", reply_markup=kb_start
            )
            await state.clear()


@stock_device_router.message(SourceLamp.current_lamp_hours)
async def check_lamp_hours(message: Message, state: FSMContext):
    await state.update_data(current_hours=message.text)
    data = await state.get_data()
    result = bot_api_db.bot_lamp_hour_calculate(data)
    await message.answer(text=f"{result[0]}", reply_markup=kb_start)
    await state.clear()


@stock_device_router.message(F.text == "/add_stock_device")
async def add_stock_device_id(message: Message, state: FSMContext):
    await message.answer(
        text="<i>Введите номер прибора на складе</i>",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(AddStockDevice.stock_device_id)
    devices_cache.update(bot_api_db.bot_keyboard_device_lst())


@stock_device_router.message(AddStockDevice.stock_device_id)
async def add_device_id_for_stock_device(message: Message, state: FSMContext):
    await state.update_data(stock_device_id=message.text)
    await message.answer(
        text="<i>Введите название прибора</i>",
        reply_markup=bot_api_db.bot_inline_kb(Marker.DEVICE),
    )


@stock_device_router.callback_query(
    DeviceCallback.filter(F.text_search.in_(devices_cache))
)
async def add_stock_device(
    callback: CallbackQuery, callback_data: DeviceCallback, state: FSMContext
):
    await callback.answer()
    stock_device_data = await state.get_data()
    stock_device_data["device_name"] = callback_data.device_name

    if callback.message:
        try:
            result_job = bot_api_db.bot_options_to_add_or_update(stock_device_data)

            if result_job == "update":
                await callback.message.answer(
                    text=f"Данные обновленны <b>{result_job}</b>",
                    reply_markup=kb_start,
                )
                await state.clear()

            elif result_job == "LED":
                await callback.message.answer(
                    text=f"Данные добавленны <code>{result_job}</code>",
                    reply_markup=kb_start,
                )
                await state.clear()

            elif result_job == "FIL":
                await state.set_data(stock_device_data)

                if callback.message:
                    await callback.message.answer(
                        text="<b>У прибора лампа накаливания. Введите максимальное колличество часов</b>"
                    )
                await state.set_state(AddStockDevice.max_lamp_hours)

            else:
                await callback.message.answer(
                    text=f"В базе отсутствет запись <code>{stock_device_data}</code>",
                    reply_markup=kb_start,
                )
                await state.clear()

        except BotHandlerException:
            logger.warning(
                BotHandlerException("В хэндлере add_stock_device бота произошла ошибка")
            )


@stock_device_router.message(AddStockDevice.max_lamp_hours)
async def add_lamp_hours_from_stock_device(message: Message, state: FSMContext):
    await state.update_data(max_lamp_hours=message.text)
    data = await state.get_data()

    try:
        result_job = bot_api_db.bot_set_device_from_stockpile_by_name_and_id_to_db(data)

        if result_job:
            await message.answer(
                text=f"Данные добавленны <code>{result_job}</code>",
                reply_markup=kb_start,
            )

    except BotHandlerException:
        raise BotHandlerException()

    finally:
        await state.clear()


@stock_device_router.callback_query(F.data == "/cancel")
async def cancel_stock(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            text="<i>Очистка всех запросов</i>", reply_markup=kb_start
        )
    await state.clear()
