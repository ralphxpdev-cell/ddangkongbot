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
        colors: {
          accent: '#F5A623',
        }
      }
    }
  }
</script>
<style>
  * { word-break: keep-all; }
  .reveal { opacity: 0; transform: translateY(20px); transition: opacity 0.6s cubic-bezier(0.16,1,0.3,1), transform 0.6s cubic-bezier(0.16,1,0.3,1); }
  .reveal.visible { opacity: 1; transform: translateY(0); }
  .card-bezel { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); }
  .card-bezel:hover { background: rgba(255,255,255,0.06); border-color: rgba(245,166,35,0.3); }
  .chip-active { background: rgba(245,166,35,0.15); border-color: rgba(245,166,35,0.5); color: #F5A623; }
  .search-box { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); }
  .search-box:focus-within { border-color: rgba(245,166,35,0.5); background: rgba(255,255,255,0.07); }
  .scrollbar-hide::-webkit-scrollbar { display: none; }
  .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
</style>
</head>
<body class="bg-zinc-950 text-zinc-100 min-h-[100dvh] font-sans antialiased">

<!-- NAV -->
<nav class="fixed top-4 left-1/2 -translate-x-1/2 z-50 flex items-center gap-3 px-5 py-2.5 rounded-full border border-white/10 shadow-[inset_0_1px_0_rgba(255,255,255,0.08)] backdrop-blur-xl" style="background: rgba(24,24,27,0.85);">
  <div class="w-7 h-7 rounded-lg flex items-center justify-center" style="background: rgba(245,166,35,0.15); border: 1px solid rgba(245,166,35,0.3);">
    <iconify-icon icon="solar:radar-2-bold-duotone" style="color:#F5A623; font-size:16px;"></iconify-icon>
  </div>
  <span class="text-sm font-bold tracking-tight">땅콩봇</span>
  <div class="w-px h-4 bg-white/10"></div>
  <span class="text-xs text-zinc-400 font-medium">공고 레이더</span>
</nav>

<!-- HERO -->
<section class="pt-32 pb-10 px-4">
  <div class="max-w-7xl mx-auto">
    <div class="reveal" style="--index:0;">
      <div class="flex items-center gap-2 mb-4">
        <div class="w-1.5 h-1.5 rounded-full bg-accent animate-pulse"></div>
        <span class="text-xs text-zinc-500 font-medium tracking-widest uppercase">bizinfo.go.kr 연동</span>
      </div>
      <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight leading-tight text-zinc-100 mb-3">
        지금 신청 가능한 공고<br>
        <span style="color:#F5A623;">{{ total }}건</span>
      </h1>
      <p class="text-base text-zinc-500 leading-relaxed">창업·청년·농업·소상공인·바우처 키워드 필터 적용</p>
    </div>
  </div>
</section>

<!-- FILTER -->
<section class="px-4 pb-8 sticky top-[4.5rem] z-40" style="background: linear-gradient(to bottom, rgba(9,9,11,0.95) 85%, transparent);">
  <div class="max-w-7xl mx-auto">
    <div class="flex flex-col sm:flex-row gap-3">

      <!-- 검색 -->
      <div class="search-box flex items-center gap-2 px-4 py-3 rounded-xl flex-1 transition-all duration-300">
        <iconify-icon icon="solar:magnifer-linear" class="text-zinc-500 flex-shrink-0" style="font-size:18px;"></iconify-icon>
        <input
          type="text"
          id="searchInput"
          placeholder="공고명, 기관명 검색..."
          oninput="applyFilter()"
          class="bg-transparent outline-none text-sm text-zinc-100 placeholder-zinc-500 w-full"
        >
      </div>

      <!-- 칩 -->
      <div class="flex gap-2 overflow-x-auto scrollbar-hide pb-0.5">
        <button class="chip flex-shrink-0 px-4 py-2.5 rounded-xl text-xs font-semibold border border-white/10 text-zinc-500 transition-all duration-200 hover:border-accent/40 hover:text-zinc-200 chip-active" data-kw="">전체</button>
        <button class="chip flex-shrink-0 px-4 py-2.5 rounded-xl text-xs font-semibold border border-white/10 text-zinc-500 transition-all duration-200 hover:border-accent/40 hover:text-zinc-200" data-kw="창업">창업</button>
        <button class="chip flex-shrink-0 px-4 py-2.5 rounded-xl text-xs font-semibold border border-white/10 text-zinc-500 transition-all duration-200 hover:border-accent/40 hover:text-zinc-200" data-kw="청년">청년</button>
        <button class="chip flex-shrink-0 px-4 py-2.5 rounded-xl text-xs font-semibold border border-white/10 text-zinc-500 transition-all duration-200 hover:border-accent/40 hover:text-zinc-200" data-kw="농업">농업</button>
        <button class="chip flex-shrink-0 px-4 py-2.5 rounded-xl text-xs font-semibold border border-white/10 text-zinc-500 transition-all duration-200 hover:border-accent/40 hover:text-zinc-200" data-kw="소상공인">소상공인</button>
        <button class="chip flex-shrink-0 px-4 py-2.5 rounded-xl text-xs font-semibold border border-white/10 text-zinc-500 transition-all duration-200 hover:border-accent/40 hover:text-zinc-200" data-kw="바우처">바우처</button>
        <button class="chip flex-shrink-0 px-4 py-2.5 rounded-xl text-xs font-semibold border border-white/10 text-zinc-500 transition-all duration-200 hover:border-accent/40 hover:text-zinc-200" data-kw="마케팅">마케팅</button>
      </div>

    </div>
  </div>
</section>

<!-- GRID -->
<section class="px-4 pb-20">
  <div class="max-w-7xl mx-auto">
    <div id="grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">

      {% for n in notices %}
      <div class="card reveal card-bezel rounded-2xl p-6 flex flex-col gap-4 transition-all duration-300 cursor-default"
           style="--index: {{ loop.index0 }};"
           data-title="{{ n.pblanc_nm }}"
           data-org="{{ n.jrsd_instt_nm }}"
           data-tags="{{ n.hashtags }}">

        <!-- 상단 -->
        <div class="flex items-start justify-between gap-2">
          <span class="text-[11px] font-medium text-zinc-400 bg-white/5 border border-white/8 px-2.5 py-1 rounded-lg truncate max-w-[160px]">
            {{ n.jrsd_instt_nm or '기관 미상' }}
          </span>
          <span class="flex-shrink-0 text-[11px] font-bold px-2.5 py-1 rounded-lg
            {% if n.dday_class == 'urgent' %}bg-red-500/10 text-red-400 border border-red-500/20
            {% elif n.dday_class == 'soon' %}bg-orange-500/10 text-orange-400 border border-orange-500/20
            {% elif n.dday_class == 'normal' %}bg-emerald-500/10 text-emerald-400 border border-emerald-500/20
            {% else %}bg-white/5 text-zinc-500 border border-white/8{% endif %}">
            {{ n.dday_label }}
          </span>
        </div>

        <!-- 제목 -->
        <p class="text-base font-semibold text-zinc-100 leading-snug flex-1">{{ n.pblanc_nm }}</p>

        <!-- 날짜 -->
        {% if n.period %}
        <div class="flex items-center gap-1.5 text-xs text-zinc-500">
          <iconify-icon icon="solar:calendar-linear" style="font-size:13px;"></iconify-icon>
          <span>{{ n.period }}</span>
        </div>
        {% endif %}

        <!-- 태그 -->
        {% if n.tags_list %}
        <div class="flex flex-wrap gap-1.5">
          {% for tag in n.tags_list %}
          <span class="text-[11px] font-medium px-2 py-0.5 rounded-md" style="background: rgba(245,166,35,0.1); color: rgba(245,166,35,0.9); border: 1px solid rgba(245,166,35,0.25);"># {{ tag }}</span>
          {% endfor %}
        </div>
        {% endif %}

        <!-- 버튼 -->
        <div class="mt-auto pt-1">
          {% if n.pblanc_url %}
          <a href="{{ n.pblanc_url }}" target="_blank" rel="noopener"
             class="flex items-center justify-center gap-2 w-full py-2.5 rounded-xl text-xs font-semibold transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]"
             style="background: rgba(245,166,35,0.12); border: 1px solid rgba(245,166,35,0.25); color: #F5A623;">
            공고 바로가기
            <iconify-icon icon="solar:arrow-right-up-linear" style="font-size:13px;"></iconify-icon>
          </a>
          {% else %}
          <div class="flex items-center justify-center w-full py-2.5 rounded-xl text-xs font-medium text-zinc-600 border border-white/8">
            링크 없음
          </div>
          {% endif %}
        </div>

      </div>
      {% else %}

      <!-- 빈 상태 -->
      <div class="col-span-full flex flex-col items-center justify-center py-32 gap-4 text-center">
        <div class="w-16 h-16 rounded-2xl flex items-center justify-center card-bezel">
          <iconify-icon icon="solar:inbox-out-linear" class="text-zinc-500" style="font-size:32px;"></iconify-icon>
        </div>
        <div>
          <p class="text-sm font-semibold text-zinc-400">아직 수집된 공고가 없어요</p>
          <p class="text-xs text-zinc-600 mt-1">매일 오전 9시에 자동으로 수집됩니다</p>
        </div>
      </div>

      {% endfor %}
    </div>
  </div>
</section>

<!-- FOOTER -->
<footer class="border-t border-white/5 px-4 py-8">
  <div class="max-w-7xl mx-auto flex items-center justify-between flex-wrap gap-4">
    <div class="flex items-center gap-2">
      <iconify-icon icon="solar:radar-2-bold-duotone" style="color:#F5A623; font-size:16px;"></iconify-icon>
      <span class="text-xs font-bold text-zinc-400">땅콩봇</span>
    </div>
    <p class="text-xs text-zinc-600">bizinfo.go.kr 기준 · 매일 09:00 KST 자동 수집</p>
  </div>
</footer>

<script>
  // 칩 필터
  let activeKw = '';
  document.querySelectorAll('.chip').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.chip').forEach(b => b.classList.remove('chip-active'));
      btn.classList.add('chip-active');
      activeKw = btn.dataset.kw;
      applyFilter();
    });
  });

  function applyFilter() {
    const q = document.getElementById('searchInput').value.toLowerCase();
    document.querySelectorAll('#grid .card').forEach(card => {
      const all = (card.dataset.title + ' ' + card.dataset.org + ' ' + card.dataset.tags).toLowerCase();
      const matchSearch = !q || all.includes(q);
      const matchChip = !activeKw || all.includes(activeKw);
      card.style.display = (matchSearch && matchChip) ? '' : 'none';
    });
  }

  // 스크롤 리빌
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        const idx = parseInt(e.target.style.getPropertyValue('--index')) || 0;
        setTimeout(() => e.target.classList.add('visible'), idx * 60);
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.08 });

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
