#!/usr/bin/env python3
"""덱 템플릿을 단일 HTML 파일로 묶는다.

CSS를 인라인해 첨부 파일 없이 어디서나 열리는 한 장짜리 덱을 만든다.
--artifact 를 주면 <html>/<head>/<body> 껍데기를 벗겨 Artifact 발행용으로 낸다.

    python3 build_single_file.py                       # dist/blue-report-deck.html
    python3 build_single_file.py --artifact            # dist/blue-report-artifact.html
    python3 build_single_file.py --artifact --brand ../../../brand/hct/brand.json
    python3 build_single_file.py --artifact --deck ax -o /tmp/ax-artifact.html

--deck 은 apply_brand.py 와 같은 이름을 받는다. A4 문서 이름(minutes)도 받는다.
생략하면 카탈로그다.
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")
DIST = os.path.join(ROOT, "dist")

# 덱·문서 이름. apply_brand.py 와 같은 것을 쓴다. 한곳에서만 고치도록 거기서 읽어 온다.
sys.path.insert(0, HERE)
from apply_brand import DECKS, DOCS, resolve  # noqa: E402

DECK = os.path.join(ASSETS, DECKS["catalog"])

# 로컬 자원 참조. 이름을 목록으로 박아 두지 않는다 — 덱은 deck-viewer,
# A4 문서는 doc-viewer 를 쓰므로 목록으로 두면 종류가 늘 때마다 여기를 고쳐야 한다.
# 폰트는 https://fonts.googleapis.com/css2?family=... 라 .css 로 끝나지 않아 걸리지 않는다.
LOCAL_CSS_RE = re.compile(r'<link rel="stylesheet" href="([^":/]+\.css)">')
LOCAL_JS_RE = re.compile(r'<script src="([^":/]+\.js)"></script>')

# 뷰어 CSS 가 지면 바깥 바탕을 정한다. 덱은 #111, A4 문서는 회색이다.
BODY_BG_RE = re.compile(r'html\s*,\s*body\s*\{[^}]*?background:\s*([^;}]+)')


def inline_assets(html, assets_dir=None):
    """<link>·<script src>로 걸린 로컬 자원을 본문에 인라인한다.

    폰트(fonts.googleapis.com)는 원격이므로 건드리지 않는다."""
    d = assets_dir or ASSETS

    def one(m, wrap):
        path = os.path.join(d, m.group(1))
        if not os.path.isfile(path):
            return m.group(0)
        return wrap[0] + open(path, encoding="utf-8").read() + wrap[1]

    html = LOCAL_CSS_RE.sub(lambda m: one(m, ("<style>\n", "\n</style>")), html)
    html = LOCAL_JS_RE.sub(lambda m: one(m, ("<script>\n", "\n</script>")), html)
    return html


def build(artifact=False, brand_path=None, deck="catalog", out_path=None):
    deck_path = resolve(deck)
    if not os.path.exists(deck_path):
        raise SystemExit(f"덱·문서를 찾지 못했다: {deck}\n"
                         f"덱 이름: {' · '.join(DECKS)}\n"
                         f"문서 이름: {' · '.join(DOCS)}")
    is_doc = os.path.basename(deck_path).startswith("doc-")
    html = open(deck_path, encoding="utf-8").read()
    if brand_path:
        # 순환 import를 피하려고 여기서 늦게 불러온다 (apply_brand 도 이 모듈을 쓴다).
        from apply_brand import load_brand, logo_uris, apply
        brand = load_brand(brand_path)
        uris = logo_uris(brand, brand_path)   # 키 목록은 apply_brand 가 한 곳에서 정한다
        html, n, left = apply(html, brand, uris)
        print(f"브랜드 적용 {n}건" + (f" · 남은 자리표시자 {len(left)}건" if left else ""))
    html = inline_assets(html)
    assert "--br-page" in html, "CSS 인라인 실패"
    marker = "data-doc-title" if is_doc else "data-deck-title"
    assert marker in html, f"뷰어 JS 인라인 실패 ({marker} 없음)"

    if not artifact:
        out = out_path or os.path.join(DIST, "blue-report-deck.html")
    else:
        # Artifact는 <!doctype>/<head>/<body>를 발행 시점에 씌운다. 본문만 남긴다.
        # 온전한 문서를 그대로 올리면 껍데기 안에 껍데기가 겹친다. 브라우저가
        # 관대해서 보이기는 하지만 <title>이 죽고 파서가 태그를 버린다.
        head = re.search(r"<head>(.*?)</head>", html, re.S).group(1)
        body = re.search(r"<body[^>]*>(.*?)</body>", html, re.S).group(1)

        keep = []
        for tag in re.findall(r'<link[^>]+>|<title>.*?</title>|<style>.*?</style>', head, re.S):
            if 'href="https://fonts.g' in tag or tag.startswith("<title") or tag.startswith("<style"):
                keep.append(tag)
        # 지면 바깥 바탕은 뷰어 CSS 가 html,body 에 걸어 둔다. 껍데기를 벗기면서
        # 그 규칙이 바깥 body 에 닿도록 값을 그대로 옮겨 적는다. 덱과 문서가 다르므로
        # 색을 박지 않고 방금 인라인한 CSS 에서 읽는다.
        m = BODY_BG_RE.search(html)
        assert m, "뷰어 CSS 에서 html,body 배경을 찾지 못했다"
        keep.append(f"<style>\nbody {{ background:{m.group(1).strip()}; margin:0; }}\n</style>")
        html = "\n".join(keep) + "\n" + body
        default = "blue-report-doc-artifact.html" if is_doc else "blue-report-artifact.html"
        out = out_path or os.path.join(DIST, default)

    os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
    open(out, "w", encoding="utf-8").write(html)
    print(f"생성: {out}  ({len(html):,}자)")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact", action="store_true", help="Artifact 발행용 (껍데기 태그 제거)")
    ap.add_argument("--brand", help="brand.json 경로. 주면 회사 정보·로고까지 넣어 만든다")
    ap.add_argument("--deck", default="catalog",
                    help="덱 이름(" + " · ".join(DECKS) + ") · A4 문서 이름("
                         + " · ".join(DOCS) + ") · 또는 HTML 파일 경로")
    ap.add_argument("-o", "--out", help="출력 경로. 생략하면 dist/ 에 넣는다")
    a = ap.parse_args()
    build(a.artifact, a.brand, a.deck, a.out)
