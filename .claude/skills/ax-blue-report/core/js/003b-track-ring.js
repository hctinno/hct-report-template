(function() {
 var d = document;
 var REV = [ [ "홍보", "홍보 · 고객 발굴", [ "서비스별 검색 노출 · 페이지 구조 개선안", "소개 자료와 콘텐츠 초안" ], "대외 발행 승인" ], [ "문의", "문의 · 상담", [ "문의를 제품 · 규격 · 일정으로 구조화", "1차 응대 초안 작성" ], "고객 회신 승인" ], [ "견적", "규격 검토 · 견적", [ "제품 사양에서 적용 시험 항목 후보 제시", "표준 공수 기준의 견적 초안" ], "시험 가능 여부 판정과 가격 · 조건" ], [ "접수", "접수 · 검체 등록", [ "의뢰서 · 사양서에서 등록 항목 추출", "필수 정보 누락 확인" ], "접수 확정과 검체 취급 책임" ], [ "시험 · 교정", "시험 · 교정 수행", [ "설비 · 환경 조건 이상 알림", "절차 체크리스트와 기록 누락 표시" ], "시험 수행과 이상 시 조치" ], [ "성적서", "데이터 · 성적서 리뷰", [ "성적서 리뷰(검토) 보조 — 원시데이터와 수치 대조", "항목 누락 · 서식 오류 후보 제시" ], "결과 판정과 성적서 최종 승인" ], [ "인증", "인증 · 사후관리", [ "국가 · 제품군별 요구 서류 체크리스트", "인증 갱신 도래 건 알림" ], "인증 판정과 고객 통보" ], [ "청구", "청구 · 매출", [ "수주 · 완료 · 청구 · 수금 불일치 후보", "시험 매출과 인증 대행비 구분 초안" ], "금액 확정과 청구 · 수금 실행" ] ];
 var OPS = [ [ "채용", "조직 · 채용", [ "직무기술서 표준 양식 초안", "채용 공고 초안 작성" ], "모든 선발 결정 – 지원자 평가에는 쓰지 않음" ], [ "교육", "교육 · 역량", [ "직무별 교육 자료 초안", "이수 · 자격 만료 예정 알림" ], "자격 부여와 교육 인정" ], [ "품질", "품질 · 인정 심사", [ "AUDIT 사전평가 체크리스트 생성", "인정 요구조항 ↔ 사내 기록 위치 매핑 · 증빙 누락 표시" ], "적합성 판단과 시정조치" ], [ "장비 · 구매", "장비 · 전산 · 구매", [ "견적 비교표 작성", "교정 만료 · 소모품 발주 알림" ], "구매 결정과 예산 집행" ], [ "재무", "재무 · 회계", [ "정산 자료 취합과 누락 확인", "계정별 증감 사유 후보" ], "확정 수치와 회계 판단" ], [ "시설", "시설 관리", [ "시설 점검 일정·보수 이력 정리", "고장 접수 분류·점검 항목 안내" ], "안전 점검과 보수 우선순위 결정" ], [ "IT·보안", "IT · 보안", [ "반복 문의 1차 응대 후 이관", "자산 · 계정 대장 정리" ], "권한 부여와 보안 조치" ], [ "경영", "경영관리", [ "승인된 집계 기반 분석 보조", "경영 보고 초안 작성" ], "경영 판단과 목표 설정" ] ];
 var trk = d.getElementById('trk');
 if (!trk) {
  return;
 }
 var VW = 1e3, VH = 500, sel = {
  k: "r",
  i: 2
 };
 function stad(x, y, w, h) {
  var r = h / 2;
  return 'M ' + (x + r) + ' ' + y + ' L ' + (x + w - r) + ' ' + y + ' A ' + r + ' ' + r + ' 0 0 1 ' + (x + w - r) + ' ' + (y + h) + ' L ' + (x + r) + ' ' + (y + h) + ' A ' + r + ' ' + r + ' 0 0 1 ' + (x + r) + ' ' + y + ' Z';
 }
 var dR = stad(95, 30, 810, 440), dO = stad(270, 132, 460, 236);
 [ 'lnR0', 'lnR' ].forEach(function(i) {
  d.getElementById(i).setAttribute('d', dR);
 });
 [ 'lnO0', 'lnO' ].forEach(function(i) {
  d.getElementById(i).setAttribute('d', dO);
 });
 var rings = [ {
  k: 'r',
  data: REV,
  p: d.getElementById('lnR'),
  ac: '--brand',
  bg: '--tint'
 }, {
  k: 'o',
  data: OPS,
  p: d.getElementById('lnO'),
  ac: '--ops',
  bg: '--opsbg'
 } ];
 var g = d.getElementById('trkArw');
 rings.forEach(function(R) {
  var L = R.p.getTotalLength(), bb = R.p.getBBox(), st = (bb.width - bb.height) / 2;
  R.data.forEach(function(s, i) {
   var t = (st - L / 16 + i * L / 8 + L) % L, p = R.p.getPointAtLength(t);
   var b = d.createElement('button');
   b.type = 'button';
   b.className = 'trknd';
   b.textContent = s[0];
   b.style.left = p.x / VW * 100 + '%';
   b.style.top = p.y / VH * 100 + '%';
   b.style.setProperty('--ac', 'var(' + R.ac + ')');
   b.style.setProperty('--acbg', 'var(' + R.bg + ')');
   b.dataset.k = R.k;
   b.dataset.i = i;
   b.addEventListener('click', function(e) {
    e.stopPropagation();
    sel = {
     k: R.k,
     i: i
    };
    paint();
   });
   trk.appendChild(b);
  });
  for (var k = 0; k < 4; k++) {
   var tt = (st + k * L / 4) % L, p1 = R.p.getPointAtLength(tt), p2 = R.p.getPointAtLength((tt + 2) % L);
   var a = Math.atan2(p2.y - p1.y, p2.x - p1.x) * 180 / Math.PI;
   var tri = d.createElementNS('http://www.w3.org/2000/svg', 'path');
   tri.setAttribute('class', 'trkarw ' + R.k);
   tri.setAttribute('d', 'M -8 -7 L 10 0 L -8 7 Z');
   tri.setAttribute('transform', 'translate(' + p1.x + ' ' + p1.y + ') rotate(' + a + ')');
   g.appendChild(tri);
  }
 });
 function card(R, i) {
  var s = R.data[i], c = d.createElement('div');
  c.className = 'trkcard';
  c.style.setProperty('--ac', 'var(' + R.ac + ')');
  c.style.setProperty('--acbg', 'var(' + R.bg + ')');
  var tg = d.createElement('span');
  tg.className = 'tg';
  tg.textContent = R.k === 'r' ? '외부 트랙 · 고객·매출' : '내부 트랙 · 운영 지원';
  c.appendChild(tg);
  var h = d.createElement('h3');
  h.textContent = s[1];
  c.appendChild(h);
  var lead = d.createElement('p');
  lead.className = 'track-detail-label';
  lead.textContent = 'AX 적용 예시';
  c.appendChild(lead);
  var ul = d.createElement('ul');
  s[2].forEach(function(x) {
   var li = d.createElement('li');
   li.textContent = x;
   ul.appendChild(li);
  });
  c.appendChild(ul);
  var hm = d.createElement('div');
  hm.className = 'hm';
  var bb = d.createElement('b');
  bb.textContent = '사람의 판단·승인';
  var sp = d.createElement('span');
  sp.textContent = s[3];
  hm.appendChild(bb);
  hm.appendChild(sp);
  c.appendChild(hm);
  var benefit = d.createElement('div');
  benefit.className = 'track-benefit';
  var effects = {
   r: [ '서비스 발견·문의 기회 확대', '문의 파악·초기 대응 부담 완화', '견적 준비·재입력 부담 완화', '준비 누락·일정 확인 부담 완화', '기록 정리·확인 부담 완화', '검토 누락·재작업 부담 완화', '요구 서류 준비·갱신 관리 지원', '청구 누락·자료 대조 부담 완화' ],
   o: [ '채용 준비 문서 작성 지원', '직무 교육·자격 관리 지원', '심사 증빙 준비·누락 확인 지원', '구매 비교·장비 일정 관리 지원', '정산·보고 자료 준비 부담 완화', '반복 안내·예외 처리 부담 완화', '문의 응대·대장 정리 부담 완화', '경영 현황 파악·판단 준비 지원' ]
  };
  benefit.innerHTML = '<small>기대 변화 · 미측정</small><b>' + effects[R.k][i] + '</b>';
  c.appendChild(benefit);
  return c;
 }
 function paint() {
  Array.prototype.forEach.call(trk.querySelectorAll('.trknd'), function(b) {
   b.setAttribute('aria-pressed', sel.k === b.dataset.k && sel.i === +b.dataset.i ? 'true' : 'false');
  });
  var pr = d.getElementById('trkR'), po = d.getElementById('trkO');
  pr.innerHTML = '';
  po.innerHTML = '';
  pr.appendChild(card(rings[sel.k === 'r' ? 0 : 1], sel.i));
  po.hidden = true;
 }
 paint();
})();
