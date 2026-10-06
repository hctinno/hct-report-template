(function() {
 var s = document.getElementById('apx-hub-scenes');
 if (!s) {
  return;
 }
 var tabs = [].slice.call(s.querySelectorAll('.hv-tab')), panes = [].slice.call(s.querySelectorAll('.hv-pane'));
 tabs.forEach(function(t) {
  t.addEventListener('click', function(e) {
   e.preventDefault();
   e.stopPropagation();
   var v = t.getAttribute('data-v');
   tabs.forEach(function(x) {
    var on = x === t;
    x.classList.toggle('on', on);
    x.setAttribute('aria-pressed', on ? 'true' : 'false');
   });
   panes.forEach(function(p) {
    p.classList.toggle('on', p.getAttribute('data-v') === v);
   });
  });
 });
})();
