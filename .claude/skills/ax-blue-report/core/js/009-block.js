(() => {
 const tabs = [ ...document.querySelectorAll('.peer-detail-tabs button') ];
 function choose(b) {
  const root = b.closest('section');
  tabs.forEach(t => t.setAttribute('aria-selected', String(t === b)));
  root.querySelectorAll('.peer-detail-panel').forEach(p => p.hidden = p.id !== b.getAttribute('aria-controls'));
 }
 tabs.forEach((b, i) => {
  b.addEventListener('click', e => {
   e.stopPropagation();
   choose(b);
  });
  b.addEventListener('keydown', e => {
   if (![ 'ArrowLeft', 'ArrowRight', 'Home', 'End' ].includes(e.key)) {
    return;
   }
   e.preventDefault();
   e.stopPropagation();
   const n = e.key === 'Home' ? 0 : e.key === 'End' ? tabs.length - 1 : (i + (e.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
   tabs[n].focus();
   choose(tabs[n]);
  });
 });
})();

(function() {
 var root = document.getElementById('coaching-demo');
 if (!root) {
  return;
 }
 var MANX = [ 58, 162, 266, 370, 474, 578 ], MANY = [ 182, 156, 130, 104, 78, 52 ];
 var man = root.querySelector('.nz-man');
 var blks = [].slice.call(root.querySelectorAll('.nz-blk'));
 var wls = [].slice.call(root.querySelectorAll('.nz-w'));
 var lays = [].slice.call(root.querySelectorAll('.nz-l'));
 var btns = [].slice.call(root.querySelectorAll('.nz-step'));
 var caps = [].slice.call(root.querySelectorAll('.nz-cap'));
 var cls = [].slice.call(root.querySelectorAll('.nz-cl-t'));
 var chips = [].slice.call(root.querySelectorAll('.nz-chip2'));
 var flag = root.querySelector('.nz-flag');
 var play = root.querySelector('.nz-play');
 var N = 5, tok = 0, timers = [], seq = 0, atim = [];
 function clear() {
  timers.forEach(clearTimeout);
  timers = [];
  tok++;
 }
 function at(ms, fn) {
  var t = tok;
  timers.push(setTimeout(function() {
   if (t === tok) {
    fn();
   }
  }, ms));
 }
 function place(i) {
  if (man) {
   man.style.transform = 'translate(' + MANX[i] + 'px,' + MANY[i] + 'px)';
  }
 }
 function setW(n, st) {
  wls.forEach(function(g) {
   var i = +g.getAttribute('data-w');
   g.classList.remove('idle', 'blocked', 'coach', 'done');
   g.classList.add(i < n ? 'done' : i > n ? 'idle' : st);
  });
 }
 function marks(n) {
  blks.forEach(function(p) {
   p.classList.toggle('on', +p.getAttribute('data-p') <= n);
  });
  chips.forEach(function(c) {
   c.classList.toggle('on', +c.getAttribute('data-k') <= n);
  });
  if (flag) {
   flag.classList.toggle('on', n >= N);
  }
 }
 function right(n) {
  lays.forEach(function(g) {
   g.classList.toggle('on', (g.getAttribute('data-on') || '').split(',').indexOf(String(n)) >= 0);
  });
  btns.forEach(function(b) {
   if (+b.getAttribute('data-s') === n) {
    b.setAttribute('aria-current', 'true');
   } else {
    b.removeAttribute('aria-current');
   }
  });
  caps.forEach(function(c) {
   c.hidden = +c.getAttribute('data-c') !== n;
  });
  cls.forEach(function(c) {
   c.hidden = +c.getAttribute('data-c') !== n;
  });
 }
 function go(n, anim) {
  clear();
  right(n);
  if (!anim) {
   setW(n, 'done');
   place(n);
   marks(n);
   return;
  }
  setW(n, 'blocked');
  place(n - 1);
  marks(n - 1);
  at(280, function() {
   setW(n, 'coach');
  });
  at(1550, function() {
   setW(n, 'done');
  });
  at(1850, function() {
   place(n);
   marks(n);
  });
 }
 function stopAuto() {
  seq++;
  atim.forEach(clearTimeout);
  atim = [];
 }
 btns.forEach(function(b) {
  b.addEventListener('click', function() {
   stopAuto();
   go(+b.getAttribute('data-s'), true);
  });
 });
 if (play) {
  play.addEventListener('click', function() {
   stopAuto();
   var my = seq;
   function run(n) {
    if (my !== seq) {
     return;
    }
    go(n, true);
    if (n < N) {
     atim.push(setTimeout(function() {
      run(n + 1);
     }, 2750));
    }
   }
   run(1);
  });
 }
 go(1, false);
 var mks = [].slice.call(root.querySelectorAll('.nz-mk'));
 function stepOf() {
  var n = 1;
  mks.forEach(function(m) {
   if (m.classList.contains('on')) {
    n++;
   }
  });
  return Math.min(Math.max(n, 1), N);
 }
 var cur = 1;
 function syncStep() {
  var n = stepOf();
  if (n === cur) {
   return;
  }
  var up = n > cur;
  cur = n;
  go(n, up);
 }
 var mo = new MutationObserver(syncStep);
 mks.forEach(function(m) {
  mo.observe(m, {
   attributes: true,
   attributeFilter: [ 'class' ]
  });
 });
 var io2 = new IntersectionObserver(function(es) {
  es.forEach(function(e) {
   if (e.intersectionRatio >= .55) {
    cur = -1;
    syncStep();
   }
  });
 }, {
  threshold: [ .55 ]
 });
 io2.observe(root);
 setTimeout(syncStep, 80);
})();
