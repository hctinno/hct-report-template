(function() {
 var root = document.getElementById('principle-compare');
 if (!root) {
  return;
 }
 var items = root.querySelector('.rl-items'), bins = [].slice.call(root.querySelectorAll('.hb-bin'));
 if (!items || !bins.length) {
  return;
 }
 var CAP = 9;
 function sync(anim) {
  var n = items.children.length, c = [ 0, 0, 0, 0, 0, 0 ];
  for (var i = 0; i < n; i++) {
   c[i % 6]++;
  }
  bins.forEach(function(b, k) {
   var st = b.querySelector('.hb-stk'), want = Math.min(c[k], CAP), have = st.children.length;
   b.querySelector('.hb-n').textContent = c[k] ? c[k] + '건' : '';
   while (have > want) {
    st.removeChild(st.lastChild);
    have--;
   }
   while (have < want) {
    var e = document.createElement('i');
    if (anim && !document.body.classList.contains('expand') || anim === 'force') {
     e.className = 'hb-drop';
     b.classList.add('hb-hit');
     setTimeout(function(bb) {
      return function() {
       bb.classList.remove('hb-hit');
      };
     }(b), 650);
    }
    st.appendChild(e);
    have++;
   }
  });
 }
 new MutationObserver(function() {
  sync(root.classList.contains('in') ? 'force' : false);
 }).observe(items, {
  childList: true
 });
 sync(false);
})();
