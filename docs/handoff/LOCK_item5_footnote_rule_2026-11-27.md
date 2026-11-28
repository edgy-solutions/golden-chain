# Lock: item 5, a geometry rule that separates column footnotes from body text on the baptism chapter (2026-11-27)

- **Locked:** 2026-11-27. Committed before the tool for this item is written and before any line statistic of the chapter is computed. Git history seals it. This file is never edited; misses are recorded in the report.
- **On:** the two-day order, Day 2, item 5 ([RULING_report_31.md](RULING_report_31.md)): "Footnotes. Design and measure, under a lock, a rule that separates column footnotes from body text on the baptism chapter, from geometry only (position, type height, the boundary). Chris's signed notes on p. 913 and p. 914 are the test cases. Report where it agrees and disagrees with them. Change no OCR output yet."
- **Geometry only.**
  - The rule reads word boxes from OCR run 1 (`~/.golden-chain/ocr-baptism-run1-2026-11-13/ocr.json`, 850 dpi, 5100 x 7650 frame).
  - It reads no word text, renders no page, views no image and reads no crop. Pages 913 and 914 are above 895, so they are never rendered here.
  - Only for the p. 914 test case does it read the keys (no text) of the CCEL-moved blocks in `~/.golden-chain/ccel-align-run1-2026-11-14-a/align.json`. That is how the signed console drew its magenta boundary.
- **No OCR output is changed.** The tool writes only to its own output directory, and it checks that the sha256 of `ocr.json` is the same at its start and its end.

## The rule (fixed here; not tuned after measuring)

1. **Lines.** In each column region (`left`, `right`) of each page, the words are grouped into lines by their OCR (block, paragraph, line) numbers. A line's top is its highest word top, and its bottom is its lowest word bottom.
2. **Type height.**
   - A line's type height is the median height of its word boxes.
   - The **body type height** is the median line type height over every column line of pp. 896-915.
3. **Small.** A line is small if its type height is at most **0.85 x** the body type height.
4. **The zone (position).**
   - Lines are sorted by their top. The walk starts at the column's last line and goes upward.
   - A small line joins the zone. One line that is not small is allowed inside the run.
   - The walk stops at the second line in a row that is not small, or at the top of the column.
   - Lines that are not small are then trimmed from the top of the run.
   - The zone stands only if it has **at least 2 lines**. Otherwise the column has no footnote zone.
5. **The boundary.**
   - The boundary is the top of the zone's first line.
   - The gap there (from the bottom of the line above to the boundary) is reported, next to the column's median line gap. The rule does not use it.
6. **Output.** For each page and column:
   - the line count;
   - the zone's first and last line, as OCR keys;
   - the boundary y;
   - the median type height of the zone, and its ratio to the body type height;
   - the boundary gap.
   No word text is written.

## The two test cases, as signed

| Case | Signed record | What agreement means |
|---|---|---|
| **T1**, p. 914 left | [SIGNED_region_reask_d7a6aab0734ffe3e.md](SIGNED_region_reask_d7a6aab0734ffe3e.md), `p914.left-foot`: "yes" (column footnotes), with the note "the magenta is most of the footnote except one line above it". The magenta top is the top of the first CCEL-moved word in that column. | The zone's first line is the line **directly above** the line that holds that word: an offset of **0 lines** from the note. The offset is reported in lines whatever it is. |
| **T2**, p. 913, both columns | [SIGNED_q11_crops_58b603f5500ae2a8.md](SIGNED_q11_crops_58b603f5500ae2a8.md), `p913-slab16`: "both columns are in the footnote zone here", and "the body text ends above the upper line". Slab 16 is rows 3760-3995 at scale 6.947; at 850 dpi (x 850/500) that is about rows **6390-6789**. | Both columns have a zone. Each zone's boundary is at or above row 6390 + 28 (half a body line), and each zone runs to row 6789 or lower. The note gives no upper bound, so a boundary well above the slab still agrees with it. |

## Predictions

| # | Prediction |
|---|---|
| N1 | T1 agrees: on p. 914 left, the offset is **0 lines**. |
| N2 | T2 agrees on **both** columns of p. 913. |
| N3 | A zone is found in **at least 20 of the 40** columns of pp. 896-915. |
| N4 | The median ratio of zone type height to body type height, over all zones, is **0.60-0.80**. |
| N5 | Of the columns that hold at least one CCEL-moved block, a zone is found in **at least 80 %**. This is a machine reference, not a signed one, and is reported as such. |
| N6 | The sha256 of `ocr.json` is unchanged, and the run is `clean_run`. |
| N7 | The full suite passes with the new tests, and no existing test is changed. |

- **If N1 or N2 misses:** the miss is reported with the rule as locked. A changed rule may be proposed in the report and measured only under a new lock. It is not substituted here.
