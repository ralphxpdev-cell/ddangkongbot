import os
from dotenv import load_dotenv

load_dotenv()

BIZINFO_API_KEY = os.getenv("BIZINFO_API_KEY")
BIZINFO_API_URL = "https://www.bizinfo.go.kr/uss/rss/bizinfoApi.do"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

KEYWORDS = ["창업", "농식품", "귀농", "바우처", "보조금", "소상공인", "청년"]

DB_PATH = os.path.join(os.path.dirname(__file__), "db", "notices.db")
