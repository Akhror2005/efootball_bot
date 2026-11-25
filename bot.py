import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from database import init_database

from handlers.menu import router as menu_router
from handlers.create_post import router as create_post_router
from handlers.subscription import router as subscription_router
from handlers.start import router as start_router
from handlers.admin import router as admin_router
from middlewares.subscription import SubscriptionMiddleware

async def main():

    init_database()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )

    dp = Dispatcher()

    dp.message.middleware(SubscriptionMiddleware())
    dp.callback_query.middleware(SubscriptionMiddleware())

    dp.include_router(subscription_router)
    dp.include_router(start_router)
    dp.include_router(admin_router)
    dp.include_router(menu_router)
    dp.include_router(create_post_router)

    print("================================")
    print("   eFootball Shop Bot")
    print("================================")

    print("🤖 Bot ishga tushdi...")

    try:
        await dp.start_polling(bot)

    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
