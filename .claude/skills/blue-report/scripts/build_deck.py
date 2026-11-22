#!/usr/bin/env python3
"""본문만 쓴 장을 받아 회사 덱으로 조립한다 — 틀은 이 스크립트가 씌운다.

에이전트(사람이든)는 본문만 쓴다. 머리띠 · 꼬리띠 · 쪽번호 · 로고 · 워터마크 · 폰트 · 진행선 ·
발표 기능은 이 스크립트가 붙이고, 표지 · 목차 · 장 간지 · 마무리 · 부록 간지는 조립 목록(plan)에서
만든다. 그래서 틀은 손으로 망가뜨릴 수 없고, 장을 더하거나 빼도 목차 · 간지가 저절로 맞는다.

    python3 build_deck.py 보고서.yaml --brand brand/hct/brand.json --single-file -o decks-out/보고서.html
    python3 build_deck.py 보고서.yaml --no-brand -o /tmp/x.html     # 자리표시자 그대로(점검용)

입력은 둘이다.
  · 조립 목록(YAML) — 표지 정보 · 장(章) 순서 · 장마다 넣을 장(張) id · 마무리 · 부록
  · 본문 파일(HTML) — <section id="…"> 마다 본문만. 형식은 아래 body_section() 설명과
    ../DESIGN.md 「1 · 2」에 있다.

장 자리에는 본문 파일의 id 말고도 라이브러리 장을 그대로 부를 수 있다.
    catalog:gantt        부품 카탈로그(live-catalog.html)의 #gantt
    patterns:pt-hub      패턴첩(live-patterns.html)의 #pt-hub
    standard:<id>        기준 덱(live-standard.html)에서 id 를 단 장
가져온 장의 머리띠 · 꼬리띠 · 로고는 떼고 이 덱의 것으로 다시 단다. 출처 칩의 근거도 따라온다.
"""
import argparse
import html as H
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")

LIBS = {"catalog": "live-catalog.html", "livecatalog": "live-catalog.html",
        "patterns": "live-patterns.html", "standard": "live-standard.html"}
LIB_PREFIX = {"live-catalog.html": "cat", "live-patterns.html": "pat", "live-standard.html": "std"}

MARK_PH = ('<div class="br-mark" data-on="{on}"><!-- 로고 자리: apply_brand.py 가 교체한다 -->'
           '<span class="br-wordmark">COMPANY NAME</span></div>')
WM_PH = ('<div class="br-watermark" data-on="{on}"><!-- 워터마크 자리: apply_brand.py 가 교체한다 -->'
         '<span class="br-wordmark">COMPANY NAME</span></div>')
FOOT = '<footer class="bl-rf"><span class="bl-rf-name"></span><span class="bl-pg"></span></footer>'

CHROME = [re.compile(r'\s*<header class="bl-hd"[^>]*>.*?</header>', re.S),
          re.compile(r'\s*<footer class="bl-rf"[^>]*>.*?</footer>', re.S),
          re.compile(r'\s*<div class="br-watermark"[^>]*>.*?</div>', re.S),
          re.compile(r'\s*<div class="br-mark"[^>]*>.*?</div>', re.S)]
ATTR = re.compile(r'([\w:-]+)(?:\s*=\s*"([^"]*)")?')


def die(msg):
    sys.exit("오류: " + msg)


# ── 읽기 ─────────────────────────────────────────────────────────────────────

def sections(html):
    """최상위 <section> 을 순서대로 [(여는 태그 속성 dict, 여는 태그, 안쪽)] 로 돌려준다.

    부품 안에도 <section> 이 들어 있어(.bl-vs-p 등) 깊이를 세며 자른다. <main> 이 있으면
    그 안만 본다 — 목업 안의 <main> 은 마지막 </main> 으로 피한다."""
    i = html.find('<main class="bl-deck"')
    if i >= 0:
        i = html.find(">", i) + 1
        html = html[i:html.rfind("</main>")]
    # 주석 · 스크립트 안의 「<section」 글자는 태그가 아니다 — 같은 길이의 빈칸으로 가리고 센다
    scan = re.sub(r"<!--.*?-->|<script\b.*?</script>", lambda m: " " * len(m.group(0)), html, flags=re.S)
    out, depth, start = [], 0, None
    for m in re.finditer(r"<section\b[^>]*>|</section>", scan):
        if m.group(0) == "</section>":
            depth -= 1
            if depth == 0 and start is not None:
                open_tag = html[start:html.find(">", start) + 1]
                inner = html[len(open_tag) + start:m.start()]
                out.append((parse_attrs(open_tag), open_tag, inner))
                start = None
        else:
            if depth == 0:
                start = m.start()
            depth += 1
    return out


def parse_attrs(tag):
    body = re.sub(r"^<section\b|>$", "", tag)
    return {k: (H.unescape(v) if v is not None else "") for k, v in ATTR.findall(body)}


_lib_cache = {}


def library(name):
    if name not in _lib_cache:
        path = os.path.join(ASSETS, name)
        src = open(path, encoding="utf-8").read()
        secs = {a.get("id"): (a, t, inner) for a, t, inner in sections(src) if a.get("id")}
        tail = src[src.rfind("</main>"):]
        m = re.search(r'<script type="application/json" id="bl-evidence">(.*?)</script>', tail, re.S)
        ev = json.loads(m.group(1)) if m else {}
        extra = {m.group(1): m.group(0) for m in re.finditer(
            r'<script type="(?:application/json|text/plain)" id="(?!bl-evidence)([^"]+)"[^>]*>.*?</script>',
            tail, re.S)}
        _lib_cache[name] = (secs, ev, extra)
    return _lib_cache[name]


# ── 틀 씌우기 ────────────────────────────────────────────────────────────────

def strip_chrome(inner):
    """본문에 틀이 섞여 들어왔으면 뗀다. 틀은 빌드가 단다."""
    n = 0
    for rx in CHROME:
        inner, k = rx.subn("", inner)
        n += k
    return inner, n


def plain(s):
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", "", s or ""))).strip()


def clean_name(name):
    """라이브러리 머리띠 이름에서 클래스 표기(.bl-x · data-x)를 뗀다 — 견본 설명이지 장 이름이 아니다."""
    n = re.sub(r"\s*\[?\.?(?:bl|br|pt)-[\w-]+\]?|\s*\[?data-[\w-]+\]?|&lt;.*?&gt;", "", plain(name))
    n = re.sub(r"\s*(?:—|·)\s*(?=(?:—|·|$))", "", n)
    return H.escape(re.sub(r"\s+", " ", n).strip(" ·—") or plain(name), quote=False)


def add_takeaway(inner, text):
    """본문 끝에 결론 줄(.bl-concl)을 붙인다. 라이브러리 장처럼 .bl-bd 가 이미 있으면 그 안 끝에."""
    line = f'\n  <p class="bl-concl bl-concl--ch">{text}</p>'
    if re.search(r'<div class="bl-bd\b', inner):
        i = inner.rfind("</div>")
        return inner[:i] + line + "\n    " + inner[i:]
    return inner.rstrip() + line + "\n"


def title_of(inner):
    m = re.search(r'<h[12][^>]*class="[^"]*\bbl-title\b[^"]*"[^>]*>(.*?)</h[12]>', inner, re.S)
    return plain(m.group(1)) if m else ""


STYLES = ("a", "c")
STYLE = "a"     # main() 이 조립 목록 style · --style 로 정한다


def band_inverts():
    """머리띠가 지면과 반대 색인가 — A 는 그렇고(짙은 띠), C 는 띠가 지면색이다."""
    return STYLE == "a"


def wrap(classes, attrs, code, name, inner, apx=False):
    """한 장을 완성한다 — 머리띠 · 본문 · 꼬리띠 · 워터마크.

    A 는 밝은 장의 띠가 짙어 머리띠 마크 data-on="dark" · 워터마크 "light",
    어두운 장은 그 반대다(마크가 앉는 곳은 지면이 아니라 띠다).
    C 는 띠가 지면색이라 마크도 지면과 같은 쪽이다."""
    dark = "bl-sl--dark" in classes
    cls = " ".join(dict.fromkeys(["bl-sl"] + [c for c in classes if c != "bl-sl"]))
    keep = {k: v for k, v in attrs.items()
            if k not in ("class", "data-name", "data-code", "data-toc", "data-sub", "data-bd", "data-apx")}
    if apx:
        keep["data-apx"] = ""
    at = "".join(f' {k}' if v == "" and k == "data-apx" else
                 f' {k}="{H.escape(v, quote=True).replace(chr(10), "&#10;")}"'
                 for k, v in keep.items())
    if not re.search(r'<div class="bl-bd\b', inner):
        bd = " ".join(["bl-bd"] + attrs.get("data-bd", "").split())
        inner = f'\n    <div class="{bd}">{inner.rstrip()}\n    </div>\n'
    head = (f'\n    <header class="bl-hd">\n      <span class="bl-code"><b>{code}</b>{name}</span>\n'
            f'      <span class="bl-sp"></span>\n      {MARK_PH.format(on=("light" if dark else "dark") if band_inverts() else ("dark" if dark else "light"))}\n'
            f'    </header>')
    return (f'  <section class="{cls}"{at}>{head}{inner.rstrip()}\n    {FOOT}\n'
            f'    {WM_PH.format(on="dark" if dark else "light")}\n  </section>\n')


# ── 구조용 장 — 조립 목록에서 만든다 ─────────────────────────────────────────

def cover_slide(c, title):
    pres = c.get("presenter") or {}
    sig = ""
    if pres:
        role = f' <em>{pres["role"]}</em>' if pres.get("role") else ""
        sig = f'\n    <div class="bl-sig"><span>{pres.get("team", "")}</span><b>{pres.get("name", "")}{role}</b></div>'
    tag = f'<span class="bl-tag">{c["tag"]}</span>' if c.get("tag") else ""
    kick = f'\n      <p class="bl-cover-k">{c["kicker"]}</p>' if c.get("kicker") else ""
    msg = (f'\n      <hr class="bl-cover-rule">\n      <p class="bl-cover-one">{c["message"]}</p>'
           if c.get("message") else "")
    inner = (f'\n    <div class="bl-bd bl-bd--center">{kick}\n      <h1 class="bl-title">{c.get("title", title)}{tag}</h1>'
             f'{msg}\n    </div>{sig}\n')
    n = c.get("notes", "표지에서는 제목과 시점만 말한다. 목차는 다음 장에서 짚는다.")
    return wrap(["bl-sl--dark", "bl-sl--cover"], {"data-notes": n},
                c.get("date", "") or "보고", c.get("org", "") or plain(title), inner)


def agenda_slide(chapters, apx_names, plan):
    names = " · ".join(ch["name"] for ch in chapters)
    rows = "".join(f'\n        <li><b>{k}</b><h3>{ch["name"]}</h3><span>{ch.get("lede", "")}</span></li>'
                   for k, ch in enumerate(chapters, 1))
    if apx_names:
        rows += f'\n        <li class="is-apx"><b>+</b><h3>부록</h3><span>{" · ".join(apx_names)}</span></li>'
    inner = (f'\n    <div class="bl-bd">\n      <h2 class="bl-title">보고 순서 — <em>{names}</em></h2>'
             f'\n      <ol class="bl-agenda">{rows}\n      </ol>\n    </div>\n')
    return wrap([], {"data-notes": plan.get("agenda_notes", "장 이름만 읽고 넘어간다. 결정이 필요한 장에 시간을 남긴다.")},
                "00", "보고 순서", inner)


def chapter_slide(k, ch, chapters, rows):
    compact = len(rows) > 3 or not any(r[2] for r in rows)
    lis = "".join(
        (f'\n          <li><b>{c}</b><h3>{t}</h3></li>' if compact else
         f'\n          <li><b>{c}</b><div><h3>{t}</h3>{f"<p>{s}</p>" if s else ""}</div></li>')
        for c, t, s in rows)
    on = ' class="is-on"'
    nav = "".join(f'<li{on if j == k else ""}><b>{j:02d}</b>{c["name"]}</li>'
                  for j, c in enumerate(chapters, 1))
    toc_cls = "bl-chapter-toc bl-chapter-toc--compact" if compact else "bl-chapter-toc"
    inner = f'''
    <div class="bl-bd bl-chapter bl-chapter--toc">
      <div class="bl-chapter-main">
        <p class="bl-chapter-k">Chapter</p>
        <p class="bl-chapter-no">{k:02d}</p>
        <h2 class="bl-title">{ch.get("title", ch["name"])}</h2>
        {f'<p class="bl-lede">{ch["lede"]}</p>' if ch.get("lede") else ""}
      </div>
      <div class="bl-chapter-side">
        <p class="bl-chapter-toc-h">이 장에서</p>
        <ol class="{toc_cls}">{lis}
        </ol>
      </div>
      <ol class="bl-chapter-nav" aria-label="장 진행">{nav}</ol>
    </div>
'''
    return wrap(["bl-sl--chapter"] + ([] if STYLE == "a" else ["bl-sl--dark"]), {"data-notes": ch.get(
        "notes", "장 간지는 제목과 오른쪽 목록만 읽고 넘어간다. 아래 칸이 지금 몇째 장인지 알려 준다.")},
        f"CH {k:02d}", ch["name"], inner)


def closing_slide(c, code):
    inner = f'''
    <div class="bl-bd bl-fin">
      {f'<p class="bl-fin-l1">{c["lead"]}</p>' if c.get("lead") else ""}
      <h2 class="bl-fin-l2"><span class="bl-fin-w">{c.get("line", "")}</span> <mark class="bl-fin-mk">{c.get("mark", "")}</mark></h2>
      <hr class="bl-fin-rule">
      <p class="bl-fin-ty">{c.get("type", "질의응답")}</p>
      {f'<p class="bl-fin-sig">{c["sign"]}</p>' if c.get("sign") else ""}
    </div>
'''
    return wrap([] if STYLE == "a" else ["bl-sl--dark"], {"data-notes": c.get("notes", "마지막 한 문장만 남기고 끝낸다. 질문을 받는다.")},
                code, "마무리", inner)


def apxdiv_slide(names):
    sub = " · ".join(names)
    inner = (f'\n    <div class="bl-bd bl-apxdiv">\n      <b aria-hidden="true">+</b>\n'
             f'      <div><h2 class="bl-title">부록</h2><p class="bl-lede">{sub}</p></div>\n    </div>\n')
    return wrap(["bl-sl--dark", "bl-sl--apxdiv"],
                {"data-notes": "여기부터 부록이다. 질문이 나올 때만 연다. a 를 누르고 부록 쪽번호를 치면 바로 간다."},
                "부록", sub, inner)


# ── 조립 ─────────────────────────────────────────────────────────────────────

class Deck:
    def __init__(self, plan, base):
        self.plan, self.base = plan, base
        self.body = {}
        self.ev = {"ev": {}}
        self.extra = {}
        self.warn = []
        self.used = set()
        self.pattern = False
        files = plan.get("body") or []
        for f in [files] if isinstance(files, str) else files:
            p = os.path.join(base, f)
            if not os.path.isfile(p):
                die(f"본문 파일이 없다 — {p}")
            for a, _t, inner in sections(open(p, encoding="utf-8").read()):
                sid = a.get("id")
                if not sid:
                    die(f"{f}: id 없는 <section> 이 있다. 장마다 id 를 단다.")
                if sid in self.body:
                    die(f"{f}: id 「{sid}」가 두 번 나온다.")
                self.body[sid] = (a, inner, f)
        evf = plan.get("evidence")
        if evf:
            p = os.path.join(base, evf)
            data = json.load(open(p, encoding="utf-8"))
            self.ev = data if "ev" in data else {"ev": data}

    def item(self, ref):
        """조립 목록의 한 칸 → (속성, 안쪽, 머리띠 코드 · 이름 기본값)."""
        over = {}
        if isinstance(ref, dict):
            over = ref
            ref = ref.get("use") or ref.get("id")
        if ref in self.used:
            die(f"「{ref}」가 조립 목록에 두 번 나온다.")
        self.used.add(ref)
        if ":" in ref:
            lib, sid = ref.split(":", 1)
            if lib not in LIBS:
                die(f"라이브러리 이름을 모른다 — {lib} (catalog · patterns · standard)")
            fname = LIBS[lib]
            secs, ev, extra = library(fname)
            if sid not in secs:
                die(f"{fname} 에 #{sid} 장이 없다.")
            a, _t, inner = secs[sid]
            a = dict(a)
            inner, _ = strip_chrome(inner)
            pre = LIB_PREFIX[fname]

            def ren(m):
                keys = []
                for key in m.group(1).split(","):
                    key = key.strip()
                    if key in ev.get("ev", {}):
                        self.ev["ev"][f"{pre}-{key}"] = ev["ev"][key]
                    keys.append(f"{pre}-{key}")
                return 'data-ev="' + ",".join(keys) + '"'
            inner = re.sub(r'data-ev="([^"]+)"', ren, inner)
            for k, v in ev.items():
                if k != "ev" and isinstance(v, dict):
                    self.ev.setdefault(k, {}).update(v)
            for xid, block in extra.items():
                if xid in inner:
                    self.extra[xid] = block
            if fname == "live-patterns.html" or " xf " in f' {a.get("class", "")} ':
                self.pattern = True
            m = re.search(r'<span class="bl-code"><b>(.*?)</b>(.*?)</span>', secs[sid][2], re.S)
            dcode, dname = (m.group(1), clean_name(m.group(2))) if m else ("", sid)
        else:
            if ref not in self.body:
                die(f"본문 파일에 #{ref} 장이 없다. (본문 id: {', '.join(self.body) or '없음'})")
            a, inner, f = self.body[ref]
            a = dict(a)
            inner, n = strip_chrome(inner)
            if n:
                self.warn.append(f"#{ref}: 본문에 머리띠 · 꼬리띠 · 로고가 들어 있어 뗐다 — 틀은 빌드가 단다")
            if "--bl-pt-" in inner or 'class="xf' in inner:
                self.pattern = True
            dcode, dname = "", a.get("data-name", "")
        for k in ("name", "code", "toc", "sub", "notes"):
            if over.get(k):
                a["data-" + k] = over[k]
        if not a.get("data-notes"):
            self.warn.append(f"#{a.get('id', ref)}: 발표자 노트(data-notes)가 없다")
        return a, inner, dcode, dname

    def build(self):
        p = self.plan
        title_plain = plain(p.get("title") or (p.get("cover") or {}).get("title", "")) or "보고서"
        chapters = p.get("chapters") or []
        appendix = p.get("appendix") or []
        out = [cover_slide(p.get("cover") or {"title": title_plain}, title_plain)]

        apx_items = [self.item(r) for r in appendix]
        apx_names = [x[0].get("data-name") or x[3] or title_of(x[1]) for x in apx_items]
        if p.get("agenda", True) and len(chapters) >= 2:
            out.append(agenda_slide(chapters, apx_names, p))

        num = 0
        for r in p.get("front") or []:
            a, inner, dcode, dname = self.item(r)
            out.append(wrap(a.get("class", "").split(), a, a.get("data-code") or "요약",
                            a.get("data-name") or dname or "보고 요지", inner))
        for k, ch in enumerate(chapters, 1):
            if not ch.get("name"):
                die(f"{k}번째 장(chapter)에 name 이 없다")
            items = [self.item(r) for r in ch.get("slides") or []]
            if not items:
                die(f"장 「{ch['name']}」에 slides 가 비었다")
            if ch.get("takeaway"):
                # 장 결론 — 장(章)의 끝(또는 처음) 한 장에만 결론 줄을 단다. 장마다 붙이지 않는다.
                at = -1 if str(ch.get("takeaway_at", "last")) != "first" else 0
                a, inner, dcode, dname = items[at]
                items[at] = (a, add_takeaway(inner, ch["takeaway"]), dcode, dname)
            built, rows = [], []
            for a, inner, dcode, dname in items:
                num += 1
                code = a.get("data-code") or f"{num:02d}"
                name = a.get("data-name") or ch["name"]
                rows.append((code, H.escape(a.get("data-toc") or title_of(inner) or name), a.get("data-sub", "")))
                built.append(wrap(a.get("class", "").split(), a, code, name, inner))
            if p.get("dividers", True):
                out.append(chapter_slide(k, ch, chapters, rows))
            out.extend(built)
        if p.get("closing"):
            num += 1
            out.append(closing_slide(p["closing"], f"{num:02d}"))
        if apx_items:
            out.append(apxdiv_slide(apx_names))
            for (a, inner, dcode, dname), nm in zip(apx_items, apx_names):
                out.append(wrap(a.get("class", "").split(), a, "부록", nm, inner, apx=True))
        seen, dup = set(), set()
        for sl in out:
            m = re.match(r'\s*<section\b[^>]*\bid="([^"]+)"', sl)
            if m:
                (dup if m.group(1) in seen else seen).add(m.group(1))
        if dup:
            die(f"장 id 가 겹친다 — {', '.join(sorted(dup))}. 라이브러리 장과 본문 장의 id 가 같으면 "
                f"본문 쪽 id 를 바꾸거나, 라이브러리 장을 본문 파일로 복사해 새 id 를 단다.")
        unused = [k for k in self.body if k not in self.used]
        if unused:
            self.warn.append(f"조립 목록에 없어 빠진 본문 장: {', '.join(unused)}")
        return title_plain, out

    def html(self):
        title, slides = self.build()
        links = ['<link rel="stylesheet" href="blue-report.css">',
                 '<link rel="stylesheet" href="blue-live.css">',
                 '<link rel="stylesheet" href="blue-pattern.css">']
        if STYLE != "a":
            links.append('<link rel="stylesheet" href="blue-style.css">')
        evjson = json.dumps(self.ev, ensure_ascii=False, indent=1).replace("</", "<\\/")
        hud = HUD
        style_attr = "" if STYLE == "a" else f' data-style="{STYLE}"'
        return f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{H.escape(title)}</title>
<!-- build_deck.py 가 조립했다. 틀(머리띠 · 꼬리띠 · 로고 · 워터마크 · 표지 · 목차 · 간지)은 손으로 고치지 않는다 —
     조립 목록과 본문 파일을 고치고 다시 빌드한다. -->
{chr(10).join(links)}
</head>
<body>

<div id="bl-prog"></div>

<main class="bl-deck" id="deck"{style_attr} data-deck-title="{H.escape(title, quote=True)}" tabindex="0"
      aria-label="{H.escape(title, quote=True)} 슬라이드">

{chr(10).join(slides)}
</main>
{hud}
{chr(10).join(self.extra.values())}
<script type="application/json" id="bl-evidence">
{evjson}
</script>

<script src="live-viewer.js"></script>
</body>
</html>
'''


HUD = '''
<!-- 조작판 — JS 가 꺼져 있어도 세로로 스크롤하면 전부 읽힌다 -->
<div class="bl-hud" role="toolbar" aria-label="덱 조작">
  <button type="button" data-act="prev" aria-label="이전 장">‹</button>
  <span data-pg aria-live="polite"></span>
  <button type="button" data-act="next" aria-label="다음 장">›</button>
  <span class="bl-hud-sep" aria-hidden="true"></span>
  <button type="button" data-act="expand" aria-pressed="true">펼침<kbd>X</kbd></button>
  <button type="button" data-act="horiz" aria-pressed="false">가로<kbd>V</kbd></button>
  <button type="button" data-act="notes" aria-pressed="false">메모<kbd>M</kbd></button>
  <button type="button" data-act="laser" aria-pressed="false">레이저<kbd>L</kbd></button>
  <button type="button" data-act="pen" aria-pressed="false">펜<kbd>P</kbd></button>
  <button type="button" data-act="present">발표<kbd>Shift+F5</kbd></button>
  <button type="button" data-act="script">대본<kbd>Alt+F5</kbd></button>
  <button type="button" data-act="help" aria-label="단축키 도움말">?</button>
</div>
<div id="bl-jump" hidden aria-hidden="true"></div>
'''


def load_plan(path):
    try:
        import yaml
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "pyyaml"])
        import yaml
    with open(path, encoding="utf-8") as f:
        plan = yaml.safe_load(f) or {}
    if not isinstance(plan, dict):
        die("조립 목록은 YAML 사전이어야 한다")
    return plan


def main():
    ap = argparse.ArgumentParser(description="본문만 쓴 장을 회사 덱으로 조립한다")
    ap.add_argument("plan", help="조립 목록 YAML")
    ap.add_argument("-o", "--out", required=True, help="출력 HTML")
    ap.add_argument("--brand", help="brand.json — 주면 로고 · 워터마크까지 입힌다")
    ap.add_argument("--single-file", action="store_true", help="CSS · 폰트 · 뷰어를 한 파일에")
    ap.add_argument("--style", choices=STYLES, help="시각 스타일 — 조립 목록의 style 보다 앞선다 (a 프레임 · c 혼합)")
    a = ap.parse_args()

    plan = load_plan(a.plan)
    global STYLE
    STYLE = (a.style or str(plan.get("style", "a"))).lower()
    if STYLE not in STYLES:
        die(f"style 은 {' · '.join(STYLES)} 중 하나다 — 받은 값: {STYLE}")
    deck = Deck(plan, os.path.dirname(os.path.abspath(a.plan)))
    html = deck.html()
    if not deck.pattern:
        html = html.replace('<link rel="stylesheet" href="blue-pattern.css">\n', "")
    for w in deck.warn:
        print("주의: " + w, file=sys.stderr)

    out = os.path.abspath(a.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if not a.brand:
        # 브랜드 없이 — 자리표시자 그대로. CSS · 뷰어는 assets/ 를 직접 가리키게 둔다.
        rel = os.path.relpath(ASSETS, os.path.dirname(out)).replace(os.sep, "/")
        html = re.sub(r'((?:href|src)=")((?:blue-[\w-]+\.css)|live-viewer\.js)"', rf'\1{rel}/\2"', html)
        open(out, "w", encoding="utf-8").write(html)
        print(f"생성(브랜드 없음): {out}")
        return
    import apply_brand as AB
    brand = AB.load_brand(a.brand)
    brand["docTitle"] = re.search(r'data-deck-title="([^"]*)"', html).group(1)
    uris = AB.logo_uris(brand, a.brand)
    html, n, left = AB.apply(html, brand, uris)
    if a.single_file:
        from build_single_file import inline_assets
        html = inline_assets(html)
    open(out, "w", encoding="utf-8").write(html)
    if not a.single_file:
        copied = AB.copy_assets(html, out)
        if copied:
            print(f"함께 복사: {' · '.join(copied)}")
    n_sl = html.count('<section class="bl-sl')
    print(f"생성: {out}  ({n_sl}장 · 브랜드 {n}건)")
    if left:
        print(f"주의: 남은 자리표시자 {len(left)}건", file=sys.stderr)
    print("다음: python3 scripts/check_live.py " + a.out)


if __name__ == "__main__":
    main()
