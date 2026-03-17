# BizRadar — 국가사업 공고 텔레그램 알리미

기업지원플러스(bizinfo.go.kr) API에서 공고를 수집하고, 키워드 필터를 적용해 텔레그램으로 알림을 보냅니다.

## 키워드 필터

`창업`, `농식품`, `귀농`, `바우처`, `보조금`, `소상공인`, `청년`

공고명 또는 해시태그에 위 키워드가 포함되면 알림을 발송합니다.

## 설치 방법

```bash
cd bizradar
pip install -r requirements.txt
cp .env.example .env
# .env 파일에 API 키, 텔레그램 봇 토큰, 채팅 ID 입력
```

## 로컬 실행

```bash
python main.py
```

첫 실행 시 기존 공고는 DB에만 저장되고 알림은 발송되지 않습니다 (중복 폭탄 방지).

## GitHub Actions 설정

1. GitHub 저장소 생성
2. Settings → Secrets and variables → Actions에서 다음 시크릿 추가:
   - `BIZINFO_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
3. 매일 오전 9시(KST) 자동 실행됩니다
4. Actions 탭에서 수동 실행도 가능합니다 (Run workflow)

## 파일 구조

```
bizradar/
├── main.py              # 메인 실행 파일
├── config.py            # 환경변수 설정
├── api/
│   └── bizinfo.py       # API 호출 + 키워드 필터
├── db/
│   └── database.py      # SQLite 중복 체크
├── bot/
│   └── telegram_bot.py  # 텔레그램 메시지 발송
├── .env                 # 환경변수 (gitignore)
├── .env.example         # 환경변수 예시
├── requirements.txt     # 의존성
└── .github/workflows/
    └── scheduler.yml    # GitHub Actions 스케줄러
```
