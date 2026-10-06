(function() {
 var root = document.getElementById('status-columns'), modal = document.getElementById('now-source-modal'), deck = document.getElementById('deck');
 if (!root || !modal || !deck) {
  return;
 }
 var ORDER = [ 'apx-gpu-stack', 'apx-onprem', 'apx-system-flow', 'apx-donut-bars', 'apx-data-pipeline', 'apx-hub-scenes', 'apx-poster-survey', 'apx-poster-contest' ], idx = 0;
 function btn(k) {
  return root.querySelector('.now-ref[data-now-source="' + k + '"]');
 }
 function present() {
  return document.body.classList.contains('present');
 }
 function onSlide() {
  var r = root.getBoundingClientRect();
  return r.height > 0 && r.top < innerHeight / 2 && r.bottom > innerHeight / 2;
 }
 function isOpen() {
  return modal.classList.contains('on');
 }
 function close() {
  var c = modal.querySelector('.now-source-close');
  if (c) {
   c.click();
  }
  modal.classList.remove('seq');
 }
 root.addEventListener('click', function(e) {
  var b = e.target.closest('.now-ref[data-now-source]');
  if (!b) {
   return;
  }
  var k = ORDER.indexOf(b.getAttribute('data-now-source'));
  if (k >= 0) {
   idx = k + 1;
  }
 }, true);
 deck.addEventListener('click', function(e) {
  if (!present() || !onSlide() || isOpen()) {
   return;
  }
  if (e.target.closest('a,button,input,select,textarea,label,summary,[data-int],[role="button"],[role="tab"],[aria-pressed]')) {
   return;
  }
  if (idx >= ORDER.length) {
   return;
  }
  var k = idx, b = btn(ORDER[k]);
  if (!b) {
   return;
  }
  e.stopPropagation();
  e.preventDefault();
  b.click();
  idx = k + 1;
  modal.classList.add('seq');
  var pg = modal.querySelector('.now-source-page');
  if (pg) {
   pg.textContent = pg.textContent + ' · ' + (k + 1) + '/' + ORDER.length;
  }
 }, true);
 modal.addEventListener('click', function(e) {
  if (!present() || !isOpen()) {
   return;
  }
  if (e.target.closest('.now-source-close')) {
   modal.classList.remove('seq');
   return;
  }
  e.stopPropagation();
  e.preventDefault();
  close();
 }, true);
 if ('IntersectionObserver' in window) {
  new IntersectionObserver(function(es) {
   es.forEach(function(x) {
    if (!x.isIntersecting || x.intersectionRatio < .5) {
     if (!isOpen()) {
      idx = 0;
     }
    }
   });
  }, {
   threshold: [ 0, .5 ]
  }).observe(root);
 }
})();
