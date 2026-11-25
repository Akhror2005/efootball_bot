from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from handlers.subscription import (
    check_subscription,
    show_subscription
)


class SubscriptionMiddleware(BaseMiddleware):

    async def __call__(self, handler, event, data):

        bot = data["bot"]

        # /start orqali kirishga ruxsat
        if isinstance(event, Message):
            if event.text and event.text.startswith("/start"):
                return await handler(event, data)

        # Obunani tekshirish tugmasiga ruxsat
        if isinstance(event, CallbackQuery):
            if event.data == "check_subscription":
                return await handler(event, data)

        user_id = event.from_user.id

        is_subscribed = await check_subscription(bot, user_id)

        if not is_subscribed:

            if isinstance(event, Message):
                await show_subscription(event)

            elif isinstance(event, CallbackQuery):
                await event.answer(
                    "❌ Botdan foydalanish uchun kanalga a'zo bo'ling!",
                    show_alert=True
                )

                await bot.send_message(
                    chat_id=user_id,
                    text=(
                        "⚠️ Botdan foydalanish uchun "
                        "kanalga a'zo bo'ling."
                    ),
                    reply_markup=__import__(
                        "handlers.subscription",
                        fromlist=["subscription_keyboard"]
                    ).subscription_keyboard()
                )

            return

        return await handler(event, data)