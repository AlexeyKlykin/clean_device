import logging
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.types import ReplyKeyboardRemove

from src.bot.keyboard.keyboard_start import kb_start
from src.bot_api import BotHandlerException, LampTypeCallback, Marker, run_api

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


device_type_router = Router()


class AddDeviceType(StatesGroup):
    type_title = State()
    description_type = State()


db_bot_api = run_api()


@device_type_router.message(F.text == "/add_device_type")
async def add_type_title(message: Message, state: FSMContext):
    await message.answer(
        text="<i>Введите название типа прибора</i>", reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AddDeviceType.type_title)


@device_type_router.message(AddDeviceType.type_title)
async def add_description_type(message: Message, state: FSMContext):
    await state.update_data(type_title=message.text)
    await message.answer(text="<i>Введите описание типа прибора</i>")
    await state.set_state(AddDeviceType.description_type)


@device_type_router.message(AddDeviceType.description_type)
async def add_device_type(message: Message, state: FSMContext):
    await state.update_data(type_description=message.text)
    await message.answer(
        text="Выберите тип лампы", reply_markup=db_bot_api.bot_inline_kb(Marker.LAMP)
    )


@device_type_router.callback_query(
    LampTypeCallback.filter(F.text_search.in_(["LED", "FIL"]))
)
async def add_lamp_typ(
    callback: CallbackQuery, callback_data: LampTypeCallback, state: FSMContext
):
    await callback.answer()
    data = await state.get_data()
    data["lamp_type"] = callback_data.lamp_type

    try:
        result_job = db_bot_api.bot_set_device_type(data)

        if callback.message:
            await callback.message.answer(
                text=f"<b>{result_job}</b>",
                reply_markup=kb_start,
            )

    except BotHandlerException as err:
        logger.warning(err)

    finally:
        await state.clear()
