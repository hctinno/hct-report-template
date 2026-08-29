# 변경 이력

블루 리포트 발표 템플릿의 판올림 기록이다. 버전은
`.claude/skills/blue-report/.claude-plugin/plugin.json` 의 `version` 과 같다.

플러그인은 `main` 을 통째로 받아 가므로, 받은 사람이 자기 판을 확인할 곳이 여기다.

```bash
claude plugin marketplace update hct-tools   # 최신판 받기
```

`.claude/skills/blue-report/` 아래를 고치면 `version` 을 올리고 여기에 적는다.
잊으면 `scripts/verify_repo.py` 의 `version` 검사가 실패한다.

---

## 1.1.0 — 2026-08-29

### 추가

- **조직 주간보고 덱** (`deck-weekly-report.html` · `--deck weekly`) 7장.
  표지 · 이번 주 요약(다크) · 조직별 현황 표 · 부서별 완료 막대 · 지난주 대비 2열 ·
  다음 주 계획 타임라인 · 지원 요청. 덱 5종이 됐다.
  - 월간 보고(9장)와 달리 **목차를 두지 않는다.** 매주 반복하는 보고라 목차가 시간만 쓴다.
  - 타임라인이 주차가 아니라 **요일 단위**(월~금)다. 주간 실행 계획에 맞춘다.
  - 요약 카드는 4개다. 월간의 6개보다 적어 카드 하단에 수치 행을 두어 여백을 채운다.
- `scripts/verify_repo.py` — 저장소 전체를 기계로 판정한다. CI 가 이것을 돌린다.
  덱 · PPTX · `dist/` 재생성 · 인코딩 · 배포 매니페스트 · 내용 동기화 · 버전 올림.
- `scripts/check_content_sync.py` — HTML 덱과 `pptx/content.js` 의 갈라짐을 잡는다.
  슬라이드 수 · 문서명 · 발표자 노트 · 막대 · 도넛 · 표를 두 곳에서 뽑아 견준다.
- `.github/workflows/verify.yml` — push(main) · PR 마다 `verify_repo.py` 를 돌린다.
  수동 실행 시 `shots` 를 켜면 슬라이드 PNG 를 아티팩트로 받는다.
- PPTX 무결성 검사 — 생긴 `.pptx` 를 실제로 열어 압축 무결성 · 필수 부품 ·
  슬라이드 수를 본다. 파일 개수만 세던 것을 고쳤다.
- 버전 올림 검사 — 스킬 폴더가 바뀌었는데 `plugin.json` 의 `version` 이 그대로면 실패한다.

### 고침

- `brand/hct/README.md` — `--br-cobalt` 는 이미 `#2f4a9c` 로 교체가 끝났는데
  "확인이 필요한 것"에 `#1140d6` 로 남아 있었다.
- 규격서 · `SKILL.md` · `rules.md` · `check_deck.py` docstring — 점검 항목을
  7항목으로 적고 있었으나 실제 판정은 10항목이다. 항목표를 실제 출력 이름으로 채웠다.
- 규격서 9절 "브랜드 자리 (미확정)" — 로고는 `brand/hct/` 에 들어와 있으므로
  미확정은 폰트뿐이다. 끝난 것과 남은 것을 나눴다.

### 알려진 미결

- 로고 원본의 마크 영역이 264×86px 다. 화면용으로는 충분하나 인쇄에는 모자란다.
- 사내 폰트 미확정. `blue-report.css` 의 `--br-font-*` 첫 패밀리만 바꾸면 된다.
- 스킬이 "블루 리포트" 이름을 대야 뜬다. 일반적인 발표자료 요청에는 반응하지 않는다.

---

## 1.0.0 — 2026-08-29

`dytc880915-commits/claude-workspace` 에서 분리한 최초 판. 그전 개발 이력은 그 저장소에 있다.

- 용도별 덱 4종(사내 보고 · 외부 제안 · 프로젝트 보고 · 교육)과 레이아웃 12종 카탈로그
- 토큰 68개 단일 소스(`blue-report.css`), HTML · PDF · PPTX 출력
- `check_deck.py` 10항목 자동 점검, `donut.py` · `palette.py` 차트 생성기
- `apply_brand.py` 브랜드 일괄 적용, 로고 두 벌(다크면 녹아웃 · 밝은면 원색)
- 플러그인 마켓플레이스 배포(`hct-tools`)
