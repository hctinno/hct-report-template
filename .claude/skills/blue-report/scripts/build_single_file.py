#!/usr/bin/env python3
"""덱 템플릿을 단일 HTML 파일로 묶는다.

CSS를 인라인해 첨부 파일 없이 어디서나 열리는 한 장짜리 덱을 만든다.
--artifact 를 주면 <html>/<head>/<body> 껍데기를 벗겨 Artifact 발행용으로 낸다.

    python3 build_single_file.py                       # dist/blue-report-deck.html
    python3 build_single_file.py --artifact            # dist/blue-report-artifact.html
    python3 build_single_file.py --artifact --brand ../../../brand/hct/brand.json
"""
import argparse
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DECK = os.path.join(ROOT, "assets", "deck-template.html")
ASSETS = os.path.join(ROOT, "assets")
DIST = os.path.join(ROOT, "dist")

# 덱이 링크하는 로컬 자원. 단일 파일로 만들 때 전부 본문에 박는다.
LOCAL_CSS = ("blue-report.css", "deck-viewer.css")
LOCAL_JS = ("deck-viewer.js",)


def inline_assets(html, assets_dir=None):
    """<link>·<script src>로 걸린 로컬 자원을 본문에 인라인한다.

    폰트(fonts.googleapis.com)는 원격이므로 건드리지 않는다."""
    d = assets_dir or ASSETS
    for name in LOCAL_CSS:
        tag = f'<link rel="stylesheet" href="{name}">'
        if tag in html:
            css = open(os.path.join(d, name), encoding="utf-8").read()
            html = html.replace(tag, "<style>\n" + css + "\n</style>", 1)
    for name in LOCAL_JS:
        tag = f'<script src="{name}"></script>'
        if tag in html:
            js = open(os.path.join(d, name), encoding="utf-8").read()
            html = html.replace(tag, "<script>\n" + js + "\n</script>", 1)
    return html


def build(artifact=False, brand_path=None):
    html = open(DECK, encoding="utf-8").read()
    if brand_path:
        # 순환 import를 피하려고 여기서 늦게 불러온다 (apply_brand 도 이 모듈을 쓴다).
        from apply_brand import load_brand, logo_data_uri, apply
        brand = load_brand(brand_path)
        uris = {"dark":  logo_data_uri(brand, brand_path, "logo"),
                "light": logo_data_uri(brand, brand_path, "logoOnLight")}
        html, n, left = apply(html, brand, uris)
        print(f"브랜드 적용 {n}건" + (f" · 남은 자리표시자 {len(left)}건" if left else ""))
    html = inline_assets(html)
    assert "--br-page" in html, "CSS 인라인 실패"
    assert "data-deck-title" in html, "뷰어 JS 인라인 실패"

    if not artifact:
        out = os.path.join(DIST, "blue-report-deck.html")
    else:
        # Artifact는 <!doctype>/<head>/<body>를 발행 시점에 씌운다. 본문만 남긴다.
        head = re.search(r"<head>(.*?)</head>", html, re.S).group(1)
        body = re.search(r"<body[^>]*>(.*?)</body>", html, re.S).group(1)

        keep = []
        for tag in re.findall(r'<link[^>]+>|<title>.*?</title>|<style>.*?</style>', head, re.S):
            if 'href="https://fonts.g' in tag or tag.startswith("<title") or tag.startswith("<style"):
                keep.append(tag)
        # body에 걸려 있던 .br-deck 배경을 body 규칙으로 옮긴다
        keep.append("<style>\nbody { background:#111; margin:0; }\n</style>")
        html = "\n".join(keep) + "\n" + body
        out = os.path.join(DIST, "blue-report-artifact.html")

    os.makedirs(DIST, exist_ok=True)
    open(out, "w", encoding="utf-8").write(html)
    print(f"생성: {out}  ({len(html):,}자)")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact", action="store_true", help="Artifact 발행용 (껍데기 태그 제거)")
    ap.add_argument("--brand", help="brand.json 경로. 주면 회사 정보·로고까지 넣어 만든다")
    a = ap.parse_args()
    build(a.artifact, a.brand)
