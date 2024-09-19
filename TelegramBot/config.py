import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
# ALLOWED_USER_IDS = [int(id) for id in os.getenv("ALLOWED_USER_IDS").split(",")]
