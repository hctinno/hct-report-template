#!/usr/bin/env python3
"""A4 문서(.bd-doc) HTML 을 회사 양식 Word(.docx)로 옮긴다 — 한 문서를 HTML · PDF · Word 셋 다로.

    python3 scripts/doc_to_docx.py decks-out/회의록.html --brand brand/hct/brand.json -o decks-out/회의록.docx

내용은 HTML 한 곳에만 있고 Word 는 거기서 뽑는다. 두 판을 따로 고치지 않는다.
덱에서 PPTX 를 뽑는 deck_to_pptx.py 와 같은 방식이다.

그림으로 찍지 않는다. 글자 · 표 · 목록 · 상자는 전부 Word 의 글자와 표로 옮겨서 Word 에서 고칠 수 있다.

  부품(blue-doc.css)            Word
  머리말 로고 · 문서번호        머리글 (로고 그림 + 오른쪽 탭 문서번호)
  꼬리말 회사 · 문서명 · 쪽번호  바닥글 (쪽번호는 Word 필드 — n / 전체)
  .bd-title · .bd-subtitle      스타일 「HCT 표제」 · 「HCT 부제」
  .bd-meta                      문서 정보 표 (라벨 칸 음영)
  .bd-h1 · .bd-h2               제목 1 · 제목 2 (탐색 창 · 목차에 잡힌다)
  .bd-p                         본문
  .bd-list                      글머리 목록 · .bd-list--legal 은 (1) (2) 글자 번호
  .bd-table(--grid)             표 (머리글 행 반복)
  .bd-key · .bd-chip            굵은 남색 글자 · 테두리 · 음영 글자
  .bd-callout(--danger|--info)  테두리 · 음영 문단
  .bd-steps                     번호 목록 (Word 자동 번호 — 끼워 넣으면 다시 매겨진다)
  .bd-toc                       점선 탭 목차
  .bd-figure                    1칸 표 (그림 · 자리 + 캡션)
  .bd-sign                      결재란 표
  .bd-kpis · .bd-bars          수치 표 · 막대 표 (Word 에 없는 부품이라 표로 그린다. 옛 x- 이름도 읽는다)

모르는 부품은 글자를 잃지 않게 문단으로 옮기고 경고를 남긴다. 경고가 있으면 결과를 열어 본다.

양식 값(여백 · 글자 크기 · 색 역할 · 머리말 · 꼬리말 · 표 · 결재란 · 번호 모양)은 양식 정의 forms/<id>.json 에서 온다.
HTML · PDF 도 같은 파일에서 온다(scripts/build_form.py → blue-doc.css). 양식은 HTML 이 쓴 것(--bd-form)을 따른다.

중간 산출물(manifest.json)은 --keep 폴더에 남길 수 있다.
"""
import argparse
import base64
import html as htmlmod
import json
import os
import re
import subprocess
import sys
import tempfile
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
DOCX_DIR = os.path.join(SKILL, "docx")
FORMS = os.path.join(SKILL, "forms")
DOC_CSS = os.path.join(SKILL, "assets", "blue-doc.css")
sys.path.insert(0, HERE)
from ensure_deps import need_node_modules  # noqa: E402

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


# ── 작은 DOM ──────────────────────────────────────────────────────────────
# 표준 라이브러리만 쓴다. Word 변환에는 브라우저가 필요 없다.
# 옛 이름(x-, 보고서 견본 한 장의 맞춤 부품) → 공용 부품 이름(blue-doc.css)
CLASS_ALIAS = {
    "x-kpis": "bd-kpis", "x-kpi-k": "bd-kpi-k", "x-kpi-v": "bd-kpi-v", "x-kpi-d": "bd-kpi-d", "x-bad": "is-bad",
    "x-bars": "bd-bars", "x-bars-t": "bd-bars-t", "x-bars-s": "bd-bars-s", "x-bar": "bd-bar", "x-bar-k": "bd-bar-k",
    "x-bar-f": "bd-bar-f", "x-bar-v": "bd-bar-v", "x-main": "is-main",
}


class Node:
    __slots__ = ("tag", "attrs", "children", "parent", "text")

    def __init__(self, tag, attrs=None, parent=None, text=None):
        self.tag, self.attrs, self.parent, self.text = tag, dict(attrs or {}), parent, text
        self.children = []

    @property
    def cls(self):
        return (self.attrs.get("class") or "").split()

    def has(self, c):
        # 1.58 — 수치 표 · 막대가 공용 부품(bd-kpis · bd-bars)이 됐다. 옛 견본의 x- 이름도 그대로 읽는다
        return c in self.cls or (c in CLASS_ALIAS and CLASS_ALIAS[c] in self.cls)

    def els(self):
        return [c for c in self.children if c.tag]

    def find_all(self, pred):
        out = []
        for c in self.children:
            if c.tag:
                if pred(c):
                    out.append(c)
                out.extend(c.find_all(pred))
        return out

    def find(self, pred):
        r = self.find_all(pred)
        return r[0] if r else None

    def text_content(self):
        if self.tag is None:
            return self.text
        return "".join(c.text_content() for c in self.children)


class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root")
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs, self.cur)
        self.cur.children.append(n)
        if tag not in VOID:
            self.cur = n

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(Node(tag, attrs, self.cur))

    def handle_endtag(self, tag):
        n = self.cur
        while n is not None and n.tag != tag:
            n = n.parent
        if n is not None and n.parent is not None:
            self.cur = n.parent

    def handle_data(self, data):
        if self.cur.tag in ("script", "style"):
            return
        self.cur.children.append(Node(None, parent=self.cur, text=data))


def parse(html):
    t = Tree()
    t.feed(html)
    return t.root


# ── 글자 조각(runs) ────────────────────────────────────────────────────────
# run = {t, b?, i?, color?, chip?, num?, size?}
#   color: 토큰 이름(navy · text2 · okText · alertText …). 색 값은 생성기가 tokens.js 에서 읽는다.
#   chip:  ""(기본) · "warn" · "late"
WARN = []


def runs(el, base=None):
    base = dict(base or {})
    out = []

    def push(t, st):
        if not t:
            return
        if out and {k: v for k, v in out[-1].items() if k != "t"} == st and "\n" not in (t, out[-1]["t"]):
            out[-1]["t"] += t
        else:
            out.append(dict(st, t=t))

    def walk(n, st):
        for c in n.children:
            if c.tag is None:
                push(re.sub(r"\s+", " ", c.text), st)
                continue
            if c.tag in ("script", "style", "button"):
                continue
            if c.tag == "br":
                out.append(dict(st, t="\n"))
                continue
            s = dict(st)
            if c.tag in ("b", "strong"):
                s["b"] = True
            if c.tag in ("em", "i"):
                s["i"] = True
            if c.has("bd-key"):
                s.update(b=True, color="navy")
            if c.has("bd-chip"):
                s = {"chip": "warn" if c.has("bd-chip--warn") else "late" if c.has("bd-chip--late") else ""}
                push(re.sub(r"\s+", " ", c.text_content()).strip(), s)
                continue
            walk(c, s)

    walk(el, base)
    # 앞뒤 공백 · 줄바꿈 주변 공백 정리
    while out and not out[0]["t"].strip():
        out.pop(0)
    while out and not out[-1]["t"].strip():
        out.pop()
    if out:
        out[0]["t"] = out[0]["t"].lstrip()
        out[-1]["t"] = out[-1]["t"].rstrip()
    for i, r in enumerate(out):
        if r["t"] == "\n":
            if i > 0:
                out[i - 1]["t"] = out[i - 1]["t"].rstrip()
            if i + 1 < len(out):
                out[i + 1]["t"] = out[i + 1]["t"].lstrip()
    return [r for r in out if r["t"]]


def plain(el):
    return re.sub(r"\s+", " ", el.text_content() if el else "").strip()


def pct_width(el):
    m = re.search(r"width\s*:\s*([\d.]+)%", el.attrs.get("style") or "")
    return float(m.group(1)) if m else None


# ── 블록 ──────────────────────────────────────────────────────────────────
def img_src(img, base_dir):
    src = img.attrs.get("src") or ""
    if src.startswith("data:"):
        m = re.match(r"data:image/(png|jpe?g|gif);base64,(.*)", src, re.S)
        if not m:
            return None
        return {"type": "jpg" if m.group(1).startswith("j") else m.group(1), "data": m.group(2).strip()}
    if not src or "//" in src:
        return None
    p = os.path.normpath(os.path.join(base_dir, htmlmod.unescape(src)))
    if not os.path.exists(p):
        return None
    ext = os.path.splitext(p)[1].lower().lstrip(".")
    if ext not in ("png", "jpg", "jpeg", "gif"):
        return None
    with open(p, "rb") as f:
        return {"type": "jpg" if ext.startswith("j") else ext, "data": base64.b64encode(f.read()).decode()}


def block(el, base_dir):
    """요소 하나 → 블록 목록. 모르는 부품은 글자를 살려 문단으로."""
    c = el.has
    tag = el.tag
    if c("bd-title"):
        return [{"t": "title", "runs": runs(el)}]
    if c("bd-subtitle"):
        return [{"t": "subtitle", "runs": runs(el)}]
    if c("bd-h1"):
        return [{"t": "h1", "runs": runs(el)}]
    if c("bd-h2"):
        return [{"t": "h2", "runs": runs(el)}]
    if c("bd-p") or tag == "p" and not el.cls:
        return [{"t": "p", "runs": runs(el)}]
    if c("bd-meta"):
        cells = el.els()
        pairs = []
        i = 0
        while i < len(cells):
            if cells[i].has("bd-meta-k"):
                v = cells[i + 1] if i + 1 < len(cells) else None
                pairs.append([plain(cells[i]), runs(v) if v is not None else []])
                i += 2
            else:
                pairs.append(["", runs(cells[i])])
                i += 1
        return [{"t": "meta", "pairs": pairs}]
    if c("bd-list") or tag in ("ul", "ol") and not el.cls:
        legal = c("bd-list--legal")
        return [{"t": "list", "legal": legal, "ordered": tag == "ol" and not legal,
                 "items": [runs(li) for li in el.els() if li.tag == "li"]}]
    if c("bd-table") or tag == "table":
        head = el.find(lambda n: n.tag == "thead")
        body = el.find(lambda n: n.tag == "tbody") or el
        hrow = head.find(lambda n: n.tag == "tr") if head else None
        ths = [n for n in hrow.els() if n.tag in ("th", "td")] if hrow else []
        rows = []
        for tr in body.find_all(lambda n: n.tag == "tr"):
            if hrow is not None and tr is hrow:
                continue
            rows.append([{"runs": runs(td), "num": td.has("num"),
                          "span": int(td.attrs.get("colspan") or 1)}
                         for td in tr.els() if td.tag in ("td", "th")])
        return [{"t": "table", "grid": c("bd-table--grid"),
                 "widths": [pct_width(th) for th in ths],
                 "head": [{"runs": runs(th), "num": th.has("num"),
                           "span": int(th.attrs.get("colspan") or 1)} for th in ths],
                 "rows": rows}]
    if c("bd-callout"):
        kind = "danger" if c("bd-callout--danger") else "info" if c("bd-callout--info") else "warn"
        k = el.find(lambda n: n.has("bd-callout-k"))
        label = plain(k) if k else ""
        if k is not None:
            k.parent.children.remove(k)
        return [{"t": "callout", "kind": kind, "label": label, "runs": runs(el)}]
    if c("bd-steps"):
        items = []
        for st in el.els():
            t = st.find(lambda n: n.has("bd-step-t"))
            title = runs(t) if t else []
            if t is not None:
                t.parent.children.remove(t)
            items.append({"title": title, "runs": runs(st)})
        return [{"t": "steps", "items": items}]
    if c("bd-toc"):
        items = []
        for li in el.els():
            items.append({"title": plain(li.find(lambda n: n.has("bd-toc-t"))),
                          "page": plain(li.find(lambda n: n.has("bd-toc-p"))),
                          "sub": li.has("bd-toc--sub")})
        return [{"t": "toc", "items": items}]
    if c("bd-figure") or tag == "figure":
        img = el.find(lambda n: n.tag == "img")
        box = el.find(lambda n: n.has("bd-figure-box"))
        cap = el.find(lambda n: n.tag == "figcaption")
        data = img_src(img, base_dir) if img is not None else None
        if img is not None and data is None:
            WARN.append(f"그림을 읽지 못해 자리 상자로 둔다: {img.attrs.get('src', '')[:60]}")
        return [{"t": "figure", "img": data,
                 "alt": (img.attrs.get("alt") if img is not None else "") or plain(cap),
                 "placeholder": plain(box) if box is not None else ("그림" if data is None else ""),
                 "caption": runs(cap) if cap is not None else []}]
    if c("bd-sign"):
        return [{"t": "sign", "labels": [plain(d.find(lambda n: n.has("bd-sign-k"))) for d in el.els()]}]
    if c("x-kpis"):
        items = []
        for k in el.els():
            v = k.find(lambda n: n.has("x-kpi-v"))
            unit = v.find(lambda n: n.tag == "small") if v else None
            d = k.find(lambda n: n.has("x-kpi-d"))
            db = d.find(lambda n: n.tag == "b") if d else None
            note = re.sub(r"\s+", " ", "".join(x.text_content() for x in d.children if x is not db)).strip() if d else ""
            items.append({"k": plain(k.find(lambda n: n.has("x-kpi-k"))),
                          "v": re.sub(r"\s+", " ", "".join(x.text_content() for x in v.children if x is not unit)).strip() if v else "",
                          "unit": plain(unit), "delta": plain(db),
                          "bad": bool(db is not None and db.has("x-bad")), "note": note})
        return [{"t": "kpis", "items": items}]
    if c("x-bars"):
        items = []
        for b in el.find_all(lambda n: n.has("x-bar")):
            f = b.find(lambda n: n.has("x-bar-f"))
            items.append({"k": plain(b.find(lambda n: n.has("x-bar-k"))),
                          "pct": pct_width(f) if f is not None else 0,
                          "main": bool(f is not None and f.has("x-main")),
                          "v": plain(b.find(lambda n: n.has("x-bar-v")))})
        return [{"t": "bars", "title": plain(el.find(lambda n: n.has("x-bars-t"))),
                 "sub": plain(el.find(lambda n: n.has("x-bars-s"))), "items": items}]
    if tag == "img":
        data = img_src(el, base_dir)
        return [{"t": "figure", "img": data, "alt": el.attrs.get("alt") or "",
                 "placeholder": "" if data else "그림", "caption": []}] if data else []
    if tag in ("div", "section", "article") and any(e.tag in BLOCK_TAGS for e in el.els()):
        out = []
        for e in el.els():
            out.extend(block(e, base_dir))
        return out
    r = runs(el)
    if r:
        WARN.append(f"모르는 부품을 문단으로 옮겼다: <{tag} class=\"{' '.join(el.cls)}\"> {plain(el)[:30]}")
        return [{"t": "p", "runs": r}]
    return []


BLOCK_TAGS = {"div", "p", "h1", "h2", "h3", "h4", "ul", "ol", "table", "figure", "section", "img"}


def extract(path):
    with open(path, encoding="utf-8") as f:
        root = parse(f.read())
    base_dir = os.path.dirname(os.path.abspath(path))
    doc = root.find(lambda n: n.has("bd-doc"))
    if doc is None:
        sys.exit("[실패] .bd-doc 가 없다. A4 문서 템플릿(doc-*.html)으로 만든 HTML 이 아니다.")
    pages = doc.find_all(lambda n: n.has("bd-page"))
    if not pages:
        sys.exit("[실패] .bd-page 가 없다.")
    company = ""
    co = doc.find(lambda n: n.has("bd-company"))
    if co is not None:
        company = plain(co)
    title_el = root.find(lambda n: n.tag == "title")
    out = {"title": doc.attrs.get("data-doc-title") or plain(title_el),
           "docNo": doc.attrs.get("data-doc-no") or "",
           "cover": doc.attrs.get("data-doc-cover") or "",
           "dept": doc.attrs.get("data-doc-dept") or "", "date": doc.attrs.get("data-doc-date") or "",
           "subtitle": plain(doc.find(lambda n: n.has("bd-subtitle"))) if doc.find(lambda n: n.has("bd-subtitle")) is not None else "",
           "company": company, "pages": []}
    for pg in pages:
        blocks = []
        for e in pg.els():
            if e.has("bd-body"):
                for b in e.els():
                    blocks.extend(block(b, base_dir))
            elif e.has("bd-sign"):
                blocks.extend(block(e, base_dir))
            elif e.has("bd-head") or e.has("bd-foot"):
                continue
            else:
                blocks.extend(block(e, base_dir))
        out["pages"].append({"blocks": blocks})
    return out


def form_of(html_path):
    """이 HTML 이 쓴 양식. 한 파일로 묶은 HTML 은 blue-doc.css 를 품고 있어 그 안의 --bd-form 을 읽는다.
    링크로 부르는 HTML 이면 지금 blue-doc.css 의 양식. HTML 과 Word 가 다른 양식을 쓰지 않게 한다."""
    pat = re.compile(r'--bd-form:\s*"([^"]+)"')
    with open(html_path, encoding="utf-8") as f:
        html = f.read()
    # 문서가 고른 양식 — <div class="bd-doc" data-form="id">
    tag = re.search(r'<div[^>]*class="bd-doc[^"]*"[^>]*>', html)
    m = re.search(r'data-form="([^"]+)"', tag.group(0)) if tag else None
    if not m:
        m = pat.search(html)
    if not m:
        # 링크로 부르는 blue-doc.css — HTML 옆의 것을 먼저, 없으면 스킬의 것
        link = re.search(r'<link[^>]+href="([^"]*blue-doc\.css)"', html)
        cands = [os.path.join(os.path.dirname(os.path.abspath(html_path)), link.group(1))] if link else []
        for c in cands + [DOC_CSS]:
            if os.path.exists(c):
                with open(c, encoding="utf-8") as f:
                    m = pat.search(f.read())
                if m:
                    break
    fid = m.group(1) if m else "hct-standard"
    for p in (os.path.join(FORMS, fid + ".json"), os.path.join(FORMS, "_test", fid + ".json")):
        if os.path.exists(p):
            return p
    sys.exit(f"[실패] 양식 정의가 없다: forms/{fid}.json")


def main():
    ap = argparse.ArgumentParser(description="A4 문서 HTML → Word(.docx)")
    ap.add_argument("html", help="A4 문서 HTML (apply_brand.py 로 만든 것 또는 doc-*.html 견본)")
    ap.add_argument("--brand", required=True, help="brand.json — 로고 · 회사명")
    ap.add_argument("-o", "--out", required=True, help="출력 .docx")
    ap.add_argument("--keep", help="manifest.json 을 남길 폴더")
    ap.add_argument("--form", help="양식 정의 JSON — 주지 않으면 HTML 이 쓴 양식(--bd-form)")
    a = ap.parse_args()
    form = os.path.abspath(a.form) if a.form else form_of(a.html)

    need_node_modules(DOCX_DIR, "docx")
    man = extract(a.html)
    with tempfile.TemporaryDirectory() as tmp:
        work = a.keep or tmp
        os.makedirs(work, exist_ok=True)
        mpath = os.path.join(work, "manifest.json")
        with open(mpath, "w", encoding="utf-8") as f:
            json.dump(man, f, ensure_ascii=False, indent=1)
        # 양식 — 기본값을 채운 것을 넘긴다(build_form.resolve). HTML 이 쓰는 기본값과 같다
        from build_form import resolve, validate
        raw = json.load(open(form, encoding="utf-8"))
        errs = validate(raw)
        if errs:
            sys.exit("[실패] 양식 정의 " + form + "\n  - " + "\n  - ".join(errs))
        fpath = os.path.join(work, "form.json")
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(resolve(raw), f, ensure_ascii=False, indent=1)
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        r = subprocess.run(["node", os.path.join(DOCX_DIR, "from_doc.js"), mpath,
                            os.path.abspath(a.brand), os.path.abspath(a.out), fpath],
                           capture_output=True, text=True)
        sys.stderr.write(r.stderr)
        if r.returncode != 0:
            sys.exit(f"[실패] Word 생성기 오류 (종료 코드 {r.returncode})")
    n = sum(len(p["blocks"]) for p in man["pages"])
    print(f"Word  {a.out}  ({len(man['pages'])}쪽 · 블록 {n}개 · 양식 {os.path.splitext(os.path.basename(form))[0]})")
    for w in WARN:
        print(f"  주의  {w}")


if __name__ == "__main__":
    main()
