'use strict';
/**
 * 블루 리포트 PowerPoint 판 생성기.
 *
 *   node build.js --brand ../../../brand/hct/brand.json --out ./dist
 *
 * --brand 경로는 어디서 실행하느냐에 따라 다르다.
 *   저장소 스킬 폴더에서   ../../../brand/hct/brand.json
 *   저장소 루트에서        brand/hct/brand.json
 *   계정 스킬 설치본에서   brand/hct/brand.json
 *   node build.js --brand brand.json --deck internal
 *
 * 색·크기는 assets/blue-report.css 에서 읽는다(tokens.js). 여기 다시 적지 않는다.
 */
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

// 의존성이 없으면 여기서 알아서 받는다. 사용자가 미리 npm install 할 필요가 없다.
if (!fs.existsSync(path.join(__dirname, 'node_modules', 'pptxgenjs'))) {
  if (process.env.BLUE_REPORT_NO_INSTALL) {
    console.error(`[준비 필요] PPTX 생성기 의존성이 없다.\n  실행: cd ${__dirname} && npm install`);
    process.exit(1);
  }
  console.error('[준비] PPTX 생성기 의존성 설치 — 처음 한 번만');
  try {
    execFileSync('npm', ['install', '--silent', '--prefix', __dirname], { stdio: 'inherit' });
  } catch (e) {
    console.error(`[준비 실패] npm install 이 실패했다.\n  직접 실행: cd ${__dirname} && npm install`);
    process.exit(1);
  }
}

const PptxGenJS = require('pptxgenjs');
const { C } = require('./tokens');
const S = require('./slides');
const L = require('./layouts');
const CONTENT = require('./content');

const { loadBrand } = require('./brand');

const BUILDERS = {
  cover: S.cover, agenda: S.agenda, darkSummary: S.darkSummary, table: S.tableSlide,
  bar: S.barSlide, donut: S.donutSlide, compare: S.compareSlide, progress: S.progressSlide,
  roadmap: S.roadmapSlide, timeline: S.timelineSlide, bigStat: S.bigStatSlide,
  closing: S.closingSlide,
};

function buildDeck(deck, brand, outDir) {
  const pres = new PptxGenJS();
  pres.layout = 'LAYOUT_WIDE';          // 슬라이드를 추가하기 전에 설정해야 좌표가 맞는다
  pres.author = brand.company;
  pres.company = brand.company;
  pres.title = deck.docTitle;

  const b = Object.assign({}, brand, { docTitle: deck.docTitle });
  deck.slides.forEach((s, i) => {
    const fn = BUILDERS[s.type];
    if (!fn) throw new Error(`알 수 없는 슬라이드 종류: ${s.type}`);
    const sl = fn(pres, s, b, i + 1);
    L.mark(sl, b);                       // 우측 상단 브랜드 마크 — 빠짐없이 모든 장에
    if (s.notes) sl.addNotes(s.notes);   // 발표자 노트는 노트 창에만 들어간다
  });

  fs.mkdirSync(outDir, { recursive: true });
  const out = path.join(outDir, deck.file);
  return pres.writeFile({ fileName: out }).then(() => {
    const kb = fs.statSync(out).size / 1024;
    console.log(`  ${path.basename(out)}  ${deck.slides.length}장  ${kb.toFixed(0)}KB`);
    return out;
  });
}

async function main() {
  const args = process.argv.slice(2);
  const get = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
  const brandPath = get('--brand');
  if (!brandPath) { console.error('사용법: node build.js --brand <brand.json> [--deck 이름] [--out 폴더]'); process.exit(1); }
  const brand = loadBrand(brandPath);
  const outDir = path.resolve(get('--out', path.join(__dirname, '..', 'dist', 'pptx')));
  const only = get('--deck');

  const decks = Object.entries(CONTENT).filter(([k, v]) => v && v.slides && (!only || k === only));
  if (!decks.length) { console.error(`덱을 찾지 못했다: ${only}`); process.exit(1); }

  console.log(`회사: ${brand.company} · 마크: 다크면 ${brand.logoPath ? '로고' : '워드마크'} · 밝은면 ${brand.logoPathOnLight ? '로고' : '워드마크'} (우측 상단)`);
  for (const [, deck] of decks) await buildDeck(deck, brand, outDir);
  console.log(`\n출력 폴더: ${outDir}`);
}

main().catch((e) => { console.error('실패:', e.message); process.exit(1); });
