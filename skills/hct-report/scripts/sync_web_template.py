#!/usr/bin/env python3
"""HCT 웹 디자인 템플릿의 DESIGN.md 에서 관리보드용 CSS 를 뽑아 assets/hct-web.css 로 고정한다.

관리보드(`--deck manage`)는 블루 리포트 고유 계통(blue-web.css)이 아니라 사내 웹 도구와 같은
모습이어야 한다. 그 기준은 별도 저장소 hctinno/HCT-WEB-DESIGN-TEMPLATE 의 DESIGN.md 다 —
토큰(라이트 · 다크 · 접근성 적응 · 기본 레이어) 세 블록과 부품 카드 18장의 순수 CSS 가 들어 있다.
손으로 옮기면 판이 올라갈 때 어긋나므로 이 스크립트가 뽑는다.

    python3 sync_web_template.py --src ~/hct-web-design-template/DESIGN.md --version 2.1.0
    python3 sync_web_template.py --check          # assets/hct-web.css 가 고정한 판 그대로인가

--src 는 파일 경로나 URL. 생략하면 release 브랜치의 raw 주소를 쓴다.
결과 파일 머리에 판 · 원본 해시를 적는다. 값을 손으로 고치지 않는다 — 고칠 것이 있으면
원본 저장소를 고치고 다시 뽑는다.
"""
import argparse
import hashlib
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "assets", "hct-web.css")
RAW = "https://raw.githubusercontent.com/hctinno/HCT-WEB-DESIGN-TEMPLATE/release/v{v}/DESIGN.md"
PIN = "2.1.0"


def read_src(src):
    if re.match(r"https?://", src):
        with urllib.request.urlopen(src, timeout=60) as r:
            return r.read().decode("utf-8")
    return open(os.path.expanduser(src), encoding="utf-8").read()


def section(md, head):
    """'## 2. 토큰' 처럼 머리로 시작하는 절의 본문(다음 '## ' 전까지)."""
    m = re.search(r"^" + re.escape(head) + r".*?$(.*?)(?=^## |\Z)", md, re.S | re.M)
    if not m:
        sys.exit(f"오류: DESIGN.md 에 「{head}」 절이 없다 — 원본 구조가 바뀌었다")
    return m.group(1)


def css_blocks(text):
    return [b.strip() for b in re.findall(r"```css\n(.*?)```", text, re.S)]


def build(md, version):
    tok = css_blocks(section(md, "## 2. 토큰"))
    if len(tok) < 3:
        sys.exit(f"오류: 「2. 토큰」 CSS 블록이 {len(tok)}개 — 토큰 · 적응 · 기본 레이어 세 블록이 있어야 한다")
    comp_sec = section(md, "## 7. 부품 규격")
    parts = []
    # 부품 카드마다 이름을 붙여 둔다 — 어느 카드에서 온 CSS 인지 찾을 수 있게
    first = css_blocks(comp_sec.split("\n### ", 1)[0])
    parts.append(("부품 카드 공통", first))
    for chunk in comp_sec.split("\n### ")[1:]:
        name = chunk.split("\n", 1)[0].strip()
        blocks = css_blocks(chunk)
        if blocks:
            parts.append((name, blocks))
    digest = hashlib.sha256(md.encode("utf-8")).hexdigest()[:16]
    out = [f"""/* ════════════════════════════════════════════════════════════════════
   HCT 웹 디자인 템플릿 v{version} — 관리보드용 사본 (생성 파일 · 손으로 고치지 않는다)
   원본: hctinno/HCT-WEB-DESIGN-TEMPLATE · release/v{version} · DESIGN.md (sha256 {digest}…)
   만든 것: scripts/sync_web_template.py — 「2-1」 세 블록 + 「7. 부품 규격」 카드 CSS
   판을 올리려면: python3 scripts/sync_web_template.py --src <DESIGN.md> --version X.Y.Z
   ════════════════════════════════════════════════════════════════════ */
:root {{ --hct-web: "{version}"; }}
"""]
    for i, b in enumerate(tok[:3], 1):
        out.append(f"\n/* ── 2-1 · {'①②③'[i - 1]} ─────────────────────────── */\n{b}\n")
    for name, blocks in parts:
        out.append(f"\n/* ── 7 · {name} ─────────────────────────── */\n" + "\n".join(blocks) + "\n")
    return "".join(out), digest


def main():
    ap = argparse.ArgumentParser(description="웹 디자인 템플릿 CSS 동기화")
    ap.add_argument("--src", help="DESIGN.md 경로 또는 URL (기본: release 브랜치 raw)")
    ap.add_argument("--version", default=PIN, help=f"판 (기본 {PIN})")
    ap.add_argument("--check", action="store_true", help="assets/hct-web.css 의 머리 · 판만 확인")
    a = ap.parse_args()
    if a.check:
        if not os.path.isfile(OUT):
            sys.exit("assets/hct-web.css 가 없다")
        head = open(OUT, encoding="utf-8").read(2000)
        m = re.search(r'--hct-web: "([\d.]+)"', head)
        if not m:
            sys.exit("hct-web.css 머리에 판 표시가 없다 — 손으로 고친 파일이다")
        print(f"hct-web.css — 웹 디자인 템플릿 v{m.group(1)}")
        return
    src = a.src or RAW.format(v=a.version)
    md = read_src(src)
    css, digest = build(md, a.version)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(css)
    print(f"생성: {OUT}  (v{a.version} · {len(css):,}자 · 원본 sha256 {digest}…)")


if __name__ == "__main__":
    main()
