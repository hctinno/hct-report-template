// 문서 뷰어 — 쪽번호·문서명 자동 채움, 축척 맞춤, 인쇄.
// 문서 4종이 이 파일 하나를 공유한다. 단일 파일로 만들 때는 인라인된다.

(function () {
  var doc   = document.querySelector('.bd-doc');
  var pages = Array.prototype.slice.call(document.querySelectorAll('.bd-page'));
  if (!doc || !pages.length) return;

  var title = doc.dataset.docTitle || '';
  var total = pages.length;

  // 쪽번호와 문서명은 여기서 채운다. 쪽을 넣거나 빼도 번호가 어긋나지 않는다.
  pages.forEach(function (pg, n) {
    var head = pg.querySelector('.bd-head');
    if (head && !head.children.length) {
      head.innerHTML = '<span>' + title + '</span><span>' + (doc.dataset.docNo || '') + '</span>';
    }
    var foot = pg.querySelector('.bd-foot');
    if (!foot) return;
    if (!foot.children.length) foot.innerHTML = '<span>' + title + '</span><span class="bd-pageno"></span>';
    var no = foot.querySelector('.bd-pageno');
    if (no) no.textContent = (n + 1) + ' / ' + total;
  });

  // 창이 좁으면 지면을 줄여 가로 스크롤이 생기지 않게 한다. 인쇄에는 영향이 없다.
  function fit() {
    var w = parseFloat(getComputedStyle(document.documentElement)
                       .getPropertyValue('--bd-page-w')) || 794;
    var s = Math.min(1, (window.innerWidth - 48) / w);
    doc.style.transform = s < 1 ? 'scale(' + s + ')' : '';
    doc.style.transformOrigin = 'top center';
  }
  window.addEventListener('resize', fit);
  fit();

  var hud = document.getElementById('bd-hud');
  if (!hud) return;
  var pos = hud.querySelector('#bd-pos');
  if (pos) pos.textContent = total + '쪽';
  var pr = hud.querySelector('#bd-print');
  if (pr) pr.onclick = function () { window.print(); };
})();
