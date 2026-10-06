(() => {
 const reduce = matchMedia('(prefers-reduced-motion:reduce)');
 function pulse(e) {
  if (!reduce.matches) {
   e.animate([ {
    opacity: .6
   }, {
    opacity: 1
   } ], {
    duration: 240,
    easing: 'ease-out'
   });
  }
 }
 const modes = [ ...document.querySelectorAll('.focus-evolution .work-mode') ];
 function chooseMode(e) {
  modes.forEach(x => x.setAttribute('aria-pressed', String(x === e)));
  pulse(e.querySelector('svg'));
 }
 modes.forEach(e => {
  e.addEventListener('click', v => {
   v.stopPropagation();
   chooseMode(e);
  });
  e.addEventListener('keydown', v => {
   if (v.key === 'Enter' || v.key === ' ') {
    v.preventDefault();
    v.stopPropagation();
    chooseMode(e);
   }
  });
 });
 document.querySelectorAll('.radar-zoom-controls button').forEach(b => b.addEventListener('click', e => {
  e.stopPropagation();
  b.parentElement.querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
  document.querySelector('.radar-zoom-stage').dataset.view = b.dataset.zoom;
 }));
 const horizon = document.querySelector('.horizon-redesign');
 horizon?.querySelectorAll('[data-horizon]').forEach(b => b.addEventListener('click', e => {
  e.stopPropagation();
  horizon?.querySelectorAll('[data-horizon]').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
  horizon.querySelectorAll('.horizon-view').forEach((x, i) => {
   x.hidden = i !== +b.dataset.horizon;
   if (!x.hidden) {
    pulse(x);
   }
  });
 }));
 document.querySelectorAll('[data-security]').forEach(b => b.addEventListener('click', e => {
  e.stopPropagation();
  b.parentElement.querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
  document.querySelectorAll('#apx-data-pipeline .security-branches article').forEach((x, i) => {
   const on = +b.dataset.security === i + 1;
   x.classList.toggle('route-selected', on);
   if (on) {
    pulse(x);
   }
  });
 }));
})();
