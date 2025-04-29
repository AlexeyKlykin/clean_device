import logging
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.run_bot import DBotAPI, DeviceCallback
from src.bot.keyboard.keyboard_start import kb_start
from src.schema_for_validate import StockBrockenDeviceData

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


get_stock_device_router = Router()

bot_api_db = DBotAPI()


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
    await message.answer(text="Введите дату а формате dd-m-yyyy")
    await state.set_state(BrokenDevices.clean_date)


@get_stock_device_router.message(BrokenDevices.clean_date)
async def get_broken_device(message: Message, state: FSMContext):
    await state.update_data(clean_date=message.text)
    data = await state.get_data()
    clean_date = data["clean_date"]

    if clean_date:
        devices = bot_api_db.get_broken_stock_device_at_date(clean_date)
    else:
        devices = bot_api_db.get_broken_stock_device_at_date()

    if devices:
        await message.answer(
            text="\n".join(
                [
                    f"ID прибора: {item.stock_device_id}\nНазвание прибора: {item.device_name}\nДата очистки: {item.at_clean_date}"
                    for item in devices
                    if isinstance(item, StockBrockenDeviceData)
                ]
            )
        )
    else:
        await message.answer(text="Нет приборов на починку")


@get_stock_device_router.message(F.text == "/mark_device")
async def start_mark_device(message: Message, state: FSMContext):
    await message.answer(text="Введите id прибора")
    await state.set_state(MarkDeviceState.stock_device_id)


@get_stock_device_router.message(MarkDeviceState.stock_device_id)
async def mark_for_stock_device_id(message: Message, state: FSMContext):
    await state.update_data(stock_device_id=message.text)
    await message.answer(
        text="Если вы хотите пометить прибор для ремонта введите 0. Если он отремонтирован то 1",
    )
    await state.set_state(MarkDeviceState.mark)


@get_stock_device_router.message(MarkDeviceState.mark)
async def mark_for_stock_device(message: Message, state: FSMContext):
    mark = message.text
    if mark in ["0", "1"]:
        await state.update_data(mark=mark)
        await message.answer(
            text="Выберите прибор",
            reply_markup=bot_api_db.gen_inline_kb_for_get_request("mark"),
        )
    else:
        await message.answer("Вы ввели неверный параметр марки", reply_markup=kb_start)


@get_stock_device_router.callback_query(
    DeviceCallback.filter(
        F.reaction_text.in_(
            ["mark_device_" + item for item in bot_api_db.get_all_devices()]
        )
    )
)
async def mark_device(
    callback: CallbackQuery, callback_data: DeviceCallback, state: FSMContext
):
    await callback.answer()
    device_data = await state.get_data()
    device_data["device_name"] = callback_data.device_name

    if callback.message:
        if device_data["mark"] == "0":
            bot_api_db.add_mark_device(
                stock_device_id=device_data["stock_device_id"],
                device_name=device_data["device_name"],
                mark=device_data["mark"],
            )

            await callback.message.answer(
                text="Прибор помещен в ремонт", reply_markup=kb_start
            )

        elif device_data["mark"] == "1":
            bot_api_db.add_mark_device(
                stock_device_id=device_data["stock_device_id"],
                device_name=device_data["device_name"],
                mark=device_data["mark"],
            )
            await callback.message.answer(
                text="Прибор выведен из ремонта", reply_markup=kb_start
            )
        else:
            await callback.message.answer(
                text="Неверно введены данные", reply_markup=kb_start
            )

    await state.clear()


@get_stock_device_router.message(F.text == "/get_stock_device")
async def send_stock_device_id(message: Message, state: FSMContext):
    await message.answer(text="Введите номер устройства со склада")
    await state.set_state(GetStockDevice.stock_device_id)


@get_stock_device_router.message(GetStockDevice.stock_device_id)
async def choice_stock_device_name(message: Message, state: FSMContext):
    await state.update_data(stock_device_id=message.text)
    await message.answer(
        text="Выберите прибор",
        reply_markup=bot_api_db.gen_inline_kb_for_get_request("device"),
    )


@get_stock_device_router.callback_query(
    DeviceCallback.filter(
        F.reaction_text.in_(
            ["get_device_" + item for item in bot_api_db.get_all_devices()]
        )
    )
)
async def get_need_device(
    callback: CallbackQuery, callback_data: DeviceCallback, state: FSMContext
):
    await callback.answer()
    device_data = await state.get_data()
    device_data["device_name"] = callback_data.device_name
    stock_device = bot_api_db.get_stock_device_id(
        device_data["stock_device_id"], device_data["device_name"]
    )

    if callback.message:
        if isinstance(stock_device, dict):
            await callback.message.answer(
                text=f"""Id прибора: {stock_device["stock_device_id"]}
        Название прибора: {stock_device["device_name"]}
        Компания производитель прибора: {stock_device["company_name"]}
        Тип прибора: {stock_device["type_title"]}
        Дата последней очистки: {stock_device["at_clean_date"]}""",
                reply_markup=kb_start,
            )

        else:
            await callback.message.answer(text=stock_device, reply_markup=kb_start)

    await state.clear()
