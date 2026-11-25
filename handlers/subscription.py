from aiogram import Router, F, Bot
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from config import REQUIRED_CHANNELS, CHANNEL_LINKS
from keyboards.main import main_menu

router = Router()


async def check_subscription(bot: Bot, user_id: int):

    for channel in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(
                chat_id=channel,
                user_id=user_id
            )

            if member.status not in ["creator", "administrator", "member"]:
                return False

        except Exception as e:
            print(f"Obuna tekshirish xatosi: {e}")
            return False

    return True


def subscription_keyboard():

    buttons = []

    for channel in REQUIRED_CHANNELS:
        buttons.append([
            InlineKeyboardButton(
                text="📢 Kanalga obuna bo'lish",
                url=CHANNEL_LINKS[channel]
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="🔄 Obunani tekshirish",
            callback_data="check_subscription"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def show_subscription(message: Message):

    await message.answer(
        "⚠️ <b>Botdan foydalanish uchun kanalimizga a'zo bo'ling!</b>\n\n"
        "1. Kanalga obuna bo'ling.\n"
        "2. Obuna bo'lganingizdan so'ng tekshirish tugmasini bosing.",
        reply_markup=subscription_keyboard()
    )


@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery, bot: Bot):

    is_subscribed = await check_subscription(
        bot,
        callback.from_user.id
    )

    if is_subscribed:

        await callback.message.delete()

        await callback.message.answer(
            "✅ Obuna tasdiqlandi!\n\n"
            "Botdan foydalanishingiz mumkin.",
            reply_markup=main_menu()
        )

    else:

        await callback.answer(
            "❌ Siz hali kanalga a'zo bo'lmagansiz!",
            show_alert=True
        )