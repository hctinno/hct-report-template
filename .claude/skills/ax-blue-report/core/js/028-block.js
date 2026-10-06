(function() {
 const payload = JSON.parse(document.getElementById('bma-rfp-payload').textContent);
 const modal = document.getElementById('bma-rfp-modal');
 const evidence = document.getElementById('evm');
 const frame = modal.querySelector('iframe');
 let returnFocus = null, loaded = false, pendingHighlight = null;
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
  const doc = frame.contentDocument;
  const target = id ? doc.getElementById(id) : doc.documentElement;
  if (target) {
   target.scrollIntoView({
    block: 'start'
   });
  }
 }
 function open(btn) {
  returnFocus = btn;
  evidence.classList.remove('on');
  modal.classList.add('on');
  if (!loaded) {
   frame.addEventListener('load', function() {
    loaded = true;
    (function(dc) {
     try {
      var vis = /[\p{L}\p{N}\p{P}]/u;
      dc.querySelectorAll('p.bma-rfp-highlight>span').forEach(function(x) {
       var t = x.textContent;
       if (!vis.test(t)) {
        x.classList.add('ws');
        return;
       }
       var m = t.match(/^(\s+)([\s\S]*)$/);
       if (m) {
        var w = x.cloneNode(false);
        w.classList.add('ws');
        w.textContent = m[1];
        x.parentNode.insertBefore(w, x);
        x.textContent = m[2];
       }
      });
     } catch (e) {}
    })(frame.contentDocument);
    setTimeout(function() {
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
  const binary = atob(payload.hwp), array = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
   array[i] = binary.charCodeAt(i);
  }
  const url = URL.createObjectURL(new Blob([ array ], {
   type: 'text/plain'
  }));
  const link = document.createElement('a');
  link.href = url;
  link.download = '예시_사업_1단계_제안요청서_가상.txt';
  link.click();
  setTimeout(function() {
   URL.revokeObjectURL(url);
  }, 3e4);
 }
 const entry = `<div class="bma-rfp-entry bma-stage-compare">\n  <div class="bma-stage-intro"><strong>예시 사업 1·2단계 — 공고·제안요청서(가상) 비교</strong><span>계획·요구사항 근거 / 완료·집행 실적 아님</span></div>\n  <div class="bma-stage-grid">\n    <article class="bma-stage-card">\n      <div class="bma-stage-top"><b>1단계 · 분석·설계</b><small>2020년 공고</small></div>\n      <div class="bma-stage-metrics"><span><b>18.5억 원</b><small>공고예산 · VAT 포함</small></span><span><b>150일 이내</b><small>계약일 기준</small></span></div>\n      <div class="bma-stage-rfp">RFP 본문: 16.8억 원(VAT 별도) · 계약 후 5개월</div>\n      <p><b>목적</b> 분산 시스템·반복 입력 개선, 고객 중심 온라인 서비스의 기반 설계</p>\n      <p><b>범위</b> 업무·고객·모바일 포털, 통합 DB·데이터 전환, ERP·내외부 연계 <em>분석·설계</em></p>\n      <button type="button" class="bma-rfp-open">1단계 원문 전체보기</button>\n    </article>\n    <article class="bma-stage-card stage-two">\n      <div class="bma-stage-top"><b>2단계 · 핵심 업무 구축</b><small>2021년 재공고</small></div>\n      <div class="bma-stage-metrics"><span><b>61.2억 원</b><small>공고예산 · VAT 포함</small></span><span><b>270일 이내</b><small>계약일 기준</small></span></div>\n      <div class="bma-stage-rfp">RFP 본문: 55.6억 원(VAT 별도) · 계약 후 9개월</div>\n      <p><b>목적</b> 상담·접수부터 시험·인증·문서 발급까지 핵심 흐름 구현</p>\n      <p><b>범위</b> 업무·고객 포털 개발, 고객 모바일 <em>시범 구축</em>, 통합 DB·데이터 전환 및 ERP 연계</p>\n      <button type="button" class="bma-rfp-open-2">2단계 원문 전체보기</button>\n    </article>\n  </div>\n  <p class="bma-stage-read">1단계의 폭넓은 설계 항목이 2단계에서 모두 같은 비중으로 구축된 것은 아님 · 핵심 업무 중심으로 범위 구체화</p>\n</div>`;
 const text = evidence.querySelector('.evt');
 const tabs = evidence.querySelector('.evtabs');
 const observer = new MutationObserver(function() {
  const active = tabs.querySelector('[aria-selected="true"]');
  if (!active || active.textContent.trim() !== 'E40' || !evidence.classList.contains('on') || text.querySelector('.bma-rfp-open')) {
   return;
  }
  text.insertAdjacentHTML('afterbegin', entry);
 });
 observer.observe(text, {
  childList: true
 });
 text.addEventListener('click', function(event) {
  const btn = event.target.closest('.bma-rfp-open');
  if (btn) {
   event.stopPropagation();
   open(btn);
  }
 });
 modal.addEventListener('click', function(event) {
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
   jump('bma-rfp-background');
  }
  if (action === 'top') {
   jump(null);
  }
  if (action === 'download') {
   download();
  }
 });
 addEventListener('keydown', function(event) {
  if (modal.classList.contains('on') && event.key === 'Escape') {
   event.preventDefault();
   event.stopImmediatePropagation();
   close();
  }
 }, true);
})();
