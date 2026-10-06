document.querySelectorAll('[data-radar-panel]').forEach(b => b.addEventListener('click', e => {
 e.stopPropagation();
 document.querySelectorAll('[data-radar-panel]').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
 [ 0, 1 ].forEach(i => document.getElementById('radar-evidence-' + i).hidden = String(i) !== b.dataset.radarPanel);
}));
