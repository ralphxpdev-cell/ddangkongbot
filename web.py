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
<title>땅콩봇 — 국가사업 공고 레이더</title>
<script src="https://cdn.tailwindcss.com"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.min.css">
<script src="https://code.iconify.design/iconify-icon/2.3.0/iconify-icon.min.js"></script>
<script>
  tailwind.config = {
    theme: {
      extend: {
        fontFamily: { sans: ['Pretendard', 'system-ui', 'sans-serif'] },
      }
    }
  }
</script>
<style>
  * { word-break: keep-all; }

  .reveal {
    opacity: 0;
    transform: translateY(16px);
    transition: opacity 0.5s cubic-bezier(0.16,1,0.3,1), transform 0.5s cubic-bezier(0.16,1,0.3,1);
  }
  .reveal.visible { opacity: 1; transform: translateY(0); }

  .card {
    background: #18181b;
    border: 1px solid #27272a;
    transition: border-color 0.2s, background 0.2s;
  }
  .card:hover {
    border-color: #3f3f46;
    background: #1c1c1f;
  }

  .tag-chip {
    background: #27272a;
    color: #d4d4d8;
    border: 1px solid #3f3f46;
  }

  .btn-link {
    background: #fbbf24;
    color: #0a0a0a;
    font-weight: 700;
    transition: background 0.2s, transform 0.15s;
  }
  .btn-link:hover { background: #f59e0b; transform: translateY(-1px); }
  .btn-link:active { transform: scale(0.98); }

  .search-wrap {
    background: #18181b;
    border: 1px solid #27272a;
    transition: border-color 0.2s;
  }
  .search-wrap:focus-within { border-color: #fbbf24; }

  .chip {
    background: #18181b;
    border: 1px solid #27272a;
    color: #a1a1aa;
    transition: all 0.15s;
  }
  .chip:hover { border-color: #52525b; color: #e4e4e7; }
  .chip.active {
    background: #fbbf24;
    border-color: #fbbf24;
    color: #0a0a0a;
    font-weight: 700;
  }

  .scrollbar-hide::-webkit-scrollbar { display: none; }
  .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
</style>
</head>
<body class="bg-zinc-950 text-zinc-100 min-h-[100dvh] font-sans antialiased">

<!-- NAV -->
<nav class="fixed top-4 left-1/2 -translate-x-1/2 z-50 flex items-center gap-3 px-5 py-2.5 rounded-full border border-zinc-800 backdrop-blur-xl" style="background: rgba(9,9,11,0.9);">
  <div class="w-6 h-6 rounded-md flex items-center justify-center bg-amber-400">
    <iconify-icon icon="solar:radar-2-bold" style="color:#0a0a0a; font-size:14px;"></iconify-icon>
  </div>
  <span class="text-sm font-bold text-zinc-100">땅콩봇</span>
  <span class="text-zinc-700">·</span>
  <span class="text-xs text-zinc-500">공고 레이더</span>
</nav>

<!-- HERO -->
<section class="pt-32 pb-8 px-4 sm:px-6">
  <div class="max-w-5xl mx-auto reveal" style="--index:0;">
    <div class="flex items-center gap-2 mb-5">
      <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse inline-block"></span>
      <span class="text-xs text-zinc-500 font-medium tracking-wider uppercase">실시간 연동 중</span>
    </div>
    <h1 class="text-5xl md:text-6xl font-bold tracking-tight leading-tight text-zinc-100 mb-4">
      신청 가능한 공고<br><span class="text-amber-400">{{ total }}건</span>
    </h1>
    <p class="text-zinc-500 text-lg">창업 · 청년 · 농업 · 소상공인 · 바우처 키워드 자동 수집</p>
  </div>
</section>

<!-- FILTER -->
<div class="sticky top-[4.5rem] z-40 px-4 sm:px-6 pb-6 pt-2" style="background: linear-gradient(to bottom, #09090b 80%, transparent);">
  <div class="max-w-5xl mx-auto flex flex-col sm:flex-row gap-3">

    <div class="search-wrap flex items-center gap-3 px-4 py-3 rounded-2xl flex-1">
      <iconify-icon icon="solar:magnifer-linear" style="color:#71717a; font-size:18px; flex-shrink:0;"></iconify-icon>
      <input type="text" id="searchInput" placeholder="공고명, 기관명으로 검색..." oninput="applyFilter()"
        class="bg-transparent outline-none text-sm text-zinc-100 placeholder-zinc-600 w-full">
    </div>

    <div class="flex gap-2 overflow-x-auto scrollbar-hide">
      <button class="chip flex-shrink-0 text-xs px-4 py-2.5 rounded-xl active" data-kw="">전체</button>
      <button class="chip flex-shrink-0 text-xs px-4 py-2.5 rounded-xl" data-kw="창업">창업</button>
      <button class="chip flex-shrink-0 text-xs px-4 py-2.5 rounded-xl" data-kw="청년">청년</button>
      <button class="chip flex-shrink-0 text-xs px-4 py-2.5 rounded-xl" data-kw="농업">농업</button>
      <button class="chip flex-shrink-0 text-xs px-4 py-2.5 rounded-xl" data-kw="소상공인">소상공인</button>
      <button class="chip flex-shrink-0 text-xs px-4 py-2.5 rounded-xl" data-kw="바우처">바우처</button>
      <button class="chip flex-shrink-0 text-xs px-4 py-2.5 rounded-xl" data-kw="마케팅">마케팅</button>
    </div>

  </div>
</div>

<!-- GRID -->
<section class="px-4 sm:px-6 pb-24">
  <div class="max-w-5xl mx-auto">
    <div id="grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">

      {% for n in notices %}
      <div class="card reveal rounded-2xl flex flex-col"
           style="--index: {{ loop.index0 }};"
           data-title="{{ n.pblanc_nm }}"
           data-org="{{ n.jrsd_instt_nm }}"
           data-tags="{{ n.hashtags }}">

        <!-- 카드 상단: 기관 + D-day -->
        <div class="px-5 pt-5 pb-4 flex items-center justify-between gap-2 border-b border-zinc-800">
          <span class="text-xs text-zinc-500 truncate max-w-[180px]">{{ n.jrsd_instt_nm or '기관 미상' }}</span>
          <span class="flex-shrink-0 text-xs font-bold px-2.5 py-1 rounded-lg
            {% if n.dday_class == 'urgent' %}bg-red-950 text-red-400
            {% elif n.dday_class == 'soon' %}bg-orange-950 text-orange-400
            {% elif n.dday_class == 'normal' %}bg-emerald-950 text-emerald-400
            {% else %}bg-zinc-800 text-zinc-500{% endif %}">
            {{ n.dday_label }}
          </span>
        </div>

        <!-- 카드 본문: 제목 + 날짜 -->
        <div class="px-5 py-4 flex-1 flex flex-col gap-3">
          <p class="text-base font-semibold text-zinc-100 leading-snug">{{ n.pblanc_nm }}</p>

          {% if n.period %}
          <div class="flex items-center gap-1.5">
            <iconify-icon icon="solar:calendar-minimalistic-linear" style="color:#52525b; font-size:13px;"></iconify-icon>
            <span class="text-xs text-zinc-500">{{ n.period }}</span>
          </div>
          {% endif %}

          {% if n.tags_list %}
          <div class="flex flex-wrap gap-1.5 mt-1">
            {% for tag in n.tags_list %}
            <span class="tag-chip text-xs px-2.5 py-1 rounded-lg font-medium">{{ tag }}</span>
            {% endfor %}
          </div>
          {% endif %}
        </div>

        <!-- 카드 하단: 버튼 -->
        <div class="px-5 pb-5">
          {% if n.pblanc_url %}
          <a href="{{ n.pblanc_url }}" target="_blank" rel="noopener"
             class="btn-link flex items-center justify-center gap-2 w-full py-3 rounded-xl text-sm">
            공고 바로가기
            <iconify-icon icon="solar:arrow-right-up-linear" style="font-size:14px;"></iconify-icon>
          </a>
          {% else %}
          <div class="flex items-center justify-center w-full py-3 rounded-xl text-xs text-zinc-600 bg-zinc-900">
            링크 없음
          </div>
          {% endif %}
        </div>

      </div>
      {% else %}

      <div class="col-span-full py-40 flex flex-col items-center gap-4 text-center">
        <iconify-icon icon="solar:inbox-out-linear" style="font-size:48px; color:#3f3f46;"></iconify-icon>
        <p class="text-zinc-500 font-medium">아직 수집된 공고가 없어요</p>
        <p class="text-sm text-zinc-700">매일 오전 9시에 자동으로 수집됩니다</p>
      </div>

      {% endfor %}
    </div>
  </div>
</section>

<!-- FOOTER -->
<footer class="border-t border-zinc-900 px-4 sm:px-6 py-8">
  <div class="max-w-5xl mx-auto flex items-center justify-between flex-wrap gap-3">
    <div class="flex items-center gap-2">
      <div class="w-5 h-5 rounded bg-amber-400 flex items-center justify-center">
        <iconify-icon icon="solar:radar-2-bold" style="color:#0a0a0a; font-size:11px;"></iconify-icon>
      </div>
      <span class="text-sm font-bold text-zinc-400">땅콩봇</span>
    </div>
    <p class="text-xs text-zinc-700">bizinfo.go.kr 기준 · 매일 09:00 KST 자동 수집</p>
  </div>
</footer>

<script>
  let activeKw = '';

  document.querySelectorAll('.chip').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.chip').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeKw = btn.dataset.kw;
      applyFilter();
    });
  });

  function applyFilter() {
    const q = document.getElementById('searchInput').value.toLowerCase();
    document.querySelectorAll('#grid .card').forEach(card => {
      const all = (card.dataset.title + ' ' + card.dataset.org + ' ' + card.dataset.tags).toLowerCase();
      card.style.display = (!q || all.includes(q)) && (!activeKw || all.includes(activeKw)) ? '' : 'none';
    });
  }

  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        const idx = parseInt(e.target.style.getPropertyValue('--index')) || 0;
        setTimeout(() => e.target.classList.add('visible'), Math.min(idx, 8) * 50);
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.05 });

  document.querySelectorAll('.reveal').forEach(el => io.observe(el));
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
    return [t.strip() for t in raw.replace("#", "").split(",") if t.strip()][:5]


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
