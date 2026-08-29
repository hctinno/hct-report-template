#!/usr/bin/env python3
"""회사 정보와 로고를 덱 템플릿에 한 번에 적용한다.

덱의 자리표시자(회사명·워드마크·이메일·전화·저작권·로고 자리)는 8군데에 흩어져 있다.
손으로 고치면 빠뜨리기 쉬우므로 brand.json 한 곳에서 읽어 일괄 적용한다.

항상 원본 템플릿에서 새로 만들기 때문에 몇 번을 실행해도 결과가 같다.
로고는 data URI로 박으므로 완성된 덱 파일 하나만 들고 다니면 된다.

    python3 apply_brand.py --brand brand.json                  # dist/deck-branded.html
    python3 apply_brand.py --brand brand.json -o 우리덱.html
    python3 apply_brand.py --brand brand.json --single-file    # CSS까지 인라인한 한 장짜리
"""
import argparse
import base64
import json
import mimetypes
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")

# 용도별 덱. 이름으로 고르거나 --deck 에 파일 경로를 직접 준다.
DECKS = {
    "catalog":  "deck-template.html",         # 레이아웃 12종 카탈로그
    "internal": "deck-internal-report.html",  # 사내 보고 (주간·월간)
    "sales":    "deck-sales-proposal.html",   # 외부 제안·영업
    "project":  "deck-project-report.html",   # 프로젝트 착수·완료
    "training": "deck-training.html",         # 교육·기술 설명
}

LOGO_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
              ".svg": "image/svg+xml", ".webp": "image/webp"}
LOGO_WARN_BYTES = 400 * 1024

HANGUL = re.compile(r"[가-힣]")

# 슬라이드 우측 상단 마크. 그룹1=배경 밝기, 그룹2=자리표시자 주석(다시 찾기 쉽게 남긴다).
MARK = re.compile(r'<div class="br-mark" data-on="(dark|light)">(<!--.*?-->)?.*?</div>', re.S)


def load_brand(path):
    with open(path, encoding="utf-8") as f:
        b = json.load(f)
    missing = [k for k in ("company", "copyrightYear") if not b.get(k)]
    if missing:
        sys.exit(f"오류: brand.json에 필수 항목이 없다 — {', '.join(missing)}")
    b.setdefault("wordmark", b["company"])
    b.setdefault("email", "")
    b.setdefault("website", "")
    b.setdefault("phone", "")
    b.setdefault("logoOnLight", "")
    b.setdefault("logoHeight", 40)
    return b


def logo_data_uri(brand, brand_path, key="logo"):
    """로고를 data URI로 만든다. 해당 항목이 비어 있으면 None."""
    rel = brand.get(key)
    if not rel:
        return None
    path = rel if os.path.isabs(rel) else os.path.join(os.path.dirname(os.path.abspath(brand_path)), rel)
    if not os.path.isfile(path):
        sys.exit(f"오류: 로고 파일이 없다 — {path}")
    ext = os.path.splitext(path)[1].lower()
    mime = LOGO_TYPES.get(ext) or mimetypes.guess_type(path)[0]
    if not mime or not mime.startswith("image/"):
        sys.exit(f"오류: 지원하지 않는 로고 형식 — {ext}. PNG·JPG·SVG·WEBP를 쓴다.")
    size = os.path.getsize(path)
    if size > LOGO_WARN_BYTES:
        print(f"주의: 로고가 {size/1024:.0f}KB다. 덱 파일이 그만큼 커진다. "
              f"200KB 이하로 줄이길 권한다.", file=sys.stderr)
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    print(f"로고[{key}]: {path} ({mime}, {size/1024:.1f}KB) → data URI")
    return f"data:{mime};base64,{data}"


def wordmark_html(brand, font_size):
    """로고가 없을 때 쓰는 워드마크. 한글이면 폰트와 자간을 바꾼다.

    색은 넣지 않는다. .br-mark[data-on] 규칙이 배경에 맞춰 정한다."""
    text = brand["wordmark"]
    if HANGUL.search(text):
        # Barlow Condensed에는 한글이 없다. 폰트를 바꾸고 자간을 줄인다.
        style = f"font:700 {font_size}px/1 var(--br-font-kr);letter-spacing:.02em"
    else:
        style = (f"font:600 {font_size}px/1 var(--br-font-label);"
                 f"letter-spacing:var(--br-ls-mark)")
    return f'<span class="br-wordmark" style="{style}">{text}</span>'


def logo_html(uri, height):
    return (f'<img class="br-logo" src="{uri}" alt="회사 로고" '
            f'style="height:{height}px;width:auto">')


def apply(html, brand, uris):
    """자리표시자를 실제 값으로 바꾼다. 바꾼 건수를 함께 돌려준다."""
    n = 0

    def sub(pattern, repl, count=0):
        nonlocal n, html
        html, k = re.subn(pattern, lambda m: repl, html, count=count)
        n += k
        return k

    # 우측 상단 브랜드 마크 — 모든 슬라이드에 같은 자리로 들어간다.
    # data-on 이 배경 밝기를 알려주므로 슬라이드마다 로고 변형을 바꿔 넣는다.
    h = brand["logoHeight"]

    def one_mark(m):
        on = m.group(1)
        u = uris["dark"] if on == "dark" else uris["light"]
        inner = logo_html(u, h) if u else wordmark_html(brand, 28)
        return f'<div class="br-mark" data-on="{on}">{m.group(2)}{inner}</div>'

    html, n_mark = MARK.subn(one_mark, html)
    n += n_mark
    if not n_mark:
        sys.exit("오류: br-mark 자리를 하나도 찾지 못했다. 템플릿이 수정된 것 같다.")

    contact = brand["email"] or brand["website"]
    if contact:
        sub(re.escape("contact@company.co.kr"), contact)
        if not brand["email"]:
            # 이메일 미확정 — 홈페이지 주소를 쓰므로 라벨도 WEB으로 바꾼다.
            sub(r'<span style="letter-spacing:\.1em">EMAIL</span>',
                '<span style="letter-spacing:.1em">WEB</span>', 1)
    else:
        # 연락처 없음 — 표지의 연락처 줄과 마무리의 EMAIL 행을 통째로 없앤다.
        sub(r'\n\s*<div class="br-num"[^>]*>contact@company\.co\.kr</div>', "", 1)
        sub(r'\n\s*<div style="display:flex;gap:24px;justify-content:flex-end;'
            r'margin-top:20px;[^"]*">\s*\n\s*<span[^>]*>EMAIL</span>'
            r'<span[^>]*>contact@company\.co\.kr</span>\s*\n\s*</div>', "", 1)

    if brand["phone"]:
        sub(re.escape("02-0000-0000"), brand["phone"])
    else:
        # 전화 없음 — PHONE 행을 통째로 없앤다.
        sub(r'\n\s*<div style="display:flex;gap:24px;justify-content:flex-end;'
            r'margin-top:14px;[^"]*">\s*\n\s*<span[^>]*>PHONE</span>'
            r'<span[^>]*>02-0000-0000</span>\s*\n\s*</div>', "", 1)
    sub(re.escape("© 2026 COMPANY NAME · All rights reserved"),
        f'© {brand["copyrightYear"]} {brand["company"]} · All rights reserved')

    # 푸터의 문서명. 쪽번호는 뷰어가 자동으로 매기므로 여기서 건드리지 않는다.
    if brand.get("docTitle"):
        sub(r'data-deck-title="[^"]*"', f'data-deck-title="{brand["docTitle"]}"', 1)

    # 자리표시자 주석은 일부러 남긴다. 나중에 로고를 바꿀 때 위치를 다시 찾기 쉽다.
    # 남은 자리표시자를 셀 때는 그 주석을 빼고 본문만 본다.
    body_only = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    left = re.findall(r"COMPANY NAME|company\.co\.kr|02-0000-0000", body_only)
    return html, n, left


def main():
    ap = argparse.ArgumentParser(description="회사 정보·로고를 덱에 적용")
    ap.add_argument("--brand", required=True, help="brand.json 경로")
    ap.add_argument("-o", "--out", help="출력 HTML (기본 dist/deck-branded.html)")
    ap.add_argument("--single-file", action="store_true",
                    help="CSS까지 인라인해 파일 하나로 만든다")
    ap.add_argument("--title", help="이 덱의 문서명 (푸터에 들어간다). brand.json의 docTitle보다 우선한다")
    ap.add_argument("--deck", default="catalog",
                    help="용도별 덱 이름(" + " · ".join(DECKS) + ") 또는 HTML 파일 경로")
    a = ap.parse_args()

    brand = load_brand(a.brand)
    if a.title:
        brand["docTitle"] = a.title
    # 다크면용(흰색 녹아웃)과 밝은면용(원색) 두 벌을 읽는다.
    uris = {"dark":  logo_data_uri(brand, a.brand, "logo"),
            "light": logo_data_uri(brand, a.brand, "logoOnLight")}
    if uris["dark"] and not uris["light"]:
        print("주의: logoOnLight 가 없다. 흰색 로고를 밝은 지면에 얹으면 보이지 않으므로 "
              "밝은 슬라이드는 워드마크 텍스트로 둔다. brand.json 에 원색 로고 경로를 넣어라.",
              file=sys.stderr)
    if uris["light"] and not uris["dark"]:
        print("주의: logo(다크면용 흰색 녹아웃)가 없다. 표지·다크 슬라이드는 "
              "워드마크 텍스트로 둔다.", file=sys.stderr)

    deck_path = (os.path.join(ASSETS, DECKS[a.deck]) if a.deck in DECKS
                 else os.path.abspath(a.deck))
    if not os.path.isfile(deck_path):
        sys.exit(f"오류: 덱을 찾지 못했다 — {deck_path}\n"
                 f"이름으로 고르려면: {' · '.join(DECKS)}")
    print(f"덱: {os.path.basename(deck_path)}")

    html = open(deck_path, encoding="utf-8").read()
    html, n, left = apply(html, brand, uris)

    if a.single_file:
        from build_single_file import inline_assets
        html = inline_assets(html)

    out = a.out or os.path.join(ROOT, "dist", f"deck-{a.deck}-branded.html")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n적용 {n}건")
    print(f"  회사명   {brand['company']}")
    print(f"  마크     다크면 {'로고' if uris['dark'] else '워드마크 ' + brand['wordmark']}"
          f" · 밝은면 {'로고' if uris['light'] else '워드마크 ' + brand['wordmark']}"
          f" (높이 {brand['logoHeight']}px, 우측 상단)")
    if brand["email"]:
        print(f"  연락처   {brand['email']}")
    elif brand["website"]:
        print(f"  연락처   {brand['website']} (이메일 미확정 — WEB으로 표기)")
    else:
        print("  연락처   없음 — 연락처 줄 삭제")
    print(f"  전화     {brand['phone'] or '없음 — PHONE 행 삭제'}")
    print(f"  저작권   © {brand['copyrightYear']} {brand['company']}")
    print(f"  문서명   {brand.get('docTitle') or '(미지정 — 템플릿 기본값 유지)'}")
    print(f"\n생성: {out}")
    if left:
        print(f"\n주의: 본문에 남은 자리표시자 {len(left)}건 — {', '.join(sorted(set(left)))}")
    if not a.single_file:
        print("blue-report.css를 같은 폴더에 두어야 스타일이 적용된다. "
              "파일 하나로 만들려면 --single-file 을 준다.")


if __name__ == "__main__":
    main()
