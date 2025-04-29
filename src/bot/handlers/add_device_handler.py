import logging
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.types import ReplyKeyboardRemove

from src.bot.keyboard.keyboard_start import kb_start
from src.run_bot import (
    CompanyCallback,
    DBotAPI,
    DeviceTypeCallback,
)

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


device_router = Router()

bot_api_db = DBotAPI()


class AddDevice(StatesGroup):
    device_name = State()
    company_name = State()
    type_title = State()


@device_router.message(F.text == "/add_device")
async def device(message: Message, state: FSMContext):
    await message.answer(
        text="Введите название устройства", reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AddDevice.device_name)


@device_router.message(AddDevice.device_name)
async def device_name(message: Message, state: FSMContext):
    await state.update_data(device_name=message.text)
    await message.answer(
        text="Введите компанию производитель прибора",
        reply_markup=bot_api_db.gen_inline_kb("company"),
    )


@device_router.callback_query(
    CompanyCallback.filter(F.reaction_text.in_(bot_api_db.get_all_company()))
)
async def company_for_device(
    callback: CallbackQuery, callback_data: CompanyCallback, state: FSMContext
):
    await callback.answer()
    device_data = await state.get_data()
    device_data["company_name"] = callback_data.company_name
    await state.set_data(device_data)

    if callback.message:
        if device_data["company_name"]:
            await callback.message.answer(
                text="Выберите тип прибора",
                reply_markup=bot_api_db.gen_inline_kb("device_type"),
            )

        else:
            await callback.message.answer(
                text="Выберите тип прибора", reply_markup=kb_start
            )
            await state.clear()


@device_router.callback_query(
    DeviceTypeCallback.filter(F.reaction_text.in_(bot_api_db.get_all_type()))
)
async def type_for_device(
    callback: CallbackQuery, callback_data: DeviceTypeCallback, state: FSMContext
):
    await callback.answer()
    device_data = await state.get_data()
    device_data["type_title"] = callback_data.device_type
    bot_api_db.save_device_from_bot_into_db(device_data)

    if callback.message:
        await callback.message.answer(
            text="Прибор добавлен в базу", reply_markup=kb_start
        )

    await state.clear()


@device_router.callback_query(F.data == "/cancel")
async def cance_stock(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            text="Очистка всех запросов", reply_markup=kb_start
        )
    await state.clear()
