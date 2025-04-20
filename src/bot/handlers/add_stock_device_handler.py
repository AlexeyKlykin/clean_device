import json
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.types import ReplyKeyboardRemove

from src.bot.keyboard.keyboard_start import kb_start
from src.bot.keyboard.keyboard_device import (
    generate_inline_keyboard_company,
    kb_add_device,
    generate_inline_keyboard_device,
    generate_inline_keyboard_stock_device,
)
from src.bot.keyboard.keyboard_company import kb_add_company
from src.utils import modificate_date_to_str
from src.run_bot import (
    request_company_interface,
    request_stock_device_interface,
    request_device_interface,
)


add_stock_device_router = Router()


class AddStockDevice(StatesGroup):
    stock_device_id = State()
    stock_device_name = State()
    stock_device_company = State()


@add_stock_device_router.message(F.text == "/add_stock_device")
async def stock_device(message: Message, state: FSMContext):
    await message.answer(text="Введите id прибора", reply_markup=ReplyKeyboardRemove())
    await message.answer(
        text="Или выберите из списка",
        reply_markup=generate_inline_keyboard_stock_device(),
    )
    await state.set_state(AddStockDevice.stock_device_id)


@add_stock_device_router.message(AddStockDevice.stock_device_id)
async def stock_device_id(message: Message, callback: CallbackQuery, state: FSMContext):
    device_id = callback.data if callback.data else message.text

    if device_id:
        stock_device_interface = request_stock_device_interface()

        if stock_device_interface.check_device_by_id(device_id=int(device_id)):
            stock_device_interface.update_device_date(device_id=int(device_id))
            await message.answer(
                text=f"Данные прибора по id {device_id} обновлены",
                reply_markup=kb_start,
            )

        else:
            await state.update_data(device_id=message.text)
            await message.answer(
                text="Введите название прибора",
                reply_markup=generate_inline_keyboard_device(),
            )
            await state.set_state(AddStockDevice.stock_device_name)
    else:
        await state.clear()
        await message.answer(
            text="Не задан id прибора. Возврат к началу", reply_markup=kb_start
        )


@add_stock_device_router.message(AddStockDevice.stock_device_name)
async def stock_device_name(
    message: Message, callback: CallbackQuery, state: FSMContext
):
    device_name = callback.data if callback.data else message.text
    if device_name:
        device_interface = request_device_interface()

        if device_interface.check_by_title(device_name):
            device_id = device_interface.get_id_by_name(device_name=device_name)
            await state.update_data(device_name=device_id)
            await message.answer(
                text="Введите компанию производителя",
                reply_markup=generate_inline_keyboard_company(),
            )
            await state.set_state(AddStockDevice.stock_device_company)
        else:
            await message.answer(
                text=f"Нужно добавить {device_name} в таблицу приборов",
                reply_markup=kb_add_device,
            )
    else:
        await state.clear()
        await message.answer(
            text="Не задано имя прибора. Возврат к началу", reply_markup=kb_start
        )


@add_stock_device_router.message(AddStockDevice.stock_device_company)
async def stock_device_company(
    message: Message, callback: CallbackQuery, state: FSMContext
):
    device_company = callback.data if callback.data else message.text
    if device_company:
        company_interface = request_company_interface()
        if company_interface.check_by_title(device_company):
            company_id = company_interface.get_id_by_name(device_company)
            await state.update_data(device_company=company_id)
            data = await state.get_data()
            match data:
                case {
                    "device_id": str(device_id),
                    "device_name": str(device_name),
                    "device_company": str(device_company),
                }:
                    item = {
                        "stock_device_id": device_id,
                        "device_id": device_name,
                        "at_clean_date": modificate_date_to_str(),
                    }
                    stock_device_interface = request_stock_device_interface()
                    stock_device_interface.insert(item)
                case _:
                    with open("temp_stock_device.json", "w") as js:
                        json.dump(obj=data, fp=js)
        else:
            await message.answer(
                text=f"В базе нет такой компании {device_company}. Нужно добавить",
                reply_markup=kb_add_company,
            )
            await state.clear()

    await message.answer(text="Возврат", reply_markup=kb_start)
    await state.clear()
