#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AX_BLUE_REPORT_V1 PDF — 덱 HTML → 링크 · 책갈피 · 쪽 이름이 붙은 PDF.

  python3 scripts/make_pdf.py decks-out/deck.html -o decks-out/deck.pdf [--keep-order] [--no-appendix] [--no-detail 08,11] [--no-qpdf] [--variable-font]

  · 화면은 scripts/pdf_render.js(Playwright · Chromium)가 1920×1080 으로 찍는다.
  · 본문 장 뒤에 그 장이 부르는 부록을 「NN-k」 상세 쪽으로 끼워 넣는다(--keep-order 면 덱 순서 그대로).
    특정 장만 끼우지 않으려면 --no-detail 08 (쪽 번호 또는 장 id, 쉼표로 여럿) 또는 장에 data-pdf-detail="off".
    끼우지 않은 부록은 부록 묶음(부록 NN)으로 뒤에 남고, --no-appendix 면 빠진다.
  · 두 화면 장은 화면마다 한 쪽(「NN②」).
  · 「부록 NN」 글자 · 지금 원문 보기 버튼 · INDEX 줄 · 상세 쪽의 「↩ NN」 은 PDF 안 링크가 된다.
  · 책갈피: 표지 · INDEX · 요약 / 장별 묶음(장 → 쪽 → 상세) / 부록.
필요: node + playwright(chromium), pip install pypdf. qpdf 가 있으면 용량을 줄인다.
"""
import argparse, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
PX = 0.75   # CSS px → pt

def static_fonts(deck, tmp):
    """가변 폰트는 Chromium PDF 에 Type3(그림 글자)로 들어가 용량이 크고 글자 검색이 안 된다.
    덱에 쓰인 굵기마다 고정 굵기 폰트를 만들어 PDF 를 찍을 때만 바꿔 끼운다."""
    import base64, io, re
    try:
        from fontTools.ttLib import TTFont
        from fontTools.varLib import instancer
        from fontTools import subset
        import brotli  # noqa: F401  (woff2 읽기 · 쓰기)
    except ImportError:
        print('· fontTools · brotli 가 없어 가변 폰트 그대로 찍는다(PDF 용량이 커진다) — pip install fonttools brotli', file=sys.stderr)
        return None
    t = open(deck, encoding='utf-8').read()
    chars = {c for c in t if ord(c) > 0x7f} | {chr(c) for c in range(0x20, 0x7f)} | set('↩·…—–')
    wts = {400, 700} | {int(x) for x in re.findall(r'font(?:-weight)?\s*:\s*(?:italic\s+)?(\d{3})\b', t)}
    wts = sorted(w for w in wts if 100 <= w <= 920)
    src = TTFont(os.path.join(SKILL, 'core', 'fonts', 'PretendardVariable.woff2'))
    o = subset.Options(); o.layout_features = ['*']; o.name_IDs = ['*']; o.notdef_outline = True
    s = subset.Subsetter(o); s.populate(unicodes=[ord(c) for c in chars]); s.subset(src)
    css = []
    for wt in wts:
        f = instancer.instantiateVariableFont(src, {'wght': wt}, inplace=False)
        f.flavor = 'woff2'; b = io.BytesIO(); f.save(b)
        css.append("@font-face{font-family:'Pretendard';src:url(data:font/woff2;base64,%s) format('woff2');font-weight:%d;font-style:normal;font-display:block}" % (base64.b64encode(b.getvalue()).decode(), wt))
    p = os.path.join(tmp, 'static-fonts.css'); open(p, 'w').write('\n'.join(css))
    print('· 고정 굵기 폰트 %d종(%s)으로 찍는다' % (len(wts), ','.join(map(str, wts))))
    return p

def main():
    ap = argparse.ArgumentParser(description='AX_BLUE_REPORT_V1 PDF')
    ap.add_argument('deck'); ap.add_argument('-o', required=True)
    ap.add_argument('--keep-order', action='store_true'); ap.add_argument('--no-appendix', action='store_true')
    ap.add_argument('--no-detail', help='상세 쪽을 끼우지 않을 본문 장 — 쪽 번호 또는 id, 쉼표로 여럿(예: 08,11)')
    ap.add_argument('--no-qpdf', action='store_true'); ap.add_argument('--keep-manifest', action='store_true')
    ap.add_argument('--variable-font', action='store_true', help='고정 굵기 폰트로 바꾸지 않는다(빠르지만 PDF 가 크다)')
    a = ap.parse_args()
    try:
        from pypdf import PdfReader, PdfWriter
        from pypdf.generic import Fit, DictionaryObject, NameObject, ArrayObject, FloatObject, NumberObject
    except ImportError:
        sys.exit('pypdf 가 없다 — pip install pypdf')
    tmp = tempfile.mkdtemp(prefix='axbr-pdf-')
    raw, man = os.path.join(tmp, 'raw.pdf'), os.path.join(tmp, 'manifest.json')
    cmd = ['node', os.path.join(HERE, 'pdf_render.js'), a.deck, raw, man] + (['--keep-order'] if a.keep_order else []) + (['--no-appendix'] if a.no_appendix else []) + (['--no-detail', a.no_detail] if a.no_detail else [])
    fc = None if a.variable_font else static_fonts(a.deck, tmp)
    if fc: cmd += ['--font-css', fc]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: sys.exit('화면 찍기 실패\n' + r.stdout + r.stderr)
    M = json.load(open(man, encoding='utf-8')); pages = M['pages']
    rd = PdfReader(raw)
    if len(rd.pages) != len(pages): sys.exit('쪽 수가 다르다: PDF %d · 계획 %d (한 장이 두 쪽으로 넘쳤을 수 있다)' % (len(rd.pages), len(pages)))
    w = PdfWriter()
    for pg in rd.pages: w.add_page(pg)
    idx = {p['label']: i for i, p in enumerate(pages)}
    H = float(w.pages[0].mediabox.height)

    # 링크
    nlink, miss = 0, set()
    for i, p in enumerate(pages):
        for l in p.get('links', []):
            j = idx.get(l['to'])
            if j is None: miss.add(l['to']); continue
            x1, y1 = l['x'] * PX, H - (l['y'] + l['h']) * PX
            # /Dest 첫 항목은 쪽 번호가 아니라 쪽 객체 참조여야 한다(PDF 규격 · 일부 뷰어는 번호를 무시한다)
            an = DictionaryObject({
                NameObject('/Type'): NameObject('/Annot'), NameObject('/Subtype'): NameObject('/Link'),
                NameObject('/Rect'): ArrayObject([FloatObject(v) for v in (x1, y1, x1 + l['w'] * PX, y1 + l['h'] * PX)]),
                NameObject('/Border'): ArrayObject([NumberObject(0), NumberObject(0), NumberObject(0)]),
                NameObject('/Dest'): ArrayObject([w.pages[j].indirect_reference, NameObject('/Fit')])})
            ref = (getattr(w, 'add_object', None) or w._add_object)(an)
            pg = w.pages[i]
            if '/Annots' not in pg: pg[NameObject('/Annots')] = ArrayObject()
            pg['/Annots'].append(ref)
            nlink += 1

    # 책갈피
    top, chap_node, last_body, apx_node = None, None, {}, None
    for i, p in enumerate(pages):
        k, name = p['kind'], '%s  %s' % (p['label'], p['title'] or '')
        if k == 'cover': w.add_outline_item(p['title'] or '표지', i, fit=Fit.fit())
        elif k == 'chapter': chap_node = w.add_outline_item(name, i, fit=Fit.fit()); last_body = {}
        elif k == 'body':
            node = w.add_outline_item(name, i, parent=chap_node, fit=Fit.fit()); last_body[p['label']] = node
        elif k in ('detail', 'view'):
            par = last_body.get(p.get('parent')) or chap_node
            w.add_outline_item(name, i, parent=par, fit=Fit.fit())
        elif k == 'divider': apx_node = w.add_outline_item('부록', i, fit=Fit.fit())
        else: w.add_outline_item(name, i, parent=apx_node, fit=Fit.fit())
    w.page_mode = '/UseOutlines'

    # 쪽 이름(뷰어 쪽 번호 칸에 「07」「07-1」「부록 03」 으로 보인다)
    for i, p in enumerate(pages): w.set_page_label(i, i, prefix=p['label'])
    w.add_metadata({'/Title': M.get('title') or 'AX_BLUE_REPORT_V1', '/Subject': 'AX_BLUE_REPORT_V1', '/Creator': 'ax-blue-report · make_pdf.py'})
    os.makedirs(os.path.dirname(os.path.abspath(a.o)) or '.', exist_ok=True)
    mid = os.path.join(tmp, 'linked.pdf')
    with open(mid, 'wb') as f: w.write(f)
    if not a.no_qpdf and shutil.which('qpdf'):
        q = subprocess.run(['qpdf', '--object-streams=generate', '--compress-streams=y', '--recompress-flate', mid, a.o], capture_output=True, text=True)
        if q.returncode not in (0, 3): shutil.copy(mid, a.o); print('· qpdf 실패 — 압축 없이 저장', file=sys.stderr)
    else:
        shutil.copy(mid, a.o)
    if a.keep_manifest: shutil.copy(man, os.path.splitext(a.o)[0] + '.manifest.json')
    shutil.rmtree(tmp, ignore_errors=True)
    print('PDF %s — %d쪽 · 링크 %d · %.2f MB%s' % (a.o, len(pages), nlink, os.path.getsize(a.o) / 1048576, (' · 대상 없는 링크 %s' % sorted(miss)) if miss else ''))
    if M.get('errors'): print('· 페이지 오류:', M['errors'][:5], file=sys.stderr)

if __name__ == '__main__':
    main()
