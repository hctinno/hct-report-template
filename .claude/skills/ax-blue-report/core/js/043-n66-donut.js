(function() {
 var w = document.querySelector('#apx-donut-bars .n66');
 if (!w) {
  return;
 }
 var T = 46, S = [].slice.call(w.querySelectorAll('.n66-s')), L = [].slice.call(w.querySelectorAll('.n66-leg li')), cb = w.querySelector('.n66-c b'), cs = w.querySelector('.n66-c span');
 function on(k) {
  w.classList.toggle('hov', k !== null);
  S.forEach(function(x) {
   x.classList.toggle('on', x.getAttribute('data-k') === String(k));
  });
  L.forEach(function(x) {
   x.classList.toggle('on', x.getAttribute('data-k') === String(k));
  });
  if (k === null) {
   cb.textContent = T;
   cs.textContent = '전체 계정';
   return;
  }
  var li = L[k], v = +li.querySelector('em').textContent;
  cb.textContent = v;
  cs.textContent = li.querySelector('b').textContent + ' · ' + Math.round(v / T * 100) + '%';
 }
 S.concat(L).forEach(function(x) {
  var k = +x.getAttribute('data-k');
  x.addEventListener('mouseenter', function() {
   on(k);
  });
  x.addEventListener('focus', function() {
   on(k);
  });
  x.addEventListener('mouseleave', function() {
   on(null);
  });
  x.addEventListener('blur', function() {
   on(null);
  });
 });
})();
