#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AX_BLUE_REPORT_V1 대본 내보내기 — 장마다 data-notes 를 모아 읽기 좋은 대본 파일로 낸다.

  python3 scripts/export_script.py decks-out/deck.html -o decks-out/deck-script.txt [--md]
  python3 scripts/export_script.py slides/*.html -o script.txt

  · 입력: 빌드한 덱 HTML 하나 또는 장 파일 여러 개(.sections.html 포함)
  · 장 제목(data-t) · 클릭 수 · 대본. --md 면 마크다운 제목(##)으로 낸다.
"""
import argparse, html as H, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_deck import top_sections  # noqa: E402

def head_attr(sec, name):
    tag = sec[:sec.index('>') + 1]
    m = re.search(r'\s%s="([^"]*)"' % name, tag)
    return H.unescape(m.group(1)) if m else ''

def main():
    ap = argparse.ArgumentParser(description='AX_BLUE_REPORT_V1 대본 내보내기')
    ap.add_argument('inputs', nargs='+'); ap.add_argument('-o', required=True); ap.add_argument('--md', action='store_true')
    ap.add_argument('--title')
    a = ap.parse_args()
    secs, title = [], a.title
    for f in a.inputs:
        t = open(f, encoding='utf-8').read()
        if not title:
            m = re.search(r'<title>(.*?)</title>', t, re.S)
            if m: title = H.unescape(m.group(1).strip())
        secs += top_sections(t)
    title = title or 'AX_BLUE_REPORT_V1'
    out = [('# %s · 발표 대본' if a.md else '%s · 발표 대본') % title, '', '총 %d장 · [클릭] = 다음 단계로 넘기는 시점' % len(secs), '']
    for s in secs:
        dt = head_attr(s, 'data-t') or head_attr(s, 'id'); notes = head_attr(s, 'data-notes').strip()
        k = notes.count('[클릭]')
        out.append(('## %s' if a.md else '■ %s') % dt + ('  (클릭 %d)' % k if k else ''))
        out.append('')
        out.append(notes or '(대본 없음)')
        out.append('')
    os.makedirs(os.path.dirname(os.path.abspath(a.o)) or '.', exist_ok=True)
    open(a.o, 'w', encoding='utf-8').write('\n'.join(out).rstrip() + '\n')
    print('대본 %s — %d장 · 대본 있는 장 %d' % (a.o, len(secs), sum(1 for s in secs if head_attr(s, 'data-notes').strip())))

if __name__ == '__main__':
    main()
