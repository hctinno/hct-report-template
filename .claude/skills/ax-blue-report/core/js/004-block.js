(() => {
 document.querySelectorAll('.case-switch').forEach(list => {
  const scope = list.parentElement;
  list.querySelectorAll('button').forEach(btn => btn.addEventListener('click', e => {
   e.stopPropagation();
   list.querySelectorAll('button').forEach(b => {
    const on = b === btn;
    b.setAttribute('aria-selected', on);
    document.getElementById(b.getAttribute('aria-controls')).hidden = !on;
   });
  }));
 });
 document.querySelectorAll('.source-toggle').forEach(btn => btn.addEventListener('click', e => {
  e.stopPropagation();
  const s = btn.closest('.bd'), open = btn.getAttribute('aria-expanded') !== 'true';
  btn.setAttribute('aria-expanded', open);
  btn.textContent = open ? '사례 설명으로 돌아가기' : '전체 출처 목록 보기';
  s.querySelector('.case-detail').hidden = open;
  s.querySelector('.original-sources').hidden = !open;
 }));
})();
