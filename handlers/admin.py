import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery

from config import ADMIN_IDS, REQUIRED_CHANNELS
from database import (
    get_pending_post,
    update_pending_post_payload,
    update_pending_post_status,
)
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

    payload = post["payload"]
    delivered_channels = payload.get("delivered_channels", [])
    failed_channels = [] if REQUIRED_CHANNELS else ["kanal sozlanmagan"]
    for channel in dict.fromkeys(REQUIRED_CHANNELS):
        if channel in delivered_channels:
            continue
        try:
            await send_post(callback.bot, channel, payload)
            delivered_channels.append(channel)
            payload["delivered_channels"] = delivered_channels
            update_pending_post_payload(post_id, payload)
        except Exception:
            logging.exception("E'lonni %s kanaliga yuborib bo'lmadi", channel)
            failed_channels.append(channel)

    if failed_channels:
        update_pending_post_status(post_id, "pending", expected="publishing")
        await callback.answer(
            "Quyidagi kanal(lar)ga yuborilmadi: "
            f"{', '.join(map(str, failed_channels))}. Botni kanal admini qiling.",
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
