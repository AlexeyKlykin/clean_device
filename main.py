import asyncio
import logging
import sys

from src.bot_api import bot, dp
from src.bot.handlers import routers


async def main():
    [dp.include_router(router) for router in routers]

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
