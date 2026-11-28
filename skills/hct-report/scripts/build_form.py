#!/usr/bin/env python3
"""A4 문서 양식 정의(forms/<id>.json) → blue-doc.css 의 생성 블록.

    python3 scripts/build_form.py                 # 지금 기본 양식으로 CSS 를 다시 만든다(forms/ 를 고친 뒤)
    python3 scripts/build_form.py forms/회사양식.json   # 기본 양식을 바꾼다
    python3 scripts/build_form.py --check          # 양식 검사 + CSS 가 양식과 같은지(verify_repo 가 부른다)

양식 정의 하나를 HTML · PDF 와 Word 가 함께 읽는다. forms/ 의 양식은 모두 CSS 에 들어가고, 하나가 기본(:root)이며
나머지는 문서가 <div class="bd-doc" data-form="<id>"> 로 고른다(예: FCC/KC 대외 보고서는 hct-standard).
  HTML · PDF  blue-doc.css 의 `/* <form …> */ … /* </form> */` 블록(이 스크립트가 쓴다)의 --bd-* 변수
  Word        docx/from_doc.js 가 같은 JSON 을 직접 읽는다
그래서 여백 · 글자 크기 · 색 역할 · 머리말 · 꼬리말 · 표 · 결재란 값을 바꿀 때 CSS 와 Word 생성기를 따로 고치지 않는다.

양식 정의 규칙(검사한다)
  - 색은 hex 가 아니라 blue-report.css 토큰 이름(--br- 뒤, 예: "navy")만. 선을 없애려면 "none"
  - 길이는 단위를 붙인다 — px · pt · mm (A4 지면 794px = 210mm, 1pt = 1.333px)
  - 본문 10.5pt · 보조 9pt 하한을 지킨다(회사 규칙 — 넘치면 줄이지 말고 쪽을 나눈다)
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
FORMS = os.path.join(SKILL, "forms")
CSS = os.path.join(SKILL, "assets", "blue-doc.css")
TOKENS_CSS = os.path.join(SKILL, "assets", "blue-report.css")
DEFAULT = os.path.join(FORMS, "hct-standard.json")

BEGIN = re.compile(r"/\* <form [^>]*> .*?\*/")
BLOCK = re.compile(r"/\* <form [^>]*> .*?\*/.*?/\* </form> \*/", re.S)
LEN = re.compile(r"^-?\d+(\.\d+)?(px|pt|mm)$")
PAGE_SIZES = {"A4": ("794px", "1123px")}


def px(v):
    """'10.5pt' · '17mm' · '64px' → px(96dpi)."""
    m = LEN.match(str(v))
    if not m:
        raise ValueError(f"길이가 아니다: {v!r} — px · pt · mm 를 붙인다")
    n = float(v[:-2])
    return {"px": n, "pt": n * 96 / 72, "mm": n * 96 / 25.4}[m.group(2)]


def tokens():
    css = open(TOKENS_CSS, encoding="utf-8").read()
    return set(re.findall(r"--br-([a-z0-9-]+)\s*:", css))


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


import copy

DEFAULTS = {
    "font": {"body": {"web": "sans", "word": "Pretendard"}, "heading": {"web": "sans", "word": "Pretendard"}},
    "type": {
        "title": {"weight": 900, "align": "left", "font": "heading"},
        "subtitle": {"font": "body"},
        "h1": {"font": "heading", "style": "bar", "numeral": "keep",
               "box": {"numberWidth": "10mm", "fill": "tint", "rule": {"width": "1pt", "color": "text"}, "height": "10mm"}},
        "h2": {"weight": 700, "font": "heading"},
        "body": {"align": "left", "font": "body"},
    },
    "space": {"indent": "0px"},
    "list": {"marker": "•", "textIndent": "20px", "hang": "14px"},
    "numbering": {"legal": "({n})", "steps": "decimalEnclosedCircle"},
    "page": {"breaks": "authored"},
    "header": {"layout": "split", "center": "none",
               "title": {"size": "9pt", "weight": 700, "letterSpacing": "0em", "font": "heading", "spaceUpTo": 6, "color": "text"},
               "bands": {"top": [], "bottom": []}},
    "toc": {"style": "leader", "itemAfter": "9px"},
    "cover": {"mode": "off",
              "logo": {"height": "11mm"},
              "title": {"size": "26pt", "weight": 700, "letterSpacing": "0em", "font": "body", "top": "40mm", "color": "deep", "spaceUpTo": 6},
              "subtitle": {"size": "12pt", "color": "text-2", "gap": "4mm"},
              "rule": {"width": "60%", "gap": "10mm", "thick": {"color": "deep", "width": "0.6mm"}, "space": "0.5mm",
                       "thin": {"color": "cobalt", "width": "0.25mm"}},
              "meta": {"size": "10.5pt", "color": "text-2", "text": "{docNo} · {dept} · {date}"},
              "company": {"size": "13pt", "weight": 700, "font": "body", "color": "deep", "gap": "5mm", "bottom": "10mm", "text": "{company}"}},
}


def _merge(base, over):
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def resolve(spec):
    """양식에 없는 항목을 기본값으로 채운다. Word 생성기는 이 결과(doc_to_docx.py 가 넘긴다)를 읽어
    HTML 과 Word 가 같은 기본값을 쓴다."""
    s = copy.deepcopy(spec)
    f = s.get("font") or {}
    if isinstance(f.get("word"), str):          # 옛 모양 — font.word 하나
        f = {"body": {"web": "sans", "word": f["word"]}, "heading": {"web": "sans", "word": f["word"]}}
    s["font"] = f
    cv = s.get("cover") or {}
    if "enabled" in cv and "mode" not in cv:                      # 옛 모양
        cv["mode"] = "always" if cv.pop("enabled") else "off"
    if "word" in s and "pageBreak" in s["word"] and "breaks" not in s.get("page", {}):   # 옛 모양
        s.setdefault("page", {})["breaks"] = "flow" if s["word"]["pageBreak"] == "flow" else "authored"
    return _merge(DEFAULTS, s)


def validate(spec):
    """틀린 곳을 문장 목록으로. 비면 통과."""
    errs = []
    tok = tokens()
    for k in ("id", "name", "page", "type", "space", "header", "footer", "meta", "table", "sign"):
        if k not in spec:
            errs.append(f"「{k}」 가 없다")
    if errs:
        return errs
    spec = resolve(spec)
    if spec["page"].get("size") not in PAGE_SIZES:
        errs.append(f"page.size 는 {', '.join(PAGE_SIZES)} 만 — {spec['page'].get('size')}")

    COLOR_KEYS = {"color", "fill", "labelFill", "labelColor", "headFill", "headColor", "rowRule", "rule"}

    def walk(node, path):
        if isinstance(node, dict):
            for k, v in node.items():
                if k.startswith("_"):
                    continue
                p = f"{path}.{k}" if path else k
                if k in COLOR_KEYS and isinstance(v, str):
                    if v.startswith("#") or re.match(r"^[0-9a-fA-F]{6}$", v):
                        errs.append(f"{p} = {v} — hex 대신 토큰 이름을 쓴다")
                    elif v != "none" and v not in tok:
                        errs.append(f"{p} = {v} — blue-report.css 에 없는 토큰")
                elif isinstance(v, str) and re.match(r"^-?\d+(\.\d+)?[a-z%]*$", v) and k not in ("version",):
                    if not (LEN.match(v) or re.match(r"^-?\d+(\.\d+)?(em|%)$", v)):
                        errs.append(f"{p} = {v} — 길이는 px · pt · mm 를 붙인다(글자 간격은 em, 막대 폭은 %)")
                walk(v, p)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]")
    walk(spec, "")
    if errs:
        return errs
    t = spec["type"]
    if px(t["body"]["size"]) < px("10.5pt") - 0.01:
        errs.append(f"type.body.size {t['body']['size']} — 본문 하한 10.5pt")
    if px(t["small"]["size"]) < px("9pt") - 0.01:
        errs.append(f"type.small.size {t['small']['size']} — 보조 글자 하한 9pt")
    for k in ("title", "h1", "h2"):
        if px(t[k]["size"]) < px(t["body"]["size"]):
            errs.append(f"type.{k}.size 가 본문보다 작다")
    ONE = {
        "type.title.align": (t["title"]["align"], ("left", "center")),
        "type.body.align": (t["body"]["align"], ("left", "justify")),
        "type.h1.style": (t["h1"]["style"], ("bar", "box")),
        "type.h1.numeral": (t["h1"]["numeral"], ("keep", "roman")),
        "header.layout": (spec["header"]["layout"], ("split", "logo-title")),
        "toc.style": (spec["toc"]["style"], ("leader", "plain")),
        "numbering.legal": (spec["numbering"]["legal"], ("({n})", "circled")),
        "numbering.steps": (spec["numbering"]["steps"], ("decimalEnclosedCircle", "decimal")),
        "page.breaks": (spec["page"]["breaks"], ("authored", "flow")),
        "cover.mode": (spec["cover"]["mode"], ("off", "opt-in", "always")),
    }
    for k, (v, ok) in ONE.items():
        if v not in ok:
            errs.append(f"{k} = {v} — {' · '.join(ok)} 만")
    for k in ("body", "heading"):
        if spec["font"][k].get("web") not in ("sans", "serif"):
            errs.append(f"font.{k}.web 은 sans(Pretendard) · serif(Noto Serif KR) 만")
        if not spec["font"][k].get("word"):
            errs.append(f"font.{k}.word 가 비었다 — Word 에 적을 글꼴 이름")
    for key in ("title", "subtitle", "h1", "h2", "body"):
        if t[key]["font"] not in ("body", "heading"):
            errs.append(f"type.{key}.font 는 body · heading")
    for k in ("left", "right", "center"):
        if spec["header"].get(k, "none") not in ("logo", "docNo", "title", "company", "none"):
            errs.append(f"header.{k} 는 logo · docNo · title · company · none")
    if spec["footer"].get("font", "body") not in ("body", "heading"):
        errs.append("footer.font 는 body · heading")
    for k in ("left", "right"):
        v = spec["footer"].get(k, "")
        if not isinstance(v, str) or '"' in v or "\\" in v:
            errs.append(f"footer.{k} 는 글 틀 문자열 — 큰따옴표 · 역슬래시를 쓰지 않는다")
        for ph in re.findall(r"\{([^}]*)\}", v):
            if ph not in ("company", "title", "docNo", "page", "pages"):
                errs.append(f"footer.{k} 의 {{{ph}}} — company · title · docNo · page · pages 만")
    for side in ("top", "bottom"):
        for i, st in enumerate(spec["header"]["bands"].get(side, [])):
            if not (("color" in st and "width" in st) or "gap" in st):
                errs.append(f"header.bands.{side}[{i}] 는 {{color, width}} 또는 {{gap}}")
    if not spec["sign"].get("labels"):
        errs.append("sign.labels 가 비었다")
    return errs


def color(v):
    return "transparent" if v == "none" else f"var(--br-{v})"


SERIF_FACE = """@font-face {
  font-family:'HCT Serif'; font-weight:400; font-style:normal; font-display:swap;
  src:url('fonts/NotoSerifKR-Regular.subset.woff2') format('woff2');
}
@font-face {
  font-family:'HCT Serif'; font-weight:700; font-style:normal; font-display:swap;
  src:url('fonts/NotoSerifKR-Bold.subset.woff2') format('woff2');
}"""


def stripes(items):
    """띠 목록 → (높이, linear-gradient). 위에서 아래로."""
    y, stops = 0.0, []
    for st in items:
        h = px(st["width"] if "width" in st else st["gap"])
        c = color(st["color"]) if "color" in st else "transparent"
        stops.append(f"{c} {y:g}px {y + h:g}px")
        y += h
    return y, (f"linear-gradient(to bottom, {', '.join(stops)})" if stops else "none")


def css_block(spec, active=True):
    """양식 하나의 CSS. active 면 :root 변수(data-form 없는 문서의 기본), 아니면 .bd-doc[data-form="id"] 안에만."""
    spec = resolve(spec)
    fid = spec["id"]
    var_sel = ":root" if active else f'.bd-doc[data-form="{fid}"]'
    scope = (f':is(.bd-doc:not([data-form]), .bd-doc[data-form="{fid}"])' if active else f'.bd-doc[data-form="{fid}"]')
    t, s, h, f, m, tb, sg = (spec[k] for k in ("type", "space", "header", "footer", "meta", "table", "sign"))
    W, H = PAGE_SIZES[spec["page"]["size"]]
    mg = spec["page"]["margin"]
    bar = t["h1"].get("bar") or {}
    bar_w = bar.get("width", "0px")
    has_bar = t["h1"]["style"] == "bar" and px(bar_w) > 0
    fam = {k: ("'HCT Serif', 'Noto Serif KR', 'Batang', serif" if spec["font"][k]["web"] == "serif" else "var(--br-font-kr)")
           for k in ("body", "heading")}
    font_of = lambda key: f"var(--bd-font-{t[key]['font']})"
    top_h, top_bg = stripes(h["bands"]["top"])
    bot_h, bot_bg = stripes(h["bands"]["bottom"])
    lst = spec["list"]
    lines = [
        ("--bd-form", f'"{spec["id"]}"', "양식 id"),
        ("--bd-page-w", W, ""), ("--bd-page-h", H, ""),
        ("--bd-pad", f'{mg["top"]} {mg["right"]} {mg["bottom"]} {mg["left"]}', "지면 여백 위 · 오른 · 아래 · 왼"),
        ("--bd-r-box", spec.get("box", {}).get("radius", "10px"), "상자 모서리"),
        ("--bd-font-body", fam["body"], "본문 글꼴"), ("--bd-font-heading", fam["heading"], "제목 글꼴"),
        ("--bd-fs-title", t["title"]["size"], ""), ("--bd-fw-title", str(t["title"].get("weight", 900)), ""),
        ("--bd-c-title", color(t["title"]["color"]), ""), ("--bd-title-align", t["title"].get("align", "left"), ""),
        ("--bd-ff-title", font_of("title"), ""),
        ("--bd-fs-subtitle", t["subtitle"]["size"], ""), ("--bd-c-subtitle", color(t["subtitle"]["color"]), ""),
        ("--bd-ff-subtitle", font_of("subtitle"), ""),
        ("--bd-fs-h1", t["h1"]["size"], "장 제목"), ("--bd-c-h1", color(t["h1"]["color"]), ""),
        ("--bd-ff-h1", font_of("h1"), ""),
        ("--bd-h1-bar-w", bar_w if has_bar else "0px", "장 제목 왼쪽 표시 — 0 이면 없음"),
        ("--bd-c-h1-bar", color(bar.get("color", "none")), ""),
        ("--bd-h1-pad", "12px" if has_bar else "0px", ""),
        ("--bd-fs-h2", t["h2"]["size"], "절 제목"), ("--bd-c-h2", color(t["h2"]["color"]), ""),
        ("--bd-fw-h2", str(t["h2"]["weight"]), ""), ("--bd-ff-h2", font_of("h2"), ""),
        ("--bd-fs-body", t["body"]["size"], "본문 — 하한"), ("--bd-c-text", color(t["body"]["color"]), ""),
        ("--bd-lh", str(t["body"]["lineHeight"]), "본문 행간"), ("--bd-align", t["body"]["align"], "본문 정렬"),
        ("--bd-ff-body", font_of("body"), ""),
        ("--bd-font-num", "var(--bd-ff-body)", "숫자(표 · 쪽번호 · 목차 쪽 · 막대 값) — 본문과 같은 글꼴. Word 도 본문 글꼴로 낸다"),
        ("--bd-fs-small", t["small"]["size"], "표 안 보조 · 각주 · 쪽번호 (본문 아님)"),
        ("--bd-c-key", color(t["key"]["color"]), "강조어"),
        ("--bd-sp-title", s["titleAfter"], ""), ("--bd-sp-subtitle", s["subtitleAfter"], ""),
        ("--bd-sp-h1-before", s["h1Before"], ""), ("--bd-sp-h1-after", s["h1After"], ""),
        ("--bd-sp-h2-before", s["h2Before"], ""), ("--bd-sp-h2-after", s["h2After"], ""),
        ("--bd-sp-para", s["paraAfter"], ""), ("--bd-sp-li", s["listItemAfter"], ""), ("--bd-sp-block", s["blockAfter"], ""),
        ("--bd-indent", s["indent"], "본문 들여쓰기 — 절 제목 · 문단 · 목록 · 목차"),
        ("--bd-list-pad", lst["textIndent"], "목록 글 시작(들여쓰기 기준)"),
        ("--bd-list-hang", lst["hang"], "목록 표시 — 글보다 이만큼 왼쪽"),
        ("--bd-head-left", f'"{h["left"]}"', "머리말 — logo · docNo · title · company · none (doc-viewer.js 가 읽는다)"),
        ("--bd-head-right", f'"{h["right"]}"', ""),
        ("--bd-head-center", f'"{h["center"]}"', ""),
        ("--bd-head-layout", f'"{h["layout"]}"', "split(좌우) · logo-title(로고 · 가운데 문서명)"),
        ("--bd-foot-left", f'"{f["left"]}"', "꼬리말 글 틀 — {company} {title} {docNo} {page} {pages}. 둘 다 비면 꼬리말 없음"),
        ("--bd-foot-right", f'"{f["right"]}"', ""),
        ("--bd-c-head", color(h["color"]), "머리말"), ("--bd-c-head-rule", color(h["rule"]), ""),
        ("--bd-head-pad", h["padding"], ""), ("--bd-head-gap", h["gap"], ""), ("--bd-logo-h", h["logoHeight"], ""),
        ("--bd-c-foot", color(f["color"]), "꼬리말"), ("--bd-c-foot-rule", color(f["rule"]), ""),
        ("--bd-foot-pad", f["padding"], ""), ("--bd-foot-gap", f["gap"], ""),
        ("--bd-meta-k-w", m["labelWidth"], "문서 정보 표"), ("--bd-c-meta-k-bg", color(m["labelFill"]), ""),
        ("--bd-c-meta-k", color(m["labelColor"]), ""), ("--bd-meta-top-w", m["topRule"]["width"], ""),
        ("--bd-c-meta-top", color(m["topRule"]["color"]), ""), ("--bd-c-meta-rule", color(m["rowRule"]), ""),
        ("--bd-c-th-bg", color(tb["headFill"]), "표"), ("--bd-c-th", color(tb["headColor"]), ""),
        ("--bd-th-top-w", tb["headRule"]["top"], ""), ("--bd-th-bottom-w", tb["headRule"]["bottom"], ""),
        ("--bd-c-th-rule", color(tb["headRule"]["color"]), ""), ("--bd-c-td-rule", color(tb["rowRule"]), ""),
        ("--bd-cell-py", tb["cellPadding"]["y"], ""), ("--bd-cell-px", tb["cellPadding"]["x"], ""),
        ("--bd-c-sign-k-bg", color(sg["labelFill"]), "결재란"), ("--bd-c-sign-k", color(sg["labelColor"]), ""),
        ("--bd-c-sign-rule", color(sg["rule"]), ""), ("--bd-sign-h", sg["height"], ""), ("--bd-sign-gap", sg["gap"], ""),
        ("--bd-numeral", f'"{t["h1"]["numeral"]}"', "장 번호 — keep(쓴 그대로) · roman(1. → Ⅰ)"),
        ("--bd-cover", f'"{spec["cover"]["mode"]}"', "표지 — off · opt-in(data-doc-cover=\"yes\" 문서만) · always. doc-viewer.js 가 첫 쪽 앞에 만든다"),
        ("--bd-cover-company", f'"{spec["cover"]["company"]["text"]}"', "표지 회사명 — {company} 는 brand.json 회사명"),
        ("--bd-cover-meta", f'"{spec["cover"]["meta"]["text"]}"', "표지 문서 정보 줄 — {docNo} {dept} {date}, 빈 칸은 빠진다"),
        ("--bd-breaks", f'"{spec["page"]["breaks"]}"', "쪽 나눔 — authored(원본 쪽 그대로) · flow(이어 흘려 저절로)"),
        ("--bd-head-title-max", str(h["title"]["spaceUpTo"]), "머리말 문서명 — 이 글자 수까지만 넓게 벌린다"),
        ("--bd-cover-title-max", str(spec["cover"]["title"]["spaceUpTo"]), "표지 문서명 — 이 글자 수까지만 넓게 벌린다"),
    ]
    out = [f"/* 양식 {fid}{' (기본 — data-form 없는 문서)' if active else ''} */", var_sel + " {"]
    for k, v, note in lines:
        out.append(f"  {k}: {v};" + (f"  /* {note} */" if note else ""))
    out.append("}")

    # ── 짜임 선택지 — 양식이 고른 것만 쓴다. 기본 양식이면 아무것도 붙지 않는다 ─────────
    rules = []
    if h["layout"] == "split" and (top_h or bot_h):
        # 좌우 머리말 + 아래 · 위 띠 — 문서명(왼쪽 또는 오른쪽)을 header.title 글꼴 · 크기 · 색으로
        ht = h["title"]
        rules.append(f"""/* 머리말 — 좌우(문서명 · 로고) · 위아래 띠 */
.bd-doc .bd-head {{ display:flex; justify-content:space-between; align-items:center; border-bottom:0;
  padding:calc({top_h:g}px + var(--bd-head-pad)) 0 calc({bot_h:g}px + var(--bd-head-pad));
  background:{top_bg} top / 100% {top_h:g}px no-repeat, {bot_bg} bottom / 100% {bot_h:g}px no-repeat; }}
.bd-doc .bd-head .bd-doctitle {{ font:{ht['weight']} {ht['size']}/1 var(--bd-font-{ht['font']}); color:{color(ht.get('color', 'text'))};
  letter-spacing:{ht['letterSpacing']}; white-space:nowrap; }}""")
    elif h["layout"] == "logo-title" or top_h or bot_h:
        ht = h["title"]
        rules.append(f"""/* 머리말 — 로고 · 가운데 문서명 · 위아래 띠 */
.bd-doc .bd-head {{ display:grid; grid-template-columns:1fr auto 1fr; align-items:center; border-bottom:0;
  padding:calc({top_h:g}px + var(--bd-head-pad)) 0 calc({bot_h:g}px + var(--bd-head-pad));
  background:{top_bg} top / 100% {top_h:g}px no-repeat, {bot_bg} bottom / 100% {bot_h:g}px no-repeat; }}
.bd-doc .bd-head > :first-child {{ justify-self:start; }}
.bd-doc .bd-head > :last-child {{ justify-self:end; }}
.bd-doc .bd-head .bd-head-title {{ font:{ht['weight']} {ht['size']}/1 var(--bd-font-{ht['font']}); color:var(--bd-c-text);
  letter-spacing:{ht['letterSpacing']}; margin-right:-{ht['letterSpacing']}; white-space:nowrap; }}
.bd-doc .bd-head .bd-head-title.is-long {{ letter-spacing:.04em; margin-right:0; }}""")
    if not (f["left"] or f["right"]):
        rules.append("/* 꼬리말 없음 */\n.bd-doc .bd-foot { display:none; }")
    elif f.get("font") in ("body", "heading"):
        rules.append(f"/* 꼬리말 글꼴 — 본문과 같은 계열 */\n.bd-doc .bd-foot {{ font-family:var(--bd-font-{f['font']}); }}")
    if t["h1"]["style"] == "box":
        bx = t["h1"]["box"]
        # 1.58 — 표가 아니라 문단 하나: 위아래 선 사이에 번호 꼬리표 · 제목. Word 도 문단으로 그려
        # 어떤 프로그램에서 열어도 「다음 문단과 함께」가 지켜진다(표는 프로그램마다 달라 제목만 쪽 끝에 남았다)
        rules.append(f"""/* 장 제목 — 위아래 선 · 번호 꼬리표 · 제목(문단 하나) */
.bd-doc .bd-h1 {{ display:flex; align-items:center; padding:5pt 0; border-left:0; min-height:0;
  border-top:{bx['rule']['width']} solid {color(bx['rule']['color'])}; border-bottom:{bx['rule']['width']} solid {color(bx['rule']['color'])}; }}
.bd-doc .bd-h1 .bd-h1-n {{ flex:none; display:inline-flex; align-items:center; justify-content:center; padding:.5mm 2.2mm; margin-right:3mm;
  background:{color(bx['fill'])};{(' color:' + color(bx['numberColor']) + ';') if bx.get('numberColor') else ''} }}
.bd-doc .bd-h1 .bd-h1-t {{ letter-spacing:.08em; }}""")
    if lst["marker"] != "•":
        rules.append(f"""/* 목록 표시 「{lst['marker']}」 */
.bd-doc .bd-list:not(.bd-list--legal) {{ list-style:none; }}
.bd-doc .bd-list:not(.bd-list--legal) > li {{ position:relative; }}
.bd-doc .bd-list:not(.bd-list--legal) > li::before {{ content:"{lst['marker']}"; position:absolute; left:calc(-1 * var(--bd-list-hang)); }}""")
    if spec["numbering"]["legal"] == "circled":
        syms = " ".join(f'"{chr(0x2460 + i)}"' for i in range(20))
        rules.append(f"""/* 규정 호 번호 ①② */
@counter-style hct-circled {{ system:fixed; symbols:{syms}; suffix:" "; }}
.bd-doc .bd-list--legal > li::before {{ content:counter(bd-legal, hct-circled); font-family:var(--bd-font-body); font-weight:400; color:inherit; }}""")
    if spec["numbering"]["steps"] == "decimal":
        rules.append("""/* 절차 번호 1. 2. */
.bd-doc .bd-step::before { content:counter(bd-step) "."; background:none; color:var(--bd-c-text); width:auto; height:auto;
  font:700 var(--bd-fs-body)/inherit var(--bd-font-body); top:0; }""")
    if spec["toc"]["style"] == "plain":
        rules.append(f"""/* 목차 — 점선 · 쪽번호 없이 */
.bd-doc .bd-toc .bd-toc-d, .bd-doc .bd-toc .bd-toc-p {{ display:none; }}
.bd-doc .bd-toc li {{ margin-bottom:{spec['toc']['itemAfter']}; }}
.bd-doc .bd-toc .bd-toc-t {{ font-family:var(--bd-font-heading); color:var(--bd-c-text); }}
.bd-doc .bd-toc li.bd-toc--sub {{ padding-left:5mm; }}
.bd-doc .bd-toc li.bd-toc--sub .bd-toc-t {{ font-family:var(--bd-font-body); color:var(--bd-c-text); }}""")
    if spec["cover"]["mode"] != "off":
        c = spec["cover"]
        r, t = c["rule"], c["title"]
        t1, sp, t2 = px(r["thick"]["width"]), px(r["space"]), px(r["thin"]["width"])
        rules.append(f"""/* 표지 — doc-viewer.js 가 첫 쪽 앞에 만든다. 가운데 정렬 · 오른쪽 위 로고 · 두 줄 선 */
.bd-doc .bd-cover .bd-body {{ display:flex; flex-direction:column; align-items:center; text-align:center; }}
.bd-doc .bd-cover .bd-cover-logo {{ align-self:flex-end; }}
.bd-doc .bd-cover .bd-cover-logo .br-mark {{ position:static; margin:0; }}
.bd-doc .bd-cover .bd-cover-logo img {{ height:{c['logo']['height']}; width:auto; display:block; }}
.bd-doc .bd-cover .bd-cover-title {{ margin:{t['top']} 0 0; max-width:85%; font:{t['weight']} {t['size']}/1.3 var(--bd-font-{t['font']});
  letter-spacing:{t['letterSpacing']}; color:{color(t.get('color', 'text'))}; }}
.bd-doc .bd-cover .bd-cover-sub {{ margin-top:{c['subtitle']['gap']}; max-width:85%; font:400 {c['subtitle']['size']}/1.6 var(--bd-font-body); color:{color(c['subtitle']['color'])}; }}
.bd-doc .bd-cover .bd-cover-rule {{ width:{r['width']}; height:{t1 + sp + t2:g}px; margin-top:{r['gap']};
  background:linear-gradient(to bottom, {color(r['thick']['color'])} 0 {t1:g}px, transparent {t1:g}px {t1 + sp:g}px, {color(r['thin']['color'])} {t1 + sp:g}px {t1 + sp + t2:g}px); }}
.bd-doc .bd-cover .bd-cover-meta {{ margin-top:auto; font:400 {c['meta']['size']}/1.6 var(--bd-font-body); color:{color(c['meta']['color'])}; }}
.bd-doc .bd-cover .bd-cover-company {{ margin:{c['company']['gap']} 0 {c['company']['bottom']}; font:{c['company']['weight']} {c['company']['size']}/1.2 var(--bd-font-{c['company']['font']});
  color:{color(c['company']['color'])}; }}""")
    out.extend(r.replace(".bd-doc ", scope + " ") for r in rules)
    return "\n".join(out)


def all_forms():
    """forms/*.json (시험용 _test/ 는 빼고) — 문서는 data-form 으로 어느 것이든 고른다."""
    out = []
    for fn in sorted(os.listdir(FORMS)):
        if fn.endswith(".json"):
            out.append(load(os.path.join(FORMS, fn)))
    return out


def generate(active_spec, extra=()):
    """생성 블록 전체 — 기본(active) 양식은 :root, 나머지 양식은 data-form 범위. 명조가 필요하면 글꼴을 한 번 선언한다."""
    others = [f for f in list(all_forms()) + list(extra) if f["id"] != active_spec["id"]]
    seen, uniq = set(), []
    for f in others:
        if f["id"] not in seen:
            seen.add(f["id"]); uniq.append(f)
    forms = [active_spec] + uniq
    head = (f"/* <form {active_spec['id']}> 생성 — forms/*.json 에서 scripts/build_form.py 가 쓴다. 손으로 고치지 않는다.\n"
            f"   기본 양식 {active_spec['id']} 은 :root, 다른 양식은 <div class=\"bd-doc\" data-form=\"<id>\"> 로 문서마다 고른다. */")
    parts = [head]
    if any("serif" in (resolve(f)["font"]["body"]["web"], resolve(f)["font"]["heading"]["web"]) for f in forms):
        parts.append(SERIF_FACE)
    parts += [css_block(f, active=(i == 0)) for i, f in enumerate(forms)]
    parts.append("/* </form> */")
    return "\n".join(parts)


def active_id(css_path=CSS):
    m = re.search(r'--bd-form:\s*"([^"]+)"', open(css_path, encoding="utf-8").read())
    return m.group(1) if m else "hct-standard"


def find_form(fid):
    for p in (os.path.join(FORMS, fid + ".json"), os.path.join(FORMS, "_test", fid + ".json")):
        if os.path.exists(p):
            return p
    return None


def main():
    ap = argparse.ArgumentParser(description="A4 양식 정의 → blue-doc.css 생성 블록")
    ap.add_argument("form", nargs="?", help="기본(active)으로 쓸 양식 JSON — 주지 않으면 지금 기본 양식")
    ap.add_argument("--check", action="store_true", help="고치지 않고 검사만 — 다르면 종료 코드 1")
    ap.add_argument("--css", default=CSS, help="쓸 blue-doc.css (기본: 스킬의 assets/blue-doc.css) — 시험용 복사본에 쓸 때")
    a = ap.parse_args()
    css_path = a.css
    form_path = a.form or find_form(active_id(css_path)) or DEFAULT

    spec = load(form_path)
    bad = []
    for f in [spec] + all_forms():
        errs = validate(f)
        if errs:
            bad.append((f.get("id", "?"), errs))
    if bad:
        for fid, errs in bad:
            print(f"[실패] 양식 정의 {fid}")
            for e in errs:
                print(f"  - {e}")
        return 1
    block = generate(spec, extra=[spec])
    css = open(css_path, encoding="utf-8").read()
    if not BLOCK.search(css):
        print(f"[실패] {css_path} 에 생성 블록 표시(/* <form …> */ … /* </form> */)가 없다")
        return 1
    new = BLOCK.sub(lambda _: block, css, count=1)
    names = ", ".join(f["id"] for f in all_forms() if f["id"] != spec["id"])
    if a.check:
        if new != css:
            print(f"[실패] blue-doc.css 가 양식 정의와 다르다 — python3 scripts/build_form.py {os.path.relpath(form_path, SKILL)}")
            return 1
        print(f"양식 — 기본 {spec['id']}" + (f" · data-form 으로 {names}" if names else "") + " — 검사 통과 · CSS 일치")
        return 0
    if new != css:
        open(css_path, "w", encoding="utf-8").write(new)
        print(f"양식 — 기본 {spec['id']}" + (f" · data-form 으로 {names}" if names else "") + f" → {css_path}")
    else:
        print(f"양식 기본 {spec['id']} — 바뀐 것 없음")
    return 0


if __name__ == "__main__":
    sys.exit(main())
