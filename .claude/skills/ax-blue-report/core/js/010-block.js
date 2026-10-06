(function() {
 var root = document.getElementById('definition-steps');
 if (!root) {
  return;
 }
 var st = root.querySelector('.ax-stages'), mk = root.querySelector('.ax-mark');
 function sync() {
  st.classList.toggle('go', mk.classList.contains('on'));
 }
 new MutationObserver(sync).observe(mk, {
  attributes: true,
  attributeFilter: [ 'class' ]
 });
 sync();
})();
