(() => {
 const reduce = matchMedia('(prefers-reduced-motion: reduce)');
 document.querySelectorAll('.role-platform-slide').forEach(root => {
  let runs = [], visible = false, timer = null, paused = false;
  const button = root.querySelector('.role-motion-replay');
  if (!button) {
   return;
  }
  button.textContent = 'Ⅱ 움직임 일시정지';
  function stop() {
   clearTimeout(timer);
   timer = null;
   runs.forEach(a => a.cancel());
   runs = [];
   root.querySelectorAll('.flow-motion-overlay').forEach(e => e.remove());
  }
  function travel(svg, path, delay, color) {
   const line = path.cloneNode();
   line.removeAttribute('opacity');
   line.classList.add('flow-motion-overlay');
   line.setAttribute('fill', 'none');
   line.setAttribute('stroke', color);
   line.setAttribute('stroke-width', '5');
   line.setAttribute('stroke-linecap', 'round');
   line.setAttribute('aria-hidden', 'true');
   line.style.pointerEvents = 'none';
   svg.append(line);
   const len = path.getTotalLength();
   line.style.strokeDasharray = len;
   line.style.strokeDashoffset = len;
   runs.push(line.animate([ {
    strokeDashoffset: len,
    opacity: 0
   }, {
    strokeDashoffset: len,
    opacity: 1,
    offset: .05
   }, {
    strokeDashoffset: 0,
    opacity: 1,
    offset: .8
   }, {
    strokeDashoffset: 0,
    opacity: 0
   } ], {
    duration: 850,
    delay: delay,
    fill: 'both',
    easing: 'ease-out'
   }));
  }
  function play() {
   stop();
   if (reduce.matches || document.hidden || paused || !visible) {
    return;
   }
   const svgs = root.querySelectorAll('.role-flow-compare svg');
   if (svgs.length) {
    const left = svgs[0].querySelectorAll('g>path');
    left.forEach((p, i) => travel(svgs[0], p, i % 2 ? 950 : 100, 'var(--ink2)'));
    svgs[1].querySelectorAll('[data-flow]').forEach(p => travel(svgs[1], p, p.dataset.flow === 'share' ? 1850 : p.dataset.flow === 'return' ? 2700 : 3450, p.dataset.flow === 'share' ? 'var(--ok)' : 'var(--amber)'));
    timer = setTimeout(play, 5500);
   } else {
    const svg = root.querySelector('.sankey-panel svg');
    svg.querySelectorAll('g>path').forEach(p => {
     const line = p.cloneNode();
     line.classList.add('flow-motion-overlay');
     line.setAttribute('fill', 'none');
     line.setAttribute('stroke-width', '3');
     line.setAttribute('stroke-linecap', 'round');
     line.setAttribute('stroke-dasharray', '5 15');
     line.setAttribute('opacity', '.65');
     line.setAttribute('aria-hidden', 'true');
     line.style.pointerEvents = 'none';
     svg.append(line);
     runs.push(line.animate([ {
      strokeDashoffset: 0
     }, {
      strokeDashoffset: -20
     } ], {
      duration: 1600,
      iterations: Infinity,
      easing: 'linear'
     }));
    });
   }
  }
  button.addEventListener('click', e => {
   e.stopPropagation();
   paused = !paused;
   button.textContent = paused ? '▶ 움직임 재생' : 'Ⅱ 움직임 일시정지';
   if (paused) {
    stop();
   } else {
    play();
   }
  });
  new IntersectionObserver(entries => {
   for (const e of entries) {
    if (e.isIntersecting && e.intersectionRatio > .6) {
     if (!visible) {
      visible = true;
      play();
     }
    } else {
     visible = false;
     stop();
    }
   }
  }, {
   threshold: [ 0, .6 ]
  }).observe(root);
  reduce.addEventListener('change', () => {
   if (reduce.matches) {
    stop();
   } else {
    play();
   }
  });
  document.addEventListener('visibilitychange', () => {
   if (document.hidden) {
    stop();
   } else {
    play();
   }
  });
 });
})();
