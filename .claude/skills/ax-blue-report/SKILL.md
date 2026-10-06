---
name: ax-blue-report
description: "AX_BLUE_REPORT_V1 — 경영진 보고용 인터랙티브 HTML 발표 덱 디자인 시스템. \"AX_BLUE_REPORT_V1\", \"AX 블루 리포트 V1\", \"AX 블루 리포트\", \"ax-blue-report\" 로 부르면 이 스킬을 쓴다(그냥 \"블루 리포트\" · \"AX 리포트 스타일\" 은 blue-report 스킬이다). 견본 덱 56장(표지 · INDEX · 보고 요지 · 장 표지 · 시장 카드 · 연표 · 벤치마킹 표 · 1:1 비교 · 조직도 · 절차 · 마일스톤 · 역할 매트릭스 · 코칭 데모 · 파이프라인 · 두 화면 전환 · 간트 · 투자 기준 · 결정 요청 · Q&A · 부록 도해 18종)을 골라 글자만 바꿔 쓴다. 남색 머리띠 · 로고 · 워터마크 · 제목 형광 밴드 · Pretendard, 클릭 단계 전개 · 등장 애니메이션 · 출처 핀과 근거 창 · 지금 원문 보기 겹창 · 영상 창 · 탭 전환 · 발표 모드(F) · 레이저(L) · 대본 창(P) · 메모(N) · 숫자 점프를 그대로 쓴다. 한 파일 HTML · 발표 전용 HTML · Artifact 판 · 링크와 책갈피가 붙은 PDF · PDF 뷰어 · 대본 txt 로 낸다."
---

# AX_BLUE_REPORT_V1

경영진 보고 덱을 **완성된 장 56종에서 골라 글자만 바꿔** 만든다. 모양 · 움직임 · 발표 기능은 엔진이
가지고 있으므로 새로 짜지 않는다. 경로는 이 `SKILL.md` 가 있는 폴더 기준이다.

> blue-report 스킬과 **다른 계통**이다. `--br-*` 토큰 · 24px 하한 · `check_deck.py` 는 여기 해당하지 않고,
> 이 스킬의 규칙과 `scripts/check_ax.py` 를 따른다. 두 계통의 부품을 섞지 않는다.

## 1. 먼저 읽을 것

- `README.md` — 규격서. 장 해부도 · 56종 목록(언제 쓰는가) · 기능 · 명령 · 점검 항목.
- `dist/ax-blue-report-gallery.html` — 견본 덱 완성본. 브라우저로 열어 `E`(펼침)로 훑는다.
- `slides/` — 장 파일 56개. 고칠 대상은 이것뿐이다. `core/` 는 엔진이라 고치지 않는다.

## 2. 덱 만들기 — 순서 그대로

1. **장 고르기.** 요청 내용을 장 단위로 나누고 `README.md` 「장 목록」에서 맞는 모양을 고른다.
   요청에서 구성이 읽히면 묻지 말고 고른다. 읽히지 않으면 추천 구성을 붙여 한 번 묻는다.
   기본 뼈대: 표지 → INDEX → 보고 요지 → (장 표지 → 본문 장들) × 장 수 → 결정 요청 → 맺음 → 부록 간지 → Q&A · 근거 부록.
2. **뼈대 복사.** 작업 폴더는 `decks-out/<덱이름>/` (저장소에서는 gitignore 대상).

   ```bash
   python3 scripts/new_deck.py --catalog                       # 고를 수 있는 장
   python3 scripts/new_deck.py decks-out/q3/src --pick cover index exec-summary chapter-1 market-cards \
       compare-1to1 decision-request closing appendix qa-1 --blank-notes
   ```
3. **글자 바꾸기.** 복사된 장 파일에서 **글자 · 숫자만** 바꾼다. 태그 · class · id · `data-f` · `style` 좌표는 둔다.
   막대는 화면 숫자와 인라인 값 변수(`style="--a:15.3;--b:16.0"` · `--v:60` 처럼 값을 받는 것)를 함께 고친다.
   `--d`(등장 지연) · `--i`(순번) · `--c`(색)는 값이 아니므로 둔다. 손으로 그린 SVG 는 좌표까지 고친다. 아래 4절 규칙을 지킨다.
4. **빌드.**

   ```bash
   python3 scripts/build_deck.py --list decks-out/q3/src/list.txt --title "3분기 AX 추진계획(안)" -o decks-out/q3/deck.html
   ```
   장 제목 번호(`data-t`)와 바닥줄 문서명은 빌더가 실제 순서와 `--title` 로 다시 매긴다.
5. **점검 — 실패 0 이 완료 조건.**

   ```bash
   python3 scripts/check_ax.py decks-out/q3/deck.html            # 정적 + 실행 검사
   node scripts/shots.js decks-out/q3/deck.html decks-out/q3/shots --sheet   # 눈 확인용 PNG
   ```
   `shots/sheet-*.png` 를 열어 넘침 · 겹침 · 어색한 여백을 눈으로 본다. 검사기가 못 잡는 것이 있다.
6. **필요한 판 내기.**

   ```bash
   python3 scripts/build_deck.py --list … --present  -o decks-out/q3/deck-present.html   # 대본 없이 처음부터 발표 모드
   python3 scripts/build_deck.py --list … --artifact -o decks-out/q3/deck-artifact.html  # Claude Artifact 게시용(껍데기 없음)
   python3 scripts/make_pdf.py decks-out/q3/deck.html -o decks-out/q3/deck.pdf            # 링크 · 책갈피 · 쪽 이름
   python3 scripts/make_pdf_viewer.py decks-out/q3/deck.pdf -o decks-out/q3/deck-pdf.html [--artifact]
   python3 scripts/export_script.py decks-out/q3/deck.html -o decks-out/q3/script.txt      # 발표 대본
   ```

## 3. 쓰는 기능 — 엔진이 이미 한다

| 키 · 표시 | 동작 |
|---|---|
| `→` `Space` / `←` | 다음 · 이전 단계(단계가 끝나면 다음 장) |
| `E` | 클릭 단계 모두 펼침(검토 모드 · 처음 열면 펼침) |
| `F` (또는 F11) | 발표 모드 · 전체 화면 · 조작판 숨김 · 레이저 자동 · 대본 창 자동 |
| `H` · `N` · `P` · `L` | 가로/세로 스냅 · 발표자 메모 · 대본 창 · 레이저 |
| 숫자 + `Enter` / `A` + 숫자 + `Enter` | 본문 · 부록 쪽으로 이동 |
| `?` | 조작 안내 |
| 「출처」 핀(`.ev-pin`) | 근거 창 — 등급 · 사실 · 출처 · 캡처 확대 · 강조 상자 |
| 「지금 원문 보기」(`[data-now-source]`) | 다른 장(주로 부록)을 겹창으로 띄움 |
| 영상 · 원문 문서 버튼 | 영상 창 · 문서 전체보기 창 |
| 탭(`[role=tab][data-v]`) | 한 장에서 두 화면 전환 |

## 4. 글자 규칙 — 어기면 점검이 실패하거나 덱이 어색해진다

- **화면 글자는 개조식(명사형 종결).** 「~합니다 · ~한다 · ~없다」로 끝내지 않는다. 대본만 존댓말.
- **제목의 핵심 구절은 `<em>` 안에.** 형광 밴드가 거기에만 그려진다(`<h2>앞 — <em>핵심</em></h2>`).
- **`data-t` 형식**: 본문 `"NN 제목"` · 장 표지 `"NN 장 제목"` · 부록 `"부록 NN · 제목"` · 간지 `"부록"` · 표지 `"표지"`.
  번호는 빌더가 다시 매기므로 순서만 맞으면 된다.
- **대본(`data-notes`)**: 존댓말 2~4문장 → `[클릭]` → 클릭 뒤 말 … → `→ 전환: …` → `※ 질문 대비 …`.
  **`[클릭]` 개수 = 그 장의 단계 수**(`.fr[data-f]` 의 서로 다른 값 개수). 점검이 센다.
- **길이는 견본과 비슷하게.** 칸이 고정이라 길어지면 넘친다. 늘려야 하면 문장을 쪼개지 말고 줄인다.
- **id 를 바꾸지 않는다.** 장의 모양이 `#deck #<id>` 에 매여 있다. 같은 장을 두 번 쓰면 모양은 같고 JS 동작은 첫 장에만 붙는다.
- **부록 장은 `class` 에 `apx`**, 부록 간지는 `id="appendix"`. 간지 뒤에 본문 장을 두지 않는다.
- **출처 핀**은 `data-ev="E07"` 코드가 `core/data/evidence.json` 의 `ev` 에 있어야 근거 창이 열린다.
  실제 덱에서는 근거를 새로 적고(등급 A 1차 공식 · B 학술 · C 언론 · R 직접 집계), 캡처는 `core/media/` 에 넣는다.
- **견본 수치 · 회사명(「샘플테크」) · 인물은 전부 가상**이다. 자리표시자가 아니라 사용법 견본 — 실제 내용으로 바꾼다.

## 5. 이미지 · 로고

- 장 안 이미지는 `src="axbr-media:파일.webp"` 처럼 적고 파일을 `core/media/` 에 둔다. 빌더가 data URI 로 넣는다.
  작업 폴더 밖의 그림이면 data URI 를 직접 적어도 된다.
- 로고 · 워터마크는 브랜드 묶음 `brand/hct/` 의 5벌(`logo-color` · `logo-white` · `watermark-light` · `watermark-dark` · `symbol`).
  다른 회사 로고를 쓰려면 같은 이름 5벌을 담은 폴더를 만들어 `--brand <폴더>` 로 준다. 장 파일은 고치지 않는다.

## 6. 완료 보고

실행한 명령, `check_ax.py` 의 결과 줄(`결과: 장 N · 실패 0 · 주의 M`), 산출물 경로, 눈으로 본 PNG 를 적는다.
점검을 돌리지 않았으면 그렇다고 쓴다. 필요한 도구: Python 3(`pip install fonttools brotli pypdf pillow`) ·
Node + Playwright(`npm i -D playwright && npx playwright install chromium`) · PDF 뷰어는 poppler(`pdftoppm`).
