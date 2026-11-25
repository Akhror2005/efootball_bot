from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📢 E'lon joylash")],
            [KeyboardButton(text="👨‍💼 Admin")]
        ],
        resize_keyboard=True
    )


def post_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🛒 Olish uchun"),
                KeyboardButton(text="💰 Sotish uchun")
            ],
            [KeyboardButton(text="🔙 Orqaga")]
        ],
        resize_keyboard=True
    )


def exchange_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="✅ Bor"),
                KeyboardButton(text="❌ Yo'q")
            ]
        ],
        resize_keyboard=True
    )


def account_status_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Ikkalasi ham ulangan")],
            [KeyboardButton(text="❌ Ikkalasi ham ulanmagan")],
            [KeyboardButton(text="⚡ Bittasi ulangan")]
        ],
        resize_keyboard=True
    )


def yes_no_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="✅ Ulangan"),
                KeyboardButton(text="❌ Ulanmagan")
            ]
        ],
        resize_keyboard=True
    )


def photo_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➡️ Keyingisi")],
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True
    )


def confirm_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="✅ Adminga yuborish"),
                KeyboardButton(text="❌ Bekor qilish")
            ]
        ],
        resize_keyboard=True
    )
