from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.main import main_menu
from database import add_user

from handlers.subscription import (
    check_subscription,
    show_subscription
)

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, bot: Bot):

    user = message.from_user

    add_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )

    is_subscribed = await check_subscription(
        bot,
        user.id
    )

    if not is_subscribed:
        await show_subscription(message)
        return

    await message.answer(
        f"Assalomu alaykum, <b>{user.first_name}</b>! 👋\n\n"
        "⚽ <b>eFootball Shop botiga xush kelibsiz!</b>\n\n"
        "Kerakli bo'limni tanlang:",
        reply_markup=main_menu()
    )