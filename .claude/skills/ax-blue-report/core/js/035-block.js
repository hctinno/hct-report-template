(function() {
 var lb = document.createElement('div');
 lb.className = 'pz-lb';
 lb.innerHTML = '<img alt=""><div class="pz-lbab" role="group" aria-label="포스터 시안 선택"></div><span>닫기 · Esc · ← → 시안</span>';
 document.body.appendChild(lb);
 var li = lb.querySelector('img'), lab = lb.querySelector('.pz-lbab'), curFig = null;
 function cur(f) {
  var im = f.querySelector('img[data-v]:not(.pz-off)');
  return im ? im.getAttribute('data-v') : '';
 }
 function show(f) {
  var im = f.querySelector('img[data-v]:not(.pz-off)');
  if (!im) {
   return;
  }
  li.src = im.src;
  li.alt = im.alt;
  lab.innerHTML = '';
  [].forEach.call(f.querySelectorAll('.pz-ab button'), function(b) {
   var c = document.createElement('button');
   c.type = 'button';
   c.textContent = b.textContent;
   c.setAttribute('data-v', b.getAttribute('data-v'));
   c.setAttribute('aria-pressed', b.getAttribute('aria-pressed'));
   lab.appendChild(c);
  });
 }
 function pick(f, v) {
  if (!f || !v) {
   return;
  }
  [].forEach.call(f.querySelectorAll('.pz-ab button'), function(x) {
   x.setAttribute('aria-pressed', x.getAttribute('data-v') === v ? 'true' : 'false');
  });
  [].forEach.call(f.querySelectorAll('img[data-v]'), function(im) {
   im.classList.toggle('pz-off', im.getAttribute('data-v') !== v);
  });
  if (curFig === f && lb.classList.contains('on')) {
   show(f);
  }
 }
 function step(k) {
  if (!curFig) {
   return;
  }
  var vs = [].map.call(curFig.querySelectorAll('img[data-v]'), function(i) {
   return i.getAttribute('data-v');
  });
  var i = vs.indexOf(cur(curFig));
  pick(curFig, vs[(i + k + vs.length) % vs.length]);
 }
 function close() {
  lb.classList.remove('on');
  curFig = null;
 }
 lb.addEventListener('click', function(e) {
  e.stopPropagation();
  var b = e.target.closest('.pz-lbab button');
  if (b) {
   pick(curFig, b.getAttribute('data-v'));
   return;
  }
  close();
 });
 document.addEventListener('keydown', function(e) {
  if (!lb.classList.contains('on')) {
   return;
  }
  if (e.key === 'Escape') {
   close();
  } else if (e.key === 'ArrowRight') {
   step(1);
  } else if (e.key === 'ArrowLeft') {
   step(-1);
  }
  e.stopPropagation();
  e.preventDefault();
 }, true);
 [].forEach.call(document.querySelectorAll('.pz-fig'), function(f) {
  [].forEach.call(f.querySelectorAll('.pz-ab button'), function(b) {
   b.addEventListener('click', function(e) {
    e.preventDefault();
    e.stopPropagation();
    pick(f, b.getAttribute('data-v'));
   });
   b.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' || e.key === ' ') {
     e.preventDefault();
     e.stopPropagation();
     pick(f, b.getAttribute('data-v'));
    }
   });
  });
  f.addEventListener('click', function(e) {
   e.stopPropagation();
   if (e.target.closest('.pz-ab')) {
    return;
   }
   curFig = f;
   show(f);
   lb.classList.add('on');
  });
 });
})();
