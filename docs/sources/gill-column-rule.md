# Gill BSB/Tegg: printed inter-column rule and gutter, pp. 896–915

- For: the architect and the goat-yard architect, before Golden Chain pins `substrate-v0`. This is goat-yard addition 2, 2026-10-25.
- Status: measured, **not yet signed**. The architect signs from the pixels; the gutter strips are listed under "Sign-off".
- This is a measurement on pixels, not an OCR step. No text layer was read (the pages have none: one image object each), no model saw any image, and no goat-yard code was used.

## Result

| Item | Result |
|---|---|
| n | 20 pages: printed 896–915, PDF pages 949–968 (PDF page = printed + 53) |
| Rule present | **20 / 20** (run 2) |
| Rule kind | **single** on every ruled slab. No double rule was found anywhere. |
| Rule width | median 14 px = **1.19 pt** (p5–p95 11–19 px; range 10–25) |
| Inter-column gutter (text edge to text edge) | median 131 px = **11.1 pt** (p5–p95 115–145 px; range 62–544) |
| White on each side of the rule | left median 58 px (4.9 pt); right median 59 px (5.0 pt) |
| Flagged for a look | p. 896 only (chapter opening: 9 of 14 interior slabs ruled) |

The gutter distribution is **unimodal**, n = 312 ruled slabs. Bin counts, edges in px:

| 0–80 | 80–100 | 100–110 | 110–120 | 120–125 | 125–130 | 130–135 | 135–140 | 140–145 | 145–150 | 150–170 | 170–200 | 200–600 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | 4 | 1 | 26 | 35 | 64 | 91 | 52 | 20 | 7 | 8 | 0 | 2 |

The 12 outliers (under 100 px or over 160 px) are slabs where one flank is unusually narrow (2–16 px: a mark intruding into the gutter) or wide (138 and 469 px: a short or ended column). The other four are p. 896's wider gutter (163–166 px, with about 80 px of white on the left).

## Per page (run 2)

| Page | T | Ruled / interior slabs | Median rule width (px) | Median gutter (px) |
|---|---|---|---|---|
| 896 | 0.525 | 9/14 (flag) | 13 | 160 |
| 897 | 0.55 | 16/16 | 14 | 132 |
| 898 | 0.575 | 16/16 | 13.5 | 121.5 |
| 899 | 0.55 | 16/16 | 12 | 129.5 |
| 900 | 0.55 | 16/16 | 15 | 132 |
| 901 | 0.55 | 16/16 | 13 | 129.5 |
| 902 | 0.55 | 16/16 | 14.5 | 127 |
| 903 | 0.55 | 16/16 | 16 | 134.5 |
| 904 | 0.55 | 16/16 | 13 | 128.5 |
| 905 | 0.55 | 16/16 | 13 | 135.5 |
| 906 | 0.55 | 16/16 | 16 | 133 |
| 907 | 0.575 | 16/16 | 18 | 135 |
| 908 | 0.55 | 16/16 | 13 | 133 |
| 909 | 0.55 | 16/16 | 14 | 128.5 |
| 910 | 0.55 | 16/16 | 14 | 134 |
| 911 | 0.575 | 16/16 | 14 | 124.5 |
| 912 | 0.55 | 16/16 | 14 | 129.5 |
| 913 | 0.55 | 16/16 | 14 | 128.5 |
| 914 | 0.55 | 16/16 | 12 | 125.5 |
| 915 | 0.55 | 15/15 | 15 | 132 |

## Method

The code is [tools/column_rule.py](../../tools/column_rule.py) (numpy, pypdfium2). It is deterministic: no randomness and no model.

1. **Bitmap.** Each page is one 1-bit CCITT image, 5100 × 7650 px at 850 dpi (6 × 9 in). The run takes the native bitmap, with no re-rendering. This scan decodes paper as 0, so ink is value > 127.
   - The run fails loud on any other page structure, on ink within the 50-px border, or on an ink fraction outside 0.02–0.4.
2. **Slabs.** Pages are cut into slabs of 400 rows. The search band is x ∈ [0.35 W, 0.65 W]. The skew is about 0.33°, which is ≤ 2.3 px within a slab.
3. **Threshold T (mode-midpoint).** For each slab and column, f is the fraction of rows inked. T is the midpoint between two modes in the page's 20-bin histogram of nonzero f:
   - the low mode, from text;
   - the highest local maximum in the upper half, from the rule.
   - If no such peak stands above a valley, the method **abstains**: no rule is detected.
4. **Rule.** Columns with f ≥ T are grouped into clusters, merged across gaps of ≤ 1 px. Each cluster is grown to its contiguous inked block.
   - The rule is the block with the most white on both sides.
   - A second isolated block, across a gap narrower than its own outer white, would make the rule *double*.
5. **Gutter.** The white run left of the rule, plus the rule width, plus the white run right of it, per two-column slab.
6. **Coverage.** Ruled slabs divided by interior two-column slabs. The outermost two straddle the running head and the block's last line.
   - Present means coverage ≥ 0.5, because a column rule runs the text height and anything shorter is a fragment.
   - A page is flagged below 0.9.

**Calibration** used p. 183 only. It is outside the measured set and is the architect's reference page.
- The calibration fixed one defect: text-stem columns were being taken for the rule. Step 4 now picks the most isolated block.
- Before calibration, one coarse column profile of p. 905 had been printed. That page is in the set.

## Runs and predictions

**Predictions**, locked at 2026-10-25T19:34:29Z, before run 1:

| | Prediction | Run 2 |
|---|---|---|
| Architect | a rule on all 20 | **held**: 20 / 20 |
| P1 | present on 20 / 20 | **held** |
| P2 | single rule everywhere | **held** |
| P3 | median rule width per page 12–16 px | **missed on p. 907** (18 px) |
| P4 | median gutter per page 125–145 px | **missed on p. 896** (160) **and p. 898** (121.5) |
| P5 | at most p. 896 flagged | **held** |

**Run 1** (script sha256 `6f08535f…`, 2026-10-25T19:34:29Z): 17 present, **3 abstained** (pp. 897, 898, 902). Of record, and a finding.
- **Cause: a defect in the mode finder, not in the page.** The high mode was the upper half's argmax. On those three pages the text tail in the half's first bin (56, 102 and 73 columns) outweighed the rule bin (f ≥ 0.95: 36, 99 and 56 columns). The method therefore found no valley.
- Two pieces of evidence show the rule was there:
  - the rule bin was populated;
  - the "gutters" measured on those pages were 53–66 px, the width of one flank, so a narrow feature was splitting the white.

**Run 2** (script sha256 `f5760f3b…`, 2026-10-25T19:35:27Z; PDF sha256 `cdfd7fdc…`; Python 3.11.1, numpy 2.4.6, pypdfium2 5.14.0).
- v2 changes only the high-mode choice: the highest local maximum.
- It was a clean full rerun of all 20 pages under the same predictions. p. 183 is unchanged under v2.

## Consequence for goat-yard

- Under run 2, **no page lacks a rule**, so the conditional "column split without a rule" request is **not triggered**. This waits on the architect's sign-off on pp. 897, 898 and 902, the run-1 abstentions.
- **Finding: single rule, not double.** goat-yard's fix A locates a printed **double** rule; this setting prints a **single** rule of about 1.2 pt on every ruled slab of all 20 pages.
  - Whether fix A accepts or abstains on a single rule is goat-yard's question. Chris sent it to the goat-yard architect on 2026-10-26; we do not wait on the tag to find out.

### Evidence for a request, if one is needed

If fix A abstains on a single rule, the request file is
`REQUEST_goldenchain_<date>.md` at goat-yard's `docs/requests/`, titled
"column split on a single rule". It carries, from this file:

- n = 20 (printed 896–915), the method above, and the run headers (script and PDF sha256);
- the Result table: rule present 20/20, single on 20/20, rule width median 14 px = 1.19 pt;
- the per-page table (run 2): ruled and interior slabs, median rule width, median gutter per page;
- the gutter distribution: unimodal, median 131 px = 11.1 pt, n = 312 ruled slabs, with the bin counts;
- the run-1 abstentions (pp. 897, 898, 902) and their cause, so no wrong-pass is hidden.

The request is not filed until the architect signs from pixels and the goat-yard answer is in.

## Sign-off (architect, from pixels)

- Gutter strips for pp. 896–915: band x ∈ [0.35 W, 0.65 W], full height, scaled 1:2, local viewing only. They are not in git: `C:\Users\cnogr\.golden-chain\column-rule-2026-10-25\strips\gutter-p{896..915}.png`.
- Full results JSON and logs are in the same folder: `run2\column_rule.json` and `run1\`. `predictions-locked.txt` is there too.
- To sign, write: n = 20, rule present on __ / 20, single on __ / 20, signed __ (one sitting, date).
