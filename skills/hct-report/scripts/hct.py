#!/usr/bin/env python3
"""HCT 회사 보고서 — 한 줄 명령. 에이전트는 이것 하나만 부르면 된다.

    python3 <스킬>/scripts/hct.py formats                       # 목적 × 형식 표 (무엇을 어떤 형식으로 만들 수 있나)
    python3 <스킬>/scripts/hct.py new present  decks-out/보고서   # 새 보고서 뼈대 — 발표 보고(덱)
    python3 <스킬>/scripts/hct.py new document decks-out/보고서 --kind report   # 문서 보고(A4)
    python3 <스킬>/scripts/hct.py build decks-out/보고서 --formats html,pptx,pdf  # 만들고 검사까지
    python3 <스킬>/scripts/hct.py check decks-out/보고서.html       # 검사만
    python3 <스킬>/scripts/hct.py form                           # A4 문서 양식(forms/<id>.json) 보기 · --use 로 바꾸기

목적은 다섯이다 — present(발표 보고) · document(문서 보고) · board(현황 관리) ·
external(대외 제출) · web(웹 게시). 형식은 html · pdf · pptx · docx · xlsx.
아직 만들 수 없는 조합을 요청받으면 지어내지 않고 종료 코드 2 와 대안을 낸다.

내용은 한 곳(덱이면 deck.yaml + slides.html, 문서 · 보드면 HTML 한 파일)에만 쓴다.
형식마다 따로 쓰지 않는다 — 형식은 그 한 곳에서 뽑는다.
"""
import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys

# head 등으로 파이프가 닫혀도 역추적 없이 끝낸다 — 에이전트가 출력을 잘라 읽는 일이 잦다
try:
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
except (AttributeError, ValueError):
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
ASSETS = os.path.join(SKILL, "assets")
PY = sys.executable

# brand.json — 설치본은 스킬 안(brand/hct), 저장소에서는 루트(brand/hct)
BRAND_CANDIDATES = [os.path.join(SKILL, "brand", "hct", "brand.json"),
                    os.path.join(SKILL, "..", "..", "..", "brand", "hct", "brand.json")]

# ── 목적 × 형식. 이 표가 유일한 기준이다 — SKILL.md 는 이 표를 다시 적지 않고 `formats` 를 부르게 한다 ──
# 상태: ok(만들 수 있음) · partial(제한 있음 — note 를 사용자에게 말한다) · planned(아직 없음)
PURPOSES = {
    "present": {
        "name": "발표 보고", "when": "말로 설명하는 보고 — 월간 · 주간 · 경영진 · 제안 · 교육 · 프로젝트 보고",
        "default": ["html"],
        "kinds": {"deck": "라이브 덱 — 내용에 맞게 장을 짠다(용도별 틀이 따로 없다)"},
        "formats": {
            "html": ("ok", "발표 · 공유 기본. 브라우저로 열어 F5 / Shift+F5 로 발표"),
            "pdf": ("ok", "배포 · 인쇄용. 장마다 한 쪽"),
            "pptx": ("partial", "제목 · 리드 · 노트는 PowerPoint 글자, 본문 도식은 그림. 틀 디자인이 HTML 과 일부 다름"),
            "docx": ("planned", "발표 보고는 Word 대상이 아님 — 문서 보고(document)로 만든다"),
        },
    },
    "document": {
        "name": "문서 보고", "when": "읽고 결재하는 A4 문서 — 사내 보고서 · 회의록 · 규정 · 매뉴얼 · 공지",
        "default": ["pdf", "html"],
        "kinds": {"report": "사내 보고서 (요약 · 지표 · 실적 · 리스크 · 요청 · 결재란)",
                  "minutes": "회의록 (안건 · 결정 · 액션아이템)",
                  "policy": "규정 · 사규 (조 · 항 · 호 · 개정 이력 · 결재란)",
                  "manual": "매뉴얼 · 가이드 (목차 · 절차 · 화면 캡처)",
                  "notice": "공지 (1쪽)"},
        "formats": {
            "html": ("ok", "화면 열람 · 브라우저 인쇄"),
            "pdf": ("ok", "결재 · 배포 기본. A4"),
            "docx": ("ok", "Word 로 고쳐 쓸 판. 글자 · 표 · 목록 전부 편집 가능. HTML 원본에서 뽑는다"),
        },
    },
    "board": {
        "name": "현황 관리", "when": "계속 고쳐 가며 보는 화면 — 과제 현황판 · 칸반 · 점검표 · 대시보드",
        "default": ["html"],
        "kinds": {"manage": "관리보드 (HCT 웹 디자인 템플릿 v2.1.0 · 앱 셸 · 과제 · 지표 · 일정)",
                  "task": "과제 실행보드 (가장 작은 견본)",
                  "exec": "실행보드 (항목별 상태 · 메모)",
                  "team": "팀보드 (칸반 4열)",
                  "gap": "점검보드 (빠진 칸 찾기)"},
        "formats": {
            "html": ("ok", "화면에서 상태를 바꾸는 웹 보드"),
            "xlsx": ("planned", "엑셀 내보내기는 다음 판 이후 — 지금은 HTML 만"),
            "pdf": ("planned", "보드는 화면 폭에 따라 흐르는 물건이라 PDF 대상이 아님"),
        },
    },
    "external": {
        "name": "대외 제출", "when": "고객 · 기관에 내는 인증 보고 — FCC/KC 인증 분석 보고서",
        "default": ["pdf"],
        "kinds": {"a": "경영 요약 — 결정 · 승인용", "b": "분석 대시보드 — 수치 비교 · 추이",
                  "c": "근거 자료집 — 재현 · 감사 대응"},
        "formats": {
            "html": ("ok", "A4 지면 HTML"),
            "pdf": ("ok", "제출 기본"),
            "docx": ("partial", "대표 시안 A/B/C 만 — scripts/build_fcc_office.py (견본 데이터 기준)"),
            "pptx": ("partial", "대표 시안 A/B/C 만 — scripts/build_fcc_office.py (견본 데이터 기준)"),
        },
    },
    "web": {
        "name": "웹 게시", "when": "사내외 공개 페이지 — 사업 소개 · 공지 페이지 · 행사 안내",
        "default": [],
        "kinds": {},
        "formats": {"html": ("planned", "웹 게시 틀은 아직 없음 — 공지는 document(notice), 현황은 board 로 대신한다")},
    },
}

# 목적 · 종류 → 저장소 견본 파일
DOC_KINDS = {"report": "archive/doc-report.html", "minutes": "doc-minutes.html", "policy": "archive/doc-policy.html",
             "manual": "archive/doc-manual.html", "notice": "archive/doc-notice.html"}
BOARD_KINDS = {"manage": "board-manage.html", "task": "archive/board-task.html", "exec": "archive/board-exec.html",
               "team": "archive/board-team.html", "gap": "archive/board-gap.html"}
FCC_KINDS = {"a": "archive/fcc-kc/templates/tpl-a-executive.html", "b": "archive/fcc-kc/templates/tpl-b-dashboard.html",
             "c": "archive/fcc-kc/templates/tpl-c-dossier.html"}


def brand_path(given=None):
    if given:
        return given
    for p in BRAND_CANDIDATES:
        if os.path.isfile(p):
            return os.path.abspath(p)
    sys.exit("brand.json 을 찾지 못했다 — 스킬 안 brand/hct/brand.json 이 있어야 한다. --brand 로 직접 준다")


def run(cmd, quiet=False):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if not quiet or r.returncode != 0:
        out = (r.stdout + r.stderr).strip()
        if out:
            print(out)
    return r


# ── formats ────────────────────────────────────────────────────────────────
def cmd_formats(a):
    if a.json:
        print(json.dumps(PURPOSES, ensure_ascii=False, indent=1))
        return 0
    mark = {"ok": "가능", "partial": "제한", "planned": "없음"}
    for key, p in PURPOSES.items():
        print(f"\n[{key}] {p['name']} — {p['when']}")
        if p["kinds"]:
            print("  종류  " + " · ".join(f"{k}({v.split(' ')[0]})" for k, v in p["kinds"].items()))
        print(f"  기본 형식  {', '.join(p['default']) or '—'}")
        for f, (st, note) in p["formats"].items():
            print(f"  {f:5} {mark[st]:3}  {note}")
    print("\n가능 = 바로 만든다 · 제한 = 만들되 note 를 사용자에게 알린다 · 없음 = 만들지 않고 대안을 말한다")
    return 0


# ── new ────────────────────────────────────────────────────────────────────
def active_form():
    """지금 blue-doc.css 가 쓰는 양식 정의(forms/<id>.json). HTML · PDF · Word 가 같은 것을 쓴다."""
    css = open(os.path.join(ASSETS, "blue-doc.css"), encoding="utf-8").read()
    m = re.search(r'--bd-form:\s*"([^"]+)"', css)
    p = os.path.join(SKILL, "forms", (m.group(1) if m else "hct-standard") + ".json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def stamp_form(path, form=None):
    """새 A4 문서에 양식의 기본값을 찍는다 — 지금은 결재란 칸(sign.labels)."""
    form = form or active_form()
    if not form:
        return
    labels = form.get("sign", {}).get("labels") or []
    html = open(path, encoding="utf-8").read()
    item = '<div><div class="bd-sign-k">{}</div><div class="bd-sign-v"></div></div>'
    pat = re.compile(r'(<div class="bd-sign">\s*)((?:<div><div class="bd-sign-k">[^<]*</div><div class="bd-sign-v"></div></div>\s*)+)')
    m = pat.search(html)
    if labels and m:
        indent = re.search(r"\n([ \t]*)<div><div", m.group(2))
        ind = indent.group(1) if indent else "    "
        g = m.group(2)
        body = ("\n" + ind).join(item.format(l) for l in labels) + g[len(g.rstrip()):]
        html = html[:m.start(2)] + body + html[m.end(2):]
        open(path, "w", encoding="utf-8").write(html)


def cmd_new(a):
    p = PURPOSES.get(a.purpose)
    if not p:
        sys.exit(f"목적을 모른다: {a.purpose} — {' · '.join(PURPOSES)}")
    if not p["kinds"]:
        print(f"[없음] {p['name']} — {p['formats']['html'][1]}")
        return 2
    dst = os.path.abspath(a.dir)
    if os.path.exists(dst) and os.listdir(dst):
        sys.exit(f"폴더가 비어 있지 않다: {dst} — 덮어쓰지 않는다")
    os.makedirs(dst, exist_ok=True)
    if a.purpose == "present":
        src = os.path.join(SKILL, "examples", "standard")
        for fn in ("deck.yaml", "slides.html", "evidence.json"):
            shutil.copy(os.path.join(src, fn), dst)
        # 시각 스타일은 C(혼합형 · 권장)로 시작한다 — 견본은 style 을 적지 않아 A 가 된다
        y = os.path.join(dst, "deck.yaml")
        txt = open(y, encoding="utf-8").read()
        if not re.search(r"^style:", txt, re.M):
            txt = re.sub(r"^(title:.*)$", r"\1\nstyle: c                            # 시각 스타일 — c 혼합형(권장) · a 프레임형",
                         txt, count=1, flags=re.M)
            open(y, "w", encoding="utf-8").write(txt)
        made = "deck.yaml(style: c) · slides.html · evidence.json"
    else:
        kinds = {"document": DOC_KINDS, "board": BOARD_KINDS, "external": FCC_KINDS}[a.purpose]
        kind = a.kind or next(iter(kinds))
        if kind not in kinds:
            sys.exit(f"종류를 모른다: {kind} — {' · '.join(kinds)}")
        src = os.path.join(ASSETS, kinds[kind])
        fn = {"document": "doc", "board": "board", "external": "fcc"}[a.purpose] + f"-{kind}.html"
        shutil.copy(src, os.path.join(dst, fn))
        if a.purpose == "document":
            stamp_form(os.path.join(dst, fn))
        if a.purpose == "external":   # FCC 전용 CSS 를 옆에 둔다 — build 가 한 파일로 넣는다
            shutil.copy(os.path.join(ASSETS, "archive", "fcc-kc", "fcc-kc.css"), dst)
        made = fn
    print(f"생성: {dst}/  ({made})")
    print("다음: 견본 문구 · 수치 · 부서명을 실제 내용으로 모두 바꾼 뒤 "
          f"`hct.py build {a.dir} --formats {','.join(p['default'])}`")
    print("      견본 내용은 자리표시자가 아니라 사용법 예시다 — 남기면 남의 숫자가 그대로 나간다")
    return 0


# ── build ──────────────────────────────────────────────────────────────────
def detect(src):
    """원본 폴더 · 파일 → (목적, 원본 경로)"""
    if os.path.isdir(src):
        if os.path.isfile(os.path.join(src, "deck.yaml")):
            return "present", os.path.join(src, "deck.yaml")
        htmls = [f for f in os.listdir(src) if f.endswith(".html") and f != "slides.html"]
        if len(htmls) != 1:
            sys.exit(f"원본을 정하지 못했다: {src} — deck.yaml 이나 HTML 한 개가 있어야 한다")
        src = os.path.join(src, htmls[0])
    if src.endswith((".yaml", ".yml")):
        return "present", src
    html = open(src, encoding="utf-8").read()
    if "fcc-kc.css" in html:
        return "external", src
    if 'class="bd-doc"' in html:
        return "document", src
    if re.search(r'<body[^>]*class="bw"', html) or "hct-board.css" in html:
        return "board", src
    sys.exit(f"어떤 목적의 원본인지 알 수 없다: {src}")


def inline_fcc_css(out, src):
    """FCC/KC 전용 CSS 는 공용 자산 폴더 밖에 있어 단일 파일 묶기에서 빠진다 — 여기서 넣는다"""
    html = open(out, encoding="utf-8").read()
    css_path = os.path.join(os.path.dirname(src), "fcc-kc.css")
    if not os.path.isfile(css_path):
        css_path = os.path.join(ASSETS, "archive", "fcc-kc", "fcc-kc.css")
    css = open(css_path, encoding="utf-8").read()
    html, n = re.subn(r'<link rel="stylesheet" href="(?:\.\./)*fcc-kc\.css">', lambda m: "<style>\n" + css + "\n</style>", html)
    open(out, "w", encoding="utf-8").write(html)
    return n


def cmd_build(a):
    purpose, src = detect(a.src)
    p = PURPOSES[purpose]
    want = [f.strip().lower() for f in (a.formats or ",".join(p["default"])).split(",") if f.strip()]
    # 형식 판정 — 없는 조합은 만들지 않는다
    refused = []
    for f in want:
        st = p["formats"].get(f, ("planned", f"{p['name']}에는 {f} 형식이 없다"))
        if st[0] == "planned" or (purpose == "external" and f in ("docx", "pptx")):
            refused.append((f, st[1]))
    if refused:
        for f, note in refused:
            print(f"[만들지 않음] {f} — {note}")
        ok = [f for f in p["formats"] if p["formats"][f][0] == "ok"]
        print(f"이 목적에서 바로 만들 수 있는 형식: {', '.join(ok)}")
        return 2
    for f in want:
        if p["formats"][f][0] == "partial":
            print(f"[제한] {f} — {p['formats'][f][1]}")

    brand = brand_path(a.brand)
    outdir = os.path.abspath(a.out or os.path.join(os.path.dirname(os.path.abspath(src)), ".."))
    # 출력 이름 — new 로 만든 폴더 이름을 따른다(파일 이름은 견본 이름이라 보고서마다 같다)
    src_dir = os.path.abspath(a.src) if os.path.isdir(a.src) else os.path.dirname(os.path.abspath(src))
    stem = a.name or (os.path.basename(src_dir) if (os.path.isdir(a.src) or purpose == "present")
                      else os.path.splitext(os.path.basename(src))[0])
    os.makedirs(outdir, exist_ok=True)
    html_out = os.path.join(outdir, stem + ".html")
    made = []

    if purpose == "present":
        cmd = [PY, os.path.join(HERE, "build_deck.py"), src, "--brand", brand, "--single-file", "-o", html_out]
        if "pptx" in want:
            cmd += ["--pptx", os.path.join(outdir, stem + ".pptx")]
        r = run(cmd, quiet=True)
        if r.returncode != 0:
            print("[실패] 덱 조립"); return 1
        made.append(html_out)
        if "pptx" in want:
            made.append(os.path.join(outdir, stem + ".pptx"))
    else:
        cmd = [PY, os.path.join(HERE, "apply_brand.py"), "--brand", brand, "--deck", os.path.abspath(src),
               "--single-file", "-o", html_out]
        if a.title:
            cmd += ["--title", a.title]
        r = run(cmd, quiet=True)
        if r.returncode != 0:
            print("[실패] 브랜드 적용"); return 1
        if purpose == "external":
            inline_fcc_css(html_out, src)
        made.append(html_out)

    if not a.no_check:
        rc = check_file(html_out, purpose)
        if rc != 0:
            print("\n[미완료] 검사 실패가 있다 — 원본을 고치고 다시 build 한다. 실패가 0 이 아니면 완료가 아니다")
            return 1

    if "pdf" in want:
        pdf = os.path.join(outdir, stem + ".pdf")
        r = run([PY, os.path.join(HERE, "to_pdf.py"), html_out, "-o", pdf], quiet=True)
        if r.returncode != 0:
            print("[실패] PDF"); return 1
        made.append(pdf)
    if "docx" in want:
        docx = os.path.join(outdir, stem + ".docx")
        r = run([PY, os.path.join(HERE, "doc_to_docx.py"), html_out, "--brand", brand, "-o", docx], quiet=True)
        if r.returncode != 0:
            print("[실패] Word 변환"); return 1
        for ln in (r.stdout or "").splitlines():
            if ln.strip().startswith("주의"):
                print("  " + ln.strip())
        if not a.no_check:
            rc = check_docx(docx, html_out)
            if rc != 0:
                print("\n[미완료] Word 검사 실패가 있다 — 원본 HTML 을 고치고 다시 build 한다")
                return 1
        made.append(docx)
    if "html" not in want:
        # HTML 은 다른 형식의 원본이자 검사 대상이라 항상 만든다. 요청이 없었으면 그렇게 알린다
        print("참고: HTML 은 다른 형식을 뽑는 기준이라 함께 남겼다")

    print("\n산출물")
    for f in made:
        print(f"  {f}  ({os.path.getsize(f) // 1024}KB)")
    return 0


# ── check ──────────────────────────────────────────────────────────────────
def check_file(path, purpose=None):
    if purpose is None:
        html = open(path, encoding="utf-8").read()
        purpose = ("external" if "fcc-kc" in html else "document" if 'class="bd-doc"' in html
                   else "board" if (re.search(r'<body[^>]*class="bw"', html) or "hct-board" in html) else "present")
    checker = {"present": "check_live.py", "document": "check_doc.py", "external": "check_doc.py",
               "board": "check_board.py"}[purpose]
    r = subprocess.run([PY, os.path.join(HERE, checker), path], capture_output=True, text=True)
    lines = (r.stdout + r.stderr).splitlines()
    shown = [ln for ln in lines if re.match(r"\s*(실패|주의)\s", ln) or ln.startswith("결과")]
    print(f"\n검사 ({checker})")
    for ln in shown:
        print("  " + ln.strip())
    # 회사 규칙은 「색은 토큰만」이다. 검사기는 본문에 적은 hex 를 주의로만 내지만(맞춤 CSS 안은 실패),
    # 스킬로 만드는 산출물은 그것도 막는다 — 주의는 스크롤에 묻혀 그대로 나가기 쉽다.
    strict = [ln.strip() for ln in shown if re.match(r"\s*주의\s+토큰 밖 raw hex", ln)]
    if strict and r.returncode == 0:
        print("  실패  (hct.py) 토큰 밖 색을 본문에 적었다 — var(--br-*) 토큰으로 바꾼다")
        return 1
    return r.returncode


def check_docx(path, html=None):
    cmd = [PY, os.path.join(HERE, "check_docx.py"), path]
    if html:
        cmd += ["--html", html]
    r = subprocess.run(cmd, capture_output=True, text=True)
    lines = (r.stdout + r.stderr).splitlines()
    print("\n검사 (check_docx.py)")
    for ln in lines:
        if re.match(r"\s*(실패|주의)\s", ln) or ln.startswith("결과"):
            print("  " + ln.strip())
    return r.returncode


def cmd_form(a):
    if a.use:
        r = subprocess.run([PY, os.path.join(HERE, "build_form.py"), a.use])
        return r.returncode
    f = active_form()
    if not f:
        print("양식 정의를 찾지 못했다 — forms/ 와 blue-doc.css 의 --bd-form 을 확인한다")
        return 1
    print(f"지금 양식: {f['id']} — {f['name']} (forms/{f['id']}.json)")
    print("  HTML · PDF(blue-doc.css 생성 블록)와 Word(docx/from_doc.js)가 이 파일 하나를 읽는다")
    others = sorted(x[:-5] for x in os.listdir(os.path.join(SKILL, "forms")) if x.endswith(".json") and x[:-5] != f["id"])  # _test/ 는 빼고
    if others:
        print(f"  다른 양식: {', '.join(others)} — 바꾸려면 `hct.py form --use <스킬>/forms/<id>.json`")
    r = subprocess.run([PY, os.path.join(HERE, "build_form.py"), os.path.join(SKILL, "forms", f["id"] + ".json"), "--check"],
                       capture_output=True, text=True)
    print("  " + (r.stdout.strip() or r.stderr.strip()))
    return r.returncode


def cmd_check(a):
    if a.file.lower().endswith(".docx"):
        return check_docx(a.file, a.html)
    return check_file(a.file)


def main():
    ap = argparse.ArgumentParser(description="HCT 회사 보고서 — 목적 × 형식 추천 · 만들기 · 검사")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("formats", help="목적 × 형식 표")
    s.add_argument("--json", action="store_true")
    s = sub.add_parser("new", help="새 보고서 뼈대 — 견본을 복사한다")
    s.add_argument("purpose", choices=list(PURPOSES))
    s.add_argument("dir")
    s.add_argument("--kind", help="종류 — formats 의 「종류」 참고")
    s = sub.add_parser("build", help="원본 → 형식들 → 검사")
    s.add_argument("src", help="new 로 만든 폴더(또는 deck.yaml · HTML 원본)")
    s.add_argument("--formats", help="쉼표로 — html,pdf,pptx,docx,xlsx. 없으면 그 목적의 기본 형식")
    s.add_argument("-o", "--out", help="출력 폴더 (기본: 원본 폴더의 상위)")
    s.add_argument("--name", help="출력 파일 이름(확장자 없이)")
    s.add_argument("--title", help="문서명 — 꼬리말에 들어간다(문서 · 보드)")
    s.add_argument("--brand", help="brand.json (기본: 스킬 안 brand/hct)")
    s.add_argument("--no-check", action="store_true", help="검사 생략 — 완료 보고에 쓰지 않는다")
    s = sub.add_parser("form", help="A4 문서 양식 — 지금 양식 보기 · 다른 양식으로 바꾸기(HTML · PDF · Word 함께)")
    s.add_argument("--use", help="쓸 양식 정의 JSON (forms/<id>.json). 검사 후 blue-doc.css 를 다시 만든다")
    s = sub.add_parser("check", help="검사만 — HTML 또는 .docx")
    s.add_argument("file")
    s.add_argument("--html", help=".docx 를 검사할 때 대조할 원본 HTML")
    a = ap.parse_args()
    return {"formats": cmd_formats, "new": cmd_new, "build": cmd_build, "check": cmd_check, "form": cmd_form}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
