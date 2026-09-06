// 덱 뷰어 — 슬라이드 넘김, 축척, 쪽번호·문서명 자동 채움, 발표자 노트.
// 4종 용도별 덱이 이 파일 하나를 공유한다. 단일 파일로 만들 때는 인라인된다.

(function () {
  var stage  = document.getElementById('stage');
  var frames = Array.prototype.slice.call(document.querySelectorAll('.br-frame'));
  var notes  = document.getElementById('notes');
  var notesText = document.getElementById('notes-text');
  var i = 0, showNotes = false;
  var allMode = new URLSearchParams(location.search).get('all') === '1';
  var deckTitle = stage.dataset.deckTitle || '';

  // 푸터의 문서명과 쪽번호는 여기서 채운다. 슬라이드를 넣거나 빼도 번호가 어긋나지 않는다.
  frames.forEach(function (f, n) {
    var foot = f.querySelector('.br-footer');
    if (!foot) return;                       // 표지·간지·마무리는 푸터가 없다
    var page = String(n + 1).padStart(2, '0');
    foot.innerHTML = deckTitle
      ? deckTitle + ' <strong>' + page + '</strong>'
      : '<strong>' + page + '</strong>';
  });

  function scale() {
    var s = Math.min(window.innerWidth / 1920,
                     (window.innerHeight - (showNotes ? window.innerHeight * .34 : 0)) / 1080);
    frames.forEach(function (f) { f.style.transform = 'scale(' + s + ')'; });
  }

  function show(n) {
    i = (n + frames.length) % frames.length;
    frames.forEach(function (f, k) {
      f.classList.toggle('is-active', k === i);
      // 애니메이션은 활성 슬라이드에서만 재생한다
      if (k === i) { f.removeAttribute('data-deck-active'); void f.offsetWidth; f.setAttribute('data-deck-active', ''); }
      else { f.removeAttribute('data-deck-active'); }
    });
    document.getElementById('pos').textContent = (i + 1) + ' / ' + frames.length;
    document.getElementById('name').textContent = frames[i].dataset.label;
    notesText.textContent = frames[i].dataset.notes || '(이 슬라이드에는 노트가 없다)';
  }

  function toggleNotes() {
    showNotes = !showNotes;
    notes.hidden = !showNotes;
    scale();
  }

  if (allMode) {
    document.body.classList.add('all-mode');
    frames.forEach(function (f) {
      f.setAttribute('data-deck-active', '');
      f.style.transform = 'none';            // 원본 크기 유지 (스크린샷·PDF용)
    });
    return;
  }

  window.addEventListener('resize', scale);
  document.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') { show(i + 1); e.preventDefault(); }
    if (e.key === 'ArrowLeft' || e.key === 'PageUp') { show(i - 1); e.preventDefault(); }
    if (e.key === 'Home') show(0);
    if (e.key === 'End') show(frames.length - 1);
    if (e.key === 'n' || e.key === 'N') toggleNotes();
  });
  document.getElementById('prev').onclick = function () { show(i - 1); };
  document.getElementById('next').onclick = function () { show(i + 1); };
  document.getElementById('notes-btn').onclick = toggleNotes;
  // 전체 보기는 제자리에서 켜고 끈다. URL 을 바꾸면 새로고침이 되고, 되돌아갈 길도 없다.
  // Artifact 처럼 주소를 못 바꾸는 곳에서도 이 방식이면 동작한다.
  var allBtn = document.getElementById('all');
  allBtn.onclick = function () {
    var on = !document.body.classList.contains('all-mode--live');
    document.body.classList.toggle('all-mode', on);
    document.body.classList.toggle('all-mode--live', on);
    frames.forEach(function (f) {
      if (on) { f.setAttribute('data-deck-active', ''); f.style.transform = 'none'; }
      else { f.removeAttribute('data-deck-active'); f.style.transform = ''; }
    });
    allBtn.textContent = on ? '한 장씩' : '전체 보기';
    if (on) { window.scrollTo(0, 0); } else { scale(); show(i); }
  };

  scale();
  show(0);
})();
