(function() {
 var D = function(x) {
  var m = x.media || {};
  Object.keys(x.img || {}).forEach(function(k) {
   var v = x.img[k];
   if (typeof v === 'string' && v.charAt(0) === '@') {
    x.img[k] = m[v.slice(1)] || '';
   }
  });
  return x;
 }(JSON.parse(document.getElementById('ev-data').textContent)), HL = D.hl || {};
 var m = document.createElement('div');
 m.id = 'evm';
 m.setAttribute('role', 'dialog');
 m.setAttribute('aria-modal', 'true');
 m.setAttribute('aria-label', '근거 원문·캡처');
 m.innerHTML = '<div class="evp"><div class="evh"><h3>근거 원문 · 캡처</h3><div class="evtabs" role="tablist"></div><button type="button" class="evwide" aria-pressed="false">캡처만 크게</button><button type="button" class="evx" aria-label="닫기">×</button></div><div class="evb"><div class="evt"></div><div class="evi"></div></div></div>';
 document.body.appendChild(m);
 var tabs = m.querySelector('.evtabs'), T = m.querySelector('.evt'), I = m.querySelector('.evi'), B = m.querySelector('.evb'), WB = m.querySelector('.evwide'), ids = [], cur = 0, back = null, F = null, wide = false;
 function esc(t) {
  return String(t || '').replace(/[&<>"]/g, function(c) {
   return {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;'
   }[c];
  });
 }
 function mk(t, hl) {
  var h = esc(t), on = false;
  (hl || []).forEach(function(p) {
   var e = esc(p);
   if (h.indexOf(e) >= 0) {
    on = true;
    h = h.split(e).join('<mark>' + e + '</mark>');
   }
  });
  return [ h, on ];
 }
 function psplit(t, sep) {
  var out = [], d = 0, st = 0;
  for (var i = 0; i < t.length; i++) {
   var c = t[i];
   if (c === '(' || c === '「' || c === '[') {
    d++;
   } else if ((c === ')' || c === '」' || c === ']') && d > 0) {
    d--;
   } else if (d === 0 && t.substr(i, sep.length) === sep) {
    out.push(t.slice(st, i));
    st = i + sep.length;
    i += sep.length - 1;
   }
  }
  out.push(t.slice(st));
  return out.map(function(x) {
   return x.trim();
  }).filter(Boolean);
 }
 function segs(f) {
  var out = [];
  psplit(f, ' / ').forEach(function(g) {
   if (g.length <= 95) {
    out.push(g);
    return;
   }
   var parts = psplit(g, ' · '), buf = '';
   parts.forEach(function(p) {
    if (!buf) {
     buf = p;
    } else if (buf.length < 28 || p.length < 22) {
     buf += ' · ' + p;
    } else {
     out.push(buf);
     buf = p;
    }
   });
   if (buf) {
    out.push(buf);
   }
  });
  return out;
 }
 var IM = [], ik = 0, kb = false, V = null, S = null, IMG = null, nw = 0, nh = 0, sc = 1, tx = 0, ty = 0, hb = [], hi = -1;
 function vw() {
  return V ? V.clientWidth : 0;
 }
 function vh() {
  return V ? V.clientHeight : 0;
 }
 function fitW() {
  return vw() / nw;
 }
 function fitAll() {
  return Math.min(vw() / nw, vh() / nh);
 }
 function clamp() {
  var W = nw * sc, H = nh * sc, pad = 40;
  if (W <= vw()) {
   tx = (vw() - W) / 2;
  } else {
   tx = Math.min(pad, Math.max(vw() - W - pad, tx));
  }
  if (H <= vh()) {
   ty = (vh() - H) / 2;
  } else {
   ty = Math.min(pad, Math.max(vh() - H - pad, ty));
  }
 }
 function apply(anim) {
  if (!V || !S) {
   return;
  }
  clamp();
  S.style.transition = anim ? 'transform .35s cubic-bezier(.3,.7,.2,1)' : 'none';
  S.style.transform = 'translate(' + tx + 'px,' + ty + 'px) scale(' + sc + ')';
  var z = I.querySelector('.evzv');
  if (z) {
   z.textContent = Math.round(sc / fitW() * 100) + '%';
  }
 }
 function zoomAt(f, px, py, anim) {
  var mn = fitAll() * .9, mx = Math.max(fitW() * 5, 3);
  var ns = Math.min(mx, Math.max(mn, sc * f));
  var k = ns / sc;
  tx = px - (px - tx) * k;
  ty = py - (py - ty) * k;
  sc = ns;
  apply(anim);
 }
 function goRect(r, anim) {
  if (!V || !S || !nw) {
   return;
  }
  var cw = Math.max(r[2] * nw * 3, nw * .55), ch = Math.max(r[3] * nh * 6, nh * .28);
  cw = Math.min(cw, nw);
  ch = Math.min(ch, nh);
  var cx = (r[0] + r[2] / 2) * nw, cy = (r[1] + r[3] / 2) * nh;
  sc = Math.min(vw() / cw, vh() / ch, fitW() * 4);
  sc = Math.max(sc, fitAll());
  tx = vw() / 2 - cx * sc;
  ty = vh() / 2 - cy * sc;
  apply(anim);
 }
 function setHi(j, anim) {
  if (!hb.length) {
   return;
  }
  hi = (j + hb.length) % hb.length;
  [].forEach.call(S.querySelectorAll('.evhb'), function(e, n) {
   e.classList.toggle('cur', n === hi);
  });
  goRect(hb[hi], anim);
  var c = I.querySelector('.evhn');
  if (c) {
   c.textContent = hi + 1 + ' / ' + hb.length;
  }
 }
 function fitMode(mode, anim) {
  sc = mode === 'w' ? fitW() : fitAll();
  tx = 0;
  ty = 0;
  if (mode === 'w') {
   tx = (vw() - nw * sc) / 2;
   ty = 16;
  }
  apply(anim);
 }
 function pic(j) {
  ik = j;
  var p = IM[j];
  [].forEach.call(I.querySelectorAll('.evthumbs button'), function(b, n) {
   b.setAttribute('aria-pressed', n === j);
  });
  I.querySelector('.evcap span').textContent = p[0] + ' · ' + p[1];
  hb = (HL[p[0]] || []).slice();
  hi = -1;
  var hn = I.querySelector('.evhlnav');
  hn.hidden = !hb.length;
  S.innerHTML = '<img alt="' + esc(p[1]) + '" src="' + D.img[p[0]] + '" draggable="false">' + hb.map(function(r) {
   return '<i class="evhb" style="left:' + r[0] * 100 + '%;top:' + r[1] * 100 + '%;width:' + r[2] * 100 + '%;height:' + r[3] * 100 + '%"></i>';
  }).join('');
  IMG = S.querySelector('img');
  function ready() {
   nw = IMG.naturalWidth;
   nh = IMG.naturalHeight;
   S.style.width = nw + 'px';
   S.style.height = nh + 'px';
   if (hb.length) {
    setHi(0, false);
   } else {
    fitMode('w', false);
   }
  }
  if (IMG.complete && IMG.naturalWidth) {
   ready();
  } else {
   IMG.onload = ready;
  }
 }
 function viewer() {
  I.querySelector('.evtool').addEventListener('click', function(e) {
   var b = e.target.closest('button');
   if (!b) {
    return;
   }
   e.stopPropagation();
   var a = b.getAttribute('data-a');
   if (a === 'in') {
    zoomAt(1.3, vw() / 2, vh() / 2, true);
   } else if (a === 'out') {
    zoomAt(1 / 1.3, vw() / 2, vh() / 2, true);
   } else if (a === 'w') {
    fitMode('w', true);
   } else if (a === 'all') {
    fitMode('all', true);
   } else if (a === 'hn') {
    setHi(hi + 1, true);
   } else if (a === 'hp') {
    setHi(hi - 1, true);
   }
  });
  V.addEventListener('wheel', function(e) {
   e.preventDefault();
   e.stopPropagation();
   var r = V.getBoundingClientRect();
   var d = e.deltaMode === 1 ? e.deltaY * 30 : e.deltaY;
   zoomAt(Math.exp(-d * .0018), e.clientX - r.left, e.clientY - r.top, false);
  }, {
   passive: false
  });
  var drag = null;
  V.addEventListener('pointerdown', function(e) {
   if (e.button !== 0) {
    return;
   }
   drag = {
    x: e.clientX,
    y: e.clientY,
    tx: tx,
    ty: ty,
    mv: false
   };
   V.setPointerCapture(e.pointerId);
   V.classList.add('grab');
  });
  V.addEventListener('pointermove', function(e) {
   if (!drag) {
    return;
   }
   var dx = e.clientX - drag.x, dy = e.clientY - drag.y;
   if (Math.abs(dx) + Math.abs(dy) > 3) {
    drag.mv = true;
   }
   tx = drag.tx + dx;
   ty = drag.ty + dy;
   apply(false);
  });
  function up() {
   drag = null;
   V.classList.remove('grab');
  }
  V.addEventListener('pointerup', up);
  V.addEventListener('pointercancel', up);
  V.addEventListener('dblclick', function(e) {
   e.stopPropagation();
   var r = V.getBoundingClientRect();
   zoomAt(2, e.clientX - r.left, e.clientY - r.top, true);
  });
  V.addEventListener('click', function(e) {
   e.stopPropagation();
  });
 }
 function show(k) {
  cur = k;
  var id = ids[k], x = D.ev[id];
  [].forEach.call(tabs.children, function(b, j) {
   b.setAttribute('aria-selected', j === k);
  });
  var foc = F && F.e === id, h = '';
  if (foc && F.claim) {
   h += '<p class="evclaim"><b>화면의 이 표시</b>' + esc(F.claim) + '</p>';
  }
  h += '<div class="evkey"><small>' + id + ' 핵심 메시지 <span class="evg ' + x.grade + '">등급 ' + x.grade + ' · ' + esc(D.gr[x.grade] || '') + '</span></small><p>' + esc(x.key) + '</p></div>';
  h += '<p class="evttl">' + esc(x.title) + '</p><div class="evsec">원문에서 확인한 사실</div><ul class="evf">';
  segs(x.facts).forEach(function(g) {
   var r = mk(g, x.hl);
   h += '<li' + (r[1] ? ' class="on"' : '') + '>' + r[0] + '</li>';
  });
  h += '</ul>';
  if (x.note) {
   h += '<div class="evnote"><b>유의 사항</b>' + esc(x.note) + '</div>';
  }
  h += '<div class="evsrc"><b>출처</b> · ' + esc(x.src) + '</div>';
  h += '<details><summary>등급 근거 · 사용 위치</summary>' + (x.gnote ? '<p>등급 근거: ' + esc(x.gnote) + '</p>' : '') + '<p>사용 위치: ' + esc(x.use) + '</p></details>';
  T.innerHTML = h;
  T.scrollTop = 0;
  IM = x.imgs.slice();
  var st = 0;
  if (foc && F.img) {
   IM.forEach(function(p, j) {
    if (p[0] === F.img) {
     st = j;
    }
   });
  }
  m.classList.toggle('noimg', !IM.length);
  m.querySelector('.evh h3').textContent = IM.length ? '근거 원문 · 캡처' : '근거 원문';
  if (!IM.length) {
   if (wide) {
    setWide(false);
   }
   I.innerHTML = '';
   V = null;
   return;
  }
  I.innerHTML = '<div class="evthumbs">' + IM.map(function(p, j) {
   return '<button type="button"' + (foc && p[0] === F.img ? ' class="hit"' : '') + '>' + (j + 1) + '. ' + esc(p[1]) + '</button>';
  }).join('') + '</div>' + '<div class="evcap"><span></span><div class="evtool"><div class="evhlnav"><b>하이라이트</b><button type="button" data-a="hp" aria-label="이전 하이라이트">‹</button><em class="evhn"></em><button type="button" data-a="hn" aria-label="다음 하이라이트">›</button></div>' + '<button type="button" data-a="out" aria-label="축소">−</button><em class="evzv">100%</em><button type="button" data-a="in" aria-label="확대">+</button><button type="button" data-a="w">폭 맞춤</button><button type="button" data-a="all">전체 보기</button></div></div>' + '<div class="evview"><div class="evstage"></div><p class="evhint">휠: 확대 · 축소 &nbsp;|&nbsp; 끌기: 이동 &nbsp;|&nbsp; 더블클릭: 2배</p></div>';
  V = I.querySelector('.evview');
  S = I.querySelector('.evstage');
  viewer();
  [].forEach.call(I.querySelectorAll('.evthumbs button'), function(b, j) {
   b.addEventListener('click', function(e) {
    e.stopPropagation();
    pic(j);
   });
  });
  pic(st);
 }
 function setWide(v) {
  wide = v;
  B.classList.toggle('wide', wide);
  WB.setAttribute('aria-pressed', wide);
  WB.textContent = wide ? '근거 함께 보기' : '캡처만 크게';
  if (V && nw) {
   setTimeout(function() {
    if (hb.length && hi >= 0) {
     setHi(hi, false);
    } else {
     fitMode('w', false);
    }
   }, 30);
  }
 }
 WB.addEventListener('click', function(e) {
  e.stopPropagation();
  setWide(!wide);
 });
 function open(list, btn, opt) {
  ids = list;
  back = btn;
  F = opt || null;
  tabs.innerHTML = ids.map(function(id) {
   return '<button type="button" role="tab">' + id + '</button>';
  }).join('');
  [].forEach.call(tabs.children, function(b, j) {
   b.addEventListener('click', function(e) {
    e.stopPropagation();
    show(j);
   });
  });
  m.classList.add('on');
  document.body.classList.add('evidence-open');
  document.documentElement.classList.add('evidence-open');
  show(0);
  m.querySelector('.evx').focus();
 }
 function close() {
  document.body.classList.remove('evidence-open');
  document.documentElement.classList.remove('evidence-open');
  m.classList.remove('on');
  I.innerHTML = '';
  V = null;
  if (back && kb) {
   back.focus();
  } else if (document.activeElement && document.activeElement.blur) {
   document.activeElement.blur();
  }
 }
 document.addEventListener('click', function(e) {
  var b = e.target.closest && e.target.closest('.ev-open,.ev-pin');
  if (!b) {
   return;
  }
  e.preventDefault();
  e.stopPropagation();
  kb = e.detail === 0;
  if (b.classList.contains('ev-pin')) {
   open([ b.getAttribute('data-ev') ], b, {
    e: b.getAttribute('data-ev'),
    img: b.getAttribute('data-img'),
    claim: b.getAttribute('data-claim')
   });
  } else {
   open(b.getAttribute('data-ev').split(','), b);
  }
 }, true);
 m.addEventListener('click', function(e) {
  e.stopPropagation();
  if (e.target === m || e.target.closest('.evx')) {
   close();
  }
 });
 m.addEventListener('wheel', function(e) {
  var t = e.target.closest('.evt,.evthumbs,details');
  if (t && t.scrollHeight > t.clientHeight) {
   var up = e.deltaY < 0;
   if (up && t.scrollTop > 0 || !up && t.scrollTop + t.clientHeight < t.scrollHeight - 1) {
    e.stopPropagation();
    return;
   }
  }
  e.preventDefault();
  e.stopPropagation();
 }, {
  passive: false
 });
 addEventListener('wheel', function(e) {
  if (m.classList.contains('on') && !m.contains(e.target)) {
   e.preventDefault();
   e.stopImmediatePropagation();
  }
 }, {
  passive: false,
  capture: true
 });
 document.addEventListener('keydown', function(e) {
  var b = e.target && e.target.closest && e.target.closest('span.ev-pin');
  if (!b || m.classList.contains('on')) {
   return;
  }
  if (e.key === 'Enter' || e.key === ' ') {
   e.preventDefault();
   e.stopImmediatePropagation();
   b.click();
  }
 }, true);
 addEventListener('keydown', function(e) {
  if (!m.classList.contains('on')) {
   return;
  }
  e.stopImmediatePropagation();
  if (e.key === ' ' || e.key === 'PageDown' || e.key === 'PageUp') {
   e.preventDefault();
   return;
  }
  if (e.key === 'Escape') {
   e.preventDefault();
   close();
  } else if (V && (e.key === '+' || e.key === '=')) {
   e.preventDefault();
   zoomAt(1.3, vw() / 2, vh() / 2, true);
  } else if (V && (e.key === '-' || e.key === '_')) {
   e.preventDefault();
   zoomAt(1 / 1.3, vw() / 2, vh() / 2, true);
  } else if (V && e.key === '0') {
   e.preventDefault();
   fitMode('w', true);
  } else if (V && (e.key === 'h' || e.key === 'H')) {
   e.preventDefault();
   setHi(hi + 1, true);
  } else if (e.key === 'ArrowRight') {
   e.preventDefault();
   show((cur + 1) % ids.length);
  } else if (e.key === 'ArrowLeft') {
   e.preventDefault();
   show((cur - 1 + ids.length) % ids.length);
  }
 }, true);
 addEventListener('resize', function() {
  if (V && nw) {
   if (hb.length && hi >= 0) {
    setHi(hi, false);
   } else {
    fitMode('w', false);
   }
  }
 });
})();
