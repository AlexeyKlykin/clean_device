import asyncio

from src.run_bot import bot, dp
from src.bot.handlers import routers


async def main():
    [dp.include_router(router) for router in routers]
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
