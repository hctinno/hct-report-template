// 문서 뷰어 — 쪽번호·문서명·문서번호 자동 채움, 축척 맞춤, 인쇄.
// 문서 여러 종이 이 파일 하나를 공유한다. 단일 파일로 만들 때는 인라인된다.
//
// 채우는 자리는 셋이다. 머리말 · 꼬리말 짜임은 양식이 기본(로고 | 문서번호, 회사 · 문서명 | n / m)과
// 다를 때만 양식대로 다시 짠다(아래 --bd-head-* · --bd-foot-*).
//   .bd-pageno    n / m
//   .bd-doctitle  .bd-doc 의 data-doc-title
//   .bd-docno     .bd-doc 의 data-doc-no

(function () {
  var doc   = document.querySelector('.bd-doc');
  var pages = Array.prototype.slice.call(document.querySelectorAll('.bd-page'));
  if (!doc || !pages.length) return;

  var title = doc.dataset.docTitle || '';
  var docno = doc.dataset.docNo || '';

  // 머리말 · 꼬리말 짜임 — 양식(forms/<id>.json → blue-doc.css 의 --bd-head-* · --bd-foot-*)을 따른다.
  // 견본 HTML 의 머리말 · 꼬리말은 기본 양식 모양 그대로이고, 양식이 다르면 여기서 다시 짠다.
  // 양식 변수는 .bd-doc 에서 읽는다 — 문서가 data-form 으로 다른 양식을 고르면 그 값이 여기 걸린다
  var rs = getComputedStyle(doc);
  function cssStr(name) {
    var v = rs.getPropertyValue(name).trim();
    return v ? v.replace(/^["']|["']$/g, '') : '';
  }
  var HEAD = [cssStr('--bd-head-left'), cssStr('--bd-head-right')];
  var HEAD_LAYOUT = cssStr('--bd-head-layout') || 'split';
  var FOOT = [cssStr('--bd-foot-left'), cssStr('--bd-foot-right')];
  var NUMERAL = cssStr('--bd-numeral') || 'keep';
  var COVER_MODE = cssStr('--bd-cover') || 'off';
  var COVER = (COVER_MODE === 'always' && doc.dataset.docCover !== 'no') || (COVER_MODE === 'opt-in' && doc.dataset.docCover === 'yes');
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  function headItem(kind, pg, company) {
    if (kind === 'logo') { var m = pg.querySelector('.bd-head .br-mark'); return m || el('span'); }
    if (kind === 'docNo') return el('span', 'bd-docno');
    if (kind === 'title') return el('span', 'bd-doctitle');
    if (kind === 'company') return el('span', 'bd-company', company);
    return el('span');
  }
  // 글 틀 → 요소. {page}/{pages} 가 든 쪽은 통째로 .bd-pageno(숫자 글꼴)로 감싸 뷰어가 채운다
  function footSide(tpl, company) {
    var box = el('span', /\{page/.test(tpl) ? 'bd-pageno' : '');
    box.dataset.tpl = tpl;
    tpl.split(/(\{[a-zA-Z]+\})/).forEach(function (part) {
      if (!part) return;
      if (part === '{company}') box.appendChild(el('span', 'bd-company', company));
      else if (part === '{title}') box.appendChild(el('span', 'bd-doctitle'));
      else if (part === '{docNo}') box.appendChild(el('span', 'bd-docno'));
      else if (part === '{page}' || part === '{pages}') box.appendChild(el('span', 'bd-pn', part));
      else box.appendChild(document.createTextNode(part));
    });
    return box;
  }
  // 쪽 나눔 — 양식 page.breaks 가 flow 면 원본의 쪽 경계를 무시하고 글을 이어 흘려 쪽을 저절로 나눈다.
  // 넘친 블록은 다음 쪽으로 옮기고, 장 · 절 제목이 쪽 끝에 홀로 남지 않게 함께 옮긴다. 결재란은 마지막 쪽에 둔다.
  var BREAKS = cssStr('--bd-breaks') || 'authored';
  if (BREAKS === 'flow' && !doc.dataset.flowed) {
    doc.dataset.flowed = '1';
    var tpl = pages[0].cloneNode(true);
    tpl.querySelector('.bd-body').innerHTML = '';
    Array.prototype.forEach.call(tpl.querySelectorAll('.bd-sign'), function (x) { x.parentNode.removeChild(x); });
    var blocks = [], sign = null;
    pages.forEach(function (pg) {
      var b = pg.querySelector('.bd-body');
      if (b) Array.prototype.forEach.call(b.children, function (c) { blocks.push(c); });
      var sg = pg.querySelector('.bd-sign');
      if (sg && sg.parentNode === pg) sign = sg;
    });
    pages.slice(1).forEach(function (pg) { pg.parentNode.removeChild(pg); });
    var cur = pages[0], body = cur.querySelector('.bd-body');
    while (body.firstChild) body.removeChild(body.firstChild);
    if (sign) sign.parentNode.removeChild(sign);
    var over = function (pg) { var b = pg.querySelector('.bd-body'); return b.scrollHeight > b.clientHeight + 1; };
    var isHead = function (n) { return n && /\bbd-h[12]\b/.test(n.className || ''); };
    var isPara = function (n) { return n && /\bbd-p\b/.test(n.className || ''); };
    // 쪽 끝에 남기지 않는 것 — 장 · 절 제목, 그리고 제목 바로 뒤의 도입 문단(「제목 → 한 줄 설명 → 표」를 한 덩어리로)
    var stranded = function () {
      var l = body.lastElementChild;
      if (!l || body.children.length <= 1) return false;
      return isHead(l) || (isPara(l) && isHead(l.previousElementSibling));
    };
    // 긴 표 — 한 쪽에 다 못 들어가면 행 단위로 나누고 다음 쪽에 머리 행을 되풀이한다(Word 와 같은 방식).
    // 이 쪽에 3행 이상, 다음 쪽에 2행 이상 남을 때만 나눈다 — 아니면 표를 통째로 넘긴다
    var splitTable = function (tbl) {
      var tb = tbl.tBodies && tbl.tBodies[0];
      if (!tb || tb.rows.length < 5) return null;
      var moved = [];
      while (over(cur) && tb.rows.length > 3) moved.unshift(tb.removeChild(tb.lastElementChild));
      if (over(cur) || moved.length < 2) {
        moved.forEach(function (r) { tb.appendChild(r); });
        return null;
      }
      var rest = tbl.cloneNode(false);
      if (tbl.tHead) rest.appendChild(tbl.tHead.cloneNode(true));
      var nb = document.createElement('tbody');
      moved.forEach(function (r) { nb.appendChild(r); });
      rest.appendChild(nb);
      rest.classList.add('bd-table--cont');
      return rest;
    };
    var newPage = function () {
      var p = tpl.cloneNode(true);
      cur.parentNode.insertBefore(p, cur.nextSibling);
      cur = p; body = p.querySelector('.bd-body');
      return p;
    };
    var queue = blocks.slice();
    while (queue.length) {
      var blk = queue.shift();
      body.appendChild(blk);
      if (!over(cur)) continue;
      var isTbl = blk.tagName === 'TABLE';
      if (isTbl) {
        var rest = splitTable(blk);
        if (rest) { newPage(); queue.unshift(rest); continue; }
      }
      if (body.children.length > 1) {
        var carry = [blk];
        body.removeChild(blk);
        while (stranded()) carry.unshift(body.removeChild(body.lastElementChild));
        newPage();
        carry.forEach(function (c) { body.appendChild(c); });
        // 새 쪽에서도 넘치는 표(한 쪽보다 긴 표)는 여기서 나눈다
        if (isTbl && over(cur)) {
          var rest2 = splitTable(blk);
          if (rest2) { newPage(); queue.unshift(rest2); }
        }
      }
    }
    if (sign) {
      var foot = cur.querySelector('.bd-foot');
      cur.insertBefore(sign, foot);
      if (over(cur)) {
        var moved = [];
        while (over(cur) && body.children.length > 1) moved.unshift(body.removeChild(body.lastElementChild));
        while (isHead(body.lastElementChild) && body.children.length > 1) moved.unshift(body.removeChild(body.lastElementChild));
        cur.removeChild(sign);
        newPage();
        moved.forEach(function (c) { body.appendChild(c); });
        cur.insertBefore(sign, cur.querySelector('.bd-foot'));
      }
    }
    pages = Array.prototype.slice.call(document.querySelectorAll('.bd-page'));
  }

  // 표지 — 양식 cover. 오른쪽 위 로고 · 문서명 · 부제 · 두 줄 선 · 아래 문서 정보 줄 · 회사명(가운데 정렬).
  // 머리말 · 꼬리말은 자리만 두고 숨긴다(blue-doc.css .bd-cover) — 본문 높이가 다른 쪽과 같다
  if (COVER && !doc.querySelector('.bd-cover')) {
    var first = pages[0];
    var cv = el('section', 'bd-page bd-cover');
    var fh = first.querySelector('.bd-head');
    if (fh) cv.appendChild(fh.cloneNode(true));
    var cb = el('div', 'bd-body');
    var fco = first.querySelector('.bd-company');
    var fmark = first.querySelector('.bd-head .br-mark');
    if (fmark) { var lg = el('div', 'bd-cover-logo'); lg.appendChild(fmark.cloneNode(true)); cb.appendChild(lg); }
    cb.appendChild(el('div', 'bd-cover-title', title));
    var fsub = first.querySelector('.bd-subtitle');
    if (fsub && fsub.textContent.trim()) cb.appendChild(el('div', 'bd-cover-sub', fsub.textContent.trim()));
    cb.appendChild(el('div', 'bd-cover-rule'));
    var mv = { docNo: docno, dept: doc.dataset.docDept || '', date: doc.dataset.docDate || '' };
    var meta = (cssStr('--bd-cover-meta') || '{docNo}').split(' · ').map(function (part) {
      return part.replace(/\{(\w+)\}/g, function (m, k) { return mv[k] || ''; }).trim();
    }).filter(Boolean).join(' · ');
    if (meta) cb.appendChild(el('div', 'bd-cover-meta', meta));
    cb.appendChild(el('div', 'bd-cover-company', (cssStr('--bd-cover-company') || '{company}').replace('{company}', fco ? fco.textContent : '')));
    cv.appendChild(cb);
    var ff = first.querySelector('.bd-foot');
    if (ff) cv.appendChild(ff.cloneNode(true));
    first.parentNode.insertBefore(cv, first);
    pages.unshift(cv);
  }
  // 쪽번호는 본문부터 센다 — 표지는 번호 · 머리말 · 꼬리말이 없다
  var numbered = pages.filter(function (pg) { return !pg.classList.contains('bd-cover'); });
  var total = numbered.length;

  // 장 번호 — 양식 type.h1.numeral 이 roman 이면 「1. 요약」을 「Ⅰ 요약」으로. 상자 모양(box)이면 번호 칸 · 제목 칸으로 나눈다
  var H1_BOX = getComputedStyle(document.querySelector('.bd-h1') || document.body).display === 'flex';
  function roman(n) {
    if (n >= 1 && n <= 12) return String.fromCharCode(0x215F + n);
    var r = '', v = [[10, 'X'], [9, 'IX'], [5, 'V'], [4, 'IV'], [1, 'I']];
    v.forEach(function (p) { while (n >= p[0]) { r += p[1]; n -= p[0]; } });
    return r;
  }
  Array.prototype.forEach.call(document.querySelectorAll('.bd-h1'), function (h) {
    if (h.children.length || h.dataset.split) return;
    var m = /^\s*(\d+|[\u2160-\u216B]+)[.)]?\s+(.*)$/.exec(h.textContent);
    if (!m) return;
    var num = m[1];
    if (NUMERAL === 'roman' && /^\d+$/.test(num)) num = roman(parseInt(num, 10));
    h.dataset.split = '1';
    if (H1_BOX) {
      h.textContent = '';
      h.appendChild(el('span', 'bd-h1-n', num));
      h.appendChild(el('span', 'bd-h1-t', m[2]));
    } else if (num !== m[1]) {
      h.textContent = num + '. ' + m[2];
    }
  });

  var STD_HEAD = HEAD_LAYOUT === 'split' && HEAD.join('|') === 'logo|docNo';
  var STD_FOOT = FOOT.join('|') === '{company} · {title}|{page} / {pages}';
  pages.forEach(function (pg) {
    var co = pg.querySelector('.bd-company');
    var company = co ? co.textContent : '';
    var hd = pg.querySelector('.bd-head'), ft = pg.querySelector('.bd-foot');
    if (hd && HEAD[0] && !STD_HEAD) {
      var h0 = headItem(HEAD[0], pg, company), h1 = headItem(HEAD[1], pg, company);
      hd.textContent = ''; hd.appendChild(h0);
      if (HEAD_LAYOUT === 'logo-title') {
        // 가운데 문서명 — 글자 사이를 양식 header.title.letterSpacing 만큼 벌린다
        var long = title.replace(/\s/g, '').length > (parseInt(cssStr('--bd-head-title-max'), 10) || 6);
        hd.appendChild(el('span', 'bd-head-title bd-doctitle' + (long ? ' is-long' : '')));
      }
      hd.appendChild(h1);
    }
    if (ft && FOOT[0] && !STD_FOOT) {
      ft.textContent = ''; ft.appendChild(footSide(FOOT[0], company)); ft.appendChild(footSide(FOOT[1], company));
    }
  });

  pages.forEach(function (pg) {
    var n = numbered.indexOf(pg);
    pg.querySelectorAll('.bd-pn').forEach(function (el) {
      el.textContent = el.textContent === '{pages}' ? total : (n + 1);
    });
    pg.querySelectorAll('.bd-doctitle').forEach(function (el) { el.textContent = title; });
    pg.querySelectorAll('.bd-docno').forEach(function (el) { el.textContent = docno; });
    pg.querySelectorAll('.bd-pageno').forEach(function (el) {
      if (!el.querySelector('.bd-pn')) el.textContent = (n + 1) + ' / ' + total;   // 기본 양식 견본
    });
  });

  // 창이 좁으면 지면을 줄여 가로 스크롤이 생기지 않게 한다. 인쇄에는 영향이 없다.
  function fit() {
    var w = parseFloat(getComputedStyle(doc).getPropertyValue('--bd-page-w')) || 794;
    var s = Math.min(1, (window.innerWidth - 48) / w);
    doc.style.transform = s < 1 ? 'scale(' + s + ')' : '';
    doc.style.transformOrigin = 'top center';
  }
  window.addEventListener('resize', fit);
  fit();

  var hud = document.getElementById('bd-hud');
  if (!hud) return;
  var pos = hud.querySelector('#bd-pos');
  if (pos) pos.textContent = total + '쪽';
  var pr = hud.querySelector('#bd-print');
  if (pr) pr.onclick = function () { window.print(); };
})();
