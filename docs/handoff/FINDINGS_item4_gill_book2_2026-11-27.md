# Findings: item 4, Gill Doctrinal II.5, II.7-II.15 and Practical Book II, read by machine (2026-11-27)

- **From:** the build agent, 2026-11-27.
- **Lock:** [LOCK_item4_gill_book2_2026-11-27.md](LOCK_item4_gill_book2_2026-11-27.md) (`bd7eb6d`), committed before any tool was written or any page processed.
- **Tools:** `tools/gy_ocr_pages.py` and `tools/pool_rates.py`, born at `5142b73` with 29 tests. The pin tools and `tools/gy_word_slant_v4.py` were not changed.
- **Where it ran:**
  - Pin runs came from a worktree at `bd7eb6d`.
  - OCR, slant and pool ran from a worktree at `5142b73`.
  - Every run was clean at its start and end. Outputs are in `~/.golden-chain/item4-*` (local, not committed).
- **Counts only.** No word text, key, box or crop is in this file or in the repo. No page above printed p. 895 was opened. No image was viewed, and nothing was drawn for signing.

## The lock, scored (never edited)

| # | Prediction | Result | |
|---|---|---|---|
| K1 | column rule located on 90 of 90 pages | At the native frame, which the lock named, **83 of 90**. It abstained on pp. 203, 231, 232, 234, 870, 886 and 895. At the 6.947 frame, **89 of 90** (p. 895: no rule). | **Missed** |
| K2 | S1 median line height inside 49-61 px on every range; median over all 90 pages 53-57 px | At the 6.947 frame, the range medians are D-a **51** [48-59], D-b **52** [48-60] and P **51** [47-60], all inside the band. The median over all 90 pages is **51**, below 53-57. At the native frame the medians are 85, 85 and 85.5 [80-104], outside the band. | **Missed** |
| K3 | 0 line-final text runs of 8 px or less in the gutter window; margin at least 1 px on every range | Margins: D-a **9**, D-b **1**, P **1**. **7** thin runs lie outside the band where the rule's own edge sits (D-b 3, P 4; see below). The machine cannot tell whether they are text. The 7 pages where the native frame abstained were not measured. | **Missed** (0 not shown) |
| K4 | 800-1000 words a page on each run | Doctrinal **955.8** (40 144 words, 46 pages); Practical **911.3** (37 364 words, 44 pages) | **Hit** |
| K5 | legacy match ≥ 0.95 on each run | Doctrinal **0.9746**; Practical **0.9755** | **Hit** |
| K6 | v4 bimodal on both runs | `unimodal` false on both | **Hit** |
| K7 | T 0.08-0.14 on both runs | **0.12** on both | **Hit** |
| K8 | slanted share: Doctrinal 5-15 %, Practical 3-10 % | Doctrinal **5.90 %** (1 620 of 27 443 measured); Practical **6.06 %** (1 564 of 25 809) | **Hit** |
| K9 | pool fail shares: slanted 5-15 %, upright 3-12 % on each run | Doctrinal: slanted **9.07 %**, upright **6.04 %**. Practical: slanted **10.04 %**, upright **6.46 %**. | **Hit** |
| K10 | every run `clean_run` | All 22 outputs are clean at start and end: the pin runs at `bd7eb6d`, and OCR, slant and pool at `5142b73`. | **Hit** |
| K11 | full suite passes; no existing test changed | 957 passed, 1 skipped at `5142b73`; no existing test changed | **Hit** |

## The pool rates: words that do not crop cleanly (v4 rule C)

| Run / range | Slanted fail / pool | Upright fail / pool | Edge fail / pool |
|---|---|---|---|
| Doctrinal, all | 147 / 1 620 (**9.07 %**) | 1 561 / 25 823 (**6.04 %**) | 15 / 158 (9.49 %) |
| D-a (pp. 201-209) | 25 / 318 (7.86 %) | 194 / 4 746 (4.09 %) | 0 / 15 |
| D-b (pp. 214-250) | 122 / 1 302 (9.37 %) | 1 367 / 21 077 (6.49 %) | 15 / 143 (10.49 %) |
| Practical (pp. 852-894) | 157 / 1 564 (**10.04 %**) | 1 566 / 24 245 (**6.46 %**) | 11 / 123 (8.94 %) |
| *Baptism baseline (report 21)* | *9.98 %* | *6.36 %* | *0 of 7* |

Failures by side:
- Doctrinal slanted: top 62, bottom 81, both 4.
- Doctrinal upright: top 847, bottom 693, both 21.
- Practical slanted: top 59, bottom 96, both 2.
- Practical upright: top 948, bottom 606, both 12.

The rates are close to the baptism chapter's. D-a is the lowest on both strata.

## Other counts (no prediction)

- **Pages the OCR skipped:**
  - A page whose column rule was not located was recorded and skipped, as the lock says. These are the native-frame abstentions: Doctrinal 4 (pp. 203, 231, 232, 234) and Practical 3 (pp. 870, 886, 895).
  - So Doctrinal measured 42 of 46 pages, and Practical 41 of 44.
- **OCR italic flags (legacy):**
  - Doctrinal: 1 100 (2.81 % of words).
  - Practical: 1 836 (5.04 %).
- **v4 slant:**
  - Abstentions at the edge: Doctrinal 158, Practical 123.
  - The highest page-column share: Doctrinal 0.0395 (202 left); Practical 0.0537 (859 right).
  - The comb check: Doctrinal reports one "empty between" bin (33); Practical reports none. Neither has a deep dip.

## The narrow-glyph thin runs outside the rule-edge band

On the baptism chapter, every run of 8 px or less in the gutter window starts 7-20 px left of the rule's centre, so it is the rule's own edge. Here, 7 thin runs fall outside that band:

| Range | Page | Offset from rule centre (px) | Width (px) | Gap (px) |
|---|---|---|---|---|
| D-b | 215 | 27 | 8 | 41 |
| D-b | 237 | 22 | 5 | 848 |
| D-b | 237 | 23 | 5 | 1 298 |
| P | 874 | 21 | 4 | 66 |
| P | 879 | 22 | 7 | 55 |
| P | 884 | 50 | 5 | 23 |
| P | 894 | 23 | 8 | 43 |

- Six of the 7 are 1-7 px outside the band. Only p. 884 (offset 50) is clearly away from the rule.
- Telling a glyph from a rule fragment needs a look at the page. That is not done here, because the item draws nothing and no image is viewed for it.

## Errors in the lock (recorded, not corrected)

1. **The frame.** The lock names the native frame (5100 x 7650) as "the line-height-matched frame" for the column rule. The frame the pin rules use for the column rule and the line height is the **6.947** frame (3002 x 4502). OCR and narrow glyphs use the native frame. Both frames were run, and K1 and K2 are scored on the frame the lock named. The 6.947 results are given beside them.
2. **The narrow-glyph baseline.**
   - The lock's baseline says "narrowest 10 px, margin 2 px", from report 13 ("872 text runs, narrowest 10 px").
   - Re-measured from the saved baptism bands with the same tool, the baseline gives **823** text runs, narrowest **9** px, margin **1** px.
   - The difference is not explained here.

## For the architect

1. **K1 and K2 on the governing frame.** Should the frame error be scored as a lock error, with the 6.947 results standing as the measurement? Or should a new lock re-predict them?
2. **K2's band.** The overall median of 51 px is inside the 49-61 design band but below the predicted 53-57. Is 51 the type of these Books, or a sign the band's centre needs moving?
3. **The 7 thin runs.** Should they go to a viewing pass, which is propose-only and outside a sitting? Or should the margin rule exclude a run that sits within a few px of the rule-edge band?
4. **The 7 skipped pages.** Should these pages be read again at the 6.947 frame, where the rule is found on all but p. 895?
5. **The baseline discrepancy** (872/10 against 823/9).
