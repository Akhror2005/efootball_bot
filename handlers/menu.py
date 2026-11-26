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
        "<b>👨‍💼 ADMIN XIZMATI</b>\n\n"
        "💰 Narxi: 10 000 so'm\n\n"
        "📩 Bog'lanish uchun adminlardan birini tanlang:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=admin_buttons)
    )
