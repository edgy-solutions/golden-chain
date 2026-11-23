# Lock: the eight amended tests move to a frozen fixture

- **By:** the build agent, 2026-11-22. Committed before the change (rule 6).
- **On:** [RULING_report_27.md](RULING_report_27.md), "Test amendments": "Move those eight to a frozen fixture copy of the data they were written for, in one commit, with the list of tests."

## The fixture

- `tests/fixtures/data-8ac7e41/`: every `data/*.ttl` exactly as at `8ac7e41`. That is the last tree before sitting eb961ddb was ingested, and the data these tests passed on. It holds no text that `data/` did not already hold.
- A born test checks that each fixture file is byte-identical to `git show 8ac7e41:data/<name>`, so the copy cannot drift.

## The eight tests

| # | Test | Reads |
|---|---|---|
| 1, 2 | `test_step3_batch_a::test_new_loci_have_no_tier` (two parameters) | the fixture, all files |
| 3 | `test_step3_batch_a::test_only_gill_holds_circumcision_no` | the fixture |
| 4 | `test_step3_batch_b::test_locus_33d_has_no_tier` | the fixture |
| 5 | `test_step3_batch_b::test_no_lbc_holding_on_validity_positions` | the fixture |
| 6 | `test_unchurches::test_real_data_no_flags_empty` | the fixture |
| 7 | `test_unchurches::test_real_data_with_flags` | the fixture, plus the two flags it adds |
| 8 | `test_weigh::test_real_data_smoke` | the fixture, plus the flags it adds |

Each test keeps its own assertions. The amendments of report 27 (the `SRC` graphs without `plumb-line.ttl`, and `gcfix.strip_flags`) are replaced by the fixture. A helper is removed if nothing else uses it.

## Predictions

| # | Prediction |
|---|---|
| X1 | The eight pass on the fixture, unchanged in what they assert. |
| X2 | `SRC` in the two batch files and `strip_flags` in `gcfix` are no longer used, and are removed. |
| X3 | Suite: 819 + 1 born = **820 passed**. No other test changes. |
| X4 | Data, weigh output and the real ingest are unchanged (0/0). |
