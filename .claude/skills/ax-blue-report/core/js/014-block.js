(function() {
 var t = document.getElementById('benchmark-table');
 if (t) {
  var tbl = t.querySelector('.bm-tbl'), foot = t.querySelector('.bm-foot'), rows = [].slice.call(t.querySelectorAll('.bm-row')), panes = [].slice.call(t.querySelectorAll('.bm-evc')), mks = [].slice.call(t.querySelectorAll('.bm-mk'));
  var pick = 0;
  function sy() {
   var n = 0;
   mks.forEach(function(m, i) {
    if (m.classList.contains('on')) {
     n = i + 1;
    }
   });
   var fo = !!(foot && foot.classList.contains('on')) || n >= rows.length;
   tbl.classList.toggle('take', fo);
   var show = pick > 0 ? pick : n;
   rows.forEach(function(r, i) {
    r.classList.toggle('focus', show === i + 1);
    r.classList.toggle('dimr', show > 0 && show !== i + 1 && !fo);
   });
   panes.forEach(function(p) {
    var k = parseInt(p.getAttribute('data-i') || '0', 10);
    p.hidden = k !== show;
   });
  }
  rows.forEach(function(r, i) {
   r.addEventListener('click', function() {
    pick = pick === i + 1 ? 0 : i + 1;
    sy();
   });
  });
  var mo = new MutationObserver(function() {
   pick = 0;
   sy();
  });
  mks.forEach(function(m) {
   mo.observe(m, {
    attributes: true,
    attributeFilter: [ 'class' ]
   });
  });
  if (foot) {
   mo.observe(foot, {
    attributes: true,
    attributeFilter: [ 'class' ]
   });
  }
  sy();
 }
})();
