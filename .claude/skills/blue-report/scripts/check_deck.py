#!/usr/bin/env python3
"""블루 리포트 덱 점검기 — 레이아웃 체크리스트를 코드로 강제한다.

정적 검사(HTML 원문)와 렌더 검사(실제 브라우저 레이아웃)를 함께 돌린다.
Playwright가 없으면 정적 검사만 수행하고 그 사실을 보고한다.

    python3 check_deck.py ../assets/deck-template.html
    python3 check_deck.py deck.html --shots out/     # 슬라이드별 PNG도 저장

검사 항목 (13)
  정적 — HTML 원문만 본다. Playwright 없이도 돈다.
    1. 금지 문체 — 존댓말(~습니다 / ~해요)과 평서형(~한다 / ~없다) 없이 명사형인가
    2. 파이(<path> 호)를 쓰지 않았는가 — 도넛만 허용
    3. 토큰 밖 raw hex를 슬라이드에 직접 쓰지 않았는가
    4. 도넛 stroke-dasharray가 원주 계산과 맞는가
  렌더 — 실제 브라우저 레이아웃. Playwright가 필요하다.
    5. 슬라이드 렌더 크기가 정확히 1920x1080인가 (넘침 없음)
    6. 24px 미만 텍스트가 없는가 (% 첨자 .br-sup 만 예외)
    7. 데이터 마크가 슬라이드 배경 대비 2:1 이상인가
    8. 본문 영역이 위아래로 서로 겹치지 않는가
    9. 브랜드 마크가 모든 슬라이드 우측 상단에 있는가
   10. 브랜드 마크가 본문과 겹치지 않는가
   11. 표지를 뺀 모든 지면에 배경 워터마크가 있는가 (표지에는 없어야 한다)
   12. 로고 변형이 배경 밝기와 맞는가 (어두운 면 흰색 · 밝은 면 원색)
   13. 배경 워터마크가 마크와 다른 자산인가 (국문 병기를 뗀 심볼이어야 한다)

종료 코드는 실패가 하나라도 있으면 1, 아니면 0이다. 주의는 0을 유지한다.
"""
import argparse
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import contrast, luminance, MIN_DATA_CONTRAST  # noqa: E402
from ensure_deps import need_browser  # noqa: E402

# 개조식·명사형 위반. 설문 문항 원문은 예외이므로 <!-- 원문 --> 주석이 같은 줄에 있으면 넘어간다.
#   1) 합니다체·해요체 — 존댓말 종결
STYLE_BAN = re.compile(r"(합니다|습니다|입니다|됩니다|해요|어요|예요|세요)(?=[\s.,·<!?)]|$)")
#   2) 평서형 종결(~한다 · ~됐다 · ~없다 …) — 슬라이드 본문은 명사형으로 끝낸다.
#      한글 음절 + '다' 로 끝나는 말을 잡되, 종결어미가 아닌 조사(마다 · 보다)는 뺀다.
#      발표자 노트(data-notes)는 대상이 아니다. 태그를 걷어낼 때 함께 사라진다.
#      '니다' 는 위 존댓말 규칙이 이미 잡으므로 여기서 빼서 두 번 세지 않게 한다.
STYLE_BAN_PLAIN = re.compile(r"(?!마다|보다|니다)[가-힣]다(?=[\s.,·<!?)\]]|$)")
STYLE_EXEMPT = re.compile(r"원문|설문 문항|survey-verbatim")

# 토큰으로 관리하는 색 + 알파 표기. 이 밖의 raw hex는 경고 대상.
ALLOWED_HEX = {
    "#fff", "#ffffff", "#111", "#000",
    "#f4f6f8", "#dbe3ec", "#c3cedb", "#c8d1dc",
    "#10151c", "#54606e", "#8b98a6", "#45505c", "#333e4a", "#e6ecf3",
    "#1140d6", "#2f4a9c", "#35b8f0", "#0b2a6b", "#ff7a59",
    "#f0c469", "#fff7e4", "#8a5a00", "#fff1ec", "#a33418",
    "#071b45", "#101827", "#182238", "#2b3852",
    "#a9bcd6", "#6b7c96", "#a6c2e6", "#8aa3c4", "#6fa8ff", "#ffcf6b",
    "#0b2a6b", "#1140d6", "#2f7ff0", "#5b9bd5", "#86b0da",
    "#20407e", "#345790", "#486da2", "#5d83b5", "#729ac8",
    "#7fb6f5", "#9dc4f2", "#a4c4e5",
    "#1382b8", "#e8f1fd", "#48566b", "#cfd8e3", "#8fa4bd", "#4a3200",
}


class Report:
    def __init__(self):
        self.fail, self.warn, self.ok = [], [], []

    def f(self, m): self.fail.append(m)
    def w(self, m): self.warn.append(m)
    def o(self, m): self.ok.append(m)

    def render(self):
        for m in self.ok:
            print(f"  통과  {m}")
        for m in self.warn:
            print(f"  주의  {m}")
        for m in self.fail:
            print(f"  실패  {m}")
        print(f"\n결과: 통과 {len(self.ok)} · 주의 {len(self.warn)} · 실패 {len(self.fail)}")
        return 1 if self.fail else 0


# ---------------------------------------------------------------- 정적 검사

def _blank(html, pattern):
    """주석·CSS·JS 를 공백으로 지운다. 줄바꿈은 남겨 행 번호를 보존한다."""
    return re.sub(pattern, lambda m: re.sub(r"[^\n]", " ", m.group()), html, flags=re.S)


def check_style(html, rep):
    raw_lines = html.splitlines()
    # 단일 파일 덱은 CSS·JS 가 본문에 인라인돼 있고 그 주석은 한국어 서술형이다.
    # HTML 주석도 여러 줄이라 줄 단위로는 지워지지 않는다. 먼저 통째로 걷어낸다.
    html = _blank(html, r"<!--.*?-->")
    html = _blank(html, r"<style[^>]*>.*?</style>")
    html = _blank(html, r"<script[^>]*>.*?</script>")

    bad = []
    # 예외 표시(<!-- 원문 -->)는 주석 안에 있으므로 원본 줄에서 찾는다.
    for n, (raw, line) in enumerate(zip(raw_lines, html.splitlines()), 1):
        if STYLE_EXEMPT.search(raw):
            continue
        # 태그를 걷어낸 본문 텍스트만 본다. data-notes 는 태그 안이라 함께 사라진다.
        text = re.sub(r"<[^>]+>", " ", line)
        for m in STYLE_BAN.finditer(text):
            bad.append(f"{n}행 '{m.group(1)}' — {text.strip()[:60]}")
        for m in STYLE_BAN_PLAIN.finditer(text):
            bad.append(f"{n}행 '{m.group()}' 평서형 — {text.strip()[:60]}")
    if bad:
        rep.f(f"문체 위반 {len(bad)}건 (개조식·명사형 아님)")
        for b in bad[:8]:
            print(f"        {b}")
    else:
        rep.o("문체 — 금지 어미 없음")


def check_pie(html, rep):
    pies = [m for m in re.findall(r"<path[^>]*\sd=\"([^\"]+)\"", html)
            if re.search(r"[Aa]\s*[\d.]", m)]
    if pies:
        rep.f(f"파이 추정 <path> {len(pies)}개 — 도넛(stroke-dasharray)으로 바꾼다")
    else:
        rep.o("파이 없음 — 도넛만 사용")


def check_donut_math(html, rep):
    circles = re.findall(
        r'<circle[^>]*\br="([\d.]+)"[^>]*stroke-dasharray="([\d.]+)\s+([\d.]+)"'
        r'[^>]*transform="rotate\(([-\d.]+)\)"', html)
    if not circles:
        rep.w("도넛 circle 없음 — 도넛 슬라이드를 쓰면 검산 대상이 생긴다")
        return
    bad = 0
    for r, dash, gapsum, rot in circles:
        r, dash, gapsum = float(r), float(dash), float(gapsum)
        C = 2 * math.pi * r
        if abs(gapsum - C) > 1.0:
            rep.f(f"도넛 r={r}: dasharray 두 번째 값 {gapsum} ≠ 원주 {C:.1f}")
            bad += 1
        pct = (dash + C * 1.5 / 360) / C * 100
        if not (0 < pct <= 100.5):
            rep.f(f"도넛 r={r}: dash {dash}에서 역산한 비율 {pct:.1f}% 가 범위 밖")
            bad += 1
    if not bad:
        rep.o(f"도넛 검산 — circle {len(circles)}개 원주·비율 일치")


def check_raw_hex(html, rep):
    body = html.split("</style>")[-1]          # 뷰어 CSS 제외, 슬라이드 마크업만
    found = {}
    for m in re.finditer(r"#[0-9a-fA-F]{3,6}\b", body):
        h = m.group(0).lower()
        if h not in ALLOWED_HEX:
            found[h] = found.get(h, 0) + 1
    if found:
        rep.w("토큰 밖 raw hex: " + ", ".join(f"{k}×{v}" for k, v in found.items()))
    else:
        rep.o("색 — 토큰 밖 raw hex 없음")


# ---------------------------------------------------------------- 렌더 검사

def check_render(path, rep, shots=None):
    # 없으면 여기서 알아서 받는다. 사용자가 미리 설치할 필요가 없다.
    chrome = need_browser()
    from playwright.sync_api import sync_playwright

    url = "file://" + os.path.abspath(path)
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path=chrome)
        # reduced_motion 으로 연다. 등장 애니메이션이 fill:both 라 재생 전에는
        # 막대가 scaleY(0) 로 접혀 있고, 스크롤로 슬라이드가 활성화되는 순간부터
        # 재생된다. 그대로 찍으면 아직 안 뜬 막대가 PNG 에서 통째로 사라져
        # "눈으로 확인한다" 단계가 거짓말을 한다. 애니메이션을 끄면 최종 상태다.
        pg = br.new_page(viewport={"width": 1920, "height": 1080}, reduced_motion="reduce")
        pg.goto(url + "?all=1")
        pg.wait_for_timeout(1800)          # 폰트 로드 대기

        data = pg.evaluate(r"""() => {
          const out = [];
          document.querySelectorAll('.br-frame').forEach((fr, i) => {
            const sec = fr.querySelector('.br-slide');
            const bg  = getComputedStyle(sec).backgroundColor;
            const small = [];
            sec.querySelectorAll('*').forEach(el => {
              const txt = Array.from(el.childNodes)
                .filter(n => n.nodeType === 3 && n.textContent.trim())
                .map(n => n.textContent.trim()).join(' ');
              if (!txt) return;
              if (el.classList.contains('br-sup')) return;   // % 첨자는 예외
              const fs = parseFloat(getComputedStyle(el).fontSize);
              if (fs < 24) small.push({fs: Math.round(fs*10)/10, txt: txt.slice(0,32)});
            });
            // 배경 워터마크 — 마크와 같은 자산이면 국문 병기가 딸려 온다.
            // 원본 픽셀 비율로 가른다. 심볼은 국문이 빠져 더 납작하다.
            let wm = null;
            const wmImg = sec.querySelector('.br-watermark img');
            const mkImg = sec.querySelector('.br-mark img');
            if (wmImg && mkImg) {
              wm = { w: wmImg.naturalWidth, h: wmImg.naturalHeight,
                     mw: mkImg.naturalWidth, mh: mkImg.naturalHeight };
            }

            // 우측 상단 브랜드 마크 — 존재 여부, 배경 선언, 본문과의 겹침
            const mk = sec.querySelector('.br-mark');
            let mark = null;
            if (mk) {
              const mr = mk.getBoundingClientRect();
              const sr = sec.getBoundingClientRect();
              const hit = [];
              sec.querySelectorAll('*').forEach(el => {
                if (mk === el || mk.contains(el) || el.contains(mk)) return;
                const cs = getComputedStyle(el);
                if (cs.visibility === 'hidden' || cs.display === 'none') return;
                // 눈에 보이는 것만 본다: 직접 글자를 가졌거나 카드·막대·도형이거나
                const own = Array.from(el.childNodes)
                  .some(n => n.nodeType === 3 && n.textContent.trim());
                const solid = el.classList.contains('br-card')
                  || el.classList.contains('br-bar-v') || el.classList.contains('br-bar-h')
                  || el.tagName === 'IMG' || el.tagName === 'svg';
                if (!own && !solid) return;
                const r = el.getBoundingClientRect();
                const ox = Math.min(mr.right, r.right) - Math.max(mr.left, r.left);
                const oy = Math.min(mr.bottom, r.bottom) - Math.max(mr.top, r.top);
                if (ox > 1 && oy > 1) {
                  hit.push({ tag: el.tagName.toLowerCase(),
                             cls: (el.className.baseVal ?? el.className ?? '').toString().slice(0, 28),
                             txt: (el.textContent || '').trim().slice(0, 28),
                             ox: Math.round(ox), oy: Math.round(oy) });
                }
              });
              mark = { on: mk.dataset.on || '', img: !!mk.querySelector('img'),
                       top: Math.round(mr.top - sr.top), right: Math.round(sr.right - mr.right),
                       h: Math.round(mr.height), hit: hit.slice(0, 3),
                       inside: mr.top >= sr.top && mr.right <= sr.right };
            }
            // 슬라이드 직계 형제끼리 세로로 겹치는가.
            // 컨테이너가 min-height:0 으로 줄어도 안의 카드는 내용 높이만큼 삐져나온다.
            // 그래서 박스가 아니라 자손까지 포함한 실제 차지 범위로 잰다.
            const bands = [];
            [...sec.children].forEach(el => {
              // .br-watermark 는 지면 뒤(z-index:-1)에 깔리는 배경 장치다. 본문과 겹치는 것이 정상.
              if (el.classList.contains('br-mark') || el.classList.contains('br-rule')
                  || el.classList.contains('br-watermark')) return;
              const cs = getComputedStyle(el);
              if (cs.display === 'none' || cs.visibility === 'hidden' || cs.position === 'absolute') return;
              let r = el.getBoundingClientRect();
              let top = r.top, bottom = r.bottom, left = r.left, right = r.right;
              el.querySelectorAll('*').forEach(d => {
                const dcs = getComputedStyle(d);
                if (dcs.display === 'none' || dcs.visibility === 'hidden' || dcs.position === 'absolute') return;
                const dr = d.getBoundingClientRect();
                if (dr.height === 0 && dr.width === 0) return;
                if (dr.top < top) top = dr.top;
                if (dr.bottom > bottom) bottom = dr.bottom;
                if (dr.left < left) left = dr.left;
                if (dr.right > right) right = dr.right;
              });
              bands.push({ cls: (el.className || el.tagName).toString().slice(0, 30),
                           txt: (el.innerText || '').trim().split(String.fromCharCode(10))[0].slice(0, 24),
                           top: Math.round(top), bottom: Math.round(bottom),
                           left: Math.round(left), right: Math.round(right) });
            });
            const collide = [];
            for (let a = 0; a < bands.length - 1; a++) {
              for (let b = a + 1; b < bands.length; b++) {
                const over = Math.round(Math.min(bands[a].bottom, bands[b].bottom)
                                      - Math.max(bands[a].top, bands[b].top));
                // 가로로도 겹쳐야 진짜 겹침이다. 2열 그리드처럼 좌우로 나란한 형제는 넘어간다.
                const ox = Math.round(Math.min(bands[a].right, bands[b].right)
                                    - Math.max(bands[a].left, bands[b].left));
                if (over > 2 && ox > 2) collide.push({ a: bands[a], b: bands[b], over });
              }
            }

            // 본문 안전영역 — 본문 잉크가 y 1000px 아래로 내려가지 않는다.
            // 푸터까지 최소 70px 완충을 둔다. 참조 덱은 본문 하단선이 y 933 이었다.
            // 겹침 검사는 "이미 부딪혔을 때"만 잡는다. 이건 부딪히기 전에 잡는다.
            let deepest = null;
            const sr0 = sec.getBoundingClientRect();
            sec.querySelectorAll('*').forEach(el => {
              if (el.closest('.br-footer, .br-mark, .br-watermark, .br-rule')) return;
              const cs = getComputedStyle(el);
              if (cs.visibility === 'hidden' || cs.display === 'none') return;
              const own = Array.from(el.childNodes).some(n => n.nodeType === 3 && n.textContent.trim());
              const solid = el.classList.contains('br-card') || el.classList.contains('br-bar-v')
                         || el.classList.contains('br-bar-h') || el.tagName === 'IMG' || el.tagName === 'svg';
              if (!own && !solid) return;
              const r = el.getBoundingClientRect();
              if (r.height <= 0) return;
              const bottom = Math.round(r.bottom - sr0.top);
              if (!deepest || bottom > deepest.y) {
                deepest = { y: bottom, txt: (el.textContent || '').trim().slice(0, 26) || el.tagName.toLowerCase() };
              }
            });

            // 지시선 주석이 실제로 그려지는가. 조상 중 하나라도 overflow 를 잘라
            // 두면 절대 배치한 글자와 점이 조용히 사라진다. 가로 막대 트랙이
            // overflow:hidden 이라 실제로 통째로 잘렸고, 다른 검사는 다 통과했다.
            const notes = [];
            sec.querySelectorAll('.br-note').forEach(nt => {
              const parts = [['점이', nt.querySelector('.br-note-dot')],
                             ['글자가', nt.querySelector('.br-note-text')]];
              const label = (nt.textContent || '').trim().slice(0, 24);
              for (const [what, el] of parts) {
                if (!el) continue;
                const r = el.getBoundingClientRect();
                for (let a = el.parentElement; a && a !== document.body; a = a.parentElement) {
                  const ov = getComputedStyle(a).overflow;
                  if (ov === 'visible') continue;
                  const ar = a.getBoundingClientRect();
                  if (r.top < ar.top - .5 || r.bottom > ar.bottom + .5 ||
                      r.left < ar.left - .5 || r.right > ar.right + .5) {
                    notes.push({ kind: '잘림', what,
                                 by: a.className.toString().split(' ')[0] || a.tagName.toLowerCase(),
                                 txt: label });
                    break;
                  }
                }
              }
              // 선이 점과 글자를 잇는가. 세로획은 글자 쪽 끝에 있어야 한다 —
              // 점 쪽에 두면 ㄱ 자가 글자에 닿지 않고 장식이 된다.
              const tx = nt.querySelector('.br-note-text');
              const bs = getComputedStyle(nt, '::before');
              if (tx && bs.content !== 'none') {
                const br = nt.getBoundingClientRect();   // 폭 0 — 점이 서 있는 자리다
                const w = parseFloat(bs.width) || 0;
                const left = nt.classList.contains('br-note--left');
                const boxLeft = left ? br.left - w : br.left;
                // 세로획이 실제로 어느 쪽에 그어졌는지는 테두리 폭으로 읽는다.
                // 변형 이름으로 짐작하면 테두리를 반대로 준 실수를 못 잡는다.
                const strokeX = parseFloat(bs.borderLeftWidth) > 0 ? boxLeft : boxLeft + w;
                const near = left ? tx.getBoundingClientRect().right : tx.getBoundingClientRect().left;
                if (Math.abs(strokeX - near) > 40)
                  notes.push({ kind: '끊김', what: '선', by: Math.round(Math.abs(strokeX - near)) + 'px',
                               txt: label });
              }
            });

            const marks = [];
            const blank = [];
            sec.querySelectorAll('.br-bar-v,.br-bar-h,.br-dot,.br-iso-cell,circle').forEach(el => {
              const cs = getComputedStyle(el);
              // 그라디언트로 칠한 막대는 backgroundColor 가 비어 있다. 그림 쪽에서
              // 색 정지점을 뽑아 전부 대비 검사에 넣는다 — 한쪽 끝만 통과하고
              // 다른 끝이 지면에 묻으면 막대의 절반이 사라진 것과 같다.
              const stops = (cs.backgroundImage || '').match(/rgba?\([^)]*\)/g) || [];
              if (el.tagName !== 'circle' && stops.length) { stops.forEach(c => marks.push(c)); return; }
              const c = el.tagName === 'circle' ? cs.stroke : cs.backgroundColor;
              // 색이 안 잡히면 건너뛰는 것이 아니라 잡아낸다. 예전에는 걸러 내기만 해서
              // 조각이 통째로 안 그려져도 대비 검사를 그냥 통과했다. var() 하나가
              // 풀리지 않으면 값 하나가 지면에서 조용히 사라진다.
              if (!c || c === 'none' || c === 'rgba(0, 0, 0, 0)') {
                blank.push({ tag: el.tagName.toLowerCase(),
                             cls: (el.className.baseVal ?? el.className ?? '').toString().slice(0,30) });
                return;
              }
              marks.push(c);
            });

            // 막대 길이가 값에 비례하는가. 도넛은 원주로 검산하면서 막대는 아무도
            // 안 봤다. 경영진 보고에서 142%가 제일 짧고 116%가 화면을 다 차지하는
            // 상태로 12항목을 전부 통과해 나갔다.
            const num = t => { const m = (t||'').replace(/,/g,'').match(/-?\d+(\.\d+)?/);
                               return m ? parseFloat(m[0]) : null; };
            // 단위는 .br-sup 에 들어간다(% · 분 · 배 · 건). 한 그룹에 단위가 섞이면
            // 공통 척도가 성립하지 않는다 — 184분과 3.8배를 같은 자로 잴 수 없다.
            // 그때는 행마다 자기 척도를 쓰는 것이 옳으므로 검산 대상에서 뺀다.
            const unit = el => (el?.querySelector('.br-sup')?.textContent || '').trim();
            const bars = [];
            // 세로 — .br-col 안의 값과 막대 높이
            const cols = [...sec.querySelectorAll('.br-col')].map(c => {
              const ve = c.querySelector('.br-col-val');
              const v = num(ve?.textContent);
              const b = c.querySelector('.br-bar-v');
              return (v !== null && b)
                ? { v, u: unit(ve), len: b.getBoundingClientRect().height } : null;
            }).filter(Boolean);
            if (cols.length > 1) bars.push({ kind: '세로', items: cols });
            // 가로 — .br-bars-h 그리드의 값과 채움 폭.
            // data-bar-scale="row" 를 준 그룹은 행마다 척도가 다르다고 선언한 것이다.
            sec.querySelectorAll('.br-bars-h').forEach(g => {
              if (g.dataset.barScale === 'row') return;
              const ves   = [...g.querySelectorAll('.br-bar-val')];
              const vals  = ves.map(e => num(e.textContent));
              const fills = [...g.querySelectorAll('.br-bar-h')].map(e => e.getBoundingClientRect().width);
              if (vals.length === fills.length && vals.length > 1 && vals.every(v => v !== null))
                bars.push({ kind: '가로',
                            items: vals.map((v,i) => ({ v, u: unit(ves[i]), len: fills[i] })) });
            });
            out.push({
              i, label: fr.dataset.label,
              h: sec.scrollHeight, w: sec.scrollWidth,
              ch: sec.clientHeight, cw: sec.clientWidth,
              bg, small, mark, collide, wm, blank, bars, deepest, notes,
              // 표지에만 워터마크를 넣지 않는다. 표지는 --cover 조판을 쓴 '첫 장'이다.
              // 마무리 장도 --cover 조판이지만 표지가 아니므로 워터마크가 깔린다.
              // 조판 클래스만 보면 마무리 장을 표지로 착각한다.
              cover: i === 0 && sec.classList.contains('br-slide--cover'),
              hasWm: !!sec.querySelector('.br-watermark'),
              marks: [...new Set(marks)]
            });
          });
          return out;
        }""")

        overflow, small_all, contrast_bad, collide_all = [], [], [], []
        mark_missing, mark_overlap, mark_variant, mark_pos = [], [], [], []
        wm_missing, wm_extra = [], []
        for s in data:
            m = s.get("mark")
            here = f"{s['i']+1}. {s['label']}"
            # 배경 워터마크 — 표지만 빼고 모든 지면에 깔린다. PPTX 판도 같은 규칙으로
            # 그리므로, 한쪽만 어기면 같은 보고가 형식에 따라 다르게 보인다.
            # ax 덱 1장이 실제로 그랬고 다른 검사는 전부 통과했다.
            if s.get("cover") and s.get("hasWm"):
                wm_extra.append(here)
            elif not s.get("cover") and not s.get("hasWm"):
                wm_missing.append(here)
            if not m:
                mark_missing.append(here)
            else:
                for h in m["hit"]:
                    mark_overlap.append(
                        f"{here}: {h['tag']}.{h['cls']} 와 {h['ox']}x{h['oy']}px 겹침"
                        + (f" — “{h['txt']}”" if h["txt"] else ""))
                if not m["inside"]:
                    mark_pos.append(f"{here}: 마크가 슬라이드 밖으로 나갔다")
                # 파란·어두운 배경이면 흰색 로고, 밝은 지면이면 원색 로고여야 한다.
                bgh = _rgb_to_hex(s["bg"])
                if bgh:
                    want = "dark" if luminance(bgh) < 0.5 else "light"
                    if m["on"] != want:
                        mark_variant.append(
                            f"{here}: 배경 {bgh}(광도 {luminance(bgh):.3f})는 "
                            f"data-on=\"{want}\" 여야 하는데 \"{m['on'] or '없음'}\" 이다")
            for c in s.get("collide", []):
                collide_all.append(
                    f"{s['i']+1}. {s['label']}: {c['a']['cls']}"
                    + (f"(“{c['a']['txt']}”)" if c['a']['txt'] else "")
                    + f" 와 {c['b']['cls']}"
                    + (f"(“{c['b']['txt']}”)" if c['b']['txt'] else "")
                    + f" 가 세로로 {c['over']}px 겹침")
            if s["h"] != 1080 or s["w"] != 1920:
                overflow.append(f"{s['i']+1}. {s['label']}: {s['w']}x{s['h']} (기대 1920x1080)")
            for t in s["small"]:
                small_all.append(f"{s['i']+1}. {s['label']}: {t['fs']}px — “{t['txt']}”")
            for m in s["marks"]:
                hexc = _rgb_to_hex(m)
                bgh = _rgb_to_hex(s["bg"])
                if not hexc or not bgh:
                    continue
                cr = contrast(hexc, bgh)
                if cr < MIN_DATA_CONTRAST:
                    contrast_bad.append(f"{s['i']+1}. {s['label']}: {hexc} vs {bgh} = {cr:.2f}:1")

        if overflow:
            rep.f(f"슬라이드 크기 이탈 {len(overflow)}건")
            for o in overflow:
                print(f"        {o}")
        else:
            rep.o(f"슬라이드 크기 — {len(data)}장 모두 정확히 1920x1080")

        if collide_all:
            rep.f(f"본문 영역이 서로 겹침 {len(collide_all)}건")
            for c in collide_all[:10]:
                print(f"        {c}")
            print("        → 여백을 줄이거나 내용을 덜어 아래 영역을 밀어내지 않게 한다")
        else:
            rep.o("본문 영역 — 위아래가 서로 겹치지 않는다")

        if small_all:
            rep.f(f"24px 미만 텍스트 {len(small_all)}건")
            for t in small_all[:10]:
                print(f"        {t}")
        else:
            rep.o("글자 크기 — 24px 미만 없음")

        if contrast_bad:
            rep.f(f"데이터 마크 대비 2:1 미달 {len(contrast_bad)}건")
            for c in contrast_bad[:10]:
                print(f"        {c}")
        else:
            rep.o("데이터 마크 — 전부 배경 대비 2:1 이상")

        # 색이 안 잡힌 마크. var() 하나가 풀리지 않으면 값 하나가 조용히 사라진다.
        blank_bad = []
        for s_ in data:
            for b in s_.get("blank", []):
                blank_bad.append(f"{s_['i']+1}장 {s_['label']} — {b['tag']}.{b['cls']} 색이 잡히지 않는다")
        if blank_bad:
            rep.f(f"안 그려지는 데이터 마크 {len(blank_bad)}건")
            for t in blank_bad[:10]:
                print(f"        {t}")
        else:
            rep.o("데이터 마크 — 전부 색이 잡힌다")

        # 본문 안전영역. 푸터와 부딪히기 전에 잡는다.
        SAFE_Y = 1000
        deep_bad = []
        for s_ in data:
            d = s_.get("deepest")
            if d and d["y"] > SAFE_Y:
                deep_bad.append(f"{s_['i']+1}장 {s_['label']} — 본문이 y {d['y']}px 까지 내려간다"
                                f"(상한 {SAFE_Y}) · {d['txt']}")
        if deep_bad:
            rep.f(f"본문 안전영역 이탈 {len(deep_bad)}건")
            for t in deep_bad[:10]:
                print(f"        {t}")
        else:
            rep.o(f"본문 안전영역 — 잉크가 y {SAFE_Y}px 위에 머문다")

        # 16. 지시선 주석이 잘리지 않는가. 절대 배치라 조상이 자르면 조용히 사라진다.
        clip_bad = []
        for s_ in data:
            for n in s_.get("notes", []):
                if n["kind"] == "잘림":
                    clip_bad.append(f"{s_['i']+1}장 {s_['label']} — 지시선 {n['what']} "
                                    f".{n['by']} 의 overflow 에 잘린다 · {n['txt']}")
                else:
                    clip_bad.append(f"{s_['i']+1}장 {s_['label']} — 지시선이 글자에 닿지 않는다"
                                    f"(세로획과 {n['by']} 떨어짐) · {n['txt']}")
        if clip_bad:
            rep.f(f"지시선 주석 결함 {len(clip_bad)}건")
            for t in clip_bad[:10]:
                print(f"        {t}")
            print("        → 지시선은 세로 막대(.br-bar-v) 안에 둔다. 가로 막대 트랙은 잘라 낸다")
            print("        → 세로획은 글자 쪽 끝에 둔다. 점 쪽에 두면 선이 글자까지 이어지지 않는다")
        else:
            rep.o("지시선 주석 — 잘리지 않고 점과 글자를 잇는다")

        # 막대 길이가 값에 비례하는가. 최댓값을 1로 놓고 견준다.
        # 최소 폭·둥근 끝 때문에 짧은 막대가 조금 길게 잡히므로 3%p 를 허용한다.
        prop_bad = []
        mixed = 0
        for s_ in data:
            for g in s_.get("bars", []):
                items = [it for it in g["items"] if it["v"] is not None]
                if len(items) < 2:
                    continue
                # 단위가 섞인 그룹은 공통 척도가 없다. 184분과 3.8배를 같은 자로
                # 재면 안 된다. 행마다 자기 척도를 쓰는 것이 옳은 조판이다.
                if len({it.get("u", "") for it in items}) > 1:
                    mixed += 1
                    continue
                vmax = max(abs(it["v"]) for it in items)
                lmax = max(it["len"] for it in items)
                if vmax == 0 or lmax == 0:
                    continue
                for it in items:
                    want, got = abs(it["v"]) / vmax, it["len"] / lmax
                    if abs(want - got) > 0.03:
                        prop_bad.append(
                            f"{s_['i']+1}장 {s_['label']} — {g['kind']} 막대 값 {it['v']}"
                            f"(최댓값의 {want*100:.0f}%)인데 길이는 {got*100:.0f}%")
        if prop_bad:
            rep.f(f"막대 길이가 값과 어긋남 {len(prop_bad)}건")
            for t in prop_bad[:10]:
                print(f"        {t}")
        else:
            note = f" (단위가 섞인 {mixed}개 그룹은 행별 척도라 제외)" if mixed else ""
            rep.o(f"막대 검산 — 길이가 값에 비례한다{note}")

        if mark_missing:
            rep.f(f"브랜드 마크 없는 슬라이드 {len(mark_missing)}장")
            for t in mark_missing[:10]:
                print(f"        {t}")
        elif mark_pos:
            rep.f(f"브랜드 마크 위치 이탈 {len(mark_pos)}건")
            for t in mark_pos:
                print(f"        {t}")
        else:
            rep.o(f"브랜드 마크 — {len(data)}장 모두 우측 상단에 있다")

        if wm_missing or wm_extra:
            if wm_missing:
                rep.f(f"워터마크 배치 — 없는 슬라이드 {len(wm_missing)}장")
                for t in wm_missing[:10]:
                    print(f"        {t}")
            if wm_extra:
                rep.f(f"워터마크 배치 — 표지에 있다 {len(wm_extra)}장 · 제목과 겹친다")
                for t in wm_extra[:10]:
                    print(f"        {t}")
        else:
            n = sum(1 for s in data if not s.get("cover"))
            rep.o(f"워터마크 배치 — 표지를 뺀 {n}장 모두 있다")

        if mark_overlap:
            rep.f(f"브랜드 마크가 본문과 겹침 {len(mark_overlap)}건")
            for t in mark_overlap[:10]:
                print(f"        {t}")
        else:
            rep.o("브랜드 마크 — 본문과 겹치지 않는다")

        # 12. 배경 워터마크가 마크와 다른 자산인가.
        #     같은 파일이면 국문 병기가 720px 로 함께 커져 본문 괘선에 닿는다.
        #     브랜드를 넣기 전 템플릿에는 이미지가 없으므로 그때는 건너뛴다.
        wm_same = []
        for s_ in data:
            w = s_.get("wm")
            if not w:
                continue
            if (w["w"], w["h"]) == (w["mw"], w["mh"]):
                wm_same.append(f"{s_['i']+1}장 {s_['label']} — "
                               f"워터마크가 마크와 같은 {w['w']}x{w['h']} 자산")
        if wm_same:
            rep.f(f"배경 워터마크가 마크와 같은 자산 {len(wm_same)}건")
            for t in wm_same[:6]:
                print(f"        {t}")
            print("        → brand.json 의 watermark·watermarkOnLight 에 심볼만 잘라 낸 판을 준다")
            print("        → make_logo_variants.py 가 -symbol-white.png · -symbol-color.png 로 만든다")
        elif any(s_.get("wm") for s_ in data):
            rep.o("배경 워터마크 — 마크와 다른 자산(심볼)을 쓴다")
        else:
            rep.w("배경 워터마크 — 브랜드 미적용 템플릿이라 확인 생략")

        if mark_variant:
            rep.f(f"로고 변형이 배경과 안 맞음 {len(mark_variant)}건")
            for t in mark_variant[:10]:
                print(f"        {t}")
        else:
            rep.o("로고 변형 — 어두운 면 흰색·밝은 면 원색 규칙 일치")

        if shots:
            os.makedirs(shots, exist_ok=True)
            for s in data:
                fr = pg.locator(".br-frame").nth(s["i"])
                fr.screenshot(path=os.path.join(shots, f"{s['i']+1:02d}-{s['label']}.png"))
            print(f"\n  스크린샷 {len(data)}장 저장: {shots}")
        br.close()


def _rgb_to_hex(c):
    m = re.match(r"rgba?\((\d+),\s*(\d+),\s*(\d+)", c or "")
    if not m:
        return None
    return "#%02x%02x%02x" % tuple(int(x) for x in m.groups())


def main():
    ap = argparse.ArgumentParser(description="블루 리포트 덱 점검")
    ap.add_argument("deck", help="점검할 HTML 파일")
    ap.add_argument("--shots", help="슬라이드별 PNG를 저장할 폴더")
    a = ap.parse_args()

    html = open(a.deck, encoding="utf-8").read()
    rep = Report()
    print(f"점검 대상: {a.deck}\n")
    check_style(html, rep)
    check_pie(html, rep)
    check_donut_math(html, rep)
    check_raw_hex(html, rep)
    check_render(a.deck, rep, a.shots)
    print()
    sys.exit(rep.render())


if __name__ == "__main__":
    main()
