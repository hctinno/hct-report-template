# 부품 카드 — 무엇을 어떤 마크업 · 토큰으로

> **생성 파일** — `scripts/build_cards.py` 가 `references/components.yaml`(판단하는 말) ·
> `assets/live-catalog.html` · `examples/*`(마크업 원본) · `assets/blue-live.css`(토큰 원본)로 만든다.
> **대조:** 카드의 HTML 을 그대로 담은 덱 `examples/components/` 를 `verify_repo.py` 가 조립해
> `check_live.py` 로 그린다 — 정의 없는 클래스 · 글자 하한 · 대비 · 넘침이 있으면 실패다.

카드 읽는 법: 쓰는 곳 → 구조(클래스 순서) → 속성(`data-*`) → 토큰 → 할 것 / 하지 말 것 → 복사용 HTML.
장 전체를 어떻게 나눌지는 `LAYOUTS.md`(짜임 카드). 맞는 부품이 없으면 `<style data-own>` 으로 새로 짠다(`DESIGN.md`).

| 부품 | 클래스 | 쓰는 곳 |
|---|---|---|
| [수치 타일 줄](#bl-kpis) | `.bl-kpis` | 핵심 수치 3~5개를 한 줄로 — 현황 요약 · 실적 |
| [가로 막대](#bl-bars) | `.bl-bars` | 항목 몇 개의 크기 비교 — 순위 · 비중 |
| [도넛 + 범례](#bl-donut-box) | `.bl-donut-box` | 합이 100%인 구성 2~6조각 |
| [100% 누적 가로 막대](#bl-stack) | `.bl-stack` | 여러 대상의 구성비를 나란히 — 부서별 · 연도별 비중 |
| [계단형 상승 열](#bl-stair) | `.bl-stair` | 단계가 오를수록 커지는 값 — 성숙도 · 누적 효과 |
| [히어로 띠](#bl-hero) | `.bl-hero` | 장 하나를 대표하는 숫자 한 개를 가로 띠로 |
| [쉐브론 띠](#bl-chev) | `.bl-chev` | 3~5단계 순서 — 절차 · 추진 단계 |
| [간트](#bl-gantt) | `.bl-gantt` | 과제별 기간 · 상태 — 일정 · 로드맵 |
| [이중 레인 연표](#bl-lanes) | `.bl-lanes` | 두 흐름의 사건을 같은 시간축에 — 우리 · 시장, 계획 · 실적 |
| [조직도](#bl-org) | `.bl-org` | 보고 라인 · 위임 관계 |
| [작은 조직](#bl-orgtree) | `.bl-orgtree` | TF · 팀 하나의 구성 |
| [역할 매트릭스](#bl-matrix) | `.bl-matrix` | 과제 × 조직의 주도 · 참여 관계 |
| [좌우 대비](#bl-vs) | `.bl-vs` | 지양 · 지향, 지금 · 바뀐 뒤 두 패널 |
| [결정 요청 판](#bl-decide) | `.bl-decide` | 승인 · 선택을 요청하는 장 |
| [파이프라인 열](#bl-pipe) | `.bl-pipe` | 단계마다 무엇이 들고 나는지 — 처리 흐름 |
| [상단 색띠 카드](#bl-tc) | `.bl-tc` | 병렬 항목 3~5개를 카드로 — 과제 · 사례 |
| [색 머리 열 카드](#bl-hc) | `.bl-hc` | 열마다 묶음이 다른 목록 — 영역별 준비 상태 |
| [탭](#bl-tabset) | `.bl-tabset` | 같은 형식의 사례 여러 개를 한 장에서 전환 |
| [결론 줄 · 장 결론 띠](#bl-concl) | `.bl-concl` | 장(章)의 처음이나 끝, 결정 · 전환 장 — 장(章)마다 한 번 |
| [출처 칩](#bl-ev) | `.bl-ev` | 수치 바로 옆 — 근거 패널로 연결 |
| [작은 막대](#bl-spark) | `.bl-spark` | 수치 카드 · 관전 카드 안에서 추세 3~6점 — 큰 수치 밑 근거 그림 |
| [아이콘 카드](#bl-icards) | `.bl-icards` | 대상 3~5개를 한 줄로 — 사업 분야 · 요인 · 관전 지표 |
| [비교 막대](#bl-cmpbars) | `.bl-cmpbars` | 같은 구간의 지난 값과 지금 값 — 분기 전년 비교 · 연도 추이 |
| [직선 연표](#bl-tline) | `.bl-tline` | 사건 5~8개를 시간 순으로 — 투자 · 인증 · 계약 이력 |

---

<a id="bl-kpis"></a>
## 수치 타일 줄 · `.bl-kpis`

| 항목 | 내용 |
|---|---|
| 쓰는 곳 | 핵심 수치 3~5개를 한 줄로 — 현황 요약 · 실적 |
| 구조(클래스) | `.bl-kpis` → `.bl-kpi` → `.bl-lbl` → `.bl-kpi-v` → `.bl-kpi-d` → `.bl-gauge` → `.bl-kpi--tint` |
| 속성 | `data-c` `data-count` |
| 토큰 | `--bl-ease-out` `--bl-fs-kpi` `--bl-fs-kpi-l` `--bl-fs-lbl` `--bl-fs-sm` `--bl-line` `--bl-shadow` `--br-amber` `--br-card` `--br-cover` `--br-dark-line` `--br-font-kr` `--br-font-num` `--br-hairline` `--br-mark` `--br-on-dark-2` `--br-page` `--br-text` `--br-text-2` `--br-text-3` `--br-tint` `--br-track` |
| 할 것 | 한 줄에 3~5칸 · 숫자는 크게 단위는 작게 · 기준(기간 · 표본)을 라벨에 |
| 하지 말 것 | 6칸 이상 · 칸마다 다른 색 |
| 원본 | `catalog#kpi` — 대조 덱 `examples/components` 장 `c-bl-kpis` |

복사용 HTML(내용만 바꾼다 — 클래스 · 속성 이름은 그대로):

```html
<div class="bl-kpis" style="--n: 4">
  <div class="bl-kpi"><span class="bl-lbl">주간 문의</span><span class="bl-kpi-v" data-count>360<small>건</small></span><p class="bl-kpi-d">4주 평균 · 휴일 제외</p></div>
  <div class="bl-kpi" data-c="2"><span class="bl-lbl">평균 응답</span><span class="bl-kpi-v" data-count>4.1<small>시간</small></span><p class="bl-kpi-d">접수 → 첫 회신</p><span class="bl-gauge" style="--v: .68"></span></div>
  <div class="bl-kpi" data-c="alert"><span class="bl-lbl">재문의</span><span class="bl-kpi-v" data-count="roll">18<small>%</small></span><p class="bl-kpi-d">같은 고객 · 7일 안</p></div>
  <div class="bl-kpi bl-kpi--tint" data-c="4"><span class="bl-lbl">사례집 검색</span><span class="bl-kpi-v" data-count>40<small>회/주</small></span><p class="bl-kpi-d">응대자 9명 기준</p></div>
</div>
```

---

<a id="bl-bars"></a>
## 가로 막대 · `.bl-bars`

| 항목 | 내용 |
|---|---|
| 쓰는 곳 | 항목 몇 개의 크기 비교 — 순위 · 비중 |
| 구조(클래스) | `.bl-bars` → `.bl-bar-row` → `.bl-bar-name` → `.bl-bar-track` → `.bl-bar` → `.bl-bar--key` → `.bl-bar-val` → `.bl-bar--mute` |
| 속성 | — |
| 토큰 | `--bl-ease-out` `--bl-fs-body` `--bl-sp-2` `--br-chan-1` `--br-font-num` `--br-mark-mute` `--br-track` `--br-warn-text` |
| 할 것 | 주인공 막대 하나만 강조색 · 값은 막대 끝에 · 눈금 상한을 라벨에 |
| 하지 말 것 | 모든 막대 다른 색 · 0이 아닌 시작점 |
| 원본 | `catalog#kpi` — 대조 덱 `examples/components` 장 `c-bl-bars` |

복사용 HTML(내용만 바꾼다 — 클래스 · 속성 이름은 그대로):

```html
<div class="bl-bars">
  <div class="bl-bar-row is-key"><span class="bl-bar-name">견적</span><div class="bl-bar-track"><div class="bl-bar bl-bar--key" style="width:92%"></div></div><span class="bl-bar-val">6.2h</span></div>
  <div class="bl-bar-row"><span class="bl-bar-name">기술 문의</span><div class="bl-bar-track"><div class="bl-bar bl-bar--mute" style="width:80%"></div></div><span class="bl-bar-val">5.4h</span></div>
  <div class="bl-bar-row"><span class="bl-bar-name">일정 변경</span><div class="bl-bar-track"><div class="bl-bar bl-bar--mute" style="width:46%"></div></div><span class="bl-bar-val">3.1h</span></div>
  <div class="bl-bar-row"><span class="bl-bar-name">서류 발급</span><div class="bl-bar-track"><div class="bl-bar bl-bar--mute" style="width:39%"></div></div><span class="bl-bar-val">2.6h</span></div>
  <div class="bl-bar-row"><span class="bl-bar-name">기타</span><div class="bl-bar-track"><div class="bl-bar bl-bar--mute" style="width:18%"></div></div><span class="bl-bar-val">1.2h</span></div>
</div>
```

---

<a id="bl-donut-box"></a>
## 도넛 + 범례 · `.bl-donut-box`

| 항목 | 내용 |
|---|---|
| 쓰는 곳 | 합이 100%인 구성 2~6조각 |
| 구조(클래스) | `.bl-donut-box` → `.bl-donut` → `.bl-donut-s` → `.bl-donut-c` → `.bl-cap` → `.bl-donut-leg` |
| 속성 | `data-k` `data-p` |
| 토큰 | `--bl-donut-size` `--bl-ease-out` `--bl-fs-cap` `--bl-fs-sm` `--br-font-kr` `--br-font-num` `--br-hairline` `--br-mark` `--br-on-dark-2` `--br-text-3` `--br-tint` |
| 할 것 | 반드시 scripts/donut.py --live 로 생성 · 가운데 합계 · 핵심 비율 |
| 하지 말 것 | 각도 · dasharray 손으로 쓰기 · 파이 차트 · 7조각 이상 |
| 원본 | `catalog#kpi` — 대조 덱 `examples/components` 장 `c-bl-donut-box` |

복사용 HTML(내용만 바꾼다 — 클래스 · 속성 이름은 그대로):

```html
<div class="bl-donut-box">
  <figure class="bl-donut" role="img" aria-label="비율 분포">
    <svg viewBox="0 0 272 272" aria-hidden="true"><g transform="translate(136,136)">
      <circle class="bl-donut-s" data-k="0" r="110" stroke="var(--br-data-1)" stroke-width="48" stroke-dasharray="346.5 691.2" transform="rotate(-90.00)" style="--i:0;--dash:346.5"></circle>
      <circle class="bl-donut-s" data-k="1" r="110" stroke="var(--br-data-2)" stroke-width="48" stroke-dasharray="181.4 691.2" transform="rotate(92.00)" style="--i:1;--dash:181.4"></circle>
      <circle class="bl-donut-s" data-k="2" r="110" stroke="var(--br-data-3)" stroke-width="48" stroke-dasharray="120.0 691.2" transform="rotate(188.00)" style="--i:2;--dash:120.0"></circle>
      <circle class="bl-donut-s" data-k="3" r="110" stroke="var(--br-data-4)" stroke-width="48" stroke-dasharray="31.7 691.2" transform="rotate(252.00)" style="--i:3;--dash:31.7"></circle>
    </g></svg>
    <figcaption class="bl-donut-c"><b>360<small>건</small></b><span class="bl-cap">주간 문의</span></figcaption>
  </figure>
  <ul class="bl-donut-leg">
    <li data-k="0" data-p="50.6%"><i style="background:var(--br-data-1)"></i><span>전화</span><b>182건</b></li>
    <li data-k="1" data-p="26.7%"><i style="background:var(--br-data-2)"></i><span>메일</span><b>96건</b></li>
    <li data-k="2" data-p="17.8%"><i style="background:var(--br-data-3)"></i><span>채팅</span><b>64건</b></li>
    <li data-k="3" data-p="5.0%"><i style="background:var(--br-data-4)"></i><span>방문</span><b>18건</b></li>
  </ul>
</div>
```

---

<a id="bl-stack"></a>
## 100% 누적 가로 막대 · `.bl-stack`

| 항목 | 내용 |
|---|---|
| 쓰는 곳 | 여러 대상의 구성비를 나란히 — 부서별 · 연도별 비중 |
| 구조(클래스) | `.bl-stack` → `.bl-stack-r` → `.bl-stack-n` → `.bl-stack-b` → `.bl-dl` → `.bl-stack-val` |
| 속성 | `data-c` |
| 토큰 | `--bl-ease-out` `--bl-fs-sm` `--bl-fs-xs` `--br-alert-text` `--br-amber` `--br-card` `--br-font-kr` `--br-font-num` `--br-ok-text` `--br-text-3` |
| 할 것 | 같은 조각 순서 · 같은 색 · 행 끝에 핵심 조각 값 |
| 하지 말 것 | 행마다 조각 순서가 다름 · 조각 7개 이상 |
| 원본 | `catalog#stack` — 대조 덱 `examples/components` 장 `c-bl-stack` |

복사용 HTML(내용만 바꾼다 — 클래스 · 속성 이름은 그대로):

```html
<div class="bl-stack">
  <div class="bl-stack-r is-key"><div class="bl-stack-n">고객지원팀<small>전화 · 메일</small></div><div class="bl-stack-b"><i data-c="1" style="--v: 18"><b class="bl-dl">18</b></i><i data-c="5" style="--v: 22"><b class="bl-dl">22</b></i><i data-c="2" style="--v: 34"><b class="bl-dl">34</b></i><i data-c="3" style="--v: 14"><b class="bl-dl">14</b></i><i data-c="4" style="--v: 12"><b class="bl-dl">12</b></i></div><div class="bl-stack-val">−8%<small>전년 대비</small></div></div>
  <div class="bl-stack-r"><div class="bl-stack-n">품질팀<small>검토</small></div><div class="bl-stack-b"><i data-c="1" style="--v: 8"><b class="bl-dl">8</b></i><i data-c="5" style="--v: 14"><b class="bl-dl">14</b></i><i data-c="2" style="--v: 20"><b class="bl-dl">20</b></i><i data-c="3" style="--v: 46"><b class="bl-dl">46</b></i><i data-c="4" style="--v: 12" class="is-est"><b class="bl-dl">12</b></i></div><div class="bl-stack-val is-neg">+4%<small>전년 대비</small></div></div>
  <div class="bl-stack-r"><div class="bl-stack-n">영업지원팀<small>견적</small></div><div class="bl-stack-b"><i data-c="1" style="--v: 12"><b class="bl-dl">12</b></i><i data-c="5" style="--v: 18"><b class="bl-dl">18</b></i><i data-c="2" style="--v: 42"><b class="bl-dl">42</b></i><i data-c="3" style="--v: 16" class="is-est"><b class="bl-dl">16</b></i><i data-c="4" style="--v: 12" class="is-est"><b class="bl-dl">12</b></i></div><div class="bl-stack-val">−3%<small>전년 대비</small></div></div>
  <div class="bl-stack-r"><div class="bl-stack-n">운영지원팀<small>기록</small></div><div class="bl-stack-b"><i data-c="1" style="--v: 6"><b class="bl-dl">6</b></i><i data-c="5" style="--v: 10"><b class="bl-dl">10</b></i><i data-c="2" style="--v: 14"><b class="bl-dl">14</b></i><i data-c="3" style="--v: 10"><b class="bl-dl">10</b></i><i data-c="4" style="--v: 60"><b class="bl-dl">60</b></i></div><div class="bl-stack-val">−11%<small>전년 대비</small></div></div>
</div>
```

---

<a id="bl-stair"></a>
## 계단형 상승 열 · `.bl-stair`

| 항목 | 내용 |
|---|---|
| 쓰는 곳 | 단계가 오를수록 커지는 값 — 성숙도 · 누적 효과 |
| 구조(클래스) | `.bl-stair` → `.bl-badge` → `.bl-bubble` |
| 속성 | `data-c` |
| 토큰 | `--bl-ease-out` `--bl-fs-h3` `--bl-fs-sm` `--bl-fs-xs` `--br-alert-text` `--br-amber` `--br-card` `--br-font-kr` `--br-navy` `--br-on-dark` |
| 할 것 | 마지막 단계만 주인공 색 · 단계 이름은 짧게 |
| 하지 말 것 | 내려가는 값에 쓰기(→ 워터폴) |
| 원본 | `catalog#stair` — 대조 덱 `examples/components` 장 `c-bl-stair` |

복사용 HTML(내용만 바꾼다 — 클래스 · 속성 이름은 그대로):

```html
<div class="bl-stair" style="--n: 4">
  <div style="--lv: 1" data-c="mute"><span class="bl-badge" data-c="mute">2022</span><h3>전화</h3><p>평일 낮 · 한 창구</p></div>
  <div style="--lv: 2" data-c="5"><span class="bl-badge" data-c="5">2023</span><h3>메일</h3><p>회신 2일 · 기록 남음</p></div>
  <div style="--lv: 3" data-c="1"><span class="bl-badge">2025</span><h3>채팅</h3><p>즉답 · 야간 자동 응답</p></div>
  <div style="--lv: 4" class="is-top"><span class="bl-bubble">이번 목표</span><h3>통합 접수</h3><p>한 화면 · 한 번호 · 한 기록</p></div>
</div>
```

---

<a id="bl-hero"></a>
## 히어로 띠 · `.bl-hero`

| 항목 | 내용 |
|---|---|
| 쓰는 곳 | 장 하나를 대표하는 숫자 한 개를 가로 띠로 |
| 구조(클래스) | `.bl-hero` → `.bl-hero-w` → `.bl-hero-arrows` → `.bl-itile` → `.bl-itile--lg` → `.bl-i` → `.bl-i--layout-grid` |
| 속성 | — |
| 토큰 | `--bl-i` `--br-amber` `--br-card` `--br-cover` `--br-font-kr` `--br-navy` `--br-on-dark` `--br-on-dark-2` `--br-track` `--br-warn-text` |
| 할 것 | 숫자 하나 + 기준 한 줄 |
| 하지 말 것 | 한 장에 히어로 띠 둘 |
| 원본 | `catalog#hero` — 대조 덱 `examples/components` 장 `c-bl-hero` |

복사용 HTML(내용만 바꾼다 — 클래스 · 속성 이름은 그대로):

```html
<div class="bl-hero">
  <span class="bl-hero-w">통합 접수</span>
  <span class="bl-hero-arrows" aria-hidden="true"><span style="--i: 0">›</span><span style="--i: 1">›</span><span style="--i: 2">›</span><span style="--i: 3">›</span></span>
  <span class="bl-itile bl-itile--lg"><i class="bl-i bl-i--layout-grid" aria-hidden="true"></i></span>
  <p><b>창구 셋 · 대장 넷</b>을 한 화면 · 한 번호 · 한 기록으로 · 시범 6주 뒤 판정</p>
</div>
```

---

<a id="bl-chev"></a>
## 쉐브론 띠 · `.bl-chev`

| 항목 | 내용 |
|---|---|
| 쓰는 곳 | 3~5단계 순서 — 절차 · 추진 단계 |
| 구조(클래스) | `.bl-chev` |
| 속성 | `data-c` |
| 토큰 | `--bl-fs-body` `--br-card` `--br-font-kr` |
| 할 것 | 단계 이름은 명사 짧게 · 지금 단계만 강조 |
| 하지 말 것 | 6단계 이상(→ 간트나 파이프라인) |
| 원본 | `catalog#chev` — 대조 덱 `examples/components` 장 `c-bl-chev` |

복사용 HTML(내용만 바꾼다 — 클래스 · 속성 이름은 그대로):

```html
<div class="bl-chev">
  <div data-c="navy">1 개인<small>서식 · 검색</small></div>
  <div data-c="4">2 팀<small>분류 · 배정</small></div>
  <div data-c="warn">3 부서<small>공용 대장</small></div>
  <div data-c="1">4 전사<small>통합 접수</small></div>
</div>
```

---

<a id="bl-gantt"></a>
## 간트 · `.bl-gantt`

| 항목 | 내용 |
|---|---|
| 쓰는 곳 | 과제별 기간 · 상태 — 일정 · 로드맵 |
| 구조(클래스) | `.bl-gantt` → `.bl-gantt-h` → `.bl-gantt-g` → `.bl-gantt-r` → `.bl-gantt-k` → `.bl-gantt-bar` → `.bl-gantt-today` → `.bl-badge` |
| 속성 | `data-f` `data-s` |
| 토큰 | `--bl-ease-out` `--bl-font-mono` `--bl-fs-sm` `--bl-fs-xs` `--bl-gantt-k` `--bl-gantt-n` `--br-alert-text` `--br-amber` `--br-card` `--br-cat-1` `--br-font-kr` `--br-hairline` `--br-mark` `--br-mark-mute` `--br-navy` `--br-ok-text` `--br-on-dark` `--br-text-2` `--br-text-3` `--br-tint` `--br-track` `--br-warn-text` |
| 할 것 | 오늘 선 하나 · 상태는 완료 · 진행 · 계획(빗금) 세 가지로 |
| 하지 말 것 | 과제 10행 이상(→ 부록 표) · 색을 과제마다 다르게 |
| 원본 | `catalog#gantt` — 대조 덱 `examples/components` 장 `c-bl-gantt` |

복사용 HTML(내용만 바꾼다 — 클래스 · 속성 이름은 그대로):

```html
<div class="bl-gantt" style="--bl-gantt-n: 12">
  <div class="bl-gantt-h"><span>실행 과제 · 담당</span><b style="grid-column: span 4">10월</b><b style="grid-column: span 4">11월</b><b style="grid-column: span 4">12월</b></div>
  <div class="bl-gantt-g"><span>A. 기반 정리</span></div>
  <div class="bl-gantt-r"><span class="bl-gantt-k">통합 접수 화면 설계<small>IT팀</small></span><i class="bl-gantt-bar" data-s="done" style="grid-column: 2 / 4">설계 완료</i><i class="bl-gantt-bar" data-s="now" style="grid-column: 4 / 6">검토</i></div>
  <div class="bl-gantt-r"><span class="bl-gantt-k">분류 기준 개정<small>품질팀</small></span><i class="bl-gantt-bar" data-s="now" style="grid-column: 3 / 8">개정안 회람</i></div>
  <div class="bl-gantt-g"><span>B. 시범 운영</span></div>
  <div class="bl-gantt-r is-focus"><span class="bl-gantt-k">채팅 응대 시범<small>고객지원팀</small></span><i class="bl-gantt-bar" data-s="now" style="grid-column: 4 / 10">시범 6주</i></div>
  <div class="bl-gantt-r"><span class="bl-gantt-k">사례집 이관<small>운영지원팀</small></span><i class="bl-gantt-bar" data-s="plan" style="grid-column: 6 / 11">이관 계획</i></div>
  <div class="bl-gantt-g" data-f="1"><span>C. 확대 판정</span></div>
  <div class="bl-gantt-r" data-f="1"><span class="bl-gantt-k">처리 시간 자동 집계<small>IT팀</small></span><i class="bl-gantt-bar" data-s="plan" style="grid-column: 8 / 13">구축</i></div>
  <div class="bl-gantt-r" data-f="1"><span class="bl-gantt-k">확대 여부 판정<small>운영위원회</small></span><i class="bl-gantt-bar" data-s="hold" style="grid-column: 11 / 14">판정</i></div>
  <div class="bl-gantt-r" data-f="1"><span class="bl-gantt-k">응대 교육<small>전 팀</small></span><i class="bl-gantt-bar" data-s="mute" style="grid-column: 9 / 14">월 1회</i></div>
  <i class="bl-gantt-today" style="--at: .08"><b class="bl-badge">10.06</b></i>
</div>
```

---

<a id="bl-lanes"></a>
## 이중 레인 연표 · `.bl-lanes`

| 항목 | 내용 |
|---|---|
| 쓰는 곳 | 두 흐름의 사건을 같은 시간축에 — 우리 · 시장, 계획 · 실적 |
| 구조(클래스) | `.bl-lanes` → `.bl-lanes-r` → `.bl-lanes-k` → `.bl-lanes-ev` → `.bl-lanes-axis` → `.bl-lanes-r--down` |
| 속성 | `data-c` `data-f` |
| 토큰 | `--bl-font-mono` `--bl-fs-sm` `--bl-lanes-k` `--bl-lanes-n` `--bl-line` `--bl-shadow` `--br-card` `--br-font-kr` `--br-navy` `--br-on-dark` `--br-text-2` `--br-text-3` |
| 할 것 | 레인 둘 · 같은 시간 눈금 |
| 하지 말 것 | 레인 셋 이상 |
| 원본 | `catalog#lanes` — 대조 덱 `examples/components` 장 `c-bl-lanes` |

복사용 HTML(내용만 바꾼다 — 클래스 · 속성 이름은 그대로):

```html
<div class="bl-lanes" style="--bl-lanes-n: 6">
  <div class="bl-lanes-r">
    <span class="bl-lanes-k">외부 창구<small>고객이 문의를 넣는 곳</small></span>
    <div class="bl-lanes-ev" data-c="1" style="grid-column: 2"><b>전화 단일</b>평일 9~18시</div>
    <div class="bl-lanes-ev" data-c="1" style="grid-column: 3"><b>메일 추가</b>회신 2일 기준</div>
    <div class="bl-lanes-ev" data-c="5" style="grid-column: 5"><b>채팅 시범</b>고객 200명</div>
    <div class="bl-lanes-ev" data-c="2" style="grid-column: 6"><b>채팅 정식</b>야간 자동 응답</div>
    <div class="bl-lanes-ev is-plan" data-c="1" style="grid-column: 7"><b>통합 접수</b>한 화면 · 한 번호</div>
  </div>
  <div class="bl-lanes-axis"><b>2022</b><b>2023</b><b>2024</b><b>2025</b><b>2026</b><b>2027</b></div>
  <div class="bl-lanes-r bl-lanes-r--down" data-f="1">
    <span class="bl-lanes-k">내부 처리<small>안에서 다루는 방식</small></span>
    <div class="bl-lanes-ev" data-c="mute" style="grid-column: 2"><b>팀별 엑셀</b>대장 4종</div>
    <div class="bl-lanes-ev" data-c="4" style="grid-column: 4"><b>공용 대장</b>한 대장 전환</div>
    <div class="bl-lanes-ev" data-c="4" style="grid-column: 5"><b>분류 기준</b>유형 7종 확정</div>
    <div class="bl-lanes-ev" data-c="3" style="grid-column: 6"><b>사례집 개설</b>128건 축적</div>
    <div class="bl-lanes-ev is-plan" data-c="4" style="grid-column: 7"><b>자동 집계</b>처리 시간 실측</div>
  </div>
</div>
```

---

<a id="bl-org"></a>
## 조직도 · `.bl-org`

| 항목 | 내용 |
|---|---|
| 쓰는 곳 | 보고 라인 · 위임 관계 |
| 구조(클래스) | `.bl-org` → `.bl-org-box` → `.bl-org-box--top` → `.bl-org-link` → `.bl-lbl` → `.bl-org-box--mid` → `.bl-org-tf` → `.bl-pill` → `.bl-pill--solid` → `.bl-push` → `.bl-org-units` → `.bl-org-unit` → `.bl-org-need` |
| 속성 | `data-c` `data-f` |
| 토큰 | `--bl-fs-body` `--bl-fs-h3` `--bl-fs-lbl` `--bl-fs-sm` `--bl-line` `--br-amber` `--br-card` `--br-cover` `--br-font-kr` `--br-navy` `--br-on-dark` `--br-on-dark-2` `--br-page` `--br-text-2` `--br-text-3` |
| 할 것 | 단계는 3단 이내 · 이번 보고에서 바뀐 칸만 강조 |
| 하지 말 것 | 전사 조직 전부 그리기 |
| 원본 | `catalog#org` — 대조 덱 `examples/components` 장 `c-bl-org` |

복사용 HTML(내용만 바꾼다 — 클래스 · 속성 이름은 그대로):

```html
<div class="bl-org">
  <div class="bl-org-box bl-org-box--top"><h3>운영위원회</h3><p>분기 판정 · 예산 승인</p></div>
  <div class="bl-org-link"><span class="bl-lbl">권한 위임</span></div>
  <div class="bl-org-box bl-org-box--mid"><h3>응대 개선 책임자</h3><p>우선순위 결정 · 팀 간 이견 조정</p></div>
  <div class="bl-org-link"><span class="bl-lbl">과제 · 권한 위임</span></div>
  <div class="bl-org-tf" data-f="1">
    <header><h3>응대 개선 TF</h3><span class="bl-pill bl-pill--solid" data-c="warn">필수 — 팀별 담당 1인</span><span class="bl-push"></span><span class="bl-lbl">역할 · 필요 권한</span></header>
    <div class="bl-org-units" style="--n: 5">
      <div class="bl-org-unit" data-c="1"><h4>고객지원팀</h4><p>창구 운영 · 답변 서식</p><p class="bl-org-need">필요 — 서식 승인</p></div>
      <div class="bl-org-unit" data-c="5"><h4>품질팀</h4><p>분류 기준 · 검토 규칙</p><p class="bl-org-need">필요 — 반려 기준 공개</p></div>
      <div class="bl-org-unit" data-c="3"><h4>IT팀</h4><p>접수 화면 · 자동 집계</p><p class="bl-org-need">필요 — 계정 권한</p></div>
      <div class="bl-org-unit" data-c="4"><h4>운영지원팀</h4><p>사례집 · 기록 보관</p><p class="bl-org-need">필요 — 보관 기간 결정</p></div>
      <div class="bl-org-unit" data-c="2"><h4>영업지원팀</h4><p>견적 문의 서식</p><p class="bl-org-need">필요 — 가격표 공개 범위</p></div>
    </div>
  </div>
</div>
```

---

<a id="bl-orgtree"></a>
## 작은 조직 · `.bl-orgtree`

| 항목 | 내용 |
|---|---|
| 쓰는 곳 | TF · 팀 하나의 구성 |
| 구조(클래스) | `.bl-orgtree` → `.bl-orgtree-lead` → `.bl-avatar` → `.bl-i` → `.bl-i--user` → `.bl-pill` → `.bl-pill--solid` → `.bl-orgtree-team` → `.bl-avatar--line` → `.bl-lbl` |
| 속성 | `data-c` |
| 토큰 | `--bl-fs-lbl` `--bl-i` `--bl-line` `--bl-shadow-up` `--br-amber` `--br-card` `--br-cover` `--br-font-kr` `--br-mark` `--br-navy` `--br-on-dark` `--br-on-dark-2` `--br-page` `--br-text-3` `--br-tint` `--br-track` `--br-warn-text` |
| 할 것 | 책임자 · 역할 이름까지 |
| 하지 말 것 | 인원 수만 나열 |
| 원본 | `catalog#team` — 대조 덱 `examples/components` 장 `c-bl-orgtree` |

복사용 HTML(내용만 바꾼다 — 클래스 · 속성 이름은 그대로):

```html
<div class="bl-orgtree">
  <div class="bl-orgtree-lead"><span class="bl-avatar"><i class="bl-i bl-i--user" aria-hidden="true"></i></span><div><b>파트장</b><br><span class="bl-pill bl-pill--solid" data-c="2">응대 개선 전담</span></div></div>
  <div class="bl-orgtree-team">
    <div><span class="bl-avatar bl-avatar--line"><i class="bl-i bl-i--user" aria-hidden="true"></i></span><b>담당 1</b><span class="bl-lbl">창구</span></div>
    <div><span class="bl-avatar bl-avatar--line"><i class="bl-i bl-i--user" aria-hidden="true"></i></span><b>담당 2</b><span class="bl-lbl">분류</span></div>
    <div><span class="bl-avatar bl-avatar--line"><i class="bl-i bl-i--user" aria-hidden="true"></i></span><b>담당 3</b><span class="bl-lbl">기록</span></div>
    <div><span class="bl-avatar bl-avatar--line"><i class="bl-i bl-i--user" aria-hidden="true"></i></span><b>담당 4</b><span class="bl-lbl">교육</span></div>
  </div>
</div>
```

---

<a id="bl-matrix"></a>
## 역할 매트릭스 · `.bl-matrix`

| 항목 | 내용 |
|---|---|
| 쓰는 곳 | 과제 × 조직의 주도 · 참여 관계 |
| 구조(클래스) | `.bl-matrix` → `.bl-mid` → `.bl-matrix-x` → `.bl-matrix-h` → `.bl-num` → `.bl-matrix-role` → `.bl-itile` → `.bl-itile--round` → `.bl-i` → `.bl-i--headset` → `.bl-matrix-c` → `.bl-pill` → `.bl-pill--solid` → `.bl-i--badge-check` … |
| 속성 | `data-c` |
| 토큰 | `--bl-font-mono` `--bl-fs-lbl` `--bl-fs-sm` `--bl-i` `--br-amber` `--br-card` `--br-cover` `--br-font-kr` `--br-hairline` `--br-navy` `--br-ok-text` `--br-text-2` `--br-tint` `--br-track` `--br-warn-text` |
| 할 것 | 주도 칸만 짙게 · 행 · 열 각 6개 이내 |
| 하지 말 것 | 모든 칸에 글자 |
| 원본 | `catalog#matrix` — 대조 덱 `examples/components` 장 `c-bl-matrix` |

복사용 HTML(내용만 바꾼다 — 클래스 · 속성 이름은 그대로):

```html
<div class="bl-matrix bl-mid" style="--n: 4">
    <div class="bl-matrix-x"></div>
    <div class="bl-matrix-h" data-c="1"><span class="bl-num">01</span>설계</div>
    <div class="bl-matrix-h" data-c="5"><span class="bl-num">02</span>시범</div>
    <div class="bl-matrix-h" data-c="2"><span class="bl-num">03</span>판정</div>
    <div class="bl-matrix-h" data-c="4"><span class="bl-num">04</span>확대</div>
    <div class="bl-matrix-role"><span class="bl-itile bl-itile--round"><i class="bl-i bl-i--headset" aria-hidden="true"></i></span>고객지원팀</div>
    <div class="bl-matrix-c">창구 요구 정리</div>
    <div class="bl-matrix-c is-lead" data-c="5"><span class="bl-pill bl-pill--solid" data-c="5">주도</span>시범 운영</div>
    <div class="bl-matrix-c">운영 기록 제출</div>
    <div class="bl-matrix-c">전 창구 적용</div>
    <div class="bl-matrix-role"><span class="bl-itile bl-itile--round"><i class="bl-i bl-i--badge-check" aria-hidden="true"></i></span>품질팀</div>
    <div class="bl-matrix-c">분류 기준 검토</div>
    <div class="bl-matrix-c">검토 규칙 적용</div>
    <div class="bl-matrix-c is-lead" data-c="2"><span class="bl-pill bl-pill--solid" data-c="2">주도</span>판정 기준 운영</div>
    <div class="bl-matrix-c">반려 기준 공개</div>
    <div class="bl-matrix-role"><span class="bl-itile bl-itile--round"><i class="bl-i bl-i--server" aria-hidden="true"></i></span>IT팀</div>
    <div class="bl-matrix-c is-lead" data-c="1"><span class="bl-pill bl-pill--solid" data-c="1">주도</span>화면 설계</div>
    <div class="bl-matrix-c">계정 · 권한</div>
    <div class="bl-matrix-c">자동 집계</div>
    <div class="bl-matrix-c">확대 구축</div>
    <div class="bl-matrix-role"><span class="bl-itile bl-itile--round"><i class="bl-i bl-i--clipboard-list" aria-hidden="true"></i></span>운영지원팀</div>
    <div class="bl-matrix-c">기록 서식</div>
    <div class="bl-matrix-c">사례집 이관</div>
    <div class="bl-matrix-c">판정 자료 정리</div>
    <div class="bl-matrix-c is-lead" data-c="4"><span class="bl-pill bl-pill--solid" data-c="4">주도</span>교육 · 확산</div>
    <div class="bl-matrix-role">결과물</div>
    <div class="bl-matrix-c is-out">◆ 화면 설계서</div>
    <div class="bl-matrix-c is-out">◆ 시범 운영 기록</div>
    <div class="bl-matrix-c is-out">◆ 판정 보고</div>
    <div class="bl-matrix-c is-out">◆ 확대 계획</div>
</div>
```

---

<a id="bl-vs"></a>
## 좌우 대비 · `.bl-vs`

| 항목 | 내용 |
|---|---|
| 쓰는 곳 | 지양 · 지향, 지금 · 바뀐 뒤 두 패널 |
| 구조(클래스) | `.bl-vs` → `.bl-fill` → `.bl-grow` → `.bl-vs-p` → `.bl-itile` → `.bl-i` → `.bl-i--triangle-alert` → `.bl-lc` → `.bl-lc--card` → `.bl-lc--dash` → `.bl-vs-mid` → `.bl-i--workflow` |
| 속성 | `data-c` |
| 토큰 | `--bl-fs-h3` `--bl-i` `--bl-line` `--bl-shadow` `--br-card` `--br-cover` `--br-font-kr` `--br-navy` `--br-track` `--br-warn-text` |
| 할 것 | 두 패널 항목 순서를 맞춤 · 오른쪽(지향)이 주인공 |
| 하지 말 것 | 항목 수가 다른 두 패널 |
| 원본 | `catalog#vs` — 대조 덱 `examples/components` 장 `c-bl-vs` |

복사용 HTML(내용만 바꾼다 — 클래스 · 속성 이름은 그대로):

```html
<div class="bl-vs bl-fill bl-grow">
  <section class="bl-vs-p" data-c="alert">
    <header><span class="bl-itile" data-c="alert"><i class="bl-i bl-i--triangle-alert" aria-hidden="true"></i></span><h3>지금 — 한 사람에게 몰림</h3></header>
    <div class="bl-lc bl-lc--card" data-c="mute"><h4>세 팀 요청</h4><p>전화 · 메일 · 메신저로 제각각</p></div>
    <div class="bl-lc bl-lc--card" data-c="alert"><h4>담당 1인 대기열</h4><p>평균 대기 1.8일 · 부재 시 정지</p></div>
    <div class="bl-lc bl-lc--dash" data-c="alert"><h4>결과 지연 · 기록 없음</h4><p>같은 질문 다시 접수</p></div>
  </section>
  <div class="bl-vs-mid" aria-hidden="true"></div>
  <section class="bl-vs-p" data-c="1">
    <header><span class="bl-itile" data-c="1"><i class="bl-i bl-i--workflow" aria-hidden="true"></i></span><h3>바꾼 뒤 — 기준으로 나눔</h3></header>
    <div class="bl-lc bl-lc--card" data-c="1"><h4>기준 공개</h4><p>유형 7종 · 담당 팀 자동 배정</p></div>
    <div class="bl-lc bl-lc--card" data-c="5"><h4>팀별 처리</h4><p>부재와 무관하게 진행</p></div>
    <div class="bl-lc bl-lc--card" data-c="4"><h4>사례집 축적 · 재사용</h4><p>다음 응대자가 바로 검색</p></div>
  </section>
</div>
```

---

<a id="bl-decide"></a>
## 결정 요청 판 · `.bl-decide`

| 항목 | 내용 |
|---|---|
| 쓰는 곳 | 승인 · 선택을 요청하는 장 |
| 구조(클래스) | `.bl-decide` → `.bl-decide-msg` → `.bl-lbl` → `.bl-decide-cards` → `.bl-decide-card` → `.bl-itile` → `.bl-itile--round` → `.bl-i` → `.bl-i--user-check` → `.bl-num` → `.bl-num--sm` → `.bl-num--solid` → `.bl-stamp` → `.bl-i--users` |
| 속성 | — |
| 토큰 | `--bl-ease` `--bl-font-mono` `--bl-fs-h3` `--bl-fs-lbl` `--bl-fs-sm` `--bl-fs-xs` `--bl-i` `--bl-line` `--bl-rot` `--bl-shadow` `--br-alert-text` `--br-amber` `--br-card` `--br-cover` `--br-font-kr` `--br-hairline` `--br-navy` `--br-ok-text` `--br-on-dark-2` `--br-page` `--br-text-2` `--br-text-3` `--br-tint` `--br-track` `--br-warn-text` |
| 할 것 | 요청마다 무엇을 · 언제까지 · 안 하면 · 도장(결정 표시)은 하나 |
| 하지 말 것 | 요청 4건 이상(→ 장을 나눔) |
| 원본 | `catalog#decide` — 대조 덱 `examples/components` 장 `c-bl-decide` |

복사용 HTML(내용만 바꾼다 — 클래스 · 속성 이름은 그대로):

```html
<div class="bl-decide">
  <div class="bl-decide-msg"><span class="bl-lbl">요청 사항</span><p><strong>통합 접수 착수</strong></p><p>10월 결정 시 <mark>12월 시범 시작</mark> · 지연 시 1월로 밀림</p></div>
  <div class="bl-decide-cards" style="--n: 2">
    <div class="bl-decide-card"><span class="bl-itile bl-itile--round"><i class="bl-i bl-i--user-check" aria-hidden="true"></i></span><h3><span class="bl-num bl-num--sm bl-num--solid">1</span> 책임자 지정</h3><p>팀 간 우선순위 · 충돌 시 최종 결정</p><span class="bl-stamp" style="--i: 1">결정</span></div>
    <div class="bl-decide-card"><span class="bl-itile bl-itile--round"><i class="bl-i bl-i--users" aria-hidden="true"></i></span><h3><span class="bl-num bl-num--sm bl-num--solid">2</span> 팀별 담당 1인</h3><p>주 2시간 · 12주 · 업무 조정 포함</p><span class="bl-stamp" style="--i: 2">결정</span></div>
  </div>
</div>
```

---

<a id="bl-pipe"></a>
## 파이프라인 열 · `.bl-pipe`

| 항목 | 내용 |
|---|---|
| 쓰는 곳 | 단계마다 무엇이 들고 나는지 — 처리 흐름 |
| 구조(클래스) | `.bl-pipe` → `.bl-fill` → `.bl-grow` → `.bl-pipe-s` → `.bl-num` → `.bl-pipe-b` → `.bl-tmap` → `.bl-dl` → `.bl-cap` → `.bl-pipe-f` → `.bl-checks` → `.bl-orbit` → `.bl-prog` → `.bl-mock-row` … |
| 속성 | `data-c` |
| 토큰 | `--bl-ease-out` `--bl-font-mono` `--bl-fs-body` `--bl-fs-cap` `--bl-fs-lbl` `--bl-fs-sm` `--bl-fs-xs` `--bl-line` `--bl-sp-1` `--br-alert-bg` `--br-alert-text` `--br-amber` `--br-card` `--br-cover` `--br-font-kr` `--br-font-num` `--br-hairline` `--br-mark` `--br-navy` `--br-ok-bg` `--br-ok-text` `--br-on-dark-2` `--br-text-2` `--br-text-3` `--br-tint` `--br-track` |
| 할 것 | 단계마다 작은 그림 하나 · 되먹임은 호 하나 |
| 하지 말 것 | 단계 7개 이상 |
| 원본 | `catalog#pipe` — 대조 덱 `examples/components` 장 `c-bl-pipe` |

복사용 HTML(내용만 바꾼다 — 클래스 · 속성 이름은 그대로):

```html
<div class="bl-pipe bl-fill bl-grow" style="--n: 5">
  <section class="bl-pipe-s" data-c="1"><header><span class="bl-num">01</span>수집</header>
    <div class="bl-pipe-b"><div class="bl-tmap"><i data-c="1" class="is-big"><b class="bl-dl">전화</b></i><i data-c="5"><b class="bl-dl">메일</b></i><i data-c="2"><b class="bl-dl">채팅</b></i><i data-c="mute"><b class="bl-dl">방문</b></i><i data-c="5"><b class="bl-dl">기타</b></i></div><span class="bl-cap">창구별 비중 — 면적</span></div>
    <p class="bl-pipe-f">주 360건</p></section>
  <section class="bl-pipe-s" data-c="5"><header><span class="bl-num">02</span>분류</header>
    <div class="bl-pipe-b"><ul class="bl-checks"><li><b>유형</b></li><li><b>긴급도</b></li><li class="is-no"><b>개인정보</b></li></ul></div>
    <p class="bl-pipe-f">유형 7 · 긴급 3</p></section>
  <section class="bl-pipe-s" data-c="navy"><header><span class="bl-num">03</span>처리</header>
    <div class="bl-pipe-b"><div class="bl-orbit" data-c="1"><b>기준</b><i></i></div><div class="bl-prog" data-c="1" style="--v: .7"></div><span class="bl-cap">기준 일치 70%</span></div>
    <p class="bl-pipe-f">평균 4.1시간</p></section>
  <section class="bl-pipe-s" data-c="2"><header><span class="bl-num">04</span>회신</header>
    <div class="bl-pipe-b"><div class="bl-mock-row"><span class="bl-badge" data-c="2">메일</span><span class="bl-sk" style="--w: 90"></span><span class="bl-mini">완료</span></div><div class="bl-mock-row"><span class="bl-badge" data-c="5">채팅</span><span class="bl-sk" style="--w: 70"></span><span class="bl-mini">완료</span></div><div class="bl-mock-row"><span class="bl-badge" data-c="1">전화</span><span class="bl-sk" style="--w: 60"></span><span class="bl-mini">대기</span></div></div>
    <p class="bl-pipe-f">회신 시각 기록</p></section>
  <section class="bl-pipe-s" data-c="4"><header><span class="bl-num">05</span>축적</header>
    <div class="bl-pipe-b"><ul class="bl-ul"><li>사례 128건</li><li>검색 주 40회</li></ul><span class="bl-pill bl-pill--tint" data-c="4">주 2회 갱신</span></div>
    <p class="bl-pipe-f">응대 사례집</p></section>
</div>
```

---

<a id="bl-tc"></a>
## 상단 색띠 카드 · `.bl-tc`

| 항목 | 내용 |
|---|---|
| 쓰는 곳 | 병렬 항목 3~5개를 카드로 — 과제 · 사례 |
| 구조(클래스) | `.bl-tc` → `.bl-tc-h` → `.bl-num` → `.bl-num--solid` → `.bl-lbl` → `.bl-itile` → `.bl-i` → `.bl-i--inbox` → `.bl-ul` → `.bl-tc-out` |
| 속성 | `data-c` `data-f` |
| 토큰 | `--bl-font-mono` `--bl-fs-body` `--bl-fs-h3` `--bl-fs-lbl` `--bl-i` `--bl-line` `--bl-shadow` `--bl-sp-1` `--bl-sp-2` `--bl-sp-3` `--br-amber` `--br-card` `--br-cover` `--br-dark-line` `--br-font-kr` `--br-navy` `--br-ok-text` `--br-on-dark-2` `--br-page` `--br-text-2` `--br-text-3` `--br-tint` `--br-track` `--br-warn-text` |
| 할 것 | 색띠는 계열 구분(data-c)에만 · 카드 높이 같게 |
| 하지 말 것 | 상태를 색띠로 표시(→ 상태 알약) |
| 원본 | `catalog#tcard` — 대조 덱 `examples/components` 장 `c-bl-tc` |

복사용 HTML(내용만 바꾼다 — 클래스 · 속성 이름은 그대로):

```html
<article class="bl-tc" data-c="1" data-f="1">
  <header class="bl-tc-h"><span class="bl-num bl-num--solid">1</span><div><span class="bl-lbl">입구</span><h3>접수</h3></div><span class="bl-itile"><i class="bl-i bl-i--inbox" aria-hidden="true"></i></span></header>
  <ul class="bl-ul"><li>전화 · 메일 · 채팅 세 창구</li><li>접수 번호 자동 부여</li><li>같은 고객 문의 묶음</li></ul>
  <p class="bl-tc-out">접수 대장 한 줄</p>
</article>
```

---

<a id="bl-hc"></a>
## 색 머리 열 카드 · `.bl-hc`

| 항목 | 내용 |
|---|---|
| 쓰는 곳 | 열마다 묶음이 다른 목록 — 영역별 준비 상태 |
| 구조(클래스) | `.bl-hc` → `.bl-itile` → `.bl-itile--round` → `.bl-i` → `.bl-i--headset` → `.bl-hc-b` → `.bl-row` → `.bl-lbl` → `.bl-meter` → `.bl-ul` → `.bl-cap` → `.bl-pgref` |
| 속성 | `data-c` `data-n` `data-peek` `data-v` |
| 토큰 | `--bl-font-mono` `--bl-fs-body` `--bl-fs-cap` `--bl-fs-h3` `--bl-fs-lbl` `--bl-i` `--bl-line` `--bl-shadow` `--bl-sp-1` `--bl-sp-2` `--br-accent-on-dark` `--br-amber` `--br-card` `--br-cover` `--br-font-kr` `--br-mark` `--br-navy` `--br-on-dark-2` `--br-page` `--br-text-3` `--br-track` `--br-warn-text` |
| 할 것 | 열 머리에 묶음 이름 · 개수 |
| 하지 말 것 | 열마다 다른 형식 |
| 원본 | `catalog#hcard` — 대조 덱 `examples/components` 장 `c-bl-hc` |

복사용 HTML(내용만 바꾼다 — 클래스 · 속성 이름은 그대로):

```html
<article class="bl-hc" data-c="1">
  <header data-n="01"><span class="bl-itile bl-itile--round"><i class="bl-i bl-i--headset" aria-hidden="true"></i></span><h3>창구</h3></header>
  <div class="bl-hc-b"><div class="bl-row"><span class="bl-lbl">준비도</span><span class="bl-meter" data-v="3"><i></i><i></i><i></i></span></div><span class="bl-lbl">확보</span><ul class="bl-ul"><li>전화 · 메일 운영</li><li>채팅 시범 계정</li></ul><p class="bl-cap">근거 <button type="button" class="bl-pgref" data-peek="raci">부록 2</button></p></div>
  <div class="bl-hc-b"><span class="bl-lbl">보완</span><ul class="bl-ul"><li>야간 자동 응답</li><li>통합 번호</li></ul></div>
</article>
```

---

<a id="bl-tabset"></a>
## 탭 · `.bl-tabset`

| 항목 | 내용 |
|---|---|
| 쓰는 곳 | 같은 형식의 사례 여러 개를 한 장에서 전환 |
| 구조(클래스) | `.bl-tabset` → `.bl-fill` → `.bl-mk` → `.bl-tabs` → `.bl-num` → `.bl-pane` → `.bl-mid` → `.bl-stack-v` → `.bl-kpis` → `.bl-kpis--cards` → `.bl-kpi` → `.bl-lbl` → `.bl-kpi-v` → `.bl-kpi-d` … |
| 속성 | `data-at` `data-c` `data-f` `data-v` |
| 토큰 | `--bl-font-mono` `--bl-fs-body` `--bl-fs-h3` `--bl-fs-kpi` `--bl-fs-kpi-l` `--bl-fs-lbl` `--bl-fs-sm` `--bl-line` `--bl-shadow` `--bl-sp-2` `--bl-sp-3` `--br-amber` `--br-card` `--br-cover` `--br-dark-line` `--br-font-kr` `--br-font-num` `--br-hairline` `--br-mark` `--br-navy` `--br-ok-text` `--br-on-dark` `--br-on-dark-2` `--br-page` `--br-text` `--br-text-2` `--br-text-3` `--br-tint` `--br-track` `--br-warn-text` |
| 할 것 | 탭 3~6개 · 발표 단계(data-at)와 묶기 |
| 하지 말 것 | 탭마다 형식이 다름 · 탭 안에 탭 |
| 원본 | `catalog#tabs` — 대조 덱 `examples/components` 장 `c-bl-tabset` |

복사용 HTML(내용만 바꾼다 — 클래스 · 속성 이름은 그대로):

```html
<div class="bl-tabset bl-fill">
  <i class="bl-mk" data-f="1"></i>
  <div class="bl-tabs"><button type="button" data-v="a"><span class="bl-num">1</span>주간 수치</button><button type="button" data-v="b" data-at="1"><span class="bl-num">2</span>남은 일정</button></div>
  <div class="bl-pane" data-v="a">
    <div class="bl-mid bl-stack-v">
    <div class="bl-kpis bl-kpis--cards" style="--n: 4">
      <div class="bl-kpi"><span class="bl-lbl">채팅 문의</span><span class="bl-kpi-v" data-count>64<small>건</small></span><p class="bl-kpi-d">주간 · 시범 3주차</p></div>
      <div class="bl-kpi" data-c="ok"><span class="bl-lbl">첫 회신</span><span class="bl-kpi-v" data-count>12<small>분</small></span><p class="bl-kpi-d">전화 대비 짧음</p></div>
      <div class="bl-kpi" data-c="warn"><span class="bl-lbl">이관</span><span class="bl-kpi-v" data-count>9<small>건</small></span><p class="bl-kpi-d">전화로 넘긴 건</p></div>
      <div class="bl-kpi bl-kpi--fill"><span class="bl-lbl">만족</span><span class="bl-kpi-v" data-count>4.3<small>/5</small></span><p class="bl-kpi-d">응답 38명</p></div>
    </div>
    <div class="bl-nband"><span class="bl-lbl">읽는 법</span><span>첫 회신은 짧고 이관은 아직 많음 · <mark>이관 사유 정리가 다음</mark></span></div>
    </div>
  </div>
  <div class="bl-pane" data-v="b">
    <div class="bl-mid bl-stack-v">
    <ol class="bl-dots" data-c="1"><li class="is-done"><b>10.06</b><span>시범 시작</span></li><li class="is-done"><b>10.20</b><span>중간 점검</span></li><li class="is-now"><b>10.27</b><span>이관 사유 정리</span></li><li class="is-plan"><b>11.10</b><span>시범 종료</span></li><li class="is-goal"><b>11.17</b><span>판정</span></li></ol>
    <div class="bl-cols bl-cols--3"><div class="bl-lc bl-lc--line" data-c="ok"><h4>완료 2</h4><p>시작 · 중간 점검</p></div><div class="bl-lc bl-lc--line" data-c="1"><h4>진행 1</h4><p>이관 사유 정리</p></div><div class="bl-lc bl-lc--line" data-c="mute"><h4>남음 2</h4><p>종료 · 판정</p></div></div>
    </div>
  </div>
</div>
```

---

<a id="bl-concl"></a>
## 결론 줄 · 장 결론 띠 · `.bl-concl`

| 항목 | 내용 |
|---|---|
| 쓰는 곳 | 장(章)의 처음이나 끝, 결정 · 전환 장 — 장(章)마다 한 번 |
| 구조(클래스) | `.bl-concl` |
| 속성 | — |
| 토큰 | `--bl-fs-body` `--bl-sp-2` `--br-alert-text` `--br-amber` `--br-font-kr` `--br-on-dark` `--br-text` |
| 할 것 | 장 결론은 조립 목록 takeaway 로(짙은 띠 .bl-concl--ch 로 붙음) · 굵은 강조어 하나 |
| 하지 말 것 | 본문 장마다 붙이기(검사 29번 주의) · 문장 두 줄 이상 |
| 원본 | `examples/standard#steps` — 대조 덱 `examples/components` 장 `c-bl-concl` |

복사용 HTML(내용만 바꾼다 — 클래스 · 속성 이름은 그대로):

```html
<p class="bl-concl"><b>네 단계 중 셋이 규칙으로 정해진 일</b> · 사람 판단이 필요한 곳은 검토 회신 반영 한 곳뿐</p>
```

---

<a id="bl-ev"></a>
## 출처 칩 · `.bl-ev`

| 항목 | 내용 |
|---|---|
| 쓰는 곳 | 수치 바로 옆 — 근거 패널로 연결 |
| 구조(클래스) | `.bl-ev` |
| 속성 | `data-claim` `data-ev` |
| 토큰 | `--bl-fs-floor` `--br-accent-on-dark` `--br-card` `--br-font-kr` `--br-mark` `--br-mark-mid` `--br-mark-mid-dark` |
| 할 것 | data-ev 키를 evidence.json 에 · data-claim 에 그 수치 문장 |
| 하지 말 것 | 근거 없는 키 · 문단 끝에 몰아 달기 |
| 원본 | `examples/standard#gist` — 대조 덱 `examples/components` 장 `c-bl-ev` |

복사용 HTML(내용만 바꾼다 — 클래스 · 속성 이름은 그대로):

```html
<button type="button" class="bl-ev" data-ev="E2" data-claim="시범 2건 처리 시간 62% 단축">출처</button>
```

---

<a id="bl-spark"></a>
## 작은 막대 · `.bl-spark`

| 항목 | 내용 |
|---|---|
| 쓰는 곳 | 수치 카드 · 관전 카드 안에서 추세 3~6점 — 큰 수치 밑 근거 그림 |
| 구조(클래스) | `.bl-spark` → `.bl-spark-c` |
| 속성 | — |
| 토큰 | `--bl-fs-lbl` `--bl-r-xs` `--br-alert-text` `--br-card` `--br-font-kr` `--br-font-num` `--br-text` `--br-text-2` |
| 할 것 | 지금 값 하나만 .is-on(꽉 찬 막대) · 지난 값은 속 빈 막대 그대로 · 음수는 .is-neg + 묶음 --bot · 아직 모르는 값은 .is-unk(물음표 칸) |
| 하지 말 것 | 회색 면으로 지난 값 칠하기 · 7점 이상(→ 비교 막대 · 간트) · 장의 주인공으로 쓰기(→ 비교 막대) |
| 원본 | `examples/hct-analysis#watch` — 대조 덱 `examples/components` 장 `c-bl-spark` |

복사용 HTML(내용만 바꾼다 — 클래스 · 속성 이름은 그대로):

```html
<div class="bl-spark" aria-label="2026 분기 매출 억원 · 4분기 미확인">
  <div class="bl-spark-c" style="--v: .82"><b>247</b><i></i><span>1Q</span></div>
  <div class="bl-spark-c" style="--v: .85"><b>256</b><i></i><span>2Q</span></div>
  <div class="bl-spark-c is-on" style="--v: .92"><b>276</b><i></i><span>3Q</span></div>
  <div class="bl-spark-c is-unk"><b>?</b><i></i><span>4Q</span></div>
</div>
```

---

<a id="bl-icards"></a>
## 아이콘 카드 · `.bl-icards`

| 항목 | 내용 |
|---|---|
| 쓰는 곳 | 대상 3~5개를 한 줄로 — 사업 분야 · 요인 · 관전 지표 |
| 구조(클래스) | `.bl-icards` → `.bl-mid` → `.bl-icard` → `.bl-icard-i` → `.bl-i` → `.bl-i--radio-tower` → `.bl-icard-k` → `.bl-i--zap` → `.bl-i--circuit-board` → `.bl-i--shield-check` → `.bl-i--microscope` |
| 속성 | `data-c` |
| 토큰 | `--bl-fs-body` `--bl-fs-h3` `--bl-fs-lbl` `--bl-fs-sm` `--bl-i` `--bl-r-s` `--bl-sp-3` `--bl-sp-4` `--br-accent-on-dark` `--br-card` `--br-deep` `--br-font-kr` `--br-font-num` `--br-mark` `--br-navy` `--br-on-dark` `--br-on-dark-2` `--br-text` `--br-text-2` `--br-track` `--br-warn-text` |
| 할 것 | 카드 안은 가운데 정렬 · 대상마다 data-c 고정(덱 전체에서 같은 번호) · 강조 하나만 .is-on · 번호 · 이름 띠가 필요하면 .bl-icards--head |
| 하지 말 것 | 카드마다 왼쪽 정렬 긴 문장 · 같은 대상에 장마다 다른 색 · 6개 이상 |
| 원본 | `examples/hct-analysis#fields` — 대조 덱 `examples/components` 장 `c-bl-icards` |

복사용 HTML(내용만 바꾼다 — 클래스 · 속성 이름은 그대로):

```html
<div class="bl-icards bl-mid" style="--n: 5">
  <div class="bl-icard is-on" data-c="1"><span class="bl-icard-i"><i class="bl-i bl-i--radio-tower"></i></span><h3>정보통신</h3><p class="bl-icard-k">EMC · RF · SAR · OTA</p><hr><p>통신기기 시험 · 매출 회복의 축</p></div>
  <div class="bl-icard" data-c="2"><span class="bl-icard-i"><i class="bl-i bl-i--zap"></i></span><h3>배터리 · ESS</h3><p class="bl-icard-k">안전성 시험</p><hr><p>2026 배터리 안전성 인증 의무화 수혜</p></div>
  <div class="bl-icard" data-c="3"><span class="bl-icard-i"><i class="bl-i bl-i--circuit-board"></i></span><h3>자동차 전장</h3><p class="bl-icard-k">고전압 EMC</p><hr><p>국내 완성차 3사 · 스텔란티스 공인 시험소</p></div>
  <div class="bl-icard" data-c="6"><span class="bl-icard-i"><i class="bl-i bl-i--shield-check"></i></span><h3>방산 · 우주</h3><p class="bl-icard-k">신뢰성 · 방사선 시험</p><hr><p>F-35 정비 장비 교정 · CMMC 레벨 1</p></div>
  <div class="bl-icard" data-c="4"><span class="bl-icard-i"><i class="bl-i bl-i--microscope"></i></span><h3>의료기기 · 보안</h3><p class="bl-icard-k">성능 · 사이버보안</p><hr><p>IoT · 의료기기 보안 KOLAS 인정</p></div>
</div>
```

---

<a id="bl-cmpbars"></a>
## 비교 막대 · `.bl-cmpbars`

| 항목 | 내용 |
|---|---|
| 쓰는 곳 | 같은 구간의 지난 값과 지금 값 — 분기 전년 비교 · 연도 추이 |
| 구조(클래스) | `.bl-cmpbars` → `.bl-cmpbars-g` → `.bl-cmpbars-bs` → `.bl-cmpbars-b` |
| 속성 | — |
| 토큰 | `--bl-fs-body` `--bl-fs-lbl` `--bl-r-xs` `--bl-sp-4` `--br-alert-text` `--br-card` `--br-font-kr` `--br-font-num` `--br-mark` `--br-text` `--br-text-2` |
| 할 것 | 지난 값은 속 빈 막대 · 지금 값은 .is-now 꽉 찬 막대 · 묶음 아래 한 줄(영업이익 등) · 범례 .bl-cmpbars-lg |
| 하지 말 것 | 회색 막대로 비교 대상 표시 — 발표 화면에서 흰색과 구분 안 됨 · 묶음 6개 이상 |
| 원본 | `examples/hct-analysis#quarters` — 대조 덱 `examples/components` 장 `c-bl-cmpbars` |

복사용 HTML(내용만 바꾼다 — 클래스 · 속성 이름은 그대로):

```html
<div class="bl-cmpbars" style="--n: 3">
  <div class="bl-cmpbars-g"><div class="bl-cmpbars-bs"><div class="bl-cmpbars-b" style="--v: .86"><b>257</b><i></i></div><div class="bl-cmpbars-b is-now" style="--v: .82"><b>247</b><i></i></div></div><h3>1분기</h3><p>영업 14억 → <b>4억</b></p></div>
  <div class="bl-cmpbars-g"><div class="bl-cmpbars-bs"><div class="bl-cmpbars-b" style="--v: .97"><b>292</b><i></i></div><div class="bl-cmpbars-b is-now" style="--v: .85"><b>256</b><i></i></div></div><h3>2분기</h3><p>영업 50억 → <b class="is-neg">−4억</b></p></div>
  <div class="bl-cmpbars-g"><div class="bl-cmpbars-bs"><div class="bl-cmpbars-b" style="--v: .94"><b>281</b><i></i></div><div class="bl-cmpbars-b is-now" style="--v: .92"><b>276</b><i></i></div></div><h3>3분기</h3><p>영업 45억 → <b>25억</b></p></div>
</div>
```

---

<a id="bl-tline"></a>
## 직선 연표 · `.bl-tline`

| 항목 | 내용 |
|---|---|
| 쓰는 곳 | 사건 5~8개를 시간 순으로 — 투자 · 인증 · 계약 이력 |
| 구조(클래스) | `.bl-tline` → `.bl-mid` → `.bl-tline-s` |
| 속성 | `data-c` |
| 토큰 | `--bl-fs-body` `--bl-fs-lbl` `--br-card` `--br-deep` `--br-font-kr` `--br-font-num` `--br-mark` `--br-navy` `--br-text-2` |
| 할 것 | 사건은 위아래 번갈아 · 큰 사건만 .is-big 채운 점 · 점 색은 대상 data-c · 범례 .bl-tline-lg |
| 하지 말 것 | 사선 · 곡선 연결 · 사건 9개 이상(→ 이중 레인 연표 · 간트) |
| 원본 | `examples/hct-analysis#invest` — 대조 덱 `examples/components` 장 `c-bl-tline` |

복사용 HTML(내용만 바꾼다 — 클래스 · 속성 이름은 그대로):

```html
<div class="bl-tline bl-mid" style="--n: 7">
  <div class="bl-tline-s" data-c="1"><i></i><div><b>2025-01</b><h3>일본 인증기관 자격</h3><p>J-MIC · JATE 국내 최초</p></div></div>
  <div class="bl-tline-s" data-c="4"><i></i><div><b>2025-10</b><h3>사이버보안 KOLAS</h3><p>IoT · 의료기기 보안</p></div></div>
  <div class="bl-tline-s"><i></i><div><b>2025-11</b><h3>100% 무상증자</h3><p>주주가치 제고</p></div></div>
  <div class="bl-tline-s is-big" data-c="5"><i></i><div><b>2026 초</b><h3>미국 법인 증설</h3><p>시험 챔버 · 시설</p></div></div>
  <div class="bl-tline-s is-big" data-c="3"><i></i><div><b>2026-05</b><h3>M솔루션센터 준공</h3><p>차량 전장 EMC</p></div></div>
  <div class="bl-tline-s"><i></i><div><b>2026-07</b><h3>대진반도체 MOU</h3><p>반도체 교정 협력</p></div></div>
  <div class="bl-tline-s is-big" data-c="4"><i></i><div><b>2026-08</b><h3>휴믹 흡수합병</h3><p>CRO 통합</p></div></div>
</div>
```
