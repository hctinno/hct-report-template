'use strict';
/**
 * 블루 리포트 PowerPoint 레이아웃 템플릿 생성기.
 *
 *   node .claude/skills/blue-report/pptx/template.js --brand brand/hct/brand.json --out decks-out
 *
 * build.js 와 쓰임이 다르다.
 *   build.js     내용이 정해진 용도별 덱 11종을 찍어 낸다 (pptx/content.js)
 *   template.js  사람이 PowerPoint 에서 직접 쓰는 빈 틀을 만든다 —
 *                「홈 → 새 슬라이드」에서 고르는 레이아웃 6종 + 쓰는 법을 보여 주는 견본 11장
 *
 * 색 · 글꼴 · 격자는 tokens.js(= assets/blue-report.css)에서 읽는다. 여기 hex 를 새로 적지 않는다.
 * 로고는 brand.js(= brand.json)에서 읽는다. 1920x1080 격자를 13.333x7.5in 로 옮긴다(1in = 144px).
 * 글자 하한은 HTML 과 같은 24px = 12pt. 견본도 이 아래로 내려가지 않는다.
 */
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

if (!fs.existsSync(path.join(__dirname, 'node_modules', 'pptxgenjs'))) {
  if (process.env.BLUE_REPORT_NO_INSTALL) {
    console.error(`[준비 필요] PPTX 생성기 의존성이 없다.\n  실행: cd ${__dirname} && npm install`);
    process.exit(1);
  }
  console.error('[준비] PPTX 생성기 의존성 설치 — 처음 한 번만');
  execFileSync('npm', ['install', '--silent', '--prefix', __dirname], { stdio: 'inherit' });
}

const PptxGenJS = require('pptxgenjs');
const { C, F, px } = require('./tokens');
const { loadBrand } = require('./brand');

const X = px;                                   // px → inch
const W = 1920, H = 1080;
const PAD = { top: 84, side: 96, bottom: 60 };  // layouts.js 와 같은 격자
const COVER = { top: 110, side: 120 };
const CW = W - PAD.side * 2;
const FOOT_Y = H - PAD.bottom - 34;
const MIN_PT = 12;                              // 24px

/* ── 레이아웃 이름. PowerPoint 「새 슬라이드」 목록에 이 이름으로 뜬다 ── */
const LAYOUT = {
  cover: 'HCT 표지', section: 'HCT 장 간지', titleOnly: 'HCT 제목만',
  titleBody: 'HCT 제목 · 본문', twoCol: 'HCT 2단 비교', closing: 'HCT 마무리',
};

function args() {
  const a = process.argv.slice(2);
  const get = (k, d) => { const i = a.indexOf(k); return i >= 0 ? a[i + 1] : d; };
  return { brand: get('--brand'), out: get('--out', 'decks-out'), name: get('--name', 'HCT_레이아웃_템플릿.pptx'),
           style: get('--style', 'h') };
}

/* ── 레이아웃 정의 ──────────────────────────────────────────────────────── */
function defineLayouts(pres, brand, opts = {}) {
  if ((opts.style || 'h') === 'h') return defineLayoutsH(pres, brand, opts);
  const Cs = pres.SchemeColor;
  const logoH = X(brand.logoHeight || 40);
  const markLight = brand.logoPathOnLight
    ? { image: { path: brand.logoPathOnLight, x: X(W - PAD.side) - logoH * brand.logoRatio, y: X(26), w: logoH * brand.logoRatio, h: logoH } }
    : { text: { text: brand.wordmark, options: { x: X(W - PAD.side - 420), y: X(26), w: X(420), h: X(40), align: 'right', fontSize: 14, bold: true, color: C.cobalt, margin: 0 } } };
  const markDark = (top, side) => brand.logoPath
    ? { image: { path: brand.logoPath, x: X(W - side) - logoH * brand.logoRatio, y: X(top), w: logoH * brand.logoRatio, h: logoH } }
    : { text: { text: brand.wordmark, options: { x: X(W - side - 420), y: X(top), w: X(420), h: X(40), align: 'right', fontSize: 14, bold: true, color: C.onDark, margin: 0 } } };
  const wm = (dark) => {
    const src = dark ? brand.watermarkPath : brand.watermarkPathOnLight;
    if (!src) return [];
    const ratio = (dark ? brand.watermarkRatio : brand.watermarkRatioOnLight) || brand.logoRatio;
    const w = X(720), h = w / ratio;
    return [{ image: { path: src, x: (X(W) - w) / 2, y: (X(H) - h) / 2, w, h, transparency: dark ? 95 : 97 } }];
  };
  const ph = (name, type, o) => ({ placeholder: { options: Object.assign({ name, type, margin: 0, valign: 'top' }, o), text: '' } });
  const foot = { text: { text: brand.company, options: { x: X(PAD.side), y: X(FOOT_Y), w: X(900), h: X(34), fontSize: MIN_PT, color: C.text3, margin: 0, valign: 'middle' } } };
  const slideNumber = { x: X(W - PAD.side - 120), y: X(FOOT_Y), w: X(120), h: X(34), fontSize: MIN_PT, bold: true, color: C.text2, align: 'right', margin: 0 };

  // 밝은 본문 장 공통 — 지면 · 워터마크 · 우측 상단 마크 · 꼬리말 · 장 이름 · 제목 · 리드 · 출처
  const lightBase = () => [
    ...wm(false), markLight, foot,
    ph('eyebrow', 'body', { x: X(PAD.side), y: X(PAD.top), w: X(CW - 400), h: X(34), fontSize: 13, bold: true, color: C.navy, valign: 'middle' }),
    ph('title', 'title', { x: X(PAD.side), y: X(PAD.top + 46), w: X(CW), h: X(78), fontSize: 27, bold: true, color: Cs.text1, align: 'left', valign: 'middle' }),
    ph('lede', 'body', { x: X(PAD.side), y: X(PAD.top + 132), w: X(CW), h: X(44), fontSize: 14, color: C.text2, valign: 'middle' }),
    ph('source', 'body', { x: X(PAD.side), y: X(FOOT_Y - 48), w: X(CW), h: X(34), fontSize: MIN_PT, color: C.text3, valign: 'middle' }),
  ];
  const BODY_Y = PAD.top + 200, BODY_H = FOOT_Y - 64 - BODY_Y;

  pres.defineSlideMaster({
    title: LAYOUT.cover, background: { color: C.cover },
    objects: [
      markDark(38, COVER.side),
      ph('eyebrow', 'body', { x: X(COVER.side), y: X(300), w: X(1400), h: X(44), fontSize: 15, color: C.soft[1], valign: 'middle' }),
      ph('title', 'title', { x: X(COVER.side), y: X(360), w: X(1500), h: X(240), fontSize: 44, bold: true, color: Cs.background1, align: 'left', valign: 'top' }),
      ph('subtitle', 'body', { x: X(COVER.side), y: X(620), w: X(1500), h: X(50), fontSize: 16, color: C.onCover2, valign: 'middle' }),
      ph('meta', 'body', { x: X(COVER.side), y: X(900), w: X(1000), h: X(44), fontSize: MIN_PT, color: C.onCover2, valign: 'middle' }),
      { text: { text: `© ${brand.copyrightYear} ${brand.company}`, options: { x: X(W - COVER.side - 800), y: X(950), w: X(800), h: X(30), fontSize: MIN_PT, color: C.onCover3, align: 'right', margin: 0, valign: 'middle' } } },
    ],
  });
  pres.defineSlideMaster({
    title: LAYOUT.section, background: { color: C.cover },
    objects: [
      ...wm(true), markDark(38, COVER.side),
      ph('number', 'body', { x: X(COVER.side), y: X(330), w: X(400), h: X(110), fontSize: 42, bold: true, color: C.accentOnDark, valign: 'bottom' }),
      ph('title', 'title', { x: X(COVER.side), y: X(460), w: X(1500), h: X(90), fontSize: 31, bold: true, color: Cs.background1, align: 'left', valign: 'middle' }),
      ph('desc', 'body', { x: X(COVER.side), y: X(570), w: X(1500), h: X(50), fontSize: 14, color: C.onCover2, valign: 'middle' }),
    ],
  });
  pres.defineSlideMaster({ title: LAYOUT.titleOnly, background: { color: C.page }, objects: lightBase(), slideNumber });
  pres.defineSlideMaster({
    title: LAYOUT.titleBody, background: { color: C.page }, slideNumber,
    objects: [...lightBase(), ph('body', 'body', { x: X(PAD.side), y: X(BODY_Y), w: X(CW), h: X(BODY_H), fontSize: 16, color: Cs.text1 })],
  });
  const colW = (CW - 48) / 2;
  pres.defineSlideMaster({
    title: LAYOUT.twoCol, background: { color: C.page }, slideNumber,
    objects: [...lightBase(),
      ph('leftHead', 'body', { x: X(PAD.side + 36), y: X(BODY_Y), w: X(colW - 72), h: X(72), fontSize: 16, bold: true, color: C.text2, valign: 'middle' }),
      ph('rightHead', 'body', { x: X(PAD.side + colW + 48 + 36), y: X(BODY_Y), w: X(colW - 72), h: X(72), fontSize: 16, bold: true, color: C.cobalt, valign: 'middle' }),
      ph('left', 'body', { x: X(PAD.side + 36), y: X(BODY_Y + 100), w: X(colW - 72), h: X(BODY_H - 120), fontSize: 15, color: Cs.text1 }),
      ph('right', 'body', { x: X(PAD.side + colW + 48 + 36), y: X(BODY_Y + 100), w: X(colW - 72), h: X(BODY_H - 120), fontSize: 15, color: Cs.text1 }),
    ],
  });
  pres.defineSlideMaster({
    title: LAYOUT.closing, background: { color: C.cover },
    objects: [
      ...wm(true), markDark(38, COVER.side),
      // 제목은 두 줄까지 — 아래에서 위로 쌓아 한 줄이든 두 줄이든 연락처와 간격이 같다
      ph('title', 'title', { x: X(COVER.side), y: X(300), w: X(W - COVER.side * 2), h: X(220), fontSize: 40, bold: true, color: Cs.background1, align: 'left', valign: 'bottom' }),
      ph('contact', 'body', { x: X(COVER.side), y: X(550), w: X(1400), h: X(50), fontSize: 14, color: C.onCover2, valign: 'middle' }),
    ],
  });
  return { colW, BODY_Y, BODY_H };
}

/* ── 스타일 H 레이아웃 — 밝은 지면 · 사선 패널(그림) · 머리 탭(그림) · 고정 워터마크 ──────────────
   패널 · 탭은 panel.js 가 blue-style.css 「H」 와 같은 조리법으로 그린 PNG 다. 레이아웃 이름 · 자리표시자
   이름은 A/C 와 같다 — from_deck.js · 견본이 그대로 쓴다. 글자 색만 밝은 지면에 맞춘다. */
function defineLayoutsH(pres, brand, opts) {
  const P = require('./panel').writePanels(fs.mkdtempSync(path.join(require('os').tmpdir(), 'blue-report-h-')));
  const Cs = pres.SchemeColor;
  const full = (p) => ({ image: { path: p, x: 0, y: 0, w: X(W), h: X(H) } });
  const logoH = X(brand.logoHeight || 40);
  const mark = (dark) => {
    const p = dark ? brand.logoPath : brand.logoPathOnLight;
    return p ? { image: { path: p, x: X(W - PAD.side) - logoH * brand.logoRatio, y: X(26), w: logoH * brand.logoRatio, h: logoH } }
      : { text: { text: brand.wordmark, options: { x: X(W - PAD.side - 420), y: X(26), w: X(420), h: X(40), align: 'right', fontSize: 14, bold: true, color: dark ? C.onDark : C.cobalt, margin: 0 } } };
  };
  // 워터마크 — 모든 장 같은 크기 · 같은 자리(폭 720 · 오른쪽 96 · 아래 104). 밝은 지면 6.5% · 패널 위 16%
  const wm = (dark) => {
    const src = dark ? brand.watermarkPath : brand.watermarkPathOnLight;
    if (!src) return [];
    const ratio = (dark ? brand.watermarkRatio : brand.watermarkRatioOnLight) || brand.logoRatio;
    const w = 720, h = w / ratio;
    return [{ image: { path: src, x: X(W - 96 - w), y: X(H - 104 - h), w: X(w), h: X(h), transparency: dark ? 84 : 93 } }];
  };
  const ph = (name, type, o) => ({ placeholder: { options: Object.assign({ name, type, margin: 0, valign: 'top' }, o), text: '' } });
  const foot = { text: { text: brand.company, options: { x: X(PAD.side), y: X(FOOT_Y), w: X(900), h: X(34), fontSize: MIN_PT, color: C.text2Hi, margin: 0, valign: 'middle' } } };
  const slideNumber = { x: X(W - PAD.side - 120), y: X(FOOT_Y), w: X(120), h: X(34), fontSize: MIN_PT, bold: true, color: C.cobalt, align: 'right', margin: 0 };
  const TAB = require('./panel').TAB;
  const lightBase = () => [
    { image: { path: P.tab, x: 0, y: 0, w: X(TAB.w), h: X(TAB.h) } },
    { line: { x: X(TAB.w - 20), y: X(TAB.h), w: X(W - TAB.w + 20), h: 0, line: { color: C.lineHi, width: 0.75 } } },
    ...wm(false), mark(false), foot,
    ph('eyebrow', 'body', { x: X(PAD.side), y: X(0), w: X(TAB.w - PAD.side - 40), h: X(TAB.h), fontSize: 13, bold: true, color: C.onDark, valign: 'middle' }),
    ph('title', 'title', { x: X(PAD.side), y: X(PAD.top + 46), w: X(CW), h: X(78), fontSize: 27, bold: false, color: Cs.text1, align: 'left', valign: 'middle' }),
    ph('lede', 'body', { x: X(PAD.side), y: X(PAD.top + 132), w: X(CW), h: X(44), fontSize: 14, color: C.text2Hi, valign: 'middle' }),
    ph('source', 'body', { x: X(PAD.side), y: X(FOOT_Y - 48), w: X(CW), h: X(34), fontSize: MIN_PT, color: C.text3Hi, valign: 'middle' }),
  ];
  const BODY_Y = PAD.top + 200, BODY_H = FOOT_Y - 64 - BODY_Y;
  const LEFT_W = 880;   // 패널 왼쪽 글 폭 — 패널이 아래로 50.8% 까지 내려온다

  // 표지 · 마무리 — 같은 오른쪽 패널. 글은 밝은 지면 왼쪽
  pres.defineSlideMaster({
    title: LAYOUT.cover, background: { color: C.card },
    objects: [
      full(P.r), ...wm(true), mark(true),
      ph('eyebrow', 'body', { x: X(PAD.side), y: X(300), w: X(LEFT_W), h: X(44), fontSize: 15, bold: true, color: C.cobalt, valign: 'middle' }),
      ph('title', 'title', { x: X(PAD.side), y: X(360), w: X(LEFT_W), h: X(250), fontSize: 44, bold: false, color: Cs.text1, align: 'left', valign: 'top' }),
      ph('subtitle', 'body', { x: X(PAD.side), y: X(640), w: X(LEFT_W), h: X(60), fontSize: 16, color: C.text2Hi, valign: 'middle' }),
      ph('meta', 'body', { x: X(PAD.side), y: X(900), w: X(LEFT_W), h: X(44), fontSize: MIN_PT, color: C.text2Hi, valign: 'middle' }),
      { text: { text: `© ${brand.copyrightYear} ${brand.company}`, options: { x: X(W - PAD.side - 700), y: X(FOOT_Y), w: X(700), h: X(34), fontSize: MIN_PT, color: C.onCover2, align: 'right', margin: 0, valign: 'middle' } } },
    ],
  });
  // 간지 — 왼쪽 패널(표지의 거울상)에 장 번호, 오른쪽에 제목
  pres.defineSlideMaster({
    title: LAYOUT.section, background: { color: C.card },
    objects: [
      full(P.l), ...wm(false), mark(false),
      { text: { text: 'CHAPTER', options: { x: X(PAD.side), y: X(230), w: X(500), h: X(40), fontSize: 13, bold: true, color: C.onCover2, charSpacing: 4, margin: 0 } } },
      ph('number', 'body', { x: X(PAD.side), y: X(280), w: X(640), h: X(260), fontSize: 120, bold: false, color: Cs.background1, valign: 'top' }),
      ph('title', 'title', { x: X(1060), y: X(300), w: X(W - 1060 - PAD.side), h: X(110), fontSize: 36, bold: false, color: Cs.text1, align: 'left', valign: 'bottom' }),
      ph('desc', 'body', { x: X(1060), y: X(420), w: X(W - 1060 - PAD.side), h: X(50), fontSize: 15, color: C.text2Hi, valign: 'middle' }),
    ],
  });
  pres.defineSlideMaster({ title: LAYOUT.titleOnly, background: { color: C.card }, objects: lightBase(), slideNumber });
  pres.defineSlideMaster({
    title: LAYOUT.titleBody, background: { color: C.card }, slideNumber,
    objects: [...lightBase(), ph('body', 'body', { x: X(PAD.side), y: X(BODY_Y), w: X(CW), h: X(BODY_H), fontSize: 16, color: Cs.text1 })],
  });
  const colW = (CW - 48) / 2;
  pres.defineSlideMaster({
    title: LAYOUT.twoCol, background: { color: C.card }, slideNumber,
    objects: [...lightBase(),
      ph('leftHead', 'body', { x: X(PAD.side + 36), y: X(BODY_Y), w: X(colW - 72), h: X(72), fontSize: 16, bold: true, color: C.text2Hi, valign: 'middle' }),
      ph('rightHead', 'body', { x: X(PAD.side + colW + 48 + 36), y: X(BODY_Y), w: X(colW - 72), h: X(72), fontSize: 16, bold: true, color: C.cobalt, valign: 'middle' }),
      ph('left', 'body', { x: X(PAD.side + 36), y: X(BODY_Y + 100), w: X(colW - 72), h: X(BODY_H - 120), fontSize: 15, color: Cs.text1 }),
      ph('right', 'body', { x: X(PAD.side + colW + 48 + 36), y: X(BODY_Y + 100), w: X(colW - 72), h: X(BODY_H - 120), fontSize: 15, color: Cs.text1 }),
    ],
  });
  pres.defineSlideMaster({
    title: LAYOUT.closing, background: { color: C.card },
    objects: [
      full(P.r), ...wm(true), mark(true),
      ph('title', 'title', { x: X(PAD.side), y: X(260), w: X(LEFT_W), h: X(300), fontSize: 40, bold: false, color: Cs.text1, align: 'left', valign: 'bottom' }),
      ph('contact', 'body', { x: X(PAD.side), y: X(590), w: X(LEFT_W), h: X(60), fontSize: 14, color: C.text2Hi, valign: 'middle' }),
    ],
  });
  return { colW, BODY_Y, BODY_H, style: 'h', LEFT_W };
}

/* ── 견본에 쓰는 원자 부품. 전부 토큰 색만 ── */
let n = 0;
const oid = (s) => `${s}_${++n}`;
const txt = (sl, text, o) => sl.addText(text, Object.assign({ isTextBox: true, margin: 0, valign: 'top', objectName: oid('text') }, o));
function card(sl, x, y, w, h, fill) {
  // 흰 카드 + 옅은 그림자 — HTML .br-card 와 같은 처리. 테두리는 두르지 않는다.
  sl.addShape('roundRect', {
    x: X(x), y: X(y), w: X(w), h: X(h), rectRadius: 0.12, objectName: oid('card'),
    fill: { color: fill || C.card }, line: { type: 'none' },
    shadow: fill ? undefined : { type: 'outer', color: C.text, opacity: 0.10, blur: 18, offset: 6, angle: 90 },
  });
}
function badge(sl, x, y, d, label, fill) {
  txt(sl, label, { x: X(x), y: X(y), w: X(d), h: X(d), shape: 'ellipse', fill: { color: fill }, line: { type: 'none' },
    color: C.white, fontSize: 14, bold: true, align: 'center', valign: 'middle' });
}
const bullets = (items, o = {}) => items.map((t, i) => ({ text: t, options: Object.assign({ bullet: true, breakLine: i < items.length - 1 }, o) }));

/* ── 견본 11장 ──────────────────────────────────────────────────────────── */
function samples(pres, brand, g) {
  const sec = (t) => pres.addSection({ title: t });
  const add = (layout, section) => pres.addSlide({ masterName: layout, sectionTitle: section });
  const head = (sl, eyebrow, title, lede, source) => {
    if (eyebrow) sl.addText(eyebrow, { placeholder: 'eyebrow' });
    sl.addText(title, { placeholder: 'title' });
    if (lede) sl.addText(lede, { placeholder: 'lede' });
    if (source) sl.addText(source, { placeholder: 'source' });
  };
  const Y0 = g.BODY_Y;

  sec('표지 · 목차');
  let s = add(LAYOUT.cover, '표지 · 목차');
  s.addText('2026년 3분기 · 경영회의 보고', { placeholder: 'eyebrow' });
  s.addText('3분기 시험인증 사업\n실적 보고', { placeholder: 'title' });
  s.addText('목표 대비 104% 달성 · 4분기 EMC 챔버 2기 증설 승인 요청', { placeholder: 'subtitle' });
  s.addText('경영기획팀  ·  기획 A  ·  2026.11.24', { placeholder: 'meta' });
  s.addNotes('표지 레이아웃. 제목은 두 줄 이내, 부제는 결론 한 줄로 쓴다.');

  s = add(LAYOUT.titleOnly, '표지 · 목차');
  head(s, 'CONTENTS', '목차');
  [['01', '요약', '결론 · 요청 사항'], ['02', '부문별 실적', '핵심 지표 · 사업부 실적 · 성장 요인'],
   ['03', '리스크 · 대응', '현행 대비 개선안'], ['04', '추진 일정', '승인 · 설치 · 가동']].forEach(([no, t, d], i) => {
    const y = Y0 + i * 150;
    badge(s, PAD.side, y, 84, no, C.cobalt);
    txt(s, t, { x: X(PAD.side + 120), y: X(y + 2), w: X(900), h: X(46), fontSize: 20, bold: true, color: C.text });
    txt(s, d, { x: X(PAD.side + 120), y: X(y + 50), w: X(1200), h: X(36), fontSize: 14, color: C.text2 });
  });
  s.addNotes('제목만 레이아웃에 번호 원과 글을 얹은 목차. 장이 둘 이상일 때만 둔다.');

  sec('요약');
  s = add(LAYOUT.titleOnly, '요약');
  head(s, '01  요약', '목표 104% 달성 — 4분기 챔버 증설 승인 필요', '2026.07~09 · 사내 ERP 집계 10.31 기준', '사용법 견본 수치 · 실제 보고에서는 실제 값과 출처로 바꾼다');
  const cw = (CW - 2 * 36) / 3;
  [['매출 312억 원', '목표 대비 104%', ['모빌리티 +24% · 국방 +11%', 'ICT 98%로 소폭 미달']],
   ['재시험률 4.1%', '목표 3.5% 초과', ['신규 시험원 투입 라인 집중', '12월 교육 과정 개편']],
   ['배터리 대기 23일', '고객 이탈 우려', ['챔버 가동률 96%', '증설 없이는 4분기 수주 제한']]].forEach(([big, sub, bl], i) => {
    const x = PAD.side + i * (cw + 36), h = 470;
    card(s, x, Y0, cw, h);
    badge(s, x + 44, Y0 + 44, 64, String(i + 1), C.cobalt);
    txt(s, big, { x: X(x + 44), y: X(Y0 + 140), w: X(cw - 88), h: X(70), fontSize: 24, bold: true, color: C.text });
    txt(s, sub, { x: X(x + 44), y: X(Y0 + 214), w: X(cw - 88), h: X(40), fontSize: 14, bold: true, color: C.cobalt });
    txt(s, bullets(bl), { x: X(x + 44), y: X(Y0 + 290), w: X(cw - 88), h: X(h - 320), fontSize: 14, color: C.text2, paraSpaceAfter: 8 });
  });
  s.addNotes('요약 세 칸. 굵은 한 줄이 주장, 아래가 근거다.');

  sec('부문별 실적');
  s = add(LAYOUT.section, '부문별 실적');
  s.addText('02', { placeholder: 'number' });
  s.addText('부문별 실적', { placeholder: 'title' });
  s.addText('핵심 지표 · 사업부 실적 · 성장 요인', { placeholder: 'desc' });

  s = add(LAYOUT.titleOnly, '부문별 실적');
  head(s, '02  부문별 실적', '핵심 지표 4개 중 3개 개선 — 재시험률만 악화', '비교 기준 — 매출 전년 동기 · 수주와 리드타임 전 분기 · 재시험률 목표', '사용법 견본 수치');
  const kw = (CW - 3 * 36) / 4;
  [['매출', '312', '억 원', '▲ 8.4%', '전년 동기 대비', C.okText], ['신규 수주', '1,284', '건', '▲ 112건', '전 분기 대비', C.okText],
   ['평균 리드타임', '9.6', '일', '▼ 1.2일', '단축 · 개선', C.okText], ['재시험률', '4.1', '%', '▲ 0.6%p', '목표 3.5% 초과', C.alertText]]
    .forEach(([k, v, u, d, basis, dc], i) => {
      const x = PAD.side + i * (kw + 36), h = 330;
      card(s, x, Y0, kw, h);
      txt(s, k, { x: X(x + 40), y: X(Y0 + 40), w: X(kw - 80), h: X(40), fontSize: 14, bold: true, color: C.text2 });
      txt(s, [{ text: v, options: { fontSize: 28, bold: true, color: C.navy } }, { text: ' ' + u, options: { fontSize: 14, bold: true, color: C.text2 } }],
        { x: X(x + 40), y: X(Y0 + 100), w: X(kw - 80), h: X(90), valign: 'bottom' });
      txt(s, [{ text: d, options: { bold: true, color: dc, breakLine: true } }, { text: basis, options: { color: C.text2 } }],
        { x: X(x + 40), y: X(Y0 + 216), w: X(kw - 80), h: X(84), fontSize: 13 });
    });
  card(s, PAD.side, Y0 + 380, CW, 130, C.tint);
  txt(s, [{ text: '시사점  ', options: { bold: true, color: C.navy } }, { text: '재시험률은 신규 시험원 라인에 집중 — 교육 개편 후 1분기 안 3.5% 복귀 목표', options: { color: C.text } }],
    { x: X(PAD.side + 44), y: X(Y0 + 380), w: X(CW - 88), h: X(130), fontSize: 16, valign: 'middle' });
  s.addNotes('수치 타일 넷. 증감 색은 방향이 아니라 좋고 나쁨이다 — 리드타임 감소는 초록, 재시험률 증가는 빨강.');

  s = add(LAYOUT.titleOnly, '부문별 실적');
  head(s, '02  부문별 실적', '모빌리티 부문이 전체 성장을 견인', '사업부별 전년 대비 매출 증가율(%)', '사용법 견본 수치');
  const chW = 1080;
  s.addChart(pres.charts.BAR, [{ name: '증가율', labels: ['모빌리티', '배터리 · 국방', '교정', '시험인증(ICT)'], values: [24, 11, 6, 3] }], {
    x: X(PAD.side), y: X(Y0), w: X(chW), h: X(g.BODY_H - 20), barDir: 'bar', objectName: 'chart_growth',
    chartColors: [C.cobalt, C.text3, C.text3, C.text3], barGapWidthPct: 70,
    showValue: true, dataLabelPosition: 'outEnd', dataLabelFontSize: 14, dataLabelColor: C.text, dataLabelFontFace: '+mn-lt', dataLabelFontBold: true, dataLabelFormatCode: '+0"%"',
    catAxisLabelColor: C.text2, catAxisLabelFontSize: 14, catAxisLabelFontFace: '+mn-lt', catAxisOrientation: 'maxMin',
    catAxisLineShow: false, catAxisLineColor: C.hairline, valAxisLineColor: C.hairline,
    valAxisHidden: true, valAxisLabelColor: C.text3, valAxisMinVal: 0, valAxisMaxVal: 30, valGridLine: { style: 'none' }, catGridLine: { style: 'none' }, showLegend: false,
  });
  const nx = PAD.side + chW + 48, nw = CW - chW - 48;
  card(s, nx, Y0, nw, g.BODY_H - 20);
  txt(s, '해설', { x: X(nx + 44), y: X(Y0 + 40), w: X(nw - 88), h: X(40), fontSize: 14, bold: true, color: C.cobalt });
  txt(s, bullets(['완성차 3사 전장부품 EMC 물량 증가', '고전압 EMC 챔버 가동 후 신규 고객 12곳', 'ICT는 단말 출시 감소로 정체']),
    { x: X(nx + 44), y: X(Y0 + 100), w: X(nw - 88), h: X(g.BODY_H - 160), fontSize: 15, color: C.text, paraSpaceAfter: 12 });
  s.addNotes('PowerPoint 기본 차트 — 막대를 눌러 데이터 편집. 주인공 막대 하나만 코발트, 나머지는 회색.');

  s = add(LAYOUT.titleOnly, '부문별 실적');
  head(s, '02  부문별 실적', '4개 사업부 중 3개 목표 달성 — 배터리 · 국방 93%', '단위 억 원 · 2026.07~09', '사용법 견본 수치 · 사내 ERP 집계 10.31 기준');
  const line = (c, w) => ({ type: 'solid', pt: w, color: c });
  const none = { type: 'none' };
  const th = (t, right) => ({ text: t, options: { bold: true, color: C.navy, fill: { color: C.page }, align: right ? 'right' : 'left', border: [line(C.navy, 2), none, line(C.navy, 1), none] } });
  const td = (t, o = {}) => ({ text: t, options: Object.assign({ color: C.text, border: [none, none, line(C.cardLine, 0.75), none] }, o) });
  const tn = (t, o = {}) => td(t, Object.assign({ align: 'right' }, o));
  const hl = { fill: { color: C.tint }, bold: true };
  s.addTable([
    [th('사업부'), th('목표', true), th('실적', true), th('달성률', true), th('상태')],
    [td('시험인증(ICT)'), tn('120'), tn('118'), tn('98%'), td('▲ 소폭 미달', { color: C.warnText, bold: true })],
    [td('모빌리티', hl), tn('80', hl), tn('96', hl), tn('120%', hl), td('● 초과 달성', Object.assign({}, hl, { color: C.okText }))],
    [td('교정'), tn('60'), tn('61'), tn('102%'), td('● 달성', { color: C.okText, bold: true })],
    [td('배터리 · 국방'), tn('40'), tn('37'), tn('93%'), td('■ 미달', { color: C.alertText, bold: true })],
    [td('합계', { bold: true }), tn('300', { bold: true }), tn('312', { bold: true }), tn('104%', { bold: true }), td('')],
  ], { x: X(PAD.side), y: X(Y0), w: X(CW), colW: [3.6, 2.0, 2.0, 2.0, 2.4].map((v) => v * X(CW) / 12), rowH: X(78), fontSize: 15, valign: 'middle', margin: [0, 0.14, 0, 0.14], objectName: 'table_results' });
  s.addNotes('표는 상세 비교가 필요할 때만. 상태는 기호와 글자로 — 색만으로 가르지 않는다.');

  sec('리스크 · 대응');
  s = add(LAYOUT.twoCol, '리스크 · 대응');
  head(s, '03  리스크 · 대응', '챔버 2기 증설 시 배터리 대기 23일 → 10일 이내', null, '사용법 견본 · 투자액과 효과는 재무 검토 후 확정');
  [C.tint, C.card].forEach((f, i) => card(s, PAD.side + i * (g.colW + 48), Y0, g.colW, g.BODY_H - 10, f));
  s.addText('현행', { placeholder: 'leftHead' });
  s.addText('개선안 — 챔버 2기 증설', { placeholder: 'rightHead' });
  s.addText(bullets(['배터리 시험 평균 대기 23일', '챔버 가동률 96% — 긴급 건 수용 불가', '경쟁사 대비 대기 1주 이상']), { placeholder: 'left', paraSpaceAfter: 14 });
  s.addText(bullets(['평균 대기 10일 이내 목표', '가동률 75% 수준 — 긴급 건 수용', '연 매출 00억 원 추가 기회']), { placeholder: 'right', paraSpaceAfter: 14 });
  s.addNotes('왼쪽은 대조군(옅은 바탕), 오른쪽이 주인공(흰 카드).');

  sec('추진 일정');
  s = add(LAYOUT.titleOnly, '추진 일정');
  head(s, '04  추진 일정', '11월 승인 시 12월 시운전 · 1월 정상 가동');
  const steps = [['10월 2주', '현황 진단', '가동률 · 대기 분석', true], ['10월 4주', '개선안 확정', '투자안 2건 비교', true],
    ['11월 27일', '투자 승인', '경영회의 상정', false], ['12월', '설치 · 시운전', '챔버 2기 설치', false], ['2027년 1월', '정상 가동', '대기 10일 이내 확인', false]];
  const gap = CW / steps.length, ly = Y0 + 40;
  s.addShape('line', { x: X(PAD.side + 20), y: X(ly), w: X(gap * (steps.length - 1)), h: 0, line: { color: C.hairline, width: 2 }, objectName: 'timeline_line' });
  steps.forEach(([d, t, desc, done], i) => {
    const x = PAD.side + i * gap;
    s.addShape('ellipse', { x: X(x), y: X(ly - 20), w: X(40), h: X(40), fill: { color: done ? C.cobalt : C.card }, line: { color: C.cobalt, width: 2.5 }, objectName: oid('dot') });
    txt(s, d, { x: X(x), y: X(ly + 50), w: X(gap - 30), h: X(36), fontSize: 13, bold: true, color: C.cobalt });
    txt(s, t, { x: X(x), y: X(ly + 96), w: X(gap - 30), h: X(46), fontSize: 18, bold: true, color: C.text });
    txt(s, desc, { x: X(x), y: X(ly + 150), w: X(gap - 30), h: X(70), fontSize: 14, color: C.text2 });
  });
  card(s, PAD.side, Y0 + 330, CW, 140, C.tint);
  txt(s, [{ text: '요청 사항  ', options: { bold: true, color: C.navy } }, { text: 'EMC 챔버 2기 증설 투자 승인 — 11월 27일 경영회의', options: { color: C.text } }],
    { x: X(PAD.side + 44), y: X(Y0 + 330), w: X(CW - 88), h: X(140), fontSize: 16, valign: 'middle' });
  s.addNotes('완료 단계는 채운 원, 예정 단계는 빈 원.');

  s = add(LAYOUT.titleBody, '추진 일정');
  head(s, '부록', '작성 원칙 — 이 장은 지우고 사용');
  const rules = [['제목 = 주장', '주제어가 아니라 결론 한 문장 · 마침표 없음'], ['한 장 한 주장', '주인공 하나 · 근거 3개 이내 · 개조식 명사형'],
    ['수치는 기준과 함께', '단위 · 비교 기준 · 기준일 · 출처'], ['색은 역할로', '강조 하나(코발트) · 비교는 회색 · 상태색은 기호와 함께'],
    ['글자 12pt 이상', '넘치면 줄이지 말고 장을 나눔 · 파이 차트 금지']];
  s.addText(rules.flatMap(([h, d], i) => [
    { text: `${i + 1}. ${h}   `, options: { bold: true, color: C.cobalt } },
    { text: d, options: { color: C.text2, breakLine: i < rules.length - 1 } },
  ]), { placeholder: 'body', paraSpaceAfter: 16 });

  s = add(LAYOUT.closing, '추진 일정');
  s.addText('감사합니다', { placeholder: 'title' });
  s.addText('문의 — 경영기획팀 기획 A', { placeholder: 'contact' });
}

/* pptxgenjs 는 테마 색 · 글꼴을 쓰지 못한다. 저장 뒤 theme*.xml 을 토큰 값으로 바꾼다.
   PowerPoint 「디자인 → 색 · 글꼴」과 차트 기본색이 HCT 값으로 잡힌다. */
async function patchTheme(file) {
  const JSZip = require(require.resolve('jszip', { paths: [path.dirname(require.resolve('pptxgenjs'))] }));
  const zip = await JSZip.loadAsync(fs.readFileSync(file));
  const scheme = { dk1: C.text, lt1: C.white, dk2: C.cover, lt2: C.page,
    accent1: C.cat[0], accent2: C.cat[1], accent3: C.cat[2], accent4: C.cat[3], accent5: C.cat[4], accent6: C.cat[5],
    hlink: C.cobalt, folHlink: C.navy };
  const clr = '<a:clrScheme name="HCT Blue Report">' + Object.entries(scheme).map(([k, v]) => `<a:${k}><a:srgbClr val="${v}"/></a:${k}>`).join('') + '</a:clrScheme>';
  const f = (tag) => `<a:${tag}><a:latin typeface="${F.kr}"/><a:ea typeface="${F.kr}"/><a:cs typeface=""/><a:font script="Hang" typeface="${F.kr}"/></a:${tag}>`;
  const fonts = `<a:fontScheme name="HCT Blue Report">${f('majorFont')}${f('minorFont')}</a:fontScheme>`;
  for (const name of Object.keys(zip.files).filter((k) => /^ppt\/theme\/theme\d+\.xml$/.test(k))) {
    let x = await zip.file(name).async('string');
    x = x.replace(/<a:clrScheme[\s\S]*?<\/a:clrScheme>/, clr).replace(/<a:fontScheme[\s\S]*?<\/a:fontScheme>/, fonts);
    zip.file(name, x);
  }
  // 폴더 항목 없이 다시 묶는다 — 폴더 항목이 있으면 클라우드 공동 편집에서 열리지 않는 경우가 있다
  const out = new JSZip();
  for (const [k, e] of Object.entries(zip.files)) if (!e.dir) out.file(k, await e.async('nodebuffer'), { createFolders: false });
  fs.writeFileSync(file, await out.generateAsync({ type: 'nodebuffer', compression: 'DEFLATE' }));
}

async function main() {
  const a = args();
  if (!a.brand) { console.error('사용법: node template.js --brand <brand.json> [--out 폴더] [--name 파일명]'); process.exit(1); }
  const brand = loadBrand(a.brand);
  const pres = new PptxGenJS();
  pres.layout = 'LAYOUT_WIDE';
  pres.author = brand.company;
  pres.company = brand.company.replace(/&/g, '&amp;');
  pres.title = `${brand.company} 레이아웃 템플릿`;
  pres.theme = { headFontFace: F.kr, bodyFontFace: F.kr };
  const g = defineLayouts(pres, brand, { style: a.style });
  samples(pres, brand, g);
  fs.mkdirSync(a.out, { recursive: true });
  const file = path.join(a.out, a.name);
  await pres.writeFile({ fileName: file });
  await patchTheme(file);
  console.log(`  ${a.name}  레이아웃 ${Object.keys(LAYOUT).length}종 · 견본 11장  ${(fs.statSync(file).size / 1024).toFixed(0)}KB`);
  console.log(`출력: ${file}`);
}

if (require.main === module) main().catch((e) => { console.error('실패:', e.message); process.exit(1); });
// from_deck.js(HTML 덱 → PPTX)가 같은 레이아웃 · 부품 · 테마 처리를 쓴다
module.exports = { LAYOUT, MIN_PT, defineLayouts, patchTheme, txt, card, badge, X, W, H, PAD, COVER, CW, FOOT_Y };
