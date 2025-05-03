import asyncio

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
    asyncio.run(main())
