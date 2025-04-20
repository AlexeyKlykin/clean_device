from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from src.bot.keyboard.keyboard_start import kb_start


start_router = Router()


@start_router.message(CommandStart())
async def start_message(message: Message):
    await message.answer(
        "Бот поможет добавлять данные о чистых приборах со склада",
        reply_markup=kb_start,
    )
