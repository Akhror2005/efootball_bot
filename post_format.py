from html import escape
from pathlib import Path

from aiogram.enums import ParseMode
from aiogram.types import FSInputFile, InputMediaPhoto

BUY_POST_IMAGE = Path(__file__).resolve().parent / "olish.jpg"


def channel_post_text(data: dict) -> str:
    comment = escape((data.get("comment") or "").strip())
    note = comment or "Ko'rsatilmagan"
    username = data.get("username")
    if username:
        contact = f"@{escape(username)}"
    else:
        contact = (
            f'<a href="tg://user?id={int(data["submitter_id"])}">'
            "Telegram profili</a>"
        )

    if data.get("listing_type") == "buy" or ("budget" in data and "price" not in data):
        return (
            "⚽️━ <b>#OLINADI #FAQAT_TOZA</b> ━⚽️\n\n"
            f"💰 <b>BUDJET:</b> {data['budget']:,} so'm\n"
            f"📝 <b>Ma'lumot:</b> {note}\n\n"
            f"📞 <b>Murojaat:</b> {contact}\n\n"
            "<blockquote>👨‍💻 <b>OLDI SOTDI GARANT ADMINLAR:</b>\n"
            '<a href="https://t.me/Razzoke_garant">@Razzoke_garant</a>\n\n'
            "<b>GARANT TARTIBI:</b>\n"
            '<a href="https://t.me/razzoke_info">@razzoke_info</a>\n\n'
            "<b>ARZON DONAT XIZMATI:</b>\n"
            '<a href="https://t.me/RazzokeCoins">@RazzokeCoins</a>\n\n'
            "<b>ELON BERISH UCHUN:</b>\n"
            '<a href="https://t.me/RazzokeShop_bot">@RazzokeShop_bot</a></blockquote>'
        )

    sale_type = data.get("sale_type", "sale")
    if sale_type == "sale_exchange":
        heading = "<b>#SOTILADI #OBMEN</b>"
        price_text = f"{data['price']:,} so'm"
        exchange_text = data.get("exchange_wanted") or "Kelishiladi"
    elif sale_type == "exchange":
        heading = "<b>#OBMEN</b>"
        price_text = "Kelishilgan (Obmen)"
        exchange_text = data.get("exchange_wanted") or "Kelishiladi"
    else:
        heading = "<b>#SOTILADI</b>"
        price_text = f"{data['price']:,} so'm"
        exchange_text = "Yo'q"

    return (
        f"⚽️━ {heading} ━⚽️\n\n"
        f"💰 <b>Narx:</b> {price_text}\n"
        f"♻️ <b>Obmen ko'rish:</b> {escape(exchange_text)}\n"
        f"⚠️ <b>Google &amp; Game Center:</b> "
        f"{escape(data.get('google', 'Noma’lum'))} &amp; "
        f"{escape(data.get('game_center', 'Noma’lum'))}\n"
        f"📞 <b>Murojaat:</b> {contact}\n\n"
        "<blockquote>📝 <b>Qo'shimcha ma'lumot:</b>\n"
        f"{note}\n\n"
        "♻️ <b>OLDI SOTDI GARANT ADMINLAR:</b>\n"
        '<a href="https://t.me/Razzoke_garant">@Razzoke_garant</a>\n\n'
        "<b>GARANT TARTIBI:</b>\n"
        '<a href="https://t.me/razzoke_info">@razzoke_info</a>\n\n'
        "<b>ARZON DONAT XIZMATI:</b>\n"
        '<a href="https://t.me/RazzokeCoins">@RazzokeCoins</a>\n\n'
        "<b>ELON BERISH UCHUN BOT:</b>\n"
        '<a href="https://t.me/RazzokeShop_bot">@RazzokeShop_bot</a></blockquote>'
    )


async def send_post(bot, chat_id: int | str, data: dict):
    """Send the same formatted post to a user preview or the channel."""
    text = channel_post_text(data)
    photos = data.get("photos", [])
    caption = text if len(text) <= 1000 else None

    if data.get("listing_type") == "buy" or ("budget" in data and "price" not in data):
        image = FSInputFile(BUY_POST_IMAGE)
        if caption:
            return await bot.send_photo(chat_id, image, caption=caption)
        await bot.send_message(chat_id, text)
        return await bot.send_photo(chat_id, image)

    if not photos:
        return await bot.send_message(chat_id, text)

    if len(photos) == 1:
        if caption:
            return await bot.send_photo(chat_id, photos[0], caption=caption)
        await bot.send_message(chat_id, text)
        return await bot.send_photo(chat_id, photos[0])

    media = [
        InputMediaPhoto(
            media=file_id,
            caption=caption if index == 0 else None,
            parse_mode=ParseMode.HTML if index == 0 and caption else None
        )
        for index, file_id in enumerate(photos[:10])
    ]
    if not caption:
        await bot.send_message(chat_id, text)
    sent = await bot.send_media_group(chat_id, media)
    for start in range(10, len(photos), 10):
        batch = photos[start:start + 10]
        if len(batch) == 1:
            sent.append(await bot.send_photo(chat_id, batch[0]))
        else:
            sent.extend(await bot.send_media_group(
                chat_id,
                [InputMediaPhoto(media=file_id) for file_id in batch]
            ))
    return sent
