import sys
import os
import re
from flask import Flask, render_template_string

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
  .reveal { opacity: 0; transform: translateY(12px); transition: opacity 0.45s cubic-bezier(0.16,1,0.3,1), transform 0.45s cubic-bezier(0.16,1,0.3,1); }
  .reveal.visible { opacity: 1; transform: translateY(0); }
</style>
</head>
<body class="bg-gray-50 text-gray-900 min-h-[100dvh] font-sans antialiased">

<!-- NAV -->
<header class="sticky top-0 z-50 bg-white border-b border-gray-200">
  <div class="max-w-4xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
    <div class="flex items-center gap-2">
      <div class="w-7 h-7 rounded-lg bg-amber-400 flex items-center justify-center">
        <iconify-icon icon="solar:radar-2-bold" style="color:#fff; font-size:15px;"></iconify-icon>
      </div>
      <span class="font-bold text-gray-900 text-sm">땅콩봇</span>
    </div>
    <span class="text-xs text-gray-400">매일 09:00 자동 수집</span>
  </div>
</header>

<!-- HERO -->
<section class="max-w-4xl mx-auto px-4 sm:px-6 pt-10 pb-6 reveal" style="--index:0;">
  <h1 class="text-3xl md:text-4xl font-bold text-gray-900 leading-tight mb-2">
    지금 신청 가능한 공고 <span class="text-amber-500">{{ total }}건</span>
  </h1>
  <p class="text-sm text-gray-500">창업 · 청년 · 농업 · 소상공인 · 바우처 키워드 필터 적용</p>
</section>

<!-- FILTER -->
<div class="sticky top-14 z-40 bg-gray-50 border-b border-gray-200">
  <div class="max-w-4xl mx-auto px-4 sm:px-6 py-3 flex flex-col sm:flex-row gap-2">

    <!-- 검색 -->
    <div class="flex items-center gap-2 bg-white border border-gray-200 rounded-xl px-3 py-2.5 flex-1 focus-within:border-amber-400 transition-colors duration-150">
      <iconify-icon icon="solar:magnifer-linear" style="color:#9ca3af; font-size:16px; flex-shrink:0;"></iconify-icon>
      <input type="text" id="searchInput" placeholder="공고명, 기관명 검색..." oninput="applyFilter()"
        class="bg-transparent outline-none text-sm text-gray-800 placeholder-gray-400 w-full">
    </div>

    <!-- 칩 -->
    <div class="flex gap-1.5 overflow-x-auto pb-0.5" style="-ms-overflow-style:none; scrollbar-width:none;">
      <button class="chip flex-shrink-0 text-xs font-semibold px-3.5 py-2 rounded-lg border border-gray-200 bg-white text-gray-600 hover:border-gray-300 transition-all duration-150 whitespace-nowrap" data-kw="">전체</button>
      <button class="chip flex-shrink-0 text-xs font-semibold px-3.5 py-2 rounded-lg border border-gray-200 bg-white text-gray-600 hover:border-gray-300 transition-all duration-150 whitespace-nowrap" data-kw="창업">창업</button>
      <button class="chip flex-shrink-0 text-xs font-semibold px-3.5 py-2 rounded-lg border border-gray-200 bg-white text-gray-600 hover:border-gray-300 transition-all duration-150 whitespace-nowrap" data-kw="청년">청년</button>
      <button class="chip flex-shrink-0 text-xs font-semibold px-3.5 py-2 rounded-lg border border-gray-200 bg-white text-gray-600 hover:border-gray-300 transition-all duration-150 whitespace-nowrap" data-kw="농업">농업</button>
      <button class="chip flex-shrink-0 text-xs font-semibold px-3.5 py-2 rounded-lg border border-gray-200 bg-white text-gray-600 hover:border-gray-300 transition-all duration-150 whitespace-nowrap" data-kw="소상공인">소상공인</button>
      <button class="chip flex-shrink-0 text-xs font-semibold px-3.5 py-2 rounded-lg border border-gray-200 bg-white text-gray-600 hover:border-gray-300 transition-all duration-150 whitespace-nowrap" data-kw="바우처">바우처</button>
      <button class="chip flex-shrink-0 text-xs font-semibold px-3.5 py-2 rounded-lg border border-gray-200 bg-white text-gray-600 hover:border-gray-300 transition-all duration-150 whitespace-nowrap" data-kw="마케팅">마케팅</button>
    </div>

  </div>
</div>

<!-- LIST -->
<section class="max-w-4xl mx-auto px-4 sm:px-6 py-6 pb-24">
  <div id="grid" class="flex flex-col gap-3">

    {% for n in notices %}
    <div class="card reveal bg-white rounded-2xl overflow-hidden flex transition-all duration-150 hover:bg-gray-50"
         style="border: 1.5px solid #e9e9e9; box-shadow: 0 4px 20px rgba(0,0,0,0.08);"
         style="--index: {{ loop.index0 }};"
         data-title="{{ n.pblanc_nm }}"
         data-org="{{ n.jrsd_instt_nm }}"
         data-tags="{{ n.hashtags }}">

      <!-- 긴급도 색상 바 (좌측) -->
      <div class="w-1 flex-shrink-0
        {% if n.dday_class == 'urgent' %}bg-red-400
        {% elif n.dday_class == 'soon' %}bg-orange-400
        {% elif n.dday_class == 'normal' %}bg-emerald-400
        {% else %}bg-gray-200{% endif %}">
      </div>

      <!-- 본문 -->
      <div class="flex-1 px-5 py-4 flex flex-col sm:flex-row sm:items-center gap-3">

        <!-- 좌: 텍스트 정보 -->
        <div class="flex-1 min-w-0 flex flex-col gap-2">

          <!-- 기관 + D-day -->
          <div class="flex items-center gap-2 flex-wrap">
            <span class="text-xs text-gray-400 font-medium">{{ n.jrsd_instt_nm or '기관 미상' }}</span>
            <span class="text-xs font-bold px-2 py-0.5 rounded-md
              {% if n.dday_class == 'urgent' %}bg-red-50 text-red-500
              {% elif n.dday_class == 'soon' %}bg-orange-50 text-orange-500
              {% elif n.dday_class == 'normal' %}bg-emerald-50 text-emerald-600
              {% else %}bg-gray-100 text-gray-400{% endif %}">
              {{ n.dday_label }}
            </span>
          </div>

          <!-- 제목 -->
          <p class="text-base font-semibold text-gray-900 leading-snug">{{ n.pblanc_nm }}</p>

          <!-- 날짜 + 태그 -->
          <div class="flex flex-wrap items-center gap-2">
            {% if n.period %}
            <span class="text-xs text-gray-400 flex items-center gap-1">
              <iconify-icon icon="solar:calendar-minimalistic-linear" style="font-size:12px;"></iconify-icon>
              {{ n.period }}
            </span>
            {% endif %}
            {% for tag in n.tags_list %}
            <span class="text-xs font-medium px-2 py-0.5 rounded-md bg-gray-100 text-gray-600">{{ tag }}</span>
            {% endfor %}
          </div>

        </div>

        <!-- 우: 버튼 -->
        {% if n.pblanc_url %}
        <a href="{{ n.pblanc_url }}" target="_blank" rel="noopener"
           class="flex-shrink-0 flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-amber-400 hover:bg-amber-500 active:scale-95 text-white font-bold text-sm transition-all duration-150 whitespace-nowrap">
          바로가기
          <iconify-icon icon="solar:arrow-right-up-linear" style="font-size:14px;"></iconify-icon>
        </a>
        {% endif %}

      </div>
    </div>
    {% else %}

    <div class="py-32 flex flex-col items-center gap-3 text-center">
      <iconify-icon icon="solar:inbox-out-linear" style="font-size:44px; color:#d1d5db;"></iconify-icon>
      <p class="text-gray-500 font-medium">아직 수집된 공고가 없어요</p>
      <p class="text-sm text-gray-400">매일 오전 9시에 자동으로 수집됩니다</p>
    </div>

    {% endfor %}
  </div>
</section>

<!-- FOOTER -->
<footer class="border-t border-gray-200 bg-white px-4 sm:px-6 py-6">
  <div class="max-w-4xl mx-auto flex items-center justify-between flex-wrap gap-3">
    <div class="flex items-center gap-2">
      <div class="w-5 h-5 rounded bg-amber-400 flex items-center justify-center">
        <iconify-icon icon="solar:radar-2-bold" style="color:#fff; font-size:11px;"></iconify-icon>
      </div>
      <span class="text-sm font-bold text-gray-700">땅콩봇</span>
    </div>
    <p class="text-xs text-gray-400">bizinfo.go.kr 기준 · 매일 09:00 KST 자동 수집</p>
  </div>
</footer>

<script>
  let activeKw = '';

  document.querySelectorAll('.chip').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.chip').forEach(b => {
        b.classList.remove('bg-amber-400', 'text-white', 'border-amber-400');
        b.classList.add('bg-white', 'text-gray-600', 'border-gray-200');
      });
      btn.classList.remove('bg-white', 'text-gray-600', 'border-gray-200');
      btn.classList.add('bg-amber-400', 'text-white', 'border-amber-400');
      activeKw = btn.dataset.kw;
      applyFilter();
    });
  });

  // 첫 번째 칩(전체) 기본 활성
  document.querySelector('.chip').classList.remove('bg-white', 'text-gray-600', 'border-gray-200');
  document.querySelector('.chip').classList.add('bg-amber-400', 'text-white', 'border-amber-400');

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
        setTimeout(() => e.target.classList.add('visible'), Math.min(idx, 10) * 40);
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.04 });

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
