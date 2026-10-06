#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AX_BLUE_REPORT_V1 PDF 보기 — PDF 를 한 파일 HTML 뷰어로 바꾼다(쪽 그림 + 누를 수 있는 링크 + 책갈피 이동).

  python3 scripts/make_pdf_viewer.py decks-out/deck.pdf -o decks-out/deck-pdf-viewer.html [--dpi 80] [--artifact]

  · 쪽 그림: pdftoppm(poppler) → webp. 링크 · 책갈피 · 쪽 이름은 PDF 에서 그대로 읽는다(pypdf).
  · --artifact  Claude Artifact 게시용(<!DOCTYPE>·<html>·<head>·<body> 없이). 16MB 를 넘으면 --dpi 를 낮춘다.
필요: poppler-utils(pdftoppm), pip install pypdf pillow
"""
import argparse, base64, glob, html, io, os, shutil, subprocess, sys, tempfile

def outline_rows(rd):
    rows = []
    def walk(items, depth):
        last = None
        for it in items:
            if isinstance(it, list): walk(it, depth + 1); continue
            try: rows.append((depth, rd.get_destination_page_number(it), it.title))
            except Exception: pass
    walk(rd.outline, 0)
    return rows

def main():
    ap = argparse.ArgumentParser(description='AX_BLUE_REPORT_V1 PDF 뷰어')
    ap.add_argument('pdf'); ap.add_argument('-o', required=True)
    ap.add_argument('--dpi', type=int, default=80); ap.add_argument('--quality', type=int, default=82)
    ap.add_argument('--artifact', action='store_true'); ap.add_argument('--title')
    a = ap.parse_args()
    try:
        from pypdf import PdfReader
        from PIL import Image
    except ImportError:
        sys.exit('pypdf · pillow 가 필요하다 — pip install pypdf pillow')
    if not shutil.which('pdftoppm'): sys.exit('pdftoppm 이 없다 — poppler-utils 를 설치한다')
    rd = PdfReader(a.pdf)
    title = a.title or (rd.metadata.title if rd.metadata and rd.metadata.title else os.path.splitext(os.path.basename(a.pdf))[0])
    labels = rd.page_labels
    tmp = tempfile.mkdtemp(prefix='axbr-view-')
    subprocess.run(['pdftoppm', '-r', str(a.dpi), '-png', a.pdf, os.path.join(tmp, 'p')], check=True)
    pngs = sorted(glob.glob(os.path.join(tmp, 'p-*.png')), key=lambda p: int(p.rsplit('-', 1)[1].split('.')[0]))
    if len(pngs) != len(rd.pages): sys.exit('쪽 그림 수가 다르다')
    # 쪽 → 그림 · 링크
    pages = []
    idmap = {}
    for i, pg in enumerate(rd.pages):
        idmap[pg.indirect_reference.idnum if pg.indirect_reference else i] = i
    for i, (pg, png) in enumerate(zip(rd.pages, pngs)):
        im = Image.open(png).convert('RGB'); b = io.BytesIO(); im.save(b, 'WEBP', quality=a.quality, method=6)
        W, H = float(pg.mediabox.width), float(pg.mediabox.height)
        links = []
        for an in (pg.get('/Annots') or []):
            o = an.get_object()
            if o.get('/Subtype') != '/Link': continue
            dest = o.get('/Dest')
            if dest is None and o.get('/A') is not None: dest = o['/A'].get('/D')
            if dest is None: continue
            try:
                ref = dest[0]; j = idmap.get(ref.idnum)
            except Exception: j = None
            if j is None: continue
            x1, y1, x2, y2 = [float(v) for v in o['/Rect']]
            links.append((j, min(x1, x2) / W * 100, (H - max(y1, y2)) / H * 100, abs(x2 - x1) / W * 100, abs(y2 - y1) / H * 100))
        pages.append({'img': base64.b64encode(b.getvalue()).decode(), 'w': im.width, 'h': im.height, 'links': links,
                      'label': labels[i] if labels else str(i + 1)})
    shutil.rmtree(tmp, ignore_errors=True)
    rows = outline_rows(rd)
    E = lambda s: html.escape(str(s), quote=True)
    opts = ''.join('<option value="%d">%s%s</option>' % (p, '　' * d, E(t)) for d, p, t in rows) or \
           ''.join('<option value="%d">%s</option>' % (i, E(p['label'])) for i, p in enumerate(pages))
    figs = []
    for i, p in enumerate(pages):
        hs = ''.join('<a class="hs" href="#p%d" data-to="%d" style="left:%.3f%%;top:%.3f%%;width:%.3f%%;height:%.3f%%" aria-label="%s 쪽으로"></a>'
                     % (j, j, x, y, w, h, E(pages[j]['label'])) for j, x, y, w, h in p['links'])
        figs.append('<figure id="p%d" data-i="%d"><div class="pg"><img src="data:image/webp;base64,%s" width="%d" height="%d" alt="%s 쪽" loading="%s" decoding="async">%s</div>'
                    '<figcaption>%s</figcaption></figure>' % (i, i, p['img'], p['w'], p['h'], E(p['label']), 'eager' if i < 3 else 'lazy', hs, E(p['label'])))
    css = """
:root{--bg:#eef1f6;--fg:#141a2b;--muted:#5b6478;--bar:#ffffffee;--line:#d6dce8;--accent:#1f4fd8;--sheet:#fff;--shadow:0 1px 3px rgba(20,30,60,.12),0 8px 24px rgba(20,30,60,.08)}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#0d111b;--fg:#e6eaf3;--muted:#98a2b8;--bar:#141a28ee;--line:#273048;--accent:#7aa2ff;--sheet:#1a2131;--shadow:0 1px 3px rgba(0,0,0,.5);color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0d111b;--fg:#e6eaf3;--muted:#98a2b8;--bar:#141a28ee;--line:#273048;--accent:#7aa2ff;--sheet:#1a2131;--shadow:0 1px 3px rgba(0,0,0,.5);color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 'Pretendard',-apple-system,'Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR',sans-serif;word-break:keep-all}
.top{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;padding:10px 16px;background:var(--bar);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.top h1{margin:0;font-size:15px;font-weight:800;letter-spacing:-.01em;min-width:0;flex:1 1 220px;text-wrap:balance}
.top select{min-width:0;max-width:100%;flex:0 1 360px;padding:6px 8px;border:1px solid var(--line);border-radius:8px;background:var(--sheet);color:var(--fg);font:inherit}
.top .cnt{color:var(--muted);font-variant-numeric:tabular-nums;white-space:nowrap}
main{display:grid;gap:22px;max-width:1200px;margin:0 auto;padding-block:20px 60px;padding-inline:16px}
figure{margin:0;scroll-margin-top:calc(var(--toph,56px) + 12px)}
.pg{position:relative;background:var(--sheet);box-shadow:var(--shadow);border-radius:6px;overflow:hidden}
.pg img{display:block;width:100%;height:auto;max-width:100%}
.hs{position:absolute;border-radius:4px;outline:2px solid transparent;transition:background .15s,outline-color .15s}
.hs:hover,.hs:focus-visible{background:color-mix(in srgb,var(--accent) 16%,transparent);outline-color:var(--accent)}
figcaption{margin-top:6px;color:var(--muted);font-size:12px;font-variant-numeric:tabular-nums}
"""
    js = """
(function(){var sel=document.getElementById('jump'),cnt=document.getElementById('cnt'),figs=[].slice.call(document.querySelectorAll('figure')),n=figs.length;
document.documentElement.style.setProperty('--toph',document.querySelector('.top').offsetHeight+'px');
function go(i){var f=document.getElementById('p'+i);if(f)f.scrollIntoView({behavior:'smooth',block:'start'});}
sel.addEventListener('change',function(){go(+sel.value);});
document.addEventListener('click',function(e){var a=e.target.closest('.hs');if(!a)return;e.preventDefault();go(+a.getAttribute('data-to'));});
var opts=[].slice.call(sel.options).map(function(o){return +o.value;});
var top=document.querySelector('.top'),cur=-1,raf=0;
function sync(){raf=0;var lim=top.getBoundingClientRect().bottom+12,i=figs.length-1;
 for(var k=0;k<figs.length;k++){if(figs[k].getBoundingClientRect().bottom>lim+40){i=k;break;}}
 if(i===cur)return;cur=i;cnt.textContent=figs[i].querySelector('figcaption').textContent+' · '+(i+1)+' / '+n;
 var best=-1;opts.forEach(function(v,k){if(v<=i)best=k;});if(best>=0&&sel.selectedIndex!==best)sel.selectedIndex=best;}
addEventListener('scroll',function(){if(!raf)raf=requestAnimationFrame(sync);},{passive:true});addEventListener('resize',sync);sync();
addEventListener('keydown',function(e){if(e.target.tagName==='SELECT')return;var cur=figs.findIndex(function(f){return f.getBoundingClientRect().top>-10;});
 if(e.key==='ArrowRight'||e.key==='PageDown'){e.preventDefault();go(Math.min(n-1,(cur<0?0:cur)+1));}
 else if(e.key==='ArrowLeft'||e.key==='PageUp'){e.preventDefault();go(Math.max(0,(cur<0?0:cur)-1));}});
})();
"""
    head = '<title>%s</title>\n<meta name="description" content="%s — PDF 보기">\n<style>%s</style>\n' % (E(title), E(title), css)
    body = ('<header class="top"><h1>%s</h1><select id="jump" aria-label="책갈피로 이동">%s</select><span class="cnt" id="cnt">%s · 1 / %d</span></header>\n'
            '<main>%s</main>\n<script>%s</script>\n') % (E(title), opts, E(pages[0]['label']), len(pages), '\n'.join(figs), js)
    out = head + body if a.artifact else ('<!DOCTYPE html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
                                          + head + '</head>\n<body>\n' + body + '</body>\n</html>\n')
    os.makedirs(os.path.dirname(os.path.abspath(a.o)) or '.', exist_ok=True)
    open(a.o, 'w', encoding='utf-8').write(out)
    mb = os.path.getsize(a.o) / 1048576
    print('뷰어 %s — %d쪽 · 링크 %d · 책갈피 %d · %.2f MB' % (a.o, len(pages), sum(len(p['links']) for p in pages), len(rows), mb))
    if a.artifact and mb > 15.5: print('· 경고: Artifact 한도(16MB)에 가깝다 — --dpi 를 낮춘다', file=sys.stderr)

if __name__ == '__main__':
    main()
