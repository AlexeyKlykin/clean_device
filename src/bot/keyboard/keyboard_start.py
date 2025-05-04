from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

button_start = [
    [
        KeyboardButton(text="/add"),
        KeyboardButton(text="/get"),
    ],
]

button_add = [
    [KeyboardButton(text="/add_stock_device"), KeyboardButton(text="/add_device")],
    [
        KeyboardButton(text="/add_device_type"),
        KeyboardButton(text="/add_device_company"),
    ],
    [
        KeyboardButton(text="/cancel"),
    ],
]

button_get = [
    [
        KeyboardButton(text="/get_stock_device"),
        KeyboardButton(text="/get_broken_device"),
    ],
    [
        KeyboardButton(text="/get_devices"),
        KeyboardButton(text="/get_companies"),
        KeyboardButton(text="/get_types"),
    ],
    [KeyboardButton(text="/mark_device")],
    [
        KeyboardButton(text="/cancel"),
    ],
]

kb_start = ReplyKeyboardMarkup(
    keyboard=button_start,
    resize_keyboard=True,
    input_field_placeholder="Можете воспользоваться меню",
)
kb_add = ReplyKeyboardMarkup(
    keyboard=button_add,
    resize_keyboard=True,
    input_field_placeholder="Можете воспользоваться меню",
)
kb_get = ReplyKeyboardMarkup(
    keyboard=button_get,
    resize_keyboard=True,
    input_field_placeholder="Можете воспользоваться меню",
)
