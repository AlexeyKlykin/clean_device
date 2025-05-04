import logging
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.bot_api import APIBotDb, DeviceCallback, Marker
from src.bot.keyboard.keyboard_start import kb_start
from src.schema_for_validation import StockBrokenDeviceData

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


get_stock_device_router = Router()

bot_api_db = APIBotDb()


class GetStockDevice(StatesGroup):
    stock_device_id = State()
    device_name = State()


class MarkDeviceState(StatesGroup):
    stock_device_id = State()
    mark = State()
    device_name = State()


class BrokenDevices(StatesGroup):
    clean_date = State()


@get_stock_device_router.message(F.text == "/get_broken_device")
async def start_get_broken_device(message: Message, state: FSMContext):
    await message.answer(
        text="""Введите дату а формате <b>d-m-yyyy</b>. 
Или введите <b>0</b> чтобы вывести приборы за текущую дату"""
    )
    await state.set_state(BrokenDevices.clean_date)


@get_stock_device_router.message(BrokenDevices.clean_date)
async def get_broken_device(message: Message, state: FSMContext):
    await state.update_data(at_clean_date=message.text)
    data = await state.get_data()
    devices = bot_api_db.bot_lst_broken_device_from_stockpile(data)

    if isinstance(devices, list):
        await message.answer(
            text="\n".join(
                [
                    f"""ID прибора: <code>{item.stock_device_id}</code>
Название прибора: <code>{item.device_name}</code>
Дата очистки: <code>{item.at_clean_date}</code>"""
                    for item in devices
                    if isinstance(item, StockBrokenDeviceData)
                ]
            ),
            reply_markup=kb_start,
        )
    else:
        await message.answer(text=f"<b>{devices}</b>")


@get_stock_device_router.message(F.text == "/mark_device")
async def start_mark_device(message: Message, state: FSMContext):
    await message.answer(text="<i>Введите id прибора</i>")
    await state.set_state(MarkDeviceState.stock_device_id)


@get_stock_device_router.message(MarkDeviceState.stock_device_id)
async def mark_for_stock_device_id(message: Message, state: FSMContext):
    await state.update_data(stock_device_id=message.text)
    await message.answer(
        text="Если вы хотите пометить прибор для ремонта введите <b>0</b>. Если он отремонтирован то <b>1</b>",
    )
    await state.set_state(MarkDeviceState.mark)


@get_stock_device_router.message(MarkDeviceState.mark)
async def mark_for_stock_device(message: Message, state: FSMContext):
    mark = message.text
    if mark in ["0", "1"]:
        await state.update_data(mark=mark)
        await message.answer(
            text="<i>Выберите прибор</i>",
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

    if callback.message:
        if device_data["mark"] == "0" and not result_job:
            await callback.message.answer(
                text="<b>Прибор помещен в ремонт</b>", reply_markup=kb_start
            )

        elif device_data["mark"] == "1" and not result_job:
            await callback.message.answer(
                text="<b>Прибор выведен из ремонта</b>", reply_markup=kb_start
            )

        else:
            await callback.message.answer(
                text=f"<b>{result_job}</b>", reply_markup=kb_start
            )

    await state.clear()


@get_stock_device_router.message(F.text == "/get_stock_device")
async def send_stock_device_id(message: Message, state: FSMContext):
    await message.answer(text="<i>Введите номер устройства со склада</i>")
    await state.set_state(GetStockDevice.stock_device_id)


@get_stock_device_router.message(GetStockDevice.stock_device_id)
async def choice_stock_device_name(message: Message, state: FSMContext):
    await state.update_data(stock_device_id=message.text)
    await message.answer(
        text="<i>Выберите прибор</i>",
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

    if callback.message:
        if isinstance(stock_device, dict):
            await callback.message.answer(
                text=f"""Id прибора: <code>{stock_device["stock_device_id"]}</code>
Название прибора: <code>{stock_device["device_name"]}</code>
Компания производитель прибора: <code>{stock_device["company_name"]}</code>
Тип прибора: <code>{stock_device["type_title"]}</code>
Дата последней очистки: <code>{stock_device["at_clean_date"]}</code>""",
                reply_markup=kb_start,
            )

        else:
            await callback.message.answer(
                text=f"<b>{stock_device}</b>", reply_markup=kb_start
            )

    await state.clear()
