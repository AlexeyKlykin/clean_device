import logging
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.types import ReplyKeyboardRemove

from src.bot.keyboard.keyboard_start import kb_start
from src.run_bot import DBotAPI, DeviceCallback

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
        text="Введите название прибора", reply_markup=bot_api_db.gen_inline_kb("device")
    )


@stock_device_router.callback_query(
    DeviceCallback.filter(F.reaction_text.in_(bot_api_db.get_all_devices()))
)
async def add_stock_device(
    callback: CallbackQuery, callback_data: DeviceCallback, state: FSMContext
):
    await callback.answer()
    stock_device_data = await state.get_data()
    stock_device_data["device_name"] = callback_data.device_name
    stock_device_id = stock_device_data["stock_device_id"]
    device_name = stock_device_data["device_name"]

    if bot_api_db.check_stock_device(stock_device_id, device_name):
        bot_api_db.update_stock_device(stock_device_id, device_name)
        if callback.message:
            await callback.message.answer(
                text=f"Данные прибора по {stock_device_id} обновленны",
                reply_markup=kb_start,
            )

    elif bot_api_db.check_device_id(device_name):
        bot_api_db.save_stock_device_into_db_from_bot(stock_device_data)
        if callback.message:
            await callback.message.answer(
                text=f"Данные прибора по {stock_device_id} сохранены",
                reply_markup=kb_start,
            )

    else:
        if callback.message:
            await callback.message.answer(
                text=f"В базе отсутствет запись об {device_name}", reply_markup=kb_start
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
