# 짜임 카드 — 장 하나를 어떻게 나눌지

> **생성 파일** — `scripts/build_cards.py` 가 `examples/layouts/cards.yaml`(판단하는 말)과
> `examples/layouts/slides.html`(장 마크업 원본)로 만든다. 고칠 것은 그 두 파일에서 고친다.
> 견본 덱: `python3 scripts/build_deck.py examples/layouts/deck.yaml --brand <brand.json> --single-file -o <결과>.html`

장의 **내용 모양**을 먼저 정하고(금액 · 추세 · 전후 · 구조 · 경로 · 1:1 비교 · 분류 · 계획 · 화면 · 단계),
아래에서 그 모양의 카드를 고른다. 같은 짜임은 덱 안에서 3장까지 — 뉴스 10건이라도 한 틀에 끼우지 않는다.
카드의 HTML 은 견본이다. 칸 수 · 문구 · 수치는 내용에 맞게 바꾸고, 바꿀 곳은 카드의 「바꿀 곳」에 있다.
부품(수치 타일 · 간트 · 도넛 …)의 규격은 `COMPONENTS.md`.

| 카드 | 내용 모양 | 주인공 |
|---|---|---|
| [큰 금액 하나](#l-amount) | 한 숫자가 뉴스 전부 — 거래액 · 투자액 · 예산 · 손실액 | 큰 숫자 |
| [추세 + 구성](#l-trend) | 시간에 따른 변화와 지금 시점의 구성비를 함께 — 분기 매출 · 비중 | 지금 시점 막대와 도넛 가운데 비율 |
| [규칙 전후](#l-rule) | 규칙 · 제도 · 절차가 바뀜 — 무엇이 더해졌나 | 아래 줄의 짙은 칸(바뀐 지점) |
| [구조 · 층](#l-structure) | 부품 · 조직 · 시스템의 층과 그중 바뀐 곳 | 단면 그림에서 짙게 칠한 층 |
| [경로 · 흐름](#l-path) | 무언가가 거쳐 가는 길 — 전력 · 데이터 · 결재 · 물류 | 짙은 원 마디(관여 지점) |
| [1:1 비교](#l-versus) | 두 선택지를 같은 기준으로 — 요금제 · 모델 · 안 A/B | 오른쪽(또는 권장) 카드 숫자 |
| [분류 · 구성](#l-taxonomy) | 묶음별 개수가 의미 — 제품군 · 모델 종류 · 조직 단위 | 가장 큰 타일 |
| [계획 · 목표](#l-plan) | 지금 한 일과 몇 년 목표 — 협약 · 투자 계획 · 로드맵 | 위 큰 숫자 중 핵심 하나(코발트) |
| [화면 · 사용법](#l-screen) | 기능 · 화면이 바뀜 — 앱 업데이트 · 새 도구 | 목업 속 바뀐 부분(번역문 · 새 버튼) |
| [단계별 수치](#l-stages) | 업무 · 공정 단계마다 값이 다름 — 활용률 · 소요 시간 · 불량률 | 가장 높은 묶음과 가장 낮은 묶음의 대비(코발트 vs 주황) |
| [요약 지도](#l-map) | 덱 첫머리 — 여러 건을 한 장에 배치(목차 대신) | 제목의 결론 한 줄 |
| [점검 카드](#l-watch) | 덱 끝 — 다음에 확인할 것 2~4개 | 짙은 카드 |

---

<a id="l-amount"></a>
## 큰 금액 하나 · `l-amount`

| 항목 | 내용 |
|---|---|
| 내용 모양 | 한 숫자가 뉴스 전부 — 거래액 · 투자액 · 예산 · 손실액 |
| 구조 | 큰 숫자(8rem) + 기준 한 줄 → 굵은 분할 막대(구성 비율) → 아래 수치 칸 3개 |
| 주인공 | 큰 숫자 |
| 토큰 | `--bl-pt-orange` `--bl-r-s` `--br-card` `--br-font-kr` `--br-font-num` `--br-hairline` `--br-navy` `--br-text-2` |
| 할 것 | 숫자 옆에 무엇의 합계인지(포함 · 제외) 한 줄 · 분할 막대 폭은 실제 비율 |
| 하지 말 것 | 숫자를 카드 안에 작게 가두기 · 수치 칸을 4개 이상으로 늘리기 |
| 바꿀 곳 | 분할 막대의 칸 수와 비율(--w) · 수치 칸 3개의 라벨 |

본문(`slides.html` 에 그대로 — 머리띠 · 꼬리띠는 빌드가 단다):

```html
<section id="l-amount" data-name="글로벌 · 자본시장" data-notes="…">
<h2 class="bl-title">가온AI 상장, <em>거래 총액 1,195억 달러</em></h2>
<p class="bl-lede">11월 19일 나스닥 ‘GAON’ 거래 개시 · 20일 공모 · 동시 사모 마감 공시<button type="button" class="bl-ev" data-ev="E01" data-claim="공모 · 사모 합산 약 1,195억 달러">출처</button></p>
<div class="x-ipo bl-fill">
  <div class="x-ipo-hero">
    <p class="x-ipo-n">1,195<small>억 달러</small></p>
    <p class="x-ipo-c">공모 + 동시 사모 · 수수료 차감 전 · 구주 매출 포함</p>
  </div>
  <div class="x-ipo-bar"><div style="--w: 78.2%"><b>주식 공모</b><strong>약 935억 달러</strong></div><div><b>동시 사모</b><strong>약 260억</strong></div></div>
  <div class="x-ipo-cells">
    <div><span class="bl-lbl">공모가</span><strong>83<small>달러 / 주</small></strong></div>
    <div><span class="bl-lbl">공모 주식</span><strong>11.27<small>억 주 · 초과배정 포함</small></strong></div>
    <div><span class="bl-lbl">그중 구주 매출</span><strong>2,365<small>만 주</small></strong></div>
  </div>
</div>
</section>
```

맞춤 CSS(장 안 `<style data-own>` — 선택자는 장 id 로 묶여 있다. 새 장에 쓸 때 id 를 바꾸면 선택자도 함께):

```css
#l-amount .x-ipo { display: grid; grid-template-rows: auto auto auto; align-content: center; gap: 2.2rem }
#l-amount .x-ipo-hero { display: flex; align-items: baseline; gap: 2.4rem }
#l-amount .x-ipo-n { margin: 0; font: 800 8rem/.9 var(--br-font-num); letter-spacing: -.03em; color: var(--br-navy) }
#l-amount .x-ipo-n small { font: 700 2.4rem/1 var(--br-font-kr); margin-left: .6rem; color: var(--br-text-2) }
#l-amount .x-ipo-c { margin: 0; font: 500 1.3rem/1.4 var(--br-font-kr); color: var(--br-text-2) }
#l-amount .x-ipo-bar { display: flex; gap: .4rem; height: 6rem }
#l-amount .x-ipo-bar > div { display: flex; flex-direction: column; justify-content: center; gap: .3rem; padding: 0 1.8rem;
                              border-radius: var(--bl-r-s); background: var(--bl-pt-orange); color: var(--br-card) }
#l-amount .x-ipo-bar > div:first-child { flex: 0 0 var(--w); background: var(--br-navy) }
#l-amount .x-ipo-bar > div:last-child { flex: 1 1 auto }
#l-amount .x-ipo-bar b { font: 600 1.1rem/1 var(--br-font-kr); opacity: .85 }
#l-amount .x-ipo-bar strong { font: 800 1.9rem/1 var(--br-font-num) }
#l-amount .x-ipo-cells { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); border-top: .18rem solid var(--br-navy) }
#l-amount .x-ipo-cells > div { display: grid; gap: .6rem; padding: 1.4rem 1.6rem 0 0 }
#l-amount .x-ipo-cells > div + div { padding-left: 1.6rem; border-left: 1px solid var(--br-hairline) }
#l-amount .x-ipo-cells strong { font: 800 2.6rem/1 var(--br-font-num); color: var(--br-navy) }
#l-amount .x-ipo-cells small { font: 600 1.1rem/1 var(--br-font-kr); color: var(--br-text-2); margin-left: .4rem }

```

---

<a id="l-trend"></a>
## 추세 + 구성 · `l-trend`

| 항목 | 내용 |
|---|---|
| 내용 모양 | 시간에 따른 변화와 지금 시점의 구성비를 함께 — 분기 매출 · 비중 |
| 구조 | 왼쪽 세로 막대(시점 3~5개, 지금만 진하게) + 증가율 · 오른쪽 도넛(donut.py) + 범례 |
| 주인공 | 지금 시점 막대와 도넛 가운데 비율 |
| 토큰 | `--bl-pt-gray` `--bl-r-xs` `--br-cobalt` `--br-data-1` `--br-data-2` `--br-font-kr` `--br-font-num` `--br-hairline` `--br-navy` `--br-text-2` `--br-text-3` |
| 할 것 | 지금 시점만 주인공 색 · 나머지 회색 · 도넛은 scripts/donut.py --live 로 생성 |
| 하지 말 것 | 시점마다 다른 색 · 도넛 각도 손으로 쓰기 · 파이 차트 |
| 바꿀 곳 | 막대 높이(--h, 최댓값 100%) · donut.py 값 |

본문(`slides.html` 에 그대로 — 머리띠 · 꼬리띠는 빌드가 단다):

```html
<section id="l-trend" data-name="글로벌 · 반도체 실적" data-notes="…">
<h2 class="bl-title">나래칩 매출의 <em>92.9%가 데이터센터</em></h2>
<p class="bl-lede">11월 17일 3분기 실적 · 10월 25일 마감 분기 · 차세대 랙 R7 출하 개시<button type="button" class="bl-ev" data-ev="E02" data-claim="데이터센터 1,076억 달러 · 전사 1,158억 달러">출처</button></p>
<div class="x-nv bl-fill">
  <div class="x-nv-chart">
    <p class="bl-lbl">전사 매출 · 억 달러</p>
    <div class="x-cols">
      <div style="--h: 49%"><em>570</em><i></i><span>전년 동기</span></div>
      <div style="--h: 83%"><em>962</em><i></i><span>직전 분기</span></div>
      <div class="is-key" style="--h: 100%"><em>1,158</em><i></i><span>이번 분기</span></div>
    </div>
    <p class="x-nv-yoy"><b>+103%</b>전사 · 전년 동기 대비 <b>+110%</b>데이터센터</p>
  </div>
  <div class="x-nv-donut">
    <p class="bl-lbl">이번 분기 매출 구성</p>
    <div class="bl-donut-box">
      <figure class="bl-donut" role="img" aria-label="이번 분기 매출 구성 — 데이터센터 92.9%">
        <svg viewBox="0 0 272 272" aria-hidden="true"><g transform="translate(136,136)">
          <circle class="bl-donut-s" data-k="0" r="110" stroke="var(--br-data-1)" stroke-width="48" stroke-dasharray="639.2 691.2" transform="rotate(-90.00)" style="--i:0;--dash:639.2"></circle>
          <circle class="bl-donut-s" data-k="1" r="110" stroke="var(--br-data-2)" stroke-width="48" stroke-dasharray="46.2 691.2" transform="rotate(244.44)" style="--i:1;--dash:46.2"></circle>
        </g></svg>
        <figcaption class="bl-donut-c"><b style="--w: 2.42">92.9<small>%</small></b><span class="bl-cap">데이터센터 비중</span></figcaption>
      </figure>
      <ul class="bl-donut-leg">
        <li data-k="0" data-p="92.9%"><i style="background:var(--br-data-1)"></i><span>데이터센터 1,076억</span><b>92.9%</b></li>
        <li data-k="1" data-p="7.1%"><i style="background:var(--br-data-2)"></i><span>그 밖 82억</span><b>7.1%</b></li>
      </ul>
    </div>
  </div>
</div>
</section>
```

맞춤 CSS(장 안 `<style data-own>` — 선택자는 장 id 로 묶여 있다. 새 장에 쓸 때 id 를 바꾸면 선택자도 함께):

```css
#l-trend .x-nv { display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr); gap: 4rem }
#l-trend .x-nv-chart { display: flex; flex-direction: column; gap: 1rem; min-width: 0 }
#l-trend .x-cols { flex: 1 1 auto; min-height: 0; display: grid; grid-template-columns: repeat(3, 1fr); gap: 2.4rem; align-items: end;
                  border-bottom: .14rem solid var(--br-text-3); margin-bottom: 2.4rem }
#l-trend .x-cols > div { height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center; gap: .5rem; position: relative }
#l-trend .x-cols i { display: block; width: 100%; height: calc(var(--h) * .82); border-radius: var(--bl-r-xs) var(--bl-r-xs) 0 0; background: var(--bl-pt-gray) }
#l-trend .x-cols .is-key i { background: var(--br-cobalt) }
#l-trend .x-cols em { font: 800 1.8rem/1 var(--br-font-num); font-style: normal; color: var(--br-navy) }
#l-trend .x-cols span { position: absolute; bottom: -2.1rem; font: 600 1.05rem/1 var(--br-font-kr); color: var(--br-text-2) }
#l-trend .x-nv-yoy { margin: 0; display: flex; align-items: baseline; gap: .7rem; font: 500 1.15rem/1 var(--br-font-kr); color: var(--br-text-2) }
#l-trend .x-nv-yoy b { font: 800 1.8rem/1 var(--br-font-num); color: var(--br-cobalt) }
#l-trend .x-nv-yoy b:nth-of-type(2) { margin-left: 1.2rem }
#l-trend .x-nv-donut { display: flex; flex-direction: column; gap: 1rem; justify-content: center; border-left: 1px solid var(--br-hairline); padding-left: 4rem }

```

---

<a id="l-rule"></a>
## 규칙 전후 · `l-rule`

| 항목 | 내용 |
|---|---|
| 내용 모양 | 규칙 · 제도 · 절차가 바뀜 — 무엇이 더해졌나 |
| 구조 | 두 줄 흐름 — 위 「기존」(흐리게) · 아래 「추가」(옅은 바탕), 심사 · 관문 칸만 짙게 · 맨 아래 「읽는 법」 한 줄 |
| 주인공 | 아래 줄의 짙은 칸(바뀐 지점) |
| 토큰 | `--bl-font-mono` `--bl-r-m` `--bl-r-s` `--br-accent-on-dark` `--br-card` `--br-cobalt` `--br-font-kr` `--br-navy` `--br-on-dark` `--br-on-dark-2` `--br-page` `--br-text` `--br-text-2` `--br-text-3` `--br-tint` |
| 할 것 | 두 줄의 칸 순서를 맞춰 무엇이 달라졌는지 위아래로 비교 · 확대 해석 경계는 노트에 |
| 하지 말 것 | 두 줄을 좌우로 나란히(비교가 안 됨) · 짙은 칸을 둘 이상 |
| 바꿀 곳 | 각 줄의 칸 3개(아이콘 · 이름 · 설명) · 짙은 칸 위치 |

본문(`slides.html` 에 그대로 — 머리띠 · 꼬리띠는 빌드가 단다):

```html
<section id="l-rule" data-name="글로벌 · 수출통제" data-notes="…">
<h2 class="bl-title">A국 칩 통제, <em>원격 이용까지 확대</em></h2>
<p class="bl-lede">11월 16일 A국 수출 당국 규칙 · 특정 해외 주체의 A국 기술 기반 첨단 연산 접근이 대상<button type="button" class="bl-ev" data-ev="E03" data-claim="원격 접근 서비스가 규칙 대상">출처</button></p>
<div class="x-rule bl-fill">
  <div class="x-lane">
    <p class="x-lane-k"><b>기존</b>물리적 반출 통제</p>
    <div class="x-step"><i class="bl-i bl-i--cpu"></i><h3>첨단 칩 · 서버</h3><p>A국 기술 기반</p></div>
    <span class="x-arr">→</span>
    <div class="x-step is-gate"><i class="bl-i bl-i--stamp"></i><h3>수출 허가 심사</h3><p>나라 밖으로 옮길 때</p></div>
    <span class="x-arr">→</span>
    <div class="x-step"><i class="bl-i bl-i--globe"></i><h3>해외 설치</h3><p>물건이 국경을 넘음</p></div>
  </div>
  <div class="x-lane is-new">
    <p class="x-lane-k"><b>추가</b>원격 접근 통제</p>
    <div class="x-step"><i class="bl-i bl-i--cpu"></i><h3>첨단 칩 · 서버</h3><p>A국 기술 기반</p></div>
    <span class="x-arr">→</span>
    <div class="x-step"><i class="bl-i bl-i--server"></i><h3>제3국 데이터센터</h3><p>연산을 원격 서비스로 제공</p></div>
    <span class="x-arr">→</span>
    <div class="x-step is-gate"><i class="bl-i bl-i--shield-alert"></i><h3>특정 해외 주체</h3><p>원격 접근 심사 대상</p></div>
  </div>
  <p class="x-rule-n"><span class="bl-lbl">읽는 법</span>칩은 국경을 넘지 않아도 <b>누가 연산을 쓰는가</b>가 심사 기준 — 해외 클라우드 계약에 최종 이용자 · 제공 연산 범위 확인 항목 추가</p>
</div>
</section>
```

맞춤 CSS(장 안 `<style data-own>` — 선택자는 장 id 로 묶여 있다. 새 장에 쓸 때 id 를 바꾸면 선택자도 함께):

```css
#l-rule .x-rule { display: grid; align-content: center; gap: 1.4rem }
#l-rule .x-lane { display: grid; grid-template-columns: 15rem minmax(0, 1fr) 2.6rem minmax(0, 1fr) 2.6rem minmax(0, 1fr); align-items: stretch;
               padding: 1.4rem 1.6rem; border-radius: var(--bl-r-m); background: var(--br-page) }
#l-rule .x-lane.is-new { background: var(--br-tint) }
#l-rule .x-lane-k { margin: 0; align-self: center; display: grid; gap: .4rem; font: 700 1.25rem/1.3 var(--br-font-kr); color: var(--br-text-2) }
#l-rule .x-lane-k b { font: 800 1.0rem/1 var(--bl-font-mono); letter-spacing: .08em; color: var(--br-text-3) }
#l-rule .x-lane.is-new .x-lane-k { color: var(--br-navy) }
#l-rule .x-lane.is-new .x-lane-k b { color: var(--br-cobalt) }
#l-rule .x-step { background: var(--br-card); border-radius: var(--bl-r-s); padding: 1.1rem 1.3rem; display: grid; gap: .35rem; align-content: start }
#l-rule .x-step .bl-i { font-size: 1.6rem; color: var(--br-cobalt) }
#l-rule .x-step h3 { margin: 0; font: 800 1.4rem/1.25 var(--br-font-kr); color: var(--br-navy) }
#l-rule .x-step p { margin: 0; font: 500 1.05rem/1.35 var(--br-font-kr); color: var(--br-text-2) }
#l-rule .x-lane:not(.is-new) .x-step { opacity: .7 }
#l-rule .x-step.is-gate { background: var(--br-navy) }
#l-rule .x-step.is-gate h3 { color: var(--br-on-dark) }
#l-rule .x-step.is-gate p { color: var(--br-on-dark-2) }
#l-rule .x-step.is-gate .bl-i { color: var(--br-accent-on-dark) }
#l-rule .x-arr { align-self: center; text-align: center; font: 700 1.6rem/1 var(--br-font-kr); color: var(--br-cobalt) }
#l-rule .x-rule-n { margin: .6rem 0 0; display: flex; gap: 1.2rem; align-items: baseline; font: 500 1.25rem/1.5 var(--br-font-kr); color: var(--br-text) }
#l-rule .x-rule-n b { color: var(--br-navy) }

```

---

<a id="l-structure"></a>
## 구조 · 층 · `l-structure`

| 항목 | 내용 |
|---|---|
| 내용 모양 | 부품 · 조직 · 시스템의 층과 그중 바뀐 곳 |
| 구조 | 왼쪽 단면 그림(층을 위에서 아래로) + 오른쪽 주석 카드 2개(바뀐 층) + 아래 일정 띠 |
| 주인공 | 단면 그림에서 짙게 칠한 층 |
| 토큰 | `--bl-font-mono` `--bl-pt-gray` `--bl-pt-orange` `--bl-pt-orange-d` `--bl-r-l` `--bl-r-m` `--bl-r-s` `--bl-r-xs` `--bl-shadow` `--br-card` `--br-cobalt` `--br-font-kr` `--br-navy` `--br-on-dark` `--br-page` `--br-text-2` `--br-text-3` `--br-tint` |
| 할 것 | 주석 카드 테두리 색을 그림의 층 색과 맞춤 · 일정 띠는 확정 · 검토 · 목표를 구분 |
| 하지 말 것 | 층을 표로 나열 · 주석을 셋 이상 |
| 바꿀 곳 | 층 이름 · 짙게 칠할 층 · 주석 카드 2개 |

본문(`slides.html` 에 그대로 — 머리띠 · 꼬리띠는 빌드가 단다):

```html
<section id="l-structure" data-name="국내 · AI 서버 부품" data-notes="…">
<h2 class="bl-title">다온전자 · 나래칩, <em>기판에서 MLCC까지</em></h2>
<p class="bl-lede">11월 18일 협력 확대 발표 · 세종 · 부산 추가 지원은 검토 단계<button type="button" class="bl-ev" data-ev="E04" data-claim="패키지기판 협력 강화 · MLCC 로 확대">출처</button></p>
<div class="x-sem bl-fill">
  <div class="x-cut">
    <div class="x-chip">GPU · 네트워크 칩</div>
    <div class="x-sub">첨단 패키지기판</div>
    <div class="x-board"><span>서버 보드</span><i></i><i></i><i></i><i></i><i></i><i></i></div>
  </div>
  <div class="x-call">
    <div class="x-c is-key"><span class="bl-lbl">협력 강화</span><h3>첨단 패키지기판</h3><p>칩과 보드 사이 신호 연결 · 차세대 GPU · 고속 네트워크용</p></div>
    <div class="x-c is-hot"><span class="bl-lbl">협력 확대 · 새로</span><h3>고신뢰성 MLCC</h3><p>급변하는 부하에서 전압 안정 · 보드 위 수백 개 단위</p></div>
  </div>
  <div class="x-when"><span><b>2026.11</b>협력 확대 발표</span><i></i><span><b>검토</b>세종 · 부산 추가 지원</span><i></i><span><b>2029</b>본격 양산체계 목표</span></div>
</div>
</section>
```

맞춤 CSS(장 안 `<style data-own>` — 선택자는 장 id 로 묶여 있다. 새 장에 쓸 때 id 를 바꾸면 선택자도 함께):

```css
#l-structure .x-sem { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr); grid-template-rows: 1fr auto; gap: 1.6rem 3.4rem }
#l-structure .x-cut { display: grid; align-content: center; justify-items: center; gap: .3rem; padding: 2rem; border-radius: var(--bl-r-l); background: var(--br-page) }
#l-structure .x-chip { width: 45%; padding: 2rem 0; text-align: center; border-radius: var(--bl-r-s); background: var(--bl-pt-gray);
                   font: 800 1.3rem/1 var(--br-font-kr); color: var(--br-card) }
#l-structure .x-sub { width: 72%; padding: 1.8rem 0; text-align: center; border-radius: var(--bl-r-s); background: var(--br-navy);
                  font: 800 1.35rem/1 var(--br-font-kr); color: var(--br-on-dark) }
#l-structure .x-board { width: 100%; position: relative; display: flex; align-items: center; gap: 1.1rem; padding: 2.4rem 1.8rem;
                    border-radius: var(--bl-r-s); background: var(--br-tint) }
#l-structure .x-board span { font: 800 1.3rem/1 var(--br-font-kr); color: var(--br-navy); margin-right: auto }
#l-structure .x-board i { width: 2rem; height: 1.3rem; border-radius: var(--bl-r-xs); background: var(--bl-pt-orange) }
#l-structure .x-call { display: grid; align-content: center; gap: 1.2rem }
#l-structure .x-c { display: grid; gap: .5rem; padding: 1.5rem 1.8rem; border-radius: var(--bl-r-m); border-left: .4rem solid var(--br-navy); background: var(--br-card); box-shadow: var(--bl-shadow) }
#l-structure .x-c.is-hot { border-left-color: var(--bl-pt-orange) }
#l-structure .x-c .bl-lbl { color: var(--br-cobalt) }
#l-structure .x-c.is-hot .bl-lbl { color: var(--bl-pt-orange-d) }
#l-structure .x-c h3 { margin: 0; font: 800 1.7rem/1.2 var(--br-font-kr); color: var(--br-navy) }
#l-structure .x-c p { margin: 0; font: 500 1.2rem/1.45 var(--br-font-kr); color: var(--br-text-2) }
#l-structure .x-when { grid-column: 1 / -1; display: flex; align-items: center; gap: 1.2rem; padding-top: 1rem; border-top: .18rem solid var(--br-navy) }
#l-structure .x-when span { display: flex; align-items: baseline; gap: .7rem; font: 600 1.15rem/1 var(--br-font-kr); color: var(--br-text-2) }
#l-structure .x-when b { font: 800 1.3rem/1 var(--bl-font-mono); color: var(--br-navy) }
#l-structure .x-when i { flex: 1 1 auto; border-top: 1px dashed var(--br-text-3) }

```

---

<a id="l-path"></a>
## 경로 · 흐름 · `l-path`

| 항목 | 내용 |
|---|---|
| 내용 모양 | 무언가가 거쳐 가는 길 — 전력 · 데이터 · 결재 · 물류 |
| 구조 | 전체 폭 아이콘 경로(5마디) + 핵심 마디에서 아래로 점선을 내린 설명 카드 |
| 주인공 | 짙은 원 마디(관여 지점) |
| 토큰 | `--bl-r-m` `--bl-shadow` `--br-accent-on-dark` `--br-card` `--br-cobalt` `--br-font-kr` `--br-hairline` `--br-navy` `--br-text-2` `--br-text-3` |
| 할 것 | 마디는 4~6개 · 설명 카드는 해당 마디 바로 아래 |
| 하지 말 것 | 모든 마디에 설명 · 화살표 대신 표 |
| 바꿀 곳 | 마디 아이콘(bl-i--*) · 이름 · 설명 카드의 grid-column 위치 |

본문(`slides.html` 에 그대로 — 머리띠 · 꼬리띠는 빌드가 단다):

```html
<section id="l-path" data-name="국내 · 데이터센터 전력" data-notes="…">
<h2 class="bl-title">GW급 AI 데이터센터, <em>전력설비부터 협력</em></h2>
<p class="bl-lede">11월 16일 라온텔레콤 · 마루중공업 업무협약 · GW급 신규 AI 데이터센터 사업 공동 발굴<button type="button" class="bl-ev" data-ev="E05" data-claim="345kV 변전소 기자재 · 800V 직류배전">출처</button></p>
<div class="x-pw bl-fill">
  <div class="x-line">
    <div class="x-p"><span class="x-ic"><i class="bl-i bl-i--radio-tower"></i></span><b>전력망</b><span>초고압 교류</span></div>
    <div class="x-p is-key"><span class="x-ic"><i class="bl-i bl-i--zap"></i></span><b>345kV 변전소</b><span>협약 ①</span></div>
    <div class="x-p"><span class="x-ic"><i class="bl-i bl-i--repeat"></i></span><b>교류 → 직류</b><span>변환마다 손실</span></div>
    <div class="x-p is-key"><span class="x-ic"><i class="bl-i bl-i--cable"></i></span><b>800V 직류배전</b><span>협약 ②</span></div>
    <div class="x-p"><span class="x-ic"><i class="bl-i bl-i--server"></i></span><b>서버 랙</b><span>GW급 연산</span></div>
  </div>
  <div class="x-notes">
    <div class="x-n" style="grid-column: 2"><span class="bl-lbl">협약 ① · 전력망 쪽</span><h3>변압기 등 장납기 기자재</h3><p>공급계획을 미리 협의 — 데이터센터 가동 시점을 좌우하는 설비</p></div>
    <div class="x-n" style="grid-column: 4"><span class="bl-lbl">협약 ② · 서버 쪽</span><h3>변환 단계 줄이는 직류배전</h3><p>800V 직류 배전 기술 공동 검토 · 실증</p></div>
  </div>
</div>
</section>
```

맞춤 CSS(장 안 `<style data-own>` — 선택자는 장 id 로 묶여 있다. 새 장에 쓸 때 id 를 바꾸면 선택자도 함께):

```css
#l-path .x-pw { display: grid; align-content: center; gap: 0 }
#l-path .x-line { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); position: relative }
#l-path .x-line::before { content: ""; position: absolute; left: 10%; right: 10%; top: 3.2rem; border-top: .3rem solid var(--br-hairline) }
#l-path .x-p { position: relative; display: grid; justify-items: center; gap: .6rem; text-align: center }
#l-path .x-ic { width: 6.4rem; height: 6.4rem; display: grid; place-items: center; border-radius: 50%;
               background: var(--br-card); color: var(--br-text-2); box-shadow: inset 0 0 0 .2rem var(--br-hairline) }
#l-path .x-ic .bl-i { font-size: 2.4rem }
#l-path .x-p b { font: 800 1.45rem/1.2 var(--br-font-kr); color: var(--br-navy) }
#l-path .x-p span { font: 600 1.05rem/1 var(--br-font-kr); color: var(--br-text-3) }
#l-path .x-p.is-key .x-ic { background: var(--br-navy); color: var(--br-accent-on-dark); box-shadow: none }
#l-path .x-p.is-key span { color: var(--br-cobalt) }
#l-path .x-notes { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); margin-top: 2rem }
#l-path .x-n { position: relative; margin: 1.6rem -6rem 0; padding: 1.4rem 1.6rem; display: grid; gap: .45rem;
              border-radius: var(--bl-r-m); background: var(--br-card); box-shadow: var(--bl-shadow); border-top: .3rem solid var(--br-navy) }
#l-path .x-n::before { content: ""; position: absolute; left: 50%; top: -1.9rem; height: 1.6rem; border-left: .2rem dashed var(--br-navy) }
#l-path .x-n .bl-lbl { color: var(--br-cobalt) }
#l-path .x-n h3 { margin: 0; font: 800 1.45rem/1.25 var(--br-font-kr); color: var(--br-navy) }
#l-path .x-n p { margin: 0; font: 500 1.15rem/1.45 var(--br-font-kr); color: var(--br-text-2) }

```

---

<a id="l-versus"></a>
## 1:1 비교 · `l-versus`

| 항목 | 내용 |
|---|---|
| 내용 모양 | 두 선택지를 같은 기준으로 — 요금제 · 모델 · 안 A/B |
| 구조 | 가격표 카드 둘(같은 행 순서) + 가운데 배수 · 차이 + 아래 비교 기준 한 줄 |
| 주인공 | 오른쪽(또는 권장) 카드 숫자 |
| 토큰 | `--bl-pt-orange-d` `--bl-r-l` `--bl-shadow` `--br-card` `--br-cobalt` `--br-font-kr` `--br-font-num` `--br-hairline` `--br-navy` `--br-on-dark` `--br-on-dark-2` `--br-page` `--br-text` `--br-text-2` |
| 할 것 | 두 카드의 행 순서 · 단위 동일 · 비교 기준(무엇으로 고르나)을 반드시 함께 |
| 하지 말 것 | 항목 수가 다른 두 카드 · 셋 이상 비교(→ 표나 막대) |
| 바꿀 곳 | 카드 머리 · 행 라벨 · 가격 · 가운데 배수 |

본문(`slides.html` 에 그대로 — 머리띠 · 꼬리띠는 빌드가 단다):

```html
<section id="l-versus" data-name="글로벌 · 모델 가격" data-notes="…">
<h2 class="bl-title">누리 6.2 두 모델, <em>토큰 단가 4배 차이</em></h2>
<p class="bl-lede">11월 17일 Pro · Lite 공개 · 표준 API 100만 토큰당 요금 · 달러<button type="button" class="bl-ev" data-ev="E06" data-claim="입력 8 · 2달러 · 출력 40 · 10달러">출처</button></p>
<div class="x-vs bl-fill">
  <div class="x-plan">
    <p class="x-plan-h"><b>Lite</b><span>일상 · 다단계 업무용</span></p>
    <div class="x-price"><span class="bl-lbl">입력</span><strong>$2</strong></div>
    <div class="x-price"><span class="bl-lbl">출력</span><strong>$10</strong></div>
  </div>
  <div class="x-mult"><b>×4</b><span>입력 · 출력 모두</span></div>
  <div class="x-plan is-key">
    <p class="x-plan-h"><b>Pro</b><span>복잡한 전문 작업용</span></p>
    <div class="x-price"><span class="bl-lbl">입력</span><strong>$8</strong></div>
    <div class="x-price"><span class="bl-lbl">출력</span><strong>$40</strong></div>
  </div>
  <p class="x-vs-n"><span class="bl-lbl">비교 기준</span>모델 단가가 아니라 검토를 통과한 <b>결과 1건당 비용</b> — 같은 업무를 두 모델로 돌려 실측</p>
</div>
</section>
```

맞춤 CSS(장 안 `<style data-own>` — 선택자는 장 id 로 묶여 있다. 새 장에 쓸 때 id 를 바꾸면 선택자도 함께):

```css
#l-versus .x-vs { display: grid; grid-template-columns: minmax(0, 1fr) 11rem minmax(0, 1fr); grid-template-rows: 1fr auto; gap: 1.6rem 1rem; align-items: stretch }
#l-versus .x-plan { display: grid; grid-template-rows: auto 1fr 1fr; border-radius: var(--bl-r-l); background: var(--br-card); box-shadow: var(--bl-shadow); overflow: hidden }
#l-versus .x-plan-h { margin: 0; display: flex; align-items: baseline; justify-content: space-between; padding: 1.4rem 2rem;
                    background: var(--br-page) }
#l-versus .x-plan-h b { font: 800 2.2rem/1 var(--br-font-kr); color: var(--br-navy) }
#l-versus .x-plan-h span { font: 600 1.15rem/1 var(--br-font-kr); color: var(--br-text-2) }
#l-versus .x-plan.is-key .x-plan-h { background: var(--br-navy) }
#l-versus .x-plan.is-key .x-plan-h b { color: var(--br-on-dark) }
#l-versus .x-plan.is-key .x-plan-h span { color: var(--br-on-dark-2) }
#l-versus .x-price { display: flex; align-items: center; justify-content: space-between; padding: 0 2rem; border-top: 1px solid var(--br-hairline) }
#l-versus .x-price strong { font: 800 4.4rem/1 var(--br-font-num); color: var(--br-text-2) }
#l-versus .x-plan.is-key .x-price strong { color: var(--br-cobalt) }
#l-versus .x-mult { align-self: center; display: grid; justify-items: center; gap: .5rem }
#l-versus .x-mult b { font: 900 3.6rem/1 var(--br-font-num); color: var(--bl-pt-orange-d) }
#l-versus .x-mult span { font: 600 1.05rem/1.2 var(--br-font-kr); color: var(--br-text-2); text-align: center }
#l-versus .x-vs-n { grid-column: 1 / -1; margin: 0; display: flex; gap: 1.2rem; align-items: baseline; font: 500 1.25rem/1.5 var(--br-font-kr); color: var(--br-text) }
#l-versus .x-vs-n b { color: var(--br-navy) }

```

---

<a id="l-taxonomy"></a>
## 분류 · 구성 · `l-taxonomy`

| 항목 | 내용 |
|---|---|
| 내용 모양 | 묶음별 개수가 의미 — 제품군 · 모델 종류 · 조직 단위 |
| 구조 | 개수에 비례한 크기의 타일(트리맵) — 많은 묶음은 크게 · 짙게, 적은 묶음은 작게 |
| 주인공 | 가장 큰 타일 |
| 토큰 | `--bl-r-m` `--bl-r-s` `--br-accent-on-dark` `--br-cobalt` `--br-dark-line` `--br-font-kr` `--br-font-num` `--br-navy` `--br-on-dark` `--br-text` `--br-tint` |
| 할 것 | 타일 크기 = 개수 · 타일 안에 실제 항목 이름 |
| 하지 말 것 | 모든 타일 같은 크기(→ 그냥 목록이 됨) · 색으로만 묶음 구분 |
| 바꿀 곳 | grid-template-areas(타일 배치) · 타일 내용 |

본문(`slides.html` 에 그대로 — 머리띠 · 꼬리띠는 빌드가 단다):

```html
<section id="l-taxonomy" data-name="글로벌 · 업무 특화 모델" data-notes="…">
<h2 class="bl-title">사라소프트, <em>업무 특화 모델 7종</em></h2>
<p class="bl-lede">11월 17일 연례 개발자 행사 · 범용 모델 하나가 아니라 작업별 모델 조합 · 성능 비교 수치는 인용 제외<button type="button" class="bl-ev" data-ev="E07" data-claim="신규 모델 7종 공식 분류">출처</button></p>
<div class="x-tm bl-fill">
  <div class="x-t is-2 a"><p><i class="bl-i bl-i--git-branch"></i>코딩<b>2</b></p><span>SC Code 2</span><span>SC Code 2 Flash</span></div>
  <div class="x-t is-2 b"><p><i class="bl-i bl-i--headset"></i>음성<b>2</b></p><span>SC Voice 1</span><span>SC Transcribe</span></div>
  <div class="x-t c"><p><i class="bl-i bl-i--shield-check"></i>보안<b>1</b></p><span>SC Guard 2</span></div>
  <div class="x-t d"><p><i class="bl-i bl-i--image"></i>이미지<b>1</b></p><span>SC Image 2.7</span></div>
  <div class="x-t e"><p><i class="bl-i bl-i--scale"></i>판단<b>1</b></p><span>SC Decide 1.1</span></div>
  <p class="x-tm-n"><span class="bl-lbl">평가 기준도 업무별</span>코드 — 수정 정확도 · 음성 — 지연 · 전사 오류 · 보안 — 탐지 누락</p>
</div>
</section>
```

맞춤 CSS(장 안 `<style data-own>` — 선택자는 장 id 로 묶여 있다. 새 장에 쓸 때 id 를 바꾸면 선택자도 함께):

```css
#l-taxonomy .x-tm { display: grid; grid-template-columns: 1fr 1fr 1fr; grid-template-rows: 1fr 1fr auto; gap: .8rem;
                   grid-template-areas: "a b c" "a b d" "n n e" }
#l-taxonomy .x-tm .a { grid-area: a } #l-taxonomy .x-tm .b { grid-area: b } #l-taxonomy .x-tm .c { grid-area: c }
#l-taxonomy .x-tm .d { grid-area: d } #l-taxonomy .x-tm .e { grid-area: e }
#l-taxonomy .x-t { display: flex; flex-direction: column; gap: .7rem; padding: 1.5rem 1.8rem; border-radius: var(--bl-r-m); background: var(--br-tint) }
#l-taxonomy .x-t.is-2 { background: var(--br-navy) }
#l-taxonomy .x-t p { margin: 0 0 auto; display: flex; align-items: center; gap: .7rem; font: 800 1.5rem/1 var(--br-font-kr); color: var(--br-navy) }
#l-taxonomy .x-t p b { margin-left: auto; font: 800 2.6rem/1 var(--br-font-num); color: var(--br-cobalt) }
#l-taxonomy .x-t.is-2 p { color: var(--br-on-dark) }
#l-taxonomy .x-t.is-2 p b { font-size: 4.4rem; color: var(--br-accent-on-dark) }
#l-taxonomy .x-t span { font: 600 1.2rem/1.3 var(--br-font-kr); color: var(--br-text) }
#l-taxonomy .x-t.is-2 span { padding: .8rem 1rem; border-radius: var(--bl-r-s); background: var(--br-dark-line); color: var(--br-on-dark) }
#l-taxonomy .x-tm-n { grid-area: n; margin: 0; align-self: center; display: flex; gap: 1.2rem; align-items: baseline;
                     font: 500 1.25rem/1.5 var(--br-font-kr); color: var(--br-text) }

```

---

<a id="l-plan"></a>
## 계획 · 목표 · `l-plan`

| 항목 | 내용 |
|---|---|
| 내용 모양 | 지금 한 일과 몇 년 목표 — 협약 · 투자 계획 · 로드맵 |
| 구조 | 위 큰 숫자 3칸(목표) + 아래 연표(지금 칸은 짙게, 기간 띠는 연도 칸에 맞춤) |
| 주인공 | 위 큰 숫자 중 핵심 하나(코발트) |
| 토큰 | `--bl-font-mono` `--bl-r-s` `--br-accent-on-dark` `--br-cobalt` `--br-font-kr` `--br-font-num` `--br-hairline` `--br-navy` `--br-on-dark` `--br-on-dark-2` `--br-text-2` `--br-tint` |
| 할 것 | 지금 한 일과 목표를 구분해 표시 · 기간 띠를 실제 연도 칸에 맞춤 |
| 하지 말 것 | 목표 숫자를 이미 이룬 것처럼 · 연표 칸과 띠 어긋남 |
| 바꿀 곳 | 큰 숫자 3칸 · 연도 칸 수 · 띠 grid-column |

본문(`slides.html` 에 그대로 — 머리띠 · 꼬리띠는 빌드가 단다):

```html
<section id="l-plan" data-name="국내 · 제조 AI" data-notes="…">
<h2 class="bl-title">스마트공장 <em>2,000곳 이상</em> 지원 목표</h2>
<p class="bl-lede">11월 18일 소관 부처 · 대기업 11곳 · 유관기관 5곳 상생협약 · 청주<button type="button" class="bl-ev" data-ev="E08" data-claim="2027–2031 민관 2조 원 · 2,000곳 이상">출처</button></p>
<div class="x-fc bl-fill">
  <div class="x-goals">
    <div><span class="bl-lbl">민관 재원 목표</span><strong>2<small>조 원</small></strong></div>
    <div><span class="bl-lbl">스마트공장 구축 지원</span><strong>2,000<small>곳 이상</small></strong></div>
    <div><span class="bl-lbl">협약 참여</span><strong>16<small>곳 · 대기업 11 · 기관 5</small></strong></div>
  </div>
  <div class="x-road">
    <div class="x-yr"><span>2026</span><span>2027</span><span>2028</span><span>2029</span><span>2030</span><span>2031</span></div>
    <div class="x-run">
      <div class="x-now"><b>11월</b>협약 체결<span>이번 주</span></div>
      <div class="x-span"><b>재원 조성 · 구축 지원</b><span>5년 · 상생형 스마트공장 · 협업 과제 사업화</span></div>
    </div>
  </div>
</div>
</section>
```

맞춤 CSS(장 안 `<style data-own>` — 선택자는 장 id 로 묶여 있다. 새 장에 쓸 때 id 를 바꾸면 선택자도 함께):

```css
#l-plan .x-fc { display: grid; grid-template-rows: auto auto; align-content: center; gap: 3rem }
#l-plan .x-goals { display: grid; grid-template-columns: 1fr 1fr 1fr; border-top: .18rem solid var(--br-navy) }
#l-plan .x-goals > div { display: grid; gap: .7rem; padding: 1.5rem 2rem 0 0 }
#l-plan .x-goals > div + div { padding-left: 2rem; border-left: 1px solid var(--br-hairline) }
#l-plan .x-goals strong { font: 800 5.2rem/1 var(--br-font-num); color: var(--br-navy) }
#l-plan .x-goals > div:nth-child(2) strong { color: var(--br-cobalt) }
#l-plan .x-goals small { font: 700 1.3rem/1 var(--br-font-kr); color: var(--br-text-2); margin-left: .4rem }
#l-plan .x-road { display: grid; gap: .8rem }
#l-plan .x-yr, #l-plan .x-run { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)) }
#l-plan .x-yr span { font: 700 1.15rem/1 var(--bl-font-mono); color: var(--br-text-2); padding: 0 0 .6rem .8rem; border-left: 1px solid var(--br-hairline) }
#l-plan .x-yr span:first-child { color: var(--br-cobalt) }
#l-plan .x-now { display: grid; gap: .3rem; margin-right: .8rem; padding: 1.1rem 1.2rem; border-radius: var(--bl-r-s); background: var(--br-navy);
                  font: 800 1.3rem/1.2 var(--br-font-kr); color: var(--br-on-dark) }
#l-plan .x-now b { font: 700 1.0rem/1 var(--bl-font-mono); color: var(--br-accent-on-dark) }
#l-plan .x-now span { font: 500 1.0rem/1 var(--br-font-kr); color: var(--br-on-dark-2) }
#l-plan .x-span { grid-column: 2 / 7; display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: 0 2rem;
                   border-radius: var(--bl-r-s); background: var(--br-tint) }
#l-plan .x-span b { font: 800 1.5rem/1 var(--br-font-kr); color: var(--br-navy) }
#l-plan .x-span span { font: 500 1.1rem/1.3 var(--br-font-kr); color: var(--br-text-2) }

```

---

<a id="l-screen"></a>
## 화면 · 사용법 · `l-screen`

| 항목 | 내용 |
|---|---|
| 내용 모양 | 기능 · 화면이 바뀜 — 앱 업데이트 · 새 도구 |
| 구조 | 왼쪽 큰 목업(실제 쓰임 예) + 오른쪽 사용 순서 3단계(마지막 단계만 짙게) |
| 주인공 | 목업 속 바뀐 부분(번역문 · 새 버튼) |
| 토큰 | `--bl-r-l` `--bl-r-m` `--bl-shadow` `--br-card` `--br-cobalt` `--br-font-kr` `--br-font-num` `--br-hairline` `--br-navy` `--br-on-dark` `--br-page` `--br-text` `--br-text-2` `--br-tint` |
| 할 것 | 목업이 재구성이면 「실제 화면 아님」 표기 · 목업 속 대화는 자연스러운 말투 |
| 하지 말 것 | 실제 캡처인 척 · 목업 속 글까지 개조식으로 |
| 바꿀 곳 | 목업 내용 · 단계 3개 |

본문(`slides.html` 에 그대로 — 머리띠 · 꼬리띠는 빌드가 단다):

```html
<section id="l-screen" data-name="국내 · 생활 AI" data-notes="…">
<h2 class="bl-title">메신저 T, <em>받은 메시지 아래 자동 번역</em></h2>
<p class="bl-lede">11월 19일 v26.10.0 업데이트 · AI 비서가 외국어로 감지한 수신 메시지에 번역 표시<button type="button" class="bl-ev" data-ev="E09" data-claim="원문 아래 번역문 표시">출처</button></p>
<div class="x-kk bl-fill">
  <div class="x-phone">
    <p class="x-phone-h">해외 협력사 채팅방<span class="bl-lbl">자동 번역 켜짐</span></p>
    <div class="x-msg"><p>Can we move the review to ten tomorrow?</p><p class="x-tr">내일 검토를 10시로 옮길 수 있을까?</p></div>
    <div class="x-msg is-me"><p>네, 10시로 하죠</p></div>
    <div class="x-msg"><p>Great. I'll share the test report tonight.</p><p class="x-tr">좋아요. 시험 보고서는 오늘 밤 보낼게요</p></div>
    <p class="x-phone-f bl-lbl">동작 재구성 예시 · 실제 화면 아님</p>
  </div>
  <ol class="x-steps">
    <li><b>1</b><div><h3>AI 실험실</h3><p>메신저 T 설정에서 자동 번역 활성화</p></div></li>
    <li><b>2</b><div><h3>채팅방 설정</h3><p>번역을 쓸 채팅방을 골라 켜기</p></div></li>
    <li class="is-key"><b>3</b><div><h3>원문 아래 번역문</h3><p>외국어 수신 메시지에 설정 언어로 자동 표시</p></div></li>
  </ol>
</div>
</section>
```

맞춤 CSS(장 안 `<style data-own>` — 선택자는 장 id 로 묶여 있다. 새 장에 쓸 때 id 를 바꾸면 선택자도 함께):

```css
#l-screen .x-kk { display: grid; grid-template-columns: 38rem minmax(0, 1fr); gap: 5rem; align-items: center }
#l-screen .x-phone { display: grid; gap: 1rem; padding: 1.6rem; border-radius: var(--bl-r-l); background: var(--br-page);
                  box-shadow: inset 0 0 0 .16rem var(--br-hairline) }
#l-screen .x-phone-h { margin: 0 0 .4rem; display: flex; justify-content: space-between; align-items: center;
                    font: 800 1.25rem/1 var(--br-font-kr); color: var(--br-navy) }
#l-screen .x-phone-f { margin: .4rem 0 0; text-align: center }
#l-screen .x-msg { max-width: 86%; background: var(--br-card); border-radius: var(--bl-r-m); padding: 1rem 1.2rem; box-shadow: var(--bl-shadow) }
#l-screen .x-msg p { margin: 0; font: 500 1.2rem/1.45 var(--br-font-kr); color: var(--br-text) }
#l-screen .x-msg .x-tr { margin-top: .55rem; padding-top: .55rem; border-top: 1px dashed var(--br-hairline); color: var(--br-cobalt); font-weight: 700 }
#l-screen .x-msg.is-me { justify-self: end; background: var(--br-tint); box-shadow: none }
#l-screen .x-steps { list-style: none; margin: 0; padding: 0; display: grid; gap: 0; position: relative }
#l-screen .x-steps li { display: grid; grid-template-columns: 4.4rem minmax(0, 1fr); gap: 1.6rem; align-items: center; padding: 1.6rem 0;
                     border-bottom: 1px solid var(--br-hairline) }
#l-screen .x-steps li > b { width: 4.4rem; height: 4.4rem; display: grid; place-items: center; border-radius: 50%;
                         background: var(--br-tint); font: 800 1.6rem/1 var(--br-font-num); color: var(--br-navy) }
#l-screen .x-steps li.is-key > b { background: var(--br-navy); color: var(--br-on-dark) }
#l-screen .x-steps h3 { margin: 0 0 .35rem; font: 800 1.6rem/1.2 var(--br-font-kr); color: var(--br-navy) }
#l-screen .x-steps p { margin: 0; font: 500 1.2rem/1.45 var(--br-font-kr); color: var(--br-text-2) }

```

---

<a id="l-stages"></a>
## 단계별 수치 · `l-stages`

| 항목 | 내용 |
|---|---|
| 내용 모양 | 업무 · 공정 단계마다 값이 다름 — 활용률 · 소요 시간 · 불량률 |
| 구조 | 흐름 순서 세로 막대 + 위에 묶음(앞단 · 뒷단) 평균 띠 + 평균 점선 |
| 주인공 | 가장 높은 묶음과 가장 낮은 묶음의 대비(코발트 vs 주황) |
| 토큰 | `--bl-pt-gray` `--bl-pt-orange` `--bl-pt-orange-d` `--bl-r-xs` `--br-cobalt` `--br-font-kr` `--br-font-num` `--br-navy` `--br-text-2` `--br-text-3` |
| 할 것 | 막대 순서 = 실제 흐름 순서(크기순 아님) · 묶음 평균을 위 띠로 |
| 하지 말 것 | 크기순 정렬로 흐름을 지움 · 묶음마다 다른 색 셋 이상 |
| 바꿀 곳 | 막대 높이(--h) · 묶음 띠의 grid-column · 평균선 위치 |

본문(`slides.html` 에 그대로 — 머리띠 · 꼬리띠는 빌드가 단다):

```html
<section id="l-stages" data-name="국내 · 방송 AI 실태" data-notes="…">
<h2 class="bl-title">방송 AI, <em>앞단 40%대 · 뒷단 20%</em></h2>
<p class="bl-lede">11월 17일 방송 소관 기관 실태조사 · 사업자 101곳 · 9–10월 · 사용 경험 88% · 업무 기준 활용률 평균 30.9%<button type="button" class="bl-ev" data-ev="E10" data-claim="업무 기준 활용률 평균 30.9%">출처</button></p>
<div class="x-md bl-fill">
  <div class="x-grp-row">
    <div class="x-g is-front" style="grid-column: 1 / 3"><b>앞단 평균 41.7%</b><span>기획 · 제작</span></div>
    <div class="x-g" style="grid-column: 3"><b>30.2%</b><span>후반제작</span></div>
    <div class="x-g is-back" style="grid-column: 4 / 6"><b>뒷단 평균 20.6%</b><span>유통 · 성과분석</span></div>
  </div>
  <div class="x-bars5">
    <div class="is-key" style="--h: 81.4%"><em>40.7</em><i></i><span>기획</span></div>
    <div class="is-key" style="--h: 85.2%"><em>42.6</em><i></i><span>제작</span></div>
    <div style="--h: 60.4%"><em>30.2</em><i></i><span>후반제작</span></div>
    <div class="is-hot" style="--h: 40.6%"><em>20.3</em><i></i><span>유통</span></div>
    <div class="is-hot" style="--h: 41.6%"><em>20.8</em><i></i><span>성과분석</span></div>
    <p class="x-avg" style="--h: 61.8%"><span>평균 30.9</span></p>
  </div>
</div>
</section>
```

맞춤 CSS(장 안 `<style data-own>` — 선택자는 장 id 로 묶여 있다. 새 장에 쓸 때 id 를 바꾸면 선택자도 함께):

```css
#l-stages .x-md { display: grid; grid-template-rows: auto 1fr; gap: 2rem; padding: 1.4rem 0 2.4rem }
#l-stages .x-grp-row, #l-stages .x-bars5 { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 2.4rem }
#l-stages .x-g { display: flex; align-items: baseline; gap: .8rem; padding-bottom: .6rem; border-bottom: .2rem solid var(--bl-pt-gray) }
#l-stages .x-g b { font: 800 1.5rem/1 var(--br-font-num); color: var(--br-text-2) }
#l-stages .x-g span { font: 600 1.05rem/1 var(--br-font-kr); color: var(--br-text-3) }
#l-stages .x-g.is-front { border-bottom-color: var(--br-cobalt) } #l-stages .x-g.is-front b { color: var(--br-cobalt) }
#l-stages .x-g.is-back { border-bottom-color: var(--bl-pt-orange) } #l-stages .x-g.is-back b { color: var(--bl-pt-orange-d) }
#l-stages .x-bars5 { position: relative; align-items: end; border-bottom: .14rem solid var(--br-text-3) }
#l-stages .x-bars5 > div { height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center; gap: .5rem; position: relative }
#l-stages .x-bars5 i { display: block; width: 100%; height: calc(var(--h) * .84); border-radius: var(--bl-r-xs) var(--bl-r-xs) 0 0; background: var(--bl-pt-gray) }
#l-stages .x-bars5 .is-key i { background: var(--br-cobalt) }
#l-stages .x-bars5 .is-hot i { background: var(--bl-pt-orange) }
#l-stages .x-bars5 em { font: 800 1.8rem/1 var(--br-font-num); font-style: normal; color: var(--br-navy) }
#l-stages .x-bars5 span { position: absolute; bottom: -2.1rem; font: 700 1.1rem/1 var(--br-font-kr); color: var(--br-text-2) }
#l-stages .x-avg { position: absolute; left: 0; right: 0; bottom: calc(var(--h) * .84); margin: 0; border-top: .14rem dashed var(--br-text-2) }
#l-stages .x-avg span { position: absolute; right: 0; top: -1.7rem; font: 700 1.0rem/1 var(--br-font-kr); color: var(--br-text-2) }

```

---

<a id="l-map"></a>
## 요약 지도 · `l-map`

| 항목 | 내용 |
|---|---|
| 내용 모양 | 덱 첫머리 — 여러 건을 한 장에 배치(목차 대신) |
| 구조 | 가치사슬 · 흐름 칸(6칸) 머리 + 칸마다 해당 항목 카드(번호 · 이름 · 핵심 수치) |
| 주인공 | 제목의 결론 한 줄 |
| 토큰 | `--bl-font-mono` `--bl-fs-body` `--bl-fs-h3` `--bl-pt-gray` `--bl-pt-orange` `--bl-r-l` `--bl-r-m` `--bl-r-s` `--bl-r-xs` `--bl-shadow` `--bl-sp-5` `--br-accent-on-dark` `--br-card` `--br-cobalt` `--br-font-kr` `--br-font-num` `--br-hairline` `--br-navy` `--br-on-dark` `--br-on-dark-2` `--br-page` `--br-text` `--br-text-2` `--br-track` |
| 할 것 | 칸 순서가 의미(흐름 · 단계) · 카드마다 핵심 수치 하나 |
| 하지 말 것 | 칸 없이 목록 · 카드에 설명 문장 |
| 바꿀 곳 | 칸 이름 · 카드 배치(grid-column) |

본문(`slides.html` 에 그대로 — 머리띠 · 꼬리띠는 빌드가 단다):

```html
<section id="l-map" data-name="이번 주 한 장" data-notes="…">
<h2 class="bl-title">돈은 칩 · 전력으로, <em>경쟁은 단가 · 특화로</em></h2>
<p class="bl-lede">11월 16–21일 · 글로벌 5건 · 국내 5건 · 기관 · 기업 공식 발표 기준 <strong>열 건을 AI 가치사슬 위에 배치</strong></p>
<div class="x-chain bl-fill">
  <div class="x-grp" style="grid-column: 1 / 5"><span class="bl-lbl">인프라 · 01–05</span></div>
  <div class="x-grp is-use" style="grid-column: 5 / 7"><span class="bl-lbl">활용 · 06–10</span></div>
  <div class="x-st" style="grid-column: 1">자본<span>상장 · 조달</span></div>
  <div class="x-st" style="grid-column: 2">칩<span>매출 · 통제</span></div>
  <div class="x-st" style="grid-column: 3">부품<span>기판 · MLCC</span></div>
  <div class="x-st" style="grid-column: 4">전력<span>변전 · 배전</span></div>
  <div class="x-st is-use" style="grid-column: 5">모델<span>단가 · 특화</span></div>
  <div class="x-st is-use" style="grid-column: 6">현장<span>제조 · 생활 · 방송</span></div>
  <div class="x-col" style="grid-column: 1">
    <div class="x-it"><b>01</b><p>가온AI 나스닥 상장</p><strong>1,195억 달러</strong></div>
  </div>
  <div class="x-col" style="grid-column: 2">
    <div class="x-it"><b>02</b><p>나래칩 데이터센터 비중</p><strong>92.9%</strong></div>
    <div class="x-it"><b>03</b><p>A국, 칩 원격 이용 통제</p></div>
  </div>
  <div class="x-col" style="grid-column: 3">
    <div class="x-it"><b>04</b><p>다온전자 · 나래칩 협력 확대</p><strong>2029 양산</strong></div>
  </div>
  <div class="x-col" style="grid-column: 4">
    <div class="x-it"><b>05</b><p>SKT · 마루중공업 전력 협약</p><strong>345kV · 800V</strong></div>
  </div>
  <div class="x-col" style="grid-column: 5">
    <div class="x-it"><b>06</b><p>누리 6.2 두 모델 단가</p><strong>4배 차이</strong></div>
    <div class="x-it"><b>07</b><p>MS 업무 특화 모델</p><strong>7종</strong></div>
  </div>
  <div class="x-col" style="grid-column: 6">
    <div class="x-it"><b>08</b><p>스마트공장 지원 목표</p><strong>2,000곳+</strong></div>
    <div class="x-it"><b>09</b><p>메신저 T 자동 번역</p></div>
    <div class="x-it"><b>10</b><p>방송 AI 제작 · 유통 격차</p><strong>22.3%p</strong></div>
  </div>
</div>
<p class="bl-src">순위 기준 — 산업 파급 범위 · 이번 주에 달라진 점 · 국내 현장 관련성을 종합한 편집 순위</p>
</section>
```

맞춤 CSS(장 안 `<style data-own>` — 선택자는 장 id 로 묶여 있다. 새 장에 쓸 때 id 를 바꾸면 선택자도 함께):

```css
/* ── 공통: 뉴스 장 짜임 ───────────────────────────── */
.x-news { display: grid; grid-template-columns: 30rem minmax(0, 1fr); gap: var(--bl-sp-5); align-items: stretch }
.x-side { display: grid; grid-template-rows: auto 1fr; min-width: 0 }
.x-tag { margin: 0; padding: 0 0 .9rem; border-bottom: .18rem solid var(--br-navy) }
.x-tag .bl-lbl { color: var(--br-navy) }
.x-pts { list-style: none; margin: 0; padding: 0; display: grid; grid-auto-rows: 1fr }
.x-pts li { display: grid; grid-template-columns: 2.6rem minmax(0, 1fr); align-items: center;
            border-bottom: 1px solid var(--br-hairline);
            font: 500 1.3rem/1.45 var(--br-font-kr); color: var(--br-text) }
.x-pts li > b { font: 700 1.05rem/1 var(--bl-font-mono); color: var(--br-cobalt) }
.x-pts li strong { color: var(--br-navy); font-weight: 800 }
.x-fig { background: var(--br-card); border-radius: var(--bl-r-l); box-shadow: var(--bl-shadow);
         padding: 2rem 2.6rem; display: flex; flex-direction: column; gap: 1.4rem; min-width: 0 }
.x-fig-h { display: flex; justify-content: space-between; gap: 1rem; align-items: baseline;
           padding-bottom: .9rem; border-bottom: 1px solid var(--br-hairline) }
.x-fig-h .bl-lbl { color: var(--br-text-2) }
.x-big { margin: 0; font: 800 5.6rem/1 var(--br-font-num); color: var(--br-navy); letter-spacing: -.02em }
.x-big small { font: 700 1.8rem/1 var(--br-font-kr); color: var(--br-text-2); margin-left: .4rem }
.x-mid { margin-block: auto }
/* 가로 막대 */
.x-bars { display: grid; gap: 1.1rem }
.x-bar { display: grid; grid-template-columns: 8.5rem minmax(0, 1fr) 5.5rem; gap: 1.2rem; align-items: center;
         font: 600 var(--bl-fs-body)/1.2 var(--br-font-kr); color: var(--br-text) }
.x-bar i { display: block; height: 1.7rem; border-radius: var(--bl-r-xs); background: var(--br-track); position: relative }
.x-bar i::after { content: ""; position: absolute; inset: 0 auto 0 0; width: var(--w); border-radius: var(--bl-r-xs);
                  background: var(--bl-pt-gray) }
.x-bar.is-key i::after { background: var(--br-cobalt) }
.x-bar.is-hot i::after { background: var(--bl-pt-orange) }
.x-bar em { font: 800 1.3rem/1 var(--br-font-num); font-style: normal; text-align: right; color: var(--br-navy) }
/* 흐름 마디 */
.x-flow { display: grid; grid-auto-flow: column; grid-auto-columns: minmax(0, 1fr); gap: 2.6rem; position: relative }
.x-node { position: relative; background: var(--br-page); border-radius: var(--bl-r-m); padding: 1.5rem 1.5rem;
          display: grid; gap: .4rem; align-content: start }
.x-node + .x-node::before { content: "→"; position: absolute; left: -2.05rem; top: 50%; transform: translateY(-50%);
                            font: 700 1.5rem/1 var(--br-font-kr); color: var(--br-cobalt) }
.x-node h3 { margin: 0; font: 800 1.5rem/1.3 var(--br-font-kr); color: var(--br-navy) }
.x-node p { margin: 0; font: 500 1.1rem/1.45 var(--br-font-kr); color: var(--br-text-2) }
.x-node.is-key { background: var(--br-navy) }
.x-node.is-key h3 { color: var(--br-on-dark) }
.x-node.is-key p { color: var(--br-on-dark-2) }
.x-node.is-key .bl-lbl { color: var(--br-accent-on-dark) }

/* ── 이번 주 한 장: 가치사슬 지도 ─────────────────── */
#l-map .x-chain { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); grid-template-rows: auto auto 1fr; gap: .7rem .6rem }
#l-map .x-grp { grid-row: 1; display: flex; align-items: center; gap: .8rem; padding-bottom: .7rem;
              border-bottom: .2rem solid var(--br-cobalt) }
#l-map .x-grp.is-use { border-bottom-color: var(--br-cobalt) }
#l-map .x-grp .bl-lbl { color: var(--br-cobalt) }
#l-map .x-grp.is-use .bl-lbl { color: var(--br-cobalt) }
#l-map .x-st { grid-row: 2; background: var(--br-navy); color: var(--br-on-dark); padding: 1.2rem 1.3rem;
             font: 800 var(--bl-fs-h3)/1.2 var(--br-font-kr); border-radius: var(--bl-r-s) }
#l-map .x-st.is-use { background: var(--br-cobalt) }
#l-map .x-st span { display: block; font: 500 1.0rem/1.3 var(--br-font-kr); color: var(--br-on-dark-2); margin-top: .25rem }
#l-map .x-col { grid-row: 3; display: grid; gap: .6rem; grid-auto-rows: 7.4rem; align-content: start }
#l-map .x-it { background: var(--br-card); box-shadow: var(--bl-shadow); border-radius: var(--bl-r-s);
             padding: 1.2rem 1.3rem; display: grid; gap: .5rem }
#l-map .x-it b { font: 700 1.0rem/1 var(--bl-font-mono); color: var(--br-cobalt) }
#l-map .x-it p { margin: 0; font: 700 var(--bl-fs-body)/1.35 var(--br-font-kr); color: var(--br-text) }
#l-map .x-it strong { font: 800 2rem/1.1 var(--br-font-num); color: var(--br-navy) }

```

---

<a id="l-watch"></a>
## 점검 카드 · `l-watch`

| 항목 | 내용 |
|---|---|
| 내용 모양 | 덱 끝 — 다음에 확인할 것 2~4개 |
| 구조 | 같은 크기 카드 3장(번호 · 지표 · 왜 · 확인할 곳 · 이어 볼 항목), 가장 중요한 하나만 짙게 |
| 주인공 | 짙은 카드 |
| 토큰 | `--bl-font-mono` `--bl-fs-body` `--bl-r-l` `--bl-r-s` `--bl-shadow` `--br-accent-on-dark` `--br-card` `--br-cobalt` `--br-dark-line` `--br-font-kr` `--br-font-num` `--br-hairline` `--br-navy` `--br-on-dark` `--br-on-dark-2` `--br-page` `--br-text-2` |
| 할 것 | 확인할 곳(출처 · 방법)을 반드시 · 앞 장 번호로 연결 |
| 하지 말 것 | 카드마다 다른 형식 · 다짐 · 구호 |
| 바꿀 곳 | 카드 내용 · 짙은 카드 위치 |

본문(`slides.html` 에 그대로 — 머리띠 · 꼬리띠는 빌드가 단다):

```html
<section id="l-watch" data-name="다음 주 점검" data-notes="…">
<h2 class="bl-title">다음 주 확인할 세 가지 — <em>납기 · 단가 · 사용률</em></h2>
<p class="bl-lede">이번 주 열 건을 이어 볼 지표 · 후속 공시와 사내 도입 판단에 공통으로 쓰는 기준</p>
<div class="x-w bl-mid">
  <div class="x-w-c"><span class="x-w-n">01</span><h3>부품 · 전력 납기</h3>
    <p>새 랙 출하에 맞춘 기판 · MLCC 증설 일정과 변압기 등 장납기 설비 공급 일정</p>
    <p class="x-w-s"><span class="bl-lbl">확인할 곳</span>공급사 증설 공시 · 분기 실적 · 전력 기자재 수주</p>
    <div class="x-w-f"><span class="bl-lbl">이어 볼 뉴스</span><b>02 · 04 · 05</b></div></div>
  <div class="x-w-c"><span class="x-w-n">02</span><h3>결과 1건당 모델 비용</h3>
    <p>같은 업무를 단가가 다른 모델로 돌려 검토 통과 결과 1건당 비용 비교</p>
    <p class="x-w-s"><span class="bl-lbl">확인할 곳</span>사내 시범 업무 2–3건 실측 · 재작업 횟수 포함</p>
    <div class="x-w-f"><span class="bl-lbl">이어 볼 뉴스</span><b>06 · 07</b></div></div>
  <div class="x-w-c is-key"><span class="x-w-n">03</span><h3>업무별 사용률</h3>
    <p>써 본 사람 수가 아니라 업무 단계별 실제 활용률 — 앞단 · 뒷단 격차 확인</p>
    <p class="x-w-s"><span class="bl-lbl">확인할 곳</span>부서별 업무 단계 활용 조사 · 분기 1회</p>
    <div class="x-w-f"><span class="bl-lbl">이어 볼 뉴스</span><b>08 · 09 · 10</b></div></div>
</div>
</section>
```

맞춤 CSS(장 안 `<style data-own>` — 선택자는 장 id 로 묶여 있다. 새 장에 쓸 때 id 를 바꾸면 선택자도 함께):

```css
#l-watch .x-w { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1.6rem; align-items: stretch }
#l-watch .x-w-c { background: var(--br-card); box-shadow: var(--bl-shadow); border-radius: var(--bl-r-l); padding: 2rem 2.2rem;
                display: flex; flex-direction: column; gap: 1rem }
#l-watch .x-w-n { font: 800 3.6rem/1 var(--br-font-num); color: var(--br-cobalt) }
#l-watch .x-w-c h3 { margin: 0; font: 800 2rem/1.25 var(--br-font-kr); color: var(--br-navy) }
#l-watch .x-w-c p { margin: 0; font: 500 1.3rem/1.5 var(--br-font-kr); color: var(--br-text-2) }
#l-watch .x-w-c .x-w-s { display: grid; gap: .4rem; margin-top: 1rem; padding: 1rem 1.2rem; border-radius: var(--bl-r-s);
                background: var(--br-page); font: 700 var(--bl-fs-body)/1.4 var(--br-font-kr); color: var(--br-navy) }
#l-watch .x-w-c.is-key .x-w-s { background: var(--br-dark-line); color: var(--br-on-dark) }
#l-watch .x-w-f { display: flex; justify-content: space-between; align-items: center;
                border-top: 1px solid var(--br-hairline); padding-top: 1rem }
#l-watch .x-w-f b { font: 700 1.1rem/1 var(--bl-font-mono); color: var(--br-navy) }
#l-watch .x-w-c.is-key { background: var(--br-navy); box-shadow: none }
#l-watch .x-w-c.is-key h3, #l-watch .x-w-c.is-key b { color: var(--br-on-dark) }
#l-watch .x-w-c.is-key p { color: var(--br-on-dark-2) }
#l-watch .x-w-c.is-key .x-w-n, #l-watch .x-w-c.is-key .bl-lbl { color: var(--br-accent-on-dark) }
#l-watch .x-w-c.is-key .x-w-f { border-top-color: var(--br-dark-line) }

```
