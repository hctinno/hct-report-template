#!/usr/bin/env python3
"""블루 리포트 덱 점검기 — 레이아웃 체크리스트를 코드로 강제한다.

정적 검사(HTML 원문)와 렌더 검사(실제 브라우저 레이아웃)를 함께 돌린다.
Playwright가 없으면 정적 검사만 수행하고 그 사실을 보고한다.

    python3 check_deck.py ../assets/deck-template.html
    python3 check_deck.py deck.html --shots out/     # 슬라이드별 PNG도 저장

검사 항목
  1. 슬라이드 렌더 크기가 정확히 1920x1080인가 (넘침 없음)
  2. 24px 미만 텍스트가 없는가 (% 첨자 .br-sup 만 예외)
  3. 금지 문체(~습니다 / ~해요 등)를 쓰지 않았는가
  4. 파이(<path> 호)를 쓰지 않았는가 — 도넛만 허용
  5. 도넛 stroke-dasharray가 원주 계산과 맞는가
  6. 데이터 마크가 슬라이드 배경 대비 2:1 이상인가
  7. 토큰 밖 raw hex를 슬라이드에 직접 쓰지 않았는가
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
STYLE_BAN = re.compile(r"(합니다|습니다|입니다|됩니다|해요|어요|예요|세요)(?=[\s.,·<!?)]|$)")
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

def check_style(html, rep):
    bad = []
    for n, line in enumerate(html.splitlines(), 1):
        if STYLE_EXEMPT.search(line):
            continue
        # 태그와 주석을 걷어낸 본문 텍스트만 본다
        text = re.sub(r"<!--.*?-->", "", line)
        text = re.sub(r"<[^>]+>", " ", text)
        for m in STYLE_BAN.finditer(text):
            bad.append(f"{n}행 '{m.group(1)}' — {text.strip()[:60]}")
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
        pg = br.new_page(viewport={"width": 1920, "height": 1080})
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
            const marks = [];
            sec.querySelectorAll('.br-bar-v,.br-bar-h,.br-dot,circle').forEach(el => {
              const cs = getComputedStyle(el);
              const c = el.tagName === 'circle' ? cs.stroke : cs.backgroundColor;
              if (c && c !== 'none' && c !== 'rgba(0, 0, 0, 0)') marks.push(c);
            });
            out.push({
              i, label: fr.dataset.label,
              h: sec.scrollHeight, w: sec.scrollWidth,
              ch: sec.clientHeight, cw: sec.clientWidth,
              bg, small, mark, marks: [...new Set(marks)]
            });
          });
          return out;
        }""")

        overflow, small_all, contrast_bad = [], [], []
        mark_missing, mark_overlap, mark_variant, mark_pos = [], [], [], []
        for s in data:
            m = s.get("mark")
            here = f"{s['i']+1}. {s['label']}"
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

        if mark_overlap:
            rep.f(f"브랜드 마크가 본문과 겹침 {len(mark_overlap)}건")
            for t in mark_overlap[:10]:
                print(f"        {t}")
        else:
            rep.o("브랜드 마크 — 본문과 겹치지 않는다")

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
