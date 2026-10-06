#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AX_BLUE_REPORT_V1 덱 빌드 — 장(section) 묶음을 엔진 · 스타일 · 폰트 · 로고 · 워터마크와 합쳐 한 파일 HTML 로 만든다.

  python3 scripts/build_deck.py <장 파일 또는 .sections.html ...> -o decks-out/deck.html [옵션]
  python3 scripts/build_deck.py --gallery -o decks-out/gallery.html          # 견본 56장 전부

입력
  .html 파일 여러 개      slides/ 의 장 파일을 그대로 또는 고쳐서 준다. 준 순서가 장 순서다.
  .sections.html 하나     <section class="sl ...">…</section> 를 이어 적은 파일. 맨 위 <title> 이 있으면 덱 제목.
  --list 파일             장 파일 경로를 한 줄에 하나씩 적은 목록(# 주석 가능).

옵션
  --title "제목"          문서 제목(브라우저 탭 · 대본 창 저장 키). 없으면 입력의 <title> 또는 기본값.
  --brand <폴더>          로고 · 워터마크 묶음. 기본 brand/hct (logo-color · logo-white · watermark-light · watermark-dark · symbol)
  --present               발표용 — 대본 · 메모 · 대본 창을 빼고 처음부터 발표 모드로 연다(레이저만 남김)
  --artifact              Claude Artifact 게시용 — <!DOCTYPE>·<html>·<head>·<body> 껍데기 없이 낸다
  --full-font             폰트를 통째로 넣는다(기본: 이 덱 글자 + KS X 1001 한글 2,350자 + 영문 · 기호만)
  --no-video              영상 견본 데이터를 넣지 않는다(영상 버튼이 없는 덱의 용량 절약)
  --keep-numbers          장 제목(data-t) 번호를 그대로 둔다(기본: 실제 순서대로 01 · 02 … · 부록 01 … 로 다시 매김)
  --footer "문서명"        바닥줄 왼쪽 문서명. 기본은 --title. 장 파일에 적힌 문서명을 그대로 두려면 --keep-footer
"""
import argparse, base64, glob, io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
CORE = os.path.join(SKILL, 'core')

MIME = {'.webp': 'image/webp', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.svg': 'image/svg+xml',
        '.mp4': 'video/mp4', '.woff2': 'font/woff2'}

def b64(path):
    return base64.b64encode(open(path, 'rb').read()).decode()

def data_uri(path):
    return 'data:%s;base64,%s' % (MIME[os.path.splitext(path)[1].lower()], b64(path))

def read(p):
    return open(p, encoding='utf-8').read()

def find_brand(brand_dir, name):
    for ext in ('.webp', '.png', '.svg', '.jpg'):
        p = os.path.join(brand_dir, name + ext)
        if os.path.exists(p): return p
    sys.exit('브랜드 파일이 없다: %s/%s.(webp|png|svg|jpg)' % (brand_dir, name))

# ───────────────────────────────────────── 입력
def load_sections(args):
    files, title = [], None
    if args.gallery:
        files = [os.path.join(SKILL, 'slides', x.strip()) for x in read(os.path.join(CORE, 'order.txt')).splitlines() if x.strip()]
    if args.list:
        base = os.path.dirname(os.path.abspath(args.list))
        for line in read(args.list).splitlines():
            line = line.split('#', 1)[0].strip()
            if line: files.append(line if os.path.isabs(line) else os.path.join(base, line) if os.path.exists(os.path.join(base, line)) else os.path.join(SKILL, line))
    files += args.inputs
    if not files: sys.exit('입력 장이 없다 — 장 파일, .sections.html, --list 또는 --gallery 중 하나를 준다')
    out = []
    for f in files:
        t = read(f)
        m = re.search(r'<title>(.*?)</title>', t, re.S)
        if m and not title: title = m.group(1).strip()
        found = top_sections(t)
        if not found: sys.exit('장(<section class="sl ...">)이 없다: ' + f)
        out += found
    return out, title

def top_sections(t):
    """중첩을 고려해 최상위 <section class="sl ..."> 만 꺼낸다. <script>/<style> 원문 안은 건너뛴다."""
    low, i, spans = t.lower(), 0, []
    pat = re.compile(r'<(script|style)\b[^>]*>', re.I)
    skip = []
    while True:
        m = pat.search(t, i)
        if not m: break
        e = low.index('</' + m.group(1).lower(), m.end()); skip.append((m.end(), e)); i = e
    ev = []
    for m in re.finditer(r'<section\b[^>]*>|</section>', t):
        if any(a <= m.start() < b for a, b in skip): continue
        ev.append((m.start(), m.end(), m.group(0)))
    st = []
    for a, b, g in ev:
        if g.startswith('</'):
            s0, op = st.pop()
            if not st and re.search(r'class="sl[\s"]', op): spans.append(t[s0:b])
        else: st.append((a, g))
    return spans

def renumber(sections):
    """엔진 번호 규칙과 같게 data-t 앞 번호를 다시 매긴다 — 첫 장은 표지(번호 없음), id="appendix" 앞은 본문, .apx 는 부록."""
    out, body_k, apx_k, cut, changed = [], 0, 0, False, 0
    for i, s in enumerate(sections):
        m = re.match(r'<section\b[^>]*>', s); tag = m.group(0)
        cls = (re.search(r'\sclass="([^"]*)"', tag) or [None, ''])[1].split()
        dt_m = re.search(r'\sdata-t="([^"]*)"', tag)
        if re.search(r'\sid="appendix"', tag): cut = True
        new = None
        if dt_m and i > 0:
            dt = dt_m.group(1)
            if 'apx' in cls:
                apx_k += 1; new = re.sub(r'^(부록\s*)?\d{1,2}\s*(·\s*)?', '부록 %02d · ' % apx_k, dt, count=1)
            elif not cut:
                body_k += 1; new = re.sub(r'^\d{1,2}\s*', '%02d ' % body_k, dt, count=1) if re.match(r'^\d', dt) else '%02d %s' % (body_k, dt)
        if new is not None and new != dt_m.group(1):
            tag2 = tag[:dt_m.start(1)] + new + tag[dt_m.end(1):]; s = tag2 + s[len(tag):]; changed += 1
        out.append(s)
    if changed: print('· 장 제목 번호 %d곳을 실제 순서대로 다시 매겼다(--keep-numbers 로 끈다)' % changed, file=sys.stderr)
    return out

# ───────────────────────────────────────── 폰트
KSX1001 = None
def ksx_hangul():
    global KSX1001
    if KSX1001 is None:
        out = []
        for hi in range(0xB0, 0xC9):
            for lo in range(0xA1, 0xFF):
                try: out.append(bytes([hi, lo]).decode('euc-kr'))
                except UnicodeDecodeError: pass
        KSX1001 = ''.join(out)
    return KSX1001

def font_uri(full, text):
    src = os.path.join(CORE, 'fonts', 'PretendardVariable.woff2')
    if full: return data_uri(src)
    try:
        from fontTools import subset
        from fontTools.ttLib import TTFont
    except ImportError:
        print('· fontTools 가 없어 폰트를 통째로 넣는다 (pip install fonttools brotli)', file=sys.stderr)
        return data_uri(src)
    chars = set(text) | set(ksx_hangul()) | set(chr(c) for c in range(0x20, 0x7F)) | set('·…—–‘’“”「」『』《》〈〉※→←↑↓↗↘⇒▶▷▲△▼▽●○◆◇■□★☆✓✔✕×±≈≤≥%‰℃°①②③④⑤⑥⑦⑧⑨⑩ⅠⅡⅢⅣⅤ↩↪⤴✗✚')
    chars = {c for c in chars if not c.isspace() or c == ' '}
    opts = subset.Options(); opts.flavor = 'woff2'; opts.layout_features = ['*']; opts.name_IDs = ['*']; opts.notdef_outline = True
    try:
        f = TTFont(src); sub = subset.Subsetter(opts); sub.populate(unicodes=[ord(c) for c in chars]); sub.subset(f)
        bio = io.BytesIO(); f.flavor = 'woff2'; f.save(bio)
        return 'data:font/woff2;base64,' + base64.b64encode(bio.getvalue()).decode()
    except Exception as e:
        print('· 폰트 서브셋 실패(%s) — 통째로 넣는다' % e, file=sys.stderr)
        return data_uri(src)

# ───────────────────────────────────────── 발표용 손질
PRESENT_LASER = r"""/* ── 발표용: 대본 창 없음 · 레이저 포인터만(003c-presenter.js 대신) ── */
(function(){
 var d=document, body=d.body;
 var laser=d.createElement('div'); laser.id='laser'; body.appendChild(laser);
 var lx=innerWidth/2, ly=innerHeight/2;
 function laserPlace(){ laser.style.transform='translate('+lx+'px,'+ly+'px)'; }
 d.addEventListener('deck:present',function(e){
  if(e.detail.on){ body.classList.add('laser'); laserPlace(); laser.classList.add('on'); }
  else { body.classList.remove('laser'); laser.classList.remove('on'); }
 });
 d.addEventListener('deck:laser',function(){ body.classList.toggle('laser'); if(!body.classList.contains('laser')) laser.classList.remove('on'); });
 addEventListener('mousemove',function(e){ lx=e.clientX; ly=e.clientY; if(!body.classList.contains('present')||!body.classList.contains('laser')) return; laserPlace(); laser.classList.add('on'); },{passive:true});
 addEventListener('mouseout',function(e){ if(!e.relatedTarget&&!e.toElement) laser.classList.remove('on'); },{passive:true});
 addEventListener('blur',function(){ laser.classList.remove('on'); });
 if(body.classList.contains('present')) body.classList.add('laser');
})();
"""
def to_present_chrome(chrome):
    chrome = re.sub(r'<dt>N</dt><dd>[^<]*</dd><dt>P</dt><dd>[^<]*</dd>', '', chrome)
    return chrome.replace('<h4>조작</h4>', '<h4>조작 · 발표용(처음부터 발표 모드)</h4>', 1)

# ───────────────────────────────────────── 빌드
def build(args):
    sections, in_title = load_sections(args)
    if not args.keep_numbers: sections = renumber(sections)
    title = args.title or in_title or 'AX_BLUE_REPORT_V1'
    if not args.keep_footer:
        foot = (args.footer or title).replace('&', '&amp;').replace('<', '&lt;')
        sections = [re.sub(r'(<footer class="rf"><span>)[^<]*?(?=( · [^<]*)?</span>)', lambda m: m.group(1) + foot, s) for s in sections]
    brand_dir = args.brand if os.path.isabs(args.brand) else os.path.join(SKILL, args.brand) if not os.path.isdir(args.brand) else args.brand

    css = read(os.path.join(CORE, 'axbr.css'))
    chrome = read(os.path.join(CORE, 'chrome.html'))
    js_files = sorted(glob.glob(os.path.join(CORE, 'js', '*.js')))
    js_blocks = [(os.path.basename(f), read(f)) for f in js_files]

    if args.present:
        sections = [re.sub(r'data-notes="[^"]*"', 'data-notes=""', x) for x in sections]
        js_blocks = [('000-present-mode', "window.AXBR_MODE = 'present';   /* 엔진: N · P 끔 · 처음부터 발표 모드 */\n")] + \
                    [(n, PRESENT_LASER) if n.endswith('-presenter.js') else (n, c) for n, c in js_blocks]
        chrome = to_present_chrome(chrome)
        css += '\n/* 발표용 — 메모 버튼 · 메모 띠 숨김 */\n#nt,#notes{display:none!important}\n'

    body_html = '\n'.join(sections)
    # 토큰 풀기
    def media(m):
        p = os.path.join(CORE, 'media', m.group(1))
        if not os.path.exists(p): sys.exit('견본 파일이 없다: core/media/' + m.group(1))
        return data_uri(p)
    def brand(m): return data_uri(find_brand(brand_dir, m.group(1)))
    def resolve(t):
        t = re.sub(r'axbr-media:([\w./-]+\.\w+)', media, t)
        return re.sub(r'axbr-brand:([\w-]+)', brand, t)
    body_html, chrome = resolve(body_html), resolve(chrome)
    css = resolve(css)

    # 데이터
    ev = json.loads(read(os.path.join(CORE, 'data', 'evidence.json')))
    ev['media'] = {k: resolve(v) for k, v in ev.get('media', {}).items()}
    used = set()
    for m in re.finditer(r'data-ev="([^"]+)"', body_html): used |= set(m.group(1).split(','))
    ev['ev'] = {k: v for k, v in ev['ev'].items() if k in used}
    keep_img = {k for e in ev['ev'].values() for k, _ in e.get('imgs', [])}
    ev['img'] = {k: v for k, v in ev['img'].items() if k in keep_img}
    used_alias = {v[1:] for v in ev['img'].values() if isinstance(v, str) and v.startswith('@')}
    ev['media'] = {k: v for k, v in ev['media'].items() if k in used_alias}
    data_scripts = ['<script type="application/json" id="ev-data">%s</script>' % json.dumps(ev, ensure_ascii=False).replace('</', '<\\/')]
    for key in ('bma-rfp-payload', 'bma-rfp-payload-2'):
        data_scripts.append('<script type="application/json" id="%s">%s</script>' % (key, read(os.path.join(CORE, 'data', key + '.json')).replace('</', '<\\/')))
    vid = '' if args.no_video else b64(os.path.join(CORE, 'media', 'sample-video.mp4'))
    data_scripts.append('<script id="bma-video-data" type="text/plain">%s</script>' % vid)

    # 폰트(글자 모으기: 장 · 조작판 · JS 문자열 · CSS content)
    text = re.sub(r'<[^>]+>', ' ', body_html + chrome) + ''.join(c for _, c in js_blocks) + css
    css = css.replace('url(axbr-font:pretendard)', 'url(%s)' % font_uri(args.full_font, text))
    if 'axbr-' in re.sub(r'data:[^)"\']+', '', css + body_html + chrome):
        left = sorted(set(re.findall(r'axbr-(?:media|brand|font):[\w./-]+', css + body_html + chrome)))
        sys.exit('풀리지 않은 자산 토큰: %s' % left[:5])

    esc = title.replace('&', '&amp;').replace('<', '&lt;')
    head = ('<title>%s</title>\n<meta name="description" content="%s — AX_BLUE_REPORT_V1">\n' % (esc, esc.replace('"', '&quot;')) +
            '<style>\n%s</style>\n' % css)
    body = ('<div id="prog"></div>\n<main id="deck" tabindex="0" aria-label="%s 슬라이드">\n%s\n</main>\n' % (esc.replace('"', '&quot;'), body_html) +
            chrome + '\n' + '\n'.join(data_scripts) + '\n' +
            '\n'.join('<script>/* %s */\n%s</script>' % (n, c) for n, c in js_blocks) + '\n')
    if args.artifact:
        out = head + body
        if re.search(r'location\.(search|href)\s*=', out): sys.exit('location 변경 코드가 있다 — Artifact 에서 막힌다')
    else:
        out = ('<!DOCTYPE html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n'
               + head + '</head>\n<body>\n' + body + '</body>\n</html>\n')
    os.makedirs(os.path.dirname(os.path.abspath(args.o)), exist_ok=True)
    open(args.o, 'w', encoding='utf-8').write(out)
    mb = os.path.getsize(args.o) / 1048576
    print('빌드 %s — 장 %d · %.2f MB%s%s' % (args.o, len(sections), mb, ' · 발표용' if args.present else '', ' · Artifact 판' if args.artifact else ''))
    if args.artifact and mb > 15.5: print('· 경고: Artifact 한도(16MB)에 가깝다 — --no-video 또는 장 수를 줄인다', file=sys.stderr)

def main():
    ap = argparse.ArgumentParser(description='AX_BLUE_REPORT_V1 덱 빌드')
    ap.add_argument('inputs', nargs='*')
    ap.add_argument('-o', required=True)
    ap.add_argument('--list'); ap.add_argument('--gallery', action='store_true')
    ap.add_argument('--title'); ap.add_argument('--brand', default='brand/hct')
    ap.add_argument('--present', action='store_true'); ap.add_argument('--artifact', action='store_true')
    ap.add_argument('--full-font', action='store_true'); ap.add_argument('--no-video', action='store_true')
    ap.add_argument('--keep-numbers', action='store_true')
    ap.add_argument('--footer'); ap.add_argument('--keep-footer', action='store_true')
    build(ap.parse_args())

if __name__ == '__main__':
    main()
