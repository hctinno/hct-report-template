(function() {
 var root = document.getElementById('search-grid');
 if (!root) {
  return;
 }
 var rows = [].slice.call(root.querySelectorAll('.kw-row')), sums = [].slice.call(root.querySelectorAll('.kw-s b'));
 var run = false, tms = [];
 function later(ms, fn) {
  tms.push(setTimeout(function() {
   if (run) {
    fn();
   }
  }, ms));
 }
 function reset() {
  rows.forEach(function(r) {
   r.classList.remove('on');
   [].slice.call(r.querySelectorAll('.kw-c')).forEach(function(c) {
    c.classList.remove('on');
   });
  });
  sums.forEach(function(b) {
   b.textContent = '0';
  });
 }
 function play() {
  if (!run) {
   return;
  }
  reset();
  var t = 250;
  var maxc = 0;
  rows.forEach(function(r) {
   var cs = [].slice.call(r.querySelectorAll('.kw-c'));
   maxc = Math.max(maxc, cs.length);
   cs.forEach(function(c, i) {
    later(t + i * 120, function() {
     c.classList.add('on');
    });
   });
  });
  later(t + maxc * 120 + 60, function() {
   rows.forEach(function(r) {
    r.classList.add('on');
   });
  });
  t += maxc * 120 + 400;
  later(t + 300, function() {
   sums.forEach(function(b) {
    var v = +b.dataset.v, n = 0;
    (function tick() {
     if (!run) {
      return;
     }
     n++;
     b.textContent = String(Math.min(v, n));
     if (n < v) {
      tms.push(setTimeout(tick, v > 20 ? 28 : 160));
     }
    })();
   });
  });
 }
 function start() {
  if (run) {
   return;
  }
  run = true;
  play();
 }
 function stop() {
  run = false;
  tms.forEach(clearTimeout);
  tms = [];
  rows.forEach(function(r) {
   r.classList.add('on');
   [].slice.call(r.querySelectorAll('.kw-c')).forEach(function(c) {
    c.classList.add('on');
   });
  });
  sums.forEach(function(b) {
   b.textContent = b.dataset.v;
  });
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
