(function() {
 var root = document.getElementById('two-view-status');
 if (!root) {
  return;
 }
 var NS = 'http://www.w3.org/2000/svg', run = false, tick = null, tms = [], ph = 0;
 var segs = [].slice.call(root.querySelectorAll('.ea-seg')), gv = root.querySelector('.ea-gv'), cbs = root.querySelector('.ea-cbs'), ins = [].slice.call(root.querySelectorAll('.ea-in'));
 var COL = {
  a: '#6bd39a',
  m: '#8fb6f6',
  w: '#ffd166',
  i: '#2c3a5e'
 }, N = 26, W = 8.2, X0 = 440;
 var rows = segs.map(function(g, i) {
  var st = [ 'a', 'a', 'm', 'i' ][i], arr = [];
  for (var k = 0; k < N; k++) {
   arr.push(st);
  }
  return {
   g: g,
   y: +g.getAttribute('data-y'),
   arr: arr,
   st: st,
   left: 6 + i * 3
  };
 });
 function next(st) {
  var r = Math.random();
  if (st === 'a') {
   return r < .08 ? 'w' : r < .12 ? 'i' : 'a';
  }
  if (st === 'm') {
   return r < .1 ? 'w' : r < .16 ? 'i' : 'm';
  }
  if (st === 'w') {
   return r < .3 ? Math.random() < .6 ? 'a' : 'm' : 'w';
  }
  return r < .12 ? 'w' : r < .2 ? 'a' : 'i';
 }
 function draw() {
  rows.forEach(function(r) {
   while (r.g.firstChild) {
    r.g.removeChild(r.g.firstChild);
   }
   r.arr.forEach(function(st, k) {
    var e = document.createElementNS(NS, 'rect');
    e.setAttribute('x', X0 + k * W);
    e.setAttribute('y', r.y);
    e.setAttribute('width', W - 1);
    e.setAttribute('height', 16);
    e.style.fill = COL[st];
    r.g.appendChild(e);
   });
  });
  var on = rows.filter(function(r) {
   var st = r.arr[N - 1];
   return st === 'a' || st === 'm';
  }).length;
  gv.textContent = String(on);
  var c = {
   a: 0,
   m: 0,
   w: 0,
   i: 0
  };
  rows.forEach(function(r) {
   r.arr.forEach(function(st) {
    c[st]++;
   });
  });
  var tot = N * rows.length, x = 622;
  while (cbs.firstChild) {
   cbs.removeChild(cbs.firstChild);
  }
  [ 'a', 'm', 'w', 'i' ].forEach(function(st) {
   var w = 108 * c[st] / tot, e = document.createElementNS(NS, 'rect');
   e.setAttribute('x', x);
   e.setAttribute('y', 184);
   e.setAttribute('width', Math.max(0, w));
   e.setAttribute('height', 10);
   e.style.fill = COL[st];
   cbs.appendChild(e);
   x += w;
  });
 }
 function step() {
  if (!run) {
   return;
  }
  ph++;
  rows.forEach(function(r) {
   if (--r.left <= 0) {
    r.st = next(r.st);
    r.left = 2 + Math.floor(Math.random() * 5);
   }
   r.arr.push(r.st);
   r.arr.shift();
  });
  draw();
  ins.forEach(function(g, i) {
   g.classList.toggle('on', Math.floor(ph / 12) % 3 === i);
  });
  tick = setTimeout(step, 420);
 }
 function start() {
  if (run) {
   return;
  }
  run = true;
  step();
 }
 function stop() {
  run = false;
  clearTimeout(tick);
  tms.forEach(clearTimeout);
  tms = [];
  ins.forEach(function(g) {
   g.classList.remove('on');
  });
 }
 draw();
 var io = new IntersectionObserver(function(es) {
  es.forEach(function(e) {
   if (e.intersectionRatio >= .55) {
    start();
   } else {
    stop();
   }
  });
 }, {
  threshold: [ .55 ]
 });
 io.observe(root);
})();
