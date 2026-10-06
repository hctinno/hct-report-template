(function() {
 const payload = JSON.parse(document.getElementById('bma-rfp-payload-2').textContent);
 const modal = document.getElementById('bma-rfp-modal-2'), evidence = document.getElementById('evm'), frame = modal.querySelector('iframe');
 let loaded = false, returnFocus = null, pendingHighlight = null;
 function jumpHighlight(index) {
  if (!loaded) {
   pendingHighlight = index;
   return;
  }
  const item = frame.contentDocument.querySelectorAll('.bma-rfp-highlight')[index];
  if (!item) {
   return;
  }
  item.scrollIntoView({
   block: 'center',
   behavior: 'auto'
  });
  modal.querySelectorAll('.bma-rfp-jumps button').forEach((button, i) => button.classList.toggle('active', i === index));
 }
 function jump(id) {
  if (!loaded) {
   return;
  }
  const doc = frame.contentDocument, target = id ? doc.getElementById(id) : doc.documentElement;
  if (target) {
   target.scrollIntoView({
    block: 'start'
   });
  }
 }
 function open(button) {
  returnFocus = button;
  evidence.classList.remove('on');
  modal.classList.add('on');
  if (!loaded) {
   frame.addEventListener('load', () => {
    loaded = true;
    setTimeout(() => {
     if (pendingHighlight !== null) {
      jumpHighlight(pendingHighlight);
      pendingHighlight = null;
     } else {
      jump(null);
     }
    }, 120);
   }, {
    once: true
   });
   frame.srcdoc = payload.html;
  } else {
   jump(null);
  }
  modal.querySelector('.bma-rfp-close').focus();
 }
 function close() {
  modal.classList.remove('on');
  evidence.classList.add('on');
  if (returnFocus) {
   returnFocus.focus();
  }
 }
 function download() {
  const binary = atob(payload.hwp), bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
   bytes[i] = binary.charCodeAt(i);
  }
  const url = URL.createObjectURL(new Blob([ bytes ], {
   type: 'text/plain'
  }));
  const a = document.createElement('a');
  a.href = url;
  a.download = '예시_사업_2단계_제안요청서_가상.txt';
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 3e4);
 }
 evidence.querySelector('.evt').addEventListener('click', event => {
  const b = event.target.closest('.bma-rfp-open-2');
  if (b) {
   event.stopPropagation();
   open(b);
  }
 });
 modal.addEventListener('click', event => {
  if (event.target === modal || event.target.closest('.bma-rfp-close')) {
   close();
   return;
  }
  const highlight = event.target.closest('[data-highlight]');
  if (highlight) {
   jumpHighlight(Number(highlight.dataset.highlight));
   return;
  }
  const action = event.target.closest('[data-action]')?.dataset.action;
  if (action === 'background') {
   jump('bma-rfp2-background');
  }
  if (action === 'scope') {
   jump('bma-rfp2-scope');
  }
  if (action === 'top') {
   jump(null);
  }
  if (action === 'download') {
   download();
  }
 });
 addEventListener('keydown', event => {
  if (modal.classList.contains('on') && event.key === 'Escape') {
   event.preventDefault();
   event.stopImmediatePropagation();
   close();
  }
 }, true);
})();
