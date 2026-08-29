---
name: blue-report
description: "\"블루 리포트\" 스타일로 보고서·발표 덱·문서를 만든다. 별칭 \"AX 리포트 스타일\", \"딥 코발트 리포트\", \"Deep Cobalt\". 사용자가 슬라이드·덱·리포트·발표자료를 요청하면서 이 이름을 대거나, 사내 공용 발표 템플릿을 쓰라고 할 때 사용한다. 1920x1080 HTML 슬라이드, 코발트·딥네이비 팔레트, 도넛·막대 차트 규칙, 개조식 문체를 강제한다."
---

# 블루 리포트

사내 공용 발표 슬라이드 디자인 시스템. 색·타입·차트·문체 규칙이 서로 맞물려 있어 하나만
어겨도 덱 전체가 어색해진다. 아래 순서를 그대로 따른다.

## 1. 먼저 읽을 것

- `assets/blue-report.css` — 색·타입·간격 토큰과 파운데이션 클래스. **색은 여기 토큰으로만 쓴다.**
- `assets/deck-template.html` — 슬라이드 10종 완성본. 새 덱은 이 파일을 복사해서 시작한다.
- `references/rules.md` — 차트·문체·레이아웃 규칙 전문. 차트를 그리기 전에 반드시 읽는다.

## 2. 새 덱 만들기

**먼저 용도를 정한다.** `deck-template.html`은 레이아웃 카탈로그이지 완성 덱이 아니다.
아무거나 골라 쓰면 슬라이드 순서가 목적에 맞지 않는다.

판단 기준은 하나다 — **요청에서 용도가 읽히면 묻지 말고 고른다. 읽히지 않을 때만 묻는다.**

- 읽힐 때 → 고른 덱과 이유를 한 줄로 밝히고 바로 만든다. 뻔한 것을 되묻지 않는다.
  예: "주간 보고" · "월간 실적" · "팀 현황" → `internal`
  "제안서" · "고객사에 보낼" · "영업" · "견적" → `sales`
  "착수 보고" · "완료 보고" · "킥오프" · "산출물" → `project`
  "교육 자료" · "사내 강의" · "온보딩" · "설명 자료" → `training`
- 읽히지 않을 때 → **추천을 붙여서** 묻는다. 선택지만 나열하지 않는다.
  예: "사내 공유용이면 사내 보고, 외부에 보낼 거면 제안서 쪽이 맞다. 어느 쪽인가?"
- 내용을 받아 보니 고른 덱과 안 맞으면 → 그때 말하고 바꾼다. 말없이 다른 구성을 쓰지 않는다.

| 용도 | `--deck` | 파일 | 장수 |
|---|---|---|---|
| 사내 보고 (주간·월간) | `internal` | `deck-internal-report.html` | 9 |
| 외부 제안·영업 | `sales` | `deck-sales-proposal.html` | 10 |
| 프로젝트 착수·완료 | `project` | `deck-project-report.html` | 9 |
| 교육·기술 설명 | `training` | `deck-training.html` | 8 |
| 레이아웃 카탈로그 | `catalog` | `deck-template.html` | 12 |

```bash
# 회사 정보까지 한 번에 (권장)
python3 scripts/apply_brand.py --brand brand.json --deck internal --single-file -o 보고서.html

# 또는 파일을 직접 복사해 손으로 편집
cp assets/deck-internal-report.html <작업경로>/deck.html
cp assets/blue-report.css assets/deck-viewer.css assets/deck-viewer.js <작업경로>/
```

템플릿의 `<div class="br-frame">` 블록이 슬라이드 1장이다. 필요한 종류만 남기고 지우거나,
같은 블록을 복사해 늘린다. 12종은 다음과 같다.

| # | 슬라이드 | 배경 | 쓰는 자리 |
|---|---|---|---|
| 01 | 표지 | `--br-cover` | 문서 첫 장 |
| 02 | 목차 | `--br-page` | 파트 4~5개까지 |
| 03 | 파트 간지 | `--br-cover` | 파트 시작 |
| 04 | 핵심 정리 | `--br-dark` | 파트 끝. 카드 6개가 상한 |
| 05 | 단일 수치 강조 | `--br-page` | 한 슬라이드 = 한 주장 |
| 06 | 도넛 차트 | `--br-page` | 구성비 3~5구간 |
| 07 | 막대 차트 | `--br-page` | 순위·비교 7구간까지 |
| 08 | 비교 2열 | `--br-page` | 전후·A안B안·평균대비 |
| 09 | 지표 표 | `--br-page` | 과제·지표 목록. 행 7개가 상한 |
| 10 | 3단계 로드맵 | `--br-page` | 실행 계획 |
| 11 | 일정 타임라인 | `--br-page` | 기간 병행과 마일스톤 |
| 12 | 마무리 CTA | `--br-cover` | 행동 하나만 제시 |

**쪽번호와 문서명은 뷰어가 자동으로 채운다.** 푸터(`.br-footer`)는 비워 두고 숫자를 적지 않는다.
문서명은 `#stage`의 `data-deck-title` 한 곳에서 읽는다. 발표자 노트는 `.br-frame`의
`data-notes` 속성에 적고 뷰어에서 `N` 키로 본다.

## 3. 차트는 반드시 스크립트로 만든다

각도를 손으로 적으면 수치와 그림이 어긋난다.

```bash
# 도넛 — 구간 퍼센트를 넘기면 SVG와 범례가 나온다
python3 scripts/donut.py --r 110 --w 48 --labels "일상 사용,주 1~2회,미사용" 58.4 27.9 13.7

# 막대 구간이 6개 이상이면 대비를 만족하는 램프를 생성한다
python3 scripts/palette.py --steps 7

# 팔레트 대비표
python3 scripts/palette.py --check
```

## 4. PDF로 내보내기

사내 배포·이메일 첨부에는 PDF를 만든다. 슬라이드 1장이 1페이지, 20in x 11.25in(16:9)이며
텍스트가 실제 글자로 남는다.

```bash
python3 scripts/to_pdf.py 보고서.html -o 보고서.pdf --notes
```

## 5. PowerPoint 판이 필요하면

파워포인트로 직접 편집해야 하는 사람이 있을 때만 만든다. 기본은 HTML 이다.

```bash
node pptx/build.js --brand <brand.json> --out <폴더> [--deck internal]
```

**설치를 사용자에게 시키지 않는다.** 스크립트가 실행될 때 없는 것만 골라 스스로 받는다
(Pillow · Playwright · Chromium · pptxgenjs). "먼저 npm install 하세요" 같은 안내를 하지 않는다.
자동 설치를 막으려면 `BLUE_REPORT_NO_INSTALL=1` 을 준다. 상태만 보려면
`python3 scripts/ensure_deps.py`.

색·크기는 `blue-report.css` 토큰을 읽는다. 애니메이션은 없고, 폰트는 맑은 고딕·Arial 로 내린다.
도넛과 막대는 PowerPoint 네이티브 차트라 값을 직접 고칠 수 있다.
덱 내용은 `pptx/content.js` 에 있으며 HTML 덱과 함께 고친다.

만든 뒤에는 반드시 검증한다.

```bash
python3 <pptx 스킬>/scripts/office/validate.py 결과.pptx
```

## 6. 만들고 나면 반드시 점검한다

```bash
python3 scripts/check_deck.py <작업경로>/deck.html --shots out/
```

10개 항목(개조식 문체, 파이 금지, 토큰 밖 raw hex, 슬라이드 크기 1920x1080, 24px 하한,
데이터 대비 2:1, 브랜드 마크 존재, 마크와 본문 겹침, 로고 변형과 배경 밝기, 도넛 검산)을
검사하고 슬라이드별 PNG를 남긴다.

**`실패`가 0이 아니면 완료가 아니다.** `주의`는 허용된다 — 도넛을 쓰지 않은 덱에서
도넛 검산 항목이 `주의`로 나오는 것이 정상이다.
**실패가 0이어도 PNG를 눈으로 확인한다.** 겹침과 어색한 여백은 스크립트가 잡지 못한다.

## 7. 절대 어기지 않을 것

- 배경은 밝은 지면 `#f4f6f8` 1개 + 다크면 `#071b45`(표지·간지), `#101827`(핵심 정리) 2개까지. 그 외 장식색 금지.
- 파이 차트 금지. 도넛만. 손으로 적은 `<path d="M…A…">` 금지.
- 밝은 지면의 데이터 마크에 `--br-soft-*`를 쓰지 않는다. 대비 2:1에 미달한다.
- 24px 미만 텍스트 금지. 예외는 `%` 첨자(`.br-sup`)뿐.
- "~합니다 / ~습니다 / ~해요" 금지. 개조식·명사형. 설문 문항 원문만 예외.
- 제목 밑줄, 장식용 색 띠, 블루프린트 `+` 코너 마크를 쓰지 않는다.

## 8. 회사 정보와 로고

회사명·연락처·저작권·로고는 손으로 고치지 않는다. `brand.json`에 적고 스크립트로 적용한다.

```bash
cp assets/brand.example.json ./brand.json     # 편집 후
python3 scripts/apply_brand.py --brand ./brand.json --single-file -o ./deck.html
```

- **마크는 모든 슬라이드 우측 상단**에 같은 자리로 들어간다(`.br-mark`). 표지도 본문도 같다.
  우측 상단 여백 띠에 콘텐츠를 붙이지 않는다.
- **로고는 두 벌이 필요하다.** 배경이 오가므로 한 벌로는 한쪽에서 안 보인다.
  `logo`는 다크·코발트 배경용 흰색 녹아웃, `logoOnLight`는 밝은 지면용 원색이다.
  `python3 scripts/make_logo_variants.py 로고.png --name mylogo` 가 원본 한 장에서
  `mylogo-white.png`(→ `logo`)와 `mylogo-color.png`(→ `logoOnLight`)를 만든다.
- `logoHeight`는 마크 높이(px). 기본 40, 권장 32~48. 키우면 본문과 겹쳐 검사가 실패한다.
- 로고는 PNG·JPG·SVG·WEBP를 data URI로 박는다. 완성 HTML 하나만 들고 다니면 된다.
- 연락처가 없으면 `email`·`website`·`phone`을 빈 문자열로 둔다. 해당 줄이 통째로 사라진다.
- `logo`·`logoOnLight`가 `null`이면 `wordmark` 텍스트가 들어간다. 한글이면 폰트를
  Noto Sans KR로 바꾸고, 색은 배경에 맞춰 밝은 면 브랜드 파랑·어두운 면 흰색으로 전환한다.
- 항상 원본 템플릿에서 새로 만들므로 몇 번 실행해도 결과가 같다.

사내 폰트가 확정되면 `blue-report.css`의 `--br-font-kr`, `--br-font-num`, `--br-font-label`
첫 패밀리만 교체한다.

## 9. 다른 프로젝트에서 쓰기

이 스킬이 저장소 안에 있으면 그 저장소에서만 로드된다. 모든 프로젝트에서 쓰려면 한 번 설치한다.

GitHub 플러그인으로 받는 것이 기본이다. 저장소를 클론하지 않아도 되고 갱신이 자동이다.
새 PC 에서 하는 일은 아래 한 줄이 전부다.

```bash
claude plugin marketplace add dytc880915-commits/hct-report-template && \
claude plugin install blue-report@hct-tools
```

설정 파일(`extraKnownMarketplaces` · `enabledPlugins`)에 적어 두는 것만으로는 설치되지 않는다.
`install` 은 PC 마다 한 번 실행해야 한다.

GitHub 에 접근할 수 없으면 파일 복사로 설치한다.

```bash
python3 <저장소>/scripts/install_blue_report_skill.py --dry-run   # 바뀔 내용 확인
python3 <저장소>/scripts/install_blue_report_skill.py             # ~/.claude/skills/ 로 설치
```

어느 쪽이든 설치 후 Claude Code 세션을 새로 시작해야 읽힌다.
