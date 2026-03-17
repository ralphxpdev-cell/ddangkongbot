import sqlite3
import os
from config import DB_PATH


def _get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS notices (
            pblanc_id TEXT PRIMARY KEY,
            pblanc_nm TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    conn.commit()
    return conn


def is_first_run():
    """DB에 데이터가 하나도 없으면 첫 실행으로 판단."""
    conn = _get_conn()
    count = conn.execute("SELECT COUNT(*) FROM notices").fetchone()[0]
    conn.close()
    return count == 0


def filter_new(items):
    """DB에 없는 새 공고만 반환한다."""
    conn = _get_conn()
    new_items = []
    for item in items:
        pid = item.get("pblancId", "")
        if not pid:
            continue
        exists = conn.execute(
            "SELECT 1 FROM notices WHERE pblanc_id = ?", (pid,)
        ).fetchone()
        if not exists:
            new_items.append(item)
    conn.close()
    return new_items


def save(items):
    """공고 목록을 DB에 저장한다."""
    conn = _get_conn()
    for item in items:
        pid = item.get("pblancId", "")
        name = item.get("pblancNm", "")
        if not pid:
            continue
        conn.execute(
            "INSERT OR IGNORE INTO notices (pblanc_id, pblanc_nm) VALUES (?, ?)",
            (pid, name),
        )
    conn.commit()
    conn.close()
