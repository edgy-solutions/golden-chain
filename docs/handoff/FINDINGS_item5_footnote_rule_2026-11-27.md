# Findings: item 5, a geometry rule for column footnotes on the baptism chapter (2026-11-27)

- **From:** the build agent, 2026-11-27.
- **Lock:** [LOCK_item5_footnote_rule_2026-11-27.md](LOCK_item5_footnote_rule_2026-11-27.md) (`895affc`), committed before the tool was written.
- **Tool:** `tools/footnote_zone.py`, born at `4e2b541` with 15 tests, fixed at `9d6dae3` (see "The first run"). The scored run is from a worktree at `9d6dae3`.
- **Inputs:** OCR run 1 (`~/.golden-chain/ocr-baptism-run1-2026-11-13/ocr.json`, sha256 `00cb18e0…0644c`), and only the moved-block keys of `~/.golden-chain/ccel-align-run1-2026-11-14-a/align.json`. No word text was read or written. No page was rendered, and no image or crop was viewed.
- **Output:** `~/.golden-chain/item5-footnote-zone/zones.json` (local, not committed).
- **Result:** the rule agrees with Chris's p. 914 note and disagrees with the p. 913 note. It finds a zone in only 5 of 40 columns. The footnote type is about 0.84 of the body height, which is just under the locked cut-off of 0.85. So the cut-off, not the walk, is what fails.

## The first run (a tool bug, not a measurement)

- The first run, at `4e2b541`, read the OCR header's `pages_printed` as a list of pages. It is a pair, [896, 915], as `gy_ocr_baptism` writes it. So that run walked only pp. 896 and 915 (4 columns), and found no zone.
- At `9d6dae3` the tool walks every page from first to last. One test was added for this. No existing test was changed, and the rule is unchanged.
- The first run's output is kept locally as `~/.golden-chain/item5-footnote-zone-run0-4e2b541/`. It is not scored.

## The two signed cases

| Case | Signed note | What the rule gives | Agrees? |
|---|---|---|---|
| **T1**, p. 914 left | "the magenta is most of the footnote except one line above it" | The first CCEL-moved word is on line `2.1.2` (index 53, top y 6827). The zone's first line is `2.1.1` (index 52, top y 6729), the line directly above. Offset **0 lines**. The gap above the zone is 149 px, against the column's median line gap of 5 px. | **Yes** |
| **T2**, p. 913 left | "both columns are in the footnote zone here"; "the body text ends above the upper line" (slab 16, about rows 6390-6789 at 850 dpi) | A zone of 9 lines, boundary y **6523**, bottom y 7300. The boundary is 133 px below the slab's top (the lock allows 28). So the rule puts the slab's upper part in the body, which the note says is footnote. | **No** |
| **T2**, p. 913 right | as above | **No zone.** | **No** |

## The lock, scored (never edited)

| # | Prediction | Result | |
|---|---|---|---|
| N1 | T1 offset 0 | offset 0 | **Hit** |
| N2 | T2 agrees on both columns of p. 913 | left: boundary 6523 > 6418; right: no zone | **Missed** |
| N3 | a zone in at least 20 of 40 columns | **5 of 40**: 909 right, 910 left, 910 right, 913 left, 914 left | **Missed** |
| N4 | median zone ratio 0.60-0.80 | **0.840** (the five zones: 0.833-0.846) | **Missed** |
| N5 | a zone in at least 80 % of the columns holding a CCEL-moved block (machine reference) | **5 of 11** (45 %) | **Missed** |
| N6 | `ocr.json` sha256 unchanged; `clean_run` | unchanged; clean at start and end (`9d6dae3`) | **Hit** |
| N7 | full suite passes with the new tests; no existing test changed | 973 passed, 1 skipped at `9d6dae3`. The fix added one test; none of the 15 was changed | **Hit** |

- Body type height (median word-box height of all column lines, pp. 896-915): **78 px**. The cut-off is 0.85 × 78 = 66.3 px.
- The five zones' median type heights are 65-66 px. They pass the cut-off by less than 1.5 px.

## What the misses show

- **The cut-off is too close to the footnote type.** Measured by OCR word-box height, the footnote type is about 0.84 of the body, not the 0.60-0.80 the lock expected. A cut-off at 0.85 sits inside the spread of footnote lines. Where a footnote line's boxes come out a pixel or two taller, the walk counts two of them as "not small" in a row, and the zone stops or never forms. That fits p. 913: the right column has no zone, and the left zone starts 133 px below the slab's top.
- **The gap is a strong signal, but the rule does not use it.** At 914 left and 910 left, the line gap above the zone is 149 px and 126 px, against median gaps of 5 px and 1 px. The other three zones have a gap of 0, so the rule's own boundary is not always at the white space.

## Proposed, not measured (a new lock would be needed)

These are proposals only. The lock says a changed rule is measured only under a new lock, and none is substituted here.

1. **Use the line pitch, not the word-box height.** The distance from one line's top to the next is set by the type and its leading, and is less noisy than a box height. Lock a cut-off on pitch ratio before measuring.
2. **Use the white gap as the boundary when there is one.** A zone's boundary moves up to the nearest line gap that is at least *k* × the column's median gap, with *k* fixed in the lock.
3. **Raise the height cut-off** (for example to 0.90). This is the simplest change, but it is tuned on what was just seen, so it would need a fresh check against other chapters, not just these 20 pages.

The test cases stay Chris's two signed notes. Any new rule is scored against them in the same way.

## Nothing changed

- No OCR output was changed. The tool writes only to its own directory.
- No word text is in `zones.json`, its README or this file.
