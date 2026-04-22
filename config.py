import os
from dotenv import load_dotenv

load_dotenv()

BIZINFO_API_KEY = os.getenv("BIZINFO_API_KEY")
BIZINFO_API_URL = "https://www.bizinfo.go.kr/uss/rss/bizinfoApi.do"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

KEYWORDS = [
    # 사업자 유형
    "소상공인", "소공인", "개인사업자", "1인창업",
    # 창업/청년
    "창업", "청년", "예비창업",
    # 농업
    "농업", "농식품", "농촌", "귀농", "귀촌", "영농", "스마트팜", "6차산업",
    # 자금/지원
    "바우처", "보조금",
    # 경영/마케팅
    "브랜딩", "마케팅", "판로", "컨설팅",
]
