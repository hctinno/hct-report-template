(function() {
 var root = document.getElementById('principle-compare');
 if (!root) {
  return;
 }
 var L = root.querySelector('.rl-left .rl-stage'), R = root.querySelector('.rl-right .rl-stage');
 var qn = root.querySelector('.rl-qn'), on = root.querySelector('.rl-on'), an = root.querySelector('.rl-an'), items = root.querySelector('.rl-items'), busy = root.querySelector('.rl-busy');
 var lorgs = [].slice.call(L.querySelectorAll('.rl-org')), rorgs = [].slice.call(R.querySelectorAll('.rl-pz'));
 var hub = L.querySelector('.rl-hub'), out = L.querySelector('.rl-out'), shelf = R.querySelector('.rl-shelf');
 var tms = [], run = false, queue = [], done = 0, assets = 0;
 function rel(el, stage) {
  var r = el.getBoundingClientRect(), p = stage.getBoundingClientRect();
  return {
   x: r.left - p.left + r.width,
   y: r.top - p.top + r.height / 2,
   l: r.left - p.left,
   w: r.width,
   h: r.height,
   t: r.top - p.top
  };
 }
 function tok(stage, cls, x, y) {
  var t = document.createElement('i');
  t.className = 'rl-tk ' + cls;
  t.style.left = x + 'px';
  t.style.top = y + 'px';
  stage.appendChild(t);
  void t.offsetWidth;
  return t;
 }
 function later(ms, fn) {
  tms.push(setTimeout(function() {
   if (run) {
    fn();
   }
  }, ms));
 }
 function spawnL() {
  if (!run) {
   return;
  }
  var o = lorgs[Math.floor(Math.random() * 3)], p = rel(o, L), h = rel(hub, L);
  var t = tok(L, '', p.x - 6, p.y - 8);
  queue.push(t);
  if (queue.length > 10) {
   var old = queue.splice(1, 1)[0];
   old.remove();
  }
  layoutQ();
  later(850 + Math.random() * 400, spawnL);
 }
 function layoutQ() {
  var h = rel(hub, L);
  queue.forEach(function(t, i) {
   var col = i % 2, row = Math.floor(i / 2);
   t.style.left = h.l - 22 - col * 20 + 'px';
   t.style.top = h.y - 8 - row * 16 + (queue.length > 4 ? Math.floor((queue.length - 1) / 2) * 8 : 0) + 'px';
   t.classList.toggle('w', i > 0);
  });
  qn.textContent = queue.length;
 }
 function consume() {
  if (!run) {
   return;
  }
  if (queue.length) {
   var t = queue.shift();
   var o = rel(out, L);
   t.classList.remove('w');
   t.style.left = o.l + o.w / 2 - 10 + 'px';
   t.style.top = o.y - 8 + 'px';
   layoutQ();
   later(950, function() {
    t.remove();
    done++;
    on.textContent = done;
   });
  }
  later(2400, consume);
 }
 function emit(i) {
  if (!run) {
   return;
  }
  var o = rorgs[i], p = rel(o, R), sh = rel(shelf, R);
  var t = tok(R, 'g', p.x - 6, p.y - 8);
  later(30, function() {
   t.style.left = sh.l + sh.w * .5 + 'px';
   t.style.top = sh.t + sh.h * .6 + 'px';
   t.style.opacity = '0';
  });
  later(950, function() {
   t.remove();
   if (assets < 36) {
    var it = document.createElement('i');
    items.appendChild(it);
   }
   assets++;
   an.textContent = assets;
  });
  later(1500 + i * 500 + Math.random() * 700, function() {
   emit(i);
  });
 }
 function dock() {
  rorgs.forEach(function(o, i) {
   later(300 + i * 550, function() {
    o.classList.add('dock');
   });
   later(1150 + i * 550, function() {
    o.classList.add('run');
   });
  });
 }
 function reuse() {
  if (!run) {
   return;
  }
  var sh = rel(shelf, R);
  var i = Math.floor(Math.random() * 3), o = rorgs[i], p = rel(o, R);
  var t = tok(R, 'g r', sh.l + 8, sh.t + sh.h * .5);
  later(40, function() {
   t.style.left = p.x - 2 + 'px';
   t.style.top = p.y - 8 + 'px';
  });
  later(950, function() {
   t.style.opacity = '0';
   o.classList.add('got');
  });
  later(1400, function() {
   t.remove();
   o.classList.remove('got');
  });
  later(4200, reuse);
 }
 function start() {
  if (run) {
   return;
  }
  run = true;
  busy.classList.add('go');
  spawnL();
  later(1200, consume);
  dock();
  rorgs.forEach(function(_, i) {
   later(1500 + i * 600, function() {
    emit(i);
   });
  });
  later(3200, reuse);
 }
 function stop() {
  run = false;
  tms.forEach(clearTimeout);
  tms = [];
  busy.classList.remove('go');
  [].slice.call(root.querySelectorAll('.rl-tk,.rl-pulse')).forEach(function(e) {
   e.remove();
  });
  rorgs.forEach(function(o) {
   o.classList.remove('dock', 'run', 'got');
  });
  queue = [];
 }
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
