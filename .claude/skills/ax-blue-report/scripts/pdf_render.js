#!/usr/bin/env node
// AX_BLUE_REPORT_V1 — 덱 HTML 을 인쇄용 PDF 한 벌로 찍는다(목차 · 링크 · 쪽 이름은 make_pdf.py 가 붙인다).
//   node scripts/pdf_render.js <deck.html> <out.pdf> <manifest.json> [--keep-order] [--no-appendix] [--font-css <css>]
// 기본: 본문 장 뒤에 그 장이 부르는 부록(지금 원문 보기 · data-now-source)을 「NN-k」 상세 쪽으로 끼워 넣는다.
//       두 화면 장([role=tab][data-v])은 화면마다 한 쪽씩 「NN②」.
// --keep-order   부록을 끼워 넣지 않고 덱 순서 그대로
// --no-appendix  본문에 끼워 넣지 않은 부록(간지 · Q&A 등)은 빼고 INDEX 의 「+ 부록」 줄도 숨긴다
const path = require('path'), fs = require('fs');

function loadPlaywright() {
  const tries = ['playwright', 'playwright-core'];
  for (const n of tries) { try { return require(n); } catch (e) {} }
  for (const n of tries) { try { return require(require.resolve(n, { paths: [process.cwd()] })); } catch (e) {} }
  try {
    const g = require('child_process').execSync('npm root -g', { encoding: 'utf8' }).trim();
    for (const n of tries) { try { return require(path.join(g, n)); } catch (e) {} }
  } catch (e) {}
  console.error('playwright 가 없다 — npm i -D playwright && npx playwright install chromium');
  process.exit(2);
}

const PLAN = ({ keepOrder, noAppendix }) => {
  const d = document, all = [...d.querySelectorAll('#deck > section.sl')];
  const div = d.getElementById('appendix');
  const cut = div ? all.indexOf(div) : all.findIndex(s => s.classList.contains('apx'));
  const head = cut < 0 ? all : all.slice(0, cut), tail = cut < 0 ? [] : all.slice(cut);
  const cover = head[0], body = head.slice(1), apx = all.filter(s => s.classList.contains('apx'));
  const two = n => String(n).padStart(2, '0'), CIRC = '①②③④⑤⑥⑦⑧⑨';
  const links = window.AXBR_LINKS || {};
  const target = v => { const r = links[v], id = r ? (Array.isArray(r) ? r[0] : r) : v; const e = d.getElementById(id); return e && e.classList.contains('sl') ? e : null; };
  const title = s => (s.getAttribute('data-t') || '').replace(/^(부록\s*)?\d+\s*(장\s*)?(·\s*)?/, '').trim();
  const short = s => title(s).split(' — ')[0].trim();
  const tabs = s => [...s.querySelectorAll('[role=tab][data-v]')].map(t => t.getAttribute('data-v'));
  const grp = s => s.getAttribute('data-grp') || '';
  const items = [], placed = new Set();
  const push = (s, o) => {
    const vs = tabs(s);
    if (vs.length < 2) items.push(Object.assign({ idx: all.indexOf(s), view: null, title: title(s), grp: grp(s) }, o));
    else vs.forEach((v, i) => items.push(Object.assign({ idx: all.indexOf(s), view: v, title: title(s) + (i ? ' (' + (i + 1) + '번째 화면)' : ''), grp: grp(s) }, o,
      i ? { label: o.label + CIRC[i], parent: o.label, kind: 'view' } : {})));
    placed.add(s);
  };
  if (cover) push(cover, { label: '표지', kind: 'cover' });
  body.forEach((s, k) => {
    const lab = two(k + 1);
    push(s, { label: lab, kind: s.classList.contains('v41-chapter') ? 'chapter' : 'body' });
    if (keepOrder) return;
    let n = 0;
    s.querySelectorAll('[data-now-source]').forEach(b => {
      const t = target(b.getAttribute('data-now-source'));
      if (!t || placed.has(t) || !tail.includes(t)) return;
      n++; push(t, { label: lab + '-' + n, kind: 'detail', parent: lab, parentTitle: short(s) });
    });
  });
  tail.forEach(s => {
    if (placed.has(s)) return;
    if (noAppendix && !keepOrder) return;
    const k = apx.indexOf(s);
    push(s, { label: s === div ? '부록' : k >= 0 ? '부록 ' + two(k + 1) : 'A' + two(tail.indexOf(s)), kind: s === div ? 'divider' : 'apx' });
  });
  // 섹션 → 쪽 이름(첫 화면 기준)
  const labelOf = new Map();
  items.forEach(it => { const s = all[it.idx]; if (!labelOf.has(s)) labelOf.set(s, it.label); });
  // 「부록 NN」 글자 → 해당 쪽 링크
  const apxLabel = {}; apx.forEach((s, i) => { if (labelOf.has(s)) apxLabel[two(i + 1)] = labelOf.get(s); });
  const SKIP = '.rf, .hd .code, script, style, [data-now-source], .pdf-ref, .pdf-back';
  [...labelOf.keys()].forEach(s => {
    const w = d.createTreeWalker(s, NodeFilter.SHOW_TEXT), hits = [];
    while (w.nextNode()) { const n = w.currentNode; if (/부록\s?\d{2}/.test(n.nodeValue) && !n.parentElement.closest(SKIP)) hits.push(n); }
    hits.forEach(n => {
      const f = d.createDocumentFragment(); let last = 0; const v = n.nodeValue;
      v.replace(/부록\s?(\d{2})(?!\s*\/)/g, (m, nn, at) => {
        if (!apxLabel[nn] || apxLabel[nn] === labelOf.get(s)) return m;
        f.appendChild(d.createTextNode(v.slice(last, at)));
        const a = d.createElement('span'); a.className = 'pdf-ref'; a.setAttribute('data-pdfto', apxLabel[nn]); a.textContent = m; f.appendChild(a);
        last = at + m.length; return m;
      });
      if (last) { f.appendChild(d.createTextNode(v.slice(last))); n.parentNode.replaceChild(f, n); }
    });
    s.querySelectorAll('[data-now-source]').forEach(b => { const t = target(b.getAttribute('data-now-source')); if (t && labelOf.has(t)) b.setAttribute('data-pdfto', labelOf.get(t)); });
  });
  // INDEX → 장 표지
  d.querySelectorAll('#deck .agenda > div').forEach(row => {
    const i = (row.querySelector('i') || {}).textContent || '';
    const t = /^\d+$/.test(i.trim()) ? d.querySelector('#deck > section.sl.v41-chapter[data-grp="g' + i.trim() + '"]') : div;
    if (t && labelOf.has(t)) row.setAttribute('data-pdfto', labelOf.get(t));
    else if (i.trim() === '+') row.style.visibility = 'hidden';
  });
  return { items, title: d.title, n: all.length };
};

const PREP = (it) => {
  const d = document, s = [...d.querySelectorAll('#deck > section.sl')][it.idx];
  d.querySelectorAll('.on[id$="-modal"], .on[id$="-modal-2"], #help.on').forEach(m => m.classList.remove('on'));
  s.scrollIntoView({ block: 'start' }); const deck = d.getElementById('deck'); if (deck) deck.scrollTop = s.offsetTop;
  s.classList.add('in');
  s.querySelectorAll('.fr').forEach(f => f.classList.add('on'));
  if (it.kind === 'detail' && !s.querySelector('.pdf-back')) {
    const chp = s.querySelector('.hd .chp'); if (chp) chp.textContent = it.label + ' · ' + it.parentTitle + ' 상세';
    const hd = s.querySelector('.hd'), lg = hd && hd.querySelector('.lg');
    if (hd) { const a = d.createElement('span'); a.className = 'pdf-back'; a.setAttribute('data-pdfto', it.parent); a.textContent = '↩ ' + it.parent + ' ' + it.parentTitle; hd.insertBefore(a, lg || null); }
  }
};

const SNAP = (it) => {
  const d = document, s = [...d.querySelectorAll('#deck > section.sl')][it.idx];
  const R = s.getBoundingClientRect();
  const links = [...s.querySelectorAll('[data-pdfto]')].map(e => {
    const r = e.getBoundingClientRect();
    return { x: r.left - R.left, y: r.top - R.top, w: r.width, h: r.height, to: e.getAttribute('data-pdfto') };
  }).filter(l => l.w > 0 && l.h > 0 && l.x < R.width && l.y < R.height);
  const c = s.cloneNode(true);
  const pg0 = s.querySelector('.rf .pg'), pg = c.querySelector('.rf .pg');
  if (pg0 && pg) {
    const cs = getComputedStyle(pg0);
    for (const p of cs) pg.style.setProperty(p, cs.getPropertyValue(p));
    pg.className = 'pgx'; pg.textContent = it.kind === 'cover' ? '' : it.label;
  }
  c.classList.add('in'); c.setAttribute('data-pdf-label', it.label);
  (window.__pdf = window.__pdf || []).push(c);
  return { links, w: R.width, h: R.height };
};

const ASSEMBLE = () => {
  const d = document, deck = d.getElementById('deck');
  [...d.querySelectorAll('#deck > section.sl')].forEach(s => s.remove());
  window.__pdf.forEach(c => deck.appendChild(c));
  const st = d.createElement('style');
  st.textContent = '@page{size:1920px 1080px;margin:0}' +
    'html,body{height:auto!important;overflow:visible!important;background:#fff!important}' +
    '#deck{position:static!important;height:auto!important;max-height:none!important;overflow:visible!important;scroll-snap-type:none!important;padding:0!important;gap:0!important}' +
    '#deck>section.sl{break-after:page;page-break-after:always;width:1920px!important;height:1080px!important;min-height:0!important;max-height:none!important;margin:0!important;overflow:hidden!important;box-shadow:none!important}' +
    '#hud,#jump,#scr,#laser,#nav,#prog,#notes,#help,#now-source-modal,[id$="-modal"],[id$="-modal-2"]{display:none!important}' +
    '*,*::before,*::after{animation-duration:1ms!important;animation-delay:0s!important;animation-iteration-count:1!important;transition:none!important}' +
    '.fr{opacity:1!important;transform:none!important;visibility:visible!important}' +
    '.f8-hint,.e8-hint{visibility:hidden!important}' +
    '.pdf-ref{text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:.18em}' +
    '.pdf-back{align-self:center;margin-right:1.2rem;font-size:.82rem;font-weight:700;letter-spacing:.01em;color:inherit;opacity:.85;white-space:nowrap}';
  d.head ? d.head.appendChild(st) : d.body.appendChild(st);
  return d.querySelectorAll('#deck > section.sl').length;
};

(async () => {
  const a = process.argv.slice(2), fcI = a.indexOf('--font-css'), [F, OUT, MAN] = a.filter((x, i) => !x.startsWith('--') && !(fcI >= 0 && i === fcI + 1));
  if (!F || !OUT || !MAN) { console.error('사용: node pdf_render.js <deck.html> <out.pdf> <manifest.json> [--keep-order] [--no-appendix]'); process.exit(1); }
  const pw = loadPlaywright();
  const b = await pw.chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, reducedMotion: 'reduce', deviceScaleFactor: 1 });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + path.resolve(F), { waitUntil: 'load', timeout: 180000 });
  await p.emulateMedia({ media: 'screen', reducedMotion: 'reduce' });
  await p.waitForTimeout(1200);
  await p.evaluate(() => { const b = document.body; b.classList.remove('present', 'notes', 'laser', 'fs', 'horiz'); b.classList.add('expand'); });
  const fi = a.indexOf('--font-css');
  if (fi >= 0) {
    const css = fs.readFileSync(a[fi + 1], 'utf8');
    const n = await p.evaluate((css) => {
      let n = 0;
      for (const sh of [...document.styleSheets]) {
        let rules; try { rules = sh.cssRules; } catch (e) { continue; }
        for (let i = rules.length - 1; i >= 0; i--) {
          const r = rules[i];
          if (r.type === CSSRule.FONT_FACE_RULE && /pretendard/i.test(r.style.getPropertyValue('font-family'))) { sh.deleteRule(i); n++; }
        }
      }
      const st = document.createElement('style'); st.id = 'pdf-static-fonts'; st.textContent = css; (document.head || document.body).appendChild(st);
      return n;
    }, css);
    await p.evaluate(async () => { await Promise.all([...document.fonts].filter(f => /pretendard/i.test(f.family)).map(f => f.load().catch(() => null))); await document.fonts.ready; });
    await p.waitForTimeout(400);
    if (!n) console.error('· 덱에서 Pretendard @font-face 를 못 찾았다 — 고정 굵기 폰트를 덧붙이기만 했다');
  }
  const plan = await p.evaluate(PLAN, { keepOrder: a.includes('--keep-order'), noAppendix: a.includes('--no-appendix') });
  const pages = [];
  for (const it of plan.items) {
    await p.evaluate(PREP, it);
    await p.waitForTimeout(900);
    if (it.view) {   // 단계 표시(.fr.on)가 끝난 뒤에 눌러야 화면 전환이 덮어써지지 않는다
      await p.evaluate(it => { const s = [...document.querySelectorAll('#deck > section.sl')][it.idx]; const t = s.querySelector('[role=tab][data-v="' + it.view + '"]'); if (t) t.click(); }, it);
      await p.waitForTimeout(700);
    }
    const snap = await p.evaluate(SNAP, it);
    pages.push(Object.assign({}, it, snap));
  }
  const n = await p.evaluate(ASSEMBLE);
  await p.waitForTimeout(600);
  await p.pdf({ path: OUT, width: '1920px', height: '1080px', printBackground: true, margin: { top: 0, right: 0, bottom: 0, left: 0 }, preferCSSPageSize: true });
  fs.writeFileSync(MAN, JSON.stringify({ title: plan.title, pages, errors: errs }, null, 1));
  console.log(JSON.stringify({ pages: n, errors: errs.slice(0, 10) }));
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
