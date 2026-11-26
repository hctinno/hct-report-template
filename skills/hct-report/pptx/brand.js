'use strict';
/**
 * brand.json 읽기 — build.js(용도별 덱)와 template.js(레이아웃 템플릿)가 함께 쓴다.
 * 로고 경로 · 비율 · 워터마크를 한 곳에서 정한다. 두 생성기가 따로 들고 있으면
 * 로고 규칙이 바뀔 때 한쪽만 따라간다.
 */
const fs = require('fs');
const path = require('path');

function loadBrand(p) {
  const b = JSON.parse(fs.readFileSync(p, 'utf8'));
  const dir = path.dirname(path.resolve(p));
  // 로고는 두 벌이다. 어두운 면에는 흰색 녹아웃, 밝은 면에는 원색을 쓴다.
  // 비율은 파일마다 다르다. 워터마크는 국문을 뗀 심볼이라 마크보다 납작하다.
  // 한 곳에 모아 두면 나중에 읽은 값이 앞의 것을 덮어써 로고가 찌그러진다.
  const resolveLogo = (rel, label) => {
    if (!rel) return null;
    const abs = path.isAbsolute(rel) ? rel : path.join(dir, rel);
    if (!fs.existsSync(abs)) {
      console.error(`주의: ${label} 로고 파일이 없어 워드마크 텍스트로 대체한다 — ${abs}`);
      return null;
    }
    const dim = pngSize(abs);
    return { path: abs, ratio: dim ? dim.w / dim.h : null };
  };
  const dark = resolveLogo(b.logo, '다크면용');
  const light = resolveLogo(b.logoOnLight, '밝은면용');
  const wm = resolveLogo(b.watermark, '워터마크용');

  b.logoPath = dark && dark.path;
  b.logoPathOnLight = light && light.path;
  // 우측 상단 마크의 비율. 다크면용을 기준으로 잡고 없으면 밝은면용을 쓴다.
  b.logoRatio = (dark && dark.ratio) || (light && light.ratio) || 3.07;
  // 배경 워터마크. 따로 주지 않으면 다크면용 로고를 그대로 키워 쓴다 (HTML 과 같은 규칙).
  b.watermarkPath = (wm && wm.path) || b.logoPath;
  b.watermarkRatio = (wm && wm.ratio) || b.logoRatio;
  const wmL = resolveLogo(b.watermarkOnLight, '밝은면 워터마크용');
  b.watermarkPathOnLight = (wmL && wmL.path) || b.logoPathOnLight;
  b.watermarkRatioOnLight = (wmL && wmL.ratio) || b.logoRatio;
  if (b.logoPath && !b.logoPathOnLight) {
    console.error('주의: logoOnLight 가 없다. 흰색 로고는 밝은 지면에서 보이지 않으므로 '
      + '밝은 슬라이드는 워드마크 텍스트로 둔다.');
  }
  b.wordmark = b.wordmark || b.company;
  b.logoHeight = b.logoHeight || 40;
  return b;
}

/** PNG 헤더에서 크기를 읽는다. 로고 비율 계산용. */
function pngSize(file) {
  const buf = fs.readFileSync(file);
  if (buf.length < 24 || buf.readUInt32BE(0) !== 0x89504e47) return null;
  return { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) };
}

module.exports = { loadBrand, pngSize };
