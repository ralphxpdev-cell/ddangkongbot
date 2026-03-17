import sys
import os
import time

sys.path.insert(0, os.path.dirname(__file__))

from api.bizinfo import fetch_notices, filter_notices
from db.database import is_first_run, filter_new, save
from bot.telegram_bot import send_notice, send_error


def run():
    try:
        print("[1/4] API에서 공고 목록 가져오는 중...")
        items = fetch_notices()
        print(f"  → 전체 공고: {len(items)}건")

        print("[2/4] 키워드 필터 적용 중...")
        matched = filter_notices(items)
        print(f"  → 키워드 매칭: {len(matched)}건")

        first_run = is_first_run()
        if first_run:
            print("[!] 첫 실행 감지 — DB 초기화만 수행 (알림 발송 안 함)")

        print("[3/4] 중복 체크 중...")
        new_items = filter_new(matched)
        print(f"  → 신규 공고: {len(new_items)}건")

        save(matched)
        print("[4/4] DB 저장 완료")

        if first_run:
            print(f"  → 첫 실행: {len(matched)}건 DB 저장 완료 (알림 스킵)")
            return

        if not new_items:
            print("  → 새 공고 없음. 종료.")
            return

        print(f"  → {len(new_items)}건 텔레그램 발송 중...")
        for item in new_items:
            send_notice(item)
            time.sleep(0.5)  # 텔레그램 rate limit 방지

        print("완료!")

    except Exception as e:
        error_msg = f"{type(e).__name__}: {e}"
        print(f"[ERROR] {error_msg}")
        send_error(error_msg)
        sys.exit(1)


if __name__ == "__main__":
    run()
