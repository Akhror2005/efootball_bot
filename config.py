import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

REQUIRED_CHANNELS = [
    "@Akhrorboi_eFootball",
]

CHANNEL_LINKS = {
    "@Akhrorboi_eFootball": "https://t.me/Akhrorboi_eFootball",
}

ADMIN_IDS = [
    1157042774,
]

DATABASE_PATH = "database/efootball.db"