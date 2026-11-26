#!/usr/bin/env python3
"""`hct-report` 에이전트 스킬을 묶는다 — Codex · Goose 등 Agent Skills 표준을 읽는 에이전트용.

    python3 scripts/build_hct_skill.py                       # decks-out/hct-report/ 폴더 + zip
    python3 scripts/build_hct_skill.py --check               # 묶지 않고 규격만 본다
    python3 scripts/build_hct_skill.py --install             # ~/.agents/skills/hct-report 에 설치(기존 것은 백업)
    python3 scripts/build_hct_skill.py --install --target /etc/codex/skills   # 공용 설치

무엇을 합치나
  .claude/skills/blue-report/   엔진 — 틀 · 부품 · CSS · 폰트 · 스크립트 · 검사기 (그대로)
  brand/hct/                    회사 로고 · brand.json → 스킬 안 brand/hct/ 로 (홀로 돌게)
  agent-skill/hct-report/       에이전트용 진입부 — SKILL.md · design/(BRAND · COMPONENTS · RULES)
뺀 것
  Claude 전용 SKILL.md · .claude-plugin/ · node_modules · dist · __pycache__ · shots
  — 받는 쪽에서 다시 만들 수 있거나(node_modules) 사람에게 건네는 산출물(dist)이다.

Codex 는 `$HOME/.agents/skills` · 저장소 `.agents/skills` · `/etc/codex/skills` 를,
Goose 는 `~/.agents/skills` · `.agents/skills` 를 읽는다. 위치는 도구 문서에서 바뀔 수 있으니
설치 전에 각 도구의 현재 문서를 확인한다.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE = os.path.join(ROOT, ".claude", "skills", "blue-report")
BRAND = os.path.join(ROOT, "brand", "hct")
OVERLAY = os.path.join(ROOT, "agent-skill", "hct-report")
NAME = "hct-report"
SKIP_DIRS = {"node_modules", "dist", "__pycache__", "shots", ".claude-plugin"}
SKIP_TOP_FILES = {"SKILL.md"}          # Claude 전용 진입부 — 에이전트용으로 갈아 끼운다
SKIP_FILES = {".DS_Store", ".gitignore"}

INSTALL_MD = """# hct-report 설치

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

판 {version} · 원본 저장소 `hctinno/hct-report-template` — 고칠 일이 생기면 설치본이 아니라 저장소를 고친다.
"""


def version():
    pj = os.path.join(ENGINE, ".claude-plugin", "plugin.json")
    return json.load(open(pj, encoding="utf-8")).get("version", "0")


def assemble(dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    for base, dirs, files in os.walk(ENGINE):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        rel = os.path.relpath(base, ENGINE)
        os.makedirs(os.path.join(dst, rel), exist_ok=True)
        for f in files:
            if f in SKIP_FILES or (rel == "." and f in SKIP_TOP_FILES):
                continue
            shutil.copy2(os.path.join(base, f), os.path.join(dst, rel, f))
    shutil.copytree(BRAND, os.path.join(dst, "brand", "hct"))
    for base, _, files in os.walk(OVERLAY):
        rel = os.path.relpath(base, OVERLAY)
        os.makedirs(os.path.join(dst, rel), exist_ok=True)
        for f in files:
            shutil.copy2(os.path.join(base, f), os.path.join(dst, rel, f))
    open(os.path.join(dst, "INSTALL.md"), "w", encoding="utf-8").write(
        INSTALL_MD.format(version=version()))


def check(dst):
    """Agent Skills 규격 · 홀로 도는지 본다. 실패 목록을 돌려준다."""
    fails = []
    skill_md = os.path.join(dst, "SKILL.md")
    s = open(skill_md, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", s, re.S)
    if not m:
        return ["SKILL.md 머리(--- … ---)가 없다"]
    head = dict(re.findall(r"^(\w+):\s*(.*)$", m.group(1), re.M))
    name, desc = head.get("name", ""), head.get("description", "")
    if name != NAME or name != os.path.basename(dst):
        fails.append(f"name 「{name}」이 폴더 이름 「{os.path.basename(dst)}」와 다르다")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64:
        fails.append("name 은 소문자 · 숫자 · 하이픈 64자 이내")
    if not desc or len(desc) > 1024:
        fails.append(f"description 길이 {len(desc)} — 1~1024자")
    elif len(desc) > 300:
        fails.append(f"description {len(desc)}자 — 스킬 목록에서 잘리지 않게 300자 이내로")
    # SKILL.md 가 가리키는 스킬 안 파일이 실제로 있는가
    for ref in sorted(set(re.findall(r"`(?:<SKILL>/)?((?:design|scripts|assets|references|brand)/[^`\s]+|DESIGN\.md|README\.md|MOTION\.md|LAYOUTS\.md|COMPONENTS\.md)`", s))):
        if not os.path.exists(os.path.join(dst, ref)):
            fails.append(f"SKILL.md 가 가리키는 파일이 없다 — {ref}")
    if not os.path.isfile(os.path.join(dst, "brand", "hct", "brand.json")):
        fails.append("brand/hct/brand.json 이 없다")
    for f in ("hct-logo-color.png", "hct-logo-white.png", "hct-logo-symbol-color.png", "hct-logo-symbol-white.png"):
        if not os.path.isfile(os.path.join(dst, "brand", "hct", f)):
            fails.append(f"로고 없음 — {f}")
    # 홀로 도는가 — 저장소 밖 경로(../../../)를 가리키는 문서 줄
    for doc in ("SKILL.md", os.path.join("design", "BRAND.md"), os.path.join("design", "COMPONENTS.md"), os.path.join("design", "RULES.md")):
        if "../../../" in open(os.path.join(dst, doc), encoding="utf-8").read():
            fails.append(f"{doc} 가 저장소 경로(../../../)를 가리킨다")
    r = subprocess.run([sys.executable, os.path.join(dst, "scripts", "hct.py"), "formats", "--json"], capture_output=True, text=True)
    if r.returncode != 0:
        fails.append("hct.py formats 실패 — " + (r.stderr.strip().splitlines() or [""])[-1])
    return fails


def zip_dir(dst, out_zip):
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for base, _, files in os.walk(dst):
            for f in files:
                p = os.path.join(base, f)
                z.write(p, os.path.join(NAME, os.path.relpath(p, dst)))


PUBLISHED_REL = "skills/hct-report"
PUBLISHED = os.path.join(ROOT, *PUBLISHED_REL.split("/"))


def tree_files(d):
    out = {}
    for base, dirs, files in os.walk(d):
        dirs[:] = [x for x in dirs if x != "__pycache__"]
        for f in files:
            p = os.path.join(base, f)
            out[os.path.relpath(p, d).replace(os.sep, "/")] = open(p, "rb").read()
    return out


def publish(check_only=False):
    """GitHub 설치용 펼친 스킬. 묶음과 같은 내용을 저장소에 둔다 — 손으로 고치지 않는다(원본을 고치고 다시 펼친다)."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        dst = os.path.join(tmp, NAME)
        assemble(dst)
        fails = check(dst)
        if fails:
            for f in fails:
                print("실패  " + f)
            sys.exit(f"\n규격 실패 {len(fails)}건 — 펼치지 않는다")
        want = tree_files(dst)
        have = tree_files(PUBLISHED) if os.path.isdir(PUBLISHED) else {}
        diff = sorted(k for k in set(want) | set(have) if want.get(k) != have.get(k))
        if check_only:
            if diff:
                print(f"실패  {PUBLISHED_REL}/ 가 원본과 다르다 {len(diff)}건 — {', '.join(diff[:5])}")
                print("      python3 scripts/build_hct_skill.py --publish")
                return 1
            print(f"{PUBLISHED_REL}/ — 원본과 같다 · 파일 {len(want)}개 · 판 {version()}")
            return 0
        if os.path.exists(PUBLISHED):
            shutil.rmtree(PUBLISHED)
        shutil.copytree(dst, PUBLISHED, ignore=shutil.ignore_patterns("__pycache__"))
        print(f"펼침: {PUBLISHED_REL}/ · 파일 {len(want)}개 · 판 {version()} — 바뀐 파일 {len(diff)}개")
        return 0


def main():
    ap = argparse.ArgumentParser(description="hct-report 에이전트 스킬 묶기")
    ap.add_argument("--out", default=os.path.join(ROOT, "decks-out"), help="묶음을 둘 폴더")
    ap.add_argument("--check", action="store_true", help="규격만 보고 폴더는 지운다")
    ap.add_argument("--install", action="store_true", help="스킬 폴더에 설치")
    ap.add_argument("--target", default=os.path.expanduser("~/.agents/skills"), help="설치할 스킬 폴더(기본 ~/.agents/skills)")
    ap.add_argument("--publish", action="store_true",
                    help=f"저장소 {PUBLISHED_REL}/ 에 펼친다 — gh skill install · npx skills add 가 GitHub 에서 받아 가는 자리")
    ap.add_argument("--check-published", action="store_true", help=f"{PUBLISHED_REL}/ 가 원본에서 새로 묶은 것과 같은지만 본다")
    a = ap.parse_args()

    if a.publish or a.check_published:
        return publish(check_only=a.check_published)

    dst = os.path.join(a.out, NAME)
    assemble(dst)
    fails = check(dst)
    n = sum(len(f) for _, _, f in os.walk(dst))
    for f in fails:
        print("실패  " + f)
    if fails:
        sys.exit(f"\n규격 실패 {len(fails)}건 — 묶지 않는다")
    print(f"규격 통과 — 파일 {n}개 · 판 {version()}")
    if a.check:
        shutil.rmtree(dst)
        return
    out_zip = os.path.join(a.out, f"{NAME}-v{version()}.zip")
    zip_dir(dst, out_zip)
    print(f"폴더: {dst}\nzip : {out_zip}  ({os.path.getsize(out_zip) // 1024}KB)")
    if a.install:
        target = os.path.join(os.path.expanduser(a.target), NAME)
        if os.path.exists(target):
            bak = target + ".bak-" + datetime.now().strftime("%Y%m%d%H%M%S")
            shutil.move(target, bak)
            print(f"기존 설치본 백업: {bak}")
        shutil.copytree(dst, target)
        print(f"설치: {target}\n에이전트를 다시 시작한다.")


if __name__ == "__main__":
    sys.exit(main())
