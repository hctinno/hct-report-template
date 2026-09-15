// 라이브 덱 뷰어 — 축 전환(검토↔발표), 단계 전개, 쪽번호, 노트·대본.
//
// 슬라이드 계통의 deck-viewer.js 와 역할은 같지만 하는 일이 훨씬 적다.
// 배율과 넘김을 CSS 가 이미 한다 — 루트 글자 크기가 clamp 로 따라가고, 넘김은
// 브라우저의 scroll-snap 이 한다. 그래서 여기서는 JS 로만 되는 것만 한다.
//
// 이 계통은 **JS 없이 열어도 전부 읽힌다.** 세로로 스크롤하면 그만이다.
// 단계 전개를 기본으로 접지 않는 이유도 같다.

(function () {
  var deck = document.getElementById('deck');
  if (!deck) return;
  var slides = Array.prototype.slice.call(deck.querySelectorAll('.bl-sl'));
  var deckTitle = deck.dataset.deckTitle || '';
  var i = 0, step = 0;

  // ── 쪽번호 ────────────────────────────────────────────────────────────
  // 부록은 본문과 다른 체계로 센다. 같은 자리에 다른 체계가 찍히는 것이
  // 부록으로 넘어왔다는 신호다 — 덱 계통과 같은 규약이다.
  var apxTotal = slides.filter(function (s) { return s.hasAttribute('data-apx'); }).length;
  var bodyN = 0, apxN = 0;
  slides.forEach(function (s) {
    var isApx = s.hasAttribute('data-apx');
    if (isApx) apxN++; else bodyN++;
    var pg = s.querySelector('.bl-pg');
    if (!pg) return;
    pg.textContent = isApx ? '부록 ' + apxN + ' / ' + apxTotal
                           : String(bodyN).padStart(2, '0');
    var nm = s.querySelector('.bl-rf-name');
    if (nm && !nm.textContent) nm.textContent = deckTitle;
  });

  // ── 단계 전개 ─────────────────────────────────────────────────────────
  function frags(s) { return Array.prototype.slice.call(s.querySelectorAll('[data-f]')); }
  function maxStep(s) {
    return frags(s).reduce(function (m, el) {
      return Math.max(m, parseInt(el.getAttribute('data-f'), 10) || 0);
    }, 0);
  }
  function staged() { return deck.classList.contains('bl-deck--present'); }

  function paint() {
    deck.classList.toggle('bl-deck--staged', staged());
    slides.forEach(function (s, k) {
      var open = !staged() || k !== i;
      frags(s).forEach(function (el) {
        var n = parseInt(el.getAttribute('data-f'), 10) || 0;
        el.classList.toggle('is-shown', open || n <= step);
      });
    });
    pushScript();
  }

  function stepFwd() {
    if (!staged() || step >= maxStep(slides[i])) return false;
    step++; paint(); return true;
  }
  function stepBack() {
    if (!staged() || step <= 0) return false;
    step--; paint(); return true;
  }

  // ── 현재 장 추적 ──────────────────────────────────────────────────────
  // 스크롤은 브라우저가 한다. 어디에 와 있는지만 관찰로 알아낸다 —
  // scroll 이벤트로 좌표를 재면 스냅 도중 값이 튄다.
  if (window.IntersectionObserver) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        var k = slides.indexOf(e.target);
        if (k < 0 || k === i) return;
        i = k; step = 0; paint();
      });
    }, { root: deck, threshold: .6 });
    slides.forEach(function (s) { io.observe(s); });
  }

  function goTo(k) {
    i = Math.max(0, Math.min(slides.length - 1, k));
    step = 0;
    slides[i].scrollIntoView({ block: 'start', inline: 'start' });
    paint();
  }

  // ── 발표 모드 ─────────────────────────────────────────────────────────
  // 축을 세로에서 가로로 바꾸고 전체화면으로 들어간다. 클래스 하나가
  // scroll-snap-type 과 flex-direction 을 함께 바꾼다.
  function inFull() {
    return !!(document.fullscreenElement || document.webkitFullscreenElement);
  }
  function setPresent(on) {
    deck.classList.toggle('bl-deck--present', on);
    document.body.classList.toggle('present', on);
    step = 0;
    paint();
    // 축이 바뀌면 스크롤 좌표가 무의미해진다. 보던 장으로 다시 앉힌다.
    requestAnimationFrame(function () {
      slides[i].scrollIntoView({ block: 'start', inline: 'start' });
    });
  }
  function enterPresent() {
    var el = document.documentElement;
    var req = el.requestFullscreen || el.webkitRequestFullscreen;
    setPresent(true);
    if (req) { var r = req.call(el); if (r && r.catch) r.catch(function () {}); }
  }
  function exitPresent() {
    if (inFull()) {
      var ex = document.exitFullscreen || document.webkitExitFullscreen;
      if (ex) ex.call(document);
    }
    setPresent(false);
  }
  function togglePresent() {
    if (deck.classList.contains('bl-deck--present')) exitPresent(); else enterPresent();
  }
  ['fullscreenchange', 'webkitfullscreenchange'].forEach(function (ev) {
    document.addEventListener(ev, function () {
      if (!inFull() && deck.classList.contains('bl-deck--present')) setPresent(false);
    });
  });

  // ── 대본 창 ───────────────────────────────────────────────────────────
  var scriptWin = null;
  function noteOf(k) {
    var s = slides[(k + slides.length) % slides.length];
    return s.dataset.notes || '';
  }
  function openScript() {
    if (scriptWin && !scriptWin.closed) { scriptWin.focus(); return; }
    scriptWin = window.open('', 'bl-script', 'width=560,height=760');
    if (!scriptWin) { alert('대본 창이 브라우저에 막혔다. 팝업을 허용한 뒤 다시 누른다.'); return; }
    scriptWin.document.open();
    scriptWin.document.write(
      '<!doctype html><meta charset="utf-8"><title>대본</title><style>' +
      "body{margin:0;padding:22px 24px;background:#0c121e;color:#dbe3ec;font:400 16px/1.7 system-ui,'Malgun Gothic',sans-serif}" +
      'h1{margin:0 0 4px;font:600 13px/1.3 system-ui;letter-spacing:.14em;text-transform:uppercase;color:#8fa4bd}' +
      '#t{font:600 28px/1 ui-monospace,Menlo,monospace;color:#fff;margin:0 0 18px}' +
      '#cur{white-space:pre-wrap;border-left:3px solid #2f4a9c;padding-left:14px;margin-bottom:22px}' +
      '#nxt{white-space:pre-wrap;color:#8fa4bd;border-left:3px solid #2b3852;padding-left:14px}' +
      'h2{margin:0 0 6px;font:600 11px/1 system-ui;letter-spacing:.14em;text-transform:uppercase;color:#8fa4bd}' +
      '</style><h1 id="pg"></h1><p id="t">00:00</p>' +
      '<h2>지금</h2><div id="cur"></div><h2>다음</h2><div id="nxt"></div>');
    scriptWin.document.close();
    var t0 = Date.now();
    scriptWin.setInterval(function () {
      var el = scriptWin.document.getElementById('t');
      if (!el) return;
      var s = Math.floor((Date.now() - t0) / 1000);
      el.textContent = String(Math.floor(s / 60)).padStart(2, '0') + ':' + String(s % 60).padStart(2, '0');
    }, 1000);
    pushScript();
  }
  function pushScript() {
    if (!scriptWin || scriptWin.closed) return;
    var d = scriptWin.document, pg = d.getElementById('pg');
    if (!pg) return;
    var ms = maxStep(slides[i]);
    pg.textContent = (i + 1) + ' / ' + slides.length + (ms ? '   단계 ' + step + ' / ' + ms : '');
    d.getElementById('cur').textContent = noteOf(i) || '(노트 없음)';
    d.getElementById('nxt').textContent = noteOf(i + 1) || '(노트 없음)';
  }
  window.addEventListener('beforeunload', function () {
    if (scriptWin && !scriptWin.closed) scriptWin.close();
  });

  // ── 조작 ──────────────────────────────────────────────────────────────
  var jump = '';
  function showJump() {
    var el = document.getElementById('bl-jump');
    if (!el) return;
    el.textContent = jump; el.hidden = !jump;
  }

  document.addEventListener('keydown', function (e) {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    if (e.key >= '0' && e.key <= '9') { jump += e.key; showJump(); e.preventDefault(); return; }
    if (e.key === 'Enter' && jump) {
      var n = parseInt(jump, 10); jump = ''; showJump();
      if (n >= 1 && n <= slides.length) goTo(n - 1);
      e.preventDefault(); return;
    }
    if (e.key === 'Escape' && jump) { jump = ''; showJump(); e.preventDefault(); return; }

    if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') {
      if (!stepFwd()) goTo(i + 1);
      e.preventDefault();
    }
    if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
      if (!stepBack()) { goTo(i - 1); if (staged()) { step = maxStep(slides[i]); paint(); } }
      e.preventDefault();
    }
    if (e.key === 'Home') goTo(0);
    if (e.key === 'End') goTo(slides.length - 1);
    if (e.key === 's' || e.key === 'S') openScript();
    if (e.key === 'f' || e.key === 'F') { togglePresent(); e.preventDefault(); }
    if (e.key === 'Escape' && deck.classList.contains('bl-deck--present')) exitPresent();
  });

  deck.addEventListener('click', function () {
    if (!deck.classList.contains('bl-deck--present')) return;
    if (!stepFwd()) goTo(i + 1);
  });

  var pb = document.getElementById('bl-present');
  if (pb) pb.onclick = togglePresent;
  var sb = document.getElementById('bl-script');
  if (sb) sb.onclick = openScript;

  paint();
})();
