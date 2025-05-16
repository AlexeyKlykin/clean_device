import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.types import ReplyKeyboardRemove

from src.bot.keyboard.keyboard_start import kb_start
from src.bot.states import StockDeviceState
from src.bot_api import (
    run_api,
    DeviceCallback,
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


stock_device_router = Router()


bot_api_db = run_api()

devices_cache = set()


@stock_device_router.message(F.text == "/add_stock_device")
async def add_stock_device_id(message: Message, state: FSMContext):
    mes_des = MessageDescription(message.text)
    await message.answer(
        text=mes_des.description(),
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(StockDeviceState.stock_device_id)
    devices_cache.update(bot_api_db.bot_keyboard_device_lst())


@stock_device_router.message(StockDeviceState.stock_device_id)
async def add_device_id_for_stock_device(message: Message, state: FSMContext):
    await state.update_data(stock_device_id=message.text)
    mes_des = MessageDescription("add_device_id_for_stock_device")
    await message.answer(
        text=mes_des.description(),
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
            mes_des = MessageDescription(result_job[0])
            mes_des.message_data = result_job[1]

            if result_job[0] == "update":
                await callback.message.answer(
                    text=mes_des.description(),
                    reply_markup=kb_start,
                )
                await state.clear()

            elif result_job[0] == "LED":
                await callback.message.answer(
                    text=mes_des.description(),
                    reply_markup=kb_start,
                )
                await state.clear()

            elif result_job[0] == "FIL":
                await state.set_data(stock_device_data)

                if callback.message:
                    await callback.message.answer(
                        text=mes_des.description(),
                    )
                await state.set_state(StockDeviceState.max_lamp_hours)

            else:
                mes_des = MessageDescription("lamp_error")
                mes_des.message_data = (result_job, stock_device_data)

                await callback.message.answer(
                    text=mes_des.description(),
                    reply_markup=kb_start,
                )
                await state.clear()

        except BotHandlerException:
            logger.warning(
                BotHandlerException("В хэндлере add_stock_device бота произошла ошибка")
            )


@stock_device_router.message(StockDeviceState.max_lamp_hours)
async def add_lamp_hours_from_stock_device(message: Message, state: FSMContext):
    await state.update_data(max_lamp_hours=message.text)
    data = await state.get_data()
    mes_des = MessageDescription("add_lamp_hours_from_stock_device")

    try:
        result_job = bot_api_db.bot_set_device_from_stockpile_by_name_and_id_to_db(data)
        mes_des.message_data = result_job

        if result_job:
            await message.answer(
                text=mes_des.description(),
                reply_markup=kb_start,
            )

    except BotHandlerException:
        await message.answer(text=mes_des.description())
        logger.warning(BotHandlerException())

    finally:
        await state.clear()
