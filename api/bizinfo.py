import requests
from config import BIZINFO_API_KEY, BIZINFO_API_URL, KEYWORDS


def fetch_notices(page_unit=100, page_index=1):
    """bizinfo API에서 공고 목록을 가져온다."""
    params = {
        "crtfcKey": BIZINFO_API_KEY,
        "dataType": "json",
        "pageUnit": page_unit,
        "pageIndex": page_index,
    }
    resp = requests.get(BIZINFO_API_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    items = data.get("jsonArray", [])
    return items if isinstance(items, list) else [items]


def filter_notices(items):
    """키워드 필터를 적용해 관련 공고만 반환한다."""
    matched = []
    for item in items:
        name = item.get("pblancNm", "")
        tags = item.get("hashtags", "")
        text = f"{name} {tags}"
        if any(kw in text for kw in KEYWORDS):
            matched.append(item)
    return matched
