(function() {
 var root = document.getElementById('benchmark-table');
 if (!root) {
  return;
 }
 var tabs = [].slice.call(root.querySelectorAll('.bm-tab'));
 if (!tabs.length) {
  return;
 }
 tabs.forEach(function(t) {
  t.addEventListener('click', function(ev) {
   ev.stopPropagation();
   var wrap = t.closest('.bm-evc');
   if (!wrap) {
    return;
   }
   wrap.querySelectorAll('.bm-tab').forEach(function(x) {
    x.classList.toggle('on', x === t);
   });
   wrap.querySelectorAll('.bm-ep').forEach(function(p) {
    p.hidden = p.dataset.e !== t.dataset.e;
   });
  });
 });
})();
