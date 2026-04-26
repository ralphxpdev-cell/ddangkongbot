import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "notices.db")


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notices (
            pblanc_id TEXT PRIMARY KEY,
            pblanc_nm TEXT,
            jrsd_instt_nm TEXT,
            reqst_begin_end_de TEXT,
            pblanc_url TEXT,
            hashtags TEXT
        )
    """)
    conn.commit()
    return conn


def is_first_run():
    """DB에 데이터가 하나도 없으면 첫 실행으로 판단."""
    with _get_conn() as conn:
        row = conn.execute("SELECT COUNT(*) FROM notices").fetchone()
        return row[0] == 0


def filter_new(items):
    """DB에 없는 새 공고만 반환한다."""
    if not items:
        return []
    ids = [item.get("pblancId", "") for item in items if item.get("pblancId")]
    with _get_conn() as conn:
        placeholders = ",".join("?" * len(ids))
        rows = conn.execute(
            f"SELECT pblanc_id FROM notices WHERE pblanc_id IN ({placeholders})", ids
        ).fetchall()
    existing = {row[0] for row in rows}
    return [item for item in items if item.get("pblancId", "") not in existing]


def save(items):
    """공고 목록을 SQLite에 저장한다."""
    if not items:
        return
    rows = []
    for item in items:
        pid = item.get("pblancId", "")
        if not pid:
            continue
        rows.append((
            pid,
            item.get("pblancNm", ""),
            item.get("jrsdInsttNm", ""),
            item.get("reqstBeginEndDe", ""),
            item.get("pblancUrl", ""),
            item.get("hashtags", ""),
        ))
    if rows:
        with _get_conn() as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO notices VALUES (?,?,?,?,?,?)", rows
            )
            conn.commit()
