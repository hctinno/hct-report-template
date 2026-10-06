(function() {
 var root = document.getElementById('two-view-status');
 if (!root) {
  return;
 }
 var wr = root.querySelector('.wrap'), mk = root.querySelector('.e8-mk'), btns = [].slice.call(root.querySelectorAll('.e8-tabs button'));
 if (!wr || !mk) {
  return;
 }
 var sel = null;
 function calc() {
  var v = sel !== null ? sel : mk.classList.contains('on') && !document.body.classList.contains('expand') ? 1 : 0;
  if (wr.getAttribute('data-e8') !== String(v)) {
   wr.setAttribute('data-e8', v);
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
  new MutationObserver(function() {
   sel = null;
   calc();
  }).observe(mk, {
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
