#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AX_BLUE_REPORT_V1 새 덱 뼈대 — 견본 장(slides/)을 골라 작업 폴더로 복사한다.

  python3 scripts/new_deck.py decks-out/q3-plan/src --pick cover index exec-summary chapter-1 market-cards ... closing
  python3 scripts/new_deck.py decks-out/q3-plan/src --pick 00 01 02 03 04 36 37 38       # 파일 번호로 골라도 된다
  python3 scripts/new_deck.py decks-out/q3-plan/src --all                               # 56장 전부(견본 덱 그대로)
  python3 scripts/new_deck.py --catalog                                                  # 고를 수 있는 장 목록

  · 고른 순서대로 01-… 02-… 로 번호를 붙여 복사하고, 같은 폴더에 list.txt(빌드 순서)를 쓴다.
  · --blank-notes  견본 대본을 비운다(새 대본을 처음부터 쓸 때)
  · 장의 모양은 section id 에 매여 있다(#deck #<id> …). id 를 바꾸지 않는다.
    같은 장을 두 번 고르면 id 가 겹친다 — 모양은 같게 나오지만 장 안의 JS 동작은 첫 장에만 붙는다.
  다음 단계: 글자를 바꾸고 → build_deck.py --list <폴더>/list.txt → check_ax.py
"""
import argparse, glob, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
SLIDES = os.path.join(SKILL, 'slides')

def catalog():
    out = []
    for f in sorted(glob.glob(os.path.join(SLIDES, '*.html'))):
        t = open(f, encoding='utf-8').read(4000)
        tag = re.match(r'<section\b[^>]*>', t).group(0)
        sid = re.search(r'\sid="([^"]*)"', tag).group(1)
        dt = re.search(r'\sdata-t="([^"]*)"', tag)
        out.append((os.path.basename(f), sid, dt.group(1) if dt else ''))
    return out

def main():
    ap = argparse.ArgumentParser(description='AX_BLUE_REPORT_V1 새 덱 뼈대')
    ap.add_argument('dest', nargs='?'); ap.add_argument('--pick', nargs='+'); ap.add_argument('--all', action='store_true')
    ap.add_argument('--blank-notes', action='store_true'); ap.add_argument('--catalog', action='store_true')
    a = ap.parse_args()
    cat = catalog()
    if a.catalog or not a.dest:
        for f, sid, dt in cat: print('%-32s %-22s %s' % (f, sid, dt))
        return
    if not a.pick and not a.all: sys.exit('--pick 또는 --all 을 준다 (--catalog 로 목록 확인)')
    picks = [c[0][:2] for c in cat] if a.all else a.pick
    os.makedirs(a.dest, exist_ok=True)
    if any(x.endswith('.html') for x in os.listdir(a.dest)): sys.exit('대상 폴더에 이미 장 파일이 있다 — 덮어쓰지 않는다: ' + a.dest)
    seen, names = {}, []
    for k, p in enumerate(picks, 1):
        hit = [c for c in cat if c[1] == p or c[0][:2] == p.zfill(2) or c[0][:-5] == p]
        if not hit: sys.exit('없는 장: %s (--catalog 로 확인)' % p)
        f, sid, _ = hit[0]
        t = open(os.path.join(SLIDES, f), encoding='utf-8').read()
        seen[sid] = seen.get(sid, 0) + 1
        if seen[sid] > 1:
            print('· %s 를 두 번 골랐다 — 모양(CSS)은 id 에 매여 있어 id 를 그대로 둔다. 장 안의 JS 동작(탭 · 고르기 · 원문 보기 대상)은 첫 장에만 붙는다' % sid, file=sys.stderr)
        if a.blank_notes: t = re.sub(r'(<section\b[^>]*\sdata-notes=")[^"]*"', r'\1"', t, count=1)
        name = '%02d-%s' % (k, f[3:])
        open(os.path.join(a.dest, name), 'w', encoding='utf-8').write(t)
        names.append(name)
    open(os.path.join(a.dest, 'list.txt'), 'w', encoding='utf-8').write('# 빌드 순서 — 위에서 아래로\n' + '\n'.join(names) + '\n')
    print('장 %d개 → %s (list.txt 포함)' % (len(names), a.dest))

if __name__ == '__main__':
    main()
