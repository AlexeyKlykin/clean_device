import asyncio

from src.run_bot import bot, dp
from src.bot.handlers import routers
from src.utils import mass_addition_of_company_to_db, mass_addition_of_type_to_db


async def main():
    [dp.include_router(router) for router in routers]
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    mass_addition_of_company_to_db()
    mass_addition_of_type_to_db()
    asyncio.run(main())
