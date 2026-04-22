import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


def is_first_run():
    """DB에 데이터가 하나도 없으면 첫 실행으로 판단."""
    res = _get_client().table("notices").select("pblanc_id", count="exact").limit(1).execute()
    return res.count == 0


def filter_new(items):
    """DB에 없는 새 공고만 반환한다."""
    if not items:
        return []
    ids = [item.get("pblancId", "") for item in items if item.get("pblancId")]
    res = _get_client().table("notices").select("pblanc_id").in_("pblanc_id", ids).execute()
    existing = {row["pblanc_id"] for row in res.data}
    return [item for item in items if item.get("pblancId", "") not in existing]


def save(items):
    """공고 목록을 Supabase에 저장한다."""
    if not items:
        return
    rows = []
    for item in items:
        pid = item.get("pblancId", "")
        if not pid:
            continue
        rows.append({
            "pblanc_id": pid,
            "pblanc_nm": item.get("pblancNm", ""),
            "jrsd_instt_nm": item.get("jrsdInsttNm", ""),
            "reqst_begin_end_de": item.get("reqstBeginEndDe", ""),
            "pblanc_url": item.get("pblancUrl", ""),
            "hashtags": item.get("hashtags", ""),
        })
    if rows:
        _get_client().table("notices").upsert(rows).execute()


def get_all_notices(limit=200):
    """저장된 공고 전체를 최신순으로 반환한다."""
    res = _get_client().table("notices").select("*").order("created_at", desc=True).limit(limit).execute()
    return res.data
