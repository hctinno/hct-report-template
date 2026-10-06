(function() {
 const roots = Object.assign({}, window.AXBR_LINKS || {});
 const modal = document.getElementById('now-source-modal'), frame = modal.querySelector('iframe'), head = modal.querySelector('h3'), badge = modal.querySelector('.now-source-page');
 let styles = '';
 let returnFocus = null;
 function target(key) {
  const r = roots[key];
  const id = r ? r[0] : key;
  const el = document.getElementById(id);
  return el && el.classList.contains('sl') ? el : null;
 }
 function open(button) {
  if (!styles) {
   styles = [ ...document.querySelectorAll('style') ].map(s => s.outerHTML).join('');
  }
  const src = target(button.dataset.nowSource);
  if (!src) {
   return;
  }
  returnFocus = button;
  const clone = src.cloneNode(true);
  clone.querySelectorAll('.fr').forEach(x => x.classList.add('on'));
  clone.querySelectorAll('.f6[data-v]').forEach(x => {
   x.setAttribute('data-v', '0');
   x.setAttribute('data-r', '1');
  });
  const title = (src.getAttribute('data-t') || '관련 본문').replace(/^\d+\s*/, '').replace(/^부록\s*\d*\s*·\s*/, '');
  const isA = src.classList.contains('apx'), pg = isA ? String([ ...document.querySelectorAll('#deck .sl.apx') ].indexOf(src) + 1) : ((src.getAttribute('data-t') || '').match(/^\d+/) || [ '' ])[0];
  badge.textContent = (isA ? '부록 ' : '본문 ') + pg + '쪽';
  head.textContent = title;
  frame.title = title + ' 본문';
  const help = modal.querySelector('.now-source-help');
  if (help) {
   if (!help.dataset.def) {
    help.dataset.def = help.textContent;
   }
   help.textContent = button.dataset.help || help.dataset.def;
  }
  const frameCSS = '<style>html,body{margin:0!important;width:1920px!important;height:1080px!important;overflow:hidden!important;background:var(--paper)!important}#deck{display:block!important;width:1920px!important;height:1080px!important;overflow:hidden!important}.sl{width:1920px!important;height:1080px!important;min-height:1080px!important;flex-basis:1080px!important;overflow:hidden!important}.ev-pin,.ev-open,.now-ref,.v60-yr,.bma-video-open{pointer-events:none}</style>';
  frame.srcdoc = '<!doctype html><html lang="ko"><head><meta charset="utf-8">' + styles + frameCSS + '</head><body><main id="deck">' + clone.outerHTML + '</main></body></html>';
  frame.onload = function() {
   try {
    frame.contentDocument.addEventListener('keydown', function(ev) {
     if (ev.key === 'Escape') {
      ev.preventDefault();
      close();
     }
    }, true);
   } catch (_) {}
  };
  modal.classList.add('on');
  fit();
  modal.querySelector('.now-source-close').focus();
 }
 function fit() {
  const k = Math.min(innerWidth / 1920, innerHeight / 1080);
  frame.style.transform = 'scale(' + k + ')';
 }
 addEventListener('resize', () => {
  if (modal.classList.contains('on')) {
   fit();
  }
 });
 function close() {
  modal.classList.remove('on');
  frame.removeAttribute('srcdoc');
  if (returnFocus) {
   returnFocus.focus();
  }
 }
 document.getElementById('deck').addEventListener('click', function(event) {
  const button = event.target.closest('[data-now-source]');
  if (!button || !target(button.dataset.nowSource)) {
   return;
  }
  event.preventDefault();
  event.stopPropagation();
  open(button);
 });
 modal.addEventListener('click', event => {
  if (event.target === modal || event.target.closest('.now-source-close')) {
   close();
  }
 });
 window.addEventListener('keydown', event => {
  if (!modal.classList.contains('on')) {
   return;
  }
  if (event.key === 'Escape') {
   event.preventDefault();
   event.stopImmediatePropagation();
   close();
  } else if ([ 'ArrowRight', 'ArrowLeft', 'PageDown', 'PageUp', ' ', 'Enter' ].includes(event.key)) {
   event.preventDefault();
   event.stopImmediatePropagation();
  }
 }, true);
})();
