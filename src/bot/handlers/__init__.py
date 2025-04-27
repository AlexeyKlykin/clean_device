from src.bot.handlers import (
    start_handler,
    add_stock_device_handler,
    add_device_handler,
    add_type_device_handler,
    add_company_handler,
    get_stock_device_handler,
)

routers = [
    start_handler.start_router,
    add_stock_device_handler.stock_device_router,
    add_device_handler.device_router,
    add_type_device_handler.device_type_router,
    add_company_handler.device_company_router,
    get_stock_device_handler.get_stock_device_router,
]
