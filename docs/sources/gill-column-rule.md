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
| P4 | median gutter per page 125–145 px | **missed on pp. 896** (160), **898** (121.5) **and 911** (124.5) |
| P5 | at most p. 896 flagged | **held** |

**Run 1** (script sha256 `6f08535f…`, 2026-10-25T19:34:29Z) found 17 rules and **abstained on 3 pages** (pp. 897, 898, 902). The cause was a defect in the mode finder, not in the pages. The high mode was taken as the upper half's argmax. On those three pages the text tail in that half's first bin (56, 102 and 73 columns) outweighed the rule bin (f ≥ 0.95: 36, 99 and 56 columns), so no valley was found. Two things showed the rule was there: the rule bin was populated, and the "gutters" measured were 53–66 px, the width of one flank, so a narrow feature was splitting the white. The fix (v2) changes only the high-mode choice, to the highest local maximum. Run 2 is a clean rerun of all 20 pages under the same locked predictions, and p. 183 is unchanged under v2. Run 1 stays of record, as a finding.

**Run 2 header:** script sha256 `f5760f3b…`; 2026-10-25T19:35:27Z; PDF sha256 `cdfd7fdc…`; Python 3.11.1, numpy 2.4.6, pypdfium2 5.14.0.

**Findings (ruling Q22): build-agent predictions P3 and P4 missed.** Neither is fixed or re-predicted.
- P3 predicted a median rule width of 12–16 px on every page. Measured: 19 pages in range and **p. 907 at 18 px**.
- P4 predicted a median gutter of 125–145 px on every page. Measured: 17 pages in range, and three out: **p. 896 at 160 px**, **p. 898 at 121.5 px** and **p. 911 at 124.5 px**. p. 911 was left out of the miss list until 2026-10-26, when this paragraph was checked against the per-page table. That omission is also a finding.

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

## goat-yard `locate_column_rule` at substrate-v0 (2026-10-26)

Asked by goat-yard (response of 2026-10-26, [goat-yard.md](goat-yard.md)) before any OCR.

**Run header.**
- Tool: [`tools/gy_locate_column_rule.py`](../../tools/gy_locate_column_rule.py), sha256 `aa57288b…`, run once at 2026-10-26T00:50:15Z. A later edit added only the module-set guard (`SUBSTRATE_MODULES`, report 5), so the file's current sha differs from the run's.
- PDF sha256 `cdfd7fdc…`.
- goat-yard: worktree at tag `substrate-v0`, commit `3d0b03e0`, clean; `verse_regions.py` sha256 `3cfe1062…`; geometry config hash `bf928b83759beb26`.
- Python 3.11.1, numpy 2.4.6, pypdfium2 5.14.0, pillow 13.0.0.

**Method.** goat-yard code is used unchanged, imported from the worktree, never copied:
1. The page's embedded image (5100 × 7650 px, about 850 dpi) is written as an 8-bit grey PNG. It is **not rescaled**; goat-yard's vol. 1 frame is 3584 × 5400.
2. `build_page_geometry.process_page` (its default `presplit`) gives the geometry record.
3. `page_ink` gives the ink mask.
4. `locate_column_rule` is called on the mask and the record.

Constants as pinned: `RULE_COL_FRAC` 0.59, `RULE_STRIP_PX` 300, `RULE_Y_TOP_PX` 700, `RULE_SEARCH_PX` 300, `RULE_MAX_RESID_PX` 15, `RULE_MIN_STRIP_FRAC` 0.5, `INK` 110.

`presplit` found **no horizontal rule** on any page (`rules` = [None, None]; the BSB has no footnote rule). The body window therefore ends at H − 300 = 7350, which gives 22 strips per page.

A smoke run on p. 183 (the calibration page, outside the set) came first: ok, 22/22, half_w 4.5, residual 8.6.

| Page | Status | Strips with a cluster | half_w (px) | Max residual (px) | Slope | xdiv |
|---|---|---|---|---|---|---|
| 896 | ok | 11/22 | 4.0 | 2.1 | 0.000348 | 2558 |
| 897 | ok | 22/22 | 3.0 | 9.5 | -0.005156 | 2566 |
| 898 | ok | 22/22 | 4.5 | 7.7 | 0.003287 | 2435 |
| 899 | ok | 22/22 | 3.5 | 8.7 | -0.001901 | 2556 |
| 900 | ok | 22/22 | 5.0 | 7.4 | 0.001345 | 2433 |
| 901 | ok | 22/22 | 3.5 | 11.7 | -0.001176 | 2557 |
| 902 | ok | 21/22 | 4.0 | 6.9 | 0.009645 | 2456 |
| 903 | ok | 22/22 | 5.5 | 11.6 | 0.001071 | 2549 |
| 904 | ok | 22/22 | 4.0 | 3.1 | -2.9e-05 | 2426 |
| 905 | ok | 22/22 | 4.0 | 5.1 | -0.002395 | 2556 |
| 906 | ok | 22/22 | 5.0 | 13.3 | -0.003415 | 2407 |
| 907 | ok | 21/22 | 5.0 | 8.3 | 0.003896 | 2571 |
| 908 | ok | 21/22 | 4.0 | 5.4 | -0.004714 | 2411 |
| 909 | ok | 22/22 | 4.5 | 5.3 | -0.003366 | 2571 |
| 910 | ok | 22/22 | 4.0 | 12.6 | -0.002221 | 2417 |
| 911 | ok | 22/22 | 4.5 | 7.9 | 0.005134 | 2580 |
| 912 | ok | 22/22 | 4.0 | 7.6 | -0.002086 | 2420 |
| 913 | ok | 22/22 | 4.2 | 5.8 | -0.001911 | 2564 |
| 914 | ok | 22/22 | 4.0 | 6.5 | 0.001614 | 2437 |
| 915 | ok | 22/22 | 5.0 | 7.7 | -0.004015 | 2556 |

**Against the prediction locked 2026-10-26 (before the run):**

| Clause | Result |
|---|---|
| 20/20 status ok | **Held.** No abstention, so no request file is triggered. |
| Max residual ≤ 15 px | **Held.** Worst is 13.3 px on p. 906, 1.7 px inside the limit. |
| Every strip carries a cluster | **FALSIFIED: 14 of 440 strips are empty, on 4 pages.** |

**Ruling on report 4.**
- **The run PASSES goat-yard's criteria, 20/20.** On every page, n_rule ≥ 3, n_rule / n_strips ≥ 0.5, and residual ≤ 15 px. The lowest is p. 896, at 11/22 = 0.50.
- **The third clause is FALSIFIED.** It was the architect's, and stricter than goat-yard's acceptance. It stays as locked and is never edited.
- The 14 empty strips are a finding, not a defect.

The 14 empty strips (peak column ink fraction in the search window against the 0.59 cut):
- **p. 896, strips 700–3700 (10 strips):** peaks 0.00–0.53. p. 896 is the page run 2 flagged (9/14 ruled slabs). The empty strips are the upper body.
- **The last strip, 7000–7300, on pp. 896, 902, 907, 908:** peaks 0.52, 0.44, 0.45, 0.55. All are below 0.59.

Not established by the run; pixels decide (below): whether the rule ends inside the last strip (so ink is diluted by the window ending at 7350), or is present but too faint for 0.59.

**Width.** `locate_column_rule` widths (columns with fraction ≥ 0.59 in a 300-row strip) have medians of 6–11 px (half_w 3.0–5.5). Run 2's per-row rule-width medians were 12–18 px. These are different measures. The slanted rule (|slope| up to 0.0096 on p. 902, about 3 px of drift per strip) spreads its ink across more columns than any one column holds at 0.59. That is the `RULE_COL_FRAC` risk goat-yard named. Observation only; nothing is changed.

Results are in `~/.golden-chain/gy-locate-column-rule-2026-10-26/` (outside the repo). Per-strip column fractions are stored for every page, so a request file can be written without a rerun.

### Empty-strip hypotheses (ruling on report 4)

Locked 2026-10-26T01:03:32Z, before any measurement or render, in `~/.golden-chain/gy-empty-strips-hypotheses-locked.txt`:
- **H1.** p. 896 is the chapter opening. The head spans both columns and the rule starts below it, so the empty strips cover the head. The split there is the fitted line, extrapolated, which is harmless.
- **H2.** The last strips on 896, 902, 907 and 908 are only partly ruled because the rule ends above the page foot. That is a strip-boundary artefact. If instead the rule runs to the bottom and is faint, the 0.59 cut is biting, and that is the first request file.

**Measure** (in code: [`tools/signing_strips.py`](../../tools/signing_strips.py)):
- The window is the run's own fit, c(y) ± (half_w + pad).
- A row is *ruled* when its ink count in the window is ≥ 2·half_w.
- F is the first y ≥ 700 with ≥ 45 of rows [y, y+49] ruled.
- L is the last y with ≥ 45 of rows [y−49, y] ruled.
- By that definition F falls 5 rows before a rule's start, and L 5 rows after its end. The born tests assert exactly that.

Run 2026-10-26T01:05:11Z. Script sha256 `d5679fdb…`, run JSON sha256 `3bc98694…`.

| Clause (locked) | Page | Measured | Result |
|---|---|---|---|
| H1: F(896) ∈ [3400, 3700) | 896 | F = 3059 | **missed** (341 rows early) |
| H2: L ∈ [7000, 7300) | 896 | 7112 | held |
| | 902 | 6921 | **missed** (ends above 7000) |
| | 907 | 6448 | **missed** (ends above 7000) |
| | 908 | 6896 | **missed** (ends above 7000) |
| H2: ruled fraction of 7000–7299 within 0.10 of the peak | 896 | 0.363 vs 0.523 | **missed** |
| | 902 | 0.050 vs 0.443 | **missed** |
| | 907 | 0.013 vs 0.447 | **missed** |
| | 908 | 0.313 vs 0.550 | **missed** |
| H2 falsifier: L ≥ 7300 on any of the four | all four | max L 7112 | **did not fire** |
| Control: L ≥ 7177 on the other 16 | 16 pages | 15 held; **p. 911 L = 7160** | **missed on 911** |

Reading. These numbers support only; pixels decide.
- **H2's direction holds, and more strongly than predicted.** By this measure the rule never runs to the foot on any of the four pages.
  - On 902, 907 and 908 it ends before the last strip begins.
  - So the 0.44–0.55 column peaks in that strip are **not** the rule at the fitted line. What carries them is not known.
- **H1's number missed.**
  - On p. 896, ruled rows begin at 3059, inside strip 2800–3100.
  - Yet strips 3100 and 3400 are empty to `locate_column_rule`. Their peaks are 0.30 and 0.50.
- These are divergences from locked numbers, so they are findings (rule 6). Nothing is re-predicted.

**Strips for Chris** (local viewing only, never sent to a hosted model; not in git): `C:\Users\cnogr\.golden-chain\gy-locate-column-rule-2026-10-26\strips-for-signing\`.
- `p896-gutter-full.png`: whole height.
- `p896-foot.png`, `p902-foot.png`, `p907-foot.png`, `p908-foot.png`: rows 6700–7649.
- `p897-gutter-full.png`, `p898-gutter-full.png`: the run-2 abstentions, still unsigned.
- Each strip is 600 px wide, centred on xdiv, at native scale.
- Overlays (`README.txt` there):
  - red ticks: the cluster centre per strip;
  - blue dots: the fitted band edges;
  - green ticks: strip boundaries;
  - magenta ticks: y_end = 7350.
- `ruled_rows.json` there holds F, L and the ruled fractions for all 20 pages.

Sign-off form for these strips: [../handoff/SIGNOFF_empty_strips.md](../handoff/SIGNOFF_empty_strips.md).

## Sign-off (architect, from pixels)

- Gutter strips for pp. 896–915: band x ∈ [0.35 W, 0.65 W], full height, scaled 1:2, local viewing only. They are not in git: `C:\Users\cnogr\.golden-chain\column-rule-2026-10-25\strips\gutter-p{896..915}.png`.
- Full results JSON and logs are in the same folder: `run2\column_rule.json` and `run1\`. `predictions-locked.txt` is there too.
- To sign, write: n = 20, rule present on __ / 20, single on __ / 20, signed __ (one sitting, date).
