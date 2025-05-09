from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import CommandStart

from src.bot.keyboard.keyboard_start import kb_start, kb_add, kb_get


start_router = Router()


@start_router.message(CommandStart())
async def start_message(message: Message):
    await message.answer(
        "<i>Бот поможет добавлять данные о чистых приборах со склада</i>",
        reply_markup=kb_start,
    )


@start_router.message(F.text == "/add")
async def add_message(message: Message):
    await message.answer(
        text="<i>Переход к меню добавления приборов</i>", reply_markup=kb_add
    )


@start_router.message(F.text == "/get")
async def get_message(message: Message):
    await message.answer(
        text="<i>Переход к меню выбора приборов</i>", reply_markup=kb_get
    )


@start_router.message(F.text == "/cancel")
async def cancel(message: Message, state: FSMContext):
    await message.answer(text="<i>Возврат назад</i>", reply_markup=kb_start)
    await state.clear()
