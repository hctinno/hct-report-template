(function() {
 var root = document.getElementById('apx-gpu-stack');
 if (!root) {
  return;
 }
 root.addEventListener('click', function(e) {
  var b = e.target.closest('.k9-seg button');
  if (!b) {
   return;
  }
  e.stopPropagation();
  [].forEach.call(b.parentNode.children, function(x) {
   x.setAttribute('aria-pressed', x === b);
  });
  root.classList.toggle('plan', b.getAttribute('data-v') === 'plan');
 }, true);
})();
