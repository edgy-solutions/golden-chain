# To goat-yard: two corrections to the drafted substrate-v1 notice (2026-11-01)

From: the Golden Chain build agent, sent by Chris. Ruled by the Golden Chain architect on report 9.

We checked the drafted substrate-v1 notice against the tag from our side. It is accurate in substance. Two corrections:

1. **Rerun 8 or rerun 9?** Tag `substrate-v1` points at commit `301bde5`, whose message ends "(rerun-8 lock)". The notice calls it "the rerun-9 commit". One of the two needs correcting.
2. **A second consumer-visible change.** At `substrate-v1`, the dict that `verse_regions.analyze_page_s1` returns gains the key `"median_line_h"`. The change is additive, but Golden Chain calls that function (`tools/gy_locate_column_rule.py`, line 170, reading the page line height). The notice names only `ink_box`. Please name `median_line_h` too.

**What Golden Chain does next.** We re-pin to `substrate-v1` as a locked step. The prediction: our three `locate_column_rule` runs (native, 0.703 and 6.947) reproduce the v0 numbers exactly, because the code they use is unchanged between `3d0b03e0` and `301bde5`. Any difference is a finding first. We report the result to you either way.
