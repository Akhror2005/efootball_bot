from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def post_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Olish uchun", callback_data="listing:buy")],
        [InlineKeyboardButton(text="💰 Sotish uchun", callback_data="listing:sell")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="listing:back")],
    ])


def optional_comment_keyboard(prefix: str):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✍️ Ha, izoh qo‘shaman", callback_data=f"{prefix}:comment:yes"),
        InlineKeyboardButton(text="⏭ Yo‘q", callback_data=f"{prefix}:comment:no"),
    ]])


def exchange_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Bor", callback_data="sell:exchange:yes"),
        InlineKeyboardButton(text="❌ Yo‘q", callback_data="sell:exchange:no"),
    ]])


def account_status_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ikkalasi ham ulangan", callback_data="sell:accounts:both_yes")],
        [InlineKeyboardButton(text="❌ Ikkalasi ham ulanmagan", callback_data="sell:accounts:both_no")],
        [InlineKeyboardButton(text="⚡ Bittasi ulangan", callback_data="sell:accounts:one")],
    ])


def yes_no_keyboard(prefix: str):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Ulangan", callback_data=f"sell:{prefix}:yes"),
        InlineKeyboardButton(text="❌ Ulanmagan", callback_data=f"sell:{prefix}:no"),
    ]])


def photo_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="➡️ Keyingisi", callback_data="sell:photos:next"),
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="sell:cancel"),
    ]])


def preview_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Adminga yuborish", callback_data="post:submit"),
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="post:cancel"),
    ]])


def review_keyboard(post_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="✅ Tasdiqlash va kanalga chiqarish",
            callback_data=f"post:approve:{post_id}"
        ),
        InlineKeyboardButton(
            text="❌ Bekor qilish",
            callback_data=f"post:reject:{post_id}"
        ),
    ]])
