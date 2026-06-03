import os
from dotenv import load_dotenv

load_dotenv()

# telegram_bot/config.py
import os

API_BASE_URL = os.environ.get("BACKEND_URL", "http://localhost:8080")
BOT_SECRET   = os.environ.get("TELEGRAM_BOT_SECRET", "")
BOT_TOKEN    = os.environ.get("TELEGRAM_BOT_TOKEN", "")