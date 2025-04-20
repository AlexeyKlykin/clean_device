from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


kb_lst = [
    [KeyboardButton(text="/add_stock_device"), KeyboardButton(text="/add_device")],
    [
        KeyboardButton(text="/add_device_type"),
        KeyboardButton(text="/add_device_company"),
    ],
    [
        KeyboardButton(text="/get_stock_device_by_id"),
        KeyboardButton(text="/get_device_by_name"),
    ],
    [
        KeyboardButton(text="/remove_stock_device"),
        KeyboardButton(text="/remove_device"),
    ],
]

kb_start = ReplyKeyboardMarkup(keyboard=kb_lst)
