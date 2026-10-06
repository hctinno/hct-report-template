#!/usr/bin/env node
// AX_BLUE_REPORT_V1 실행 점검 — check_ax.py 가 부른다. 결과는 JSON 한 줄.
//   node scripts/check_runtime.js <deck.html> [--mobile]
// 1920×1080 에서 장마다: 머리띠 · 로고 · 바닥줄 · 워터마크 · 넘침, 단계(.fr[data-f]) 수, 대본 [클릭] 수
// 조작: → 키로 전부 넘기기 · 근거 핀 · 지금 원문 보기 · 영상 · 발표 모드(F) — 페이지 오류 · 팝업 수
// --mobile: 420px 폭에서 가로 스크롤 여부
const path = require('path');
function loadPlaywright() {
  for (const n of ['playwright', 'playwright-core']) { try { return require(n); } catch (e) {} }
  for (const n of ['playwright', 'playwright-core']) { try { return require(require.resolve(n, { paths: [process.cwd()] })); } catch (e) {} }
  try { const g = require('child_process').execSync('npm root -g', { encoding: 'utf8' }).trim(); return require(path.join(g, 'playwright')); } catch (e) {}
  console.log(JSON.stringify({ fatal: 'playwright 가 없다 — npm i -D playwright && npx playwright install chromium' })); process.exit(2);
}
(async () => {
  const a = process.argv.slice(2), F = a.find(x => !x.startsWith('--'));
  const pw = loadPlaywright(), b = await pw.chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1920, height: 1080 }, reducedMotion: 'reduce' });
  const p = await ctx.newPage(); const errs = [], R0 = []; let pops = 0;
  p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
  ctx.on('page', pg => { pops++; R0.push(pg.url()); });
  await p.goto('file://' + path.resolve(F), { waitUntil: 'load', timeout: 180000 }); await p.waitForTimeout(1500);
  const R = {};
  R.startPresent = await p.evaluate(() => document.body.classList.contains('present'));
  R.slides = await p.evaluate(() => [...document.querySelectorAll('#deck > section.sl')].map((s, i) => {
    const q = x => s.querySelector(x), cs = (e, ps) => e ? getComputedStyle(e, ps) : null;
    const lg = q('.hd .lg'), wm = cs(s, '::after'), wrap = q('.wrap') || s;
    const steps = new Set([...s.querySelectorAll('.fr[data-f]')].map(f => f.dataset.f)).size;
    const notes = s.getAttribute('data-notes') || '';
    const over = [];
    if (wrap.scrollHeight > wrap.clientHeight + 4) over.push('세로 ' + (wrap.scrollHeight - wrap.clientHeight) + 'px');
    // 글자가 바닥줄을 덮거나 장 밖으로 나가는지(일부러 잘라 둔 상자 안 글자는 뺀다)
    const R = s.getBoundingClientRect(), rf = q('.rf'), lim = rf ? rf.getBoundingClientRect().top : R.bottom;
    const w = document.createTreeWalker(s, NodeFilter.SHOW_TEXT), rg = document.createRange();
    const clipped = (el, r) => { for (let e = el; e && e !== s; e = e.parentElement) { const c = getComputedStyle(e); if (c.overflow !== 'visible' || c.overflowY !== 'visible') { const b = e.getBoundingClientRect(); if (r.bottom > b.bottom + 1 || r.right > b.right + 1) return true; } } return false; };
    let worst = null;
    while (w.nextNode()) {
      const n = w.currentNode, el = n.parentElement;
      if (!n.nodeValue.trim() || !el || el.closest('.rf, script, style, [aria-hidden="true"]')) continue;
      const c = getComputedStyle(el); if (c.visibility === 'hidden' || c.position === 'fixed') continue;
      rg.selectNodeContents(n);
      for (const r of rg.getClientRects()) {
        if (!r.width || !r.height) continue;
        const d = Math.max(r.bottom - lim, r.right - R.right, R.left - r.left);
        if (d > 3 && !clipped(el, r) && (!worst || d > worst.d)) worst = { d: Math.round(d), x: n.nodeValue.trim().slice(0, 24) };
      }
    }
    if (worst) over.push('글자 넘침 ' + worst.d + 'px 「' + worst.x + '」');
    return { i, id: s.id, t: s.getAttribute('data-t') || '', apx: s.classList.contains('apx'), dark: s.classList.contains('dark'),
      header: !!q('.hd'), logo: !!(lg && cs(lg).backgroundImage !== 'none'), footer: !!q('.rf'),
      watermark: !!(wm && wm.backgroundImage && wm.backgroundImage !== 'none' && wm.content !== 'none'),
      steps, clicks: (notes.match(/\[클릭\]/g) || []).length, notes: notes.trim().length, over };
  }));
  // 조작
  const n = R.slides.length;
  await p.evaluate(() => { document.body.classList.remove('expand'); });
  for (let i = 0; i < n + 5; i++) { await p.keyboard.press('ArrowRight'); await p.waitForTimeout(40); }
  await p.keyboard.press('Home'); await p.waitForTimeout(200);
  R.ops = {};
  const esc = async () => { await p.keyboard.press('Escape'); await p.waitForTimeout(250); };
  R.ops.evidence = await p.evaluate(() => { const b = document.querySelector('.ev-pin'); if (!b) return null; b.scrollIntoView(); b.click(); const m = document.getElementById('evm'); return !!(m && m.classList.contains('on')); }); await esc();
  R.ops.nowSource = await p.evaluate(() => { const b = document.querySelector('[data-now-source]'); if (!b) return null; b.click(); const m = document.getElementById('now-source-modal'); return !!(m && m.classList.contains('on')); }); await esc();
  R.ops.video = await p.evaluate(() => { const b = document.querySelector('.bma-video-open'); if (!b) return null; b.click(); const m = document.getElementById('bma-video-modal'); return !!(m && m.classList.contains('on')); }); await esc();
  R.ops.closed = await p.evaluate(() => [...document.querySelectorAll('#evm, #now-source-modal, #bma-video-modal')].every(m => !m.classList.contains('on')));
  await p.keyboard.press('f'); await p.waitForTimeout(300);
  R.ops.present = await p.evaluate(() => document.body.classList.contains('present'));
  await p.keyboard.press('f');
  if (a.includes('--mobile')) {
    const m = await b.newPage({ viewport: { width: 420, height: 900 } });
    m.on('pageerror', e => errs.push('mobile: ' + e.message));
    await m.goto('file://' + path.resolve(F), { waitUntil: 'load', timeout: 180000 }); await m.waitForTimeout(1200);
    R.mobile = await m.evaluate(() => ({ sw: document.documentElement.scrollWidth, w: innerWidth }));
  }
  R.errors = errs.slice(0, 30); R.popups = pops; R.popupUrls = R0.slice(0, 5);
  console.log(JSON.stringify(R));
  await b.close();
})().catch(e => { console.log(JSON.stringify({ fatal: String(e) })); process.exit(1); });
