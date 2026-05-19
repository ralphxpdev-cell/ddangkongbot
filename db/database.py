import os
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


def _client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def is_first_run():
    """DB에 데이터가 하나도 없으면 첫 실행으로 판단."""
    res = _client().table("notices").select("id", count="exact").execute()
    return (res.count or 0) == 0


def filter_new(items):
    """DB에 없는 새 공고만 반환한다."""
    if not items:
        return []
    ids = [item.get("pblancId", "") for item in items if item.get("pblancId")]
    if not ids:
        return items
    res = _client().table("notices").select("pblanc_id").in_("pblanc_id", ids).execute()
    existing = {row["pblanc_id"] for row in (res.data or [])}
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
            "pblanc_id":       pid,
            "pblanc_nm":       item.get("pblancNm", ""),
            "jrsd_instt_nm":   item.get("jrsdInsttNm", ""),
            "reqst_begin_end_de": item.get("reqstBeginEndDe", ""),
            "pblanc_url":      item.get("pblancUrl", ""),
            "hashtags":        item.get("hashtags", ""),
        })
    if rows:
        _client().table("notices").upsert(rows, on_conflict="pblanc_id").execute()


def get_all_notices():
    """저장된 공고 전체를 dict 리스트로 반환한다."""
    res = _client().table("notices").select("*").order("id", desc=True).execute()
    return res.data or []
