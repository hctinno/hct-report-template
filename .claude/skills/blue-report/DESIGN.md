# 본문 스타일 한 장 — 발표 덱을 만드는 에이전트가 반드시 읽는 문서

**이 문서 하나면 덱을 만들 수 있다.** 나머지 문서는 찾아보는 색인이다 — 부품 속성은 `README.md` 「6-3」,
색 역할 상세는 `references/design-language.md`, 효과 목록은 `MOTION.md`.

---

## 0. 일하는 방식 — 본문만 쓰고 빌드가 틀을 씌운다

```
보고서/
  deck.yaml        조립 목록 — 표지 정보 · 장(章) 순서 · 장마다 넣을 장 id · 마무리 · 부록
  slides.html      본문 파일 — <section id> 마다 본문만
  evidence.json    출처 근거(선택)
```

```bash
python3 scripts/build_deck.py 보고서/deck.yaml --brand <brand.json> --single-file -o decks-out/보고서.html
python3 scripts/check_live.py decks-out/보고서.html --shots decks-out/shots   # 실패 0 까지 고친다
```

- 견본: `examples/standard/`(기준 덱 내용을 이 형식으로 옮긴 것) · `examples/showcase/`(카탈로그 · 패턴첩 장을 id 로 불러 조립).
- **쓰지 않는 것 — 빌드가 만든다:** 머리띠 · 꼬리띠 · 쪽번호 · 회사 로고 · 워터마크 · 폰트 · 진행선 ·
  조작판 · 발표 기능, 그리고 표지 · 목차 · 장 간지 · 마무리 · 부록 간지. 본문에 섞어 쓰면 빌드가 떼고 주의를 낸다.
- **쓰는 것:** 장마다 제목 · 리드 · 본문 도식 · 발표자 노트. 이 문서의 스타일로.

## 1. 본문 파일 — 장 하나 = `<section>` 하나

```html
<section id="hours" data-name="시간 분포"
         data-toc="월 168시간의 분포" data-sub="단계별 시간 · 가장 무거운 단계"
         data-notes="수치 넉 점을 먼저 읽고, 막대에서 가장 무거운 단계를 짚는다.">
  <h2 class="bl-title">월 <em>168시간</em>이 네 단계에 묶임</h2>
  <p class="bl-lede">3개 팀 · 9명 · 8주 기록 기준 <strong>정리 단계가 절반 이상</strong></p>
  <div class="bl-kpis bl-mid">…</div>
</section>
```

| 속성 | 뜻 |
|---|---|
| `id` | 필수 · 조립 목록이 부르는 이름 |
| `data-name` | 머리띠 왼쪽 짧은 이름(없으면 장 이름) |
| `data-notes` | 발표자 노트 — `~한다` 형 · `[클릭]` · `**굵게**` · `→ 전환:` · `※ 메모` |
| `data-toc` · `data-sub` | 장 간지 「이 장에서」 목록 문구(없으면 제목) |
| `data-bd` | 본문 칸 배치 클래스(예: `bl-gist`) |
| `class` | 장 변형 — `bl-sl--dark`(어두운 지면) · `bl-sl--dense` |

- 맞춤 CSS 는 장 안 `<style data-own>` — 선택자는 `#장id` 나 `x-` 접두어로 묶는다.
- 출처 칩 `<button type="button" class="bl-ev" data-ev="E1">출처</button>` → `evidence.json` 의 `E1`.
- 단계 전개는 요소에 `data-f="1"` 부터, 노트의 `[클릭]` 수와 맞춘다.

## 2. 조립 목록 — `deck.yaml`

```yaml
title: 업무 자동화 확산 계획
body: slides.html
evidence: evidence.json
cover: {date: 2026-09, org: 운영지원팀, title: 업무 자동화 <em>확산 계획</em>, tag: (안),
        message: 되풀이되는 일은 도구에 <b>판단은 사람에게</b>, presenter: {team: 운영지원팀, name: 홍길동, role: 팀장}}
front: [gist]                          # 목차 다음 · 첫 간지 앞(보고 요지)
chapters:
  - {name: 현황, title: 반복 업무의 실태, lede: 어느 일이 얼마나 되풀이되는가, slides: [steps, hours, catalog:gantt]}
  - {name: 실행, title: 넉 달 동안 무엇을 하는가, lede: 바뀌는 단계 · 일정, slides: [compare, roadmap]}
closing: {lead: 사람이 판단하는 자리는 지키고, line: 되풀이되는 자리만, mark: 도구로, sign: 9월 조사 · 10월 착수}
appendix: [qa, terms]
```

- 장 자리에는 본문 id 말고 **라이브러리 장**도 부른다 — `catalog:<id>`(부품 카탈로그) · `patterns:<id>`(패턴첩).
  가져온 장은 그대로가 아니라 **견본**이다. 맞는 부품이면 본문 파일로 복사해 내용을 바꾼다.
- 장(章)이 둘 이상이면 목차가, 장마다 간지가 자동으로 붙는다. 순서를 바꾸면 목차 · 간지 · 쪽번호가 따라온다.

## 3. 톤과 한 장의 위계

- **기업 보고.** 차분하고 단정하게. 장식보다 정보, 놀람보다 이해.
- **한 장 한 주장.** 제목이 주장이다 — 「주장 — `<em>`핵심구`</em>`」. 제목만 넘겨 읽어도 보고가 된다.
- 문체는 개조식(명사형 종결). 지면에 `~합니다` · `~한다` · `~없다` 를 쓰지 않는다(노트만 `~한다`).

```
제목(주장)        ← 한 줄. 핵심구를 <em> 형광 밴드로
리드(기준 · 결론)  ← 한 줄. 수치의 기준일 · 범위 · 굵은 결론
주인공 하나        ← 도식 · 차트 · 수치 · 화면 중 하나. 장의 60% 이상
곁들임            ← 해설 2~4줄 · 출처 칩. 주인공보다 작게
```

- 주인공은 **하나**다. 도식 둘을 나란히 두면 둘 다 약해진다 — 장을 나눈다.
- 16:9 한 화면에 들어가야 한다. 넘치면 줄이지 말고 장을 나눈다. 본문 덩어리는 `.bl-mid` 로 세로 가운데.
- 큰 수치는 장마다 하나가 주인공 — 숫자는 크게, 단위는 작게 옆에.

## 4. 무엇을 그릴까 — 내용이 모양을 정한다

먼저 내용의 모양을 정한다(흐름 · 일정 · 비교 · 구성 · 수치 · 구조 · 화면 · 사례). 그다음 아래 표에서 표현을
고르고 용례 장을 연다 — 따라 그리려는 것이 아니라 위계와 밀도를 보려는 것이다.

| 내용 | 그린다 | 용례(패턴첩 `patterns:`) | 부품(카탈로그 `catalog:`) |
|---|---|---|---|
| 흐름 · 경로 · 유입 | 허브 · 시스템 지도 · 깔때기 · 노선 | `pt-hub` · `pt-system-map` · `pt-api-first` · `pt-journey` | `flow` · `own` · `route` · `pipe` |
| 일정 · 단계 · 연혁 | 연표 · 간트 + 오늘 선 · 연도 단계 · 단계 카드 | `pt-timeline-cluster` · `pt-roadmap-gantt` · `pt-phase-years` · `pt-steps3` | `gantt` · `lanes` · `history` |
| 비교 · 선택 | 3구역 편집 · 전과 후 패널 · 좌우 대비 | `pt-three-zone` · `pt-before-after-panel` · `pt-same-diagnosis` | `vs` · `years` · `matrix` |
| 구성 · 비율 | 도넛 · 100% 누적 막대 | `pt-subscription` · `pt-stack-compare` | `kpi` · `stack` · `rack` |
| 수치 · 추세 | 큰 수치 타일 · 콤보 · 워터폴 · 계단 | `pt-combo-chart` · `pt-segment-waterfall` · `pt-gap-3panel` · `pt-four-cards` | `kpi` · `stair` · `hero` |
| 구조 · 조직 · 역할 | 쉐브론 3단 · 링 · 경계도 · 조직도 | `pt-chevron3` · `pt-ring-roles` · `pt-boundary` · `pt-team` | `org` · `team` · `matrix` |
| 화면 · 시연 | 목업 + 번호 주석 · 탭 + 화면 | `pt-governance-b` · `pt-device-data` · `pt-peer-tabs` | `explorer` · `portal` · `shot` · `tabs` |
| 여러 사례 | 탭 · 색띠 카드 열 · 칸반 | `pt-global-two-way` · `pt-four-cards` · `pt-kanban5` | `tcard` · `focusrow` · `hcard` |
| 결정 요청 | 요청 카드 + 결론 줄 · 결정 판 | `pt-chevron3` | `decide` |
| 상세 · 근거(부록) | 편집 표 · 질문 답 | `pt-proc-table` · `pt-type-matrix` · `pt-qa` | `raci` · `monthly` · `qa` |

- **표 · 목록은 마지막 선택이다.** 부록 · 상세 비교처럼 표가 맞는 장만 표로 둔다(검사 29번).
- 수치가 있으면 수치가 주인공이다. 문장 안에 묻지 않는다.
- 용례의 칸 수 · 문구를 그대로 두고 숫자만 갈지 않는다. 내용이 넷이면 넷, 둘이면 둘로 짠다.
- 맞는 것이 없으면 문법(이 문서의 색 · 위계)을 빌려 `<style data-own>` 으로 새로 짠다 — 견본은 `catalog:own`.

## 5. 색 — 이름이 아니라 역할로

| 역할 | 토큰 | 쓰는 자리 |
|---|---|---|
| 주 강조 | `--br-cobalt` · `--br-navy` (`--bl-pt-brand` · `--bl-pt-brand-2`) | 기본 강조 · 번호 머리 · 큰 수치 · 짙은 카드 |
| 당사 · 결과 | `--bl-pt-orange` · `--bl-pt-orange-d` | 당사 막대 · 결과 화살 · 결론 강조어 |
| 비교 대상 | `--bl-pt-gray` | 업계 · 경쟁 · 과거 — 주인공을 돋보이게 물린다 |
| 진행 · 지금 | `--bl-pt-blue` | 진행 중 단계 · 지금 위치 |
| 상태 | `--br-ok-*` · `--br-warn-*` · `--br-alert-*` | 상태를 말할 때만. 장식 금지 |
| 바탕 강조 | `--br-tint` (`--bl-pt-tint`) | 결론 띠 · 강조 칸 바탕 |
| 계열 구분 | `--br-cat-1~6` · 부품은 `data-c` | 순서 없는 항목(부서 · 제품) |

- 한 장에 강조색은 **하나가 주인공** — 대개 주황(당사 · 결과) 아니면 코발트.
- 비교는 「주인공 색 하나 + 회색」. 여러 색을 같은 무게로 늘어놓지 않는다.
- 데이터 마크는 배경 대비 2:1 이상. 밝은 지면에 `--br-soft-*` 를 쓰지 않는다.
- `--bl-pt-*` 를 쓰는 장이 있으면 빌드가 `blue-pattern.css` 를 함께 부른다.

## 6. 움직임 — 요청이 있을 때만

- 기본은 부품에 든 움직임만(막대 성장 · 도넛 · 흐름선 · 숫자 세기). 효과를 덧붙이지 않는다.
- 요청이 있으면 `MOTION.md` 에서 고른다. 원칙: 틀이 먼저 → 값이 그려지고 → 강조가 마지막.
  반복은 「지금 · 흐름」 한 곳만. 장마다 등장 3종 · 반복 2종을 넘지 않는다(검사 30번).

## 7. 토큰 — 새로 짤 때 이 값만

| 무엇 | 토큰 |
|---|---|
| 글꼴 | `--br-font-kr` · `--br-font-num`(수치) · `--bl-font-mono`(세는 숫자) |
| 글자 크기 | `--bl-fs-title` · `--bl-fs-lede` · `--bl-fs-h3` · `--bl-fs-body`(1.0rem 이상) · `--bl-fs-kpi` · `--bl-fs-kpi-l` · 라벨 `--bl-fs-lbl` |
| 간격 | `--bl-sp-1~5` · 판 너비 `--bl-max` |
| 모서리 · 그림자 | `--bl-r-xs · s · m · l · pill` · `--bl-shadow` · `--bl-shadow-up` |
| 움직임 | `--bl-ease` · `--bl-ease-out` · `--bl-ease-pop` · 길이 0.15~2.4초 |

## 8. 금지

- hex · `rgb()` · 색 이름 · `px`(테두리 1px 제외) · 다른 글꼴.
- 파이 차트. 도넛은 `python3 scripts/donut.py --live …` 로 만든다 — 각도를 손으로 쓰지 않는다.
- 글자 24px(본문 1.0rem) 미만 — `%` 첨자 · 라벨 계열만 예외.
- 계통 이름(`bl-` · `br-` · `pt-` · `xf`) 새로 짓기. 맞춤 클래스는 `x-` 접두어.
- 고정 영역 클래스(`bl-hd` · `bl-rf` · `br-mark` · `br-watermark` · `bl-pg`)를 본문이나 맞춤 선택자에 넣기.
- 예시 수치 · 부서명을 실제 내용으로 바꾸지 않고 남기기.

## 9. 끝내기 전에

1. `build_deck.py … --brand … --single-file` 로 빌드한다.
2. `check_live.py <결과> --shots <폴더>` — **실패 0.** 29번(글 · 표뿐인 장) · 30번(움직임 과다) 주의도 없앤다.
3. `<폴더>` 의 장별 PNG 를 넘겨 본다 — 주인공이 하나인가 · 빈자리가 아래에 모였나 · 제목만으로 읽히나 ·
   글자가 겹치거나 잘리지 않았나. 고칠 것이 있으면 본문 파일을 고치고 다시 빌드한다.
