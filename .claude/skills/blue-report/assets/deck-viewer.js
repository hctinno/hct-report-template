// 덱 뷰어 — 슬라이드 넘김, 축척, 쪽번호·문서명 자동 채움, 발표자 노트.
// 4종 용도별 덱이 이 파일 하나를 공유한다. 단일 파일로 만들 때는 인라인된다.

(function () {
  var stage  = document.getElementById('stage');
  var frames = Array.prototype.slice.call(document.querySelectorAll('.br-frame'));
  var notes  = document.getElementById('notes');
  var notesText = document.getElementById('notes-text');
  var i = 0, showNotes = false;
  var allBtn = document.getElementById('all');
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

  // 지면 전체가 언제나 화면 안에 들어오게 맞춘다.
  //   - 가로·세로 중 더 빡빡한 쪽에 맞춘다(contain). 16:9 가 아닌 화면에서는 위아래나
  //     좌우에 여백이 남는다. 잘라 내지 않는다.
  //   - HUD 띠 높이를 빼 둔다. 안 빼면 16:9 정확히 맞는 화면에서 지면 아래 47px 가
  //     HUD 뒤로 들어가 꼬리말(문서명·쪽번호)이 가려진다.
  //   - translate(-50%,-50%) 로 되돌려 어느 창 크기에서든 가운데에 앉힌다.
  function scale() {
    var hud = document.getElementById('hud');
    var chrome = (hud && hud.offsetHeight ? hud.offsetHeight : 0)
               + (showNotes ? window.innerHeight * .34 : 0);
    // 무대를 HUD·노트 띠 위까지로 줄인다. 배율만 줄이고 무대를 그대로 두면 지면이
    // 화면 한가운데에 앉아 아래쪽이 띠 뒤로 들어간다.
    stage.style.bottom = chrome + 'px';
    var s = Math.min(window.innerWidth / 1920,
                     Math.max(window.innerHeight - chrome, 100) / 1080);
    frames.forEach(function (f) {
      f.style.transform = 'translate(-50%,-50%) scale(' + s + ')';
    });
  }

  function show(n) {
    i = (n + frames.length) % frames.length;
    frames.forEach(function (f, k) {
      f.classList.toggle('is-active', k === i);
      // 애니메이션은 활성 슬라이드에서만 재생한다
      if (k === i) { f.removeAttribute('data-deck-active'); void f.offsetWidth; f.setAttribute('data-deck-active', ''); }
      else { f.removeAttribute('data-deck-active'); }
    });
    // HUD 요소가 하나라도 없으면 여기서 예외가 나고, show() 를 부른 쪽의 나머지가
    // 통째로 멈춘다. 실제로 덱 2종에 #notes-text 가 빠져 있어 슬라이드를 넘길 때마다
    // 던지고 있었고, 그래서 '목록 → 발표' 전환이 조용히 실패했다. 없으면 건너뛴다.
    var pos = document.getElementById('pos');
    var nm = document.getElementById('name');
    if (pos) pos.textContent = (i + 1) + ' / ' + frames.length;
    if (nm) nm.textContent = frames[i].dataset.label;
    if (notesText) {
      notesText.textContent = frames[i].dataset.notes || '(이 슬라이드에는 노트가 없다)';
    }
  }

  // 발표 모드 — 브라우저 전체화면으로 들어가고 HUD·노트를 감춘다.
  // 이게 없으면 F11 을 눌러도 화면만 커지고 버튼은 그대로 남는다. 발표를 못 한다.
  //
  // 전체화면은 사용자 제스처가 있어야 열리고, iframe(Artifact 미리보기 등)에서는
  // allow="fullscreen" 이 없으면 거부된다. 거부돼도 present 클래스는 붙인다 —
  // 창을 못 키워도 버튼이 사라지고 지면이 창을 가득 채우면 발표는 된다.
  var idleTimer = null;

  function inFull() {
    return !!(document.fullscreenElement || document.webkitFullscreenElement);
  }

  function setPresent(on) {
    document.body.classList.toggle('present', on);
    if (!on) {
      document.body.classList.remove('idle');
      clearTimeout(idleTimer);
    }
    scale();
  }

  function enterPresent() {
    // 전체 보기(세로 나열)에서 바로 들어오면 먼저 한 장씩으로 되돌린다.
    if (document.body.classList.contains('all-mode--live')) allBtn.onclick();
    var el = document.documentElement;
    var req = el.requestFullscreen || el.webkitRequestFullscreen;
    setPresent(true);
    if (req) {
      var r = req.call(el);
      if (r && r.catch) r.catch(function () { /* 거부돼도 present 는 유지한다 */ });
    }
  }

  function exitPresent() {
    if (inFull()) {
      var ex = document.exitFullscreen || document.webkitExitFullscreen;
      if (ex) ex.call(document);
    }
    setPresent(false);
  }

  function togglePresent() {
    if (document.body.classList.contains('present')) exitPresent();
    else enterPresent();
  }

  // 브라우저가 Esc·F11 로 전체화면을 끄면 클래스도 따라 꺼야 한다.
  // 안 그러면 창은 돌아왔는데 버튼이 계속 숨어 있어 되돌아갈 길이 없다.
  ['fullscreenchange', 'webkitfullscreenchange'].forEach(function (ev) {
    document.addEventListener(ev, function () {
      if (!inFull() && document.body.classList.contains('present')) setPresent(false);
      else scale();
    });
  });

  // F11 은 브라우저 UI 전체화면이라 Fullscreen API 이벤트를 쏘지 않는다.
  // fullscreenchange 만 듣고 있으면 F11 을 눌러도 HUD 가 그대로 남는다 —
  // "전체화면인데 버튼이 보인다"가 정확히 이것이다.
  // display-mode 미디어 질의는 F11 에도 반응하므로 둘을 함께 듣는다.
  if (window.matchMedia) {
    var mq = window.matchMedia('(display-mode: fullscreen)');
    var onMq = function (e) { setPresent(e.matches || inFull()); };
    if (mq.addEventListener) mq.addEventListener('change', onMq);
    else if (mq.addListener) mq.addListener(onMq);
    if (mq.matches) setPresent(true);          // 전체화면인 채로 열린 경우
  }

  document.addEventListener('mousemove', function () {
    if (!document.body.classList.contains('present')) return;
    document.body.classList.remove('idle');
    clearTimeout(idleTimer);
    idleTimer = setTimeout(function () { document.body.classList.add('idle'); }, 2000);
  });

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
    if (e.key === 'f' || e.key === 'F') { togglePresent(); e.preventDefault(); }
    // 진짜 전체화면이면 브라우저가 Esc 를 먹고 위 리스너가 정리한다.
    // 거부돼 present 클래스만 붙은 경우에는 여기서 빠져나온다.
    if (e.key === 'Escape' && document.body.classList.contains('present')) exitPresent();
  });
  stage.addEventListener('click', function () {
    if (document.body.classList.contains('present')) show(i + 1);
  });
  document.getElementById('prev').onclick = function () { show(i - 1); };
  document.getElementById('next').onclick = function () { show(i + 1); };
  document.getElementById('notes-btn').onclick = toggleNotes;
  var presentBtn = document.getElementById('present');
  if (presentBtn) presentBtn.onclick = togglePresent;
  // 전체 보기는 제자리에서 켜고 끈다. URL 을 바꾸면 새로고침이 되고, 되돌아갈 길도 없다.
  // Artifact 처럼 주소를 못 바꾸는 곳에서도 이 방식이면 동작한다.
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
