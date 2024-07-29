import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TOKEN = os.getenv("DISCORD_TOKEN")
    GUILD_ID = int(os.getenv("GUILD_ID"))
    DATABASE_PATH = os.getenv("DATABASE_PATH", "katsupport.sqlite")
    OWNER_ID = int(os.getenv("OWNER_ID"))
    MODMAIL_CATEGORY_ID = int(os.getenv("MODMAIL_CATEGORY_ID"))
    TICKET_CATEGORY_ID = int(os.getenv("TICKET_CATEGORY_ID"))
    LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))
    VOICE_CHANNEL_ID = int(os.getenv("VOICE_CHANNEL_ID"))

CONFIG = Config()