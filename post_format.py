from html import escape

from aiogram.enums import ParseMode
from aiogram.types import InputMediaPhoto


def channel_post_text(data: dict) -> str:
    comment = escape((data.get("comment") or "").strip())
    comment_line = f"📝 {comment}\n" if comment else ""
    username = data.get("username")
    if username:
        contact = f"@{escape(username)}"
    else:
        contact = (
            f'<a href="tg://user?id={int(data["submitter_id"])}">'
            "Telegram profili</a>"
        )

    if "price" in data:
        return (
            "⚡️ <b>eFOOTBALL AKKAUNTI SOTILADI</b>\n\n"
            "━━━━━━━━━━━━━━\n\n"
            f"💸 <b>Narxi:</b> {data['price']:,} so'm\n"
            f"🔄 <b>Obmen:</b> {escape(data['exchange'])}\n"
            f"🔐 <b>Google:</b> {escape(data['google'])}\n"
            f"🎮 <b>Game Center:</b> {escape(data['game_center'])}\n\n"
            "━━━━━━━━━━━━━━\n"
            f"{comment_line}\n"
            f"📩 <b>Murojat uchun:</b> {contact}\n\n"
            "E'lon berish uchun: @razzokeshop_bot\n"
            "#eFootball #akkaunt #sotiladi"
        )

    return (
        "🔎 <b>eFOOTBALL AKKAUNTI QIDIRILMOQDA</b>\n"
        "━━━━━━━━━━━━━━\n"
        f"💰 <b>Budjet:</b> {data['budget']:,} so'm\n"
        "━━━━━━━━━━━━━━\n"
        f"{comment_line}\n"
        f"📩 <b>Murojat uchun:</b> {contact}\n\n"
        "E'lon berish uchun: @razzokeshop_bot\n"
        "#eFootball #akkaunt #qidirilmoqda"
    )


async def send_post(bot, chat_id: int | str, data: dict):
    """Send the same formatted post to a user preview or the channel."""
    text = channel_post_text(data)
    photos = data.get("photos", [])
    caption = text if len(text) <= 1000 else None

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
