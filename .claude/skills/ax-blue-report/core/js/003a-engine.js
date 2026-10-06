(function() {
 'use strict';
 var d = document, deck = d.getElementById('deck'), body = d.body, root = d.documentElement, $ = function(id) {
  return d.getElementById(id);
 };
 var PRESENT_ONLY = window.AXBR_MODE === 'present';
 var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
 root.classList.add('anim');
 body.classList.add('expand');
 function visible() {
  return Array.prototype.slice.call(d.querySelectorAll('.sl'));
 }
 var cur = 0;
 function steps(el) {
  var set = {};
  Array.prototype.forEach.call(el.querySelectorAll('.fr[data-f]'), function(f) {
   set[f.dataset.f] = 1;
  });
  return Object.keys(set).map(Number).sort(function(a, b) {
   return a - b;
  });
 }
 function shown(el) {
  return parseInt(el.dataset.step || '0', 10);
 }
 function apply(el) {
  var n = shown(el);
  Array.prototype.forEach.call(el.querySelectorAll('.fr[data-f]'), function(f) {
   f.classList.toggle('on', parseInt(f.dataset.f, 10) <= n);
  });
 }
 function stepFwd() {
  var el = visible()[cur], st = steps(el), n = shown(el);
  var nx = st.filter(function(s) {
   return s > n;
  })[0];
  if (nx === undefined || body.classList.contains('expand')) {
   return false;
  }
  el.dataset.step = nx;
  apply(el);
  return true;
 }
 function stepBack() {
  var el = visible()[cur], st = steps(el), n = shown(el);
  if (body.classList.contains('expand')) {
   return false;
  }
  var pv = st.filter(function(s) {
   return s < n;
  });
  if (n === 0) {
   return false;
  }
  el.dataset.step = pv.length ? pv[pv.length - 1] : 0;
  apply(el);
  return true;
 }
 function resetSteps(el, all) {
  el.dataset.step = all ? '999' : '0';
  apply(el);
 }
 function goTo(i, smooth, fromEnd) {
  var list = visible();
  i = Math.max(0, Math.min(list.length - 1, i));
  var el = list[i];
  cur = i;
  if (!body.classList.contains('expand')) {
   resetSteps(el, !!fromEnd);
  }
  var beh = smooth === false || reduce ? 'auto' : 'smooth';
  if (body.classList.contains('horiz')) {
   deck.scrollTo({
    left: el.offsetLeft,
    behavior: beh
   });
  } else {
   deck.scrollTo({
    top: el.offsetTop,
    behavior: beh
   });
  }
  sync();
 }
 function next() {
  if (!stepFwd()) {
   goTo(cur + 1);
  } else {
   sync();
  }
 }
 function prev() {
  if (!stepBack()) {
   goTo(cur - 1, true, true);
  } else {
   sync();
  }
 }
 var pg = $('pg'), prog = $('prog'), ntx = $('ntx');
 function sync() {
  var list = visible(), el = list[cur];
  if (!el) {
   return;
  }
  var pages = Array.prototype.slice.call(d.querySelectorAll('.sl'));
  var numbered = pages.slice(1), d8 = d.getElementById('appendix'), cut = d8 ? numbered.indexOf(d8) : -1;
  var bodyP = cut < 0 ? numbered.filter(function(x) {
   return !x.classList.contains('apx');
  }) : numbered.slice(0, cut), apxP = pages.filter(function(x) {
   return x.classList.contains('apx');
  });
  function two(n) {
   return String(n).padStart(2, '0');
  }
  function pgOf(x) {
   var k = bodyP.indexOf(x);
   if (k >= 0) {
    return two(k + 1) + ' / ' + two(bodyP.length);
   }
   k = apxP.indexOf(x);
   if (k >= 0) {
    return '부록 ' + two(k + 1) + ' / ' + two(apxP.length);
   }
   return x === d8 ? '부록' : '';
  }
  var lab = pgOf(el);
  var st = steps(el);
  if (st.length && !body.classList.contains('expand')) {
   var n = st.filter(function(s) {
    return s <= shown(el);
   }).length;
   lab += ' · ' + n + '/' + st.length;
  }
  pg.textContent = lab;
  Array.prototype.forEach.call(d.querySelectorAll('.sl'), function(s) {
   var p = s.querySelector('.rf .pg');
   if (!p) {
    return;
   }
   p.textContent = pgOf(s);
  });
  prog.style.width = (list.length > 1 ? cur / (list.length - 1) * 100 : 0) + '%';
  ntx.textContent = el.getAttribute('data-notes') || '(메모 없음)';
  var stp = steps(el), sn = body.classList.contains('expand') ? stp.length : stp.filter(function(x) {
   return x <= shown(el);
  }).length;
  d.dispatchEvent(new CustomEvent('deck:sync', {
   detail: {
    el: el,
    cur: cur,
    list: list,
    step: sn,
    steps: stp.length
   }
  }));
 }
 var io = new IntersectionObserver(function(es) {
  es.forEach(function(e) {
   if (e.isIntersecting && e.intersectionRatio >= .55) {
    e.target.classList.add('in');
    var i = visible().indexOf(e.target);
    if (i >= 0 && i !== cur) {
     cur = i;
     if (!body.classList.contains('expand')) {
      resetSteps(e.target, false);
     }
     sync();
    }
    runCounters(e.target);
   }
  });
 }, {
  root: deck,
  threshold: [ .55 ]
 });
 Array.prototype.forEach.call(d.querySelectorAll('.sl'), function(s) {
  io.observe(s);
 });
 function runCounters(sec) {
  Array.prototype.forEach.call(sec.querySelectorAll('[data-count]'), function(el) {
   if (el.dataset.done) {
    return;
   }
   el.dataset.done = '1';
   var to = parseFloat(el.dataset.count), dec = parseInt(el.dataset.dec || '0', 10);
   if (reduce) {
    el.textContent = to.toFixed(dec);
    return;
   }
   var t0 = null, dur = 1100;
   (function step(t) {
    if (!t0) {
     t0 = t;
    }
    var p = Math.min(1, (t - t0) / dur);
    p = 1 - Math.pow(1 - p, 3);
    el.textContent = (to * p).toFixed(dec);
    if (p < 1) {
     requestAnimationFrame(step);
    }
   })(performance.now());
  });
 }
 function setExpand(on) {
  body.classList.toggle('expand', on);
  $('ex').classList.toggle('on', on);
  var el = visible()[cur];
  if (el && !on) {
   resetSteps(el, false);
  }
  sync();
 }
 function toggleDir() {
  var el = visible()[cur];
  body.classList.toggle('horiz');
  $('dir').classList.toggle('on', body.classList.contains('horiz'));
  $('dir').innerHTML = body.classList.contains('horiz') ? '세로 <kbd>H</kbd>' : '가로 <kbd>H</kbd>';
  requestAnimationFrame(function() {
   goTo(visible().indexOf(el), false);
  });
 }
 function toggleNotes() {
  body.classList.toggle('notes');
  $('nt').classList.toggle('on', body.classList.contains('notes'));
 }
 function toggleHelp() {
  $('help').classList.toggle('on');
 }
 var fsOptOut = false, fsWas = false;
 function enterPresent(noFs) {
  body.classList.add('present');
  setExpand(false);
  d.dispatchEvent(new CustomEvent('deck:present', {
   detail: {
    on: true
   }
  }));
  if (!noFs) {
   try {
    if (d.fullscreenEnabled && !d.fullscreenElement) {
     root.requestFullscreen().catch(function() {});
    }
   } catch (e) {}
  }
  deck.focus({
   preventScroll: true
  });
 }
 function exitPresent(noFs) {
  if (!noFs && body.classList.contains('fs')) {
   fsOptOut = true;
  }
  body.classList.remove('present', 'peek');
  setExpand(true);
  d.dispatchEvent(new CustomEvent('deck:present', {
   detail: {
    on: false
   }
  }));
  if (!noFs) {
   try {
    if (d.fullscreenElement) {
     d.exitFullscreen();
    }
   } catch (e) {}
  }
 }
 function togglePresent() {
  if (body.classList.contains('present')) {
   exitPresent();
  } else {
   fsOptOut = false;
   enterPresent();
  }
 }
 d.addEventListener('fullscreenchange', syncFs);
 var mqFs = null;
 try {
  mqFs = window.matchMedia('(display-mode: fullscreen)');
 } catch (e) {}
 function screenFull() {
  try {
   if (mqFs && mqFs.matches) {
    return true;
   }
   var sw = screen.width, sh = screen.height, iw = innerWidth, ih = innerHeight, ow = outerWidth, oh = outerHeight;
   if (ih >= sh - 2 && iw >= sw - 2) {
    return true;
   }
   if (ow > 0 && iw > 0) {
    var z = ow / iw;
    if (Math.abs(ow - sw) <= 2 && Math.abs(oh - sh) <= 2 && Math.abs(oh - ih * z) <= 8 * z) {
     return true;
    }
    if (window.top !== window.self && Math.abs(ow - sw) <= 1 && Math.abs(oh - sh) <= 1) {
     return true;
    }
   }
   return false;
  } catch (e) {
   return false;
  }
 }
 var baseFull = screenFull(), sawFull = false, f11On = false, rsT = 0;
 function syncFs() {
  var full = screenFull();
  if (baseFull && !full) {
   baseFull = false;
  }
  if (full && !baseFull) {
   sawFull = true;
  } else if (!full && sawFull) {
   sawFull = false;
   f11On = false;
  }
  var on = !!d.fullscreenElement || !baseFull && full || f11On;
  body.classList.toggle('fs', on);
  if (on) {
   if (!body.classList.contains('present') && !fsOptOut) {
    enterPresent(true);
   }
  } else {
   fsOptOut = false;
   body.classList.remove('peek');
   if (fsWas && body.classList.contains('present')) {
    exitPresent(true);
   }
  }
  fsWas = on;
 }
 addEventListener('keydown', function(e) {
  if (e.key !== 'F11' || e.ctrlKey || e.altKey || e.metaKey || d.fullscreenElement) {
   return;
  }
  f11On = !body.classList.contains('present');
  if (f11On) {
   fsOptOut = false;
   enterPresent(true);
  } else {
   sawFull = false;
   exitPresent(true);
  }
  setTimeout(syncFs, 450);
  setTimeout(syncFs, 1100);
 }, true);
 addEventListener('resize', function() {
  syncFs();
  clearTimeout(rsT);
  rsT = setTimeout(syncFs, 450);
 });
 if (mqFs) {
  try {
   mqFs.addEventListener('change', syncFs);
  } catch (e) {
   try {
    mqFs.addListener(syncFs);
   } catch (_) {}
  }
 }
 syncFs();
 $('prev').onclick = prev;
 $('next').onclick = next;
 $('ex').onclick = function() {
  setExpand(!body.classList.contains('expand'));
 };
 $('dir').onclick = toggleDir;
 $('nt').onclick = toggleNotes;
 $('hp').onclick = toggleHelp;
 $('fs').onclick = togglePresent;
 $('help').onclick = toggleHelp;
 $('ex').classList.add('on');
 var jumpBuf = '', jumpApx = false, jumpT = null, jumpEl = d.createElement('div');
 jumpEl.id = 'jump';
 body.appendChild(jumpEl);
 function jumpPaint(msg, bad) {
  if (msg === null) {
   jumpEl.classList.remove('on', 'bad');
   return;
  }
  jumpEl.textContent = msg;
  jumpEl.classList.add('on');
  jumpEl.classList.toggle('bad', !!bad);
 }
 function jumpClear() {
  jumpBuf = '';
  jumpApx = false;
  clearTimeout(jumpT);
  jumpPaint(null);
 }
 function jumpArm() {
  clearTimeout(jumpT);
  jumpT = setTimeout(jumpClear, 3e3);
 }
 function jumpShow() {
  jumpPaint((jumpApx ? '부록 ' : '') + (jumpBuf || '—') + '  ↵ 이동');
  jumpArm();
 }
 function findPage(n, apx) {
  var list = visible(), i;
  if (apx) {
   var ap = d.querySelectorAll('.sl.apx');
   if (n >= 1 && n <= ap.length) {
    return list.indexOf(ap[n - 1]);
   }
   return -1;
  }
  if (n === 0) {
   for (i = 0; i < list.length; i++) {
    if (list[i].dataset.grp === 'cover') {
     return i;
    }
   }
   return -1;
  }
  return n >= 1 && n < list.length ? n : -1;
 }
 function jumpGo() {
  if (!jumpBuf) {
   jumpClear();
   return;
  }
  var n = parseInt(jumpBuf, 10), i = findPage(n, jumpApx);
  if (i < 0) {
   jumpPaint((jumpApx ? '부록 ' : '') + jumpBuf + ' 없음', true);
   jumpArm();
   return;
  }
  jumpClear();
  goTo(i, false);
 }
 addEventListener('keydown', function(e) {
  var _tg = e.target;
  if (_tg && (_tg.tagName === 'TEXTAREA' || _tg.tagName === 'INPUT' || _tg.isContentEditable)) {
   return;
  }
  if (e.altKey || e.ctrlKey || e.metaKey) {
   return;
  }
  var k = e.key;
  if (/^[0-9]$/.test(k)) {
   e.preventDefault();
   if (jumpBuf.length < 3) {
    jumpBuf += k;
   }
   jumpShow();
   return;
  }
  if (k === 'Enter') {
   if (jumpBuf) {
    e.preventDefault();
    jumpGo();
   }
   return;
  }
  if (k === 'Backspace' && jumpBuf) {
   e.preventDefault();
   jumpBuf = jumpBuf.slice(0, -1);
   jumpShow();
   return;
  }
  if ((k === 'a' || k === 'A' || k === 'ㅁ') && !jumpBuf) {
   e.preventDefault();
   jumpApx = !jumpApx;
   jumpShow();
   return;
  }
  if (jumpBuf && k !== 'Escape') {
   jumpClear();
  }
  if (k === 'ArrowRight' || k === ' ') {
   e.preventDefault();
   next();
  } else if (k === 'ArrowLeft') {
   e.preventDefault();
   prev();
  } else if (k === 'ArrowDown' || k === 'PageDown') {
   e.preventDefault();
   next();
  } else if (k === 'ArrowUp' || k === 'PageUp') {
   e.preventDefault();
   prev();
  } else if (k === 'Home') {
   e.preventDefault();
   goTo(0);
  } else if (k === 'End') {
   e.preventDefault();
   goTo(visible().length - 1);
  } else if (k === 'e' || k === 'E') {
   setExpand(!body.classList.contains('expand'));
  } else if (k === 'h' || k === 'H') {
   toggleDir();
  } else if ((k === 'n' || k === 'N') && !PRESENT_ONLY) {
   toggleNotes();
  } else if (k === 'f' || k === 'F') {
   togglePresent();
  } else if (k === '?') {
   toggleHelp();
  } else if ((k === 'p' || k === 'P') && !PRESENT_ONLY) {
   d.dispatchEvent(new CustomEvent('deck:presenter'));
  } else if (k === 'l' || k === 'L') {
   d.dispatchEvent(new CustomEvent('deck:laser'));
  } else if (k === 'Escape') {
   if (jumpBuf || jumpApx) {
    jumpClear();
   } else if ($('help').classList.contains('on')) {
    $('help').classList.remove('on');
   } else if (body.classList.contains('present')) {
    exitPresent();
   }
  }
 });
 var peekT, hudEl = $('hud');
 function hudAuto() {
  return body.classList.contains('present') || body.classList.contains('fs');
 }
 addEventListener('mousemove', function(e) {
  if (!hudAuto()) {
   return;
  }
  var r = hudEl.getBoundingClientRect();
  var near = e.clientY >= r.top - 30;
  clearTimeout(peekT);
  if (near) {
   body.classList.add('peek');
  } else {
   peekT = setTimeout(function() {
    body.classList.remove('peek');
   }, 200);
  }
 }, {
  passive: true
 });
 addEventListener('mouseout', function(e) {
  if (!e.relatedTarget && !e.toElement) {
   body.classList.remove('peek');
  }
 }, {
  passive: true
 });
 addEventListener('blur', function() {
  body.classList.remove('peek');
 });
 deck.addEventListener('click', function(e) {
  if (!body.classList.contains('present')) {
   return;
  }
  if (e.target.closest('a,button,input,select,textarea,label,summary,[data-int],[role="button"],[role="tab"],[aria-pressed]')) {
   return;
  }
  next();
 });
 var wheelLock = 0;
 deck.addEventListener('wheel', function(e) {
  if (!body.classList.contains('horiz')) {
   return;
  }
  e.preventDefault();
  var now = Date.now();
  if (now - wheelLock < 650) {
   return;
  }
  if (Math.abs(e.deltaY) < 8 && Math.abs(e.deltaX) < 8) {
   return;
  }
  wheelLock = now;
  e.deltaY > 0 || e.deltaX > 0 ? goTo(cur + 1) : goTo(cur - 1);
 }, {
  passive: false
 });
 var tx0 = 0, ty0 = 0;
 deck.addEventListener('touchstart', function(e) {
  tx0 = e.touches[0].clientX;
  ty0 = e.touches[0].clientY;
 }, {
  passive: true
 });
 deck.addEventListener('touchend', function(e) {
  var dx = e.changedTouches[0].clientX - tx0, dy = e.changedTouches[0].clientY - ty0;
  if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy)) {
   dx < 0 ? next() : prev();
  }
 }, {
  passive: true
 });
 d.querySelector('.sl').classList.add('in');
 runCounters(d.querySelector('.sl'));
 sync();
 deck.focus({
  preventScroll: true
 });
 if (PRESENT_ONLY) {
  enterPresent(true);
 }
})();
