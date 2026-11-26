# Lock: merging `hold/adr3-r3` into `phase-0` (ruling on report 28, items 4 and 5)

- **From:** the build agent, 2026-11-26. Committed before the merge.
- **On:** [RULING_report_28.md](RULING_report_28.md) items 4 (the 26 R3 test amendments accepted; merge) and 5 (`test_w1_w2_w3` accepted; fix 1 lands with the merge).
- **Base:** `phase-0` at `1b62c9a`, suite 851 passed. `hold/adr3-r3` at `a193e8b`, which carries `hold/weigh-fix-1` (`194149b`, `2a817d1`). The merge base is `ac25d0a`.

## Predictions

| # | Prediction |
|---|---|
| M1 | The merge has no conflicts: the two sides changed disjoint files since `ac25d0a`. |
| M2 | Full suite with the bibles set: 875 passed, 0 failed, 0 skipped. That is 820 at the merge base, plus 31 born on `phase-0` and 24 born on the branch. No test is amended in the merge beyond the 26 + 1 already ruled. |
| M3 | Real ingest 0 violations, 0 warnings. |
| M4 | Weigh as on the branch: members `b5ad57ea0df3`, officers `6a2ffd426bf9`. |
| M5 | `data/plumb-line.ttl` sha256 begins `bfb0238c`; every other `data/*.ttl` is byte-identical to `phase-0` at `1b62c9a`. The PREDICTED counts are unchanged. |
| M6 | The two unsigned console pages keep their build16 when rebuilt from the merged tree: sitting 2 `b7c9ffb0096a4522`, statements `0894df4edd1fe4b1` (their builders read `data/loci.ttl` and the content files, which the merge does not change). |

A miss is recorded, not edited. If M6 misses, the page Chris signs is the rebuilt one, and the report names its new build16.
