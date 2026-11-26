#!/usr/bin/env python3
"""짜임 카드(LAYOUTS.md)와 부품 카드(COMPONENTS.md)를 원본에서 만든다 — 손으로 쓰지 않는다.

HCT 웹 디자인 템플릿이 부품 규격을 코드에서 뽑아 카드로 내듯이, 블루 리포트도 카드를 원본에서 뽑는다.
문서와 코드가 어긋나는 일이 없게 하려는 것이다.

  짜임 카드  examples/layouts/cards.yaml(판단하는 말) + examples/layouts/slides.html(장 마크업 원본)
             → LAYOUTS.md. 견본 덱 자체가 examples/layouts/deck.yaml 로 조립돼 검사를 받는다.
  부품 카드  references/components.yaml(판단하는 말) + assets/live-catalog.html · examples/*(마크업 원본)
             + assets/blue-live.css(토큰 원본) → COMPONENTS.md 와 대조 덱 examples/components/.
             대조 덱은 카드에 실린 마크업 그대로를 장마다 하나씩 담는다 — verify_repo 가 그 덱을
             조립해 check_live 로 그려 본다. 카드의 HTML 이 실제로 그려지고 규칙을 지키는지의 대조다.

    python3 build_cards.py            # 세 가지를 다시 만든다
    python3 build_cards.py --check    # 다시 만든 결과가 저장소 파일과 같은가(다르면 1)
"""
import argparse
import html as H
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_deck as B  # noqa: E402

ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")
LAY_DIR = os.path.join(ROOT, "examples", "layouts")
CMP_DIR = os.path.join(ROOT, "examples", "components")
OUT_LAY = os.path.join(ROOT, "LAYOUTS.md")
OUT_CMP = os.path.join(ROOT, "COMPONENTS.md")
CMP_META = os.path.join(ROOT, "references", "components.yaml")


def load_yaml(p):
    import yaml
    return yaml.safe_load(open(p, encoding="utf-8"))


def slide_map(path):
    return {a.get("id"): (a, inner) for a, _t, inner in B.sections(open(path, encoding="utf-8").read()) if a.get("id")}


def dedent(block):
    """들여쓰기를 걷는다. 떼어 낸 요소는 첫 줄만 들여쓰기가 없으므로 나머지 줄의 최소 들여쓰기에서
    닫는 줄의 들여쓰기를 기준으로 삼는다."""
    lines = block.strip("\n").splitlines()
    rest = [l for l in lines[1:] if l.strip()]
    pad = min((len(l) - len(l.lstrip()) for l in (rest if lines[0][:1] == "<" else lines) if l.strip()), default=0)
    if lines[0][:1] == "<" and rest:
        pad = len(lines[-1]) - len(lines[-1].lstrip())
    return "\n".join(lines[:1] + [l[pad:] if l[:pad].strip() == "" else l.lstrip() for l in lines[1:]]) \
        if lines[0][:1] == "<" else "\n".join(l[pad:] for l in lines)


def tokens_in(text):
    return sorted(set(re.findall(r"var\((--(?:br|bl)-[\w-]+)", text)))


def bullets(items):
    return " · ".join(items or [])


# ── 짜임 카드 ───────────────────────────────────────────────────────────────

def layout_cards():
    meta = load_yaml(os.path.join(LAY_DIR, "cards.yaml"))
    slides = slide_map(os.path.join(LAY_DIR, "slides.html"))
    out = ["""# 짜임 카드 — 장 하나를 어떻게 나눌지

> **생성 파일** — `scripts/build_cards.py` 가 `examples/layouts/cards.yaml`(판단하는 말)과
> `examples/layouts/slides.html`(장 마크업 원본)로 만든다. 고칠 것은 그 두 파일에서 고친다.
> 견본 덱: `python3 scripts/build_deck.py examples/layouts/deck.yaml --brand <brand.json> --single-file -o <결과>.html`

장의 **내용 모양**을 먼저 정하고(금액 · 추세 · 전후 · 구조 · 경로 · 1:1 비교 · 분류 · 계획 · 화면 · 단계),
아래에서 그 모양의 카드를 고른다. 같은 짜임은 덱 안에서 3장까지 — 뉴스 10건이라도 한 틀에 끼우지 않는다.
카드의 HTML 은 견본이다. 칸 수 · 문구 · 수치는 내용에 맞게 바꾸고, 바꿀 곳은 카드의 「바꿀 곳」에 있다.
부품(수치 타일 · 간트 · 도넛 …)의 규격은 `COMPONENTS.md`.

| 카드 | 내용 모양 | 주인공 |
|---|---|---|
"""]
    for c in meta:
        out.append(f"| [{c['name']}](#{c['id']}) | {c['when']} | {c['hero']} |\n")
    for c in meta:
        if c["id"] not in slides:
            sys.exit(f"오류: cards.yaml 의 {c['id']} 가 slides.html 에 없다")
        a, inner = slides[c["id"]]
        own = "\n".join(re.findall(r"<style data-own>(.*?)</style>", inner, re.S))
        body = re.sub(r"\s*<style data-own>.*?</style>", "", inner, flags=re.S)
        attrs = " ".join(f'{k}="{H.escape(v, quote=True)}"' for k, v in a.items() if k != "data-notes")
        out.append(f"""
---

<a id="{c['id']}"></a>
## {c['name']} · `{c['id']}`

| 항목 | 내용 |
|---|---|
| 내용 모양 | {c['when']} |
| 구조 | {c['structure']} |
| 주인공 | {c['hero']} |
| 토큰 | {' '.join(f'`{t}`' for t in tokens_in(own + body)) or '—'} |
| 할 것 | {bullets(c.get('do'))} |
| 하지 말 것 | {bullets(c.get('dont'))} |
| 바꿀 곳 | {c.get('swap', '—')} |

본문(`slides.html` 에 그대로 — 머리띠 · 꼬리띠는 빌드가 단다):

```html
<section {attrs} data-notes="…">
{dedent(body)}
</section>
```

맞춤 CSS(장 안 `<style data-own>` — 선택자는 장 id 로 묶여 있다. 새 장에 쓸 때 id 를 바꾸면 선택자도 함께):

```css
{dedent(own)}
```
""")
    return "".join(out)


# ── 부품 카드 ───────────────────────────────────────────────────────────────

def element(html, cls):
    """class 에 cls 가 든 첫 요소를 짝 맞춰 통째로 떼어 낸다."""
    m = re.search(r'<(\w+)\b[^>]*class="(?:[^"]*\s)?%s(?:\s[^"]*)?"[^>]*>' % re.escape(cls), html)
    if not m:
        return None
    tag, i, depth = m.group(1), m.start(), 0
    for t in re.finditer(r"<(/?)%s\b[^>]*>" % tag, html[i:]):
        if t.group(0).endswith("/>"):
            continue
        depth += -1 if t.group(1) else 1
        if depth == 0:
            return html[i:i + t.end()]
    return None


def source_slides(ref):
    name, sid = ref.split("#", 1)
    if name == "catalog":
        path = os.path.join(ASSETS, "live-catalog.html")
    elif name.startswith("examples/"):
        path = os.path.join(ROOT, name, "slides.html")
    else:
        sys.exit(f"오류: 원본 이름을 모른다 — {name}")
    sm = slide_map(path)
    if sid not in sm:
        sys.exit(f"오류: {path} 에 #{sid} 장이 없다")
    return sm[sid][1]


def css_rules_for(classes, css):
    """blue-live.css 에서 이 부품의 클래스를 선택자에 쓴 규칙 묶음."""
    css_nc = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    hits = []
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css_nc):
        sel = m.group(1)
        if any(re.search(r"\.%s(?![\w-])" % re.escape(c), sel) for c in classes):
            hits.append(m.group(0))
    return "\n".join(hits)


def component_cards():
    meta = load_yaml(CMP_META)
    css = open(os.path.join(ASSETS, "blue-live.css"), encoding="utf-8").read()
    rows, cards, slides, evkeys = [], [], [], set()
    for c in meta:
        root = c["root"]
        snip = element(source_slides(c["from"]), root)
        if not snip:
            sys.exit(f"오류: {c['from']} 에 .{root} 요소가 없다")
        classes = list(dict.fromkeys(t for attr in re.findall(r'class="([^"]*)"', snip)
                                     for t in attr.split() if t.startswith(("bl-", "br-"))))
        rules = css_rules_for(classes, css)
        toks = tokens_in(rules)
        attrs = sorted(set(re.findall(r"\b(data-[\w-]+)=", snip)))
        evkeys |= {k for v in re.findall(r'data-ev="([^"]+)"', snip) for k in v.split(",")}
        rows.append(f"| [{c['name']}](#{root}) | `.{root}` | {c['when']} |\n")
        cards.append(f"""
---

<a id="{root}"></a>
## {c['name']} · `.{root}`

| 항목 | 내용 |
|---|---|
| 쓰는 곳 | {c['when']} |
| 구조(클래스) | {' → '.join(f'`.{x}`' for x in classes[:14])}{' …' if len(classes) > 14 else ''} |
| 속성 | {' '.join(f'`{x}`' for x in attrs) or '—'} |
| 토큰 | {' '.join(f'`{t}`' for t in toks) or '—'} |
| 할 것 | {bullets(c.get('do'))} |
| 하지 말 것 | {bullets(c.get('dont'))} |
| 원본 | `{c['from']}` — 대조 덱 `examples/components` 장 `c-{root}` |

복사용 HTML(내용만 바꾼다 — 클래스 · 속성 이름은 그대로):

```html
{dedent(snip)}
```
""")
        title = f"{c['name']} — <em>.{root}</em>"
        steps = len(set(re.findall(r'data-f="([^"]+)"', snip)))
        clicks = " ".join(["[클릭] 다음 단계를 연다."] * steps)
        slides.append(f'<section id="c-{root}" data-name="{c["name"]}" data-notes="부품 카드 대조 장이다. COMPONENTS.md 의 {c["name"]} 카드 마크업을 그대로 담았다.{(" " + clicks) if clicks else ""}">\n'
                      f'  <h2 class="bl-title">{title}</h2>\n'
                      f'  <p class="bl-lede">{c["when"]}</p>\n'
                      f'  <div class="bl-mid">\n{snip}\n  </div>\n</section>\n')
    md = ["""# 부품 카드 — 무엇을 어떤 마크업 · 토큰으로

> **생성 파일** — `scripts/build_cards.py` 가 `references/components.yaml`(판단하는 말) ·
> `assets/live-catalog.html` · `examples/*`(마크업 원본) · `assets/blue-live.css`(토큰 원본)로 만든다.
> **대조:** 카드의 HTML 을 그대로 담은 덱 `examples/components/` 를 `verify_repo.py` 가 조립해
> `check_live.py` 로 그린다 — 정의 없는 클래스 · 글자 하한 · 대비 · 넘침이 있으면 실패다.

카드 읽는 법: 쓰는 곳 → 구조(클래스 순서) → 속성(`data-*`) → 토큰 → 할 것 / 하지 말 것 → 복사용 HTML.
장 전체를 어떻게 나눌지는 `LAYOUTS.md`(짜임 카드). 맞는 부품이 없으면 `<style data-own>` 으로 새로 짠다(`DESIGN.md`).

| 부품 | 클래스 | 쓰는 곳 |
|---|---|---|
"""] + rows + cards
    deck = {
        "title": "부품 카드 대조 덱",
        "body": "slides.html",
        "evidence": "evidence.json",
        "agenda": False, "dividers": False,
        "cover": {"date": "대조", "org": "COMPONENTS.md", "title": "부품 카드 <em>대조 덱</em>",
                  "message": "카드에 실린 마크업 그대로 — <b>그려지는지 검사</b>",
                  "notes": "생성 파일이다. build_cards.py 가 COMPONENTS.md 와 함께 만든다."},
        "chapters": [{"name": "부품", "slides": [f"c-{c['root']}" for c in meta]}],
    }
    ev = {"ev": {k: {"title": "견본 근거", "grade": "R", "facts": ["카드 대조용 견본"], "src": "가상 견본", "date": "2026"}
                 for k in sorted(evkeys)}}
    head = "<!-- 생성 파일 — scripts/build_cards.py. COMPONENTS.md 카드의 마크업을 그대로 담은 대조 덱. 고치지 않는다. -->\n\n"
    return "".join(md), head + "\n".join(slides), deck, ev


def render_all():
    import yaml
    lay = layout_cards()
    cmp_md, cmp_slides, deck, ev = component_cards()
    deck_y = "# 생성 파일 — scripts/build_cards.py\n" + yaml.safe_dump(deck, allow_unicode=True, sort_keys=False)
    return {
        OUT_LAY: lay,
        OUT_CMP: cmp_md,
        os.path.join(CMP_DIR, "slides.html"): cmp_slides,
        os.path.join(CMP_DIR, "deck.yaml"): deck_y,
        os.path.join(CMP_DIR, "evidence.json"): json.dumps(ev, ensure_ascii=False, indent=2) + "\n",
    }


def main():
    ap = argparse.ArgumentParser(description="짜임 카드 · 부품 카드 생성")
    ap.add_argument("--check", action="store_true", help="저장소 파일이 다시 만든 결과와 같은지만 본다")
    a = ap.parse_args()
    files = render_all()
    if a.check:
        stale = [os.path.relpath(p, ROOT) for p, t in files.items()
                 if not os.path.isfile(p) or open(p, encoding="utf-8").read() != t]
        if stale:
            print("카드가 원본과 어긋난다 — python3 scripts/build_cards.py 로 다시 만든다: " + " · ".join(stale))
            sys.exit(1)
        print(f"카드 — 원본과 일치 ({len(files)}개 파일)")
        return
    os.makedirs(CMP_DIR, exist_ok=True)
    for p, t in files.items():
        with open(p, "w", encoding="utf-8") as f:
            f.write(t)
        print(f"생성: {os.path.relpath(p, ROOT)}  ({len(t):,}자)")


if __name__ == "__main__":
    main()
