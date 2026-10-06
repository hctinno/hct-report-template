#!/usr/bin/env node
// AX_BLUE_REPORT_V1 장별 PNG — 넘침 · 여백을 눈으로 확인할 때.
//   node scripts/shots.js <deck.html> <폴더> [--motion] [--sheet] [장 id ...]
// 1920×1080 · 펼침(검토) 모드 · 움직임 줄임. --motion 은 등장 효과까지 기다린다.
// --sheet 는 9장씩 묶은 한눈 보기(sheet-N.png)도 만든다(장별 PNG 를 브라우저로 이어 붙인다).
const path = require('path'), fs = require('fs');
function loadPlaywright() {
  for (const n of ['playwright', 'playwright-core']) { try { return require(n); } catch (e) {} }
  for (const n of ['playwright', 'playwright-core']) { try { return require(require.resolve(n, { paths: [process.cwd()] })); } catch (e) {} }
  try { const g = require('child_process').execSync('npm root -g', { encoding: 'utf8' }).trim(); return require(path.join(g, 'playwright')); } catch (e) {}
  console.error('playwright 가 없다 — npm i -D playwright && npx playwright install chromium'); process.exit(2);
}
(async () => {
  const a = process.argv.slice(2), [F, OUT] = a.filter(x => !x.startsWith('--')), only = a.filter(x => !x.startsWith('--')).slice(2);
  if (!F || !OUT) { console.error('사용: node scripts/shots.js <deck.html> <폴더> [--motion] [--sheet] [장 id ...]'); process.exit(1); }
  const motion = a.includes('--motion');
  fs.mkdirSync(OUT, { recursive: true });
  const pw = loadPlaywright(), b = await pw.chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, reducedMotion: motion ? 'no-preference' : 'reduce' });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('file://' + path.resolve(F), { waitUntil: 'load', timeout: 180000 }); await p.waitForTimeout(1500);
  const ids = await p.evaluate(() => [...document.querySelectorAll('#deck > section.sl')].map(s => s.id));
  const list = only.length ? only.map(id => ids.indexOf(id)) : ids.map((_, i) => i), files = [];
  only.forEach(id => { if (ids.indexOf(id) < 0) errs.push('없는 장 id: ' + id); });
  for (const i of list) {
    if (i < 0) continue; const id = ids[i];
    await p.evaluate(i => { const s = document.querySelectorAll('#deck > section.sl')[i]; s.scrollIntoView(); const d = document.getElementById('deck'); if (d) d.scrollTop = s.offsetTop; }, i);
    await p.waitForTimeout(motion ? 3200 : 1300);
    const f = path.join(OUT, String(i).padStart(2, '0') + '_' + id + '.png'); await p.screenshot({ path: f }); files.push(f);
  }
  if (a.includes('--sheet') && files.length) {
    const q = await b.newPage({ viewport: { width: 1920, height: 1080 } });
    for (let k = 0; k * 9 < files.length; k++) {
      const part = files.slice(k * 9, k * 9 + 9);
      const html = '<body style="margin:0;background:#888;display:grid;grid-template-columns:repeat(3,640px);gap:6px;width:1932px">' +
        part.map(f => '<figure style="margin:0;position:relative"><img style="width:640px;height:360px;display:block" src="data:image/png;base64,' + fs.readFileSync(f).toString('base64') +
          '"><figcaption style="position:absolute;left:6px;bottom:4px;font:600 14px sans-serif;color:#fff;background:#0009;padding:1px 6px">' + path.basename(f, '.png') + '</figcaption></figure>').join('') + '</body>';
      await q.setContent(html); await q.setViewportSize({ width: 1932, height: Math.ceil(part.length / 3) * 366 });
      await q.screenshot({ path: path.join(OUT, 'sheet-' + k + '.png') });
    }
  }
  console.log(JSON.stringify({ n: files.length, out: OUT, errors: errs.slice(0, 20) }));
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
