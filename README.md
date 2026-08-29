# HCT 발표 템플릿

주식회사 에이치시티 사내 공용 발표 슬라이드 디자인 시스템. **블루 리포트**라 부른다.

한 소스에서 **HTML · PDF · PowerPoint** 세 형식을 만들고, 규칙을 사람 눈이 아니라 스크립트가 판정한다.

---

## 쓰는 법 — 세 가지

### 1. Claude Code — 플러그인 (권장)

저장소를 클론하지 않아도 되고, PC 마다 한 번만 실행하면 그 PC 의 모든 프로젝트에서 쓸 수 있다.

```bash
claude plugin marketplace add dytc880915-commits/hct-report-template
claude plugin install blue-report@hct-tools
```

설치 뒤 "블루 리포트로 사내 보고 덱 만들어줘" 처럼 말하면 스킬이 뜬다.

> `.claude/settings.json` 의 `extraKnownMarketplaces` 는 마켓플레이스를 **등록**만 한다. 설치는 하지 않는다. `plugin install` 은 PC 마다 한 번 실행해야 한다.

### 2. Codex 등 다른 에이전트 — 클론

Codex 는 `.claude/skills/` 를 인식하지 못한다. 파일이 디스크에 있어야 한다.

```bash
git clone https://github.com/dytc880915-commits/hct-report-template.git
cd hct-report-template
```

그 폴더에서 에이전트를 띄우고 한 줄 친다.

```
docs/CODEX_DECK_PROMPT.md 를 읽고 그대로 수행해라. 용도는 사내 보고, 주제는 8월 월간 업무 보고.
```

용도와 주제를 빼도 된다. 그 경우 에이전트가 먼저 묻는다.

### 3. 다른 프로젝트에 복사

```bash
python scripts/install_blue_report_skill.py                       # 사용자 스킬 폴더
python scripts/install_blue_report_skill.py --target <프로젝트경로>   # 특정 프로젝트
```

---

## 덱 6종

같은 레이아웃을 쓰되 배치 순서와 장수가 용도에 맞게 다르다. 조직 주간보고는 매주 반복하므로 목차를 두지 않고 타임라인이 요일 단위다. 사내 보고는 다크 요약이 3번째에 있고(경영진이 앞부분만 보고 넘어간다), 외부 제안은 9번째에 있다(문제 제기부터 설득한 뒤 정리한다).

| 파일 | 용도 | 장수 |
|---|---|---|
| `deck-internal-report.html` | 사내 보고 (월간) | 9 |
| `deck-weekly-report.html` | 조직 주간보고 | 7 |
| `deck-ax-weekly.html` | AX 조직 1장 보고 + 부록 | 6 |
| `deck-sales-proposal.html` | 외부 제안·영업 | 10 |
| `deck-project-report.html` | 프로젝트 착수·완료 | 9 |
| `deck-training.html` | 교육·기술 설명 | 8 |
| `deck-template.html` | 레이아웃 12종 카탈로그 | 12 |

전부 `.claude/skills/blue-report/assets/` 에 있다.

---

## 만들기

저장소 루트에서 실행한다. 산출물은 `decks-out/` 에 넣는다(gitignore 처리돼 있다).
macOS·Linux 는 `python` 대신 `python3`.

```bash
# HTML — 회사명·로고·저작권을 넣어 한 파일로
python .claude/skills/blue-report/scripts/apply_brand.py --brand brand/hct/brand.json --deck internal --single-file -o decks-out/deck.html

# PDF — --notes 를 주면 발표자 노트를 마지막 장에 붙인다
python .claude/skills/blue-report/scripts/to_pdf.py decks-out/deck.html

# PowerPoint
node .claude/skills/blue-report/pptx/build.js --brand brand/hct/brand.json --out decks-out
```

`--deck` 은 이름(`catalog` · `internal` · `weekly` · `sales` · `project` · `training`) 또는 HTML 파일 경로를 받는다.

필요한 것(Pillow · Chromium · node_modules)은 스크립트가 스스로 받는다. 미리 설치하지 않아도 된다. 막으려면 `BLUE_REPORT_NO_INSTALL=1` 을 준다.

---

## 완료 조건

```bash
python .claude/skills/blue-report/scripts/check_deck.py decks-out/deck.html
```

11항목을 기계로 판정한다.

문체(금지 어미) · 파이 차트 금지 · 도넛 dasharray 검산 · 토큰 밖 raw hex · 슬라이드 크기 1920x1080 · 최소 글자 24px · 데이터 마크 대비 2:1 · **본문 영역 겹침** · 브랜드 마크 존재 · 마크와 본문 겹침 · 배경 밝기와 로고 변형 일치.

**실패가 0 이 아니면 완료가 아니다.** `주의`는 허용된다(도넛을 쓰지 않은 덱에서 나오는 정상 결과).

`--shots <폴더>` 를 붙이면 슬라이드별 PNG 를 남긴다. 겹침은 스크립트가 잡지만 어색한 여백은 잡지 못하므로 눈으로 한 번 본다.

### 템플릿 자체를 고쳤다면

덱 하나가 아니라 템플릿·스크립트·문서를 고쳤을 때는 저장소 전체를 본다.

```bash
python3 scripts/verify_repo.py            # 전부
python3 scripts/verify_repo.py --shots out  # 슬라이드 PNG 55장도 남긴다
```

덱 6종을 만들어 `check_deck.py` 로 판정하고, PPTX 5종 생성과 무결성 · `dist/` 재생성 대조 ·
한국어 인코딩 · 배포 매니페스트 · 내용 동기화 · 버전 올림을 함께 본다.
실패가 있으면 종료 코드가 1 이다.

**GitHub Actions 가 push·PR 마다 이 스크립트를 그대로 돌린다**(`.github/workflows/verify.yml`).
CI 와 로컬이 같은 한 줄을 쓰므로 결과가 갈라지지 않는다. 워크플로를 수동 실행할 때
`shots` 를 켜면 슬라이드 PNG 를 아티팩트로 내려받을 수 있다.

---

## 브랜드

`brand/hct/brand.json` 한 곳에서 회사명·로고·저작권을 관리한다.

로고는 **두 벌**이 필요하다. 마크가 모든 슬라이드 우측 상단에 들어가는데 배경이 딥네이비(`#071b45` · `#101827`)와 밝은 지면(`#f4f6f8`)을 오가므로 한 벌로는 반드시 한쪽에서 안 보인다.

| 항목 | 쓰이는 곳 | 파일 |
|---|---|---|
| `logo` | 표지 · 파트 간지 · 다크 요약 | `hct-logo-white.png` (흰색 녹아웃) |
| `logoOnLight` | 그 밖의 모든 본문 슬라이드 | `hct-logo-color.png` (원색) |

원본 한 장에서 두 벌을 뽑는 스크립트가 있다.

```bash
python .claude/skills/blue-report/scripts/make_logo_variants.py 로고.png --out-dir . --name mylogo
```

HCT 브랜드 파랑은 로고 원본에서 측정한 `#2f4a9c` 다. 밝은 지면 대비 7.51:1, 표지 `#071b45` 위에서는 2.06:1 이라 녹아웃이 필요하다.

**현재 로고 원본의 마크 영역은 264x86px 이다.** 화면용으로는 충분하지만 인쇄에는 모자란다. SVG 나 고해상도 원본이 생기면 교체한다.

---

## 규격서

`.claude/skills/blue-report/README.md` 가 자기완결 사양서다. 색값 · 타입 스케일 · 간격 · 차트 계산법 · 문체 규칙이 전부 들어 있어, 파일을 줄 수 없는 환경(웹 UI 등)에서는 이 문서를 통째로 붙여넣고 쓸 수 있다.

`.claude/skills/blue-report/references/rules.md` 는 같은 내용의 압축본이다.

---

## 구성

```
.claude-plugin/marketplace.json          플러그인 마켓플레이스 정의
.claude/skills/blue-report/
  SKILL.md                               스킬 트리거 정의
  README.md                              자기완결 사양서
  references/rules.md                    압축 규칙
  assets/blue-report.css                 토큰 68개 — 단일 소스
  assets/deck-*.html                     완성 덱 5종 + 레이아웃 카탈로그
  scripts/check_deck.py                  11항목 자동 점검
  scripts/apply_brand.py                 브랜드 일괄 적용
  scripts/to_pdf.py                      PDF 내보내기
  scripts/make_logo_variants.py          로고 두 벌 생성
  scripts/donut.py · palette.py          도넛 SVG · 대비 검증
  scripts/ensure_deps.py                 의존성 자동 확보
  pptx/                                  PowerPoint 생성기
brand/hct/                               회사 정보와 로고
docs/CODEX_DECK_PROMPT.md                Codex 등 외부 에이전트용 작업 지시서
scripts/verify_repo.py                   저장소 전체 점검 — CI 가 이것을 돌린다
scripts/check_content_sync.py            HTML 덱과 PPTX 내용 갈라짐 검사
CHANGELOG.md                             판올림 기록. 스킬을 고치면 여기에 적는다
scripts/install_blue_report_skill.py     오프라인 복사 설치기
.github/workflows/verify.yml             push·PR 자동 점검
```

`pptx/tokens.js` 가 `blue-report.css` 의 `--br-*` 를 파싱하므로 HTML 판과 PPTX 판의 색이 갈라질 수 없다.

내용은 그렇게 할 수 없어 `assets/deck-*.html` 과 `pptx/content.js` 두 곳에 따로 있다. HTML 이 기준이다. 두 곳을 합치지 않는 대신 `scripts/check_content_sync.py` 가 갈라짐을 잡고, CI 가 이것을 돌린다.

---

## 이력

이 저장소는 `dytc880915-commits/claude-workspace` 에서 분리해 나왔다. 그전 개발 이력은 그 저장소에 남아 있다.
