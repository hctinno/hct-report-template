(function() {
 var root = document.getElementById('apx-track-ring');
 if (!root) {
  return;
 }
 var tracks = [].slice.call(root.querySelectorAll('.tr-track')), sts = [].slice.call(root.querySelectorAll('.tr-st')), cards = [].slice.call(root.querySelectorAll('.tr-card[data-i]')), empty = root.querySelector('.tr-empty');
 var pick = -1, cur = -1, tim = null, vis = false;
 function avail() {
  var out = [];
  tracks.forEach(function(t) {
   if (t.classList.contains('on') || document.body.classList.contains('expand')) {
    [].slice.call(t.querySelectorAll('.tr-st')).forEach(function(b) {
     out.push(+b.getAttribute('data-i'));
    });
   }
  });
  return out;
 }
 function show(i) {
  cur = i;
  sts.forEach(function(b) {
   b.classList.toggle('on', +b.getAttribute('data-i') === i);
  });
  cards.forEach(function(c) {
   c.hidden = +c.getAttribute('data-i') !== i;
  });
  empty.hidden = i >= 0;
 }
 function tick() {
  clearTimeout(tim);
  if (!vis) {
   return;
  }
  if (pick >= 0) {
   show(pick);
   return;
  }
  var av = avail();
  if (!av.length) {
   show(-1);
   tim = setTimeout(tick, 600);
   return;
  }
  var k = av.indexOf(cur);
  show(av[(k + 1) % av.length]);
  tim = setTimeout(tick, 2600);
 }
 sts.forEach(function(b) {
  b.addEventListener('click', function() {
   var i = +b.getAttribute('data-i');
   pick = pick === i ? -1 : i;
   if (pick < 0) {
    cur = -1;
   }
   tick();
  });
 });
 var mo = new MutationObserver(function() {
  var av = avail();
  if (pick >= 0 && av.indexOf(pick) < 0) {
   pick = -1;
  }
  if (cur >= 0 && av.indexOf(cur) < 0) {
   cur = -1;
  }
  tick();
 });
 tracks.forEach(function(t) {
  mo.observe(t, {
   attributes: true,
   attributeFilter: [ 'class' ]
  });
 });
 var io = new IntersectionObserver(function(es) {
  es.forEach(function(e) {
   vis = e.intersectionRatio >= .55;
   if (vis) {
    tick();
   } else {
    clearTimeout(tim);
   }
  });
 }, {
  threshold: [ .55 ]
 });
 io.observe(root);
 show(-1);
})();
