#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AX_BLUE_REPORT_V1 점검 — 빌드한 덱 HTML 을 검사한다. 실패가 있으면 종료 코드 1.

  python3 scripts/check_ax.py decks-out/deck.html [--no-runtime] [--mobile] [--json 결과.json]

정적 검사(브라우저 불필요)
  · 글자 깨짐(저장소 검사와 같은 깨짐 글자 5종 · 물음표 셋 · U+FFFD)   실패
  · 장 제목(data-t) 형식과 번호 — 본문 「NN 제목」 · 장 표지 「NN 장 제목」 · 부록 「부록 NN · 제목」   실패
  · 대본 [클릭] 수 = 화면 단계(.fr[data-f]) 수            실패
  · 대본 없음 · 화면 글자 구어체 종결(~합니다 · ~한다)       주의
  · 「부록 NN」 글자가 없는 부록을 가리킴                     주의
  · 풀리지 않은 자산 토큰(axbr-media: · axbr-brand: · axbr-font:)  실패
실행 검사(node + playwright)
  · 페이지 오류 · 콘솔 오류                                 실패
  · 장마다 머리띠 · 로고 · 바닥줄 · 워터마크                 실패(표지 · 간지 제외 항목은 주의)
  · 1920×1080 세로 넘침                                    실패
  · 근거 핀 · 지금 원문 보기 · 영상 · 발표 모드(F)            실패
  · --mobile: 420px 폭 가로 스크롤                          실패
"""
import argparse, html as H, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
# 인코딩이 깨졌을 때 나오는 대표 글자. 이 파일 자신이 저장소 검사에 걸리지 않게 코드포인트로 적는다.
MOJI = ['\u6fe1', '\u6e72', '\u907a', '\u5a9b', '\u674e', '?' * 3, '\ufffd']

def sections(t):
    sys.path.insert(0, HERE)
    from build_deck import top_sections
    return top_sections(t)

def attr(sec, name):
    m = re.search(r'\s%s="([^"]*)"' % name, sec[:sec.index('>') + 1] if '>' in sec else sec)
    return H.unescape(m.group(1)) if m else None

def step_values(sec):
    """엔진과 같은 규칙 — .fr[data-f] 의 서로 다른 data-f 값"""
    out = set()
    for tag in re.findall(r'<[a-zA-Z][^>]*>', re.sub(r'<(script|style)\b.*?</\1>', ' ', sec, flags=re.S | re.I)):
        c = re.search(r'\sclass="([^"]*)"', tag); f = re.search(r'\sdata-f="([^"]*)"', tag)
        if c and f and 'fr' in c.group(1).split(): out.add(f.group(1))
    return out

def visible_text(sec):
    s = re.sub(r'<(script|style)\b.*?</\1>', ' ', sec, flags=re.S | re.I)
    s = re.sub(r'\sdata-notes="[^"]*"', '', s)
    return [H.unescape(x).strip() for x in re.split(r'<[^>]+>', s) if x.strip()]

def is_present_build(t):
    return bool(re.search(r"window\.AXBR_MODE\s*=\s*'present'", t))

def static_checks(t):
    fail, warn = [], []
    present = is_present_build(t)
    for m in MOJI:
        if m in re.sub(r'data:[^"\')\s]+', '', t):
            fail.append('글자 깨짐 의심 「%s」' % m)
    left = sorted(set(re.findall(r'axbr-(?:media|brand|font):[\w./-]+', re.sub(r'data:[^"\')\s]+', '', t))))
    if left: fail.append('풀리지 않은 자산 토큰 %s' % left[:5])
    secs = sections(t)
    div = next((i for i, s in enumerate(secs) if attr(s, 'id') == 'appendix'), None)
    body_i = 0
    apx_have = {'%02d' % (k + 1) for k in range(sum(1 for s in secs if 'apx' in (attr(s, 'class') or '').split()))}
    ids = {attr(s, 'id') for s in secs}
    allid = [attr(s, 'id') for s in secs]
    for d in sorted({x for x in allid if x and allid.count(x) > 1}):
        warn.append('장 id 「%s」 가 %d번 — 모양은 같게 나오지만 장 안의 JS 동작은 첫 장에만 붙는다' % (d, allid.count(d)))
    for v in sorted(set(re.findall(r'\sdata-now-source="([^"]*)"', t))):
        if v not in ids: (warn if re.search(r'AXBR_LINKS\s*=', t) else fail).append('지금 원문 보기 대상 장 「%s」 이 덱에 없다 — 버튼을 지우거나 그 장을 넣는다' % v)
    rows = []
    for i, s in enumerate(secs):
        cls = (attr(s, 'class') or '').split(); dt = attr(s, 'data-t') or ''; sid = attr(s, 'id') or '(id 없음)'
        notes = attr(s, 'data-notes') or ''
        steps = len(step_values(s))
        clicks = notes.count('[클릭]')
        tag = '%02d %s' % (i, sid)
        if i == 0: pass
        elif div is not None and i == div:
            if dt != '부록': warn.append('%s 간지 data-t 는 「부록」 권장 (지금 「%s」)' % (tag, dt))
        elif 'apx' in cls:
            k = sum(1 for x in secs[:i + 1] if 'apx' in (attr(x, 'class') or '').split())
            if not re.match(r'^부록 %02d · \S' % k, dt): fail.append('%s data-t 형식 「부록 %02d · 제목」 아님: 「%s」' % (tag, k, dt))
        elif div is not None and i > div:
            warn.append('%s 부록 간지 뒤의 본문 장 — 쪽 번호가 붙지 않는다(간지 앞으로 옮기거나 class 에 apx 추가)' % tag)
        elif div is None or i < div:
            body_i += 1
            pat = r'^%02d 장 \S' % body_i if 'v41-chapter' in cls else r'^%02d \S' % body_i
            if not re.match(pat, dt): fail.append('%s data-t 형식 「%s」 아님: 「%s」' % (tag, '%02d 장 제목' % body_i if 'v41-chapter' in cls else '%02d 제목' % body_i, dt))
        if not present:   # 발표 전용 판은 대본을 일부러 뺐다
            if clicks != steps: fail.append('%s 대본 [클릭] %d개 · 화면 단계 %d개' % (tag, clicks, steps))
            if not notes.strip(): warn.append('%s 대본 없음' % tag)
        for x in visible_text(s):
            if re.search(r'(습니다|합니다|한다|된다)[.!]?$', x) and len(x) > 8:
                warn.append('%s 화면 글자 구어체 종결: 「%s」' % (tag, x[-40:])); break
        for nn in re.findall(r'부록\s?(\d{2})(?!\s*/)', ' '.join(visible_text(s))):
            if nn not in apx_have: warn.append('%s 「부록 %s」 을 가리키는데 그 부록 장이 없다' % (tag, nn))
        rows.append({'i': i, 'id': sid, 't': dt, 'steps': steps, 'clicks': clicks})
    return fail, warn, rows

def runtime_checks(path, mobile, present=False):
    fail, warn = [], []
    cmd = ['node', os.path.join(HERE, 'check_runtime.js'), path] + (['--mobile'] if mobile else [])
    r = subprocess.run(cmd, capture_output=True, text=True)
    try: R = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception: return ['실행 검사 실패: ' + (r.stderr or r.stdout)[-400:]], [], None
    if R.get('fatal'): return ['실행 검사 실패: ' + R['fatal']], [], R
    for e in R.get('errors', []): fail.append('페이지 오류: ' + e[:160])
    for s in R['slides']:
        tag = '%02d %s' % (s['i'], s['id'])
        special = s['i'] == 0 or s['id'] == 'appendix'
        for k, name in (('header', '머리띠(.hd)'), ('logo', '로고'), ('footer', '바닥줄(.rf)'), ('watermark', '워터마크')):
            if not s[k]: (warn if special else fail).append('%s %s 없음' % (tag, name))
        for o in s['over']: fail.append('%s 1920×1080 넘침 %s' % (tag, o))
    ops = R.get('ops', {})
    for k, name in (('evidence', '근거 핀 → 근거 창'), ('nowSource', '지금 원문 보기 → 겹창'), ('video', '영상 버튼 → 영상 창')):
        if ops.get(k) is False: fail.append('%s 동작 안 함' % name)
    if present:
        if not R.get('startPresent'): fail.append('발표 전용 판인데 처음부터 발표 모드가 아니다')
    elif ops.get('present') is False: fail.append('F → 발표 모드 동작 안 함')
    if ops.get('closed') is False: fail.append('Esc 로 창이 닫히지 않음')
    if mobile and R.get('mobile') and R['mobile']['sw'] > R['mobile']['w'] + 1:
        fail.append('420px 폭 가로 스크롤 %dpx' % (R['mobile']['sw'] - R['mobile']['w']))
    return fail, warn, R

def main():
    ap = argparse.ArgumentParser(description='AX_BLUE_REPORT_V1 점검')
    ap.add_argument('deck'); ap.add_argument('--no-runtime', action='store_true'); ap.add_argument('--mobile', action='store_true')
    ap.add_argument('--json')
    a = ap.parse_args()
    t = open(a.deck, encoding='utf-8').read()
    fail, warn, rows = static_checks(t)
    R = None
    if not a.no_runtime:
        f2, w2, R = runtime_checks(a.deck, a.mobile, is_present_build(t)); fail += f2; warn += w2
    for w in warn[:60]: print('주의', w)
    for f in fail[:80]: print('실패', f)
    n = len(rows)
    print('결과: 장 %d · 실패 %d · 주의 %d%s%s' % (n, len(fail), len(warn), '' if a.no_runtime else ' · 실행 검사 포함', ' · 발표 전용 판' if is_present_build(t) else ''))
    if a.json: json.dump({'fail': fail, 'warn': warn, 'slides': rows, 'runtime': R}, open(a.json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    sys.exit(1 if fail else 0)

if __name__ == '__main__':
    main()
