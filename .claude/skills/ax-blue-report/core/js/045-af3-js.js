(function() {
 var root = document.getElementById('seat-grid');
 if (!root) {
  return;
 }
 var bd = root.querySelector('.af2'), main = root.querySelector('.af2-main');
 if (!bd || !main) {
  return;
 }
 var mk = [].slice.call(root.querySelectorAll('.af2-m1,.af2-m2,.af2-m3'));
 function calc() {
  var sel = main.getAttribute('data-sel'), n;
  if (sel !== null) {
   n = +sel;
  } else if (document.body.classList.contains('expand')) {
   n = 3;
  } else {
   n = 0;
   mk.forEach(function(m) {
    if (m.classList.contains('on')) {
     n++;
    }
   });
  }
  if (bd.getAttribute('data-st') !== String(n)) {
   bd.setAttribute('data-st', n);
  }
 }
 if (window.MutationObserver) {
  var mo = new MutationObserver(calc);
  mk.forEach(function(m) {
   mo.observe(m, {
    attributes: true,
    attributeFilter: [ 'class' ]
   });
  });
  mo.observe(main, {
   attributes: true,
   attributeFilter: [ 'data-sel' ]
  });
  mo.observe(document.body, {
   attributes: true,
   attributeFilter: [ 'class' ]
  });
 }
 calc();
})();
