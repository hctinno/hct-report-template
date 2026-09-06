# 인수인계

이 저장소를 처음 이어받는 사람이 먼저 읽는 문서다. 쓰는 법은 `README.md`, 규격은
`.claude/skills/blue-report/README.md`, 작업 규칙은 `CLAUDE.md` 에 있다. 여기에는
**저장소 자체의 사정** — 왜 브랜치가 이런 모양인지와 남은 정리 항목 — 만 적는다.

기준 시점 2026-09-06 · 스킬 v1.33.0

---

## 지금 상태

정상이다. `python3 scripts/verify_repo.py` 가 실패 0 으로 통과하고, 덱 9종 · A4 문서
4종 · FCC/KC 템플릿 14종 · PPTX 8종이 모두 살아 있다.

다만 **브랜치 모양이 보통과 다르다.** 기본 브랜치가 `main` 이 아니라 `full/main` 이다.
모르고 건드리면 엉뚱한 계통에 커밋하게 되므로 아래를 먼저 읽는다.

---

## 왜 계통이 둘인가

이 저장소는 `dytc880915-commits/claude-workspace` 에서 분리해 나왔다. 그 뒤 그 계정이
삭제되었고, `hctinno` 로 옮겨 복구하는 과정에서 **뿌리가 다른 두 계통이 함께 들어왔다.**

```
1b62414 (2026-08-29)  블루 리포트 발표 템플릿을 독립 저장소로 분리
   └─ ... ─ full/main          ← 개발 이력을 그대로 이어받은 계통. 기본 브랜치.

35f0897 (2026-09-06)  Recover snapshot from ...
   └─ main                     ← 복구용 1커밋 스냅샷. 위 계통과 조상을 공유하지 않는다.
```

`git merge-base main full/main` 은 아무것도 내놓지 않는다. 두 계통은 공통 조상이 없다.

**`main` 에는 고유한 내용이 없다.** 트리 해시가 `full` 계통의 `4ae7a0e` 시점과 바이트
단위로 같다(`95d10de9af57d73e59b0820936d9774c29ddb949`). `main` 에만 있는 파일은 없고,
스킬 버전은 v1.23.0 에 멈춰 있다. 복구가 성공했는지 확인하려고 남겨 둔 흔적이다.

### 기준은 `full/main` 이다

작업은 전부 `full/main` 에서 갈라져 나가고 `full/main` 으로 돌아온다. `main` 은
건드리지 않는다.

---

## 브랜치 지도

| 브랜치 | 상태 | 처리 |
|---|---|---|
| `full/main` | **기본 브랜치. 기준선.** | — |
| `main` | 1커밋 스냅샷 · 고유 내용 없음 | 삭제 후보. 승인 필요 |
| `full/origin` | v1.32.0 · **회수 완료** | 삭제 후보. 승인 필요 |
| `full/claude/blue-report-handover-ih4bnv` | `full/origin` 과 같은 커밋 · **회수 완료** | 삭제 후보. 승인 필요 |
| `full/fix/style-false-positive-and-mark-none` | 검사기 오탐 수정 · **회수 완료**(cherry-pick) | 삭제 후보. 승인 필요 |
| `full/claude/on-premise-ai-repo-m686j9` | 이 저장소 주제와 무관 | 별도 저장소로 이관 |

「회수 완료」는 그 브랜치의 내용이 `full/main` 에 들어왔다는 뜻이다. 커밋을 잃지 않고
지울 수 있다. 다만 **브랜치를 지우는 일은 승인을 받고 한다.**

### `full/` 접두사

복구 과정에서 붙은 것이지 의미가 있는 이름은 아니다. 기본 브랜치를 평범한 `main` 으로
되돌리려면 `main` 스냅샷을 먼저 정리해야 하므로 두 가지를 함께 결정한다.

### `full/claude/on-premise-ai-repo-m686j9` 주의

폐쇄망 로컬 LLM/RAG 스택이다. 이 저장소의 주제가 아니고, `verify_repo.py` ·
`check_content_sync.py` · `build_account_skill_bundle.py` 를 지운다.
**`full/main` 에 병합하지 않는다.** 옮길 곳을 정해 이관한다.

---

## 남은 일

승인 없이 해도 되는 것은 없다. 전부 브랜치 정리이고, 되돌리기 어렵기 때문이다.

1. 회수 완료된 세 브랜치(`full/origin` · `full/claude/blue-report-handover-ih4bnv` ·
   `full/fix/style-false-positive-and-mark-none`)를 지운다.
2. `main` 스냅샷을 지울지 정한다. 지운다면 기본 브랜치 이름을 `full/main` 에서
   `main` 으로 되돌릴지 함께 정한다. 되돌리면 `.github/workflows/verify.yml` 의
   push 트리거와 `verify_repo.py` 의 기준 브랜치 후보를 다시 볼 필요는 없다 —
   둘 다 이미 양쪽을 본다.
3. `full/claude/on-premise-ai-repo-m686j9` 를 별도 저장소로 옮긴다.

### 브랜치와 무관한 미해결 항목

- **로고 원본 해상도.** 마크 영역이 264x86px 이다. 화면용으로는 충분하지만 인쇄에는
  모자란다. SVG 나 고해상도 원본이 생기면 `brand/hct/` 를 교체하고
  `make_logo_variants.py` 로 두 벌을 다시 뽑는다.

---

## 이어받을 때 먼저 하는 일

```bash
git clone https://github.com/hctinno/hct-report-template.git
cd hct-report-template
git branch --show-current          # full/main 이어야 한다
python3 scripts/verify_repo.py     # 실패 0 이어야 한다
```

`verify_repo.py` 는 Chromium · Pillow · node_modules 를 스스로 받는다. 처음 한 번은
몇 분 걸린다. 결과의 「버전 올림」 줄에 **기준 브랜치 이름이 함께 찍힌다** — 거기에
`origin/full/main` 이 아닌 다른 것이 보이면 계통을 잘못 잡은 것이므로 이 문서를
다시 읽는다.

CI 는 `full/main` 과 `main` 양쪽의 push, 그리고 모든 PR 에서 같은 스크립트를 돌린다.
로컬에서 통과하면 CI 도 통과한다.
