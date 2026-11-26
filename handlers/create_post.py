import re
import logging
from html import escape

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from config import ADMIN_IDS
from database import create_pending_post, update_pending_post_status
from keyboards.main import main_menu
from keyboards.posts import (
    account_status_keyboard,
    optional_comment_keyboard,
    photo_keyboard,
    preview_keyboard,
    preview_retry_keyboard,
    review_keyboard,
    sell_type_keyboard,
    yes_no_keyboard,
)
from post_format import channel_post_text, send_post

router = Router()


class PostStates(StatesGroup):
    buy_budget = State()
    buy_comment_choice = State()
    buy_comment = State()

    sell_type = State()
    sell_price = State()
    sell_exchange_details = State()
    sell_account_status = State()
    sell_google = State()
    sell_game_center = State()
    sell_comment_choice = State()
    sell_comment = State()
    sell_photos = State()

    confirmation = State()


async def clear_inline(callback: CallbackQuery):
    await callback.answer()
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)


async def show_post_preview(message: Message, state: FSMContext, user):
    data = await state.get_data()
    data["username"] = user.username
    data["submitter_id"] = user.id
    data["submitter_name"] = escape(user.full_name or "Foydalanuvchi")
    data["submitter_contact"] = (
        f"@{escape(user.username)}" if user.username
        else f'<a href="tg://user?id={user.id}">Telegram profili</a>'
    )
    data["preview"] = channel_post_text(data)
    await state.update_data(**data)
    try:
        await send_post(message.bot, message.chat.id, data)
    except Exception:
        logging.exception("E'lon previewini foydalanuvchiga yuborib bo'lmadi")
        await state.set_state(PostStates.confirmation)
        await message.answer(
            "❌ E'lon previewini yuborib bo'lmadi. Qayta urinib ko'ring.",
            reply_markup=preview_retry_keyboard()
        )
        return

    await state.set_state(PostStates.confirmation)
    await message.answer(
        "Yuqoridagi e'lon kanalga chiqadigan ko'rinishda. Uni adminga yuboraymi?",
        reply_markup=preview_keyboard()
    )


async def ask_sell_comment(message: Message, state: FSMContext):
    await state.set_state(PostStates.sell_comment_choice)
    await message.answer(
        "📝 E'longa qo'shimcha izoh kiritasizmi?",
        reply_markup=optional_comment_keyboard("sell")
    )


async def ask_for_photos(message: Message, state: FSMContext):
    await state.update_data(photos=[])
    await state.set_state(PostStates.sell_photos)
    await message.answer(
        "🖼 Akkaunt rasmlarini yuboring. Rasm yuborib bo'lgach, «Keyingisi»ni bosing.",
        reply_markup=photo_keyboard()
    )


@router.callback_query(F.data == "listing:buy")
async def buy_start(callback: CallbackQuery, state: FSMContext):
    await clear_inline(callback)
    await state.clear()
    await state.set_state(PostStates.buy_budget)
    await callback.message.answer(
        "💰 Akkaunt olish uchun budjetingizni kiriting. Masalan: 500000"
    )


@router.message(PostStates.buy_budget)
async def buy_budget(message: Message, state: FSMContext):
    price = re.sub(r"\D", "", message.text or "")
    if not price or int(price) <= 0:
        await message.answer("❌ To'g'ri budjet kiriting.")
        return

    await state.update_data(budget=int(price), comment="", listing_type="buy")
    await state.set_state(PostStates.buy_comment_choice)
    await message.answer(
        "📝 E'longa qo'shimcha izoh kiritasizmi?",
        reply_markup=optional_comment_keyboard("buy")
    )


@router.callback_query(PostStates.buy_comment_choice, F.data == "buy:comment:yes")
async def buy_comment_yes(callback: CallbackQuery, state: FSMContext):
    await clear_inline(callback)
    await state.set_state(PostStates.buy_comment)
    await callback.message.answer("Izohingizni yozing:")


@router.callback_query(PostStates.buy_comment_choice, F.data == "buy:comment:no")
async def buy_comment_no(callback: CallbackQuery, state: FSMContext):
    await clear_inline(callback)
    await state.update_data(comment="")
    await show_post_preview(callback.message, state, callback.from_user)


@router.message(PostStates.buy_comment)
async def buy_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.text or "")
    await show_post_preview(message, state, message.from_user)


@router.callback_query(F.data == "listing:sell")
async def sell_start(callback: CallbackQuery, state: FSMContext):
    await clear_inline(callback)
    await state.clear()
    await state.set_state(PostStates.sell_type)
    await callback.message.answer(
        "Sotuv e'loni turini tanlang:",
        reply_markup=sell_type_keyboard()
    )


@router.callback_query(PostStates.sell_type, F.data.startswith("sell:type:"))
async def sell_type_selected(callback: CallbackQuery, state: FSMContext):
    await clear_inline(callback)
    sale_type = callback.data.rsplit(":", 1)[1]
    await state.update_data(
        listing_type="sale",
        sale_type=sale_type,
        exchange_wanted="Yo'q" if sale_type == "sale" else ""
    )
    if sale_type == "exchange":
        await state.update_data(price=None)
        await ask_exchange_details(callback.message, state)
    else:
        await state.set_state(PostStates.sell_price)
        await callback.message.answer(
            "💰 Akkaunt narxini kiriting. Masalan: 500000"
        )


@router.message(PostStates.sell_price)
async def sell_price(message: Message, state: FSMContext):
    price = re.sub(r"\D", "", message.text or "")
    if not price or int(price) <= 0:
        await message.answer("❌ To'g'ri narx kiriting.")
        return

    await state.update_data(price=int(price))
    data = await state.get_data()
    if data.get("sale_type") == "sale_exchange":
        await ask_exchange_details(message, state)
    else:
        await ask_account_status(message, state)


async def ask_exchange_details(message: Message, state: FSMContext):
    await state.set_state(PostStates.sell_exchange_details)
    await message.answer("♻️ Qanday akkaunt yoki futbolchilarga obmen ko'rasiz? Yozing:")


@router.message(PostStates.sell_exchange_details)
async def sell_exchange_details(message: Message, state: FSMContext):
    exchange_wanted = (message.text or "").strip()
    if not exchange_wanted:
        await message.answer("❌ Obmen ko'riladigan narsani yozing:")
        return
    await state.update_data(exchange_wanted=exchange_wanted)
    await ask_account_status(message, state)


async def ask_account_status(message: Message, state: FSMContext):
    await state.set_state(PostStates.sell_account_status)
    await message.answer(
        "🎮 Google va Game Center holatini tanlang:",
        reply_markup=account_status_keyboard()
    )


@router.callback_query(PostStates.sell_account_status, F.data.startswith("sell:accounts:"))
async def sell_account_status(callback: CallbackQuery, state: FSMContext):
    await clear_inline(callback)
    choice = callback.data.rsplit(":", 1)[1]
    if choice == "both_yes":
        await state.update_data(google="Ulangan", game_center="Ulangan")
        await ask_sell_comment(callback.message, state)
    elif choice == "both_no":
        await state.update_data(google="Ulanmagan", game_center="Ulanmagan")
        await ask_sell_comment(callback.message, state)
    else:
        await state.set_state(PostStates.sell_google)
        await callback.message.answer(
            "🔐 Google ulanganmi?", reply_markup=yes_no_keyboard("google")
        )


@router.callback_query(PostStates.sell_google, F.data.startswith("sell:google:"))
async def sell_google(callback: CallbackQuery, state: FSMContext):
    await clear_inline(callback)
    google = "Ulangan" if callback.data.endswith("yes") else "Ulanmagan"
    await state.update_data(google=google)
    await state.set_state(PostStates.sell_game_center)
    await callback.message.answer(
        "🎮 Game Center ulanganmi?", reply_markup=yes_no_keyboard("game_center")
    )


@router.callback_query(PostStates.sell_game_center, F.data.startswith("sell:game_center:"))
async def sell_game_center(callback: CallbackQuery, state: FSMContext):
    await clear_inline(callback)
    status = "Ulangan" if callback.data.endswith("yes") else "Ulanmagan"
    await state.update_data(game_center=status)
    await ask_sell_comment(callback.message, state)


@router.callback_query(PostStates.sell_comment_choice, F.data == "sell:comment:yes")
async def sell_comment_yes(callback: CallbackQuery, state: FSMContext):
    await clear_inline(callback)
    await state.set_state(PostStates.sell_comment)
    await callback.message.answer("Izohingizni yozing:")


@router.callback_query(PostStates.sell_comment_choice, F.data == "sell:comment:no")
async def sell_comment_no(callback: CallbackQuery, state: FSMContext):
    await clear_inline(callback)
    await state.update_data(comment="")
    await ask_for_photos(callback.message, state)


@router.message(PostStates.sell_comment)
async def sell_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.text or "")
    await ask_for_photos(message, state)


@router.message(PostStates.sell_photos, F.photo)
async def sell_photos(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    await message.answer(
        f"✅ Rasm qabul qilindi. Jami: {len(photos)} ta.",
        reply_markup=photo_keyboard()
    )


@router.callback_query(PostStates.sell_photos, F.data == "sell:photos:next")
async def sell_photos_next(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get("photos"):
        await callback.answer("Kamida bitta rasm yuboring.", show_alert=True)
        return
    await clear_inline(callback)
    await show_post_preview(callback.message, state, callback.from_user)


@router.callback_query(PostStates.sell_photos, F.data == "sell:cancel")
async def cancel_sell_photos(callback: CallbackQuery, state: FSMContext):
    await clear_inline(callback)
    await state.clear()
    await callback.message.answer("❌ E'lon bekor qilindi.", reply_markup=main_menu())


@router.callback_query(PostStates.confirmation, F.data == "post:cancel")
async def cancel_post(callback: CallbackQuery, state: FSMContext):
    await clear_inline(callback)
    await state.clear()
    await callback.message.answer("❌ E'lon bekor qilindi.", reply_markup=main_menu())


@router.callback_query(PostStates.confirmation, F.data == "post:preview:retry")
async def retry_post_preview(callback: CallbackQuery, state: FSMContext):
    await clear_inline(callback)
    data = await state.get_data()
    try:
        await send_post(callback.bot, callback.message.chat.id, data)
    except Exception:
        logging.exception("E'lon previewini qayta yuborib bo'lmadi")
        await callback.message.answer(
            "❌ Preview hali yuborilmadi. Birozdan keyin yana urinib ko'ring.",
            reply_markup=preview_retry_keyboard()
        )
        return

    await callback.message.answer(
        "Yuqoridagi e'lon kanalga chiqadigan ko'rinishda. Uni adminga yuboraymi?",
        reply_markup=preview_keyboard()
    )


@router.callback_query(PostStates.confirmation, F.data == "post:submit")
async def confirm_post(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not ADMIN_IDS:
        await callback.message.answer(
            "❌ Admin sozlanmagan. E'lon yuborilmadi.", reply_markup=main_menu()
        )
        await state.clear()
        return

    data = await state.get_data()
    user = callback.from_user
    post_id = create_pending_post(user.id, data)
    admin_text = (
        f"🆕 <b>Yangi e'lon · #{post_id}</b>\n\n"
        f"👤 Yuboruvchi: {data['submitter_name']}\n"
        f"🔗 Aloqa: {data['submitter_contact']}\n"
        f"🆔 ID: <code>{user.id}</code>\n\n"
        "⬆️ Yuqoridagi postni ko'rib chiqib, pastdagi tugmalar orqali qaror bering."
    )
    sent_admins = []
    failed_admins = []
    for admin_id in ADMIN_IDS:
        try:
            await send_post(callback.bot, admin_id, data)
            await callback.bot.send_message(
                admin_id, admin_text, reply_markup=review_keyboard(post_id)
            )
            sent_admins.append(admin_id)
        except Exception:
            logging.exception("E'lonni %s adminga yuborib bo'lmadi", admin_id)
            failed_admins.append(admin_id)

    if not sent_admins:
        update_pending_post_status(post_id, "failed")
        await callback.message.answer(
            "❌ E'lonni adminga yuborishda xatolik yuz berdi.",
            reply_markup=main_menu()
        )
        await state.clear()
        return

    if failed_admins:
        logging.warning("E'lon faqat adminlarga yuborildi: %s", sent_admins)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "✅ E'lon admin(lar)ga yuborildi. Tasdiqlansa, kanalga joylanadi.",
        reply_markup=main_menu()
    )
    await state.clear()
