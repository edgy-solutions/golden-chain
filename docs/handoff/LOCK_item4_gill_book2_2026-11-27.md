# Lock: item 4, Gill Doctrinal Book II (II.5 and the covenant chapters) and Practical Book II, read by machine (2026-11-27)

- **Locked:** 2026-11-27. Committed before any tool for this item is written and before any page is processed. Git history seals it. This file is never edited; misses are recorded in the report.
- **On:** the two-day order, Day 2, item 4 ([RULING_report_31.md](RULING_report_31.md)): "Under the standing pin rules (column rule, narrow-glyph margin, line height reported): OCR and v4 slant on Doctrinal Book II (the covenant chapters and II.5) and Practical Book II. Report counts and the pool rates of words that do not crop cleanly. No text enters the repo. Draw nothing for signing yet."

## The pages (read from the BSB contents, PDF pp. 16-17, viewed to locate only)

| Range | Printed pages | PDF pages | Chapters |
|---|---|---|---|
| D-a | 201-209 | 254-262 | Doctrinal II.5, "Of Adoption as an Immanent Act" (p. 201), with its unnumbered "Of Justification as an Immanent Act" (p. 203). II.6 begins on p. 209. |
| D-b | 214-250 | 267-303 | Doctrinal II.7-II.15: every Book II chapter with "Covenant" in its contents title. II.7 begins on p. 214. II.16 begins on p. 250. |
| P | 852-895 | 905-948 | Practical Book II, all six chapters. Practical III.1 begins on p. 896. |

- **Total: 90 pages.** The pages where a chapter starts or ends are taken whole (pp. 209, 214 and 250 carry part of a neighbouring chapter).
- **The choice of "the covenant chapters" is the build agent's:** II.7-II.15 by title. II.6 (the everlasting council) and II.16 (complacency) are left out. The architect may widen it.
- **No page above 895** is opened, by any tool. The new OCR tool refuses one in code.

## Method

1. **Pin rules, per range:**
   - `tools/gy_locate_column_rule.py` at the native frame (5100 x 7650, the line-height-matched frame), with goat-yard's S1 line height reported;
   - `tools/gy_narrow_glyph.py`, with the margin reported against `RULE_RUN_MAX_W` (8 px).
   - Both are unchanged.
2. **OCR:** a new tool, `tools/gy_ocr_pages.py`.
   - It is the baptism OCR (`tools/gy_ocr_baptism.py`: the same frame, regions, engines, DPI, PSM and matching), imported, not copied, with three differences:
     - there is **no CCEL alignment**;
     - there is **no candidate draw**;
     - a page whose column rule is not located is recorded and skipped, not fatal.
   - It is run twice: one run for Doctrinal (D-a and D-b, 46 pages) and one for Practical (P, 44 pages).
3. **Slant:** `tools/gy_word_slant_v4.py`, unchanged, once on each OCR run.
4. **Pool rates:** a new tool, `tools/pool_rates.py`.
   - It takes every eligible word of a v4 slant run, sorts it into a stratum by `truthset_v2.stratum` (slanted, upright, edge), and applies the crop check `truthset_crops_v5.crop_check` (v4's rule C) to each.
   - It writes **counts and shares only**: per stratum, per range and per side. It writes no key, no text and no crop.
   - Nothing is drawn.
5. **Where it runs:**
   - Every run is made from a separate golden-chain worktree at a pushed commit, so the main checkout can take commits meanwhile.
   - Every run must be `clean_run`.
   - Outputs go to `~/.golden-chain/item4-*` (local, never committed).
6. **Tests:** the two new tools are born with tests. No existing test is changed. If one would have to change, the change goes to a hold/ branch.

## Baselines (the baptism chapter, pp. 896-915)

- OCR run 1 (`00cb18e0`): 18 150 words on 20 pages (907 a page); legacy match 0.9727.
- v4 slant (`f25ea51e`): T = 0.11; 700 slanted of 12 474 rows (5.6 %).
- Pool fail shares (report 21): slanted 9.98 %, upright 6.36 %, edge 0 of 7.
- Narrow-glyph margin: narrowest 10 px, margin 2 px.

## Predictions

| # | Prediction |
|---|---|
| K1 | The column rule is located (status ok) on **90 of 90** pages. |
| K2 | goat-yard's S1 median page line height is inside its 49-61 px design band on every range. The median over all 90 pages is **53-57 px**. |
| K3 | Narrow glyphs: **0** line-final text runs of 8 px or less inside the gutter window, on all 90 pages. The margin is **at least 1 px** on every range. |
| K4 | OCR: **800-1000 words a page** on each run. |
| K5 | Legacy match fraction **≥ 0.95** on each run. |
| K6 | v4 slant is **bimodal** on both runs: the tool makes a slanted call, and does not leave every row uncalled. |
| K7 | The threshold T is **0.08-0.14** on both runs. |
| K8 | Slanted share of the measured rows: **Doctrinal 5-15 %**, **Practical 3-10 %**. |
| K9 | Pool fail shares: **slanted 5-15 %** and **upright 3-12 %** on each run. Edge is reported with no prediction, because its pool is small. |
| K10 | Every run is `clean_run`. |
| K11 | The full suite passes with the new tests, and no existing test is changed. |
