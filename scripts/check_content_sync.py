#!/usr/bin/env python3
"""HTML 덱과 PPTX 내용이 갈라졌는지 본다.

같은 내용이 `assets/deck-*.html` 과 `pptx/content.js` 두 곳에 따로 있다.
HTML 이 기준이고 PPTX 는 그 내용을 데이터로 옮긴 것이라, 한쪽만 고치면
같은 덱인데 형식에 따라 내용이 달라진다. 사람 눈으로는 잘 보이지 않는다.

두 곳을 합치지 않는 이유 — HTML 덱은 손으로 고치는 것이 이 시스템의 사용법이다
(`assets/deck-*.html` 을 복사해 내용만 바꾼다). HTML 을 생성물로 만들면 그 사용법이
사라진다. 그래서 원본을 둘로 두고, 갈라짐을 사람이 아니라 이 스크립트가 잡는다.

    python3 scripts/check_content_sync.py
    python3 scripts/check_content_sync.py --deck internal

대조 항목
  슬라이드 수 · 문서명 · 발표자 노트 · 세로 막대(이름·값) · 도넛(범례 이름·값)
  · 표(머리글·행)

레이아웃·문체·색은 대상이 아니다. 그쪽은 check_deck.py 가 본다.
종료 코드는 어긋난 곳이 있으면 1 이다.
"""
import argparse
import html as htmllib
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, ".claude", "skills", "blue-report")
ASSETS = os.path.join(SKILL, "assets")
CONTENT_JS = os.path.join(SKILL, "pptx", "content.js")

# content.js 의 덱 키 → HTML 덱 파일. deck-template.html 은 카탈로그라 PPTX 판이 없다.
DECKS = {
    "internal": "deck-internal-report.html",
    "sales": "deck-sales-proposal.html",
    "project": "deck-project-report.html",
    "training": "deck-training.html",
}


# ------------------------------------------------------------------ 공통 도구

def text(fragment):
    """태그를 벗기고 공백을 하나로 줄인다."""
    s = re.sub(r"<[^>]+>", "", fragment)
    return re.sub(r"\s+", " ", htmllib.unescape(s)).strip()


def flat(node):
    """content.js 의 lede/title 조각([문자열, {k: 강조}])을 문자열로 편다."""
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, dict):
        return str(node.get("k", node.get("t", "")))
    if isinstance(node, list):
        return "".join(flat(x) for x in node)
    return str(node)


def norm(s):
    return re.sub(r"\s+", " ", str(s)).strip()


def num(s):
    """'36.0%' · '174' → 비교 가능한 숫자. 숫자가 아니면 None."""
    m = re.search(r"-?\d+(?:\.\d+)?", str(s))
    return float(m.group()) if m else None


# '36.0%' · '312h' — 숫자 뒤에 붙는 단위. HTML 은 지면에 찍고 PPTX 는 생성기가 붙이므로
# 한쪽에만 있는 것이 정상이다. 양쪽 다 있으면 그때는 같아야 한다.
UNIT_RE = re.compile(r"^\s*(-?[\d,]+(?:\.\d+)?)\s*([^\d\s]*)\s*$")


def same_value(a, b):
    """숫자는 값으로, 그 밖은 문자열로 견준다.

    36 과 36.0 을 다르다고 하지 않고, '36%' 와 36 도 다르다고 하지 않는다.
    후자는 단위를 PPTX 생성기가 붙이기 때문이다(`labelFormat` · `sup`).
    '2026.08.01 ~ 08.31' 처럼 숫자로 떨어지지 않는 것은 문자열로 견준다."""
    ma, mb = UNIT_RE.match(norm(a)), UNIT_RE.match(norm(b))
    if ma and mb:
        if abs(float(ma.group(1).replace(",", "")) - float(mb.group(1).replace(",", ""))) >= 1e-9:
            return False
        ua, ub = ma.group(2), mb.group(2)
        return not (ua and ub) or ua == ub
    return norm(a) == norm(b)


# ---------------------------------------------------------------- HTML 쪽 추출

def split_frames(html):
    """`.br-frame` 단위로 슬라이드를 자른다."""
    starts = [m.start() for m in re.finditer(r'<div class="br-frame"', html)]
    if not starts:
        return []
    ends = starts[1:] + [len(html)]
    return [html[a:b] for a, b in zip(starts, ends)]


def html_facts(frame):
    """한 슬라이드에서 대조 가능한 사실만 뽑는다."""
    f = {}

    m = re.search(r'data-notes="([^"]*)"', frame)
    f["notes"] = norm(htmllib.unescape(m.group(1))) if m else ""

    # 세로 막대 — 값 열과 이름 열이 따로 있다
    vals = [text(x) for x in re.findall(r'<div class="br-col-val[^"]*">(.*?)</div>', frame, re.S)]
    names = [text(x) for x in re.findall(r'<div class="[^"]*br-col-name[^"]*">(.*?)</div>', frame, re.S)]
    if vals and names:
        f["bar"] = {"names": names, "values": vals}

    # 도넛 — 범례가 이름과 값을 함께 들고 있다
    leg = re.findall(
        r'<div class="br-legend-name">(.*?)</div>\s*<div class="br-legend-val">(.*?)</div>',
        frame, re.S)
    if leg:
        f["donut"] = {"names": [text(a) for a, _ in leg], "values": [text(b) for _, b in leg]}

    # 표
    if "<table" in frame:
        head = [text(x) for x in re.findall(r"<th[^>]*>(.*?)</th>", frame, re.S)]
        rows = []
        for tr in re.findall(r"<tr>(.*?)</tr>", frame, re.S):
            cells = re.findall(r"<td([^>]*)>(.*?)</td>", tr, re.S)
            if not cells:
                continue
            # colspan 은 빈 칸으로 편다. content.js 는 칸을 하나씩 들고 있다.
            row = []
            for attrs, body in cells:
                span = re.search(r'colspan="(\d+)"', attrs)
                row.append(text(body))
                row.extend([""] * (int(span.group(1)) - 1 if span else 0))
            rows.append(row)
        f["table"] = {"head": head, "rows": rows}

    return f


def read_html(fname):
    path = os.path.join(ASSETS, fname)
    src = open(path, encoding="utf-8").read()
    m = re.search(r'data-deck-title="([^"]*)"', src)
    return {
        "docTitle": norm(htmllib.unescape(m.group(1))) if m else "",
        "slides": [html_facts(fr) for fr in split_frames(src)],
    }


# ------------------------------------------------------------ content.js 쪽

def read_content_js():
    """node 로 실제 모듈을 읽는다. 정규식으로 JS 를 파싱하지 않는다."""
    script = (
        "const c = require(%s);\n"
        "const out = {};\n"
        "for (const [k, v] of Object.entries(c)) if (v && v.slides) out[k] = v;\n"
        "process.stdout.write(JSON.stringify(out));\n"
    ) % json.dumps(CONTENT_JS)
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
        fh.write(script)
        tmp = fh.name
    try:
        r = subprocess.run(["node", tmp], capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"content.js 를 읽지 못했다 — {r.stderr.strip()[:300]}")
        return json.loads(r.stdout)
    finally:
        os.unlink(tmp)


def js_facts(slide):
    f = {"notes": norm(slide.get("notes", ""))}

    if slide.get("type") == "bar":
        f["bar"] = {"names": [norm(x) for x in slide.get("categories", [])],
                    "values": [norm(v) for v in slide.get("values", [])]}

    if slide.get("type") == "donut":
        seg = slide.get("segments", [])
        f["donut"] = {"names": [norm(s.get("name", "")) for s in seg],
                      "values": [norm(s.get("value", "")) for s in seg]}

    if slide.get("type") == "table":
        f["table"] = {
            "head": [norm(flat(h.get("t", h))) for h in slide.get("head", [])],
            "rows": [[norm(flat(c.get("t", c) if isinstance(c, dict) else c)) for c in row]
                     for row in slide.get("rows", [])],
        }
    return f


# -------------------------------------------------------------------- 대조

def compare_deck(key, hd, cd, problems):
    where = f"{key}"

    if not same_value(hd["docTitle"], cd.get("docTitle", "")):
        problems.append(f"{where} 문서명 — HTML「{hd['docTitle']}」 · PPTX「{cd.get('docTitle','')}」")

    hs, cs = hd["slides"], cd.get("slides", [])
    if len(hs) != len(cs):
        problems.append(f"{where} 슬라이드 수 — HTML {len(hs)}장 · PPTX {len(cs)}장")

    for i, (h, c_raw) in enumerate(zip(hs, cs), start=1):
        c = js_facts(c_raw)
        at = f"{where} {i}장"

        if h["notes"] != c["notes"]:
            problems.append(f"{at} 발표자 노트\n      HTML: {h['notes'][:80]}\n      PPTX: {c['notes'][:80]}")

        for kind, label in (("bar", "막대"), ("donut", "도넛")):
            if kind in h and kind in c:
                for field, fl in (("names", "이름"), ("values", "값")):
                    a, b = h[kind][field], c[kind][field]
                    if len(a) != len(b):
                        problems.append(f"{at} {label} {fl} 개수 — HTML {len(a)} · PPTX {len(b)}")
                    elif not all(same_value(x, y) for x, y in zip(a, b)):
                        problems.append(f"{at} {label} {fl}\n      HTML: {a}\n      PPTX: {b}")
            elif (kind in h) != (kind in c):
                problems.append(f"{at} {label} — 한쪽에만 있다 "
                                f"(HTML {'있음' if kind in h else '없음'} · "
                                f"PPTX {'있음' if kind in c else '없음'})")

        if "table" in h and "table" in c:
            if [norm(x) for x in h["table"]["head"]] != c["table"]["head"]:
                problems.append(f"{at} 표 머리글\n      HTML: {h['table']['head']}\n      PPTX: {c['table']['head']}")
            hr, cr = h["table"]["rows"], c["table"]["rows"]
            if len(hr) != len(cr):
                problems.append(f"{at} 표 행 수 — HTML {len(hr)} · PPTX {len(cr)}")
            else:
                for r, (a, b) in enumerate(zip(hr, cr), start=1):
                    if len(a) != len(b) or not all(same_value(x, y) for x, y in zip(a, b)):
                        problems.append(f"{at} 표 {r}행\n      HTML: {a}\n      PPTX: {b}")


def main():
    ap = argparse.ArgumentParser(description="HTML 덱과 PPTX 내용 동기화 점검")
    ap.add_argument("--deck", choices=sorted(DECKS), help="한 종만 본다")
    a = ap.parse_args()

    try:
        content = read_content_js()
    except Exception as e:
        print(f"  실패  {e}")
        return 1

    targets = {a.deck: DECKS[a.deck]} if a.deck else DECKS
    problems, checked = [], 0

    for key, fname in targets.items():
        if key not in content:
            problems.append(f"{key} — content.js 에 없다")
            continue
        compare_deck(key, read_html(fname), content[key], problems)
        checked += 1

    if problems:
        print(f"  실패  HTML 덱과 PPTX 내용이 갈라졌다 — {len(problems)}건")
        for p in problems:
            print(f"    · {p}")
        print("\n  HTML 이 기준이다. pptx/content.js 를 HTML 에 맞춘다.")
        return 1

    print(f"  통과  내용 동기화 — 덱 {checked}종의 노트·막대·도넛·표가 HTML 과 일치")
    return 0


if __name__ == "__main__":
    sys.exit(main())
