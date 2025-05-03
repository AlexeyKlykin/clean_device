import logging
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.types import ReplyKeyboardRemove

from src.bot.keyboard.keyboard_start import kb_start
from src.bot_api import APIBotDb, DeviceCallback, Marker

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


bot_api_db = APIBotDb()


@stock_device_router.message(F.text == "/add_stock_device")
async def add_stock_device_id(message: Message, state: FSMContext):
    await message.answer(
        text="Введите номер прибора на складе",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(AddStockDevice.stock_device_id)


@stock_device_router.message(AddStockDevice.stock_device_id)
async def add_device_id_for_stock_device(message: Message, state: FSMContext):
    await state.update_data(stock_device_id=message.text)
    await message.answer(
        text="Введите название прибора",
        reply_markup=bot_api_db.bot_inline_kb(Marker.DEVICE),
    )


@stock_device_router.callback_query(
    DeviceCallback.filter(F.text_search.in_(bot_api_db.bot_keyboard_device_lst()))
)
async def add_stock_device(
    callback: CallbackQuery, callback_data: DeviceCallback, state: FSMContext
):
    await callback.answer()
    stock_device_data = await state.get_data()
    stock_device_data["device_name"] = callback_data.device_name

    if bot_api_db.bot_check_device_from_stockpile(stock_device_data):
        bot_api_db.bot_update_devices_stock_clearence_date(stock_device_data)
        if callback.message:
            await callback.message.answer(
                text=f"Данные прибора {stock_device_data} обновленны",
                reply_markup=kb_start,
            )

    elif bot_api_db.bot_check_device(stock_device_data["device_name"]):
        bot_api_db.bot_set_device_from_stockpile_by_name_and_id_to_db(stock_device_data)
        if callback.message:
            await callback.message.answer(
                text=f"Данные прибора {stock_device_data} сохранены",
                reply_markup=kb_start,
            )

    else:
        if callback.message:
            await callback.message.answer(
                text=f"В базе отсутствет запись {stock_device_data}",
                reply_markup=kb_start,
            )

    await state.clear()


@stock_device_router.callback_query(F.data == "/cancel")
async def cancel_stock(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            text="Очистка всех запросов", reply_markup=kb_start
        )
    await state.clear()
