(function() {
 var b = document.body, last = b.className;
 function ping() {
  [].slice.call(document.querySelectorAll('.fr')).forEach(function(e) {
   e.classList.add('sync-ping');
   e.classList.remove('sync-ping');
  });
 }
 new MutationObserver(function() {
  if (b.className !== last) {
   last = b.className;
   ping();
  }
 }).observe(b, {
  attributes: true,
  attributeFilter: [ 'class' ]
 });
})();
