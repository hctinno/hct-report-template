# hct-report 설치

## GitHub 에서 바로 (권장)

```bash
gh skill install hctinno/hct-report-template hct-report --agent codex --scope user     # Codex
gh skill install hctinno/hct-report-template hct-report --agent goose --scope user     # Goose
# 새 판으로 바꿀 때 — 같은 명령에 --force
```

GitHub CLI(`gh`)가 없으면 `npx skills add hctinno/hct-report-template --skill hct-report -g -a codex`.
설치본은 저장소의 `skills/hct-report/` 다(`scripts/build_hct_skill.py --publish` 가 만들고 검사가 원본과 대조한다).

## 손으로

이 폴더를 통째로 에이전트의 스킬 폴더에 둔다. 폴더 이름은 `hct-report` 그대로.

| 에이전트 | 개인 설치 | 프로젝트 · 공용 |
|---|---|---|
| Codex | `~/.agents/skills/hct-report/` | 저장소 `.agents/skills/hct-report/` · `/etc/codex/skills/hct-report/` |
| Goose | `~/.agents/skills/hct-report/` | 프로젝트 `.agents/skills/hct-report/` |

설치 뒤 에이전트를 다시 시작한다. 확인: `python3 ~/.agents/skills/hct-report/scripts/hct.py formats`

준비물 — Python 3.9+, Node.js 18+(PPTX). 첫 실행에 Chromium(약 150MB) · npm 패키지를 받는다.

판 1.56.0 · 원본 저장소 `hctinno/hct-report-template` — 고칠 일이 생기면 설치본이 아니라 저장소를 고친다.
