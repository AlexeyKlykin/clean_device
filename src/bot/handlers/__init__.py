from src.bot.handlers import start_handler, add_stock_device_handler

routers = [start_handler.start_router, add_stock_device_handler.add_stock_device_router]
