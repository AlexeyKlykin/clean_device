import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.types import ReplyKeyboardRemove

from src.bot.keyboard.keyboard_start import kb_start
from src.bot.states import AddDeviceType
from src.bot_api import LampTypeCallback, Marker, run_api
from src.data_handler import BotHandlerException
from src.message_handler import MessageDescription

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


device_type_router = Router()


db_bot_api = run_api()


@device_type_router.message(F.text == "/add_device_type")
async def add_type_title(message: Message, state: FSMContext):
    mes_des = MessageDescription(message.text)
    await message.answer(text=mes_des.description(), reply_markup=ReplyKeyboardRemove())
    await state.set_state(AddDeviceType.type_title)


@device_type_router.message(AddDeviceType.type_title)
async def add_description_type(message: Message, state: FSMContext):
    await state.update_data(type_title=message.text)
    mes_des = MessageDescription("add_description_type")
    await message.reply(text=mes_des.description())
    await state.set_state(AddDeviceType.description_type)


@device_type_router.message(AddDeviceType.description_type)
async def add_device_type(message: Message, state: FSMContext):
    await state.update_data(type_description=message.text)
    mes_des = MessageDescription("add_device_type")
    await message.reply(
        text=mes_des.description(), reply_markup=db_bot_api.bot_inline_kb(Marker.LAMP)
    )


@device_type_router.callback_query(
    LampTypeCallback.filter(F.text_search.in_(["LED", "FIL"]))
)
async def add_lamp_type(
    callback: CallbackQuery, callback_data: LampTypeCallback, state: FSMContext
):
    await callback.answer()
    data = await state.get_data()
    data["lamp_type"] = callback_data.lamp_type
    mes_des = MessageDescription("add_lamp_type")

    if callback.message:
        try:
            result_job = db_bot_api.bot_set_device_type(data)
            mes_des.message_data = result_job

            await callback.message.answer(
                text=mes_des.description(),
                reply_markup=kb_start,
            )

        except BotHandlerException as err:
            logger.warning(err)
            await callback.message.reply(text=mes_des.description())

        finally:
            await state.clear()
