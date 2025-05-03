import logging
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove

from src.bot.keyboard.keyboard_start import kb_start
from src.bot_api import APIBotDb

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


db_bot_api = APIBotDb()


@device_type_router.message(F.text == "/add_device_type")
async def add_type_title(message: Message, state: FSMContext):
    await message.answer(
        text="Введите название типа прибора", reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AddDeviceType.type_title)


@device_type_router.message(AddDeviceType.type_title)
async def add_description_type(message: Message, state: FSMContext):
    await state.update_data(type_title=message.text)
    await message.answer(text="Введите описание типа прибора")
    await state.set_state(AddDeviceType.description_type)


@device_type_router.message(AddDeviceType.description_type)
async def add_device_type(message: Message, state: FSMContext):
    await state.update_data(type_description=message.text)
    data = await state.get_data()

    try:
        db_bot_api.bot_set_device_type(data)

        await message.answer(
            text=f"Данные записаны {data}. Возврат в главное меню",
            reply_markup=kb_start,
        )

    except Exception as err:
        logger.warning(err)
        await message.answer(
            text=f"Данные {data} не записаны. Возврат в главное меню",
            reply_markup=kb_start,
        )

    finally:
        await state.clear()
