from aiogram.fsm.state import State, StatesGroup


class StockDeviceState(StatesGroup):
    stock_device_id = State()
    max_lamp_hours = State()


class SourceLampState(StatesGroup):
    stock_device_id = State()
    current_lamp_hours = State()


class ReplacementLamp(StatesGroup):
    stock_device_id = State()
    max_lamp_hours = State()


class AddDeviceCompany(StatesGroup):
    company_name = State()
    producer_country = State()
    description_company = State()


class AddDevice(StatesGroup):
    device_name = State()


class AddDeviceType(StatesGroup):
    type_title = State()
    description_type = State()


class GetStockDevice(StatesGroup):
    stock_device_id = State()
    device_name = State()


class MarkDeviceState(StatesGroup):
    stock_device_id = State()
    mark = State()


class BrokenDevices(StatesGroup):
    clean_date = State()


class CleanDevices(StatesGroup):
    clean_date = State()
