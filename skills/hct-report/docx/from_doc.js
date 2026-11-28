'use strict';
/**
 * A4 문서 manifest(scripts/doc_to_docx.py 가 만든다) → 회사 양식 Word(.docx)
 *
 *   node docx/from_doc.js manifest.json brand.json out.docx [form.json]
 *
 * 양식 값(여백 · 글자 크기 · 색 역할 · 머리말 · 꼬리말 · 문서 정보 표 · 표 · 결재란 · 번호 모양)은
 * 양식 정의 forms/<id>.json 에서 읽는다 — HTML · PDF 의 blue-doc.css 생성 블록과 같은 파일이다(scripts/build_form.py).
 * 양식을 주지 않으면 forms/hct-standard.json. 색은 양식의 토큰 이름을 blue-report.css(pptx/tokens.js)에서 hex 로 바꾼다.
 * 로고 · 회사명은 brand.json(pptx/brand.js). 이 파일에는 hex 도, 양식 치수도 적지 않는다.
 * 지면 794px = A4 210mm 이므로 1px = 0.75pt = 15 DXA.
 *
 * Word 에서 고치기 쉽게 만든다.
 *   - 표제 · 부제 · 장 · 절 제목은 Word 스타일(제목 1 · 제목 2)이다. 탐색 창과 자동 목차에 잡힌다
 *   - 강조어 · 상태 칩은 문자 스타일(HCT 강조어 · HCT 칩 …)이다. 스타일만 바꾸면 문서 전체가 바뀐다
 *   - 절차 단계는 Word 자동 번호다. 단계를 끼워 넣으면 번호가 다시 매겨진다
 *   - 규정의 (1) (2) 번호는 글자로 적는다 — 조문 번호는 개정해도 바뀌면 안 된다
 *   - 쪽번호는 필드(n / 전체)다. 손으로 적지 않는다
 */
const fs = require('fs');
const path = require('path');
const D = require('docx');
const { C, F, hex } = require('../pptx/tokens');
const { loadBrand } = require('../pptx/brand');

const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, Header, Footer,
  AlignmentType, BorderStyle, ShadingType, WidthType, HeightRule, TableLayoutType, VerticalAlign,
  TabStopType, LevelFormat, PageNumber, LineRuleType,
} = D;

const [, , MANIFEST, BRAND, OUT, FORM_ARG] = process.argv;
if (!MANIFEST || !BRAND || !OUT) {
  console.error('사용법: node docx/from_doc.js manifest.json brand.json out.docx [form.json]');
  process.exit(2);
}
const man = JSON.parse(fs.readFileSync(MANIFEST, 'utf8'));
const brand = loadBrand(BRAND);
// 양식은 scripts/doc_to_docx.py 가 기본값을 채워(build_form.resolve) 넘긴다 — HTML 과 Word 가 같은 기본값을 쓴다
if (!FORM_ARG) { console.error('양식 JSON 이 없다 — scripts/doc_to_docx.py 로 부른다'); process.exit(2); }
const FORM_PATH = FORM_ARG;
const FORM = JSON.parse(fs.readFileSync(FORM_PATH, 'utf8'));

// ── 단위 ──────────────────────────────────────────────────────────────────
const PX = 15;                         // 1px = 15 DXA (= 0.75pt)
/** '64px' · '10.5pt' · '17mm' → DXA(1/20pt) */
function dxa(v) {
  const m = /^(-?\d+(?:\.\d+)?)(px|pt|mm)$/.exec(String(v));
  if (!m) throw new Error(`양식 길이 값이 아니다: ${v} (${FORM_PATH})`);
  const n = Number(m[1]);
  return Math.round({ px: n * 15, pt: n * 20, mm: (n * 1440) / 25.4 }[m[2]]);
}
const ptOf = (v) => dxa(v) / 20;
const hp = (pt) => Math.round(pt * 2); // 반 포인트
const hpOf = (v) => hp(ptOf(v));
/** 양식의 색 토큰 이름 → hex. "none" 은 null */
const tok = (name) => (name && name !== 'none' ? hex(name) : null);

// ── 양식에서 읽은 치수 ────────────────────────────────────────────────────
const PAGE = { A4: [11906, 16838] }[FORM.page.size];
if (!PAGE) throw new Error(`양식 page.size 를 모른다: ${FORM.page.size}`);
const [PAGE_W, PAGE_H] = PAGE;
const MG = FORM.page.margin;
const W = PAGE_W - dxa(MG.left) - dxa(MG.right); // 본문 폭
const TY = FORM.type, SP = FORM.space, HD = FORM.header, FT = FORM.footer;
const META = FORM.meta, TBL = FORM.table, SIGN = FORM.sign;
const LST = FORM.list, NUM = FORM.numbering, TOC = FORM.toc, COVER = FORM.cover;
const FLOW = FORM.page.breaks === 'flow';
const IND = dxa(FORM.space.indent);   // 본문 들여쓰기 — 절 제목 · 문단 · 목록 · 절차 · 목차
const JUSTIFY = TY.body.align === 'justify';
const BODY_PT = ptOf(TY.body.size);
const LINE = Math.round(BODY_PT * TY.body.lineHeight * 20); // 본문 행간 — 최소값으로 준다(큰 글자는 늘어난다)
const SMALL = hpOf(TY.small.size);

const T = {
  page: C.page, card: C.card, line: C.cardLine, hair: C.hairline, chipLine: C.chipLine, track: hex('track'),
  text: C.text, text2: C.text2, text3: C.text3, navy: C.navy, cobalt: C.cobalt, coral: C.coral,
  okText: C.okText, warnBg: C.warnBg, warnLine: C.warnLine, warnText: C.warnText,
  alertBg: C.alertBg, alertText: C.alertText, onDark: hex('on-dark'),
};
void F;
const fontObj = (n) => ({ ascii: n, eastAsia: n, hAnsi: n, cs: n });
const FONT = fontObj(FORM.font.body.word);        // 본문 글꼴
const HFONT = fontObj(FORM.font.heading.word);    // 제목 글꼴
const fontFor = (key) => (TY[key].font === 'heading' ? HFONT : FONT);
const NUMFONT = FONT;
const KO = { value: 'ko-KR', eastAsia: 'ko-KR' };

const NONE = { style: BorderStyle.NONE, size: 0, color: 'auto' };
const NO_BORDERS = { top: NONE, bottom: NONE, left: NONE, right: NONE, insideHorizontal: NONE, insideVertical: NONE };
/** 선 — 색 hex(없으면 선 없음), 굵기는 px 수 또는 양식 길이 문자열. 1px = 6/8pt */
const line = (color, w = 1) => {
  if (!color) return NONE;
  const pxw = typeof w === 'number' ? w : dxa(w) / PX;
  return pxw > 0 ? { style: BorderStyle.SINGLE, size: Math.max(2, Math.round(pxw * 6)), color } : NONE;
};
const fill = (color) => ({ type: ShadingType.CLEAR, fill: color, color: 'auto' });

// ── 글자 조각 ─────────────────────────────────────────────────────────────
const CHIP_STYLE = { '': 'HctChip', warn: 'HctChipWarn', late: 'HctChipLate' };
const NB = ' ';

/** manifest 의 runs → TextRun[]. 줄바꿈("\n")은 break 로. */
function textRuns(rs, extra = {}) {
  const out = [];
  let brk = 0;
  for (const r of rs || []) {
    if (r.t === '\n') { brk += 1; continue; }
    const o = Object.assign({}, extra, { text: r.t });
    if (brk) { o.break = brk; brk = 0; }
    if (r.chip !== undefined) {
      o.text = NB + r.t + NB;
      o.style = CHIP_STYLE[r.chip] || 'HctChip';
    } else if (r.color === 'navy' && r.b) {
      o.style = 'HctKey';
    } else {
      if (r.b) o.bold = true;
      if (r.color) o.color = T[r.color] || undefined;
    }
    if (r.i) o.italics = true;
    out.push(new TextRun(o));
  }
  return out;
}

// 한글 · 숫자 사이 자동 틈은 문서 기본값(styles)에도 끄지만 LibreOffice 등은 문단 속성만 본다 — 문단마다 다시 적는다
const NOSPACE = { autoSpaceEastAsianText: false, autoSpaceLatinAndEastAsianText: false };
const para = (children, o = {}) => new Paragraph(Object.assign({ children }, NOSPACE, o));

// ── 블록 → Word ───────────────────────────────────────────────────────────
let stepsInstance = 0, bulletInstance = 0, orderedInstance = 0;

function cell(children, o = {}) {
  return new TableCell(Object.assign({ children: children.length ? children : [para([])] }, o));
}

function widthsFrom(pcts, n) {
  const known = pcts.filter((x) => x != null);
  let ws;
  if (known.length === n && n > 0) {
    const sum = known.reduce((a, b) => a + b, 0);
    ws = known.map((x) => Math.round((W * x) / sum));
  } else {
    const rest = 100 - known.reduce((a, b) => a + b, 0);
    const free = n - known.length;
    ws = pcts.map((x) => Math.round((W * (x != null ? x : rest / Math.max(free, 1))) / 100));
  }
  ws[ws.length - 1] += W - ws.reduce((a, b) => a + b, 0);
  return ws;
}

function table(b) {
  const n = Math.max(b.head.reduce((a, c) => a + (c.span || 1), 0),
    ...b.rows.map((r) => r.reduce((a, c) => a + (c.span || 1), 0)), 1);
  const pcts = b.head.length === n ? b.widths : new Array(n).fill(null);
  const ws = widthsFrom(pcts, n);
  const cy = dxa(TBL.cellPadding.y), cx = dxa(TBL.cellPadding.x);
  const margins = { top: cy, bottom: cy, left: cx, right: cx };
  const thRule = tok(TBL.headRule.color), tdRule = tok(TBL.rowRule);
  const spanW = (i, span) => ws.slice(i, i + span).reduce((a, x) => a + x, 0);
  const rows = [];
  const mk = (cells, head, last) => {
    let i = 0;
    return cells.map((c) => {
      const span = c.span || 1;
      const w = spanW(i, span);
      i += span;
      const borders = b.grid
        ? { top: head ? line(thRule, TBL.headRule.top) : line(tdRule), bottom: head ? line(thRule, TBL.headRule.bottom) : line(tdRule),
            left: line(head ? thRule : tdRule), right: line(head ? thRule : tdRule) }
        : { top: head ? line(thRule, TBL.headRule.top) : NONE, bottom: head ? line(thRule, TBL.headRule.bottom) : line(tdRule),
            left: NONE, right: NONE };
      void last;
      return cell([para(textRuns(c.runs, head ? { bold: true, color: tok(TBL.headColor) } : (c.num ? { font: NUMFONT, bold: true } : {})),
        { alignment: c.num ? AlignmentType.RIGHT : AlignmentType.LEFT, spacing: { after: 0 } })],   // 숫자 열은 머리도 오른쪽(HTML .num 과 같다)
      { width: { size: w, type: WidthType.DXA }, columnSpan: span > 1 ? span : undefined, margins, borders,
        shading: head && tok(TBL.headFill) ? fill(tok(TBL.headFill)) : undefined, verticalAlign: VerticalAlign.TOP });
    });
  };
  if (b.head.length) rows.push(new TableRow({ tableHeader: true, cantSplit: true, children: mk(b.head, true) }));
  b.rows.forEach((r, k) => rows.push(new TableRow({ cantSplit: true, children: mk(r, false, k === b.rows.length - 1) })));
  return [new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: ws, layout: TableLayoutType.FIXED,
    borders: NO_BORDERS, rows }), gap(dxa(SP.blockAfter) / PX)];
}

/** 표 뒤 간격. Word 는 표에 아래 여백이 없어 빈 문단으로 준다(높이 = px). */
function gap(px, keepNext = false) {
  return para([], { spacing: { before: 0, after: 0, line: Math.max(px * PX, 20), lineRule: LineRuleType.EXACT },
    style: 'HctGap', keepNext });
}

function meta(b) {
  const KW = dxa(META.labelWidth);
  const VW = Math.round((W - KW * 2) / 2);
  const ws = [KW, VW, KW, W - KW * 2 - VW];
  const rows = [];
  for (let i = 0; i < b.pairs.length; i += 2) {
    const pr = [b.pairs[i], b.pairs[i + 1] || ['', []]];
    const first = i === 0;
    const borders = { top: first ? line(tok(META.topRule.color), META.topRule.width) : NONE,
      bottom: line(tok(META.rowRule)), left: NONE, right: NONE };
    const margins = { top: 9 * PX, bottom: 9 * PX, left: 12 * PX, right: 12 * PX };
    const cells = [];
    pr.forEach(([k, v], j) => {
      cells.push(cell([para([new TextRun({ text: k, bold: true, color: tok(META.labelColor) })], { spacing: { after: 0 } })],
        { width: { size: ws[j * 2], type: WidthType.DXA }, borders, margins,
          shading: tok(META.labelFill) ? fill(tok(META.labelFill)) : undefined }));
      cells.push(cell([para(textRuns(v), { spacing: { after: 0 } })],
        { width: { size: ws[j * 2 + 1], type: WidthType.DXA }, borders, margins }));
    });
    rows.push(new TableRow({ cantSplit: true, children: cells }));
  }
  return [new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: ws, layout: TableLayoutType.FIXED,
    borders: NO_BORDERS, rows }), gap(4)];
}

function list(b) {
  if (b.legal) {
    // 조 · 항 · 호 번호는 글자로 — 개정 때 번호가 저절로 바뀌면 인용한 조문이 어긋난다. 모양은 양식 numbering.legal
    const circled = NUM.legal === 'circled';
    const label = (k) => (circled ? String.fromCharCode(0x2460 + Math.min(k, 19)) : NUM.legal.replace('{n}', String(k + 1)));
    return b.items.map((it, k) => para([new TextRun(circled ? { text: label(k) } : { text: label(k), bold: true, color: tok(TY.key.color), font: NUMFONT }),
      new TextRun({ text: '\t' }), ...textRuns(it)], {
      indent: { left: IND + 34 * PX, hanging: 34 * PX }, tabStops: [{ type: TabStopType.LEFT, position: IND + 34 * PX }],
      spacing: { after: k === b.items.length - 1 ? dxa(SP.blockAfter) : dxa(SP.listItemAfter) } }));
  }
  const ref = b.ordered ? 'hct-ordered' : 'hct-bullet';
  const instance = b.ordered ? ++orderedInstance : ++bulletInstance;
  return b.items.map((it, k) => para(textRuns(it), {
    numbering: { reference: ref, level: 0, instance },
    spacing: { after: k === b.items.length - 1 ? dxa(SP.blockAfter) : dxa(SP.listItemAfter) } }));
}

function callout(b) {
  // 1.58 — 가는 회청 테두리 + 아주 옅은 면(HTML .bd-callout 과 같다). 색은 머리 글자에만, 본문은 본문색
  const tone = { warn: [hex('form-rule'), T.alertText], danger: [hex('alert-line'), T.alertText],
    info: [hex('form-rule'), hex('deep')] }[b.kind] || [hex('form-rule'), T.alertText];
  const [ln, kc] = tone, bg = T.page, fg = tok(TY.body.color);
  const side = (space) => ({ style: BorderStyle.SINGLE, size: 6, color: ln, space });
  // 같은 테두리를 가진 문단은 Word 가 한 상자로 묶는다 — 라벨 문단과 본문 문단을 한 상자에
  const border = { top: side(9), bottom: side(9), left: side(12), right: side(12) };
  const base = { border, shading: fill(bg), indent: { left: 12 * 20 + 20, right: 12 * 20 + 20 } };
  const out = [];
  if (b.label) {
    out.push(para([new TextRun({ text: b.label, bold: true, color: kc })],
      Object.assign({}, base, { spacing: { after: 4 * PX }, keepNext: true })));
  }
  out.push(para(textRuns(b.runs, { color: fg }), Object.assign({}, base, { spacing: { after: 0 } })));
  out.push(gap(14));
  return out;
}

function steps(b) {
  const instance = ++stepsInstance;
  const out = [];
  b.items.forEach((it, k) => {
    const last = k === b.items.length - 1;
    const hasBody = (it.runs || []).length > 0;
    out.push(para(textRuns(it.title, { bold: true, color: NUM.steps === 'decimal' ? tok(TY.body.color) : T.navy }), {
      numbering: { reference: 'hct-steps', level: 0, instance }, keepNext: hasBody,
      spacing: { after: hasBody ? 2 * PX : (last ? 12 * PX : 14 * PX) } }));
    if (hasBody) {
      out.push(para(textRuns(it.runs), { indent: { left: IND + 40 * PX },
        spacing: { after: last ? 12 * PX : 14 * PX } }));
    }
  });
  return out;
}

function toc(b) {
  if (TOC.style === 'plain') {
    // 점선 · 쪽번호 없이 — 장 줄은 굵은 제목 글꼴, 항목은 들여 쓴 본문 글꼴
    return b.items.map((it, k) => para([new TextRun(it.sub ? { text: it.title } : { text: it.title, bold: true, font: HFONT })],
      // 목차는 한 덩어리 — HTML 뷰어처럼 쪽 사이에서 갈라지지 않게 마지막 줄까지 다음 줄과 붙인다
      { indent: { left: IND + (it.sub ? dxa('5mm') : 0) }, alignment: AlignmentType.LEFT, keepNext: k < b.items.length - 1, keepLines: true,
        spacing: { after: k === b.items.length - 1 ? 12 * PX : dxa(TOC.itemAfter) } }));
  }
  return b.items.map((it, k) => para([
    new TextRun({ text: it.title, bold: !it.sub, color: it.sub ? T.text2 : T.navy }),
    new TextRun({ text: '\t' }),
    new TextRun({ text: it.page, bold: true, color: T.navy, font: NUMFONT }),
  ], { indent: { left: IND + (it.sub ? 20 * PX : 0) }, keepNext: k < b.items.length - 1, keepLines: true,
    tabStops: [{ type: TabStopType.RIGHT, position: W, leader: 'dot' }],
    spacing: { after: k === b.items.length - 1 ? 12 * PX : 9 * PX } }));
}

function figure(b) {
  const inner = W - 2 * PX;
  const rows = [];
  if (b.img) {
    const buf = Buffer.from(b.img.data, 'base64');
    const dim = imgSize(buf, b.img.type) || { w: 1280, h: 720 };
    const wpx = Math.round(inner / PX);
    const hpx = Math.round((wpx * dim.h) / dim.w);
    rows.push(new TableRow({ children: [cell([para([new ImageRun({ type: b.img.type, data: buf,
      transformation: { width: wpx, height: hpx },
      altText: { title: b.alt || '그림', description: b.alt || '그림', name: 'figure' } })],
    { alignment: AlignmentType.CENTER, spacing: { after: 0, line: 240, lineRule: LineRuleType.AUTO } })],
    { width: { size: W, type: WidthType.DXA }, shading: fill(T.page), margins: { top: 0, bottom: 0, left: 0, right: 0 } })] }));
  } else {
    rows.push(new TableRow({ height: { value: 150 * PX, rule: HeightRule.ATLEAST }, children: [
      cell([para([new TextRun({ text: b.placeholder || '그림', color: T.text2 })], { alignment: AlignmentType.CENTER, spacing: { after: 0 } })],
        { width: { size: W, type: WidthType.DXA }, shading: fill(T.page), verticalAlign: VerticalAlign.CENTER })] }));
  }
  if (b.caption && b.caption.length) {
    rows.push(new TableRow({ cantSplit: true, children: [cell([para(textRuns(b.caption, { color: T.text2 }), { spacing: { after: 0 } })],
      { width: { size: W, type: WidthType.DXA }, margins: { top: 8 * PX, bottom: 8 * PX, left: 12 * PX, right: 12 * PX },
        borders: { top: line(tok(TBL.rowRule)), bottom: NONE, left: NONE, right: NONE } })] }));
  }
  return [new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: [W], layout: TableLayoutType.FIXED,
    borders: { top: line(tok(TBL.rowRule)), bottom: line(tok(TBL.rowRule)), left: line(tok(TBL.rowRule)), right: line(tok(TBL.rowRule)),
      insideHorizontal: line(tok(TBL.rowRule)), insideVertical: NONE }, rows }), gap(12)];
}

function sign(b) {
  if (!b.labels.length) b.labels = SIGN.labels;
  const n = Math.max(b.labels.length, 1);
  const G = dxa(SIGN.gap);
  const cw = Math.floor((W - G * (n - 1)) / n);
  const ws = [];
  for (let i = 0; i < n; i++) { ws.push(cw); if (i < n - 1 && G > 0) ws.push(G); }
  ws[ws.length - 1] += W - ws.reduce((a, x) => a + x, 0);
  const sr = tok(SIGN.rule);
  const box = { top: line(sr), bottom: line(sr), left: line(sr), right: line(sr) };
  const head = [], body = [];
  ws.forEach((w, i) => {
    const isGap = G > 0 && i % 2 === 1;
    const lab = b.labels[G > 0 ? i / 2 : i];
    head.push(cell(isGap ? [] : [para([new TextRun({ text: lab || '', bold: true, color: tok(SIGN.labelColor), size: SMALL })],
      { alignment: AlignmentType.CENTER, spacing: { after: 0 } })],
    { width: { size: w, type: WidthType.DXA }, borders: isGap ? { top: NONE, bottom: NONE, left: NONE, right: NONE } : box,
      shading: isGap || !tok(SIGN.labelFill) ? undefined : fill(tok(SIGN.labelFill)), margins: { top: 7 * PX, bottom: 7 * PX, left: 10 * PX, right: 10 * PX } }));
    body.push(cell([], { width: { size: w, type: WidthType.DXA },
      borders: isGap ? { top: NONE, bottom: NONE, left: NONE, right: NONE } : box }));
  });
  return [gap(20), new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: ws, layout: TableLayoutType.FIXED,
    borders: NO_BORDERS, rows: [new TableRow({ cantSplit: true, children: head }),
      new TableRow({ cantSplit: true, height: { value: dxa(SIGN.height), rule: HeightRule.EXACT }, children: body })] })];
}

/** 보고서 수치 타일 — 문서의 다른 표와 같은 짜임으로: 칸 위 머리 줄(지표 이름 · 머리 칸 색) · 아래 값(수치 · 증감 · 기준).
 *  면 · 빈 칸 없이 표 선만 — HTML 의 .x-kpis 와 같다. 글자 순서도 HTML 과 같게 지표마다 한 칸에 이름 → 값. */
function kpis(b) {
  const n = Math.max(b.items.length, 1);
  const cw = Math.floor(W / n);
  const ws = new Array(n).fill(cw);
  ws[n - 1] += W - cw * n;
  const thRule = tok(TBL.headRule.color), tdRule = tok(TBL.rowRule);
  const px = dxa(TBL.cellPadding.x), py = dxa(TBL.cellPadding.y);
  const ind = { left: px, right: px };
  const cells = b.items.map((it, i) => cell([
    // 머리 줄 — 문단 음영 · 아래 선으로 표 머리 칸과 같게(칸 좌우 여백 0, 글은 들여쓰기로)
    para([new TextRun({ text: it.k, bold: true, color: tok(TBL.headColor) })],
      { indent: ind, alignment: AlignmentType.LEFT, shading: tok(TBL.headFill) ? fill(tok(TBL.headFill)) : undefined,
        // 음영을 칸 끝까지 — 머리 칸 색의 가는 좌우 · 위 선을 여백만큼 띄워 그 사이를 음영이 채우게 한다
        border: { bottom: Object.assign({}, line(thRule, TBL.headRule.bottom), { space: Math.round(py / 20) }),
                  top: Object.assign({}, line(tok(TBL.headFill) || 'FFFFFF', 0.5), { space: Math.round(py / 20) }),
                  left: Object.assign({}, line(tok(TBL.headFill) || 'FFFFFF', 0.5), { space: Math.round(px / 20) }),
                  right: Object.assign({}, line(tok(TBL.headFill) || 'FFFFFF', 0.5), { space: Math.round(px / 20) }) },
        spacing: { before: 0, after: 0 } }),
    para([new TextRun({ text: it.v, bold: true, size: hp(14) }), new TextRun({ text: ' ' + (it.unit || ''), color: T.text2 })],
      { indent: ind, alignment: AlignmentType.LEFT, spacing: { before: 8 * PX, after: 2 * PX, line: 240, lineRule: LineRuleType.AUTO } }),
    para([new TextRun({ text: it.delta + '  ', bold: true, color: it.bad ? T.alertText : tok(TY.body.color) }),
      new TextRun({ text: it.note, color: T.text2 })], { indent: ind, alignment: AlignmentType.LEFT, spacing: { before: 0, after: 8 * PX } }),
  ], { width: { size: ws[i], type: WidthType.DXA }, margins: { top: 0, bottom: 0, left: 0, right: 0 },
    borders: { top: line(thRule, TBL.headRule.top), bottom: line(tdRule), left: i ? line(tdRule) : NONE, right: NONE } }));
  return [new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: ws, layout: TableLayoutType.FIXED,
    rows: [new TableRow({ cantSplit: true, children: cells })] }), gap(12)];
}

/** 보고서 가로 막대 — 막대 칸 안의 2칸 표(채움 · 트랙). 값을 고치면 너비는 손으로 맞춘다. */
function bars(b) {
  const KW = 112 * PX, VW = 56 * PX, G = 10 * PX;
  const BW = W - KW - VW - G * 2;
  const ws = [KW, G, BW, G, VW];
  const tiny = () => para([new TextRun({ text: '', size: 2 })],
    { spacing: { before: 0, after: 0, line: 20, lineRule: LineRuleType.EXACT } });
  const out = [];
  if (b.title) out.push(para([new TextRun({ text: b.title, bold: true })], { spacing: { before: 4 * PX, after: 2 * PX }, keepNext: true }));
  if (b.sub) out.push(para([new TextRun({ text: b.sub, color: T.text2 })], { spacing: { after: 10 * PX }, keepNext: true }));
  const rows = b.items.map((it) => {
    const pct = Math.max(0, Math.min(100, Number(it.pct) || 0));
    const fw = Math.round((BW * pct) / 100);
    const parts = [];
    if (fw >= 30) parts.push([fw, it.main ? T.cobalt : hex('mark-mute')]);
    if (BW - fw >= 30) parts.push([BW - parts.reduce((a, p) => a + p[0], 0), T.track]);
    const bar = new Table({ width: { size: BW, type: WidthType.DXA }, columnWidths: parts.map((p) => p[0]),
      layout: TableLayoutType.FIXED, borders: NO_BORDERS,
      rows: [new TableRow({ height: { value: 16 * PX, rule: HeightRule.EXACT }, children: parts.map(([w, c]) =>
        cell([tiny()], { width: { size: w, type: WidthType.DXA }, shading: fill(c),
          margins: { top: 0, bottom: 0, left: 0, right: 0 } })) })] });
    const m0 = { top: 4 * PX, bottom: 4 * PX, left: 0, right: 0 };
    return new TableRow({ cantSplit: true, children: [
      cell([para([new TextRun({ text: it.k, color: T.text2 })], { spacing: { after: 0 } })],
        { width: { size: KW, type: WidthType.DXA }, margins: m0, verticalAlign: VerticalAlign.CENTER }),
      cell([], { width: { size: G, type: WidthType.DXA } }),
      cell([bar, tiny()], { width: { size: BW, type: WidthType.DXA }, margins: m0, verticalAlign: VerticalAlign.CENTER }),
      cell([], { width: { size: G, type: WidthType.DXA } }),
      cell([para([new TextRun({ text: it.v, bold: true, font: NUMFONT })], { alignment: AlignmentType.RIGHT, spacing: { after: 0 } })],
        { width: { size: VW, type: WidthType.DXA }, margins: m0, verticalAlign: VerticalAlign.CENTER }),
    ] });
  });
  out.push(new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: ws, layout: TableLayoutType.FIXED,
    borders: NO_BORDERS, rows }));
  out.push(gap(12));
  return out;
}

function imgSize(buf, type) {
  if (type === 'png' && buf.readUInt32BE(0) === 0x89504e47) return { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) };
  if (type === 'jpg') {
    let i = 2;
    while (i < buf.length) {
      if (buf[i] !== 0xff) return null;
      const m = buf[i + 1];
      if (m >= 0xc0 && m <= 0xc3) return { h: buf.readUInt16BE(i + 5), w: buf.readUInt16BE(i + 7) };
      i += 2 + buf.readUInt16BE(i + 2);
    }
  }
  return null;
}

// ── 장 제목 ───────────────────────────────────────────────────────────────
// 양식 type.h1.numeral 이 roman 이면 「1. 요약」→ 「Ⅰ」, style 이 box 면 번호 칸 · 제목 칸 상자(doc-viewer.js 와 같은 규칙)
function roman(n) {
  if (n >= 1 && n <= 12) return String.fromCharCode(0x215F + n);
  let r = '';
  [[10, 'X'], [9, 'IX'], [5, 'V'], [4, 'IV'], [1, 'I']].forEach(([v, c]) => { while (n >= v) { r += c; n -= v; } });
  return r;
}
function splitNumber(runs) {
  const text = (runs || []).map((r) => r.t).join('');
  const m = /^\s*(\d+|[Ⅰ-Ⅻ]+)[.)]?\s+([\s\S]*)$/.exec(text);
  if (!m || (runs || []).length !== 1) return null;
  let num = m[1];
  if (TY.h1.numeral === 'roman' && /^\d+$/.test(num)) num = roman(parseInt(num, 10));
  return { num, title: m[2], changed: num !== m[1] };
}
function h1(b, first, pb) {
  const sp = first ? { before: 0, after: dxa(SP.h1After) } : undefined;
  const sn = splitNumber(b.runs);
  if (TY.h1.style !== 'box') {
    const runs = sn && sn.changed ? [{ t: `${sn.num}. ${sn.title}` }] : b.runs;
    return [para(textRuns(runs), Object.assign({ heading: D.HeadingLevel.HEADING_1, spacing: sp }, pb))];
  }
  // 1.58 — 표가 아니라 문단 하나(HTML 과 같은 모양): 위아래 선 · 번호 꼬리표(글자 음영) · 제목.
  // 문단이라 MS Word · LibreOffice · 한컴 어디서나 「다음 문단과 함께」가 지켜져 제목만 쪽 끝에 남지 않는다
  const bx = TY.h1.box;
  const rw = Math.max(2, Math.round(ptOf(bx.rule.width) * 8));
  const rule = { style: BorderStyle.SINGLE, size: rw, color: tok(bx.rule.color), space: 5 };
  const size = hpOf(TY.h1.size);
  const runs = [];
  if (sn) {
    runs.push(new TextRun({ text: '\u2002' + sn.num + '\u2002', bold: true, font: HFONT, size,
      color: tok(bx.numberColor || TY.h1.color), shading: tok(bx.fill) ? fill(tok(bx.fill)) : undefined }));
    runs.push(new TextRun({ text: '\u2003', size }));
  }
  runs.push(...textRuns(sn ? [{ t: sn.title }] : b.runs, { characterSpacing: 20 }));
  return [para(runs, Object.assign({ heading: D.HeadingLevel.HEADING_1, keepNext: true, keepLines: true,
    alignment: AlignmentType.LEFT, indent: { left: 0 }, border: { top: rule, bottom: rule },
    spacing: { before: first ? 0 : dxa(SP.h1Before), after: dxa(SP.h1After) } }, pb))];
}

/** 블록 → Word 요소. brk 는 「앞에서 쪽 나눔」 — HTML 의 쪽과 같은 자리에서 넘긴다. */
function blocks(b, first, brk, afterHead = false) {
  const pb = brk ? { pageBreakBefore: true } : {};
  const top = first ? { before: 0 } : {};
  const ind = IND ? { indent: { left: IND } } : {};
  switch (b.t) {
    case 'title': return [para(textRuns(b.runs), Object.assign({ style: 'Title' }, pb))];
    case 'subtitle': return [para(textRuns(b.runs), Object.assign({ style: 'Subtitle' }, pb))];
    case 'h1': return h1(b, first, pb);
    case 'h2': return [para(textRuns(b.runs), Object.assign({ heading: D.HeadingLevel.HEADING_2,
      spacing: first ? { before: 0, after: dxa(SP.h2After) } : undefined }, pb))];
    // 제목 바로 뒤의 도입 문단은 다음 블록과 붙인다 — HTML 뷰어와 같이 「제목 → 한 줄 설명 → 표」를 한 덩어리로
    case 'p': return [para(textRuns(b.runs), Object.assign({ spacing: Object.assign({ after: dxa(SP.paraAfter) }, top),
      keepNext: afterHead, keepLines: true }, ind, pb))];
    default: {
      const els = ({ meta, list, table, callout, steps, toc, figure, sign, kpis, bars })[b.t];
      if (!els) {
        console.error(`주의: 모르는 블록 ${b.t} — 건너뜀`);
        return [];
      }
      const out = els(b);
      // 표 · 상자로 시작하는 쪽은 쪽 나눔 문단을 앞에 둔다(줄 높이 1pt)
      if (brk) out.unshift(para([new D.PageBreak()], { spacing: { before: 0, after: 0, line: 20, lineRule: LineRuleType.EXACT } }));
      return out;
    }
  }
}

// ── 표지 ──────────────────────────────────────────────────────────────────
// 양식 cover — 오른쪽 위 로고 · 문서명 · 부제 · 두 줄 선 · 아래 문서 정보 줄 · 회사명(가운데 정렬). HTML 뷰어와 같은 짜임.
// 한 칸 표 두 줄(높이 고정)로 쪽을 채운다 — 아래 줄은 아래 맞춤이라 회사명이 쪽 아래에 앉는다
function coverPage() {
  const c = COVER;
  const t = c.title, r = c.rule;
  const tSize = ptOf(t.size);
  const bodyH = PAGE_H - (dxa(MG.top) + headBlock) - (dxa(MG.bottom) + footBlock);
  const ruleW = /%$/.test(r.width) ? Math.round((W * parseFloat(r.width)) / 100) : dxa(r.width);
  const side = Math.max(0, Math.round((W - ruleW) / 2));
  const kids = [];
  // 로고 — 오른쪽 위
  if (brand.logoPathOnLight) {
    const buf = fs.readFileSync(brand.logoPathOnLight);
    const ratio = (buf.readUInt32BE(16) / buf.readUInt32BE(20)) || 3;
    const h = Math.round(dxa(c.logo.height) / PX);
    kids.push(para([new ImageRun({ type: 'png', data: buf, transformation: { width: Math.round(h * ratio), height: h },
      altText: { title: VALUES.company || '로고', description: `${VALUES.company} 로고`, name: 'cover-logo' } })],
    { alignment: AlignmentType.RIGHT, spacing: { before: 0, after: 0 } }));
  }
  kids.push(para([new TextRun({ text: man.title || '', size: hp(tSize), bold: t.weight >= 600, color: tok(t.color || 'text'),
    font: t.font === 'heading' ? HFONT : FONT })],
  { alignment: AlignmentType.CENTER, indent: { left: Math.round(W * 0.075), right: Math.round(W * 0.075) },
    spacing: { before: dxa(t.top), after: 0, line: 312, lineRule: LineRuleType.AUTO } }));
  if (man.subtitle) {
    kids.push(para([new TextRun({ text: man.subtitle, size: hpOf(c.subtitle.size), color: tok(c.subtitle.color) })],
      { alignment: AlignmentType.CENTER, spacing: { before: dxa(c.subtitle.gap), after: 0 } }));
  }
  // 두 줄 선 — 굵은 선 문단 + (간격) + 가는 선 문단, 폭은 rule.width
  const bline = (st) => ({ style: BorderStyle.SINGLE, size: Math.min(96, Math.max(2, Math.round(ptOf(st.width) * 8))), color: tok(st.color), space: 0 });
  kids.push(para([], { indent: { left: side, right: side }, border: { bottom: bline(r.thick) },
    spacing: { before: 0, after: 0, line: dxa(r.gap), lineRule: LineRuleType.EXACT } }));
  kids.push(para([], { indent: { left: side, right: side }, border: { bottom: bline(r.thin) },
    spacing: { before: 0, after: 0, line: Math.max(20, dxa(r.space)), lineRule: LineRuleType.EXACT } }));
  const row1H = (brand.logoPathOnLight ? dxa(c.logo.height) + 60 : 0) + dxa(t.top) + Math.round(tSize * 20 * 1.3 * 2)
    + (man.subtitle ? dxa(c.subtitle.gap) + Math.round(ptOf(c.subtitle.size) * 20 * 1.6) : 0) + dxa(r.gap) + dxa(r.space) + 300;
  const mv = { docNo: VALUES.docNo, dept: man.dept || '', date: man.date || '' };
  const metaTxt = String(c.meta.text || '{docNo}').split(' · ')
    .map((p) => p.replace(/\{(\w+)\}/g, (m, k) => mv[k] || '').trim()).filter(Boolean).join(' · ');
  const bottom = [];
  if (metaTxt) bottom.push(para([new TextRun({ text: metaTxt, size: hpOf(c.meta.size), color: tok(c.meta.color) })],
    { alignment: AlignmentType.CENTER, spacing: { before: 0, after: dxa(c.company.gap) } }));
  bottom.push(para([new TextRun({ text: String(c.company.text || '{company}').replace('{company}', VALUES.company),
    size: hpOf(c.company.size), bold: (c.company.weight || 400) >= 600, color: tok(c.company.color || 'text'),
    font: c.company.font === 'heading' ? HFONT : FONT })],
  { alignment: AlignmentType.CENTER, spacing: { before: 0, after: dxa(c.company.bottom), line: 240, lineRule: LineRuleType.AUTO } }));
  const noB = { top: NONE, bottom: NONE, left: NONE, right: NONE };
  const m0 = { top: 0, bottom: 0, left: 0, right: 0 };
  return [new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: [W], layout: TableLayoutType.FIXED, borders: NO_BORDERS,
    rows: [
      new TableRow({ height: { value: row1H, rule: HeightRule.EXACT }, children: [cell(kids, { width: { size: W, type: WidthType.DXA }, borders: noB, margins: m0 })] }),
      // 머리글이 계산보다 조금만 커도 표지가 두 쪽으로 넘친다 — 남는 높이의 88% 만 쓴다
      new TableRow({ height: { value: Math.max(1000, Math.round((bodyH - row1H) * 0.88)), rule: HeightRule.EXACT },
        children: [cell(bottom, { width: { size: W, type: WidthType.DXA }, borders: noB, margins: m0, verticalAlign: VerticalAlign.BOTTOM })] }),
    ] })];
}

// ── 머리말 · 꼬리말 ───────────────────────────────────────────────────────
// 양식 header.left/right 와 footer.left/right 로 짠다. 바닥글 글은 {company} {title} {docNo} {page} {pages} 를 채운다.
const small = { size: SMALL, color: tok(HD.color) };
const VALUES = {
  company: brand.company || man.company || '', title: man.title || '', docNo: man.docNo || '',
};
function headItem(kind, style) {
  if (kind === 'logo') {
    if (brand.logoPathOnLight) {
      const buf = fs.readFileSync(brand.logoPathOnLight);
      const ratio = (buf.readUInt32BE(16) / buf.readUInt32BE(20)) || 3;
      const h = Math.round(dxa(HD.logoHeight) / PX);
      return [new ImageRun({ type: 'png', data: buf, transformation: { width: Math.round(h * ratio), height: h },
        altText: { title: VALUES.company || '로고', description: `${VALUES.company} 로고`, name: 'logo' } })];
    }
    return [new TextRun({ text: brand.wordmark || VALUES.company, bold: true, color: tok(TY.key.color), size: hp(11) })];
  }
  if (kind === 'none' || !VALUES[kind]) return [];
  if (kind === 'title' && HD.layout === 'split') {
    // 좌우 머리말의 문서명 — header.title 의 글꼴 · 크기 · 굵기 · 색(HTML 의 .bd-head .bd-doctitle 과 같다)
    const ht = HD.title || {};
    return [new TextRun({ text: VALUES.title, bold: (ht.weight || 700) >= 600, size: hp(ptOf(ht.size || '9pt')),
      color: tok(ht.color || 'text'), font: ht.font === 'body' ? FONT : HFONT,
      characterSpacing: Math.round(parseFloat(ht.letterSpacing || '0') * ptOf(ht.size || '9pt') * 20) })];
  }
  return [new TextRun(Object.assign({ text: VALUES[kind], bold: kind === 'docNo', font: NUMFONT }, style))];
}
/** 바닥글 글 틀 → TextRun[]. {company} 는 굵게(머리말 · 꼬리말의 회사명 표시), {page} {pages} 는 필드 */
function pattern(tpl, style) {
  const out = [];
  for (const part of String(tpl || '').split(/(\{[a-zA-Z]+\})/).filter(Boolean)) {
    const m = /^\{([a-zA-Z]+)\}$/.exec(part);
    if (!m) { out.push(new TextRun(Object.assign({}, style, { text: part }))); continue; }
    const k = m[1];
    if (k === 'page') out.push(new TextRun(Object.assign({}, style, { children: [PageNumber.CURRENT], bold: true, font: NUMFONT })));
    else if (k === 'pages') out.push(new TextRun(Object.assign({}, style, { children: [PageNumber.TOTAL_PAGES_IN_SECTION], bold: true, font: NUMFONT })));
    else if (k === 'company') out.push(new TextRun(Object.assign({}, style, { text: VALUES.company, bold: true, color: tok('text-2') })));
    else out.push(new TextRun(Object.assign({}, style, { text: VALUES[k] || '' })));
  }
  return out;
}
const rule = (name, pos) => (tok(name) ? { [pos]: { style: BorderStyle.SINGLE, size: 6, color: tok(name),
  space: Math.floor(dxa(pos === 'bottom' ? HD.padding : FT.padding) / 20) } } : undefined);
/** 띠 하나 → 문단 테두리. 굵기 mm → 1/8pt (Word 상한 12pt) */
const bandBorder = (st, space) => ({ style: BorderStyle.SINGLE, size: Math.min(96, Math.max(2, Math.round(ptOf(st.width) * 8))),
  color: tok(st.color), space: Math.max(0, Math.round(space)) });
/** 띠 목록을 문단 테두리로 — 첫 띠는 머리말 문단에, 나머지는 띠 사이 간격만큼 높이를 준 빈 문단에 단다 */
function bandParas(list, pos) {
  const out = [];
  let gapPt = 0;
  const items = pos === 'top' ? [...list].reverse() : list;
  items.forEach((st) => {
    if (st.gap) { gapPt += ptOf(st.gap); return; }
    out.push({ st, gapPt });
    gapPt = 0;
  });
  return out;
}
function headerParas() {
  const pad = ptOf(HD.padding);
  const kids = [...headItem(HD.left, small)];
  const tabs = [{ type: TabStopType.RIGHT, position: W }];
  if (HD.layout === 'logo-title') {
    // 가운데 문서명 — 글자 사이를 header.title.letterSpacing 만큼 벌린다(긴 제목은 좁게)
    const ht = HD.title;
    const long = VALUES.title.replace(/\s/g, '').length > (ht.spaceUpTo || 6);
    const size = ptOf(ht.size);
    const ls = long ? 0.04 : parseFloat(ht.letterSpacing);
    tabs.unshift({ type: TabStopType.CENTER, position: Math.round(W / 2) });
    kids.push(new TextRun({ text: '\t' }));
    kids.push(new TextRun({ text: VALUES.title, bold: ht.weight >= 600, size: hp(size), color: tok(TY.body.color),
      font: ht.font === 'heading' ? HFONT : FONT, characterSpacing: Math.round(ls * size * 20) }));
  }
  kids.push(new TextRun({ text: '\t' }), ...headItem(HD.right, small));
  const bands = HD.bands || { top: [], bottom: [] };
  const top = bandParas(bands.top || [], 'top');
  const bot = bandParas(bands.bottom || [], 'bottom');
  const border = {};
  if (top.length) border.top = bandBorder(top[0].st, pad);
  if (bot.length) border.bottom = bandBorder(bot[0].st, pad);
  if (!top.length && !bot.length && rule(HD.rule, 'bottom')) Object.assign(border, rule(HD.rule, 'bottom'));
  const main = para(kids, { tabStops: tabs, border, alignment: AlignmentType.LEFT,
    spacing: { after: 0, line: 240, lineRule: LineRuleType.AUTO } });
  const thin = (st, g, pos) => para([], { border: { [pos]: bandBorder(st, 0) },
    spacing: { before: 0, after: 0, line: Math.max(20, Math.round(g * 20)), lineRule: LineRuleType.EXACT } });
  const before = top.slice(1).reverse().map((x) => thin(x.st, x.gapPt, 'top'));
  const after = bot.slice(1).map((x) => thin(x.st, x.gapPt, 'bottom'));
  return [...before, main, ...after];
}
function footerPara() {
  const st = { size: SMALL, color: tok(FT.color) };
  if (FT.font === 'body' || FT.font === 'heading') st.font = FT.font === 'body' ? FONT : HFONT;   // 꼬리말 글꼴 — 양식 footer.font
  return para([...pattern(FT.left, st), new TextRun({ text: '\t' }), ...pattern(FT.right, st)],
    { tabStops: [{ type: TabStopType.RIGHT, position: W }], border: rule(FT.rule, 'top'),
      spacing: { after: 0, line: 240, lineRule: LineRuleType.AUTO } });
}

// ── 스타일 · 번호 ─────────────────────────────────────────────────────────
const chipRun = (bg, ln, fg) => ({ size: SMALL, bold: true, color: fg, shading: fill(bg),
  border: { style: BorderStyle.SINGLE, size: 4, color: ln, space: 0 } });
const bar = TY.h1.bar || {};
const barW = bar.width ? dxa(bar.width) / PX : 0;
const h1Para = { spacing: { before: dxa(SP.h1Before), after: dxa(SP.h1After) }, keepNext: true, keepLines: true };
if (barW > 0 && tok(bar.color)) {
  // HTML 의 왼쪽 굵은 표시 — 굵기 px → 1/8pt, 글자와의 간격 12px
  h1Para.border = { left: { style: BorderStyle.SINGLE, size: Math.round(barW * 6), color: tok(bar.color), space: 9 } };
  h1Para.indent = { left: 12 * PX + 60 };
}
const titleAlign = TY.title.align === 'center' ? AlignmentType.CENTER : AlignmentType.LEFT;
const STEP_FORMAT = { decimalEnclosedCircle: LevelFormat.DECIMAL_ENCLOSED_CIRCLE, decimal: LevelFormat.DECIMAL }[NUM.steps]
  || LevelFormat.DECIMAL_ENCLOSED_CIRCLE;
// 머리말 높이 — blue-doc.css 의 .bd-head 와 같다. 띠가 있으면 위아래 띠 + 안쪽 여백, 없으면 로고 + 아래 여백 + 선
const bandH = (list) => (list || []).reduce((a, st) => a + dxa(st.width || st.gap), 0);
const HB = HD.bands || {};
const headBlock = (bandH(HB.top) || bandH(HB.bottom))
  ? bandH(HB.top) + dxa(HD.padding) * 2 + dxa(HD.logoHeight) + bandH(HB.bottom) + dxa(HD.gap)
  : dxa(HD.logoHeight) + dxa(HD.padding) + 2 * PX + dxa(HD.gap);
const HAS_FOOT = Boolean(FT.left || FT.right);
const footBlock = HAS_FOOT ? dxa(FT.padding) + dxa(FT.gap) + 1 * PX : 0;

// ── 본문 ──────────────────────────────────────────────────────────────────
// 쪽 나눔 — 양식 page.breaks 가 authored 면 HTML 의 쪽 경계에서, flow 면 Word 가 흘려 나눈다
const body = [];
const withCover = (COVER.mode === 'always' && man.cover !== 'no') || (COVER.mode === 'opt-in' && man.cover === 'yes');
const cover = withCover ? coverPage() : null;
let prevT = '';
man.pages.forEach((pg, pi) => {
  pg.blocks.forEach((b, bi) => {
    // 표지는 따로 구역을 두므로 본문 첫 블록 앞에 쪽 나눔을 넣지 않는다
    const pageStart = bi === 0 && pi > 0 && !FLOW;
    body.push(...blocks(b, bi === 0 && (pi === 0 || !FLOW), pageStart, prevT === 'h1' || prevT === 'h2'));
    prevT = b.t;
  });
});

const PAGE_PROPS = { size: { width: PAGE_W, height: PAGE_H },
  margin: { top: dxa(MG.top) + headBlock, bottom: dxa(MG.bottom) + footBlock, left: dxa(MG.left), right: dxa(MG.right),
    header: dxa(MG.top), footer: dxa(MG.bottom) } };

const doc = new Document({
  creator: VALUES.company,
  title: VALUES.title,
  description: `${VALUES.docNo} — HTML 원본에서 만든 Word 판(양식 ${FORM.id}). 내용을 고치면 HTML 원본도 함께 고친다.`,
  styles: {
    default: {
      document: { run: { font: FONT, size: hpOf(TY.body.size), color: tok(TY.body.color), language: KO },
        // 한글과 숫자 · 영문 사이에 Word 가 저절로 넣는 틈을 끈다 — 「9월」이 「9 월」로 벌어진다
        paragraph: { spacing: { after: 0, line: LINE, lineRule: LineRuleType.AT_LEAST },
          alignment: JUSTIFY ? AlignmentType.JUSTIFIED : AlignmentType.LEFT,
          autoSpaceEastAsianText: false, autoSpaceLatinAndEastAsianText: false } },
      title: { run: { font: fontFor('title'), size: hpOf(TY.title.size), bold: TY.title.weight >= 600, color: tok(TY.title.color) },
        paragraph: { alignment: titleAlign, spacing: { before: 0, after: dxa(SP.titleAfter), line: 240, lineRule: LineRuleType.AUTO }, keepNext: true } },
      heading1: { run: { font: fontFor('h1'), size: hpOf(TY.h1.size), bold: true, color: tok(TY.h1.color) }, paragraph: h1Para },
      heading2: { run: { font: fontFor('h2'), size: hpOf(TY.h2.size), bold: TY.h2.weight >= 600, color: tok(TY.h2.color) },
        paragraph: { spacing: { before: dxa(SP.h2Before), after: dxa(SP.h2After) }, keepNext: true, keepLines: true,
          alignment: AlignmentType.LEFT, indent: IND ? { left: IND } : undefined } },
    },
    paragraphStyles: [
      { id: 'Subtitle', name: 'Subtitle', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: fontFor('subtitle'), size: hpOf(TY.subtitle.size), color: tok(TY.subtitle.color) },
        paragraph: { alignment: titleAlign, spacing: { after: dxa(SP.subtitleAfter) } } },
      { id: 'HctGap', name: 'HCT 간격', basedOn: 'Normal', run: { size: 2 } },
    ],
    characterStyles: [
      { id: 'HctKey', name: 'HCT 강조어', basedOn: 'DefaultParagraphFont', quickFormat: true, run: { bold: true, color: tok(TY.key.color) } },
      { id: 'HctChip', name: 'HCT 칩', basedOn: 'DefaultParagraphFont', quickFormat: true, run: chipRun(T.card, T.chipLine, T.text2) },
      { id: 'HctChipWarn', name: 'HCT 칩 주의', basedOn: 'DefaultParagraphFont', quickFormat: true, run: chipRun(T.card, hex('alert-line'), T.alertText) },
      { id: 'HctChipLate', name: 'HCT 칩 위험', basedOn: 'DefaultParagraphFont', quickFormat: true, run: chipRun(T.card, T.alertText, T.alertText) },
    ],
  },
  numbering: { config: [
    // 글머리 — 양식 list.marker · textIndent(글 시작) · hang(표시는 글보다 이만큼 왼쪽). 들여쓰기 space.indent 를 더한다
    { reference: 'hct-bullet', levels: [{ level: 0, format: LevelFormat.BULLET, text: LST.marker, alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: IND + dxa(LST.textIndent), hanging: dxa(LST.hang) } },
        run: { color: LST.marker === '•' ? T.text2 : tok(TY.body.color), font: FONT } } }] },
    { reference: 'hct-ordered', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: IND + 24 * PX, hanging: 24 * PX } }, run: { bold: true, color: tok(TY.key.color), font: NUMFONT } } }] },
    // 절차 단계 — 양식 word.steps. 기본은 원 숫자(①②③, 20단계까지) — HTML 의 남색 원 번호
    { reference: 'hct-steps', levels: [{ level: 0, format: STEP_FORMAT, text: STEP_FORMAT === LevelFormat.DECIMAL ? '%1.' : '%1',
      alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: IND + 40 * PX, hanging: 40 * PX }, tabStops: [{ type: TabStopType.LEFT, position: IND + 40 * PX }] },
        run: STEP_FORMAT === LevelFormat.DECIMAL ? { bold: true, color: tok(TY.body.color) } : { bold: true, color: tok(TY.key.color), size: hp(14) } } }] },
  ] },
  // 표지는 따로 구역 — 머리말 · 꼬리말 없음. 본문 구역은 쪽번호 1부터, 전체 쪽수는 본문 구역 쪽수(HTML 뷰어와 같다)
  sections: [
    ...(cover ? [{
      properties: { page: PAGE_PROPS },
      headers: { default: new Header({ children: [para([])] }) },
      footers: { default: new Footer({ children: [para([])] }) },
      children: cover,
    }] : []),
    {
      properties: { page: Object.assign({ pageNumbers: { start: 1 } }, PAGE_PROPS) },
      headers: { default: new Header({ children: headerParas() }) },
      footers: { default: new Footer({ children: HAS_FOOT ? [footerPara()] : [para([])] }) },
      children: body,
    },
  ],
});

Packer.toBuffer(doc).then((buf) => {
  fs.mkdirSync(path.dirname(path.resolve(OUT)), { recursive: true });
  fs.writeFileSync(OUT, buf);
}).catch((e) => { console.error(e); process.exit(1); });
