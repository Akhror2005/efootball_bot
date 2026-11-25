import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

REQUIRED_CHANNELS = [
    "@Akhrorboi_eFootball",
    "@RazzokeShop",
]

CHANNEL_LINKS = {
    "@Akhrorboi_eFootball": "https://t.me/Akhrorboi_eFootball",
    "@RazzokeShop": "https://t.me/RazzokeShop",
}

ADMIN_IDS = [
    7579990560,
]

DATABASE_PATH = "database/efootball.db"
