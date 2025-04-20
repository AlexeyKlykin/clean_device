from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


kb_btn_company = [
    [KeyboardButton(text="/add_device_company")],
    [KeyboardButton(text="/back")],
]

kb_add_company = ReplyKeyboardMarkup(keyboard=kb_btn_company)
