'use strict';
/**
 * 스타일 H 의 사선 패널 · 머리 탭을 PNG 로 그린다 — PowerPoint 는 그라데이션 면을 못 받으므로 그림으로 깐다.
 *
 * 모양과 색은 assets/blue-style.css 「H」 와 같은 조리법이다.
 *   바탕 --br-deep
 *   + 원형 그라데이션 1  --br-cobalt 88% → 투명(반지름 62%) · 상자 폭 110% × 높이 95%
 *   + 원형 그라데이션 2  --br-data-3 30% → 투명(반지름 60%) · 상자 폭 60% × 높이 55%
 *   사선 기울기 하나 — 가로 이동 = 세로 높이 × 0.3
 * 색은 tokens.js(= blue-report.css)에서 읽는다. 여기 hex 를 적지 않는다.
 * 외부 모듈 없이 zlib 로 PNG 를 쓴다.
 */
const fs = require('fs');
const path = require('path');
const zlib = require('zlib');
const { C, RAW } = require('./tokens');

const rgb = (h) => [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16));
const tok = (name) => rgb(String(RAW[name]).replace('#', '').trim());

const DEEP = rgb(C.deep), CI = rgb(C.cobalt), RAY = tok('data-3');
const W = 1920, H = 1080, K = 0.3;

/* ── PNG ─────────────────────────────────────────────────────────── */
const CRC = (() => {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; }
  return t;
})();
function crc32(buf) { let c = 0xffffffff; for (const b of buf) c = CRC[(c ^ b) & 0xff] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0; }
function chunk(type, data) {
  const len = Buffer.alloc(4); len.writeUInt32BE(data.length);
  const td = Buffer.concat([Buffer.from(type, 'ascii'), data]);
  const crc = Buffer.alloc(4); crc.writeUInt32BE(crc32(td));
  return Buffer.concat([len, td, crc]);
}
function png(w, h, rgba) {
  const raw = Buffer.alloc((w * 4 + 1) * h);
  for (let y = 0; y < h; y++) { raw[y * (w * 4 + 1)] = 0; rgba.copy(raw, y * (w * 4 + 1) + 1, y * w * 4, (y + 1) * w * 4); }
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(w, 0); ihdr.writeUInt32BE(h, 4); ihdr[8] = 8; ihdr[9] = 6; ihdr[10] = 0; ihdr[11] = 0; ihdr[12] = 0;
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk('IHDR', ihdr),
    chunk('IDAT', zlib.deflateSync(raw, { level: 9 })), chunk('IEND', Buffer.alloc(0))]);
}

/* ── 깊은 면 한 가지 조리법 — 상자(bx, by, bw, bh) 기준 ─────────────────── */
function deepAt(x, y, box, cx, cy, cx2, cy2) {
  const [bx, by, bw, bh] = box;
  const g = (px, py, rx, ry, stop, a0) => {
    const t = Math.hypot((x - (bx + px * bw)) / (rx * bw), (y - (by + py * bh)) / (ry * bh));
    return t >= stop ? 0 : a0 * (1 - t / stop);
  };
  let c = DEEP.slice();
  const a2 = g(cx2, cy2, 0.60, 0.55, 0.60, 0.30);
  c = c.map((v, i) => v * (1 - a2) + RAY[i] * a2);
  const a1 = g(cx, cy, 1.10, 0.95, 0.62, 0.88);
  return c.map((v, i) => v * (1 - a1) + CI[i] * a1);
}

/** 사선 패널 — side 'r' (표지 · 마무리) · 'l' (간지 · 부록 간지). 밝은 부분은 투명, 패널 옆 실선 포함 */
function panel(side) {
  const buf = Buffer.alloc(W * H * 4);
  const slope = K * H;                                   // 324px
  const R = side === 'r';
  const box = R ? [0.508 * W, 0, W - 0.508 * W, H] : [0, 0, 0.492 * W, H];
  const [cx, cy, cx2, cy2] = R ? [0.72, 0.62, 0.84, 0.44] : [0.28, 0.62, 0.40, 0.44];
  const hairTop = R ? 0.6435 * W : 0.5245 * W;           // 패널 옆 실선 — 같은 기울기
  for (let y = 0; y < H; y++) {
    const t = y / H;
    // 패널 경계(이 행의 x) — 오른쪽 패널은 경계 오른쪽이, 왼쪽 패널은 경계 왼쪽이 패널이다
    const edge = R ? box[0] + slope * (1 - t) : box[2] - slope * t;
    const hx = hairTop - slope * t;
    for (let x = 0; x < W; x++) {
      const i = (y * W + x) * 4;
      const d = R ? x + 0.5 - edge : edge - (x + 0.5);
      const cov = Math.max(0, Math.min(1, d + 0.5));    // 1px 가장자리 매끈하게
      if (cov > 0) {
        const c = deepAt(x + 0.5, y + 0.5, box, cx, cy, cx2, cy2);
        buf[i] = c[0]; buf[i + 1] = c[1]; buf[i + 2] = c[2]; buf[i + 3] = Math.round(cov * 255);
      }
      const hd = Math.abs(x + 0.5 - hx);
      if (cov < 1 && hd < 1.5) {                         // 실선: CI 35%
        const a = 0.35 * Math.max(0, Math.min(1, 1.5 - hd));
        buf[i] = CI[0]; buf[i + 1] = CI[1]; buf[i + 2] = CI[2]; buf[i + 3] = Math.max(buf[i + 3], Math.round(a * 255));
      }
    }
  }
  return png(W, H, buf);
}

/** 본문 장 머리 탭 — 오른쪽 끝만 같은 기울기로 자른 깊은 면 */
function tab(w = 560, h = 92) {
  const buf = Buffer.alloc(w * h * 4);
  const cut = K * h;
  for (let y = 0; y < h; y++) {
    const edge = w - cut * (y + 0.5) / h;
    for (let x = 0; x < w; x++) {
      const cov = Math.max(0, Math.min(1, edge - x));
      if (!cov) continue;
      const i = (y * w + x) * 4, c = deepAt(x + 0.5, y + 0.5, [0, 0, w, h], 0.86, 0.40, 0.98, 0.22);
      buf[i] = c[0]; buf[i + 1] = c[1]; buf[i + 2] = c[2]; buf[i + 3] = Math.round(cov * 255);
    }
  }
  return png(w, h, buf);
}

/** 그림 셋을 폴더에 쓰고 경로를 돌려준다. 토큰이 바뀌었을 수 있으니 매번 새로 그린다(1초 안쪽) */
function writePanels(dir) {
  fs.mkdirSync(dir, { recursive: true });
  const out = { r: path.join(dir, 'h-panel-r.png'), l: path.join(dir, 'h-panel-l.png'), tab: path.join(dir, 'h-tab.png') };
  fs.writeFileSync(out.r, panel('r'));
  fs.writeFileSync(out.l, panel('l'));
  fs.writeFileSync(out.tab, tab());
  return out;
}

module.exports = { panel, tab, writePanels, TAB: { w: 560, h: 92 } };

if (require.main === module) {
  const dir = process.argv[2] || 'decks-out/h-panels';
  console.log(writePanels(dir));
}
