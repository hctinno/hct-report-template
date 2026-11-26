#!/usr/bin/env python3
"""라이브 HTML 덱을 PowerPoint 로 옮긴다 — 한 보고서를 HTML · PPTX 둘 다로.

    python3 scripts/deck_to_pptx.py decks-out/보고서.html --brand brand/hct/brand.json -o decks-out/보고서.pptx

build_deck.py 로 만든 덱(또는 같은 계통의 라이브 덱)을 받는다. 내용은 HTML 한 곳에만 있고,
PPTX 는 거기서 뽑는다 — 두 판을 따로 고치지 않는다.

장마다 이렇게 옮긴다.
  표지 · 목차 · 장 간지 · 마무리 · 부록 간지   PowerPoint 레이아웃(pptx/template.js)에 글자로 — 전부 편집 가능
  본문 장                                    제목 · 리드는 글자(편집 가능), 본문 도식은 고해상도 그림
  제목이 본문 칸 안에 섞인 장(보고 요지 등)    장 전체를 그림 한 장으로
  발표자 노트                                 PowerPoint 노트 창으로

머리띠 · 꼬리띠 · 쪽번호 · 로고 · 워터마크는 그림에서 빼고 PowerPoint 레이아웃이 다시 단다.
단계 전개(data-f)와 등장 애니메이션은 모두 펼친 마지막 모습으로 찍는다.

중간 산출물(장별 PNG · manifest.json)은 --keep 폴더에 남길 수 있다.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from ensure_deps import need_browser, need_node_modules  # noqa: E402

VIEW = {"width": 1920, "height": 1080}
SCALE = 2  # 그림 해상도 — 3840x2160 기준. 인쇄 · 확대에도 깨지지 않게

# 찍기 전에 덮는 스타일. 뷰어 조작판 · 진행선을 감추고, 단계 전개와 움직임을 끝 상태로 둔다.
FREEZE_CSS = """
#bl-prog, .bl-hud, #bl-jump { display:none !important; }
[data-f] { opacity:1 !important; visibility:visible !important; transform:none !important; }
*, *::before, *::after { animation-duration:0s !important; animation-delay:0s !important;
                         transition:none !important; caret-color:transparent !important; }
"""

# 장 하나의 정보를 뽑는다. 글자는 runs([{t, em}])로 — <em> · <b> · <strong> · <mark> 는 강조, <br> 은 줄바꿈.
EXTRACT_JS = r"""
(k) => {
  const s = document.querySelectorAll('.bl-sl')[k];
  const bd = s.querySelector(':scope > .bl-bd');
  const runs = (el) => {
    if (!el) return [];
    const out = [];
    const walk = (n, em) => {
      for (const c of n.childNodes) {
        if (c.nodeType === 3) { const t = c.textContent.replace(/\s+/g, ' '); if (t.trim() || t === ' ') out.push({t, em}); }
        else if (c.nodeType === 1) {
          const tag = c.tagName.toLowerCase();
          if (tag === 'br') { out.push({t: '\n', em}); continue; }
          if (tag === 'button' || c.classList.contains('bl-ev') || getComputedStyle(c).display === 'none') continue;
          // 꼬리표(「(안)」 · 「요청」)는 CSS 여백으로 떨어져 있다 — 글자로 옮길 때 띄어 쓴다
          if (c.classList.contains('bl-tag') && out.length && !/\s$/.test(out[out.length - 1].t)) out.push({t: ' ', em});
          walk(c, em || ['em', 'b', 'strong', 'mark'].includes(tag));
        }
      }
    };
    walk(el, false);
    // 앞뒤 공백 정리
    while (out.length && !out[0].t.trim()) out.shift();
    while (out.length && !out[out.length - 1].t.trim()) out.pop();
    if (out.length) { out[0].t = out[0].t.replace(/^\s+/, ''); out[out.length - 1].t = out[out.length - 1].t.replace(/\s+$/, ''); }
    return out;
  };
  const text = (el) => runs(el).map(r => r.t).join('').trim();
  // 자식 조각을 떼어 낸다 — <b>2026-09</b>운영지원팀 처럼 붙어 있는 머리띠 · 서명 칸
  const parts = (el) => el ? [...el.childNodes].map(n => n.textContent.replace(/\s+/g, ' ').trim()).filter(Boolean) : [];
  const q = (sel) => s.querySelector(sel);
  const hd = q('.bl-hd .bl-code');
  const base = { notes: s.dataset.notes || '', name: parts(hd).join('  '), id: s.id || '',
                 dark: s.classList.contains('bl-sl--dark'), apx: s.hasAttribute('data-apx') };
  if (s.classList.contains('bl-sl--cover')) {
    return Object.assign(base, { kind: 'cover', title: runs(q('.bl-bd .bl-title')),
      message: runs(q('.bl-cover-one')), kicker: parts(q('.bl-cover-k')).join(' · '),
      // 서명(부서 · 발표자) + 머리띠 첫 조각(보고 시점). 머리띠 나머지는 서명과 겹치는 부서명이라 뺀다
      meta: [...parts(q('.bl-sig')), ...parts(hd).slice(0, 1)].join('  ·  ') });
  }
  if (s.classList.contains('bl-sl--chapter')) {
    const items = [...s.querySelectorAll('.bl-chapter-toc > li')].map(li => ({ no: text(li.querySelector('b')), t: text(li.querySelector('h3')) }));
    return Object.assign(base, { kind: 'chapter', no: text(q('.bl-chapter-no')), title: runs(q('.bl-chapter-main .bl-title')),
      lede: text(q('.bl-chapter-main .bl-lede')), items });
  }
  if (s.classList.contains('bl-sl--apxdiv')) {
    return Object.assign(base, { kind: 'chapter', no: text(q('.bl-apxdiv > b')) || '+', title: runs(q('.bl-title')),
      lede: text(q('.bl-lede')), items: [] });
  }
  if (q('.bl-fin')) {
    return Object.assign(base, { kind: 'closing', l1: text(q('.bl-fin-l1')), l2: runs(q('.bl-fin-l2')),
      ty: text(q('.bl-fin-ty')), sig: text(q('.bl-fin-sig')) });
  }
  if (q('.bl-agenda')) {
    const items = [...s.querySelectorAll('.bl-agenda > li')].map(li => ({
      no: text(li.querySelector('b')), t: text(li.querySelector('h3')), d: text(li.querySelector('span')),
      apx: li.classList.contains('is-apx') }));
    return Object.assign(base, { kind: 'agenda', title: runs(q('.bl-bd .bl-title')), items });
  }
  const t = bd && bd.querySelector(':scope > .bl-title');
  const l = bd && bd.querySelector(':scope > .bl-lede');
  return Object.assign(base, { kind: t ? 'content' : 'image', title: runs(t), lede: runs(l) });
}
"""

# 본문 그림의 범위. 제목 · 리드(본문 칸의 직계 자식)를 감추고 남은 자식들의 합집합.
# 'image' 장은 본문 칸 전체. 머리띠 · 꼬리띠 · 워터마크는 그림에서 뺀다.
CLIP_JS = r"""
([k, kind]) => {
  const s = document.querySelectorAll('.bl-sl')[k];
  const bd = s.querySelector(':scope > .bl-bd');
  const hide = [...s.querySelectorAll(':scope > .bl-hd, :scope > .bl-rf, :scope > .br-watermark')];
  if (kind === 'content') hide.push(...bd.querySelectorAll(':scope > .bl-title, :scope > .bl-lede'));
  hide.forEach(el => { el.dataset.pptxHid = el.style.visibility || '-'; el.style.visibility = 'hidden'; });
  let r;
  if (kind === 'content') {
    const kids = [...bd.children].filter(c => !c.classList.contains('bl-title') && !c.classList.contains('bl-lede')
                                           && getComputedStyle(c).display !== 'none');
    if (!kids.length) return null;
    const rs = kids.map(c => c.getBoundingClientRect()).filter(b => b.width > 2 && b.height > 2);
    if (!rs.length) return null;
    r = { x: Math.min(...rs.map(b => b.left)), y: Math.min(...rs.map(b => b.top)),
          r: Math.max(...rs.map(b => b.right)), b: Math.max(...rs.map(b => b.bottom)) };
  } else {
    const b = bd.getBoundingClientRect();
    r = { x: b.left, y: b.top, r: b.right, b: b.bottom };
  }
  const pad = 12, W = innerWidth, H = innerHeight;
  const x = Math.max(0, Math.floor(r.x - pad)), y = Math.max(0, Math.floor(r.y - pad));
  return { x, y, width: Math.min(W, Math.ceil(r.r + pad)) - x, height: Math.min(H, Math.ceil(r.b + pad)) - y };
}
"""

RESTORE_JS = r"""
(k) => { document.querySelectorAll('.bl-sl')[k].querySelectorAll('[data-pptx-hid]').forEach(el => {
  el.style.visibility = el.dataset.pptxHid === '-' ? '' : el.dataset.pptxHid; delete el.dataset.pptxHid; }); }
"""


def extract(html, work):
    from playwright.sync_api import sync_playwright
    chrome = need_browser()
    slides = []
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=chrome)
        pg = br.new_page(viewport=VIEW, device_scale_factor=SCALE, reduced_motion="reduce")
        pg.goto("file://" + os.path.abspath(html))
        pg.wait_for_timeout(1200)
        if not pg.evaluate("() => !!(window.blDeck && blDeck.slides && blDeck.slides.length)"):
            sys.exit("라이브 덱 엔진(blDeck)이 없다 — build_deck.py 나 apply_brand.py 로 만든 라이브 덱을 준다")
        pg.add_style_tag(content=FREEZE_CSS)
        title = pg.evaluate("() => (document.querySelector('.bl-rf-name')||{}).textContent || document.title")
        n = pg.evaluate("() => document.querySelectorAll('.bl-sl').length")
        for k in range(n):
            pg.evaluate("(k) => blDeck.go(k)", k)
            pg.wait_for_timeout(250)
            info = pg.evaluate(EXTRACT_JS, k)
            if info["kind"] in ("content", "image"):
                clip = pg.evaluate(CLIP_JS, [k, info["kind"]])
                if clip and clip["width"] > 4 and clip["height"] > 4:
                    name = f"{k + 1:02d}{'-' + info['id'] if info['id'] else ''}.png"
                    pg.screenshot(path=os.path.join(work, name), clip=clip)
                    info["image"] = {"file": name, "x": clip["x"], "y": clip["y"],
                                     "w": clip["width"], "h": clip["height"]}
                pg.evaluate(RESTORE_JS, k)
            slides.append(info)
        br.close()
    return {"title": (title or "").strip(), "view": VIEW, "slides": slides}


def main():
    ap = argparse.ArgumentParser(description="라이브 HTML 덱 → PowerPoint")
    ap.add_argument("html", help="build_deck.py 로 만든 라이브 덱 HTML")
    ap.add_argument("--brand", required=True, help="brand.json")
    ap.add_argument("-o", "--out", required=True, help="출력 .pptx")
    ap.add_argument("--keep", help="장별 PNG · manifest.json 을 남길 폴더")
    a = ap.parse_args()

    need_node_modules()
    work = a.keep or tempfile.mkdtemp(prefix="deck2pptx-")
    os.makedirs(work, exist_ok=True)
    manifest = extract(a.html, work)
    mpath = os.path.join(work, "manifest.json")
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    kinds = {}
    for s in manifest["slides"]:
        kinds[s["kind"]] = kinds.get(s["kind"], 0) + 1
    print(f"추출: {len(manifest['slides'])}장 — " + " · ".join(f"{k} {v}" for k, v in kinds.items()))

    r = subprocess.run(["node", os.path.join(SKILL, "pptx", "from_deck.js"), mpath,
                        "--brand", a.brand, "--out", os.path.abspath(a.out)])
    if r.returncode != 0:
        sys.exit("PPTX 조립 실패")
    if not a.keep:
        for fn in os.listdir(work):
            os.remove(os.path.join(work, fn))
        os.rmdir(work)


if __name__ == "__main__":
    main()
