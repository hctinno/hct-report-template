'use strict';
/**
 * HTML 덱에서 뽑은 manifest.json 을 PowerPoint 로 조립한다.
 * 직접 부르지 않는다 — scripts/deck_to_pptx.py 가 HTML 에서 장을 뽑은 뒤 부른다.
 *
 *   node from_deck.js <manifest.json> --brand <brand.json> --out <파일.pptx>
 *
 * 레이아웃 · 색 · 로고 · 테마는 template.js 와 같다. PowerPoint 에서 「새 슬라이드」로 장을 더해도
 * 같은 틀이 나온다. 1920x1080 격자가 HTML 과 같으므로 본문 그림은 HTML 에서 놓였던 자리에 그대로 놓는다.
 */
const fs = require('fs');
const path = require('path');
const PptxGenJS = require('pptxgenjs');
const { C, F } = require('./tokens');
const { loadBrand } = require('./brand');
const T = require('./template');

const { X, W, PAD, COVER, CW, FOOT_Y, LAYOUT, txt, badge } = T;
const BODY_TOP = 250;            // 이보다 위로 올라온 본문 그림은 제목과 겹치므로 맞춰 줄인다
const BODY_BOTTOM = FOOT_Y - 8;  // 꼬리말 바로 위까지. HTML 의 출처 줄은 그림 안에 들어 있다

function args() {
  const a = process.argv.slice(2);
  const get = (k) => { const i = a.indexOf(k); return i >= 0 ? a[i + 1] : null; };
  return { manifest: a[0], brand: get('--brand'), out: get('--out') };
}

/** HTML 글자 조각 → pptxgenjs 글자 조각. 강조(<em> · <b> …)는 굵게 + 색 */
function rich(runs, emColor) {
  const out = [];
  (runs || []).forEach((r) => {
    if (r.t === '\n') { if (out.length) out[out.length - 1].options.breakLine = true; return; }
    out.push({ text: r.t, options: r.em ? { bold: true, color: emColor } : {} });
  });
  return out.length ? out : [{ text: '', options: {} }];
}
const plain = (runs) => (runs || []).map((r) => r.t).join('').replace(/\s*\n\s*/g, ' ').trim();

function build(m, brand, out) {
  const pres = new PptxGenJS();
  pres.layout = 'LAYOUT_WIDE';
  pres.author = brand.company;
  pres.company = brand.company.replace(/&/g, '&amp;');
  pres.title = m.title || brand.docTitle || brand.company;
  pres.theme = { headFontFace: F.kr, bodyFontFace: F.kr };
  const style = m.style || 'a';
  const H = style === 'h';
  // 스타일 H — 표지 · 간지 · 마무리 글이 밝은 지면에 앉는다. 강조색도 HTML 과 같게(딥 블루)
  const EM = H ? C.deep : C.cobalt;
  T.defineLayouts(pres, brand, { style });
  const dir = path.dirname(path.resolve(out.manifest));

  let section = null;
  const sec = (t) => { if (t !== section) { pres.addSection({ title: t }); section = t; } };
  const add = (layout) => pres.addSlide({ masterName: layout, sectionTitle: section });
  sec('표지 · 목차');

  m.slides.forEach((s) => {
    let sl;
    if (s.kind === 'chapter') sec(s.apx ? '부록' : (plain(s.title) || '장'));
    if (s.apx && section !== '부록' && s.kind !== 'chapter') sec('부록');

    if (s.kind === 'cover') {
      sl = add(LAYOUT.cover);
      if (s.kicker) sl.addText(s.kicker, { placeholder: 'eyebrow' });
      sl.addText(rich(s.title, H ? C.deep : C.accentOnDark), { placeholder: 'title' });
      if (s.message && s.message.length) sl.addText(rich(s.message, H ? C.text : C.onDark), { placeholder: 'subtitle' });
      if (s.meta) sl.addText(s.meta, { placeholder: 'meta' });
    } else if (s.kind === 'agenda') {
      sl = add(LAYOUT.titleOnly);
      sl.addText('CONTENTS', { placeholder: 'eyebrow' });
      sl.addText(rich(s.title, EM), { placeholder: 'title' });
      const gap = Math.min(150, (BODY_BOTTOM - 284) / Math.max(1, s.items.length));
      s.items.forEach((it, i) => {
        const y = 284 + i * gap;
        badge(sl, PAD.side, y, 84, it.no || String(i + 1), it.apx ? C.text3 : C.cobalt);
        txt(sl, it.t, { x: X(PAD.side + 120), y: X(y + 2), w: X(1200), h: X(46), fontSize: 20, bold: true, color: C.text });
        if (it.d) txt(sl, it.d, { x: X(PAD.side + 120), y: X(y + 50), w: X(1400), h: X(36), fontSize: 14, color: C.text2 });
      });
    } else if (s.kind === 'chapter') {
      sl = add(LAYOUT.section);
      sl.addText(s.no || '', { placeholder: 'number' });
      sl.addText(rich(s.title, H ? C.deep : C.accentOnDark), { placeholder: 'title' });
      if (s.lede) sl.addText(s.lede, { placeholder: 'desc' });
      if (s.items && s.items.length && H) {
        // H — 오른쪽 열(패널 밖 밝은 지면)에 「이 장에서」
        txt(sl, [{ text: '이 장에서', options: { bold: true, color: C.text, breakLine: true } },
          ...s.items.map((it, i) => ({ text: `${it.no || String(i + 1).padStart(2, '0')}  ${it.t}`, options: { breakLine: i < s.items.length - 1 } }))],
        { x: X(1060), y: X(500), w: X(W - 1060 - PAD.side), h: X(Math.min(440, 60 + s.items.length * 42)), fontSize: 14, color: C.text2Hi, paraSpaceAfter: 4, fit: 'shrink' });
      } else if (s.items && s.items.length) {
        txt(sl, [{ text: '이 장에서', options: { bold: true, color: C.onDark, breakLine: true } },
          // 번호는 HTML 간지와 같게 — 덱 전체에서 몇째 장인지(04 · 05 …)
          ...s.items.map((it, i) => ({ text: `${it.no || String(i + 1).padStart(2, '0')}  ${it.t}`, options: { breakLine: i < s.items.length - 1 } }))],
        { x: X(COVER.side), y: X(680), w: X(1400), h: X(60 + s.items.length * 42), fontSize: 14, color: C.onCover2, paraSpaceAfter: 4 });
      }
    } else if (s.kind === 'closing') {
      sl = add(LAYOUT.closing);
      sl.addText([{ text: s.l1, options: { breakLine: true, bold: false, color: H ? C.cobalt : undefined } }, ...rich(s.l2, H ? C.deep : C.accentOnDark)], { placeholder: 'title' });
      const c = [s.ty, s.sig].filter(Boolean).join('  ·  ');
      if (c) sl.addText(c, { placeholder: 'contact' });
    } else {
      sl = add(LAYOUT.titleOnly);
      if (s.kind === 'content') {
        if (s.name) sl.addText(s.name, { placeholder: 'eyebrow' });
        sl.addText(rich(s.title, EM), { placeholder: 'title' });
        if (s.lede && s.lede.length) sl.addText(rich(s.lede, H ? C.text : C.navy), { placeholder: 'lede' });
      }
      if (s.image) placeImage(sl, s, dir);
    }
    if (s.notes) sl.addNotes(s.notes);
  });
  return pres;
}

/** 본문 그림을 HTML 에서 놓였던 자리에 그대로. 제목 칸을 침범하거나 꼬리말을 넘으면 본문 칸에 맞춰 줄인다 */
function placeImage(sl, s, dir) {
  const im = s.image;
  let { x, y, w, h } = im;
  const full = s.kind === 'image';
  const top = full ? 70 : BODY_TOP, bottom = BODY_BOTTOM;
  // 같은 1920x1080 격자라 대개는 HTML 자리 그대로 들어간다. 넘칠 때만 줄이되, 가로는 가운데 ·
  // 세로는 원래 자리를 최대한 지킨다 — 위로 끌어올리면 HTML 의 세로 가운데 배치(bl-mid)가 깨진다.
  if (y < top || y + h > bottom || x < PAD.side - 40 || x + w > W - PAD.side + 40) {
    const k = Math.min(1, (CW + 80) / w, (bottom - top) / h);
    const cy = y + h / 2;
    w *= k; h *= k;
    x = Math.max(PAD.side - 40, Math.min(x + (im.w - w) / 2, W - PAD.side + 40 - w));
    y = Math.max(top, Math.min(cy - h / 2, bottom - h));
  }
  sl.addImage({ path: path.join(dir, im.file), x: X(x), y: X(y), w: X(w), h: X(h),
    altText: full ? `${s.name || '본문'} — HTML 덱 장 그림` : `${plain(s.title)} — 본문 도식`, objectName: `body_${s.id || 'image'}` });
}

async function main() {
  const a = args();
  if (!a.manifest || !a.brand || !a.out) {
    console.error('사용법: node from_deck.js <manifest.json> --brand <brand.json> --out <파일.pptx>');
    process.exit(1);
  }
  const m = JSON.parse(fs.readFileSync(a.manifest, 'utf8'));
  const brand = loadBrand(a.brand);
  const pres = build(m, brand, a);
  fs.mkdirSync(path.dirname(path.resolve(a.out)), { recursive: true });
  await pres.writeFile({ fileName: a.out });
  await T.patchTheme(a.out);
  const kb = (fs.statSync(a.out).size / 1024).toFixed(0);
  console.log(`생성: ${a.out}  (${m.slides.length}장 · ${kb}KB)`);
}

main().catch((e) => { console.error('실패:', e.message); process.exit(1); });
