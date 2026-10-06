(function() {
 var root = document.getElementById('seat-grid');
 if (!root) {
  return;
 }
 var main = root.querySelector('.af2-main'), cards = [].slice.call(root.querySelectorAll('.af2-st')), marks = [].slice.call(root.querySelectorAll('.af2-m1,.af2-m2,.af2-m3'));
 if (!main || !cards.length) {
  return;
 }
 function shown(c) {
  return !c.classList.contains('fr') || c.classList.contains('on') || document.body.classList.contains('expand');
 }
 cards.forEach(function(c, k) {
  c.setAttribute('tabindex', '0');
  c.setAttribute('role', 'button');
  c.setAttribute('aria-label', (c.querySelector('.af2-tag') || {}).textContent + ' 보기');
 });
 function pick(c) {
  var k = cards.indexOf(c);
  if (k < 0 || !shown(c)) {
   return false;
  }
  if (main.getAttribute('data-sel') === String(k)) {
   main.removeAttribute('data-sel');
  } else {
   main.setAttribute('data-sel', k);
  }
  return true;
 }
 root.addEventListener('click', function(e) {
  var c = e.target.closest('.af2-st');
  if (!c || e.target.closest('.ev-pin')) {
   return;
  }
  if (pick(c)) {
   e.stopPropagation();
   e.preventDefault();
  }
 }, true);
 root.addEventListener('keydown', function(e) {
  if (e.key !== 'Enter' && e.key !== ' ') {
   return;
  }
  var c = e.target.closest && e.target.closest('.af2-st');
  if (c && pick(c)) {
   e.stopPropagation();
   e.preventDefault();
  }
 }, true);
 if (window.MutationObserver) {
  var mo = new MutationObserver(function() {
   main.removeAttribute('data-sel');
  });
  marks.forEach(function(m) {
   mo.observe(m, {
    attributes: true,
    attributeFilter: [ 'class' ]
   });
  });
 }
})();
