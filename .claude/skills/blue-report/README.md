# 블루 리포트 디자인 시스템

사내 공용 발표 슬라이드 · 보고서 디자인 시스템. 딥 코발트 계열 단일 팔레트, 1920×1080 HTML 슬라이드,
개조식 문체를 하나로 묶은 규격이다.

이 문서는 **자기완결 사양서**다. 다른 AI 도구(ChatGPT, Gemini, v0, Cursor 등)에 이 파일 전체를
붙여넣으면 별도 자료 없이 같은 결과를 만들 수 있다.

---

## 파일 구성

```
blue-report/
├─ SKILL.md                    Claude Code용 스킬 정의 ("블루 리포트" 트리거)
├─ README.md                   이 문서 — 다른 AI 도구에 붙여넣는 자기완결 사양서
├─ assets/
│  ├─ blue-report.css          토큰(색·타입·간격) + 파운데이션 + 애니메이션
│  ├─ blue-doc.css             A4 문서 파운데이션 (토큰은 blue-report.css 를 씀)
│  ├─ doc-viewer.css           문서 뷰어 껍데기
│  ├─ doc-viewer.js            쪽번호 자동 · 축척 · 인쇄
│  ├─ doc-minutes.html         회의록 2쪽
│  ├─ deck-viewer.css          뷰어 껍데기 (디자인 시스템 아님)
│  ├─ deck-viewer.js           넘김 · 축척 · 쪽번호 자동 · 발표자 노트
│  ├─ deck-template.html       레이아웃 12종 카탈로그
│  ├─ deck-internal-report.html   사내 보고 (월간) 9장
│  ├─ deck-weekly-report.html     조직 주간보고 7장
│  ├─ deck-ax-weekly.html         AX 조직 1장 보고 + 부록 5장
│  ├─ deck-sales-proposal.html    외부 제안·영업 10장
│  ├─ deck-project-report.html    프로젝트 착수·완료 9장
│  ├─ deck-training.html          교육·기술 설명 8장
│  └─ brand.example.json       회사명·연락처·로고 설정 견본
├─ references/
│  └─ rules.md                 차트 계산법 · 레이아웃 체크리스트 · 문체 규칙 전문
├─ pptx/                       PowerPoint 판 생성기
│  ├─ tokens.js                blue-report.css 의 토큰을 읽어 온다 (색 값 중복 없음)
│  ├─ layouts.js               카드 · 칩 · 머리말 · 꼬리말 등 원자 helper
│  ├─ slides.js                슬라이드 종류별 생성기 11종
│  ├─ content.js               용도별 덱 5종의 내용
│  └─ build.js                 실행 진입점
└─ scripts/
   ├─ donut.py                 도넛 SVG 생성 (각도 손계산 금지)
   ├─ palette.py               N단계 램프 생성 + 대비 검증
   ├─ check_deck.py            덱 자동 점검 11항목 + 슬라이드별 PNG
   ├─ check_doc.py             A4 문서 점검 8항목 + 쪽별 PNG
   ├─ ensure_deps.py           필요한 것을 스스로 갖춘다 (수동 설치 불필요)
   ├─ apply_brand.py           회사 정보·로고를 덱에 일괄 적용
   ├─ to_pdf.py                덱 HTML → 발표용 PDF (슬라이드 1장 = 1페이지)
   ├─ make_logo_variants.py    흰 배경 로고 → 투명 원색판 + 흰색 녹아웃
   └─ build_single_file.py     CSS 인라인 단일 파일 빌드
```

설치기 `install_blue_report_skill.py`는 이 저장소의 `scripts/`에 있다.

### 용도별 덱 고르기

`deck-template.html`은 레이아웃 12종을 모아 둔 **카탈로그**다. 실제 문서를 만들 때는
용도에 맞는 덱에서 시작한다. 각 덱은 슬라이드 순서와 내용 골격이 그 용도에 맞춰져 있다.

| 용도 | 파일 | 장수 | 구성 |
|---|---|---|---|
| 사내 보고 (월간) | `deck-internal-report.html` | 9 | 표지 · 목차 · **요약(다크)** · 지표 표 · 막대 · 비교 2열 · 최대 이슈 · 타임라인 · 결정 요청 |
| 조직 주간보고 | `deck-weekly-report.html` | 7 | 표지 · **요약(다크)** · 조직별 표 · 막대 · 지난주 대비 2열 · 요일 타임라인 · 지원 요청 |
| AX 조직 1장 보고 | `deck-ax-weekly.html` | 5 | **한 장 보고(문서형)** · 단계 표 · 자원 표 · 병목 · 요일 타임라인 |
| 외부 제안·영업 | `deck-sales-proposal.html` | 10 | 표지 · 목차 · 문제 · 도넛 · 3단계 · 효과 · 사례 표 · 일정 · 요약(다크) · CTA |
| 프로젝트 착수·완료 | `deck-project-report.html` | 9 | 표지 · 목차 · 범위 2열 · 타임라인 · 산출물 표 · 달성 막대 · 미달 · 판정(다크) · 승인 요청 |
| 교육·기술 설명 | `deck-training.html` | 8 | 표지 · 학습 목표 · 3단계 절차 · 방식 비교 · 도넛 · 체크리스트 표 · 요약(다크) · 다음 학습 |

용도가 요청에 드러나면 그대로 고르고, 드러나지 않을 때만 추천을 붙여 묻는 것이 기본 동작이다.
판단 기준은 `SKILL.md` 2절에 있다.

**AX 덱은 1장이 보고서 전부다** — 뒤 4장은 부록이며 질문이 나온 항목만 편다. 간지를 두지 않아 부록이 바로 이어진다.

한 장의 뼈대는 **업무 카테고리 × 이번 주·다음 주** 표다. 주간보고의 본체가 그 대조이기 때문이다.
그 위에 지표 4개를 한 줄 띠로 얹는데, 신생조직 보고를 받는 관리자의 질문에 1:1로 대응한다 —
①언제 성과가 나오나(첫 성과 시점) ②될 것 같나(파이프라인) ③사람·돈(인력·예산) ④내가 뭘(결정 요청).
**리스크는 따로 두지 않는다** — 해당 업무 행의 상태 칩이 말한다.
조판은 **문서형**이다. 카드·라운드를 쓰지 않고 왼쪽 라벨 열과 괘선으로만 구획한다.
다른 덱은 카드 조판을 쓰므로 이 덱만 다르다 — 한 장에 밀도를 높이면서도 대시보드처럼
보이지 않게 하려는 의도다. 색과 타입은 `--br-*` 토큰 그대로다.

**진척률만 적지 않는다.** 진척률은 팀이 스스로 매긴 노력의 양이라 받는 사람이 판단 기준으로
쓸 수 없다. 관문 날짜를 함께 적고, 결정 요청에는 미결 시 결과를 붙인다.
한 장 안에 판정 제목 · 지표 4 · 과제 진척 · 이슈 · 결정 요청이 모두 들어간다.
상위 관리자가 앞 장만 보고 판단을 끝내는 자리에 쓴다. 밀도가 높아 내용을 늘리면
겹침 검사(7번)가 실패하므로, 늘리는 대신 부록으로 내린다.

**주간보고에는 목차가 없다** — 매주 반복하는 보고라 목차가 시간만 쓴다. 타임라인도 주차가
아니라 요일(월~금) 단위다. 월간 보고와 헷갈리면 주기로 가른다. 매주면 `weekly`, 매달이면 `internal`.

**사내 보고는 요약을 앞에 둔다** — 경영진이 앞부분만 보고 넘어가는 경우가 많다.
**외부 제안은 요약을 뒤에 둔다** — 문제부터 설득한 뒤 정리하는 순서가 맞는다.

### 빠른 시작

```bash
# 용도별 덱 + 공용 자원 3개를 같은 폴더로 복사
cp assets/deck-internal-report.html ./deck.html
cp assets/blue-report.css assets/deck-viewer.css assets/deck-viewer.js ./
# 슬라이드 편집 후
python3 scripts/check_deck.py ./deck.html --shots ./out/
```

회사 정보까지 한 번에 넣으려면 `apply_brand.py`가 덱 선택과 단일 파일 묶기를 함께 처리한다.

```bash
python3 scripts/apply_brand.py --brand ./brand.json --deck internal --single-file -o ./보고서.html
# --deck: catalog · internal · weekly · ax · sales · project · training, 또는 HTML 파일 경로
```

### PowerPoint(.pptx)로 만들기

파워포인트로 직접 편집해야 하는 사람이 있으면 같은 내용을 .pptx 로 낸다.

```bash
node pptx/build.js --brand brand/hct/brand.json --out dist/pptx
node pptx/build.js --brand brand.json --deck internal    # 한 종만
```

색·크기는 `blue-report.css` 의 토큰을 그대로 읽으므로(`pptx/tokens.js`) 값이 두 벌로 갈라지지 않는다.
캔버스 1920x1080px 를 13.333x7.5in 로 옮기며 **1in = 144px, 1pt = 2px** 다. HTML 과 물리적으로 같은 크기다.

**HTML 판과 다른 점** — 형식의 한계이며 의도한 차이다.

| 항목 | HTML | PPTX |
|---|---|---|
| 등장 애니메이션 | 있음 | 없음 (PowerPoint 애니메이션은 넣지 않는다) |
| 폰트 | Noto Sans KR · Barlow (웹폰트) | 맑은 고딕 · Arial (PC 설치 폰트) |
| 도넛 · 막대 | SVG · CSS | **PowerPoint 네이티브 차트** — 값을 직접 고칠 수 있다 |
| 막대 기준선 | 차트에 선으로 표시 | 제목 아래 문장으로 표시 |
| 목록 | 글머리 기호 | `키워드 — 내용` 구조만 |
| 표 상태 | 알약 칩 | 색 있는 글자 |
| 발표자 노트 | `N` 키로 표시 | 슬라이드 노트 창 |

Noto Sans KR 과 Barlow 를 사내 PC 에 배포했다면 `pptx/tokens.js` 의 `F` 두 줄만 바꾼다.

#### 내용이 두 곳에 있다 — 합치지 않고 갈라짐을 검사한다

덱 내용은 `assets/deck-*.html` 과 `pptx/content.js` 두 곳에 따로 있다.
**HTML 이 기준이므로 내용을 고칠 때는 두 곳을 함께 고친다.**

합치지 않기로 했다. HTML 덱을 손으로 고치는 것이 이 시스템의 사용법이고
(`deck-*.html` 을 복사해 내용만 바꾼다), HTML 을 데이터에서 만들어 내는 생성물로
바꾸면 그 사용법이 사라진다. 색이 갈라지지 않는 것은 `tokens.js` 가 CSS 를 읽기
때문이지만, 내용은 그렇게 한쪽이 다른 쪽을 읽을 수 없다.

대신 갈라짐을 사람 눈이 아니라 스크립트가 잡는다.

```bash
python3 ../../../scripts/check_content_sync.py            # 저장소 루트 기준
python3 scripts/check_content_sync.py --deck internal
```

슬라이드 수 · 문서명 · 발표자 노트 36개 · 세로 막대 이름과 값 · 도넛 범례 · 표 머리글과
행을 두 곳에서 뽑아 견준다. 어긋나면 어느 덱 몇 장 어느 항목인지까지 찍는다.
`verify_repo.py` 와 CI 가 이것을 함께 돌리므로 한쪽만 고친 채로는 통과하지 못한다.

단위(`%` · `h`)와 표의 `colspan` 은 형식 차이라 대조에서 제외한다. 단위는 PPTX 생성기가
붙이고, HTML 은 지면에 직접 찍기 때문이다.

### A4 문서판 — 슬라이드가 아닌 문서

회의록 · 사규 · 매뉴얼 · 공지는 발표 슬라이드가 아니라 **A4 세로 문서**다.
지면 794×1123px(210×297mm @96dpi)이고 인쇄하면 그대로 A4 한 장이다.

```bash
cp assets/doc-minutes.html ./회의록.html
cp assets/blue-report.css assets/blue-doc.css assets/doc-viewer.css assets/doc-viewer.js ./
python3 scripts/check_doc.py ./회의록.html --shots out/
```

**색·타입·간격 토큰은 슬라이드와 같은 것을 쓴다.** `blue-doc.css` 는 토큰을
선언하지 않고 `blue-report.css` 를 전제한다. 두 파일을 함께 불러야 한다.
그래서 슬라이드와 문서의 색이 갈라질 수 없다.

| 항목 | 슬라이드 | A4 문서 |
|---|---|---|
| 지면 | 1920×1080 가로 | 794×1123 세로 |
| 글자 하한 | 24px (멀리서 봄) | 10.5pt = 14px (손에 듦) |
| 본문 대비 | 데이터 마크 2:1 | 본문 4.5:1 (인쇄물) |
| 애니메이션 | 있음 (끌 수 있음) | 없음 |
| 머리말·꼬리말 | 꼬리말만 | 쪽마다 둘 다 |
| 검사기 | `check_deck.py` 11항목 | `check_doc.py` 8항목 |

파일 구성도 덱과 같은 방식으로 나뉜다.

| 파일 | 역할 |
|---|---|
| `blue-doc.css` | 문서 파운데이션. raw hex 0, `--br-*` 토큰만 참조 |
| `doc-viewer.css` · `doc-viewer.js` | 껍데기 — 회색 바탕 · 조작 막대 · 인쇄 · 쪽번호 자동 |
| `doc-minutes.html` | 회의록 2쪽 |

**쪽번호와 문서명은 뷰어가 채운다.** `.bd-foot` 을 비워 두고 숫자를 적지 않는다.
쪽을 넣거나 빼도 번호가 어긋나지 않으며, 손으로 적으면 `check_doc.py` 가 실패시킨다.
문서명은 `.bd-doc` 의 `data-doc-title`, 문서번호는 `data-doc-no` 한 곳에서 읽는다.

**한 쪽을 넘치면 쪽을 나눈다.** `.bd-page` 가 `overflow:hidden` 이라 넘친 내용은
잘려 보이지 않고 꼬리말과 겹친다. `check_doc.py` 6번 항목이 이것을 잡는다.

---

### PDF로 내보내기

사내 배포나 이메일 첨부에는 PDF가 필요하다. 슬라이드 1장이 1페이지가 되고
크기는 **20in × 11.25in (정확히 16:9)** 다. 텍스트는 이미지가 아니라 실제 글자로 남아
복사와 검색이 된다.

```bash
python3 scripts/to_pdf.py ./보고서.html -o ./보고서.pdf --notes
```

`--notes` 를 주면 발표자 노트를 슬라이드별로 모아 마지막 페이지에 붙인다.
인쇄해서 손에 들기 위한 용도다.

### 준비물은 스크립트가 알아서 받는다

미리 설치할 것이 없다. 스크립트를 실행하면 없는 것만 골라 스스로 받고, 이미 있으면
아무것도 하지 않는다.

| 필요한 것 | 언제 | 받는 방법 |
|---|---|---|
| Pillow | 로고 변환 | `pip install Pillow` |
| Playwright + Chromium | 렌더 점검 · PDF | `pip install playwright` → `playwright install chromium` (약 150MB) |
| pptxgenjs | PPTX | `npm install` |

```bash
python3 scripts/ensure_deps.py          # 무엇이 있고 없는지만 본다
python3 scripts/ensure_deps.py --all    # 미리 다 받아 둔다
BLUE_REPORT_NO_INSTALL=1 …              # 자동 설치를 막고 명령만 안내받는다
```

### 회사 정보와 로고 넣기

회사명·워드마크·이메일·전화·저작권·로고 자리는 덱 안 8군데에 흩어져 있다. 손으로 고치면
빠뜨리기 쉬우므로 `brand.json` 한 곳에서 읽어 일괄 적용한다.

```bash
cp assets/brand.example.json ./brand.json
# brand.json 편집 후
python3 scripts/apply_brand.py --brand ./brand.json --single-file -o ./우리덱.html
```

```json
{
  "company": "주식회사 한빛테크",
  "wordmark": "한빛테크",
  "email": "contact@company.co.kr",
  "phone": "02-3456-7890",
  "copyrightYear": "2026",
  "logo": "mylogo-white.png",
  "logoOnLight": "mylogo-color.png",
  "logoHeight": 40
}
```

#### 로고는 두 벌이 필요하다

마크가 **모든 슬라이드의 우측 상단**에 들어가는데, 이 덱은 딥네이비 표지(`#071b45`)와
밝은 지면(`#f4f6f8`)을 오간다. 한 벌로는 반드시 한쪽에서 안 보인다.

| 항목 | 쓰이는 곳 | 필요한 로고 |
|---|---|---|
| `logo` | 표지 · 파트 간지 · 다크 요약 | 흰색 녹아웃 |
| `logoOnLight` | 그 밖의 모든 본문 슬라이드 | 원색(브랜드 파랑) |

원본 한 장에서 두 벌을 자동으로 뽑는다.

```bash
python3 scripts/make_logo_variants.py 로고.png --out-dir . --name mylogo
# mylogo-white.png  다크면용 흰색 녹아웃  → brand.json 의 logo
# mylogo-color.png  밝은 지면용 투명 원색판 → brand.json 의 logoOnLight
```

`logoOnLight`를 비워 두면 밝은 슬라이드는 워드마크 텍스트로 대체된다. 흰 로고를 흰 지면에
얹어 보이지 않게 만드는 대신 일부러 이렇게 실패시킨다. `check_deck.py`가 배경 광도를 재서
변형이 뒤바뀐 슬라이드를 잡아낸다.

- **로고** — PNG · JPG · SVG · WEBP. `brand.json` 기준 상대 경로 또는 절대 경로.
  data URI로 덱에 박히므로 완성된 HTML 하나만 들고 다니면 된다. 200KB 이하를 권한다.
- **`logoHeight`** — 우측 상단 마크의 높이(px). 기본 40, 권장 32~48. 상하 여백 띠
  (일반 슬라이드 84px · 표지 110px) 안에 들어가야 본문과 겹치지 않는다. 너무 키우면
  `check_deck.py`의 겹침 검사가 실패한다.
- **연락처가 없으면** `email` · `website` · `phone`을 빈 문자열로 둔다. 해당 줄과 행이
  통째로 사라진다. 사내 배포용 덱은 대개 이쪽이 맞다.
- **로고가 없으면** `logo`와 `logoOnLight`를 `null`로 둔다. `wordmark` 텍스트가 대신 들어가며,
  배경에 맞춰 밝은 면은 브랜드 파랑, 어두운 면은 흰색으로 자동 전환한다.
  한글이면 Barlow Condensed에 한글 글리프가 없으므로 Noto Sans KR로 자동 전환한다.
- 항상 원본 템플릿에서 새로 만들기 때문에 몇 번을 실행해도 결과가 같다.
  로고를 바꾸면 다시 실행하기만 하면 된다.
- 자리표시자 주석은 적용 후에도 남는다. 나중에 위치를 다시 찾기 쉽게 하기 위함이다.

본문 슬라이드의 예시 내용(수치 · 부서명 · 문구)은 자리표시자가 아니라 사용법을 보여주는
견본이다. 실제 발표 내용으로 직접 바꾼다.

### 다른 프로젝트에서 쓰기

이 폴더가 저장소 안(`<repo>/.claude/skills/blue-report`)에 있으면 **그 저장소에서만** 로드된다.
다른 프로젝트에서도 쓰려면 두 가지 방법이 있다.

#### 방법 1 — GitHub 플러그인 (권장)

저장소를 클론하지 않아도 되고, 저장소를 갱신하면 자동으로 최신판을 받는다.

```
/plugin marketplace add dytc880915-commits/hct-report-template
/plugin install blue-report@hct-tools
```

터미널에서는 한 줄로 붙여넣을 수 있다. **새 PC 에서 하는 일은 이 한 줄이 전부다.**

```bash
claude plugin marketplace add dytc880915-commits/hct-report-template && claude plugin install blue-report@hct-tools
```

한 번만 실행하면 그 PC의 모든 프로젝트에서 쓸 수 있다.
터미널에서 바로 하려면 `claude plugin marketplace add …` · `claude plugin install …` 를 쓴다.

`owner/repo` 짧은 형식은 기본 브랜치(`main`)에서 `.claude-plugin/marketplace.json` 을 찾는다.
아직 병합하지 않은 브랜치의 판을 쓰려면 URL 뒤에 브랜치를 붙인다.

```
/plugin marketplace add https://github.com/dytc880915-commits/hct-report-template.git#브랜치이름
```

설치 뒤 스킬 이름은 `blue-report:blue-report` 로 바뀐다(플러그인 이름이 앞에 붙는다).

이 저장소의 `.claude/settings.json` 에 마켓플레이스가 등록돼 있어, 이 저장소를 여는 사람은
`marketplace add` 없이 `install` 만 하면 된다.

> **설정만으로는 설치되지 않는다.** `extraKnownMarketplaces` 와 `enabledPlugins` 를
> 설정 파일에 적어 두어도 플러그인이 저절로 받아지지는 않는다. 설정을 남긴 채
> 플러그인 캐시를 지우고 세션을 두 번 띄워 확인했다 — 마켓플레이스는 다시 받아오지만
> `installed_plugins.json` 은 비어 있었고 스킬도 잡히지 않았다.
> 설정이 줄여 주는 것은 `marketplace add` 한 줄뿐이며, `install` 은 반드시 한 번 실행해야 한다.
> 새 PC 에서 명령을 0 으로 만드는 방법은 없다.

#### 방법 2 — 파일 복사 (오프라인·사내망)

GitHub 에 접근할 수 없는 환경에서 쓴다.

```bash
python3 scripts/install_blue_report_skill.py --check     # 설치 상태 확인, 변경 없음
python3 scripts/install_blue_report_skill.py --dry-run   # 바뀔 내용만 출력
python3 scripts/install_blue_report_skill.py             # ~/.claude/skills/blue-report 로 설치
```

- 멱등하다. 다시 실행해도 같은 내용이면 아무것도 쓰지 않는다.
- 기존 설치본을 덮어쓰기 전 `blue-report.backup-<타임스탬프>`로 통째 백업한다.
- 재생성 가능한 `dist/shots/`와 `__pycache__`는 설치본에서 제외한다.
- **설치 후 Claude Code 세션을 새로 시작한다.** 실행 중인 세션은 새 스킬을 즉시 읽지 않는다.

특정 프로젝트에만 넣으려면 `--target <프로젝트>/.claude/skills/blue-report`를 준다.
폴더를 직접 복사해도 동작한다. 스크립트는 상대 경로만 쓰므로 위치를 가리지 않는다.

| 설치 위치 | 적용 범위 |
|---|---|
| `~/.claude/skills/blue-report` | 내 모든 프로젝트 |
| `<프로젝트>/.claude/skills/blue-report` | 그 프로젝트만. 팀과 공유하려면 저장소에 커밋 |

브라우저에서 `deck.html`을 열면 좌우 화살표로 넘긴다. `N` 키로 발표자 노트를 켜고 끈다.
`deck.html?all=1`은 전 슬라이드를 원본 크기로 세로 나열한다(스크린샷 · PDF 내보내기용).

**쪽번호와 문서명은 뷰어가 자동으로 채운다.** 푸터에 숫자를 적지 않는다.
슬라이드를 넣거나 빼도 번호가 어긋나지 않는다. 문서명은 `#stage`의 `data-deck-title`
한 곳에서 읽으며, `apply_brand.py --title "문서명"` 으로 덮어쓴다.
표지 · 파트 간지 · 마무리에는 `.br-footer`가 없어 번호가 찍히지 않는다.

**발표자 노트**는 각 `.br-frame`의 `data-notes` 속성에 적는다.

---

## 1. 색

배경은 **밝은 지면 1개 + 다크면 2개까지**만 쓴다. 그 외 장식색은 금지한다.

### 지면과 카드

| 역할 | 값 | CSS 토큰 |
|---|---|---|
| 본문 지면 | `#f4f6f8` | `--br-page` |
| 카드 배경 | `#ffffff` | `--br-card` |
| 카드 테두리 | `#dbe3ec` | `--br-card-line` |
| 카드 그림자 | `0 10px 28px rgba(11,42,107,.07)` | `--br-card-shadow` |
| 기준선 · 구분선 | `#c3cedb` | `--br-hairline` |
| 알약 칩 테두리 | `#c8d1dc` | `--br-chip-line` |

### 텍스트

| 역할 | 값 | CSS 토큰 |
|---|---|---|
| 본문 | `#10151c` | `--br-text` |
| 보조 | `#54606e` | `--br-text-2` |
| 약함 | `#8b98a6` | `--br-text-3` |

### 강조

| 역할 | 값 | CSS 토큰 |
|---|---|---|
| 강조 1 · 주 | `#2f4a9c` | `--br-cobalt` |
| 강조 2 (시안) | `#35b8f0` | `--br-cyan` |
| 깊은 값 · 키워드 볼드 (딥네이비) | `#0b2a6b` | `--br-navy` |
| 경고 · 핵심 단일 수치 (코랄) | `#ff7a59` | `--br-coral` |

### 주의 콜아웃

| 역할 | 값 | CSS 토큰 |
|---|---|---|
| 테두리 | `#f0c469` | `--br-warn-line` |
| 배경 | `#fff7e4` | `--br-warn-bg` |
| 텍스트 | `#8a5a00` | `--br-warn-text` |

### 지연 · 위험 상태

| 역할 | 값 | CSS 토큰 |
|---|---|---|
| 배경 | `#fff1ec` | `--br-alert-bg` |
| 텍스트 | `#a33418` | `--br-alert-text` |
| 테두리 | `#ff7a59` | `--br-coral` |

### 다크면

| 역할 | 값 | CSS 토큰 |
|---|---|---|
| 표지 · 파트 간지 | `#071b45` | `--br-cover` |
| 핵심 정리 | `#101827` | `--br-dark` |
| 다크면 카드 | `#182238` | `--br-dark-card` |
| 다크면 카드 테두리 | `#2b3852` | `--br-dark-line` |
| 다크면 본문 | `#f4f6f8` | `--br-on-dark` |
| 다크면 보조 | `#a9bcd6` | `--br-on-dark-2` |
| 다크면 약함 | `#6b7c96` | `--br-on-dark-3` |
| 표지 보조 | `#a6c2e6` | `--br-on-cover-2` |
| 표지 약함 | `#8aa3c4` | `--br-on-cover-3` |
| 다크면 강조 · 숫자 | `#6fa8ff` | `--br-accent-on-dark` |
| 다크면 마지막 단계 강조 | `#ffcf6b` | `--br-amber` |

### 데이터 램프 — 밝은 지면 전용

값이 클수록 진한 단조 램프. **5색 전부 지면 `#f4f6f8` 대비 2:1 이상**이다.

| 토큰 | 값 | 지면 대비 |
|---|---|---|
| `--br-data-1` | `#0b2a6b` | 12.44 : 1 |
| `--br-data-2` | `#2f4a9c` | 7.51 : 1 |
| `--br-data-3` | `#2f7ff0` | 3.58 : 1 |
| `--br-data-4` | `#5b9bd5` | 2.73 : 1 |
| `--br-data-5` | `#86b0da` | 2.10 : 1 |

구간이 6개 이상이면 양 끝(`#0b2a6b` → `#86b0da`)을 고정한 보간 램프를 쓴다.
7단계는 토큰에 이미 있다: `#0b2a6b #20407e #345790 #486da2 #5d83b5 #729ac8 #86b0da`
(`--br-bar-1` ~ `--br-bar-7`, 전 단계 2:1 통과).

### 소프트 램프 — 다크면 전용

`--br-soft-1` `#7fb6f5` · `--br-soft-2` `#9dc4f2` · `--br-soft-3` `#a4c4e5`

> **주의.** 이 3색은 밝은 지면 `#f4f6f8`에서 각각 **1.96 / 1.67 / 1.67 : 1**로
> "데이터 마크 2:1 이상" 규칙에 미달한다. 밝은 면의 데이터 마크로 쓰지 않는다.
> 다크면 `#101827` 위에서는 6.9~8.4 : 1로 안전하다. 밝은 면에서는 보조 텍스트·구분선 등
> 비데이터 요소에만 쓴다.

---

## 2. 타입

폰트는 Google Fonts에서 불러온다.

```html
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;500;600;700&family=Barlow:wght@400;500;600;700&family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap">
```

| 용도 | 폰트 | 토큰 |
|---|---|---|
| 한글 제목 · 본문 | Noto Sans KR | `--br-font-kr` |
| 숫자 | Barlow 700 | `--br-font-num` |
| 섹션 라벨 | Barlow Condensed 600 + `letter-spacing:.14em` 대문자 | `--br-font-label` |

- 제목은 **weight 300과 900을 한 문장에서 대비**시킨다. `가벼운 앞말 + <strong>굵은 핵심</strong>`
- **1920×1080에서 24px 하한.** 예외는 큰 숫자에 붙는 `%` 첨자(`.br-sup`, `.44em`)뿐이다.
- 전역으로 `word-break:keep-all; overflow-wrap:break-word` — 한글이 음절 단위로 잘리는 것을 막는다.

### 크기 척도

| 토큰 | 값 | 용도 |
|---|---|---|
| `--br-fs-cover` | 108px | 표지 제목 |
| `--br-fs-display` | 96px | 마무리 CTA 제목 |
| `--br-fs-part` | 84px | 파트 번호 |
| `--br-fs-h2` | 62px | 슬라이드 제목 |
| `--br-fs-h2-sm` | 54px | 두 줄 이상 제목 |
| `--br-fs-h3` | 38px | 목차 항목 |
| `--br-fs-card-title` | 32px | 카드 제목 |
| `--br-fs-lede` | 28px | 제목 아래 요약 |
| `--br-fs-label` | 26px | 섹션 라벨 |
| `--br-fs-body` | 25px | 본문 |
| `--br-fs-foot` | 24px | 푸터 · 하한 |
| `--br-fs-stat-hero` | 200px | 단일 수치 강조 |
| `--br-fs-stat` | 56px | 카드 안 수치 |
| `--br-fs-stat-sm` | 32px | 막대 값 |

---

## 3. 간격과 형태

- 슬라이드 여백 — 본문 `84px 96px 60px`, 표지·간지 `110px 120px 80px`
- 간격 척도 — `8 / 14 / 22 / 34 / 52 / 84 px` (`--br-sp-1` ~ `--br-sp-6`)
- 카드 라운드 **18px**, 알약 칩 **999px**, 좁은 막대 **2px**, 넓은 세로 막대 **8px**
- 알약 칩은 **한 줄 전용**이고 **그림자를 주지 않는다.** 두 줄이 되면 라운드 18px 사각형으로 바꾼다.
- 제목 밑줄, 장식용 색 띠, 사이드 스트라이프, 블루프린트 `+` 코너 마크를 쓰지 않는다.

---

## 4. 차트 규칙 (엄수)

### 도넛 — 파이 금지

```
C    = 2 × π × r                       원주
dash = C × pct/100  −  C × 1.5/360     구간 길이 (1.5도 간격 차감)
rot  = 누적pct × 3.6 − 90              12시에서 시작
```

```html
<circle class="dsh" r="110" stroke="#0b2a6b" stroke-width="48"
        stroke-dasharray="400.8 691.2" transform="rotate(-90)"></circle>
```

- `stroke-dasharray`의 **두 번째 값은 항상 원주 C**다. 다르면 구간이 반복된다.
- 손으로 적은 `<path d="M0 0 L… A…">` 파이는 금지한다. 수치와 각도가 어긋난다.
- 구간은 3~5개. 6개를 넘으면 막대로 바꾸거나 하위를 '기타'로 묶는다.
- 라벨은 **도넛 밖**에. 좁은 홀에 텍스트를 넣지 않는다.
  필요하면 꺾은 리더 라인 + 구간색 점(r=6)으로 연결한다.

### 막대

- **값은 막대 안이 아니라 전용 컬럼 또는 막대 위 줄에.** 퍼센트 폭 안에 넣으면 짧은 값에서 삐져나온다.
- 이름은 차트와 **다른 그리드 컬럼 / flex 형제**에 둔다. 절대 위치로 막대 위에 올리지 않는다.
- 높이 = `값 / 최댓값 × 채널높이`. 채널 470px 기준.
- `border-radius = 높이/2`인 막대는 값이 높이보다 좁아지면 전부 같은 캡슐로 보인다 → 좁은 채널은 2px.

### 공통

- **데이터 마크(호·막대·버블·범례 스와치)는 지면 대비 2:1 이상.** 배경·구분선 톤을 데이터에 쓰지 않는다.
- 인접 구간에 같은 색 금지. 값이 클수록 진한 단조 램프.
- 버블은 면적 비례: `d = k × √value`. 지름 비례는 큰 값을 과장한다.

---

## 5. 문체 (엄수)

- **개조식 · 명사형.** 슬라이드 본문은 명사로 끝낸다.
  - 존댓말 종결 금지 — `~합니다 / ~습니다 / ~입니다 / ~됩니다 / ~해요 / ~어요`
  - **평서형 종결도 금지** — `~한다 / ~된다 / ~없다 / ~았다·었다` 등 `다` 로 끝나는 서술
  - 예: `진단으로 푼다` → `진단으로 해결`, `시작도 안 됐다` → `시작 전`
  예외는 설문 문항과 응답 선택지 원문뿐이며, 그 줄에 `<!-- 원문 -->` 주석을 남긴다.
  **발표자 노트(`data-notes`)는 대상이 아니다** — 노트는 `~한다` 형으로 적는다.
- 긴 서술은 `키워드 — 내용`으로 쪼갠다.
- 핵심 수치·개념은 `<strong style="font-weight:700;color:#0b2a6b">`로 강조한다 (`.br-key`).
- **한 슬라이드 = 한 주장.** 문장 수를 줄이고 한눈에 스캔되게 한다.

---

## 6. 진입 애니메이션

슬라이드가 활성화되면 `[data-deck-active]`가 붙고 **제목 → 본문 → 차트** 순으로 등장한다.

| 클래스 | 동작 | 쓰는 자리 |
|---|---|---|
| `.a` | fade-up | 제목·본문·카드 기본값 |
| `.ad` | fade-down | 섹션 라벨 |
| `.f` | fade | 푸터·축 이름 |
| `.bx` | scale-X | 가로 막대 |
| `.by` | scale-Y | 세로 막대 |
| `.p` | pop | 단일 수치 강조 |
| `.dsh` | dasharray | 도넛 구간 |

딜레이 `.d1` ~ `.d12` = **80ms 단위**. 마지막 딜레이가 1초를 넘지 않게 한다.
넘으면 요소가 너무 많은 것이므로 슬라이드를 쪼갠다.
`prefers-reduced-motion: reduce`에서는 전부 꺼지므로, 애니메이션에 의존해 정보를 전달하지 않는다.

**덱 단위로 끌 수 있다.** `#stage` 에 `data-no-anim` 을 주면 등장 효과가 전부 꺼진다.

```html
<div id="stage" data-no-anim data-deck-title="…">
```

주간보고처럼 화면에 띄워 놓고 읽거나 인쇄해서 돌리는 문서는 꺼 두는 편이 낫다.
넘길 때마다 요소가 하나씩 나타나면 표를 훑는 속도가 느려진다.
`weekly` 와 `ax` 덱은 이미 꺼져 있고, 발표용 덱(`internal` · `sales` · `project` · `training` · `catalog`)은 켜져 있다.

```css
@keyframes br-fu   { from { opacity:0; transform:translateY(22px) } }
@keyframes br-fd   { from { opacity:0; transform:translateY(-16px) } }
@keyframes br-fi   { from { opacity:0 } }
@keyframes br-gx   { from { transform:scaleX(0) } }
@keyframes br-gy   { from { transform:scaleY(0) } }
@keyframes br-pop  { from { opacity:0; transform:scale(.8) } }
@keyframes br-dash { from { stroke-dasharray:0 4000 } }
```

---

## 7. 슬라이드 12종

| # | 슬라이드 | 배경 | 쓰는 자리 |
|---|---|---|---|
| 01 | 표지 | `#071b45` | 문서 첫 장 |
| 02 | 목차 | `#f4f6f8` | 파트 4~5개까지 |
| 03 | 파트 간지 | `#071b45` | 파트 시작 |
| 04 | 핵심 정리 | `#101827` | 파트 끝. 카드 6개가 상한 |
| 05 | 단일 수치 강조 | `#f4f6f8` | 한 슬라이드 = 한 주장 |
| 06 | 도넛 차트 | `#f4f6f8` | 구성비 3~5구간 |
| 07 | 막대 차트 | `#f4f6f8` | 순위·비교 7구간까지 |
| 08 | 비교 2열 | `#f4f6f8` | 전후 · A안B안 · 평균대비 |
| 09 | 지표 표 | `#f4f6f8` | 과제·지표 목록. 행 7개가 상한 |
| 10 | 3단계 로드맵 | `#f4f6f8` | 실행 계획 |
| 11 | 일정 타임라인 | `#f4f6f8` | 기간 병행과 마일스톤 |
| 12 | 마무리 CTA | `#071b45` | 행동 하나만 제시 |

---

## 8. 레이아웃 체크리스트

새 슬라이드를 만들면 반드시 확인한다.

1. `section.scrollHeight === 1080`, `scrollWidth === 1920`
   넘치면 `flex:1` 컨테이너에 `min-height:0`을 주고 행 높이를 줄인다.
2. 절대 위치 라벨이 차트를 덮지 않는가 → 차트와 라벨을 다른 그리드 컬럼 / flex 형제로 분리
3. 푸터가 콘텐츠와 겹치지 않는가 → 항상 마지막 형제, `flex-shrink:0`
4. 24px 미만 텍스트가 없는가 (`%` 첨자만 예외)
5. 데이터 마크 대비 2:1 이상, 인접 색 중복 없음
6. 파이 `<path>` 없음, 도넛 dasharray가 원주와 일치
7. 토큰 밖 raw hex 없음
8. 우측 상단 `.br-mark`가 있고, 본문과 겹치지 않으며, 배경 밝기와 변형이 맞는가
   → 마크는 상단 여백 띠 안에만 둔다. 우측 상단에 콘텐츠를 붙이지 않는다.

`python3 scripts/check_deck.py deck.html --shots out/`이 위 1·4·5·6·7·8과 문체를 자동
검사하고 슬라이드별 PNG를 남긴다. 판정은 11항목이다.

| # | 항목 | 실패하면 |
|---|---|---|
| 1 | 문체 — 존댓말·평서형 종결 없음 | `~합니다` · `~한다` 로 끝나는 말을 명사형으로 고친다 |
| 2 | 파이 없음 — 도넛만 사용 | 손으로 적은 `<path d="M…A…">` 를 `donut.py` 산출물로 바꾼다 |
| 3 | 색 — 토큰 밖 raw hex 없음 | 슬라이드의 hex 를 `--br-*` 변수로 바꾼다 |
| 4 | 슬라이드 크기 1920x1080 | `flex:1` 컨테이너에 `min-height:0` 을 주고 행 높이를 줄인다 |
| 5 | 글자 크기 24px 미만 없음 | `%` 첨자(`.br-sup`) 외에는 24px 이상으로 올린다 |
| 6 | 데이터 마크 대비 2:1 이상 | 밝은 지면에서 `--br-soft-*` 를 빼고 데이터 램프를 쓴다 |
| 7 | 본문 영역이 위아래로 겹치지 않는다 | 여백을 줄이거나 내용을 덜어 아래 영역을 밀어내지 않게 한다 |
| 8 | 브랜드 마크가 우측 상단에 있다 | `.br-mark` 를 빠뜨린 슬라이드에 넣는다 |
| 9 | 브랜드 마크가 본문과 겹치지 않는다 | `logoHeight` 를 줄이거나 본문을 여백 띠 밖으로 뺀다 |
| 10 | 로고 변형이 배경 밝기와 맞는다 | `data-on` 값과 `logo` · `logoOnLight` 짝을 맞춘다 |
| 11 | 도넛 dasharray 검산 | `donut.py` 로 다시 생성한다. 손계산하지 않는다 |

11번은 도넛을 쓰지 않은 덱에서 `주의`로 나온다. **`주의`는 허용되고 `실패`만 완료를 막는다.**

**실패가 0이어도 PNG를 눈으로 확인한다.** 어색한 여백은 스크립트가 잡지 못한다.

---

## 9. 브랜드 자리

교체 지점은 두 곳뿐이다. 하나는 끝났고 하나는 남아 있다.

### 브랜드 마크 — 적용 완료

모든 슬라이드 우측 상단의 `.br-mark`. 표지도 본문도 같은 자리다.
`data-on="dark"`는 딥네이비·다크 배경, `data-on="light"`는 밝은 지면을 뜻하며
`apply_brand.py`가 이 값을 보고 로고 변형을 고른다.

이 저장소에는 HCT 로고 두 벌이 `brand/hct/`에 들어와 있고 `brand.json`이 가리킨다.
로고를 지정하지 않은 브랜드에서는 `.br-wordmark`의 회사명 텍스트가 대신 들어간다.

**남은 것** — 원본 로고의 마크 영역이 264×86px 이다. 화면 발표에는 충분하지만 인쇄에는
모자란다. SVG 나 고해상도 원본이 생기면 교체하고 `make_logo_variants.py`로 두 벌을
다시 뽑는다.

### 사내 폰트 — 미확정

`blue-report.css`의 `--br-font-kr`, `--br-font-num`, `--br-font-label`의 첫 패밀리만
교체한다. 나머지는 폴백으로 남긴다. 현재는 Google Fonts 의 Noto Sans KR · Barlow ·
Barlow Condensed 를 쓴다.

PPTX 판은 PC 설치 폰트를 쓰므로 별도다. 사내 폰트를 PC 에 배포했다면 `pptx/tokens.js`의
`F` 두 줄도 함께 바꾼다.

### 연락처

`brand.json`의 `email` · `website` · `phone`에 적는다. 빈 문자열로 두면 해당 줄과 행이
통째로 사라진다. 사내 배포용 덱은 대개 이쪽이 맞고, `brand/hct/brand.json`도 그렇게 돼 있다.
