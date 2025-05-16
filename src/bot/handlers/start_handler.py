from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import CommandStart

from src.bot.keyboard.keyboard_start import kb_start, kb_add, kb_get
from src.message_handler import MessageDescription


start_router = Router()


@start_router.message(CommandStart())
async def start_message(message: Message):
    mes_des = MessageDescription(message.text)
    await message.answer(
        mes_des.description(),
        reply_markup=kb_start,
    )


@start_router.message(F.text == "/add")
async def add_message(message: Message):
    mes_des = MessageDescription(message.text)
    await message.answer(text=mes_des.description(), reply_markup=kb_add)


@start_router.message(F.text == "/get")
async def get_message(message: Message):
    mes_des = MessageDescription(message.text)
    await message.answer(text=mes_des.description(), reply_markup=kb_get)


@start_router.message(F.text == "/cancel")
async def cancel(message: Message, state: FSMContext):
    mes_des = MessageDescription(message.text)
    await message.answer(text=mes_des.description(), reply_markup=kb_start)
    await state.clear()
