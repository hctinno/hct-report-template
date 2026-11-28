#!/usr/bin/env python3
"""회사 양식 Word(.docx) 검사 — doc_to_docx.py 가 만든 파일이 HTML 원본과 회사 규칙대로인지 본다.

    python3 scripts/check_docx.py decks-out/회의록.docx --html decks-out/회의록.html

실패(종료 코드 1)
  - 파일이 열리지 않는다 · 필수 부품(document · styles · numbering · 머리글 · 바닥글)이 없다
  - ZIP 안에 폴더 항목이 있다 (클라우드 공동 편집에서 Word 가 거부한 사례가 있다)
  - 글꼴이 Pretendard 가 아니다
  - 색이 blue-report.css 토큰 밖이다
  - 글자가 9pt 보다 작다 (머리말 · 꼬리말 · 칩 9pt, 본문 10.5pt)
  - 머리글에 로고 · 문서번호, 바닥글에 쪽번호 필드가 없다
  - HTML 원본의 글자가 Word 에 빠졌다 (--html 을 줄 때)
  - HTML 의 장 · 절 제목 수와 Word 의 제목 1 · 제목 2 수가 다르다 (--html 을 줄 때)
주의
  - LibreOffice 로 그린 쪽수가 HTML 쪽수와 다르다 (soffice 가 있을 때만. Word 와 LibreOffice 는 줄바꿈이 조금 다르다)
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
CSS = os.path.join(SKILL, "assets", "blue-report.css")
sys.path.insert(0, HERE)

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
FORMS = os.path.join(SKILL, "forms")


def tokens():
    css = open(CSS, encoding="utf-8").read()
    root = css[css.index(":root"):]
    out = set()
    for m in re.finditer(r"--br-[a-z0-9-]+\s*:\s*#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b", root):
        h = m.group(1)
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        out.add(h.upper())
    return out


def docx_text(xml):
    """w:t 를 문서 순서대로. 문단 경계는 공백."""
    xml = re.sub(r"</w:p>", " ", xml)
    parts = re.findall(r"<w:t(?:\s[^>]*)?>([^<]*)</w:t>", xml)
    import html
    return html.unescape(" ".join(parts))


NUMERAL = re.compile(r"^(\d+|[\u2160-\u216B]+)[.)]?$")


def html_words(path, form=None):
    from doc_to_docx import parse  # 같은 파서 — 무엇을 글자로 보는지 어긋나지 않게
    with open(path, encoding="utf-8") as f:
        root = parse(f.read())
    doc = root.find(lambda n: n.has("bd-doc"))
    if doc is None:
        return None, 0, 0, 0
    words = []
    pages = doc.find_all(lambda n: n.has("bd-page"))

    renum = bool(form) and (form["type"]["h1"]["style"] == "box" or form["type"]["h1"]["numeral"] == "roman")

    plain_toc = bool(form) and form["toc"]["style"] == "plain"

    def walk(n):
        if plain_toc and (n.has("bd-toc-p") or n.has("bd-toc-d")):
            return   # 양식이 목차 쪽번호를 감춘다(HTML · Word 모두)
        if renum and n.has("bd-h1"):
            # 양식이 장 번호를 바꾸거나(1. → Ⅰ) 번호 칸으로 옮긴다 — 번호는 빼고 대조한다
            ws = n.text_content().split()
            words.extend(ws[1:] if ws and NUMERAL.match(ws[0]) else ws)
            return
        for c in n.children:
            if c.tag is None:
                words.extend(c.text.split())
            elif c.tag not in ("script", "style", "button") and not (c.has("bd-head") or c.has("bd-foot")):
                walk(c)
    for pg in pages:
        walk(pg)
    h1 = len(doc.find_all(lambda n: n.has("bd-h1")))
    h2 = len(doc.find_all(lambda n: n.has("bd-h2")))
    return words, len(pages), h1, h2


def main():
    ap = argparse.ArgumentParser(description="회사 양식 Word 검사")
    ap.add_argument("docx")
    ap.add_argument("--html", help="원본 HTML — 글자 누락 · 제목 수 · 쪽수 대조")
    ap.add_argument("--no-render", action="store_true", help="LibreOffice 쪽수 대조를 건너뛴다")
    ap.add_argument("--form", help="양식 정의 JSON — 주지 않으면 Word 가 적어 둔 양식(문서 설명의 「양식 <id>」)")
    a = ap.parse_args()

    fails, warns, passes = [], [], []
    # 양식 — 글꼴 · 하한 · 여백을 양식에서 읽는다(Word 생성기와 같은 파일)
    form_path = a.form
    if not form_path:
        try:
            core = zipfile.ZipFile(a.docx).read("docProps/core.xml").decode("utf-8")
            m = re.search(r"양식 ([A-Za-z0-9_-]+)", core)
            fid = m.group(1) if m else "hct-standard"
            form_path = next((c for c in (os.path.join(FORMS, fid + ".json"), os.path.join(FORMS, "_test", fid + ".json"))
                              if os.path.exists(c)), os.path.join(FORMS, "hct-standard.json"))
        except Exception:
            form_path = os.path.join(FORMS, "hct-standard.json")
    import json
    from build_form import px as form_px, resolve
    form = resolve(json.load(open(form_path, encoding="utf-8")))
    FONT_OK = {form["font"]["body"]["word"], form["font"]["heading"]["word"]}
    MIN_HALF_PT = round(form_px(form["type"]["small"]["size"]) * 72 / 96 * 2)
    try:
        z = zipfile.ZipFile(a.docx)
    except Exception as e:
        print(f"  실패  파일이 열리지 않는다 — {e}")
        print("결과  실패 1")
        return 1
    names = z.namelist()
    need = ["word/document.xml", "word/styles.xml", "word/numbering.xml", "[Content_Types].xml"]
    miss = [n for n in need if n not in names]
    (fails if miss else passes).append(f"필수 부품 {'없음: ' + ', '.join(miss) if miss else '있음'}")
    dirs = [n for n in names if n.endswith("/")]
    (fails if dirs else passes).append(f"ZIP 폴더 항목 {len(dirs)}개")
    if miss:
        for m in fails:
            print(f"  실패  {m}")
        print(f"결과  실패 {len(fails)}")
        return 1

    doc = z.read("word/document.xml").decode("utf-8")
    styles = z.read("word/styles.xml").decode("utf-8")
    hdrs = [z.read(n).decode("utf-8") for n in names if re.match(r"word/header\d*\.xml$", n)]
    ftrs = [z.read(n).decode("utf-8") for n in names if re.match(r"word/footer\d*\.xml$", n)]
    numbering = z.read("word/numbering.xml").decode("utf-8")
    allxml = doc + styles + numbering + "".join(hdrs) + "".join(ftrs)

    # 글꼴 — 테마 글꼴 참조(+mn-lt 등)는 rFonts 에 이름이 없어 걸리지 않는다
    fonts = set()
    for m in re.finditer(r"<w:rFonts\b([^>]*)/?>", allxml):
        for v in re.findall(r'w:(?:ascii|eastAsia|hAnsi|cs)="([^"]*)"', m.group(1)):
            fonts.add(v)
    bad = sorted(fonts - FONT_OK)
    (fails if bad else passes).append(f"글꼴 {'양식 밖: ' + ', '.join(bad) if bad else ' · '.join(sorted(FONT_OK)) + ' 만'}")

    # 색 — 글자색 · 음영 · 테두리
    tok = tokens() | {"FFFFFF"}
    used = set()
    for m in re.finditer(r'w:(?:color|fill)="([0-9A-Fa-f]{6})"', allxml):
        used.add(m.group(1).upper())
    off = sorted(used - tok)
    (fails if off else passes).append(f"색 {len(used)}개 {'— 토큰 밖: ' + ', '.join(off) if off else '모두 토큰'}")

    # 글자 크기 — 글자가 있는 run 만 본다(간격용 빈 문단은 1pt 로 둔다)
    small = 0
    for run in re.findall(r"<w:r>(.*?)</w:r>", doc + "".join(hdrs) + "".join(ftrs), re.S):
        if not re.search(r"<w:t(?:\s[^>]*)?>[^<]*\S[^<]*</w:t>", run):
            continue
        m = re.search(r'<w:sz w:val="(\d+)"', run)
        if m and int(m.group(1)) < MIN_HALF_PT:
            small += 1
    for m in re.finditer(r'<w:style\b[^>]*w:styleId="([^"]+)".*?</w:style>', styles, re.S):
        if m.group(1) == "HctGap":
            continue
        s = re.search(r'<w:sz w:val="(\d+)"', m.group(0))
        if s and int(s.group(1)) < MIN_HALF_PT:
            small += 1
    (fails if small else passes).append(f"{MIN_HALF_PT / 2:g}pt 미만 글자 {small}곳")

    # 여백 — 양식의 좌우 여백과 같은가(위아래는 머리말 · 꼬리말 높이가 더해져 따로 본다)
    pg = re.search(r"<w:pgMar\b([^>]*)/>", doc)
    if pg:
        got = dict(re.findall(r'w:(left|right|header|footer)="(\d+)"', pg.group(1)))
        tw = lambda v: round(form_px(v) * 15)
        mg = form["page"]["margin"]
        want = {"left": tw(mg["left"]), "right": tw(mg["right"]), "header": tw(mg["top"]), "footer": tw(mg["bottom"])}
        off = [k for k, v in want.items() if abs(int(got.get(k, -999)) - v) > 2]
        (fails if off else passes).append(f"여백 {'양식과 다름: ' + ', '.join(off) if off else '양식 ' + form['id'] + ' 과 같음'}")

    # 머리말 · 꼬리말
    hdr = "".join(hdrs)
    head_items = {form["header"].get(k) for k in ("left", "right", "center")}
    if "logo" in head_items:
        ok_logo = "<pic:pic" in hdr or "<w:drawing" in hdr
        (passes if ok_logo else warns).append(f"머리글 로고 {'그림' if ok_logo else '없음 — brand.json 의 logoOnLight 를 확인 (워드마크 글자로 대체됨)'}")
    # 문서번호 — 머리글 오른쪽. 비우면 결재 · 보관에서 문서를 찾을 수 없다. 모르면 「확인 필요」로 둔다
    hdr_text = re.sub(r"\s+", "", docx_text(hdr))
    if "docNo" in head_items:
        if not hdr_text:
            warns.append("머리글 문서번호가 비었다 — 번호를 모르면 data-doc-no 에 「문서번호 확인 필요」로 둔다")
        else:
            passes.append("머리글 문서번호 있음")
    ftr = "".join(ftrs)
    if "{page}" in form["footer"]["left"] + form["footer"]["right"]:
        ok_page = re.search(r"PAGE\b", ftr) is not None
        (passes if ok_page else fails).append(f"바닥글 쪽번호 필드 {'있음' if ok_page else '없음'}")
    else:
        passes.append("바닥글 — 양식에 쪽번호 없음")

    # 원본 대조
    text = docx_text(doc)
    flat = re.sub(r"\s+", "", text)
    if a.html:
        words, npages, h1, h2 = html_words(a.html, form)
        if words is None:
            fails.append("원본 HTML 에 .bd-doc 가 없다")
        else:
            pos, lost = 0, []
            for w in words:
                i = flat.find(w, pos)
                if i < 0:
                    lost.append(w)
                else:
                    pos = i + len(w)
            if lost:
                fails.append(f"HTML 글자 {len(lost)}개가 Word 에 없다(또는 순서가 다르다): {' '.join(lost[:8])}")
            else:
                passes.append(f"HTML 글자 {len(words)}어절 모두 Word 에 있음")
            # 제목은 문단이어야 하고 「다음 문단과 함께」가 걸려 있어야 한다 — 표 안 제목이나 keepNext 없는 제목은
            # Word · LibreOffice · 한컴에서 제목만 쪽 끝에 남는다
            outside = re.sub(r"<w:tbl>.*?</w:tbl>", "", doc, flags=re.S)
            heads = [p for p in re.findall(r"<w:p[ >].*?</w:p>", outside, flags=re.S)
                     if re.search(r'<w:pStyle w:val="Heading[12]"/>', p)]
            in_tbl = len(re.findall(r'<w:pStyle w:val="Heading[12]"/>', doc)) - len(heads)
            def style_keeps(sid):
                m = re.search(r'<w:style [^>]*w:styleId="%s".*?</w:style>' % sid, styles, flags=re.S)
                return bool(m and re.search(r"<w:keepNext(/>| )", m.group(0)))
            keep_style = {sid: style_keeps(sid) for sid in ("Heading1", "Heading2")}
            def keeps(p):
                if re.search(r"<w:keepNext(/>| )", p):
                    return True
                sid = re.search(r'<w:pStyle w:val="(Heading[12])"/>', p).group(1)
                return keep_style[sid]
            no_keep = [re.sub(r"<[^>]+>", "", p)[:20] for p in heads if not keeps(p)]
            if in_tbl or no_keep:
                fails.append(f"제목 쪽 끝 방지 — 표 안 제목 {in_tbl}개 · 다음 문단과 함께 없는 제목 {len(no_keep)}개 {' '.join(no_keep[:4])}")
            else:
                passes.append(f"제목 쪽 끝 방지 — 제목 {len(heads)}개 모두 문단 · 다음 문단과 함께")
            d1 = len(re.findall(r'<w:pStyle w:val="Heading1"/>', doc))
            d2 = len(re.findall(r'<w:pStyle w:val="Heading2"/>', doc))
            if (d1, d2) != (h1, h2):
                fails.append(f"제목 수 — HTML 장 {h1} · 절 {h2}, Word 제목1 {d1} · 제목2 {d2}")
            else:
                passes.append(f"제목 수 일치 (장 {h1} · 절 {h2})")
            # 쪽수 — LibreOffice 가 있으면
            soffice = shutil.which("soffice") or shutil.which("libreoffice")
            if form["page"]["breaks"] == "flow":
                passes.append("쪽수 — 양식이 흘려 나누므로(flow) HTML 쪽수와 대조하지 않는다")
            elif soffice and not a.no_render:
                with tempfile.TemporaryDirectory() as tmp:
                    env = dict(os.environ, HOME=tmp)
                    subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", tmp, os.path.abspath(a.docx)],
                                   capture_output=True, timeout=180, env=env)
                    pdf = os.path.join(tmp, os.path.splitext(os.path.basename(a.docx))[0] + ".pdf")
                    n = None
                    if os.path.exists(pdf):
                        data = open(pdf, "rb").read()
                        m = re.findall(rb"/Type\s*/Pages\b.*?/Count\s+(\d+)", data, re.S)
                        n = max(int(x) for x in m) if m else None
                    if n is None:
                        warns.append("LibreOffice 로 쪽수를 세지 못했다 — Word 로 열어 쪽수를 확인한다")
                    elif n != npages:
                        warns.append(f"쪽수 — HTML {npages}쪽, Word(LibreOffice 렌더) {n}쪽. 넘친 쪽은 Word 로 열어 확인한다")
                    else:
                        passes.append(f"쪽수 일치 ({n}쪽 · LibreOffice 렌더)")

    for p in passes:
        print(f"  통과  {p}")
    for w in warns:
        print(f"  주의  {w}")
    for f in fails:
        print(f"  실패  {f}")
    print(f"결과  통과 {len(passes)} · 주의 {len(warns)} · 실패 {len(fails)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
