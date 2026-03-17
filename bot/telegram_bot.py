import re
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def _format_date(raw):
    """'20220727 ~ 20220930' → '2022.07.27 ~ 2022.09.30'"""
    def convert(m):
        d = m.group(0)
        return f"{d[:4]}.{d[4:6]}.{d[6:8]}"
    return re.sub(r"\d{8}", convert, raw) if raw else "-"


def _format_tags(raw):
    """'창업,청년,바우처' → '#창업 #청년 #바우처'"""
    if not raw:
        return ""
    tags = [t.strip() for t in raw.replace("#", "").split(",") if t.strip()]
    return " ".join(f"#{t}" for t in tags)


def build_message(item):
    name = item.get("pblancNm", "")
    org = item.get("jrsdInsttNm", "")
    period = _format_date(item.get("reqstBeginEndDe", ""))
    url = item.get("pblancUrl", "")
    tags = _format_tags(item.get("hashtags", ""))

    msg = (
        f"🔔 새 공고 발견\n\n"
        f"📌 {name}\n"
        f"🏛 {org}\n"
        f"📅 신청기간: {period}\n"
        f"🔗 {url}\n"
    )
    if tags:
        msg += f"{tags}\n"
    return msg


def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "disable_web_page_preview": True,
    }
    resp = requests.post(url, json=payload, timeout=15)
    resp.raise_for_status()
    return resp.json()


def send_notice(item):
    msg = build_message(item)
    return send_message(msg)


def send_error(error_text):
    msg = f"⚠️ BizRadar 오류 발생\n\n{error_text}"
    try:
        send_message(msg)
    except Exception:
        pass
