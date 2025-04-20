from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from src.run_bot import (
    request_company_interface,
    request_device_interface,
    request_stock_device_interface,
)


def generate_inline_keyboard_device() -> InlineKeyboardMarkup:
    device_interface = request_device_interface()
    lst_device = device_interface.get_all_devices()
    lst_btn = [
        InlineKeyboardButton(text=str(device[1]), callback_data=str(device[0]))
        for device in lst_device
    ]
    lst_btn.append(InlineKeyboardButton(text="/add_device", callback_data="add_device"))

    return InlineKeyboardMarkup(inline_keyboard=[lst_btn])


def generate_inline_keyboard_stock_device() -> InlineKeyboardMarkup:
    device_interface = request_stock_device_interface()
    lst_device = device_interface.get_all_stock_devices()
    lst_btn = [
        InlineKeyboardButton(text=str(device), callback_data=str(device))
        for device in lst_device
    ]
    lst_btn.append(
        InlineKeyboardButton(text="/add_stock_device", callback_data="add_stock_device")
    )

    return InlineKeyboardMarkup(inline_keyboard=[lst_btn])


def generate_inline_keyboard_company() -> InlineKeyboardMarkup:
    device_interface = request_company_interface()
    lst_device = device_interface.get_all_company()
    lst_btn = [
        InlineKeyboardButton(text=str(device), callback_data=str(device))
        for device in lst_device
    ]
    lst_btn.append(
        InlineKeyboardButton(text="/add_company", callback_data="add_company")
    )

    return InlineKeyboardMarkup(inline_keyboard=[lst_btn])


kb_btn_device = [
    [KeyboardButton(text="/add_device")],
    [KeyboardButton(text="/back")],
]
kb_add_device = ReplyKeyboardMarkup(keyboard=kb_btn_device)
