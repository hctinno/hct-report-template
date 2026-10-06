# AX_BLUE_REPORT_V1 규격서

경영진 보고용 **인터랙티브 HTML 발표 덱** 디자인 시스템이다. 1920×1080 비율의 장 56종,
남색 머리띠 · 로고 · 워터마크 · 제목 형광 밴드, 클릭 단계 전개와 등장 애니메이션, 출처 핀과 근거 창,
발표 모드 · 레이저 · 대본 창을 한 엔진이 처리한다. 결과물은 **한 파일 HTML** 이라 메일 · 메신저로 그대로 보낸다.

- 견본 완성본: `dist/ax-blue-report-gallery.html`(대본 포함) · `dist/ax-blue-report-present.html`(대본 없이 처음부터 발표 모드)
- 견본 내용(「샘플테크」 · 홍길동 · 수치 · 기관명)은 **전부 가상**이다. 실제 회사 · 기관 · 인물과 관계없다.
- blue-report 스킬과는 별개 계통이다. 토큰 · 글자 하한 · 검사기가 다르다(아래 9절).

---

## 1. 설치와 부르기

```bash
# 플러그인(권장) — PC 마다 한 번
claude plugin marketplace add hctinno/hct-report-template
claude plugin install ax-blue-report@hct-tools
```

설치 뒤 **세션을 새로 열고** 이렇게 부른다.

```
AX_BLUE_REPORT_V1 으로 3분기 AX 추진계획 경영진 보고 덱 만들어줘.
AX 블루 리포트 V1 스타일로 이 자료를 15장짜리 발표 덱으로.
```

「AX_BLUE_REPORT_V1」 · 「AX 블루 리포트 V1」 · 「AX 블루 리포트」 · 「ax-blue-report」 가 스위치다.
그냥 「블루 리포트」 · 「AX 리포트 스타일」 은 blue-report 스킬이 받는다.

클론해서 쓸 때는 저장소 안 `.claude/skills/ax-blue-report/` 가 프로젝트 스킬로 바로 읽힌다.
Codex 등 다른 에이전트에게는 「`.claude/skills/ax-blue-report/SKILL.md` 를 읽고 그대로 수행해라」 한 줄을 준다.

필요한 도구

| 쓰임 | 도구 |
|---|---|
| 빌드(필수) | Python 3.9+ |
| 폰트 줄이기 · PDF 폰트 고정 | `pip install fonttools brotli` (없으면 폰트를 통째로 넣는다 · PDF 가 커진다) |
| 점검 · PNG · PDF | Node 18+ · `npm i -D playwright && npx playwright install chromium` |
| PDF 합치기 · 링크 | `pip install pypdf` · (선택) `qpdf` |
| PDF 뷰어 | poppler(`pdftoppm`) · `pip install pillow` |

---

## 2. 폴더

```
ax-blue-report/
  SKILL.md                 스킬 트리거와 작업 순서
  README.md                이 규격서
  CHANGELOG.md             판올림 기록(버전 = .claude-plugin/plugin.json)
  slides/NN-<id>.html      장 56종. 덱을 만들 때 복사해 글자만 바꾸는 대상
  core/                    엔진 — 고치지 않는다
    axbr.css               모든 장의 모양 · 움직임(한 파일)
    chrome.html            조작판 · 메모 띠 · 도움말 · 근거 창 · 겹창 · 영상 창
    js/NNN-*.js            엔진 · 발표 · 레이저 · 대본 창 · 장별 동작(이름 순서대로 실행)
    data/evidence.json     출처 핀이 여는 근거(가상 견본)
    data/bma-rfp-payload*.json   07장 「원문 전체보기」 문서(가상 견본)
    media/                 견본 화면 · 포스터 · 캡처 · 영상(전부 「예시 · 가상」 표기)
    fonts/                 Pretendard Variable(woff2) · OFL 라이선스
    order.txt              견본 덱 장 순서
  brand/hct/               로고 · 워터마크 5벌(webp)
  scripts/                 빌드 · 점검 · PDF · 뷰어 · 대본 · PNG
  dist/                    견본 덱 완성본 2종
```

`core/` 의 자산은 토큰으로 가리킨다 — `axbr-media:<파일>` · `axbr-brand:<이름>` · `axbr-font:pretendard`.
빌더가 data URI 로 풀어 한 파일에 넣는다. 그래서 장 파일과 CSS 에는 경로가 없다.

---

## 3. 장 해부도

```html
<section class="sl" id="market-cards" data-grp="g1"
         data-t="04 글로벌 시험인증(TIC) 트렌드"
         data-notes="첫 화면에서 할 말 …&#10;&#10;[클릭]&#10;&#10;클릭 뒤 할 말 …&#10;&#10;→ 전환: …">
  <div class="wrap">
    <header class="hd">
      <span class="code"><em class="chp">1. AX 추진 배경</em>글로벌 트렌드</span>   <!-- 장 이름 · 쪽 주제 -->
      <span class="sp"></span><span class="lg"></span>                           <!-- 여백 · 로고 -->
    </header>
    <h2>글로벌 시험인증(TIC) 트렌드 — <em>성장 · 재편 · AI 전환</em></h2>          <!-- em = 형광 밴드 -->
    <p class="lede">한 줄 요지 — <b>강조</b></p>
    <div class="bd"> … 본문 … <div class="fr" data-f="1"> 클릭 1단계 </div> … </div>
    <footer class="rf"><span>문서명</span><span class="pg"></span></footer>      <!-- 쪽번호는 엔진이 채운다 -->
  </div>
</section>
```

| 속성 · 요소 | 뜻 |
|---|---|
| `id` | 장의 모양이 매인 이름(`#deck #market-cards …`). **바꾸지 않는다** |
| `class` | `sl` 필수. 부록은 `apx`, 어두운 장은 `dark`, 장 표지는 `v41-chapter` |
| `data-grp` | 장(章) 묶음 `g1`…`g5` · 부록 `g6`. INDEX 링크 · PDF 책갈피가 쓴다 |
| `data-t` | 장 제목. 본문 `NN 제목` · 장 표지 `NN 장 제목` · 부록 `부록 NN · 제목` · 간지 `부록` · 표지 `표지` |
| `data-notes` | 발표 대본. `[클릭]` 수 = 단계 수 |
| `.fr[data-f="N"]` | 클릭 단계. 같은 N 은 함께 열린다. 검토(펼침) 모드에서는 모두 보인다 |
| `id="appendix"` | 부록 간지. 이 앞이 본문(쪽번호 01…), 뒤가 부록(부록 01…) |
| `data-pdf-detail="off"` | PDF 에서 이 장 뒤에 「NN-k」 상세 쪽을 끼우지 않는다(화면 덱에는 영향 없음) |
| 첫 장 | 표지 — 쪽번호 없음 |

### 대본 형식

```
첫 화면에서 말할 내용(존댓말 · 2~4문장)

[클릭]

클릭한 뒤 말할 내용

→ 전환: 다음 장으로 넘어가는 한 문장

※ 질문 대비 메모(선택 · 한 줄)
```

---

## 4. 디자인

| 토큰 | 값 | 쓰임 |
|---|---|---|
| `--paper` | `#f7f8f6` | 장 바탕 |
| `--frame` | `#e6e8ec` | 장 바깥 |
| `--ink` · `--ink3` | `#151b2e` · `#262d44` | 글자 |
| `--brand` · `--brand2` | `#2f4a9c` · `#1d2f6b` | 남색 강조 · 머리띠 |
| `--tint` | `#e8edf8` | 옅은 남색 면 |
| `--hi` · `--hi2` | `#bcd4fb` · `#8fb6f6` | 제목 형광 밴드 |
| `--ok` · `--no` · `--amber` | `#1f7a4d` · `#b3261e` · `#8f5500` | 좋음 · 나쁨 · 주의 |
| `--line` · `--line2` | `#c9cdd8` · `#e2e5ec` | 선 |

- **글꼴**: Pretendard Variable 한 벌(굵기 45~920). 빌더가 덱에 쓰인 글자 + KS X 1001 한글 2,350자 + 영문 · 기호만 남겨 넣는다(`--full-font` 로 통째).
- **크기**: `html{font-size:clamp(10.5px, min(1vw, 1.78vh), 20px)}` — 모든 치수가 rem 이라 창 크기에 맞춰 16:9 로 늘고 준다.
- **크롬**: 장마다 남색 머리띠(장 이름 · 쪽 주제 · 로고) · 바닥줄(문서명 · 쪽번호) · 우하단 워터마크. 어두운 장은 흰 로고 · 어두운 워터마크로 자동 전환.
- **형광 밴드**: `h1 em` · `h2 em` · `mark` 아래쪽 46% 에 연한 남색 띠.
- **문체**: 화면은 개조식(명사형 종결). 대본만 존댓말.

---

## 5. 움직임과 기능

| 기능 | 표시 · 마크업 | 동작 |
|---|---|---|
| 등장 애니메이션 | 장이 화면에 55% 들어오면 `.in` | 카드 · 막대 · 선이 차례로 들어온다(`--d` 지연). 움직임 줄이기 설정이면 바로 완성 |
| 클릭 단계 | `.fr[data-f]` | 발표 모드에서 `→` 마다 한 단계. 펼침 모드는 전부 |
| 세는 숫자 | `data-count="46" data-dec="0"` | 장이 들어오면 0 → 값 |
| 출처 핀 | `<button class="ev-pin" data-ev="E07" data-img="E07b" data-claim="…">출처</button>` | 근거 창 — 등급 · 사실 · 출처 · 캡처(확대 · 끌기 · 강조 상자) |
| 지금 원문 보기 | `<button class="now-ref" data-now-source="apx-gpu-stack">` | 대상 장을 겹창으로. 대상은 장 id(또는 `window.AXBR_LINKS` 별칭) |
| 영상 창 | `<button class="bma-video-open">` | `core/media/sample-video.mp4` 를 창으로 재생(`--no-video` 로 뺀다) |
| 원문 문서 창 | 07장 「원문 전체보기」 | `core/data/bma-rfp-payload*.json` 의 문서를 창으로 |
| 두 화면 전환 | `[role=tab][data-v]` | 28 · 29장. 한 장에서 화면 둘 |
| 비교 고르기 | 부록 16장 회사 버튼 | `script.k8-data` JSON 으로 막대를 다시 그림 |
| 노선도 | 부록 18장 역 버튼 | 역을 고르면 오른쪽 상세가 바뀜 |
| 발표 모드 | `F` · F11 | 전체 화면 · 조작판 숨김(화면 맨 아래로 마우스를 내리면 잠깐) · 레이저 · 대본 창 |
| 대본 창 | `P` | 새 창(막히면 화면 안 패널)에 현재 장 대본 · 경과 시간 · 고쳐 쓰기 · 내보내기 |
| 메모 · 가로 · 펼침 | `N` · `H` · `E` | 메모 띠 · 가로/세로 스냅 · 단계 펼침 |
| 쪽 이동 | 숫자 `Enter` · `A` 숫자 `Enter` | 본문 · 부록 쪽 |

---

## 6. 장 목록 — 56종

「단계」는 클릭 단계 수, 「핀」은 출처 핀 수다. 장 표지(03 · 09 · 12 · 18 · 31)와 Q&A(38~41)는 같은 모양이 여럿이다.

| 파일 | id | 모양 | 이런 내용에 쓴다 | 기능 |
|---|---|---|---|---|
| 00 | `cover` | 표지 — 눈썹 · 큰 제목 + (안) · 한 줄 메시지 · 우하단 발표자 | 모든 덱의 첫 장 | |
| 01 | `index` | INDEX — 번호 · 장 이름 · 부제 6줄 | 장 4~5개 + 부록 | |
| 02 | `exec-summary` | 보고 요지 — 결론 + 결정 요청 카드 + 3단 실행 흐름 | 앞 장만 보고 넘기는 경영진용 요약 | 단계 3 |
| 03 | `chapter-1` | 장 표지 — CHAPTER NN · 장 제목 · 진행 표시 | 장 시작(09 · 12 · 18 · 31 같은 모양) | |
| 04 | `market-cards` | 2열 트렌드 카드 — 수치 막대 · 이동 화살표 · 사례 목록 | 시장 · 산업 동향 두 갈래 | 단계 1 · 핀 9 |
| 05 | `event-timeline` | 연도 타임라인 + 사건 칩 + 시사점 3 | 연도별 사건 · 인수 · 규제 흐름 | 단계 2 · 핀 18 |
| 06 | `benchmark-table` | 벤치마킹 표 — 기관별 적용 영역 · 연표 · 시사점 열 | 동종 기관 비교 | 단계 4 · 핀 9 · 영상 |
| 07 | `stage-cards` | 연도 3단계 카드(큰 날짜) + 비교 띠 | 한 기관의 단계별 변화 | 단계 3 · 핀 5 · 영상 · 원문 문서 |
| 08 | `compare-1to1` | 1:1 비교 — 누적 막대 SVG · 지표 쌍 · 판단 | 우리 vs 비교 대상 | 단계 2 · 핀 3 · 원문 보기 |
| 10 | `definition-steps` | 정의 + 4단계 흐름 | 개념 정의와 단계 | 단계 1 |
| 11 | `status-columns` | 현황 5열 카드(큰 번호) | 영역별 현황 · 보유 자산 | 원문 보기 8 |
| 13 | `jcurve-stairs` | J커브 · 계단 그래프 + 설명 | 도입 초기 하락 뒤 상승 | 단계 4 · 핀 3 |
| 14 | `governance-org` | 추진 조직도 — 결정 → 책임자 → 조직별 TF | 거버넌스 · 보고 라인 | 단계 2 |
| 15 | `process-steps` | 4단계 절차 카드(아이콘 · 산출물) | 운영 절차 | 단계 2 |
| 16 | `milestone-grid` | 과제 × 연도 마일스톤 격자 + 판단 열 | 다년 병렬 과제 | 원문 보기 |
| 17 | `role-matrix` | 역할 × 단계 매트릭스 | 누가 언제 주도하나 | |
| 19 | `team-org` | 소조직 구성(장 + 구성원) + 성장 곡선 | 신생 조직 · 파트 구성 | |
| 20 | `role-bridge` | 3단계 역할 다리 — 기준 수립 → 검증 → 이관 | 역할 이동 · 이관 | 단계 3 |
| 21 | `principle-compare` | 원칙 대비 도식(지금 vs 원칙) | 운영 원칙 | 단계 1 |
| 22 | `coaching-demo` | 화면 목업 + 단계별 코칭 진행 | 사례 시연 · 화면 흐름 | 단계 6 · 버튼 5 |
| 23 | `type-table` | 유형 6종 표 + 단계 띠 | 과제 유형 · 가치 범위 | 단계 3 |
| 24 | `pilot-banner` | 큰 키워드 배너(→ AI) + 2열 설명 + 진행 막대 | 파일럿 과제 소개 | 단계 4 |
| 25 | `search-grid` | 결과 격자(전체 중 몇 칸) + 해석 | 노출 · 점유율 시각화 | 단계 3 |
| 26 | `product-shot` | 제품 화면 + 지표 3 + 설명 카드 | 도구 · 시스템 소개 | 견본 화면 |
| 27 | `flow-pipeline` | 5단계 파이프라인 — 트리맵 · AI 노드 움직임 | 수집 → 분석 → 전달 흐름 | |
| 28 | `two-view-intro` | 두 화면(탭) — 소개 ↔ 활용 분야 · 일정 | 한 장에 개요와 세부 | 단계 2 · 탭 |
| 29 | `two-view-status` | 두 화면(탭) — 구조도 ↔ 진행 간트 | 구조와 진행 현황 | 단계 3 · 탭 |
| 30 | `plan-gantt` | 월별 간트 + 오늘 선 | 실행 일정 | 단계 3 · 원문 보기 |
| 32 | `year-columns` | 연도 4열 방향 + 하단 띠 | 연도별 로드맵 | 단계 4 |
| 33 | `invest-columns` | 2열 투자 목록(올해 / 다음 해) | 투자 · 자원 요청 | 단계 2 |
| 34 | `seat-grid` | 좌석 격자 + 단계별 금액 카드 | 인원 · 계정 단계 지원 | 단계 3 · 핀 1 |
| 35 | `decision-request` | 결정 요청 카드 2 + 실행 순서 5단 | 마지막 결정 요청 | 단계 1 |
| 36 | `closing` | 맺음 문장 + 감사합니다 | 마무리 | |
| 37 | `appendix` | 부록 간지(어두운 장 · 큰 +) | 본문과 부록 경계 | |
| 38~41 | `qa-1`…`qa-4` | Q&A 3문항(질문 · 답 요지) | 예상 질문 | |
| 42 | `apx-plan-table` | 분기별 실행계획 표 | 상세 일정표 | |
| 43 | `apx-raci` | 역할 분담표(히트맵) | 부서 × 과제 역할 | |
| 44 | `apx-poster-survey` | 포스터 + 3단계 설명(시안 A · B · C 전환) | 설문 · 캠페인 | 단계 3 · 포스터 3 |
| 45 | `apx-poster-contest` | 포스터 + 진행 방식 카드 | 경진대회 · 행사 | 단계 3 · 포스터 2 |
| 46 | `apx-data-pipeline` | 파일 목록 화면 + 등급 표시 미리보기 | 보안 등급 · 자료 기준 | |
| 47 | `apx-onprem` | 구성도(외부 차단 · 사내 서버) + 단계 띠 | 시스템 구성 · 이전 계획 | 단계 2 |
| 48 | `apx-system-flow` | 시스템 4 → AI → 결과 4 흐름도 | 시스템 연계 경로 | 단계 2 |
| 49 | `apx-hub-scenes` | 포털 화면 장면 전환 | 플랫폼 화면 설명 | 버튼 10 |
| 50 | `apx-gpu-stack` | 자원 할당 누적 막대 + 판단 카드(계획 전환) | 자원 배분 · 증설 판단 | 버튼 2 |
| 51 | `apx-donut-bars` | 큰 숫자 3 + 가로 막대 + 도넛 | 구독 · 배분 현황 | |
| 52 | `apx-status-table` | 이력 표 + 핵심 수치 3 | 조달 · 계약 이력 | 핀 5 |
| 53 | `apx-stack-picker` | 100% 누적 막대 + 비교 대상 고르기 + 상대 · 절대값 전환 | 비용 구조 비교 | 핀 2 · 원문 보기 · 버튼 |
| 54 | `apx-segment-bars` | 큰 지표 4 + 워터폴 + 비교 막대 2 | 부문별 수익성 | 핀 1 |
| 55 | `apx-track-ring` | 두 트랙 노선도 + 역별 상세 | 업무 흐름별 적용 후보 | 단계 2 · 버튼 18 |

---

## 7. 만들기 · 내보내기

```bash
# 견본 장 고르기 → 작업 폴더(decks-out/ 는 gitignore)
python3 scripts/new_deck.py decks-out/q3/src --pick cover index exec-summary … --blank-notes

# 한 파일 HTML
python3 scripts/build_deck.py --list decks-out/q3/src/list.txt --title "3분기 AX 추진계획(안)" -o decks-out/q3/deck.html
python3 scripts/build_deck.py --gallery -o decks-out/gallery.html          # 견본 56장
```

| `build_deck.py` 옵션 | 뜻 |
|---|---|
| 입력 | 장 파일 여러 개 · `.sections.html`(장을 이어 적은 파일) · `--list 목록.txt` · `--gallery` |
| `--title` | 문서 제목 — 탭 · 바닥줄 문서명 · 대본 저장 키 |
| `--present` | 발표 전용 — 대본 · 메모 · 대본 창을 빼고 처음부터 발표 모드(레이저만) |
| `--artifact` | Claude Artifact 게시용 — `<!DOCTYPE>`·`<html>`·`<head>`·`<body>` 없이 · location 변경 코드 검사 |
| `--brand <폴더>` | 로고 · 워터마크 묶음(기본 `brand/hct`) |
| `--full-font` · `--no-video` | 폰트 통째 · 영상 데이터 빼기 |
| `--keep-numbers` · `--footer` · `--keep-footer` | `data-t` 번호 그대로 · 바닥줄 문서명 지정 · 그대로 |

```bash
# PDF — 본문 장 뒤에 그 장이 부르는 부록을 「NN-k」 상세 쪽으로 끼우고, 두 화면 장은 「NN②」 로 한 쪽 더
python3 scripts/make_pdf.py decks-out/q3/deck.html -o decks-out/q3/deck.pdf [--keep-order] [--no-appendix] [--no-detail 08,11]
# PDF 뷰어(쪽 그림 + 누르는 링크 + 책갈피 이동) — 메신저 미리보기 · Artifact 용
python3 scripts/make_pdf_viewer.py decks-out/q3/deck.pdf -o decks-out/q3/deck-pdf.html [--artifact] [--dpi 80]
# 대본
python3 scripts/export_script.py decks-out/q3/deck.html -o decks-out/q3/script.txt [--md]
```

상세 쪽을 끼우지 않을 장은 `--no-detail 08`(쪽 번호 또는 장 id) 또는 장에 `data-pdf-detail="off"` 로 정한다 —
그 장이 부르던 부록은 뒤쪽 부록 묶음(부록 NN)에 남고, `--no-appendix` 면 빠진다. 견본 08장은 `data-pdf-detail="off"` 다.
PDF 는 「부록 NN」 글자 · 지금 원문 보기 버튼 · INDEX 줄 · 상세 쪽의 「↩ NN」 이 쪽 링크가 되고,
책갈피는 표지 · INDEX · 요지 / 장 → 쪽 → 상세 / 부록으로 묶인다. 쪽 이름은 뷰어 쪽 번호 칸에 「07-1」 처럼 보인다.
가변 폰트는 Chromium PDF 에서 그림 글자(Type 3)가 되어 크고 검색이 안 되므로, 덱에 쓰인 굵기마다 고정 굵기 폰트를 만들어 찍는다.

---

## 8. 점검 — 완료 조건

```bash
python3 scripts/check_ax.py decks-out/q3/deck.html [--mobile] [--no-runtime]
node scripts/shots.js decks-out/q3/deck.html decks-out/q3/shots --sheet
```

| 검사 | 판정 |
|---|---|
| 글자 깨짐(저장소 검사와 같은 깨짐 글자 · U+FFFD) | 실패 |
| 풀리지 않은 자산 토큰 | 실패 |
| `data-t` 형식과 번호 | 실패 |
| 대본 `[클릭]` 수 = 단계 수 | 실패 |
| 지금 원문 보기 대상 장이 덱에 있음 | 실패 |
| 페이지 오류 · 콘솔 오류 | 실패 |
| 장마다 머리띠 · 로고 · 바닥줄 · 워터마크 | 실패(표지 · 간지는 주의) |
| 1920×1080 에서 글자가 바닥줄을 덮거나 장 밖으로 나감 | 실패 |
| 근거 핀 · 원문 보기 · 영상 · 발표 모드 · Esc 닫기 | 실패 |
| `--mobile` 420px 폭 가로 스크롤 | 실패 |
| 대본 없음 · 화면 글자 구어체 종결 · 없는 부록 번호 언급 · 같은 id 두 번 · 간지 뒤 본문 장 | 주의 |

**실패가 0 이 아니면 완료가 아니다.** 실패 0 이어도 `shots/sheet-*.png` 를 눈으로 본다 — 어색한 여백 · 줄바꿈은 검사기가 잡지 못한다.

---

## 9. blue-report 와 다른 점

| | blue-report | AX_BLUE_REPORT_V1 |
|---|---|---|
| 출발점 | 덱 12종 · 기준 덱 | 장 56종에서 골라 조립 |
| 토큰 | `--br-*` | `--paper` · `--brand` 등(4절) |
| 크기 | 1920×1080 고정 · 24px 하한 | rem 비율(16:9) · 견본 크기 유지 |
| 검사 | `check_deck.py` · `check_live.py` | `scripts/check_ax.py` |
| 출력 | HTML · PDF · PPTX · DOCX | HTML(일반 · 발표 · Artifact) · PDF · PDF 뷰어 · 대본 |

두 계통의 CSS · 부품을 한 덱에 섞지 않는다.

---

## 10. 브랜드 바꾸기

`brand/hct/` 와 같은 이름 5벌을 담은 폴더를 만들고 `--brand <폴더>` 로 빌드한다.

| 파일 | 자리 |
|---|---|
| `logo-white` | 보통 장의 남색 머리띠 오른쪽(흰 녹아웃) |
| `logo-color` | 어두운 장(표지 · 부록 간지)의 흰 머리띠 오른쪽(원색) |
| `watermark-light` · `watermark-dark` | 밝은 · 어두운 장 우하단 워터마크 |
| `symbol` | 28장 작은 심볼 |

webp · png · svg · jpg 를 받는다. 장 파일과 CSS 는 고치지 않는다.

---

## 11. 한계와 주의

- 장 모양이 `#deck #<id>` 선택자에 매여 있다. id 를 바꾸면 모양이 풀린다. 같은 장을 두 번 쓰면 JS 동작은 첫 장에만 붙는다.
- 07장 원문 문서 창 · 부록 16장 비교 데이터 · 22장 코칭 데모처럼 **장 전용 JS** 가 있는 장은 그 장의 id 와 함께 움직인다.
  그 장을 빼도 오류는 나지 않는다(대상이 없으면 아무것도 하지 않는다).
- 화면 글자의 길이는 견본과 비슷하게 맞춘다. 칸이 고정이라 길어지면 넘치고, 점검이 「글자 넘침」으로 잡는다.
- 견본의 근거(`evidence.json`) · 캡처 · 포스터 · 영상은 가상이다. 실제 덱에서는 실제 근거로 바꾸거나 핀을 지운다.
- Pretendard 는 SIL Open Font License 1.1 이다(`core/fonts/LICENSE-Pretendard.txt`).
