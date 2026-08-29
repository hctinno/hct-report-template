#!/usr/bin/env python3
"""블루 리포트 팔레트 계산기 — 단조 램프 생성과 대비 검증.

블루 리포트의 두 규칙을 코드로 강제한다.
  - 데이터 마크는 지면 대비 2:1 이상
  - 인접 구간 같은 색 금지, 값이 클수록 진한 단조 램프

라이브러리로도, CLI로도 쓴다.

    python3 palette.py --check                 # 토큰 팔레트 전체 대비표
    python3 palette.py --steps 7               # 밝은 지면용 7단계 램프
    python3 palette.py --steps 5 --dark        # 다크면용 5단계 램프
"""
import argparse

PAGE = "#f4f6f8"
DARK = "#101827"
COVER = "#071b45"

# 램프 양 끝. 밝은 끝은 지면 대비 2.10:1로, 2:1 경계를 넘지 않게 고정한다.
LIGHT_ENDS = ("#0b2a6b", "#86b0da")
DARK_ENDS = ("#dbe9ff", "#2a5fc0")

MIN_DATA_CONTRAST = 2.0


def _rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def _hex(t):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(v)))) for v in t)


def luminance(h):
    def f(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = _rgb(h)
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + .05) / (lo + .05)


def ramp(n, dark=False):
    """n단계 단조 램프. 값이 클수록 진한 색이 앞에 온다."""
    if n < 2:
        return [LIGHT_ENDS[0] if not dark else DARK_ENDS[0]]
    a, b = (DARK_ENDS if dark else LIGHT_ENDS)
    ra, rb = _rgb(a), _rgb(b)
    out = [_hex([ra[k] + (rb[k] - ra[k]) * i / (n - 1) for k in range(3)]) for i in range(n)]
    if len(set(out)) != len(out):
        raise ValueError(f"{n}단계는 중복 색을 만든다. 구간을 줄이거나 묶는다.")
    return out


def audit(colors, background, label=""):
    """데이터 색 목록이 대비 규칙을 지키는지 검사한다. 위반 목록을 돌려준다."""
    problems = []
    for i, c in enumerate(colors):
        r = contrast(c, background)
        if r < MIN_DATA_CONTRAST:
            problems.append(f"{label}{c}: 배경 {background} 대비 {r:.2f}:1 — 2:1 미달")
        if i and c == colors[i - 1]:
            problems.append(f"{label}{c}: 인접 구간과 같은 색")
    return problems


TOKENS = {
    "코발트 (강조1)": "#1140d6",
    "시안 (강조2)": "#35b8f0",
    "딥네이비 (깊은 값)": "#0b2a6b",
    "코랄 (핵심 수치)": "#ff7a59",
    "소프트1": "#7fb6f5",
    "소프트2": "#9dc4f2",
    "소프트3": "#a4c4e5",
}


def main():
    ap = argparse.ArgumentParser(description="블루 리포트 팔레트 계산기")
    ap.add_argument("--steps", type=int, help="생성할 램프 단계 수")
    ap.add_argument("--dark", action="store_true", help="다크면(#101827)용")
    ap.add_argument("--check", action="store_true", help="토큰 팔레트 대비표 출력")
    a = ap.parse_args()

    if a.check:
        for bg, name in ((PAGE, "밝은 지면"), (DARK, "다크 정리면"), (COVER, "표지·간지")):
            print(f"\n[{name} {bg}]")
            for k, v in TOKENS.items():
                r = contrast(v, bg)
                mark = "OK " if r >= MIN_DATA_CONTRAST else "미달"
                print(f"  {k:<20} {v}  {r:6.2f}:1  {mark}")
        print("\n※ '미달'은 그 배경의 데이터 마크로 쓰지 않는다. 텍스트·장식에는 별도 기준을 적용한다.")

    if a.steps:
        cols = ramp(a.steps, dark=a.dark)
        bg = DARK if a.dark else PAGE
        print(f"\n{a.steps}단계 램프 (배경 {bg})")
        for i, c in enumerate(cols):
            print(f"  {i+1}. {c}   대비 {contrast(c, bg):5.2f}:1")
        bad = audit(cols, bg)
        print("  판정:", "전 단계 통과" if not bad else "위반 " + "; ".join(bad))
        print("\n  CSS:", " ".join(cols))

    if not a.check and not a.steps:
        ap.print_help()


if __name__ == "__main__":
    main()
