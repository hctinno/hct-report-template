# A4 문서 양식 정의 (`forms/`)

A4 문서(회의록 · 사내 보고서 · 규정 · 매뉴얼 · 공지)의 **양식 값과 짜임 선택은 이 폴더의 JSON 에만 있다.**
HTML · PDF 와 Word 가 같은 파일을 읽으므로 둘이 갈라지지 않는다.

```
forms/<id>.json ──┬─ scripts/build_form.py ─→ assets/blue-doc.css 생성 블록(--bd-* 변수 + 고른 짜임의 규칙) ─→ HTML · PDF
                  │                            └ doc-viewer.js 가 머리말 짜임 · 장 번호 · 표지 · 쪽 흘림을 읽는다
                  └─ scripts/doc_to_docx.py(기본값을 채워 넘김) ─→ docx/from_doc.js ─────────────────────→ Word
```

## 양식 목록

| id | 이름 | 쓰는 곳 |
|---|---|---|
| `hct-official` | **HCT 공식 문서** — 회사 규정 · 강령 원본(윤리강령)을 잰 양식. **기본** | 사내 A4 문서 전부 (`data-form` 없는 문서) |
| `hct-standard` | 블루 리포트 표준 A4 — 프리텐다드 · 남색 장 제목 막대 · 쪽번호 꼬리말 | FCC/KC 대외 보고서(`data-form="hct-standard"`) · 원하는 문서 |

기본 양식은 `blue-doc.css` 의 `:root` 에, 나머지는 `.bd-doc[data-form="<id>"]` 범위에 들어간다. 문서 하나만 다른 양식으로 내려면
`<div class="bd-doc" data-form="hct-standard" …>`. Word 도 그 값을 따른다(`doc_to_docx.py` 가 `data-form` → 묶은 HTML 의 기본 양식 순으로 본다).
지금 기본 양식은 `hct.py form` 으로 본다. `_test/` 의 양식은 검사용이다.

## 바꾸는 법

1. 고칠 양식 JSON 을 고치거나, 비슷한 것을 복사해 `forms/<id>.json` 을 만들고 `id` · `name` 을 고친다.
2. 색은 hex 가 아니라 `assets/blue-report.css` 토큰 이름(`--br-` 뒤 — `navy` · `text-2` · `form-band` …), 선을 없애려면 `"none"`.
   길이는 단위를 붙인다 — `px` · `pt` · `mm`(지면 794px = 210mm). 글자 간격은 `em`, 막대 폭은 `%`.
   회사 양식에만 있는 색은 먼저 `blue-report.css` 의 「회사 공식 문서 양식」 토큰으로 더한다.
3. `python3 scripts/build_form.py` — 양식을 모두 검사하고 `blue-doc.css` 를 다시 쓴다. 기본 양식을 바꾸려면
   `python3 scripts/hct.py form --use forms/<id>.json`.
4. `python3 scripts/verify_repo.py`(저장소 루트) — 견본 5종의 HTML 검사 · Word 변환 · Word 검사가 다시 돈다.

생성 블록(`/* <form …> */ … /* </form> */`)은 손으로 고치지 않는다 — `build_form.py --check` 가 잡는다.

## 항목

빠진 항목은 기본값(`build_form.py` 의 `DEFAULTS` — 표준 양식 모양)을 쓴다.

| 항목 | 정하는 것 |
|---|---|
| `page.size` · `page.margin` | 지면(A4) · 여백 위 · 오른 · 아래 · 왼(머리말은 위 여백에서 시작) |
| `page.breaks` | `authored` — 원본의 쪽(`.bd-page`) 그대로(넘치면 검사 실패) · `flow` — HTML · Word 모두 이어 흘려 쪽을 저절로 나눈다(장 · 절 제목이 쪽 끝에 홀로 남지 않게, 결재란은 마지막 쪽) |
| `font.body` · `font.heading` | `web`(HTML · PDF) — `sans`(내장 Pretendard) · `serif`(내장 Noto Serif KR), `word` — Word 에 적을 글꼴 이름 |
| `type.title` · `subtitle` · `h1` · `h2` · `body` · `small` · `key` | 크기 · 굵기 · 색 · 글꼴(`font`: body · heading) · 정렬(표제 left · center, 본문 left · justify) · 행간 |
| `type.h1.style` | `bar` — 왼쪽 굵은 막대(`h1.bar`) · `box` — 위아래 선 상자 + 번호 칸(`h1.box`: 번호 칸 폭 · 바탕 · 선 · 높이) |
| `type.h1.numeral` | `keep` — 쓴 그대로 · `roman` — 「1. 요약」을 「Ⅰ」로(본문에는 1. 2. 로 쓴다) |
| `space` | 제목 · 문단 · 목록 · 표 뒤 간격, `indent` — 절 제목 · 문단 · 목록 · 절차 · 목차 들여쓰기 |
| `list` | 글머리 표시(`marker`) · 글 시작(`textIndent`) · 표시와 글 사이(`hang`) |
| `numbering` | 규정 호 번호(`legal`: `({n})` · `circled` ①②) · 절차 번호(`steps`: `decimalEnclosedCircle` · `decimal`) |
| `header` | `layout`(`split` 좌우 · `logo-title` 로고 + 가운데 문서명) · 왼쪽 · 오른쪽 항목 · 문서명 크기 · 글자 간격(`spaceUpTo` 글자까지만 넓게) · 위아래 띠(`bands`) · 선 · 간격 · 로고 높이 |
| `footer` | 왼쪽 · 오른쪽 글 틀 — `{company}` `{title}` `{docNo}` `{page}` `{pages}`. 둘 다 비우면 꼬리말 없음 |
| `meta` · `table` · `box` · `sign` | 문서 정보 표 · 표 · 상자 모서리 · 결재란(기본 칸 — `hct.py new` 가 찍는다) |
| `toc` | `leader` — 점선 · 쪽번호 · `plain` — 쪽번호 없이(장 줄 굵은 제목 글꼴) |
| `cover` | `mode`(`off` · `opt-in` — `data-doc-cover="yes"` 문서만 · `always`) · 문서명 크기 · 글자 간격 · 밑 막대 · 회사명(`text`, `{company}`) |

검사(`build_form.py`)가 막는 것 — hex 색 · 없는 토큰 · 단위 없는 길이 · 본문 10.5pt 미만 · 보조 9pt 미만 · 모르는 선택지 값 ·
모르는 머리말 항목 · 모르는 꼬리말 자리표시자.

## `hct-official` 의 근거

윤리강령 원본 11쪽(A4 150dpi 이미지)에서 잰 값이다. 머리말 띠(위 파랑 1.6mm · 아래 노랑 0.8mm + 파랑 1.4mm) · 로고 높이 10mm ·
가운데 문서명 16pt 굵게 넓은 간격 · 본문 명조 12pt 행간 약 175% 양쪽 정렬 · 여백 왼 20mm 오른 10mm · 장 제목 상자(높이 10.6mm,
번호 칸 10mm 청록 바탕, 위아래 1pt 선) · 「1. 항목」 5mm 들여씀 · 「- 세부」 9.5mm, 이어지는 줄 14mm · ①② 번호 · 꼬리말 없음 ·
표지(문서명 · 둥근 파란 막대 · (주)에이치시티). 원본에 없는 부품(문서 정보 표 · 표 · 결재란 · 수치 타일)은 같은 선 · 청록 바탕으로 맞췄다.

HTML · PDF 의 명조는 Noto Serif KR(SIL OFL, `scripts/make_serif_subset.py` 로 KS X 1001 범위만), Word 는 「바탕」 · 「맑은 고딕」이다.
바탕은 재배포할 수 없어 HTML 에 넣지 않는다 — 두 판의 글자 모양이 조금 다르다.

## 아직 양식으로 못 바꾸는 것

결재란 **위치**(마지막 쪽 아래 고정), 표제 블록 **구성**(제목 · 부제 · 문서 정보 표), 문체 규칙(검사기는 개조식을 본다 — 규정 · 강령의
「~한다」 조문체는 지금 「문체 위반」으로 걸린다)은 틀이 정한다. 다른 짜임이 필요하면 틀에 선택지를 더해 JSON 으로 고르게 한다.
