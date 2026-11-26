#!/usr/bin/env python3
"""회사 공식 문서 양식(forms/hct-official.json)의 본문 명조 — Noto Serif KR 을 잘라 assets/fonts/ 에 넣는다.

사내 규정 · 강령 원본은 HWP 바탕 계열 명조다. 바탕은 재배포할 수 없어 HTML · PDF 에는 모양이 가까운
Noto Serif KR(SIL OFL 1.1)을 심고, Word 에는 양식의 font.body.word(「바탕」)를 적는다.

원본은 npm @fontsource/noto-serif-kr 이다. 이 패키지는 글자를 120여 조각(unicode-range)으로 나눠 두므로,
필요한 글자가 든 조각만 골라 합친 뒤 프리텐다드 서브셋과 같은 범위로 자른다.
  KS X 1001 완성형 한글 2,350자 + ASCII + 문서 기호(로마 숫자 Ⅰ~Ⅹ · 원문자 ①~⑳ · 가운뎃점 · 따옴표 · 괄호)
조판 기능(GSUB · GPOS)은 뺀다 — 한글 본문에 쓰이지 않고, 조각마다 달라 합칠 수 없다.

    python3 scripts/make_serif_subset.py           # 받아서 자른다 (400 · 700 두 벌)
    python3 scripts/make_serif_subset.py --check   # 지금 것이 필요한 글자를 다 갖는지만 본다
"""
import argparse
import io
import json
import os
import re
import sys
import tarfile
import tempfile
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ensure_deps import need_fonttools  # noqa: E402

SKILL = os.path.dirname(HERE)
FONT_DIR = os.path.join(SKILL, "assets", "fonts")
REGISTRY = "https://registry.npmjs.org/@fontsource/noto-serif-kr"
OUTS = {"400": "NotoSerifKR-Regular.subset.woff2", "700": "NotoSerifKR-Bold.subset.woff2"}

SYMBOLS = ({0xA0, 0xB7, 0xD7, 0x2013, 0x2014, 0x2015, 0x2018, 0x2019, 0x201C, 0x201D, 0x2022, 0x2026,
            0x203B, 0x2192, 0x25A0, 0x25A1, 0x25B2, 0x25BC, 0x25CB, 0x25CF, 0x3131, 0xFF5E,
            0x3008, 0x3009, 0x300C, 0x300D, 0x300E, 0x300F, 0x3010, 0x3011}
           | set(range(0x2160, 0x216A)) | set(range(0x2460, 0x2474)))


def wanted():
    need = set(range(0x20, 0x7F)) | SYMBOLS
    for b in range(0xB0, 0xC9):
        for c in range(0xA1, 0xFF):
            try:
                need.add(ord(bytes([b, c]).decode("euc-kr")))
            except UnicodeDecodeError:
                pass
    return need


def check():
    need_fonttools()
    from fontTools.ttLib import TTFont
    need, bad = wanted(), []
    for w, fn in OUTS.items():
        p = os.path.join(FONT_DIR, fn)
        if not os.path.exists(p):
            bad.append(f"{fn} 없음")
            continue
        miss = need - set(TTFont(p).getBestCmap())
        if miss:
            bad.append(f"{fn} 빠진 글자 {len(miss)}개 — {''.join(chr(c) for c in sorted(miss)[:10])}")
    for b in bad:
        print("  실패 ", b)
    print("명조 서브셋 —", "통과" if not bad else "실패")
    return 1 if bad else 0


def build():
    need_fonttools()
    from fontTools.ttLib import TTFont
    from fontTools import subset
    from fontTools.merge import Merger
    meta = json.load(urllib.request.urlopen(REGISTRY))
    ver = meta["dist-tags"]["latest"]
    tgz = urllib.request.urlopen(meta["versions"][ver]["dist"]["tarball"]).read()
    tar = tarfile.open(fileobj=io.BytesIO(tgz))
    need = wanted()
    with tempfile.TemporaryDirectory() as tmp:
        for w, out in OUTS.items():
            css = tar.extractfile(f"package/{w}.css").read().decode()
            files = re.findall(rf"url\(\./files/(noto-serif-kr-\d+-{w}-normal\.woff2)\)", css)
            parts, seen = [], set()
            for fn in files:
                f = TTFont(io.BytesIO(tar.extractfile(f"package/files/{fn}").read()))
                hit = (set(f.getBestCmap()) & need) - seen
                if not hit:
                    continue
                seen |= hit
                o = subset.Options()
                o.layout_features = []
                o.drop_tables += ["GSUB", "GPOS", "GDEF", "BASE", "STAT", "vhea", "vmtx"]
                o.name_IDs = ["*"]
                o.notdef_outline = True
                s = subset.Subsetter(o)
                s.populate(unicodes=hit)
                s.subset(f)
                f.flavor = None
                p = os.path.join(tmp, f"{w}-{len(parts)}.ttf")
                f.save(p)
                parts.append(p)
            m = Merger().merge(parts)
            m.flavor = "woff2"
            m.save(os.path.join(FONT_DIR, out))
            print(f"{out}  조각 {len(parts)}개 · 글자 {len(seen)}자 · {os.path.getsize(os.path.join(FONT_DIR, out)) // 1024}KB")
        lic = tar.extractfile("package/LICENSE").read()
        open(os.path.join(FONT_DIR, "LICENSE-NotoSerifKR.txt"), "wb").write(lic)
    print(f"원본 @fontsource/noto-serif-kr {ver} (SIL OFL 1.1)")
    return check()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="회사 공식 양식 명조 서브셋")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    sys.exit(check() if a.check else build())
