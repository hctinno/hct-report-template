(function() {
 var root = document.getElementById('coaching-demo'), k = root && root.querySelector('.k21');
 if (!k) {
  return;
 }
 var mks = [].slice.call(k.querySelectorAll('.k21-mk')), scs = [].slice.call(k.querySelectorAll('.k21-sc')), btns = [].slice.call(k.querySelectorAll('.k21-rl button'));
 var cur = -1, tm = [];
 function show(n) {
  k.setAttribute('data-st', n);
  scs.forEach(function(sc) {
   var on = +sc.getAttribute('data-sc') === n;
   sc.classList.toggle('cur', on);
   sc.classList.remove('go');
   if (on) {
    void sc.offsetWidth;
    sc.classList.add('go');
   }
  });
  btns.forEach(function(b) {
   var j = +b.getAttribute('data-k');
   b.classList.toggle('ok', j < n);
   b.classList.toggle('now', j === n);
  });
 }
 function stepOf() {
  if (document.body.classList.contains('expand')) {
   return 6;
  }
  var n = 0;
  mks.forEach(function(m) {
   if (m.classList.contains('on')) {
    n++;
   }
  });
  return n;
 }
 function stop() {
  tm.forEach(clearTimeout);
  tm = [];
 }
 function sync(force) {
  var n = stepOf();
  if (n === cur && !force) {
   return;
  }
  stop();
  cur = n;
  show(n);
 }
 var mo = new MutationObserver(function() {
  sync(false);
 });
 mks.forEach(function(m) {
  mo.observe(m, {
   attributes: true,
   attributeFilter: [ 'class' ]
  });
 });
 mo.observe(document.body, {
  attributes: true,
  attributeFilter: [ 'class' ]
 });
 if (window.IntersectionObserver) {
  new IntersectionObserver(function(es) {
   es.forEach(function(e) {
    if (e.intersectionRatio >= .55) {
     sync(true);
    }
   });
  }, {
   threshold: [ .55 ]
  }).observe(root);
 }
 btns.forEach(function(b) {
  b.addEventListener('click', function(e) {
   e.stopPropagation();
   stop();
   var n = +b.getAttribute('data-k');
   show(n);
   for (var j = n + 1; j <= 6; j++) {
    (function(j) {
     tm.push(setTimeout(function() {
      show(j);
     }, (j - n) * 5600));
    })(j);
   }
  });
 });
 setTimeout(function() {
  sync(true);
 }, 80);
})();
