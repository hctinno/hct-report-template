# Codex 발표 덱 작업 지시서

이 문서는 사람이 읽는 설명서가 아니라 **에이전트에게 그대로 건네는 작업 지시**다.
Codex·Gemini 등 Claude Code 가 아닌 에이전트는 `.claude/skills/` 를 인식하지 못하므로
이 파일이 진입점 역할을 한다.

---

## 사람이 칠 한 줄

저장소 안에서 에이전트를 띄운 뒤 이렇게 친다. **경로는 저장소 루트 기준 상대 경로이므로
어느 PC 어느 폴더에 클론했든 그대로 통한다.**

```
docs/CODEX_DECK_PROMPT.md 를 읽고 그대로 수행해라. 용도는 사내 보고, 주제는 8월 월간 업무 보고.
```

용도와 주제를 빼고 파일만 지목해도 된다. 그 경우 에이전트가 먼저 물어본다.

| 넘길 값 | 고르는 것 |
|---|---|
| 용도 | 사내 월간 · 주간 · AX 주간 · 팀 압축 주간 · 경영진 · 전직원 · 외부 제안 · 프로젝트 · 교육 · 전략 · 고밀도 · A4 문서 · 웹 보드 |
| 주제 | 덱 제목과 내용 |
| 형식 | HTML(기본) · PDF · PPTX. 여러 개 가능. 보드는 HTML 만 |

저장소가 아직 없는 PC라면 먼저 받는다. 폴더 이름과 위치는 아무래도 좋다.
**기본 브랜치가 `main` 이 아니라 `full/main` 이므로 브랜치를 적을 때 주의한다.**

```bash
git clone -b full/main https://github.com/hctinno/hct-report-template.git
cd hct-report-template
```

매번 이 파일을 지목하는 것이 번거로우면 에이전트의 전역 지침에 한 번만 심어 둔다.
그러면 어느 폴더에서 시작하든 에이전트가 스스로 저장소를 받아 온다 —
`docs/AGENT_WIRING.md` 가 붙여넣을 문단과 설치기를 담고 있다.

---

## 여기서부터가 에이전트에게 주는 지시다

### 0. 준비와 사전 확인

**모든 경로는 저장소 루트 기준 상대 경로다.** 절대 경로를 쓰지 않는다. 저장소가 어느
드라이브 어느 폴더에 있든 상관없어야 한다. 먼저 저장소 루트로 이동해 `git pull` 로
최신 기본 브랜치(`full/main`)를 받는다.

명령 예시는 `python` 으로 적었다. macOS·Linux 에서는 `python3` 으로 바꿔 쓴다.
경로 구분자는 `/` 로 통일했다. Windows 에서도 그대로 동작한다.

아래 5개가 실재하는지 먼저 확인한다. **하나라도 없으면 작업을 멈추고 그 사실을 보고한다.**
없는 파일을 짐작으로 대체하지 않는다.

```
.claude/skills/blue-report/README.md
.claude/skills/blue-report/references/rules.md
.claude/skills/blue-report/DESIGN.md
.claude/skills/blue-report/scripts/build_deck.py
.claude/skills/blue-report/scripts/check_live.py
brand/hct/brand.json
```

### 1. 규격 읽기

**`.claude/skills/blue-report/DESIGN.md`(본문 스타일 한 장)를 처음부터 끝까지 읽는다.** 발표 덱을 만드는 데
필요한 것이 이 한 장에 있다 — 일하는 방식 · 본문 파일 형식 · 조립 목록 · 위계 · 내용별로 그릴 것 · 색 역할 ·
토큰 · 금지 · 끝내기 전 점검. 나머지 문서는 찾아보는 색인이다 — 부품 속성 · 위젯 · 근거 JSON · 발표 키는
스킬 `README.md` 「6-3」, 색 역할 상세는 `references/design-language.md`, 차트 규칙은 `references/rules.md`.
사용자가 애니메이션 · 효과를 요청하면 **`.claude/skills/blue-report/MOTION.md`** 에서 고른다.

### 2. 덱 고르기와 만들기

| 무엇을 만드나 | 만드는 법 |
|---|---|
| 보고서 · 발표 덱 (기본) | **본문만 쓰고 `build_deck.py` 로 조립** — 아래 |
| 회의록 (A4 인쇄) | `--deck minutes` 견본을 복사해 내용만 바꾼다 — 아래 「회의록」 |
| 고쳐 가며 쓰는 현황판 | `--deck manage` 견본을 복사해 내용만 바꾼다 — 아래 「관리보드」 |

경영진 보고 · 주간보고 · 전략 보고처럼 용도가 달라도 발표 · 보고는 전부 첫 줄이다.
나머지 양식은 `assets/archive/` 에 보관했다(아래 「보관 양식」). **사람이 이름을 짚거나
PowerPoint 파일이 꼭 필요할 때만 쓴다.**

#### 발표 덱 — 본문만 쓰고 빌드가 틀을 씌운다

`decks-out/<보고서>/` 에 파일 셋을 만든다. 견본은 `.claude/skills/blue-report/examples/standard/`.

```
deck.yaml       조립 목록 — 표지 정보 · 장(章) 순서 · 장마다 넣을 장 id · 마무리 · 부록
slides.html     본문 파일 — 장마다 <section id="…" data-name data-notes> 하나, 본문만
evidence.json   출처 칩 근거(선택)
```

```bash
python .claude/skills/blue-report/scripts/build_deck.py decks-out/<보고서>/deck.yaml --brand brand/hct/brand.json --single-file -o decks-out/<보고서>.html
python .claude/skills/blue-report/scripts/check_live.py decks-out/<보고서>.html --shots decks-out/<보고서>-shots
```

- **쓰지 않는 것:** 머리띠 · 꼬리띠 · 쪽번호 · 로고 · 워터마크 · 폰트 · 진행선 · 조작판 · 발표 기능,
  표지 · 목차 · 장 간지 · 마무리 · 부록 간지. 빌드가 만든다. 본문에 섞어 쓰면 떼고 주의를 낸다.
- **쓰는 것:** 장마다 제목(「주장 — `<em>`핵심구`</em>`」) · 리드 · 본문 도식 · 발표자 노트.
  `DESIGN.md` 「4」 대응표에서 내용 모양에 맞는 표현을 고르고, 부품 카탈로그(`assets/live-catalog.html`)나
  패턴첩(`assets/live-patterns.html`)의 해당 장을 열어 마크업을 가져와 내용에 맞게 고친다.
  조립 목록에 `catalog:<id>` · `patterns:<id>` 를 적으면 그 장을 견본 그대로 불러 볼 수 있다.
- 맞는 부품이 없으면 장 안 `<style data-own>` 으로 새로 짠다 — 선택자는 `#장id` · `x-` 접두어,
  색은 `var(--br-*)` · `var(--bl-*)` 토큰, 치수는 `rem`. 견본은 카탈로그 `own` 장.
- 실패가 0 이 될 때까지 본문 파일을 고치고 다시 빌드한다. `--shots` 로 남은 장별 PNG 를 눈으로 넘겨 본다.

옛 방식(기준 덱 `live-standard.html` 을 복사해 내용만 바꾸기)도 그대로 돌지만 예비다.

#### 회의록 — A4 세로 문서

1920x1080 이 아니라 794x1123 지면이고, 검사기도 `check_doc.py` 로 다르다.

| 파일 | `--deck` 이름 | 용도 | 쪽수 |
|---|---|---|---|
| `doc-minutes.html` | `minutes` | 회의록 | 4 |

#### 관리보드 — 웹 보드

읽는 물건이 아니라 **화면에서 상태를 바꾸는 것**이다. 지면 크기가 없고 화면 폭에 따라
흐른다. 글자 하한이 12.5px 로 다르고 검사기도 `check_board.py` 다. PPTX·PDF 대상이 아니다.
`blue-report.css` 와 `blue-web.css` 두 벌을 함께 부른다.

| 파일 | `--deck` 이름 | 용도 |
|---|---|---|
| `board-manage.html` | `manage` | 관리보드 (대시보드형 · 절 12 · 표 8 · 일정 격자) |

#### 보관 양식 — `assets/archive/`

| 묶음 | `--deck` 이름 | 비고 |
|---|---|---|
| 고정 지면 덱 1920x1080 · 12종 | `internal` · `weekly` · `ax` · `team` · `exec` · `allhands` · `sales` · `project` · `training` · `strategy` · `report` · `catalog` | PPTX 빌드의 원본 · 검사기 `check_deck.py` |
| A4 문서 3종 | `policy` · `manual` · `notice` | |
| 웹 보드 4종 | `board` · `execboard` · `teamboard` · `gapcheck` | |
| 라이브 브리핑 | `live` | |
| FCC/KC 보고서 14종 | `assets/archive/fcc-kc/` | 인증 시험 보고서 전용 |

보관 파일은 CSS·뷰어를 `../` 로 부른다. 손으로 복사하지 말고 `apply_brand.py --deck <이름>` 으로 만든다.

**용도를 지시받지 못했으면 임의로 고르지 말고 사람에게 먼저 묻는다.**

복사할 때 다음 3개를 같은 폴더에 함께 둔다. 없으면 스타일이 전혀 적용되지 않는다.

```
assets/blue-report.css
assets/deck-viewer.css
assets/deck-viewer.js
```

한 파일로 만들려면 4절의 `--single-file` 을 쓴다. 그 경우 위 3개를 옮기지 않아도 된다.

### 3. 어겨선 안 되는 것

- **색은 `--br-*` CSS 변수만 쓴다.** 새 hex 값을 슬라이드에 직접 적지 않는다.
- **파이 차트 금지.** 도넛만 쓴다. `<path d="M…A…">` 로 부채꼴을 그리지 않는다.
  도넛 SVG 는 `scripts/donut.py` 로 생성한다. 각도를 손으로 계산하지 않는다.
- **문체는 개조식**(명사형 종결). `~합니다`, `~됩니다`, `~입니다` 를 쓰지 않는다.
- **슬라이드는 정확히 1920x1080.** 넘치면 행 높이를 줄인다. 축소하지 않는다.
- **글자는 24px 이상.** `%` 첨자(`.br-sup`)만 예외다.
- **데이터 마크는 배경 대비 2:1 이상.** 밝은 지면에 `--br-soft-*` 를 쓰지 않는다.
- **로고는 모든 슬라이드 우측 상단** `.br-mark` 자리에 들어간다.
  그 자리(상단 여백 띠)에 본문 콘텐츠를 붙이지 않는다.
- **예시 수치·부서명·문구는 자리표시자가 아니라 사용법 견본이다.** 실제 내용으로 바꾼다.
  바꾸지 않고 남기면 남의 회사 숫자가 그대로 발표된다.
- **기준·라이브 덱은 치수를 `rem` 으로만 적는다.** `px` 는 1px 테두리와 blur 반경만 예외다.
- **기준·라이브 덱은 머리띠·꼬리띠·쪽번호·로고·워터마크를 장마다 단다.** 하나라도 빼면
  `check_live.py` 가 실패로 잡는다. 이것이 「우리 양식으로 만들었다」와 실제로 회사 문서로
  보이는 것의 차이다.
- **기준 덱 산출물은 `apply_brand.py --deck <파일> --title "문서명" --single-file` 로 만든다.** `--title` 을
  빼면 brand.json 의 `docTitle` 이 덱 제목을 덮어 꼬리띠 문서명이 장마다 바뀐다. 견본의 로고 자리는
  「COMPANY NAME」이다. 복사해 내용만 바꾸고 끝내면 로고도 워터마크도 없다.
- **근거가 있는 수치에는 출처 칩을 단다.** 수치 옆 `<button type="button" class="bl-ev" data-ev="E1">출처</button>`,
  문서 끝 `<script type="application/json" id="bl-evidence">` 에 근거(제목·등급·사실·출처·날짜).
  등급은 A 1차 공식 · B 학술·전문 · C 언론·2차 · R 직접 조회·집계. 근거 없는 칩은 실패다.

### 4. 브랜드 적용과 출력

저장소 루트에서 실행한다. **산출물은 `decks-out/` 에 넣는다.** 이 폴더는 `.gitignore`
처리돼 있어 저장소를 더럽히지 않는다. 저장소 루트에 결과 파일을 흩어 놓지 않는다.

```bash
# 발표 덱은 2절의 build_deck.py 가 브랜드까지 입힌다. 아래 apply_brand.py 는 회의록 · 보드 · 보관 양식용
# HTML — 회사명·로고·저작권을 넣어 한 파일로 만든다
python .claude/skills/blue-report/scripts/apply_brand.py --brand brand/hct/brand.json --deck standard --title "문서명" --single-file -o decks-out/deck.html

# --deck 은 위 표의 이름 또는 HTML 파일 경로. A4 문서와 웹 보드도 같은 --deck 으로 준다
#   --deck minutes   A4 회의록      --deck manage   관리보드
# 내용을 직접 편집한 덱이면 파일 경로를 준다:
#   --deck decks-out/my-deck.html

# PDF — 발표용. --notes 를 주면 발표자 노트를 마지막 장에 붙인다
python .claude/skills/blue-report/scripts/to_pdf.py decks-out/deck.html

# PowerPoint — 보관 고정 지면 덱 내용(pptx/content.js)으로 만든다
node .claude/skills/blue-report/pptx/build.js --brand brand/hct/brand.json --out decks-out
```

PPTX 는 HTML 덱과 내용을 따로 들고 있다. **HTML 쪽이 기준이므로 내용을 바꿀 때는
`assets/archive/deck-*.html` 과 `pptx/content.js` 두 곳을 함께 고친다.** 색은 두 판이
`assets/blue-report.css` 의 토큰을 같이 읽으므로 갈라지지 않는다.

한쪽만 고쳤는지는 스크립트가 잡는다. 템플릿 자체를 고쳤다면 돌린다.

```bash
python scripts/check_content_sync.py
```

슬라이드 수 · 문서명 · 발표자 노트 · 막대 · 도넛 · 표를 두 곳에서 뽑아 견주고,
어긋나면 어느 덱 몇 장 어느 항목인지 찍는다.

필요한 것(Pillow · Chromium · node_modules)은 스크립트가 스스로 받는다. 미리 설치하지
않아도 된다. 설치를 막으려면 환경변수 `BLUE_REPORT_NO_INSTALL=1` 을 준다. 그 경우
필요한 명령만 출력하고 멈춘다.

### 5. 완료 조건

```bash
# 계통마다 검사기가 다르다. 만든 것에 맞는 것을 돌린다.
python .claude/skills/blue-report/scripts/check_deck.py  decks-out/deck.html   # 슬라이드 덱
python .claude/skills/blue-report/scripts/check_live.py  decks-out/deck.html   # 기준·라이브 덱
python .claude/skills/blue-report/scripts/check_doc.py   decks-out/doc.html    # A4 문서
python .claude/skills/blue-report/scripts/check_board.py decks-out/board.html  # 웹 보드
```

`check_deck.py` 가 17항목, `check_live.py` 가 30항목을 기계로 판정한다.
`check_live.py` 의 30항목 중 여섯이 지면 크롬이다 — 머리띠 · 꼬리띠 · 쪽번호 ·
머리띠 브랜드 마크 · 워터마크 · 마크 배경 짝. 넷은 산출물이 회사 문서로 나왔는지다 —
로고 자리표시자 · 스타일 · 본문 폰트 · 지면 끝. 출처 칩이 있으면 근거에 이어지는지도 본다.
조작판이 꼬리띠의 문서명·쪽번호를 덮는지는 1600·760·400px 세 폭에서 장마다 잰다.
맞춤 CSS 가 고정 영역 · 토큰 · rem · 이름 규칙을 지켰는지(28번), 글 · 표뿐인 장 비율(29번, 주의)도 본다.

check_deck.py 가 판정하는 것:

문체 · 파이 차트 금지 · 도넛 dasharray 검산 · 토큰 밖 raw hex · 슬라이드 크기 ·
최소 글자 크기 · 데이터 마크 대비 · 본문 겹침 · 브랜드 마크 존재 · 마크와 본문 겹침 ·
배경 워터마크 배치(표지 제외) · 배경 밝기와 로고 변형 일치 · 워터마크 자산 구분 ·
지시선 주석 잘림.

**실패가 0 이 아니면 완료가 아니다.** 실패가 남은 채로 "완료"라고 쓰지 않는다.

덱 하나가 아니라 템플릿·스크립트·문서를 고쳤다면 저장소 전체를 본다. GitHub Actions 가
push·PR 마다 이 한 줄을 그대로 돌린다.

```bash
python scripts/verify_repo.py
```

`주의`는 허용된다. 도넛을 쓰지 않은 덱에서 나오는 정상 결과다.

레이아웃 검수까지 하려면 `--shots 폴더명` 을 붙여 슬라이드별 PNG 를 남기고 눈으로 본다.
겹침은 스크립트가 잡지만 어색한 여백은 잡지 못한다.

### 5-1. HTML 덱은 발표에 쓴다

만든 HTML 을 넘길 때 조작법을 함께 알린다. 모르면 발표를 못 한다.

| 키 · 버튼 | 하는 일 |
|---|---|
| `F` · 「발표」 | 전체화면 발표 모드 — 버튼과 노트가 사라진다 |
| `←` `→` `Space` · 클릭 | 슬라이드 넘김 |
| `Esc` | 발표 모드 나가기 |
| `N` · 「노트」 | 발표자 노트 |
| 「목록」 | 전 슬라이드 세로 나열 (검수용, 발표용 아님) |

**「목록」을 발표용으로 안내하지 않는다.** 세로 스크롤이라 발표가 되지 않는다.

### 6. 보고 형식

보고는 **한국어로** 쓴다. 다음을 반드시 포함한다.

- 실행한 명령 (그대로)
- `check_deck.py` 결과의 통과 / 주의 / 실패 수
- 산출물 파일 경로
- 바꾸지 못했거나 확신이 없는 내용

검사를 돌리지 않았으면 그 사실을 쓴다. 돌린 것처럼 쓰지 않는다.

---

## 참고 — 이 저장소 밖에서 쓸 때

다른 프로젝트 폴더에서 작업한다면 스킬 폴더를 통째로 복사한다. `--target` 을 생략하면
사용자 스킬 폴더(`~/.claude/skills/blue-report`)에 설치되어 그 PC 의 모든 프로젝트에서 쓸 수 있다.

```bash
python scripts/install_blue_report_skill.py                      # 사용자 스킬 폴더
python scripts/install_blue_report_skill.py --target <프로젝트경로>   # 특정 프로젝트
```

Claude Code 라면 저장소를 클론하지 않고 플러그인으로 받을 수도 있다. PC 마다 한 번만
실행하면 된다.

```bash
claude plugin marketplace add hctinno/hct-report-template
claude plugin install blue-report@hct-tools
```

파일도 줄 수 없는 환경(웹 UI 등)이라면 `.claude/skills/blue-report/README.md` 내용을
통째로 붙여넣고 "이 규격을 따라 1920x1080 HTML 슬라이드를 만들어라"라고 지시한다.
다만 이 경우 완성된 덱 템플릿과 검증 스크립트가 없어 품질이 떨어진다.
