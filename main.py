import asyncio

from src.run_bot import bot, dp
from src.bot.handlers import routers

import inspect

from src.run_bot import DBotAPI


if __name__ == "__main__":
    bot = DBotAPI()

    res = inspect.getmembers(bot, predicate=inspect.ismethod)
    print([item[0] for item in res])
# async def main():
#     [dp.include_router(router) for router in routers]
#     await bot.delete_webhook(drop_pending_updates=True)
#     await dp.start_polling(bot)
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
