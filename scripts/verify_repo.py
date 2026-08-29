#!/usr/bin/env python3
"""저장소 전체 점검 — CI 와 로컬이 같은 명령을 쓴다.

    python3 scripts/verify_repo.py             # 전부 점검
    python3 scripts/verify_repo.py --shots out # 슬라이드별 PNG 도 남긴다
    python3 scripts/verify_repo.py --only decks

검사 항목
  decks     덱 6종을 apply_brand.py 로 만들고 check_deck.py 로 판정한다.
            11항목 중 `실패` 가 하나라도 있으면 저장소 점검이 실패한다.
            `주의` 는 허용한다 — 도넛을 쓰지 않은 덱에서 나오는 정상 결과다.
  pptx      build.js 가 돌고 .pptx 4종이 나오는가.
  dist      dist/ 의 두 파일이 소스에서 재생성한 것과 같은가.
            assets/ 를 고치고 dist/ 를 다시 만들지 않으면 여기서 걸린다.
  encoding  한국어가 UTF-8 로 저장됐고 깨짐 패턴이 없는가.
  plugin    마켓플레이스·플러그인 매니페스트가 성립하는가.
            여기가 깨지면 다른 PC 에서 `plugin install` 이 실패한다.
  sync      HTML 덱과 pptx/content.js 의 내용이 갈라지지 않았는가.
            같은 내용이 두 곳에 있어 한쪽만 고치기 쉽다.
  version   스킬 폴더를 고쳤으면 plugin.json 의 version 을 올렸는가.
            플러그인은 main 을 통째로 받아 가므로 버전이 그대로면
            받는 쪽이 자기 판을 구분하지 못한다.

종료 코드는 실패가 하나라도 있으면 1, 아니면 0 이다.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, ".claude", "skills", "blue-report")
SCRIPTS = os.path.join(SKILL, "scripts")
BRAND = os.path.join(ROOT, "brand", "hct", "brand.json")

DECKS = ["catalog", "internal", "weekly", "ax", "sales", "project", "training"]

# PPTX 는 카탈로그를 뺀 용도별 덱만 나온다. 카탈로그는 발표물이 아니라 레이아웃 견본첩이다.
EXPECTED_PPTX = len(DECKS) - 1

# dist/ 의 두 파일은 빌드 명령이 서로 다르다. 아래가 그 정본이다.
DIST_BUILDS = [
    ("blue-report-deck.html", []),
    ("blue-report-artifact.html", ["--artifact", "--brand", BRAND]),
]

# 인코딩이 깨졌을 때 나오는 대표 글자. 스크립트 자신이 걸리지 않도록 코드포인트로 적는다.
MOJIBAKE = ["濡", "湲", "遺", "媛", "李", "???"]
# 이 패턴을 규칙 문장으로 인용하는 문서. 검사에서 제외한다.
MOJIBAKE_EXEMPT = {"CLAUDE.md", "AGENTS.md", os.path.join("scripts", "verify_repo.py")}
SCAN_EXT = {".md", ".html", ".js", ".py", ".json", ".css", ".yml", ".yaml"}

RESULT_RE = re.compile(r"결과: 통과 (\d+) · 주의 (\d+) · 실패 (\d+)")


class Log:
    def __init__(self):
        self.rows, self.failed = [], False

    def ok(self, name, detail=""):
        self.rows.append(("통과", name, detail))

    def warn(self, name, detail=""):
        self.rows.append(("주의", name, detail))

    def fail(self, name, detail=""):
        self.rows.append(("실패", name, detail))
        self.failed = True

    @staticmethod
    def _w(s):
        """한글은 터미널에서 두 칸을 먹는다. 그 폭으로 센다."""
        return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)

    def render(self):
        print("\n" + "=" * 62)
        print("저장소 점검 결과")
        print("=" * 62)
        w = max((self._w(n) for _, n, _ in self.rows), default=0)
        for mark, name, detail in self.rows:
            pad = " " * (w - self._w(name))
            print(f"  {mark}  {name}{pad}  {detail}")
        n_ok = sum(1 for m, _, _ in self.rows if m == "통과")
        n_wa = sum(1 for m, _, _ in self.rows if m == "주의")
        n_fa = sum(1 for m, _, _ in self.rows if m == "실패")
        print(f"\n통과 {n_ok} · 주의 {n_wa} · 실패 {n_fa}")
        if self.failed:
            print("\n실패가 있다. 완료가 아니다.")
        return 1 if self.failed else 0


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd or ROOT, capture_output=True, text=True)


# ------------------------------------------------------------------- 덱 6종

def check_decks(log, out_dir, shots_dir):
    for name in DECKS:
        deck = os.path.join(out_dir, f"{name}.html")
        r = run([sys.executable, os.path.join(SCRIPTS, "apply_brand.py"),
                 "--brand", BRAND, "--deck", name, "--single-file", "-o", deck])
        if r.returncode != 0 or not os.path.exists(deck):
            log.fail(f"덱 {name}", "apply_brand.py 실패 — " + (r.stderr.strip().splitlines() or [""])[-1])
            continue

        cmd = [sys.executable, os.path.join(SCRIPTS, "check_deck.py"), deck]
        if shots_dir:
            cmd += ["--shots", os.path.join(shots_dir, name)]
        r = run(cmd)
        print(r.stdout, end="")
        if r.stderr.strip():
            print(r.stderr, end="", file=sys.stderr)

        m = RESULT_RE.search(r.stdout)
        if not m:
            log.fail(f"덱 {name}", "check_deck.py 가 결과 줄을 내지 않았다")
            continue
        ok, warn, fail = (int(x) for x in m.groups())
        detail = f"통과 {ok} · 주의 {warn} · 실패 {fail}"
        if fail or r.returncode != 0:
            log.fail(f"덱 {name}", detail)
        elif warn:
            log.warn(f"덱 {name}", detail)
        else:
            log.ok(f"덱 {name}", detail)


# ---------------------------------------------------------------------- PPTX

def check_pptx(log, out_dir):
    if not shutil.which("node"):
        log.fail("PPTX 생성", "node 가 없다")
        return
    r = run(["node", os.path.join(SKILL, "pptx", "build.js"),
             "--brand", BRAND, "--out", out_dir])
    made = sorted(f for f in os.listdir(out_dir) if f.endswith(".pptx"))
    if r.returncode != 0:
        log.fail("PPTX 생성", (r.stderr.strip().splitlines() or ["build.js 실패"])[-1])
        return
    if len(made) != EXPECTED_PPTX:
        log.fail("PPTX 생성", f"{EXPECTED_PPTX}종이 나와야 하는데 {len(made)}종")
        return
    log.ok("PPTX 생성", f"{len(made)}종 — " + ", ".join(made))
    check_pptx_integrity(log, out_dir, made)


def check_pptx_integrity(log, out_dir, made):
    """생긴 파일이 실제로 열리는가. 파일 개수만 세면 깨진 것도 통과한다.

    .pptx 는 zip 이다. 표준 라이브러리로 열어 압축 무결성과 필수 부품,
    슬라이드 수를 본다. 슬라이드 수는 content.js 가 선언한 값과 견준다."""
    try:
        expect = expected_slide_counts()
    except Exception as e:
        log.warn("PPTX 무결성", f"기대 슬라이드 수를 읽지 못했다 — {e}")
        expect = {}

    bad = []
    for name in made:
        path = os.path.join(out_dir, name)
        try:
            with zipfile.ZipFile(path) as z:
                if z.testzip() is not None:
                    bad.append(f"{name} (압축 손상)")
                    continue
                names = z.namelist()
                if "[Content_Types].xml" not in names:
                    bad.append(f"{name} ([Content_Types].xml 없음)")
                    continue
                n = len([x for x in names
                         if x.startswith("ppt/slides/slide") and x.endswith(".xml")])
                want = expect.get(name)
                if n == 0:
                    bad.append(f"{name} (슬라이드 0장)")
                elif want is not None and n != want:
                    bad.append(f"{name} (슬라이드 {n}장 · content.js 는 {want}장)")
        except Exception as e:
            bad.append(f"{name} (열지 못함 — {e})")

    if bad:
        log.fail("PPTX 무결성", "; ".join(bad))
    else:
        total = sum(expect.get(n, 0) for n in made)
        log.ok("PPTX 무결성", f"{len(made)}종 모두 정상 · 슬라이드 합계 {total}장")


def expected_slide_counts():
    """content.js 가 선언한 덱별 파일명과 슬라이드 수."""
    script = (
        "const c = require(%s);\n"
        "const o = {};\n"
        "for (const v of Object.values(c)) if (v && v.slides) o[v.file] = v.slides.length;\n"
        "process.stdout.write(JSON.stringify(o));\n"
    ) % json.dumps(os.path.join(SKILL, "pptx", "content.js"))
    r = subprocess.run(["node", "-e", script], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[:200])
    return json.loads(r.stdout)


# ---------------------------------------------------------------------- dist

def check_dist(log):
    """dist/ 가 소스에서 재생성한 것과 같은지 본다. 원본은 건드리지 않는다."""
    dist = os.path.join(SKILL, "dist")
    backup = {}
    try:
        for fname, _ in DIST_BUILDS:
            p = os.path.join(dist, fname)
            backup[fname] = open(p, "rb").read() if os.path.exists(p) else None

        for fname, extra in DIST_BUILDS:
            r = run([sys.executable, os.path.join(SCRIPTS, "build_single_file.py")] + extra)
            p = os.path.join(dist, fname)
            if r.returncode != 0 or not os.path.exists(p):
                log.fail(f"dist/{fname}", "재생성 실패 — " + (r.stderr.strip().splitlines() or [""])[-1])
                continue
            if open(p, "rb").read() == backup[fname]:
                log.ok(f"dist/{fname}", "소스와 일치")
            else:
                cmd = "python3 .claude/skills/blue-report/scripts/build_single_file.py " + " ".join(
                    "brand/hct/brand.json" if x == BRAND else x for x in extra)
                log.fail(f"dist/{fname}", f"소스와 다르다 — 다시 만들어 커밋한다: {cmd}")
    finally:
        for fname, data in backup.items():
            if data is not None:
                open(os.path.join(dist, fname), "wb").write(data)


# ------------------------------------------------------------------ 인코딩

def check_encoding(log):
    r = run(["git", "ls-files"])
    if r.returncode != 0:
        log.warn("한국어 인코딩", "git ls-files 실패 — 건너뜀")
        return
    bad = []
    for rel in r.stdout.splitlines():
        if os.path.splitext(rel)[1] not in SCAN_EXT:
            continue
        if rel in MOJIBAKE_EXEMPT or rel.replace("/", os.sep) in MOJIBAKE_EXEMPT:
            continue
        p = os.path.join(ROOT, rel)
        try:
            text = open(p, encoding="utf-8").read()
        except UnicodeDecodeError:
            bad.append(f"{rel} (UTF-8 아님)")
            continue
        hits = [m for m in MOJIBAKE if m in text]
        if hits:
            bad.append(f"{rel} ({' '.join(hits)})")
    if bad:
        log.fail("한국어 인코딩", "깨짐 의심 — " + "; ".join(bad[:5]))
    else:
        log.ok("한국어 인코딩", "UTF-8 · 깨짐 패턴 없음")


# ------------------------------------------------------- HTML · PPTX 내용 동기화

def check_sync(log):
    """같은 내용이 assets/deck-*.html 과 pptx/content.js 두 곳에 있다.

    합치지 않기로 했다. HTML 을 손으로 고치는 것이 이 시스템의 사용법이고,
    HTML 을 생성물로 만들면 그 사용법이 사라진다. 대신 갈라짐을 기계가 잡는다.
    자세한 내용은 scripts/check_content_sync.py 머리말에 있다."""
    script = os.path.join(ROOT, "scripts", "check_content_sync.py")
    r = run([sys.executable, script])
    print(r.stdout, end="")
    if r.stderr.strip():
        print(r.stderr, end="", file=sys.stderr)
    first = (r.stdout.strip().splitlines() or [""])[0]
    detail = first.split("  ", 2)[-1].strip() if first else ""
    # 하위 스크립트가 자기 이름을 앞에 붙여 나온다. 표에서 두 번 찍지 않게 뗀다.
    for prefix in ("내용 동기화 — ", "내용 동기화 "):
        if detail.startswith(prefix):
            detail = detail[len(prefix):]
            break
    if r.returncode == 0:
        log.ok("내용 동기화", detail or "HTML 과 PPTX 일치")
    else:
        log.fail("내용 동기화", detail or "HTML 덱과 pptx/content.js 가 갈라졌다")


# ------------------------------------------------------------------ 배포

def check_plugin(log):
    """`plugin install` 이 성립하는 최소 조건을 본다."""
    mp = os.path.join(ROOT, ".claude-plugin", "marketplace.json")
    try:
        data = json.load(open(mp, encoding="utf-8"))
    except Exception as e:
        log.fail("마켓플레이스 매니페스트", f"{mp} 를 읽지 못했다 — {e}")
        return

    plugins = data.get("plugins") or []
    if not data.get("name") or not plugins:
        log.fail("마켓플레이스 매니페스트", "name 또는 plugins 가 비어 있다")
        return
    log.ok("마켓플레이스 매니페스트", f"{data['name']} · 플러그인 {len(plugins)}개")

    for entry in plugins:
        pname = entry.get("name", "(이름 없음)")
        src = entry.get("source", "")
        pdir = os.path.normpath(os.path.join(ROOT, src))
        if not os.path.isdir(pdir):
            log.fail(f"플러그인 {pname}", f"source 경로가 없다 — {src}")
            continue

        manifest = os.path.join(pdir, ".claude-plugin", "plugin.json")
        if not os.path.exists(manifest):
            log.fail(f"플러그인 {pname}", "plugin.json 이 없다")
            continue
        try:
            pj = json.load(open(manifest, encoding="utf-8"))
        except Exception as e:
            log.fail(f"플러그인 {pname}", f"plugin.json 이 깨졌다 — {e}")
            continue
        if pj.get("name") != pname:
            log.fail(f"플러그인 {pname}",
                     f"이름이 어긋난다 — marketplace {pname} · plugin.json {pj.get('name')}")
            continue

        skill = os.path.join(pdir, "SKILL.md")
        if not os.path.exists(skill):
            log.fail(f"플러그인 {pname}", "SKILL.md 가 없다")
            continue
        head = open(skill, encoding="utf-8").read(2048)
        if not head.startswith("---") or "\nname:" not in head:
            log.fail(f"플러그인 {pname}", "SKILL.md 머리말에 name 이 없다")
            continue

        log.ok(f"플러그인 {pname}", f"v{pj.get('version', '?')} · {src}")

    # 저장소 설정이 가리키는 마켓플레이스 이름이 실제와 같은가
    st = os.path.join(ROOT, ".claude", "settings.json")
    if os.path.exists(st):
        try:
            known = json.load(open(st, encoding="utf-8")).get("extraKnownMarketplaces", {})
        except Exception as e:
            log.fail("settings.json", f"읽지 못했다 — {e}")
            return
        if known and data.get("name") not in known:
            log.fail("settings.json",
                     f"등록된 이름 {list(known)} 이 marketplace.json 의 {data['name']} 와 다르다")
        else:
            log.ok("settings.json", "마켓플레이스 이름 일치")


# ------------------------------------------------------------------ 버전 올림

def check_version(log):
    """스킬 폴더가 바뀌었는데 version 이 그대로면 실패.

    기준 브랜치를 찾지 못하는 환경(얕은 클론, main 이 없는 저장소)에서는
    실패가 아니라 주의로 넘긴다. 없는 것을 근거로 실패시키지 않는다."""
    base = next((r for r in ("origin/main", "main")
                 if run(["git", "rev-parse", "--verify", "--quiet", r]).returncode == 0), None)
    if base is None:
        log.warn("버전 올림", "기준 브랜치(main)가 없어 건너뜀")
        return

    # 갈라진 지점 기준으로 본다. 아직 커밋하지 않은 것도 포함하려고 작업 트리와 견준다.
    mb = run(["git", "merge-base", base, "HEAD"])
    if mb.returncode != 0:
        log.warn("버전 올림", "merge-base 를 찾지 못해 건너뜀 "
                             "(얕은 클론이면 checkout 의 fetch-depth 를 0 으로 둔다)")
        return
    ref = mb.stdout.strip()

    rel = os.path.relpath(SKILL, ROOT).replace(os.sep, "/")
    r = run(["git", "diff", "--name-only", ref, "--", rel])
    if r.returncode != 0:
        log.warn("버전 올림", "git diff 실패 — 건너뜀")
        return
    changed = [x for x in r.stdout.splitlines() if x.strip()]
    if not changed:
        log.ok("버전 올림", f"{rel} 변경 없음")
        return

    manifest = f"{rel}/.claude-plugin/plugin.json"
    try:
        now = json.load(open(os.path.join(ROOT, manifest), encoding="utf-8")).get("version")
    except Exception as e:
        log.fail("버전 올림", f"plugin.json 을 읽지 못했다 — {e}")
        return
    r2 = run(["git", "show", f"{ref}:{manifest}"])
    if r2.returncode != 0:
        log.warn("버전 올림", "갈라진 지점에 plugin.json 이 없어 건너뜀")
        return
    try:
        before = json.loads(r2.stdout).get("version")
    except Exception as e:
        log.warn("버전 올림", f"갈라진 지점의 plugin.json 을 읽지 못했다 — {e}")
        return

    if now == before:
        log.fail("버전 올림",
                 f"스킬 파일 {len(changed)}개가 바뀌었는데 version 이 {now} 그대로 — "
                 f"{manifest} 와 CHANGELOG.md 를 올린다")
    else:
        log.ok("버전 올림", f"{before} → {now} · 스킬 파일 {len(changed)}개 변경")


# ------------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser(description="블루 리포트 저장소 점검")
    ap.add_argument("--shots", metavar="폴더", help="슬라이드별 PNG 를 남길 폴더")
    ap.add_argument("--only", choices=["decks", "pptx", "dist", "encoding", "plugin", "sync", "version"],
                    action="append", help="일부만 돌린다. 여러 번 줄 수 있다")
    ap.add_argument("--keep", metavar="폴더", help="만든 덱·PPTX 를 여기에 남긴다")
    a = ap.parse_args()

    only = set(a.only or ["decks", "pptx", "dist", "encoding", "plugin", "sync", "version"])
    log = Log()

    if a.shots:
        os.makedirs(a.shots, exist_ok=True)

    tmp = a.keep or tempfile.mkdtemp(prefix="blue-report-verify-")
    os.makedirs(tmp, exist_ok=True)
    try:
        if "decks" in only:
            print("── 덱 6종 ──")
            check_decks(log, tmp, a.shots)
        if "pptx" in only:
            print("\n── PPTX ──")
            check_pptx(log, tmp)
        if "dist" in only:
            print("\n── dist 재생성 대조 ──")
            check_dist(log)
        if "encoding" in only:
            print("\n── 한국어 인코딩 ──")
            check_encoding(log)
        if "plugin" in only:
            print("\n── 배포 매니페스트 ──")
            check_plugin(log)
        if "sync" in only:
            print("\n── HTML · PPTX 내용 동기화 ──")
            check_sync(log)
        if "version" in only:
            print("\n── 버전 올림 ──")
            check_version(log)
    finally:
        if not a.keep:
            shutil.rmtree(tmp, ignore_errors=True)

    return log.render()


if __name__ == "__main__":
    sys.exit(main())
