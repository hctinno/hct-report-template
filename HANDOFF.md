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

| 브랜치 | 끝 커밋 | 상태 | 처리 |
|---|---|---|---|
| `full/main` | `48fc1e2` | **기본 브랜치. 기준선.** | — |
| `main` | `35f0897` | 1커밋 스냅샷 · 고유 내용 없음 · 뿌리가 다르다 | 태그로 남기고 삭제 |
| `full/origin` | `cbab49f` | v1.32.0 · **회수 완료**(SHA 포함) | 삭제 가능 |
| `full/claude/blue-report-handover-ih4bnv` | `cbab49f` | `full/origin` 과 같은 커밋 · **회수 완료**(SHA 포함) | 삭제 가능 |
| `full/fix/style-false-positive-and-mark-none` | `9b66310` | 검사기 오탐 수정 · **회수 완료**(cherry-pick) | 태그로 남기고 삭제 |
| `full/claude/on-premise-ai-repo-m686j9` | `d00f263` | 이 저장소 주제와 무관 · **병합 금지** | 별도 저장소로 이관 |

「회수 완료」는 그 브랜치의 내용이 `full/main` 에 들어왔다는 뜻이다. 다만 **회수 방식이
두 가지고, 삭제 안전도가 다르다.**

- **SHA 포함** — 그 커밋이 `full/main` 의 조상이다. 브랜치를 지워도 커밋은 그대로
  남는다. 잃을 것이 없다.
- **cherry-pick** — 내용만 옮겨 담았고 커밋 SHA 는 `full/main` 에 없다. 브랜치를 지우면
  원본 커밋이 참조를 잃고, 언젠가 GitHub 의 정리 대상이 된다.

`full/fix/style-false-positive-and-mark-none` 이 그 cherry-pick 쪽이다. 세 커밋의 내용은
`68b902c` 「검사기 오탐 셋을 회수한다」로 전부 들어왔고 문체 케이스 11건으로 확인했으므로
기능상 잃을 것은 없다. 그래도 원본을 되짚을 수 있게 **지우기 전에 태그로 고정한다.**

```
453e6ed15c2649a4ac227a5fe4837c5da03acacc  검사기 오탐 둘 — 문체 낱말 경계와 마크 자리표시자 None
bda0202489c64579d0bcc6845b3a0feec516b434  문체 예외에 과다(過多) 추가
9b66310018a79b7e5c449e90c648309d001d794d  인라인 강조에 가려진 종결어미도 잡는다
```

이 브랜치를 통째로 병합하지 않은 이유도 함께 적어 둔다 — 기준선보다 15커밋 뒤처져 있어
그대로 합치면 FCC/KC 템플릿 체계가 지워진다(-13500줄).

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

1. 회수 완료된 브랜치를 지운다. 아래 「브랜치 지우는 법」 참고.
2. `main` 스냅샷을 지우고 기본 브랜치 이름을 `main` 으로 되돌린다.
   아래 「기본 브랜치 이름 되돌리는 법」 참고.
3. `full/claude/on-premise-ai-repo-m686j9` 를 별도 저장소로 옮긴다.
   아래 「온프레미스 AI 스택 옮기는 법」 참고.

### 브랜치 지우는 법

**Claude Code 원격 세션에서는 되지 않는다.** 그 세션의 push 정책이 지정 작업 브랜치
외의 ref 를 만들거나 지우는 것을 막아, 브랜치 삭제도 태그 생성도 `HTTP 403` 으로
거부된다. 사람이 로컬 클론이나 GitHub 웹에서 해야 한다.

로컬 클론에서 한다면 태그부터 만들고 지운다.

```bash
git fetch origin
git tag -a archive/fix-style-false-positive-and-mark-none 9b66310 \
        -m "검사기 오탐 수정 원본 — 68b902c 로 cherry-pick 회수한 뒤 남긴다"
git push origin archive/fix-style-false-positive-and-mark-none

git push origin --delete full/origin
git push origin --delete full/claude/blue-report-handover-ih4bnv
git push origin --delete full/fix/style-false-positive-and-mark-none
```

GitHub 웹에서는 `Branches` 탭(<https://github.com/hctinno/hct-report-template/branches>)
에서 지운다. 다만 웹에는 태그를 만드는 자리가 따로 없으므로, 위 태그는 먼저 로컬에서
밀어 넣거나 릴리스를 만들어 대신한다. **태그 없이 `full/fix/...` 를 지우면 원본 세
커밋을 되짚을 수 없게 된다.**

지운 뒤에는 이 문서의 브랜치 지도에서 해당 줄을 지운다.

### 기본 브랜치 이름 되돌리는 법

`full/` 은 복구 과정에서 붙은 것이지 뜻이 있는 이름이 아니다. `main` 으로 되돌리려면
그 자리를 차지하고 있는 구 스냅샷을 먼저 치워야 한다.

**`main` 에 `full/main` 을 force push 해서 덮지 않는다.** 두 계통은 뿌리가 달라
fast-forward 가 되지 않으므로 force 가 필요해지는데, 그러면 이력이 한 번 끊기고
열린 PR 의 base 도 손으로 옮겨야 한다. GitHub 의 이름 바꾸기를 쓰면 그럴 일이 없다 —
기본 브랜치 설정, 열린 PR, 웹 링크 리다이렉트가 함께 따라간다.

**첫째, 구 `main` 을 태그로 남기고 지운다.** 뿌리가 달라 지우면 그 커밋이 참조를
잃는다. 트리는 full 계통 `4ae7a0e` 와 같아 내용을 잃지는 않지만, 「복구가 이렇게
이뤄졌다」는 기록은 사라진다.

```bash
git fetch origin
git tag -a archive/recovery-snapshot 35f0897 \
        -m "구 계정 삭제 후 복구용 1커밋 스냅샷 — full 계통 4ae7a0e 와 트리가 같다"
git push origin archive/recovery-snapshot
git push origin --delete main
```

**둘째, GitHub 웹에서 이름을 바꾼다.** `Settings` → `General` → `Default branch` 의
연필, 또는 `Branches` 페이지에서 `full/main` 을 `main` 으로 바꾼다. 명령줄에는 이에
해당하는 것이 없다 — git 에는 원격 브랜치 이름 바꾸기가 없어서 지우고 새로 미는
것이 되고, 그러면 리다이렉트도 PR 이관도 얻지 못한다.

**셋째, 로컬 클론을 맞춘다.**

```bash
git fetch origin
git remote set-head origin -a
git branch -m full/main main
git branch -u origin/main main
```

#### 바꾼 뒤 저장소에서 손볼 곳

**깨지는 것은 없다.** 브랜치 이름에 기대던 자리를 미리 없애 뒀다.

- `plugin.json` 의 `homepage` 는 브랜치를 가리키지 않는다(저장소 루트).
- `.github/workflows/verify.yml` 의 push 트리거는 `[main, full/main]` 로 양쪽을 건다.
- `verify_repo.py` 의 기준 브랜치 탐색은 `origin/HEAD` 를 먼저 보고, 이름 후보에도
  `origin/main` · `main` 이 들어 있다.

낡는 것은 서술뿐이다. 급하지 않으나 정리한다면 이 문서, `README.md` 의 「이력」 절,
`CLAUDE.md` 의 시작 순서 1번, `verify.yml` 의 주석이다. `verify.yml` 과
`verify_repo.py` 에서 `full/main` 을 빼도 되고 그대로 둬도 무해하다 — 양쪽을 보는
편이 이런 사고를 한 번 더 막는다.

### 온프레미스 AI 스택 옮기는 법

`full/claude/on-premise-ai-repo-m686j9` 의 `onpremise-ai/` 는 이 저장소와 주제가
다르다. 사내 폐쇄망 로컬 LLM · RAG · 하네스 스택이고, **새 저장소를 만들 권한이 없던
세션이 여기 브랜치에 임시로 얹어 둔 것**이다. 그 사정이 원래 그 README 서두에 적혀
있었다.

**이 브랜치를 `full/main` 에 병합하지 않는다.** 온프레미스 AI 코드가 들어오는 동시에
보고서 템플릿 파일 63개가 지워진다.

옮길 것은 `onpremise-ai/` 59파일뿐이고 그 밖에 추가된 것은 없다. 서드파티 의존이
없어 표준 라이브러리만으로 돌며, 떼어낸 상태에서 테스트 98개가 통과한다.

Claude Code 원격 세션에서는 새 저장소를 만들 수 없다 — `POST /user/repos` 가
`403 Resource not accessible by integration` 이다. 그 브랜치를 만든 세션이 막힌
자리와 같다. 사람이 만들어야 한다.

**첫째, GitHub 에서 `hct-onpremise-ai` 를 private 으로 만든다.** README 없이 빈
저장소로 둔다. 아래에서 첫 커밋을 밀어 넣는다.

**둘째, 이 저장소에서 떼어내 밀어 넣는다.** `onpremise-ai/` 는 `d00f263` 한 커밋에서
통째로 추가됐으므로 쪼갠 결과도 한 커밋이다.

```bash
git fetch origin full/claude/on-premise-ai-repo-m686j9
git checkout -b onprem-tmp origin/full/claude/on-premise-ai-repo-m686j9
git subtree split --prefix=onpremise-ai -b onpremise-ai-main
git push https://github.com/hctinno/hct-onpremise-ai.git onpremise-ai-main:main
git checkout full/main && git branch -D onprem-tmp onpremise-ai-main
```

이 길로 가면 새 저장소의 `README.md` 서두에 **임시 안내 블록이 그대로 남는다.**
「독립 저장소로 분리하기 위한 완결된 프로젝트다 … 분리 후 이 안내 블록을 지운다」로
시작하는 인용구다. 옮긴 뒤 지운다.

**셋째, 원 브랜치를 지운다.**

```bash
git push origin --delete full/claude/on-premise-ai-repo-m686j9
```

지운 뒤 이 문서의 브랜치 지도에서 해당 줄과 이 절을 함께 지운다.

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
