# hct-report-template 프로젝트 지침

## 목적

주식회사 에이치시티 사내 공용 발표 슬라이드 디자인 시스템이다. 한 소스에서 HTML·PDF·PowerPoint 를 만들고, 규칙을 스크립트가 판정한다.

## 시작 순서

1. `HANDOFF.md` 에서 저장소 사정을 확인한다. 뿌리가 다른 두 계통이 들어 있고 기본
   브랜치가 `main` 이 아니라 `full/main` 이다. 브랜치를 합치거나 지우려면 승인을 받는다.
2. `README.md` 에서 쓰는 법과 구성을 확인한다.
3. `.claude/skills/blue-report/README.md` 를 전부 읽는다. 이것이 규격서다.
4. 압축본이 필요하면 `.claude/skills/blue-report/references/rules.md` 를 본다.
5. Claude Code 가 아닌 에이전트에게 시킬 때는 `docs/CODEX_DECK_PROMPT.md` 를 지목한다.
6. 공개본(`hctinno/blue-report`)을 갱신하려면 `public/README.md` 를 본다.
   손으로 옮기지 않는다 — `scripts/build_public_release.py` 가 한다.

## 작업 방식

- 답변과 문서는 한국어로 작성한다. 기술 용어, 코드 식별자, 파일 경로, 명령어는 원문을 유지한다.
- 서브에이전트를 실행할 때는 프롬프트에 "보고는 한국어로 작성한다"를 명시한다.
- **새 보고서는 본문만 쓰고 빌드가 틀을 씌운다.** `deck.yaml`(표지 정보 · 장 순서 · 장 id · 마무리 · 부록) +
  `slides.html`(장마다 `<section id>` 본문만) → `scripts/build_deck.py <deck.yaml> --brand brand/hct/brand.json
  --single-file -o decks-out/…`. 머리띠·꼬리띠·쪽번호·로고·워터마크·폰트·진행선·발표 기능, 표지·목차·장 간지·
  마무리·부록 간지는 빌드가 만든다 — 직접 쓰지 않는다. 견본은 `examples/standard/` · `examples/showcase/`.
  라이브러리 장은 `catalog:<id>` · `patterns:<id>` 로 부른다. 기준 덱 `live-standard.html` 을 복사하는 옛 방식은
  예비로만 쓴다. 고르는 양식은 넷이다 — 기준 덱(`standard`) · 부품 카탈로그(`livecatalog`) · 회의록(`minutes`) ·
  관리보드(`manage`). 그 밖은 `assets/archive/` 에 보관했다 — 사용자가 이름을 짚거나 PowerPoint 파일이 꼭
  필요할 때만 쓴다.
- **발표 덱은 `.claude/skills/blue-report/DESIGN.md`(본문 스타일 한 장)를 먼저 읽고 그 규칙으로 짠다.**
  일하는 방식 · 본문 파일 형식 · 조립 목록 · 위계 · 내용별 그릴 것 · 색 역할 · 금지가 이 한 장에 있다.
  시각 스타일은 둘 — A 프레임형(기본) · C 혼합형(권장). 조립 목록 `style:` 한 줄로 고르고 본문 HTML 은
  같다(`DESIGN.md` 「2-1」 · `assets/blue-style.css`). 맞춤 CSS 를 스타일 이름으로 갈라 짜지 않는다 — 역할 토큰으로 짠다.
  장 짜임은 `LAYOUTS.md`(짜임 카드 12종), 부품 규격은 `COMPONENTS.md`(부품 카드 20종)에서 고른다 — 둘 다
  `scripts/build_cards.py` 가 원본에서 만드는 생성 파일이라 손으로 고치지 않는다(`verify_repo.py` 가 어긋남을 잡는다).
  관리보드는 HCT 웹 디자인 템플릿 v2.1.0(`hct-*` 부품)으로 짜고, 실제로 동작하는 웹 앱은 그 템플릿을 직접 쓴다. 움직임은 절제 —
  효과는 사용자가 요청할 때만 `.claude/skills/blue-report/MOTION.md`(효과 라이브러리)에서 고른다
  (`check_live.py` 30번 — 장마다 등장 3종 · 반복 2종 넘으면 주의).
- **고정 영역과 자유 영역을 나눈다.** 머리띠·꼬리띠·쪽번호·로고·워터마크·진행선·제목 형광 밴드·
  조작판·발표 엔진은 빌드가 다는 그대로 둔다. 본문(`.bl-bd` 안 제목 아래)은 **내용에 맞게 짠다** — 카탈로그
  부품을 그대로 쓰거나 고쳐 쓰고, 맞는 것이 없으면 장 안 `<style data-own>` 으로 새 도식·레이아웃·
  애니메이션을 만든다. 규칙은 스킬 README 「6-3 · 본문 맞춤 디자인」, 판정은 `check_live.py` 28번.
- 표·목록만으로 장을 채우지 않는다. 흐름·일정·비교·구성·수치·구조는 그림으로 그린다
  (`check_live.py` 29번이 글·표뿐인 장이 내용 장의 절반을 넘으면 주의를 낸다).
- 보관한 고정 지면 덱·A4 문서·웹 보드는 지금처럼 견본을 복사해 내용만 바꾼다.
- 덱 내용은 `assets/archive/deck-*.html` 과 `pptx/content.js` 두 곳에 있다. HTML 이 기준이며 고칠 때 두 곳을 함께 고친다. 합치지 않기로 했고, 갈라짐은 `scripts/check_content_sync.py` 가 잡는다.
- 용도가 분명하지 않으면 임의로 고르지 말고 사용자에게 먼저 묻는다.
- 예시 수치·부서명·문구는 자리표시자가 아니라 사용법 견본이다. 실제 내용으로 바꾼다.
- **산출물은 반드시 `apply_brand.py` 를 거친다.** `assets/` 의 견본은 로고 자리가
  「COMPANY NAME」으로 비어 있다 — 복사해 내용만 바꾸고 끝내면 회사 로고도 워터마크도
  없는 덱이 나온다. `--single-file` 을 붙이면 CSS·폰트·로고가 한 파일에 박힌다.
  안 붙이면 스크립트가 CSS · 뷰어 JS · `fonts/` 를 결과물 옆에 같이 복사한다 — CSS 를 떼어
  옮기면 지면이 통째로 Times New Roman 이 되고, JS 를 떼어 옮기면 넘김 · 발표 기능이 죽는다.
- **본문 디자인 기준은 사내 발표 덱 최종본의 디자인 언어다** — 문법은 `.claude/skills/blue-report/references/design-language.md`,
  용례는 패턴첩 `assets/live-patterns.html`(`--deck patterns`, 63장 · 내용은 가상). **베끼지 않는다** — 보고서 내용을
  먼저 보고 그 문법(색 역할 · 위계 · 배치 · 연출)으로 내용에 맞게 짠다. 맞는 용례는 가져와 고쳐 쓰고, 없으면 문법을
  빌려 `<style data-own>` 으로 새로 짠다(색 `--bl-pt-*`). 덱 머리에 `blue-pattern.css` 를 더한다(누락은 `check_live.py` 가 실패로 잡는다).
  고정 영역(머리띠 · 꼬리띠 · 로고 · 워터마크 · 진행선 · 발표 기능)은 그대로다.
- 부품은 `assets/live-catalog.html`(`--deck livecatalog`)에서 찾는다 — 장째 복사해도, 고쳐 써도,
  참고만 해도 된다. 계통 이름(`bl-`·`br-`)은 새로 짓지 않는다 — 맞춤 클래스는 `x-` 같은 다른 접두어로
  짓는다. 색인은 `.claude/skills/blue-report/README.md` 「6-3. 라이브 덱」.
- 완료라고 말하기 전에 `check_deck.py` 를 돌리고 결과를 제시한다. 실패가 0 이 아니면 완료가 아니다.
- 템플릿·스크립트·문서를 고쳤으면 `python3 scripts/verify_repo.py` 를 돌린다. CI 가 push·PR 마다 같은 것을 돌리므로 여기서 통과하지 않으면 CI 도 빨간불이다.
- `assets/` 를 고쳤으면 `dist/` 를 다시 만들어 함께 커밋한다. `build_single_file.py` 를 세 번 돌린다 — 인자 없이 한 번, `--artifact --brand brand/hct/brand.json` 으로 한 번, 거기에 `--deck minutes` 를 더해 한 번(A4 문서)이다.
- 자동 점검이 못 잡는 여백과 균형은 `--shots` 로 남긴 PNG 를 눈으로 확인한다.
- 공개본에 나갈 판올림이면 `public/VERSION` 과 `public/overlay/CHANGELOG.md` 를 함께 올린다.
  `python3 scripts/build_public_release.py --out /tmp/pub` 로 확인한 뒤 `--commit --push` 한다.

## 어길 수 없는 규칙

- 색은 `--br-*` CSS 변수만 쓴다. 새 hex 를 슬라이드에 직접 적지 않는다. 맞춤 CSS 도 같다 —
  hex·`rgb()`·색 이름 금지, 치수는 `rem`. 글꼴·모서리·그림자·움직임 곡선도 토큰만
  (`--br-font-*`·`--bl-r-*`·`--bl-shadow*`·`--bl-ease*`), 움직임 길이 0.15~2.4초.
- 파이 차트 금지. 도넛만 쓰고 `scripts/donut.py` 로 생성한다. 각도를 손으로 계산하지 않는다.
- 문체는 개조식(명사형 종결). 슬라이드 본문에 `~합니다` 같은 존댓말도, `~한다`·`~없다` 같은 평서형도 쓰지 않는다. 발표자 노트는 예외로 `~한다` 형을 쓴다.
- 슬라이드는 정확히 1920x1080. 글자는 24px 이상(`%` 첨자만 예외).
- 데이터 마크는 배경 대비 2:1 이상. 밝은 지면에 `--br-soft-*` 를 쓰지 않는다.
- 브랜드 마크는 모든 슬라이드 우측 상단. 그 여백 띠에 본문을 붙이지 않는다.
- 기준·라이브 덱은 장마다 머리띠·꼬리띠·쪽번호·로고·워터마크를 단다. `check_live.py` 가 강제한다.
  네 검사기 모두 자리표시자가 남은 산출물과 스타일·폰트가 안 붙은 산출물을 실패로 잡는다.
  머리띠 마크의 `data-on` 은 지면과 **반대**다 — 마크가 앉는 곳은 지면이 아니라 띠이기 때문이다.

## 산출물

- `decks-out/` 에 넣는다. gitignore 처리돼 있다.
- 저장소 루트에 결과 파일을 흩어 놓지 않는다.

## 안전 기준

- 기본 작업 범위는 이 저장소의 체크아웃 루트다. 저장소 밖 경로는 사용자가 명시적으로 범위를 넓힌 경우에만 변경한다.
- 키, 토큰, 비밀번호, 쿠키를 저장소에 기록하거나 출력하지 않는다.
- 삭제, 덮어쓰기, 강제 푸시 전 정확한 대상과 복구 방법을 확인한다.
- 사용자가 요청하지 않은 커밋·푸시·브랜치 삭제는 하지 않는다.
- **공개본 push 는 되돌릴 수 없다.** `build_public_release.py` 의 유출 검사가 실패하면
  원인을 없애기 전에는 `--push` 를 쓰지 않는다. 검사를 끄는 선택지는 두지 않았다.

## 한국어 인코딩

UTF-8 로 저장하고 `???`, `濡`, `湲`, `遺`, `媛`, `李` 패턴을 검사한다.
