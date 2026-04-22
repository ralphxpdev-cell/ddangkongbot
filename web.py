import sys
import os
import re
from flask import Flask, render_template_string, request

sys.path.insert(0, os.path.dirname(__file__))

from db.database import get_all_notices

app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>공고 레이더 — BizRadar</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg:        #F5F6FA;
    --surface:   #FFFFFF;
    --border:    #E4E7EE;
    --primary:   #2E6DF5;
    --primary-light: #EEF3FF;
    --text:      #1A1D27;
    --sub:       #6B7280;
    --tag-bg:    #F0F3FF;
    --tag-text:  #4361C2;
    --dday-red:  #EF4444;
    --dday-orange: #F97316;
    --dday-green:  #22C55E;
    --radius:    12px;
  }

  body {
    font-family: 'Noto Sans KR', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
  }

  /* ── 헤더 ── */
  header {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 0 24px;
    position: sticky;
    top: 0;
    z-index: 100;
  }
  .header-inner {
    max-width: 1200px;
    margin: 0 auto;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .logo {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 18px;
    font-weight: 700;
    color: var(--text);
    text-decoration: none;
  }
  .logo-icon {
    width: 34px; height: 34px;
    background: var(--primary);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
  }
  .badge {
    background: var(--primary-light);
    color: var(--primary);
    font-size: 12px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
  }

  /* ── 메인 ── */
  main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 32px 24px 60px;
  }

  /* ── 히어로 텍스트 ── */
  .hero {
    margin-bottom: 28px;
  }
  .hero h1 {
    font-size: 26px;
    font-weight: 700;
    margin-bottom: 6px;
  }
  .hero p {
    font-size: 14px;
    color: var(--sub);
  }
  .total-count {
    color: var(--primary);
    font-weight: 700;
  }

  /* ── 검색/필터 ── */
  .filter-bar {
    display: flex;
    gap: 10px;
    margin-bottom: 24px;
    flex-wrap: wrap;
  }
  .search-wrap {
    position: relative;
    flex: 1;
    min-width: 220px;
  }
  .search-wrap input {
    width: 100%;
    height: 44px;
    padding: 0 16px 0 42px;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    font-size: 14px;
    font-family: inherit;
    background: var(--surface);
    outline: none;
    transition: border-color .15s;
  }
  .search-wrap input:focus { border-color: var(--primary); }
  .search-icon {
    position: absolute;
    left: 14px; top: 50%;
    transform: translateY(-50%);
    color: var(--sub);
    font-size: 16px;
  }
  .filter-chips {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    align-items: center;
  }
  .chip {
    height: 44px;
    padding: 0 16px;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    font-size: 13px;
    font-family: inherit;
    background: var(--surface);
    color: var(--sub);
    cursor: pointer;
    transition: all .15s;
    white-space: nowrap;
  }
  .chip:hover, .chip.active {
    border-color: var(--primary);
    color: var(--primary);
    background: var(--primary-light);
    font-weight: 600;
  }

  /* ── 그리드 ── */
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 16px;
  }

  /* ── 카드 ── */
  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 22px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    transition: box-shadow .15s, transform .15s;
    cursor: default;
  }
  .card:hover {
    box-shadow: 0 6px 24px rgba(46,109,245,.10);
    transform: translateY(-2px);
  }

  .card-top {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 10px;
  }

  .org-badge {
    font-size: 11px;
    font-weight: 600;
    color: var(--sub);
    background: var(--bg);
    padding: 4px 10px;
    border-radius: 20px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 160px;
  }

  .dday {
    font-size: 11px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 20px;
    white-space: nowrap;
    flex-shrink: 0;
  }
  .dday.urgent  { background: #FEF2F2; color: var(--dday-red); }
  .dday.soon    { background: #FFF7ED; color: var(--dday-orange); }
  .dday.normal  { background: #F0FDF4; color: var(--dday-green); }
  .dday.unknown { background: var(--bg); color: var(--sub); }

  .card-title {
    font-size: 15px;
    font-weight: 700;
    line-height: 1.5;
    color: var(--text);
  }

  .card-meta {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: var(--sub);
  }
  .card-meta span { display: flex; align-items: center; gap: 4px; }

  .tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }
  .tag {
    font-size: 11px;
    font-weight: 500;
    color: var(--tag-text);
    background: var(--tag-bg);
    padding: 3px 9px;
    border-radius: 20px;
  }

  .card-footer {
    margin-top: auto;
    padding-top: 4px;
  }
  .btn-link {
    display: block;
    text-align: center;
    padding: 10px;
    background: var(--primary-light);
    color: var(--primary);
    font-size: 13px;
    font-weight: 600;
    text-decoration: none;
    border-radius: 8px;
    transition: background .15s;
  }
  .btn-link:hover { background: var(--primary); color: #fff; }

  /* ── 빈 상태 ── */
  .empty {
    grid-column: 1 / -1;
    text-align: center;
    padding: 80px 20px;
    color: var(--sub);
  }
  .empty p { font-size: 15px; margin-top: 12px; }

  /* ── 반응형 ── */
  @media (max-width: 600px) {
    main { padding: 20px 16px 40px; }
    .hero h1 { font-size: 20px; }
    .grid { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>

<header>
  <div class="header-inner">
    <a class="logo" href="/">
      <div class="logo-icon">📡</div>
      BizRadar
    </a>
    <span class="badge">공고 레이더</span>
  </div>
</header>

<main>
  <div class="hero">
    <h1>지금 신청 가능한 공고 <span class="total-count">{{ total }}건</span></h1>
    <p>bizinfo.go.kr 기준 · 키워드 필터 적용 공고만 표시</p>
  </div>

  <div class="filter-bar">
    <div class="search-wrap">
      <span class="search-icon">🔍</span>
      <input type="text" id="searchInput" placeholder="공고명, 기관명 검색..." oninput="applyFilter()">
    </div>
    <div class="filter-chips" id="chips">
      <button class="chip active" data-kw="">전체</button>
      <button class="chip" data-kw="창업">창업</button>
      <button class="chip" data-kw="청년">청년</button>
      <button class="chip" data-kw="농업">농업</button>
      <button class="chip" data-kw="소상공인">소상공인</button>
      <button class="chip" data-kw="바우처">바우처</button>
      <button class="chip" data-kw="마케팅">마케팅</button>
    </div>
  </div>

  <div class="grid" id="grid">
    {% for n in notices %}
    <div class="card"
         data-title="{{ n.pblanc_nm }}"
         data-org="{{ n.jrsd_instt_nm }}"
         data-tags="{{ n.hashtags }}">
      <div class="card-top">
        <span class="org-badge">{{ n.jrsd_instt_nm or '기관 미상' }}</span>
        <span class="dday {{ n.dday_class }}">{{ n.dday_label }}</span>
      </div>
      <div class="card-title">{{ n.pblanc_nm }}</div>
      {% if n.reqst_begin_end_de %}
      <div class="card-meta">
        <span>📅 {{ n.period }}</span>
      </div>
      {% endif %}
      {% if n.tags_list %}
      <div class="tags">
        {% for tag in n.tags_list %}
        <span class="tag"># {{ tag }}</span>
        {% endfor %}
      </div>
      {% endif %}
      <div class="card-footer">
        {% if n.pblanc_url %}
        <a class="btn-link" href="{{ n.pblanc_url }}" target="_blank" rel="noopener">공고 바로가기 →</a>
        {% else %}
        <span class="btn-link" style="cursor:default;opacity:.5;">링크 없음</span>
        {% endif %}
      </div>
    </div>
    {% else %}
    <div class="empty">
      <div style="font-size:48px;">📭</div>
      <p>아직 저장된 공고가 없어요.<br>main.py를 먼저 실행해 공고를 수집하세요.</p>
    </div>
    {% endfor %}
  </div>
</main>

<script>
  let activeKw = '';

  document.querySelectorAll('#chips .chip').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('#chips .chip').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeKw = btn.dataset.kw;
      applyFilter();
    });
  });

  function applyFilter() {
    const q = document.getElementById('searchInput').value.toLowerCase();
    document.querySelectorAll('#grid .card').forEach(card => {
      const title = card.dataset.title.toLowerCase();
      const org   = card.dataset.org.toLowerCase();
      const tags  = card.dataset.tags.toLowerCase();
      const all   = title + ' ' + org + ' ' + tags;

      const matchSearch = !q || all.includes(q);
      const matchChip   = !activeKw || all.includes(activeKw);
      card.style.display = (matchSearch && matchChip) ? '' : 'none';
    });
  }
</script>
</body>
</html>"""


def _format_date(raw):
    if not raw:
        return ""
    def conv(m):
        d = m.group(0)
        return f"{d[:4]}.{d[4:6]}.{d[6:8]}"
    return re.sub(r"\d{8}", conv, raw)


def _dday(raw):
    """마감일 기준 D-day 계산. raw = '20240101 ~ 20240331'"""
    if not raw:
        return "unknown", "기간 미상"
    dates = re.findall(r"\d{8}", raw)
    if len(dates) < 2:
        return "unknown", "기간 미상"
    from datetime import date
    end_str = dates[1]
    try:
        end = date(int(end_str[:4]), int(end_str[4:6]), int(end_str[6:8]))
        diff = (end - date.today()).days
        if diff < 0:
            return "unknown", "마감"
        elif diff == 0:
            return "urgent", "D-Day"
        elif diff <= 7:
            return "urgent", f"D-{diff}"
        elif diff <= 30:
            return "soon", f"D-{diff}"
        else:
            return "normal", f"D-{diff}"
    except ValueError:
        return "unknown", "기간 미상"


def _tags(raw):
    if not raw:
        return []
    return [t.strip() for t in raw.replace("#", "").split(",") if t.strip()][:6]


@app.route("/")
def index():
    rows = get_all_notices()
    for r in rows:
        r["period"] = _format_date(r.get("reqst_begin_end_de", ""))
        r["dday_class"], r["dday_label"] = _dday(r.get("reqst_begin_end_de", ""))
        r["tags_list"] = _tags(r.get("hashtags", ""))
    return render_template_string(HTML, notices=rows, total=len(rows))


if __name__ == "__main__":
    app.run(debug=True, port=5050)
