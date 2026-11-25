import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery

from config import ADMIN_IDS, REQUIRED_CHANNELS
from database import get_pending_post, update_pending_post_status
from post_format import send_post

router = Router()


@router.callback_query(F.data.startswith("post:approve:"))
async def approve_post(callback: CallbackQuery):
    await review_post(callback, "approve")


@router.callback_query(F.data.startswith("post:reject:"))
async def reject_post(callback: CallbackQuery):
    await review_post(callback, "reject")


async def review_post(callback: CallbackQuery, action: str):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Bu amal faqat admin uchun.", show_alert=True)
        return

    try:
        post_id = int(callback.data.rsplit(":", 1)[1])
    except (ValueError, AttributeError):
        await callback.answer("E'lon raqami noto'g'ri.", show_alert=True)
        return

    post = get_pending_post(post_id)
    if not post:
        await callback.answer("E'lon topilmadi.", show_alert=True)
        return

    if action == "reject":
        if not update_pending_post_status(post_id, "cancelled"):
            await callback.answer("Bu e'lon avval ko'rib chiqilgan.", show_alert=True)
            return
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.answer("E'lon bekor qilindi.")
        try:
            await callback.bot.send_message(
                post["user_telegram_id"],
                "❌ E'loningiz admin tomonidan bekor qilindi."
            )
        except Exception:
            pass
        return

    if not update_pending_post_status(post_id, "publishing"):
        await callback.answer("Bu e'lon avval ko'rib chiqilgan.", show_alert=True)
        return

    try:
        if not REQUIRED_CHANNELS:
            raise RuntimeError("Kanal sozlanmagan")
        await send_post(callback.bot, REQUIRED_CHANNELS[0], post["payload"])
    except Exception:
        logging.exception("Tasdiqlangan e'lonni kanalga yuborib bo'lmadi")
        update_pending_post_status(post_id, "pending", expected="publishing")
        await callback.answer(
            "Kanalga yuborilmadi. Bot kanal admini ekanini tekshiring.",
            show_alert=True
        )
        return

    update_pending_post_status(post_id, "published", expected="publishing")
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer("E'lon kanalga joylandi!")
    try:
        await callback.bot.send_message(
            post["user_telegram_id"],
            "✅ E'loningiz admin tomonidan tasdiqlanib, kanalga joylandi."
        )
    except Exception:
        pass
