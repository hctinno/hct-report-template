# hct-report-template agent instructions

## Purpose

This repository is the HCT shared presentation design system, called **Blue Report**. One source produces HTML, PDF, and PowerPoint decks, and the rules are enforced by a script rather than by eye.

`docs/CODEX_DECK_PROMPT.md` is the full step-by-step work order, written for agents that cannot load `.claude/skills/`. Read it before starting deck work; the rules below are its summary.

## Working rules

- Work in the current checkout root. Paths here are relative to it — never assume a specific drive or directory.
- Read `.claude/skills/blue-report/README.md` first. It is the self-contained spec: color tokens, type scale, spacing, chart rules, and writing style. `.claude/skills/blue-report/references/rules.md` is the condensed rule list.
- Start from a finished deck in `.claude/skills/blue-report/assets/`, replacing content only. Do not invent a new visual style.
  - `deck-internal-report.html` internal monthly reporting
  - `deck-weekly-report.html` organisation-wide weekly reporting (no agenda slide; weekday timeline)
  - `deck-sales-proposal.html` external proposal and sales
  - `deck-project-report.html` project kickoff and completion
  - `deck-training.html` training and technical explanation
  - `deck-template.html` catalog of all 12 layouts
- Ask the user which purpose applies before choosing a deck when the request does not make it obvious.
- Hard rules: use `--br-*` CSS custom properties only and add no raw hex; donut charts only, never pie; Korean body copy in 개조식 (noun-ending) form; slides are exactly 1920x1080; no text below 24px; the brand mark stays in the top-right margin band and body content never intrudes there.
- Write output to `decks-out/`, which is gitignored. Do not scatter result files in the checkout root.
- Save Korean text as UTF-8 and treat mojibake patterns such as `???`, `濡`, `湲`, `遺`, `媛`, `李` as blocking corruption.
- Preserve user changes. Inspect `git status` before editing.
- Do not commit, push, reset, or delete branches unless the user explicitly requests it.
- Never print or store API keys, tokens, cookies, or passwords.

## Generators and checks

Python and Node only — no Claude Code dependency. Use `python3` on macOS and Linux.

```bash
# Whole-repository check. Required after changing templates, scripts, or docs.
# CI runs exactly this on every push and pull request.
python scripts/verify_repo.py

# Machine-checked rules for a single deck. Required before reporting a deck complete.
python .claude/skills/blue-report/scripts/check_deck.py decks-out/deck.html

python .claude/skills/blue-report/scripts/apply_brand.py --brand brand/hct/brand.json --deck internal --single-file -o decks-out/deck.html
python .claude/skills/blue-report/scripts/to_pdf.py decks-out/deck.html
node   .claude/skills/blue-report/pptx/build.js --brand brand/hct/brand.json --out decks-out
```

`check_deck.py` enforces ten rules mechanically: banned sentence endings, pie charts, donut dasharray arithmetic, off-token hex, slide size, minimum font size, 2:1 contrast for data marks, brand-mark presence, mark/body overlap, and logo variant against background luminance. Its report is the completion evidence for deck work — a run with failures is not "done".

`verify_repo.py` builds all five decks, runs `check_deck.py` on each, builds the four PPTX
files, re-derives `dist/` and compares it against what is committed, scans Korean text for
mojibake, and validates the plugin manifests. It exits 1 if anything fails. `.github/workflows/verify.yml`
runs the same single command, so local and CI results cannot diverge.

If you change `assets/`, rebuild `dist/` and commit it: `build_single_file.py` once with no
arguments, once with `--artifact --brand brand/hct/brand.json`. The dist check fails otherwise.

PPTX content lives separately in `pptx/content.js`. The HTML decks are the source of truth, so change both when content changes. Colors cannot drift because `pptx/tokens.js` parses `assets/blue-report.css`.

The two content sources are deliberately not merged: hand-editing the HTML decks is how this system is used, and generating the HTML from data would remove that. Drift is caught mechanically instead — `scripts/check_content_sync.py` compares slide counts, deck titles, all 36 speaker notes, bar names and values, donut legends, and table headers and rows across both sources, and names the deck, slide, and field that diverged. `verify_repo.py` and CI run it, so changing only one side does not pass.

## Reporting

Write reports in Korean. Include the commands you ran, the pass/warn/fail counts from `check_deck.py`, and the output paths. If you did not run the check, say so — do not write "완료" without it.
