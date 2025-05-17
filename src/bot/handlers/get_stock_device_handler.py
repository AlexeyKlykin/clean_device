import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.bot.states import BrokenDevices, CleanDevices, GetStockDevice, MarkDeviceState
from src.bot_api import DeviceCallback, Marker, run_api
from src.bot.keyboard.keyboard_start import kb_start, kb_get
from src.message_handler import MessageDescription
from src.scheme_for_validation import StockDeviceData

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


get_stock_device_router = Router()

bot_api_db = run_api()


@get_stock_device_router.message(F.text == "/stock_device_at_date")
async def start_get_stock_device_at_date(message: Message, state: FSMContext):
    mes_des = MessageDescription(message.text)
    await message.answer(text=mes_des.description())
    await state.set_state(CleanDevices.clean_date)


@get_stock_device_router.message(CleanDevices.clean_date)
async def get_stock_device_at_date(message: Message, state: FSMContext):
    await state.update_data(at_clean_date=message.text)
    data = await state.get_data()
    lst_devices = bot_api_db.bot_get_devices_at_date(data)
    mes_des = MessageDescription("get_stock_device_at_date")
    mes_des.message_data = lst_devices

    if isinstance(lst_devices, list):
        await message.answer(text=mes_des.description())

    else:
        await message.answer(text=mes_des.description())

    await state.clear()


@get_stock_device_router.message(F.text == "/get_broken_device")
async def start_get_broken_device(message: Message, state: FSMContext):
    mes_des = MessageDescription(message.text)
    await message.answer(text=mes_des.description())
    await state.set_state(BrokenDevices.clean_date)


@get_stock_device_router.message(BrokenDevices.clean_date)
async def get_broken_device(message: Message, state: FSMContext):
    await state.update_data(at_clean_date=message.text)
    data = await state.get_data()
    devices = bot_api_db.bot_lst_broken_device_from_stockpile(data)
    mes_des = MessageDescription("get_broken_device")
    mes_des.message_data = devices

    if isinstance(devices, list):
        await message.answer(
            text=mes_des.description(),
            reply_markup=kb_start,
        )

    else:
        await message.answer(text=mes_des.description())

    await state.clear()


@get_stock_device_router.message(F.text == "/mark_device")
async def start_mark_device(message: Message, state: FSMContext):
    mes_des = MessageDescription(message.text)
    await message.answer(text=mes_des.description())
    await state.set_state(MarkDeviceState.stock_device_id)


@get_stock_device_router.message(MarkDeviceState.stock_device_id)
async def mark_for_stock_device_id(message: Message, state: FSMContext):
    await state.update_data(stock_device_id=message.text)
    mes_des = MessageDescription("mark_for_stock_device_id")
    await message.reply(
        text=mes_des.description(),
    )
    await state.set_state(MarkDeviceState.mark)


@get_stock_device_router.message(MarkDeviceState.mark)
async def mark_for_stock_device(message: Message, state: FSMContext):
    mark = message.text
    mes_des = MessageDescription("mark_for_stock_device")

    if mark in ["0", "1"]:
        await state.update_data(mark=mark)
        await message.reply(
            text=mes_des.description(),
            reply_markup=bot_api_db.bot_inline_kb(Marker.MARKING_DEVICES),
        )

    else:
        await message.answer(
            "<i>Вы ввели неверный параметр марки</i>", reply_markup=kb_start
        )


@get_stock_device_router.callback_query(
    DeviceCallback.filter(F.text_search.contains("mark_"))
)
async def mark_device(
    callback: CallbackQuery, callback_data: DeviceCallback, state: FSMContext
):
    await callback.answer()
    device_data = await state.get_data()
    device_data["device_name"] = callback_data.device_name
    result_job = bot_api_db.bot_change_device_status(device_data)
    mes_des = MessageDescription(device_data["mark"])

    if callback.message:
        if device_data["mark"] == "0" and not result_job:
            await callback.message.answer(
                text=mes_des.description(), reply_markup=kb_start
            )

        elif device_data["mark"] == "1" and not result_job:
            await callback.message.answer(
                text=mes_des.description(), reply_markup=kb_start
            )

        else:
            await callback.message.answer(
                text=f"<b>{result_job}</b>", reply_markup=kb_get
            )

    await state.clear()


@get_stock_device_router.message(F.text == "/get_stock_device")
async def send_stock_device_id(message: Message, state: FSMContext):
    mes_des = MessageDescription(message.text)
    await message.answer(text=mes_des.description())
    await state.set_state(GetStockDevice.stock_device_id)


@get_stock_device_router.message(GetStockDevice.stock_device_id)
async def choice_stock_device_name(message: Message, state: FSMContext):
    await state.update_data(stock_device_id=message.text)
    mes_des = MessageDescription("choice_stock_device_name")
    await message.answer(
        text=mes_des.description(),
        reply_markup=bot_api_db.bot_inline_kb(Marker.GET_DEVICE),
    )


@get_stock_device_router.callback_query(
    DeviceCallback.filter(F.text_search.contains("get_"))
)
async def show_the_devices_found(
    callback: CallbackQuery, callback_data: DeviceCallback, state: FSMContext
):
    await callback.answer()
    device_data = await state.get_data()
    device_data["device_name"] = callback_data.device_name
    stock_device = bot_api_db.bot_device_from_stockpile(device_data)
    mes_des = MessageDescription("show_the_devices_found")
    mes_des.message_data = stock_device

    if callback.message:
        if isinstance(stock_device, StockDeviceData):
            await callback.message.answer(
                text=mes_des.description(),
                reply_markup=kb_start,
            )

        else:
            await callback.message.answer(
                text=mes_des.description(), reply_markup=kb_start
            )

    await state.clear()
