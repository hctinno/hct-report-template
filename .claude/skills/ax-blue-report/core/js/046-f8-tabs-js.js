(function() {
 var root = document.getElementById('two-view-intro');
 if (!root) {
  return;
 }
 var bd = root.querySelector('.f6'), m1 = root.querySelector('.f8-m1'), m2 = root.querySelector('.f8-m2'), btns = [].slice.call(root.querySelectorAll('.f8-tabs button'));
 if (!bd || !m1 || !m2) {
  return;
 }
 var sel = null;
 function calc() {
  var ex = document.body.classList.contains('expand');
  var v = sel !== null ? sel : m2.classList.contains('on') && !ex ? 1 : 0;
  var r = ex || sel !== null || v === 1 || m1.classList.contains('on') ? 1 : 0;
  if (bd.getAttribute('data-v') !== String(v)) {
   bd.setAttribute('data-v', v);
  }
  if (bd.getAttribute('data-r') !== String(r)) {
   bd.setAttribute('data-r', r);
  }
  btns.forEach(function(b) {
   b.setAttribute('aria-selected', String(+b.getAttribute('data-v') === v));
  });
 }
 btns.forEach(function(b) {
  b.addEventListener('click', function(e) {
   e.stopPropagation();
   e.preventDefault();
   sel = +b.getAttribute('data-v');
   calc();
  });
 });
 if (window.MutationObserver) {
  var mo = new MutationObserver(function() {
   sel = null;
   calc();
  });
  mo.observe(m1, {
   attributes: true,
   attributeFilter: [ 'class' ]
  });
  mo.observe(m2, {
   attributes: true,
   attributeFilter: [ 'class' ]
  });
  new MutationObserver(calc).observe(document.body, {
   attributes: true,
   attributeFilter: [ 'class' ]
  });
 }
 calc();
})();
