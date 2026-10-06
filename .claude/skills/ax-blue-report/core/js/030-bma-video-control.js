(function() {
 const modal = document.getElementById('bma-video-modal');
 const player = modal.querySelector('video');
 let sourceUrl = null, returnFocus = null;
 function prepare() {
  if (sourceUrl) {
   return;
  }
  {
   const t = document.getElementById('bma-video-data').textContent.trim(), b = atob(t), u = new Uint8Array(b.length);
   for (let i = 0; i < b.length; i++) {
    u[i] = b.charCodeAt(i);
   }
   sourceUrl = URL.createObjectURL(new Blob([ u ], {
    type: 'video/mp4'
   }));
  }
  player.src = sourceUrl;
  player.load();
 }
 function close() {
  player.pause();
  player.currentTime = 0;
  modal.classList.remove('on');
  if (returnFocus) {
   returnFocus.focus();
  }
 }
 document.getElementById('deck').addEventListener('click', function(event) {
  const button = event.target.closest('.bma-video-open');
  if (!button) {
   return;
  }
  event.stopPropagation();
  returnFocus = button;
  prepare();
  modal.classList.add('on');
  modal.querySelector('.bma-video-close').focus();
  player.play().catch(function() {});
 });
 modal.addEventListener('click', function(event) {
  if (event.target === modal || event.target.closest('.bma-video-close')) {
   close();
  }
 });
 addEventListener('keydown', function(event) {
  if (!modal.classList.contains('on')) {
   return;
  }
  if (event.key === 'Escape') {
   event.preventDefault();
   event.stopImmediatePropagation();
   close();
  } else if ([ 'ArrowRight', 'ArrowLeft', 'PageDown', 'PageUp', ' ' ].includes(event.key)) {
   event.stopImmediatePropagation();
  }
 }, true);
})();
