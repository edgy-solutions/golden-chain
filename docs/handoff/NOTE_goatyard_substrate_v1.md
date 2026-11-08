# To goat-yard: one correction to the substrate-v1 notice (2026-11-01)

From: the Golden Chain build agent, sent by Chris. Ruled by the Golden Chain architect on report 9, and amended by the architect on 2026-11-01.

We checked the substrate-v1 notice against the tag from our side. It is accurate in substance. One correction:

**A second consumer-visible change.** At `substrate-v1`, the dict that `verse_regions.analyze_page_s1` returns gains the key `"median_line_h"`. The change is additive, but Golden Chain calls that function (`tools/gy_locate_column_rule.py`, line 170, reading the page line height). The notice names only `ink_box`. Please name `median_line_h` too. (goat-yard has accepted this, and A2 is amending the notice to list every added output field.)

**Withdrawn:** an earlier draft of this note asked whether the tag was cut on rerun 8 or rerun 9. goat-yard showed that both labels are correct. The commit subject names the design lock ("rerun-8 lock"), and the annotated tag names the validating run (rerun 9, lock `b213cb9d`). There is no re-cut.

**What Golden Chain does next.** We re-pin to `substrate-v1` as a locked step, and use it only to reproduce the column split. `ink_box` waits for v1.1. The prediction: our three `locate_column_rule` runs (native, 0.703 and 6.947) reproduce the v0 numbers exactly, because the code they use is unchanged between `3d0b03e0` and `301bde5`. Any difference is a finding first. We report the result to you either way.

Re-pin result: hit. All three runs (native, 0.703, 6.947) reproduce
v0 exactly on substrate-v1; 60 page images byte-identical; run
headers differ only where predicted. OCR proceeds on v1. ink_box
untouched until v1.1.
