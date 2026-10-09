#!/usr/bin/env python3
"""블루 리포트 라이브 덱 점검기 — 고정 지면이 없는 발표 덱이다.

    python3 check_live.py live-standard.html
    python3 check_live.py live-standard.html --shots out/

check_deck.py 를 그대로 쓸 수 없다. 저쪽은 1920x1080 고정 지면과 24px 하한을
본다. 라이브 계통은 한 장이 100dvh 이고 치수가 전부 rem 이라 px 하한이라는
개념 자체가 없다 — 루트 글자 크기가 뷰포트를 따라 움직이기 때문이다.

판정이 겹치는 것(문체·raw hex·마크 대비)은 check_deck.py 에서 불러 쓴다.
같은 낱말을 두 스크립트가 다르게 판정하는 일이 없도록 한 곳에만 둔다.

검사 항목 (27)
  정적 — HTML 원문만 본다. Playwright 없이도 돈다.
    1. 문체 — 존댓말·평서형 종결 없이 명사형인가 (check_deck.py 규칙 재사용)
    2. 색 — 토큰 밖 raw hex 를 본문에 직접 쓰지 않았는가
    3. blue-report.css 와 blue-live.css 를 함께 불렀는가
    4. 리터럴 px 치수가 없는가 — 이 계통은 rem 으로만 말한다
       px 로 적으면 루트 글자 크기를 따라가지 않아 창이 작아질 때 그 값만 남는다.
       테두리 1px 와 미디어 질의 분기점은 예외다
    5. 장마다 data-notes 가 있는가 — 발표자 노트 없는 장은 대본 창이 빈다
    6~10. 지면 크롬 — 머리띠 · 꼬리띠 · 쪽번호 · 머리띠 브랜드 마크 · 워터마크가 장마다 있는가
   11. 마크 배경 짝 — data-on 이 마크가 앉는 면과 맞는가 (머리띠 마크는 지면과 반대)
   12. 브랜드 자리 — 산출물에 「COMPANY NAME」이 남지 않았는가 (assets/ 견본만 예외)
   13. 출처 칩 — .bl-ev 의 키(쉼표로 여럿)가 #bl-evidence 근거에 있고 근거마다 제목·등급·출처가
       있는가. 캡처(imgs)·하이라이트 상자(hl)·원문(doc)이 가리키는 것도 실제로 있는가
  렌더 — 실제 브라우저 레이아웃. Playwright 가 필요하다.
   14. 스타일 — 계통 CSS 토큰이 렌더에서 살아 있는가
   15. 본문 폰트 — Pretendard FontFace 가 실제로 로드됐는가
   16. 지면 — 화면 좌우 끝까지 닿는가 (body 기본 여백 8px)
   17. 조작판 — 1600·760·400px 에서 장마다 꼬리띠 글자(문서명·쪽번호)를 덮지 않는가
   18. 절대 하한(0.78rem) 미만 글자가 없는가
   19. 본문 계열이 본문 하한(1.0rem) 이상인가 — 주석 계열만 그 아래를 허용한다
   20. 16:9 · 좁은 폭 · 휴대폰 폭 세 경우에서 가로로 넘치지 않는가
   21. 데이터 마크가 실제 뒷배경 대비 2:1 이상인가 (채움 마크만)
   22. 문체 — **그려진 뒤의** 본문까지 개조식인가
   23. 스크립트 — 뷰어 엔진이 떠 있고 부품이 예외 없이 시작하는가 (세 폭 모두)
       live-viewer.js 를 부르는 덱인데 window.blDeck 이 없으면 실패다. 연결형 산출물에서
       JS 를 옆에 복사하지 않으면 지면은 멀쩡히 그려지고 넘김·발표·근거가 전부 죽는다
  정적 — 블라인드 제작 시험(스킬 문서만 받은 에이전트)이 검사기 밖에서 찾은 결함들
   24. 단계 — 장마다 노트의 [클릭] 이 단계(data-f 값 가짓수)보다 적지 않은가.
       적으면 대본 창 배지가 단계와 어긋나 발표자가 지금 몇 번째인지 잃는다
   25. 클래스 — bl-·br- 클래스가 전부 CSS 나 뷰어에 있는가. 지어낸 클래스는 아무
       일도 하지 않는다 — 화면은 멀쩡해 보여 눈으로는 모른다
  렌더
   26. 보이지 않는 글자 — 글자색과 실제 뒷배경 대비가 1.25:1 미만인 글자가 없는가.
       카드형 수치 타일 안의 강조 칸이 흰 바탕 흰 글자로 사라진 일이 있었다
   27. 세로 넘침 — 16:9 화면에서 장마다 본문이 꼬리띠 위에서 끝나는가. 지면은 한 화면
       높이에 overflow:hidden 이라 넘친 줄은 잘려 사라진다. 900px 이하 읽기 폭(장이 내용만큼
       늘어난다)에서는 꼬리띠가 장 안에 있고 본문이 그 위에서 끝나는가

왜 rem 으로 판정하는가
  px 로 재면 창 크기에 따라 결과가 달라져 같은 파일이 통과했다 떨어졌다 한다.
  루트 글자 크기로 나눠 rem 으로 되돌린 뒤 판정하면 창과 무관하게 같은 답이다.

종료 코드는 실패가 하나라도 있으면 1, 아니면 0 이다.
"""
import argparse
import json
import os
import re
import sys
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from palette import contrast, MIN_DATA_CONTRAST  # noqa: E402
from ensure_deps import need_browser  # noqa: E402
from check_deck import (  # noqa: E402
    Report, style_violations, ALLOWED_HEX, _blank, _rgb_to_hex,
    check_brand, check_style_applied, sentinels, STYLE_PROBE,
)

MIN_REM = 0.78     # 절대 하한. 무엇도 이보다 작게 쓰지 않는다
BODY_REM = 1.0     # 본문 하한. 주석 계열만 이 아래를 허용한다
# 주석·라벨 계열. 이 클래스를 단 요소는 BODY_REM 아래여도 된다.
NOTE_CLS = ("bl-note", "bl-src", "bl-chip", "bl-eyebrow", "bl-stat-t", "bl-rf",
            "bl-ord", "bl-code", "bl-pg", "bl-ev",
            # 라이브 부품(1.44.0) — 라벨 · 칩 · 축 · 칸 안 값처럼 본문이 아닌 글자만.
            # 본문을 담는 그릇(카드 · 행)은 넣지 않는다 — 넣으면 그 안 본문까지 하한이 풀린다.
            "bl-lbl", "bl-cap", "bl-mini", "bl-axis", "bl-dl", "bl-leg", "bl-num", "bl-pill",
            "bl-badge", "bl-delta", "bl-asof", "bl-pgref", "bl-stamp", "bl-conf", "bl-seg",
            "bl-fig-ab", "bl-replay", "bl-shot-open", "bl-route-st", "bl-sc-pick")
# 16:9 한 벌, 좁은 폭 한 벌, 휴대폰 폭 한 벌. 좁은 쪽 둘은 루트가 하한(10.5px)에
# 걸리는 구간이다 — 글자는 그대로고 가로 자리만 줄어 겹침·넘침이 여기서 난다.
VIEWS = [(1600, 900), (760, 900), (400, 800)]


# 지면이 화면 좌우 끝까지 닿는가. 브라우저 기본 body 여백(8px)이 살아 있으면
# 머리띠·꼬리띠가 끝에 닿지 않고 흰 틈이 테두리처럼 남는다 — 실제로 그랬다.
EDGE_PROBE = r"""() => {
  const s = document.querySelector('.bl-sl');
  if (!s) return {left: 0, right: 0, gap: 0};
  const r = s.getBoundingClientRect();
  const left = Math.round(r.left), right = Math.round(innerWidth - r.right);
  return {left, right, gap: Math.max(left, right)};
}"""


# 떠 있는 조작판이 꼬리띠 글자(문서명 · 쪽번호)를 덮는가. 조작판 단추를 넷에서
# 여덟로 늘리자 400px 에서 둘 다 덮었다 — 겹침은 넘침이 아니라 가로 넘침 검사가
# 못 잡는다. 글자의 실제 폭(Range)으로 잰다. 요소 상자는 띠 폭만큼 늘어날 수 있다.
# 장마다 잰다 — 쪽번호 폭과 꼬리띠는 장마다 다를 수 있다. 조작판은 화면 아래에 붙어
# 있고 꼬리띠는 장 아래 끝에 있으니, 장의 아래 끝을 화면 아래 끝에 맞춘 자리로 옮겨
# 잰다(좁은 폭에서 화면보다 긴 장도 끝까지 내리면 그 자리에서 만난다).
HUD_PROBE = r"""() => {
  const hud = document.querySelector('.bl-hud');
  if (!hud || getComputedStyle(hud).display === 'none') return [];
  const a = hud.getBoundingClientRect(), hit = [];
  document.querySelectorAll('.bl-sl').forEach((s, i) => {
    const dy = innerHeight - s.getBoundingClientRect().bottom;
    s.querySelectorAll('.bl-rf-name, .bl-pg').forEach(el => {
      const r = document.createRange(); r.selectNodeContents(el);
      const b = r.getBoundingClientRect();
      // 말줄임으로 잘린 글자는 글자 폭(Range)이 상자 밖까지 잡힌다. 보이는 부분만 잰다
      let L = b.left, R = b.right;
      if (getComputedStyle(el).overflowX !== 'visible') {
        const e = el.getBoundingClientRect(); L = Math.max(L, e.left); R = Math.min(R, e.right);
      }
      const T = b.top + dy, B = b.bottom + dy;
      if (R - L > 0 && a.left < R && L < a.right && a.top < B && T < a.bottom)
        hit.push([el.classList.contains('bl-pg') ? '쪽번호' : '문서명', i + 1]);
    });
  });
  return hit;
}"""


# 글자색과 실제 뒷배경. 뒷배경은 위로 올라가며 처음 만나는 칠한 바탕이다. 도중에
# 그림 · 그라데이션 바탕을 만나면 판정하지 않는다(색 하나로 대비를 말할 수 없다).
# 1.25:1 미만이면 글자와 바탕이 사실상 같은 색이다 — 흐린 글자(고스트 번호처럼 일부러
# 옅게 깐 장식)를 잡는 검사가 아니라 사라진 글자를 잡는다.
INK_PROBE = r"""() => {
  const lum = c => { const v = c.map(x => { x /= 255; return x <= .03928 ? x / 12.92 : Math.pow((x + .055) / 1.055, 2.4); });
                     return .2126 * v[0] + .7152 * v[1] + .0722 * v[2]; };
  // color-mix() 로 만든 색은 color(srgb r g b / a) 로 나온다(0~1). 못 읽는 형식이면 판정하지 않는다
  const rgba = t => {
    let m = t.match(/rgba?\(([^)]+)\)/);
    if (m) { const p = m[1].split(/[,\s/]+/).filter(Boolean).map(Number); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; }
    m = t.match(/color\(srgb\s+([^)]+)\)/);
    if (m) { const p = m[1].split(/[\s/]+/).filter(Boolean).map(Number); return [p[0] * 255, p[1] * 255, p[2] * 255, p.length > 3 ? p[3] : 1]; }
    return null;
  };
  const out = [], INK_MIN = 1.25;
  document.querySelectorAll('.bl-sl *').forEach(el => {
    const txt = Array.from(el.childNodes).filter(n => n.nodeType === 3 && n.textContent.trim())
      .map(n => n.textContent.trim()).join(' ');
    if (!txt) return;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility !== 'visible' || parseFloat(cs.fontSize) < 2) return;
    if (el.closest('svg, .br-watermark')) return;   // 워터마크는 일부러 흐린 장식이다
    for (let p = el; p; p = p.parentElement) if (parseFloat(getComputedStyle(p).opacity) === 0) return;
    const fg = rgba(cs.color); if (!fg || fg[3] < .2) return;
    // 뒷배경은 글자가 실제로 그 위에 놓인 상자다. 막대 위로 띄운 값 라벨처럼 부모 상자
    // 밖에 놓인 글자는 부모 색이 아니라 그 바깥 바탕 위에 있다 — 가운데 점으로 가린다
    const er = el.getBoundingClientRect(), cx = er.left + er.width / 2, cy = er.top + er.height / 2;
    if (!er.width || !er.height) return;   // 조상이 숨긴 글자(고르지 않은 보기 · 탭)
    let bg = null;
    for (let p = el; p; p = p.parentElement) {
      const ps = getComputedStyle(p);
      const pr = p.getBoundingClientRect();
      const over = cx >= pr.left && cx <= pr.right && cy >= pr.top && cy <= pr.bottom;
      if (!over) continue;
      if (ps.backgroundImage && ps.backgroundImage !== 'none') return;
      const c = rgba(ps.backgroundColor);
      if (!c) return;
      if (c[3] >= .5) { bg = c; break; }
    }
    if (!bg) return;
    const a = lum(fg), b = lum(bg), r = (Math.max(a, b) + .05) / (Math.min(a, b) + .05);
    if (r < INK_MIN) {
      const s = el.closest('.bl-sl');
      out.push({sl: s && s.id || '', cls: (el.className && el.className.baseVal === undefined ? el.className : el.tagName) || el.tagName,
                txt: txt.slice(0, 30), r: +r.toFixed(2)});
    }
  });
  return out;
}"""

# 장마다 본문 요소가 머리띠 아래 · 꼬리띠 위 · 지면 안에 있는가. 세로 보기(펼침)라 단계가
# 전부 열린 최대 모습을 잰다. 고르지 않은 장면(.bl-scene)은 겹쳐 놓인 판이라 뺀다.
FIT_PROBE = r"""() => {
  const out = [];
  document.querySelectorAll('#deck > .bl-sl, main > .bl-sl').forEach((s, k) => {
    const r = s.getBoundingClientRect(), bd = s.querySelector('.bl-bd');
    const hd = s.querySelector('.bl-hd'), rf = s.querySelector('.bl-rf');
    if (!bd) return;
    const top = hd ? hd.getBoundingClientRect().bottom : r.top, bot = rf ? rf.getBoundingClientRect().top : r.bottom;
    let worst = 0, who = '';
    bd.querySelectorAll('*').forEach(el => {
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden' || cs.position === 'fixed') return;
      if (el.closest('.bl-scene:not(.is-cur)')) return;
      const b = el.getBoundingClientRect();
      if (!b.width || !b.height) return;
      const o = Math.max(b.bottom - bot, top - b.top, b.right - r.right, r.left - b.left);
      if (o > worst) { worst = o; who = (el.className && el.className.baseVal === undefined ? el.className : el.tagName) || el.tagName; }
    });
    if (worst > 1.5) out.push({k: k + 1, sl: s.id || '', px: Math.round(worst), cls: String(who).slice(0, 40)});
  });
  return out;
}"""


# 좁은 폭(900px 이하)은 장이 내용만큼 늘어나는 읽기 폭이다. 그래도 꼬리띠는 장 안에 있어야
# 하고 본문은 꼬리띠 위에서 끝나야 한다 — 띠 높이가 장 높이의 % 라 장이 늘면 꼬리띠가
# 장 밖으로 밀려 다음 장에 가려진 일이 있었다. 가로는 보지 않는다(넓은 부품은 옆으로 스크롤한다).
NARROW_PROBE = r"""() => {
  const out = [];
  document.querySelectorAll('#deck > .bl-sl, main > .bl-sl').forEach((s, k) => {
    const R = s.getBoundingClientRect(), rf = s.querySelector('.bl-rf');
    if (!rf) return;
    const F = rf.getBoundingClientRect();
    let worst = F.bottom - R.bottom, who = 'bl-rf';
    s.querySelectorAll('.bl-bd *').forEach(el => {
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden' || cs.position === 'fixed') return;
      if (el.closest('.bl-scene:not(.is-cur)')) return;
      const b = el.getBoundingClientRect();
      if (!b.width || !b.height) return;
      if (b.bottom - F.top > worst) { worst = b.bottom - F.top; who = (el.className && el.className.baseVal === undefined ? el.className : el.tagName) || el.tagName; }
    });
    if (worst > 1.5) out.push({k: k + 1, sl: s.id || '', px: Math.round(worst), cls: String(who).slice(0, 40)});
  });
  return out;
}"""


# ---------------------------------------------------------------- 정적 검사

def check_links(html, rep):
    """두 CSS 를 함께 불렀는가. blue-live.css 는 색을 선언하지 않는다."""
    has_base = re.search(r'href="[^"]*blue-report\.css"', html) or "--br-page:" in html
    has_live = re.search(r'href="[^"]*blue-live\.css"', html) or "--bl-fs-body:" in html
    if has_base and has_live:
        rep.o("CSS — blue-report.css 와 blue-live.css 를 함께 부른다")
    elif has_live:
        rep.f("blue-report.css 를 부르지 않았다 — 색 토큰이 전부 빈다")
    else:
        rep.f("blue-live.css 를 부르지 않았다 — 배율과 배치가 없다")


def check_raw_hex(html, rep):
    """본문에 토큰 밖 hex 를 직접 적지 않았는가. 규칙 문장과 CSS 는 뺀다."""
    body = _blank(html, r"<style[^>]*>.*?</style>")
    body = _blank(body, r"<!--.*?-->")
    found = {}
    for m in re.finditer(r"#[0-9a-fA-F]{3,8}\b", body):
        h = m.group().lower()
        if h not in ALLOWED_HEX:
            found[h] = found.get(h, 0) + 1
    if found:
        rep.w("토큰 밖 raw hex: " + ", ".join(f"{k}×{v}" for k, v in found.items()))
    else:
        rep.o("색 — 토큰 밖 raw hex 없음")


def check_literal_px(html, rep, path_hint=None):
    """라이브 계통 규칙에 리터럴 px 치수를 쓰지 않았는가.

    이 계통은 루트 글자 크기가 뷰포트를 따라 움직이고 안의 치수가 전부 rem 이다.
    px 를 하나 섞으면 그 값만 창 크기와 무관하게 고정돼, 작은 창에서 그 요소만
    상대적으로 커진다. 눈에 잘 안 띄고 실제로 깨지는 것은 좁은 화면이다.

    **라이브 규칙만 본다.** 한 파일로 묶으면 blue-report.css 가 통째로 인라인되는데
    거기 --br-fs-* 는 전부 px 다 — 그게 슬라이드 계통의 규격이라 정상이다. 선택자에
    bl- 가 들어간 규칙과 인라인 style= 만 세지 않으면 묶은 판에서만 129건이 뜬다.

    테두리 1px 는 실선 한 줄이라 배율을 따라갈 이유가 없다. 미디어 질의의
    분기점도 뷰포트 자체의 값이라 예외다."""
    css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S))
    # 원본 형태에서는 blue-live.css 가 외부 파일이라 <style> 이 비어 있다. 그대로
    # 두면 묶은 판에서만 검사가 돌고 원본은 무사통과한다 — 고치는 자리는 원본인데.
    # 링크를 따라가 디스크에서 읽어 함께 본다.
    for href in re.findall(r'<link[^>]+href="([^"]*blue-live\.css)"', html):
        side = os.path.join(os.path.dirname(os.path.abspath(path_hint or ".")), href)
        if os.path.isfile(side):
            css += "\n" + open(side, encoding="utf-8").read()
    css = re.sub(r"@media[^{]*\{", "{", css)          # 분기점은 뷰포트 값이라 뺀다

    def px_in(decls, where, out):
        for m in re.finditer(r"([a-z-]+)\s*:\s*([^;{}]*?-?[\d.]+px[^;{}]*)", decls):
            prop, val = m.group(1), m.group(2).strip()
            if "border" in prop or prop == "outline":
                if re.match(r"[\d.]*1px", val):
                    continue                            # 테두리 1px
            # 배율 엔진 자신은 px 로 적을 수밖에 없다. 루트 글자 크기를 rem 으로
            # 적으면 자기 자신을 참조해 순환한다.
            if prop == "font-size" and val.startswith("clamp("):
                continue
            # 흐림·그림자 반지름은 배치 치수가 아니다. 배율을 따라갈 이유가 없다.
            if prop in ("backdrop-filter", "filter", "box-shadow", "text-shadow"):
                continue
            out.append(f"{where} {prop}: {val[:44]}")

    bad = []
    # 선택자에 bl- 가 들어간 규칙만 본다 — 이 계통이 스스로 선언한 치수다.
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        sel, decls = m.group(1), m.group(2)
        if "bl-" not in sel:
            continue
        px_in(decls, "<style>", bad)
    # 인라인 style= 은 **속성 하나씩** 본다. 여러 개를 이어 붙이면 앞 선언의 px 가
    # 뒤 선언과 한 덩어리로 잡혀 없는 위반이 생긴다 — 실제로 width:100% 가
    # 앞 태그의 height:40px 에 붙어 걸렸다.
    #
    # br-logo 는 예외다. 그 height 는 brand.json 의 logoHeight 를 apply_brand.py 가
    # 넣은 값이라 이 파일이 적은 치수가 아니다.
    for tag in re.findall(r"<[^>]*\sstyle=\"[^\"]*\"[^>]*>", html):
        if "br-logo" in tag:
            continue
        m = re.search(r'style="([^"]*)"', tag)
        if m:
            px_in(m.group(1), "style=", bad)

    if bad:
        rep.f(f"리터럴 px 치수 {len(bad)}건 — 이 계통은 rem 으로만 적는다")
        for b in bad[:6]:
            print(f"        {b}")
    else:
        rep.o("치수 — 리터럴 px 없이 rem 만 쓴다")


def _slices(html):
    """장 단위로 자른다. 정규식 하나로 장 안팎을 가릴 수 없어 시작 위치로 나눈다."""
    starts = [m for m in re.finditer(
        r"<section[^>]*\bclass=\"[^\"]*\bbl-sl\b[^\"]*\"[^>]*>", html)]
    out = []
    for k, m in enumerate(starts):
        end = starts[k + 1].start() if k + 1 < len(starts) else len(html)
        out.append((m.group(0), html[m.start():end]))
    return out


def check_chrome(html, rep):
    """지면 크롬이 장마다 붙어 있는가.

    이 검사가 이 계통의 핵심이다. 앞서 라이브 덱을 냈을 때 규격서에는 띠·로고·
    워터마크가 적혀 있었지만 강제하는 것이 없었다 — 그래서 다른 에이전트가 만든
    덱에 로고도 워터마크도 띠도 붙지 않았고, 「우리 양식으로 만들었다」면서
    회사 문서로 보이지 않는 결과가 나왔다. 규칙을 글로만 두면 지켜지지 않는다.

    브랜드 마크의 data-on 이 지면과 반대인 것도 여기서 잡는다. 마크가 앉는 곳은
    지면이 아니라 띠이고 띠 색은 지면과 반대이므로, 밝은 장의 머리띠 마크는
    data-on="dark" 다. 눈으로는 틀려도 알아채기 어렵다 — 로고가 배경에 묻힐 뿐
    사라지지는 않기 때문이다."""
    sl = _slices(html)
    if not sl:
        rep.f("bl-sl 장을 찾지 못했다")
        return

    miss_hd, miss_rf, miss_pg, miss_mark, miss_wm, wrong = [], [], [], [], [], []
    for n, (tag, body) in enumerate(sl, 1):
        dark = "bl-sl--dark" in tag
        if not re.search(r'class="[^"]*\bbl-hd\b', body):       miss_hd.append(n)
        if not re.search(r'class="[^"]*\bbl-rf\b', body):       miss_rf.append(n)
        if not re.search(r'class="[^"]*\bbl-pg\b', body):       miss_pg.append(n)

        # 머리띠 안의 마크 — 띠 구간만 잘라서 본다
        hd = re.search(r'<header[^>]*\bbl-hd\b.*?</header>', body, re.S)
        mark = re.search(r'<div class="br-mark" data-on="(dark|light)"', hd.group(0)) if hd else None
        if not mark:
            miss_mark.append(n)
        else:
            want = "light" if dark else "dark"     # 띠 색은 지면과 반대다
            if mark.group(1) != want:
                wrong.append(f"{n}장 머리띠 마크 data-on=\"{mark.group(1)}\" — "
                             f"{'어두운' if dark else '밝은'} 장이므로 \"{want}\"")

        wm = re.search(r'<div class="br-watermark" data-on="(dark|light)"', body)
        if not wm:
            miss_wm.append(n)
        else:
            want = "dark" if dark else "light"     # 워터마크는 지면 위에 앉는다
            if wm.group(1) != want:
                wrong.append(f"{n}장 워터마크 data-on=\"{wm.group(1)}\" — "
                             f"{'어두운' if dark else '밝은'} 장이므로 \"{want}\"")

    def verdict(label, missing, total=len(sl)):
        if missing:
            rep.f(f"{label} 없는 장 {len(missing)}건 / 전체 {total}장 — "
                  f"{', '.join(str(x) for x in missing[:8])}")
        else:
            rep.o(f"{label} — {total}장 모두 있다")

    verdict("머리띠 .bl-hd", miss_hd)
    verdict("꼬리띠 .bl-rf", miss_rf)
    verdict("쪽번호 .bl-pg", miss_pg)
    verdict("머리띠 브랜드 마크", miss_mark)
    verdict("워터마크", miss_wm)

    if wrong:
        rep.f(f"마크 배경 짝 어긋남 {len(wrong)}건 — 띠 색은 지면과 반대다")
        for w in wrong[:6]:
            print(f"        {w}")
    else:
        rep.o("마크 배경 짝 — 머리띠·워터마크 모두 앉는 면과 맞다")


EV_GRADES = {"A", "B", "C", "R"}   # 1차 공식 · 학술·전문 · 언론·2차 · 직접 조회·집계


class _Evidence(HTMLParser):
    """칩과 근거 JSON 을 브라우저가 읽는 대로 찾는다.

    정규식으로 원문을 훑으면 `--single-file` 산출물에서 틀린다. CSS·JS 가 문서
    안으로 들어오면서 CSS 주석의 사용 예(`<script id="bl-evidence">{…}`)가
    진짜 근거보다 앞에 놓이기 때문이다. 브라우저에게 `<style>`·`<script>` 속
    글자와 주석은 태그가 아니다 — HTMLParser 도 그렇게 읽는다."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.chips, self.json, self._in = [], None, False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "bl-ev" in (a.get("class") or "").split():
            self.chips.append(a.get("data-ev"))
        if tag == "script" and a.get("id") == "bl-evidence" and self.json is None:
            self._in, self.json = True, ""

    def handle_endtag(self, tag):
        if tag == "script":
            self._in = False

    def handle_data(self, data):
        if self._in:
            self.json += data


def check_evidence(html, rep):
    """출처 칩이 실제 근거를 가리키는가.

    칩(.bl-ev data-ev="E1")은 키만 들고 있고 내용은 문서 끝 #bl-evidence JSON
    한 벌에 있다. 키가 어긋나면 누른 사람에게 「근거 없음」이 뜬다 — 근거를
    보여 주려고 단 칩이 오히려 근거가 없다는 표시가 된다. 그래서 막는다.
    칩 하나가 근거 여럿을 가리킬 수 있다(data-ev="E1,E2" — 패널에 탭으로 뜬다).

    근거 항목마다 제목 · 등급 · 출처는 반드시 있어야 한다. 등급은 A·B·C·R
    네 가지다(JSON 의 grades 로 늘릴 수 있다). 칩이 하나도 없는 덱은 해당 없음.

    캡처를 붙인 근거는 셋을 더 본다 — 캡처 id 가 img 표에 있는가, 하이라이트
    상자(hl)가 있는 캡처를 가리키고 값이 0~1 사각형인가, 원문(doc)이 문서 안
    <script id> 로 있는가. 하나라도 어긋나면 패널이 빈 뷰어나 빈 원문을 연다."""
    p = _Evidence()
    p.feed(html)
    p.close()
    chips = p.chips
    if not chips:
        rep.o("출처 칩 — 없음 (해당 없음)")
        return
    if not all(chips):
        rep.f(f"출처 칩 {sum(1 for k in chips if not k)}개에 data-ev 키가 없다")
        return
    if p.json is None:
        rep.f(f"출처 칩 {len(chips)}개가 있는데 #bl-evidence 근거 JSON 이 없다")
        return
    try:
        data = json.loads(p.json)
    except ValueError as e:
        rep.f(f"근거 JSON 을 읽지 못했다 — {e}")
        return
    ev = data.get("ev", {})
    imgs = data.get("img") or {}
    rects = data.get("hl") or {}
    grades = EV_GRADES | set((data.get("grades") or data.get("gr") or {}).keys())
    keys = [k.strip() for c in chips for k in c.split(",") if k.strip()]
    missing = sorted(set(keys) - set(ev))
    bad = []
    for k, e in ev.items():
        lack = [f for f in ("title", "grade", "src") if not e.get(f)]
        if lack:
            bad.append(f"{k} — {'·'.join(lack)} 없음")
        elif e["grade"] not in grades:
            bad.append(f"{k} — 등급 {e['grade']} 은 정의되지 않음")
        for it in e.get("imgs") or []:
            iid = it[0] if isinstance(it, (list, tuple)) and it else None
            if not iid or iid not in imgs:
                bad.append(f"{k} — 캡처 {iid} 가 img 표에 없음")
        doc = e.get("doc")
        if doc and not re.search(r'<script[^>]*\sid="' + re.escape(doc) + r'"', html):
            bad.append(f"{k} — 원문 {doc} 의 <script id> 가 없음")
    for iid, rs in rects.items():
        if iid not in imgs:
            bad.append(f"하이라이트 상자 {iid} — 그런 캡처가 없음")
            continue
        for r in rs:
            ok = (isinstance(r, (list, tuple)) and len(r) == 4 and all(isinstance(v, (int, float)) for v in r)
                  and 0 <= r[0] <= 1 and 0 <= r[1] <= 1 and 0 < r[2] <= 1 and 0 < r[3] <= 1)
            if not ok:
                bad.append(f"하이라이트 상자 {iid} — 0~1 사각형 [x, y, w, h] 가 아님: {r}")
    if missing:
        rep.f(f"근거 없는 출처 칩 — {', '.join(missing)}")
    if bad:
        rep.f(f"근거 항목 불완전 {len(bad)}건")
        for b in bad[:6]:
            print(f"        {b}")
    if not missing and not bad:
        extra = f" · 캡처 {len(imgs)}장" if imgs else ""
        rep.o(f"출처 칩 — {len(chips)}개 모두 근거 {len(ev)}건에 이어짐 · 제목·등급·출처 완비{extra}")


def check_notes(html, rep):
    """장마다 발표자 노트가 있는가. 없으면 대본 창이 그 장에서 빈칸이 된다."""
    sl = re.findall(r"<section[^>]*class=\"[^\"]*\bbl-sl\b[^\"]*\"[^>]*>", html)
    miss = [s for s in sl if "data-notes" not in s]
    if not sl:
        rep.f("bl-sl 장을 찾지 못했다")
    elif miss:
        rep.f(f"발표자 노트 없는 장 {len(miss)}건 / 전체 {len(sl)}장")
    else:
        rep.o(f"발표자 노트 — {len(sl)}장 모두 있다")


class _Slides(HTMLParser):
    """장마다 id · 노트 · 단계 값, 그리고 문서 전체의 클래스를 모은다.

    정규식으로 원문을 훑으면 화면에 글자로 적힌 마크업 견본(&lt;i class=…&gt;)까지
    클래스로 센다. 브라우저처럼 태그만 읽는다 — script · style 속은 태그가 아니다."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.slides, self.classes, self.links = [], set(), []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get("class") or "").split()
        self.classes.update(c for c in cls if c.startswith(("bl-", "br-")))
        if tag == "link" and "stylesheet" in (a.get("rel") or "") and a.get("href"):
            self.links.append(("css", a["href"]))
        if tag == "script" and a.get("src"):
            self.links.append(("js", a["src"]))
        if tag == "section" and "bl-sl" in cls:
            self.slides.append({"id": a.get("id") or "", "notes": a.get("data-notes") or "", "f": set()})
        elif self.slides and "data-f" in a:
            self.slides[-1]["f"].add((a.get("data-f") or "").strip())


def check_steps(html, rep):
    """노트의 [클릭] 이 단계 수보다 적은 장이 없는가.

    대본 창은 [클릭] 을 「클릭 n」 배지로 그리고 지금 단계와 맞춰 지난 것 · 다음 것을
    칠한다. 단계가 셋인데 [클릭] 이 없으면 발표자는 몇 번 눌러야 다음 장인지 모른다.
    [클릭] 이 단계보다 많은 것은 허용한다 — 발표 중 클릭으로 여는 겹쳐 보기(data-peek-seq)도
    [클릭] 으로 적는다."""
    p = _Slides()
    p.feed(html)
    p.close()
    bad, staged = [], 0
    for k, sl in enumerate(p.slides, 1):
        lv = len(sl["f"])
        if not lv:
            continue
        staged += 1
        n = len(re.findall(r"\[클릭\]", sl["notes"]))
        if n < lv:
            bad.append(f"{k:02d}장 {sl['id'] or ''} — 단계 {lv} · [클릭] {n}")
    if bad:
        rep.f(f"노트의 [클릭] 이 단계보다 적은 장 {len(bad)}개 — 대본 창 배지가 단계와 어긋난다")
        for b in bad[:8]:
            print(f"        {b}")
    elif staged:
        rep.o(f"단계 — 단계가 있는 {staged}장 모두 노트의 [클릭] 이 단계 수 이상")
    else:
        rep.o("단계 — 단계 전개 없음 (해당 없음)")


def _read_near(path, ref):
    """덱이 부르는 CSS · JS 를 덱 옆에서, 없으면 스킬 assets/ 에서 읽는다."""
    if "//" in ref or ref.startswith("data:"):
        return ""
    for base in (os.path.dirname(os.path.abspath(path)), os.path.join(os.path.dirname(HERE), "assets")):
        f = os.path.join(base, ref)
        if os.path.isfile(f):
            return open(f, encoding="utf-8").read()
    return ""


def check_classes(html, rep, path):
    """bl- · br- 클래스가 전부 정의돼 있는가.

    CSS(덱이 부르는 것 + 문서 안 <style>)의 클래스 선택자와 뷰어 JS 가 쓰는 이름이
    「아는 클래스」다. 그 밖의 이름은 지어낸 것이다 — 아무 모양도 동작도 붙지 않는다."""
    p = _Slides()
    p.feed(html)
    p.close()
    css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S))
    js = "\n".join(re.findall(r"<script(?![^>]*\btype=\"application/json\")(?![^>]*\btype=\"text/plain\")[^>]*>(.*?)</script>",
                              html, re.S))
    for kind, ref in p.links:
        text = _read_near(path, ref)
        if kind == "css":
            css += "\n" + text
        else:
            js += "\n" + text
    known = set(re.findall(r"\.(b[lr]-[\w-]+)", css)) | set(re.findall(r"\b(b[lr]-[\w-]+)", js))
    unknown = sorted(c for c in p.classes if c not in known)
    if not css.strip():
        rep.w("클래스 검사 생략 — 덱이 부르는 CSS 를 찾지 못했다")
    elif unknown:
        rep.f(f"정의 없는 클래스 {len(unknown)}개 — CSS · 뷰어 어디에도 없다: {' '.join(unknown[:12])}")
        print("        부품은 live-catalog.html 에서 장째 복사한다. 클래스를 지어내지 않는다")
    else:
        rep.o(f"클래스 — bl-·br- {len(p.classes)}개 모두 CSS · 뷰어에 있다")


# ---------------------------------------------------------------- 렌더 검사

def check_render(path, rep, shots=None, seen_style=()):
    chrome = need_browser()
    if not chrome:
        rep.w("렌더 검사 생략 — 브라우저를 찾지 못했다")
        return
    from playwright.sync_api import sync_playwright

    url = "file://" + os.path.abspath(path)
    overflow, tiny, body_small, marks, drawn = [], [], [], [], ""
    style, need = None, sentinels(open(path, encoding="utf-8").read())
    edge, hud_hits, errors, dead = None, [], [], []
    ink, fit, narrow = [], [], []
    wants_engine = "live-viewer.js" in open(path, encoding="utf-8").read()
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=chrome)
        for w, h in VIEWS:
            pg = br.new_page(viewport={"width": w, "height": h}, reduced_motion="reduce")
            pg.on("pageerror", lambda e, w=w: errors.append(f"{w}px {str(e).splitlines()[0]}"))
            pg.goto(url)
            pg.wait_for_timeout(1200)

            data = pg.evaluate(r"""(NOTE) => {
              const root = parseFloat(getComputedStyle(document.documentElement).fontSize);
              const out = {root, tiny: [], body: [], marks: [], over: 0, html: ''};
              out.over = Math.max(0, document.documentElement.scrollWidth
                                   - document.documentElement.clientWidth);
              out.html = document.body.innerText;
              out.engine = !!(window.blDeck && window.blDeck.slides && window.blDeck.slides.length);

              // 글자 크기 — 직접 글자를 가진 요소만 본다. 부모까지 세면 같은
              // 문장을 여러 번 센다.
              document.querySelectorAll('.bl-sl *').forEach(el => {
                const txt = Array.from(el.childNodes)
                  .filter(n => n.nodeType === 3 && n.textContent.trim())
                  .map(n => n.textContent.trim()).join(' ');
                if (!txt) return;
                const cs = getComputedStyle(el);
                if (cs.display === 'none' || cs.visibility === 'hidden') return;
                const rem = parseFloat(cs.fontSize) / root;
                const isNote = NOTE.some(c => el.closest('.' + c));
                const rec = {rem: +rem.toFixed(3), cls: el.className || el.tagName,
                             txt: txt.slice(0, 40)};
                if (rem < 0.7795) out.tiny.push(rec);
                else if (!isNote && rem < 0.9995) out.body.push(rec);
              });

              // 채움 데이터 마크 — 실제로 깔린 배경과 견준다
              document.querySelectorAll('.bl-bar,.bl-stat-v').forEach(el => {
                const cs = getComputedStyle(el);
                const fill = el.classList.contains('bl-bar')
                  ? cs.backgroundColor : cs.color;
                if (!fill || fill === 'rgba(0, 0, 0, 0)') return;
                let p = el.parentElement, bg = null;
                while (p) {
                  const b = getComputedStyle(p).backgroundColor;
                  if (b && b !== 'rgba(0, 0, 0, 0)' && !/,\s*0\)$/.test(b)) { bg = b; break; }
                  p = p.parentElement;
                }
                out.marks.push({fill, bg: bg || 'rgb(255,255,255)',
                                cls: el.className});
              });
              return out;
            }""", list(NOTE_CLS))

            if w == VIEWS[0][0]:
                style = pg.evaluate(STYLE_PROBE, [t for _, t in need])
                edge = pg.evaluate(EDGE_PROBE)
            by_what = {}
            for what, n in pg.evaluate(HUD_PROBE):
                by_what.setdefault(what, []).append(n)
            for what, ns in by_what.items():
                at = ",".join(map(str, ns[:6])) + ("…" if len(ns) > 6 else "")
                hud_hits.append(f"{w}px {what} {len(ns)}장({at})")

            if data["over"] > 1:
                overflow.append(f"{w}px — {data['over']}px 넘침")
            if wants_engine and not data["engine"]:
                dead.append(f"{w}px")
            tiny += [dict(r, view=w) for r in data["tiny"]]
            body_small += [dict(r, view=w) for r in data["body"]]
            if w != VIEWS[0][0]:
                narrow += [dict(r, view=w) for r in pg.evaluate(NARROW_PROBE)]
            if w == VIEWS[0][0]:
                marks = data["marks"]
                drawn = data["html"]
                ink = pg.evaluate(INK_PROBE)
                fit = pg.evaluate(FIT_PROBE)
                if shots:
                    # 장마다 한 장씩. 눈으로 볼 것(여백 · 균형 · 겹침)은 장 단위로 나온다
                    os.makedirs(shots, exist_ok=True)
                    ids = pg.evaluate("() => [...document.querySelectorAll('.bl-sl')].map(s => s.id || '')")
                    for k, sid in enumerate(ids):
                        pg.evaluate("(k) => { const s = document.querySelectorAll('.bl-sl')[k];"
                                    " if (window.blDeck) blDeck.go(k); else s.scrollIntoView(); }", k)
                        pg.wait_for_timeout(160)
                        name = f"{k + 1:02d}" + (f"-{sid}" if sid else "") + ".png"
                        pg.screenshot(path=os.path.join(shots, name), full_page=False)
            pg.close()
        br.close()

    if style is not None:
        check_style_applied(style, need, rep)

    if edge is not None:
        if edge["gap"] > 0:
            rep.f(f"지면이 화면 끝에 닿지 않는다 — 좌 {edge['left']}px · 우 {edge['right']}px 틈")
            print("        body 기본 여백(8px)이 살아 있으면 이렇게 된다. "
                  "blue-live.css 를 불렀는지 본다")
        else:
            rep.o("지면 — 화면 좌우 끝까지 닿는다")

    if hud_hits:
        rep.f("조작판이 꼬리띠 글자를 덮는다 — " + " · ".join(hud_hits))
    else:
        rep.o(f"조작판 — {'·'.join(str(w) for w, _ in VIEWS)}px 모두 꼬리띠 글자를 덮지 않는다")

    if tiny:
        rep.f(f"절대 하한 미만 {len(tiny)}건 — {MIN_REM}rem 보다 작다")
        for t in tiny[:6]:
            print(f"        {t['view']}px  {t['rem']}rem  .{t['cls']}  {t['txt']}")
    else:
        rep.o(f"글자 크기 — {MIN_REM}rem 미만 없음")

    if body_small:
        rep.f(f"본문 하한 미만 {len(body_small)}건 — {BODY_REM}rem 보다 작다")
        for t in body_small[:6]:
            print(f"        {t['view']}px  {t['rem']}rem  .{t['cls']}  {t['txt']}")
    else:
        rep.o(f"본문 글자 — {BODY_REM}rem 이상 (주석 계열 제외)")

    if overflow:
        rep.f("가로 넘침 — " + " · ".join(overflow))
    else:
        rep.o(f"가로 넘침 — {'·'.join(str(w) for w, _ in VIEWS)}px 모두 없음")

    weak = []
    for m in marks:
        try:
            c = contrast(_rgb_to_hex(m["fill"]), _rgb_to_hex(m["bg"]))
        except Exception:
            continue
        if c < MIN_DATA_CONTRAST:
            weak.append(f".{m['cls']} {c:.2f}:1")
    if weak:
        rep.f(f"데이터 마크 대비 미달 {len(weak)}건 — 뒷배경 대비 {MIN_DATA_CONTRAST}:1 미만")
        for w in weak[:5]:
            print(f"        {w}")
    elif marks:
        rep.o(f"데이터 마크 — {len(marks)}개 모두 뒷배경 대비 {MIN_DATA_CONTRAST}:1 이상")
    else:
        rep.w("채움 데이터 마크 없음 — 막대를 쓰면 검산 대상이 생긴다")

    if ink:
        rep.f(f"보이지 않는 글자 {len(ink)}건 — 글자색과 뒷배경 대비 1.25:1 미만")
        for t in ink[:6]:
            print(f"        {t['sl']}  .{t['cls']}  {t['r']}:1  {t['txt']}")
    else:
        rep.o("보이지 않는 글자 — 글자색과 뒷배경이 같은 색인 글자 없음 (1.25:1 미만 0)")

    if fit or narrow:
        rep.f(f"세로 넘침 — 16:9 {len(fit)}장 · 좁은 폭 {len(narrow)}건 — 본문이 꼬리띠 밑으로 · 꼬리띠가 장 밖으로 나간다")
        for t in fit[:6]:
            print(f"        16:9   {t['k']:02d}장 {t['sl']}  {t['px']}px  .{t['cls']}")
        for t in narrow[:6]:
            print(f"        {t['view']}px  {t['k']:02d}장 {t['sl']}  {t['px']}px  .{t['cls']}")
    else:
        rep.o("세로 넘침 — 16:9 는 한 화면 안, 좁은 폭은 꼬리띠가 장 안에서 본문 아래")

    if errors:
        rep.f(f"스크립트 예외 {len(errors)}건 — 뷰어나 부품이 시작하다 멈췄다")
        for e in errors[:5]:
            print(f"        {e}")
    elif dead:
        rep.f(f"뷰어 엔진이 뜨지 않았다 ({' · '.join(dead)}) — live-viewer.js 를 찾지 못했다. "
              "연결형이면 JS 를 덱 옆에 두고, 아니면 --single-file 로 묶는다")
    else:
        rep.o("스크립트 — 세 폭 모두 엔진이 뜨고 예외 없이 시작한다")

    # 원문 검사가 못 본 글자(JS 로 그린 것)를 한 번 더 본다.
    def _key(b):
        return b.split("행 ", 1)[-1]
    seen = {_key(b) for b in seen_style}
    late = [b for b in style_violations(drawn) if _key(b) not in seen]
    if late:
        rep.f(f"문체 위반 {len(late)}건 — 그려진 본문 (개조식·명사형 아님)")
        for b in late[:8]:
            print(f"        {b}")
    else:
        rep.o("문체 — 그려진 본문까지 금지 어미 없음")


def main():
    ap = argparse.ArgumentParser(description="블루 리포트 라이브 덱 점검기")
    ap.add_argument("path")
    ap.add_argument("--shots", help="장마다 화면 PNG(1600x900)를 저장할 폴더")
    a = ap.parse_args()

    if not os.path.isfile(a.path):
        raise SystemExit(f"파일이 없다: {a.path}")
    html = open(a.path, encoding="utf-8").read()
    print(f"점검 대상: {a.path}\n")

    rep = Report()
    bad = style_violations(html)
    if bad:
        rep.f(f"문체 위반 {len(bad)}건 (개조식·명사형 아님)")
        for b in bad[:8]:
            print(f"        {b}")
    else:
        rep.o("문체 — 금지 어미 없음")
    check_raw_hex(html, rep)
    check_links(html, rep)
    check_literal_px(html, rep, a.path)
    check_notes(html, rep)
    check_chrome(html, rep)
    check_brand(html, rep, a.path)
    check_evidence(html, rep)
    check_steps(html, rep)
    check_classes(html, rep, a.path)
    check_render(a.path, rep, a.shots, seen_style=bad)

    sys.exit(rep.render())


if __name__ == "__main__":
    main()
