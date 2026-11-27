# HCT 브랜드 자산

블루 리포트 발표 템플릿에 쓰는 회사 자산이다. 사내 보고서용이라 연락처는 넣지 않는다.

## 파일

| 파일 | 용도 |
|---|---|
| `hct-logo-source.png` | 2016 CI 로고(HCT + (주)에이치시티) 원본을 흰 바탕에 놓은 것. 573×245, 로고 영역 493×165 |
| `hct-logo-white.png` | 흰색 녹아웃. **표지 · 마무리 패널 · 간지 등 짙은 면 전용** |
| `hct-logo-color.png` | 흰 배경을 투명으로 뺀 원색판. 밝은 지면용 |
| `hct-logo-symbol-white.png` · `hct-logo-symbol-color.png` | 국문 병기를 뗀 심볼만 — 배경 워터마크용 |
| `brand.json` | 회사명 · 워드마크 · 저작권 설정 |

1.57.0 에서 로고를 2016 CI 판으로 바꿨다(이전 판은 git 기록에 있다). CI 블루는 `#0054a4` 다.

## 왜 두 가지인가

표지 · 간지의 짙은 면은 딥네이비 `#071b45`(A · C)와 딥 블루 `#08275e`(H 패널)다.
로고 원색 `#0054a4` 는 딥네이비 대비 **2.24 : 1**로 거의 보이지 않는다.
밝은 지면 `#f7f9fc` 에서는 7.10 : 1로 충분하다. 그래서 면에 따라 나눠 쓴다.

파생본은 스크립트로 만들었고 재실행하면 같은 파일이 나온다. 투명 배경 PNG 도 받는다(흰 바탕에 먼저 합성한다).

```bash
python3 .claude/skills/blue-report/scripts/make_logo_variants.py \
        brand/hct/hct-logo-source.png --out-dir brand/hct --name hct-logo
```

## 덱 만들기

```bash
python3 .claude/skills/blue-report/scripts/build_deck.py <보고서>/deck.yaml \
        --brand brand/hct/brand.json --single-file -o decks-out/<보고서>.html
```

## 확인이 필요한 것

- 원본 로고 영역이 **493×165px**이다. 화면 발표(1920×1080에서 58~64px 표시)에는 충분하지만
  인쇄 · 큰 확대에는 **SVG 또는 고해상도 원본**으로 바꾸는 것이 낫다.
- 흰색 녹아웃은 원본에서 파생한 것이다. 사내 브랜드 가이드에 별도 반전 로고가 있으면 그것으로 교체한다.

## 강조색

`blue-report.css` 의 `--br-cobalt` 가 HCT CI 블루 `#0054a4` 다(1.57.0 — 이전 `#2f4a9c`, 그 전 블루 리포트 기본 `#1140d6`).
스타일 H 의 깊은 면은 `--br-deep` `#08275e` 하나다. 바꿀 일이 생기면 `.claude/skills/blue-report/assets/blue-report.css`
의 해당 줄만 고친다. 슬라이드에는 hex 를 직접 적지 않으므로 그 줄이 전부다(PPT 는 `pptx/tokens.js` 가 같은 파일을 읽는다).
