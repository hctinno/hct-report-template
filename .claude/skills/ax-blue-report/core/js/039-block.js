(function() {
 document.querySelectorAll('.rp48').forEach(function(b) {
  b.addEventListener('click', function(e) {
   e.stopPropagation();
   var s = b.closest('.sl');
   if (!s) {
    return;
   }
   s.classList.add('rs48');
   void s.offsetWidth;
   requestAnimationFrame(function() {
    s.classList.remove('rs48');
   });
  });
 });
})();
