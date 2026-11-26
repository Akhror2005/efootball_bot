from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.main import main_menu
from keyboards.posts import post_menu
from config import ADMIN_IDS

router = Router()


@router.message(F.text == "📢 E'lon joylash")
async def post_menu_handler(message: Message):
    await message.answer(
        "Qaysi turdagi e'lon joylamoqchisiz?",
        reply_markup=post_menu()
    )


@router.callback_query(F.data == "listing:back")
async def back_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "Asosiy menyu:",
        reply_markup=main_menu()
    )


@router.message(F.text == "👨‍💼 Admin")
async def admin_handler(message: Message):
    if not ADMIN_IDS:
        await message.answer("Admin aloqa ma'lumotlari sozlanmagan.")
        return

    admin_buttons = [
        [InlineKeyboardButton(
            text=f"✉️ Admin {index} bilan bog'lanish",
            url=f"tg://user?id={admin_id}"
        )]
        for index, admin_id in enumerate(ADMIN_IDS, start=1)
    ]
    await message.answer(
        "<b>🛍 ADMIN GARANT NARXLARI</b>\n\n"

        "<blockquote>🔴 <b>Agar xaridor Gmail parolini o'zi o'zgartirsa:</b>\n\n"
        "▪️ 1 000 – 99 000 so'm: <b>5 000 so'm</b> ⚡️\n"
        "▪️ 100 000 – 400 000 so'm: <b>10 000 so'm</b> ⚡️\n"
        "▪️ 401 000 – 999 000 so'm: <b>15 000 so'm</b> ⚡️\n"
        "▪️ 1 000 000 so'm +: <b>20 000 so'm</b> ⚡️\n\n"

        "🔴 <b>Agar garant admin Gmail parolini o'zgartirsa:</b>\n\n"
        "▪️ 1 000 – 99 000 so'm: <b>10 000 so'm</b> ⚡️\n"
        "▪️ 100 000 – 400 000 so'm: <b>15 000 so'm</b> ⚡️\n"
        "▪️ 401 000 – 999 000 so'm: <b>20 000 so'm</b> ⚡️\n"
        "▪️ 1 000 000 so'm +: <b>25 000 so'm</b> ⚡️\n\n"

        "🔄 <b>Obmen uchun:</b>\n\n"
        "▪️ 1 000 – 199 000 so'm: <b>15 000 so'm</b> ⚡️\n"
        "▪️ 200 000 – 999 000 so'm: <b>20 000 so'm</b> ⚡️\n"
        "▪️ 1 000 000 so'm +: <b>25 000 so'm</b> ⚡️\n\n"

        "⚠️ <b>Doplata bo'lsa, narxi oshadi!</b>\n\n"

        "👍 Game Center ko'rib berish: <b>5 000 so'm</b>\n"
        "👍 Google Play ko'rib berish: <b>5 000 so'm</b>\n"
        "🔵 Email almashtirish: <b>5 000 so'm</b>\n\n"

        "🟥 <b>Savdo bekor qilinsa, admin puli qaytarilmaydi.</b></blockquote>\n\n"

        "📩 <b>Garant xizmatidan foydalanish uchun adminlardan birini tanlang:</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=admin_buttons)
    )
