# Lock: weigh fix 2, every source of a Holding, in IRI order

- **By:** the build agent, 2026-11-22. Committed before the code (rule 6). Git history seals it.
- **On:** [RULING_report_27.md](RULING_report_27.md), "Weigh fixes", item 2: "Where a Holding cites several sources, weigh lists all of them in IRI order. No choice among them, so the output is stable." And: "Add a test that runs weigh twice in separate processes and compares bytes."
- **Defect:** `goldenchain/unchurches.excluded` takes one source with `g.value(h, DCTERMS.source)`. Which one it gets depends on Python's string-hash seed, which changes from process to process ([REPORT_phase1_27.md](REPORT_phase1_27.md)).

## Measured before the code (current tree, `ea28fa4`)

- **Only one predicate is multi-valued in the real data:** `dcterms:source`, on 5 WCF Holdings (baptism-efficacy/grace-conferred-in-right-use, baptism-significance/sign-and-seal-of-the-covenant, circumcision-covenant/administration-of-grace, covenant-administrations/one-covenant-two-administrations, covenant-of-grace/made-in-time-after-fall). I checked every predicate that weigh and unchurches read with `g.value`.
- **The render path reads a Holding's source in two places:** `unchurches.excluded` (the exclusion line) and `weigh._own_cell` (congregations only: whether the source is personal knowledge). Every other source list in weigh is already sorted (`weigh.py` line 274).
- **Hash by seed** (`PYTHONHASHSEED`, `weigh | sha256sum`, first 12):
  - members: seeds 0 and 3 give `13209f4b689f`; seeds 1, 2, 4, 5 give `72a2d3c329e7`.
  - officers: seeds 0 and 3 give `590965a0a299`; seeds 1 and 2 give `7dcf90eb14d4`. **Correction to report 27,** which said officers gave the same hash both times: it varies too. My two runs happened to agree.

## The change

- `excluded` gives each row `"sources"`: every `dcterms:source` of the Holding, sorted by IRI. The key `"source"` is replaced (no test or other module reads it).
- `render_body` prints them joined with ", " inside the parentheses, or "no source" if there are none.
- `_own_cell` asks whether **any** of the Holding's sources is personal knowledge, and no longer picks one.
- Fix 1 (`LOCK_weigh_flag_source`) is not in this change. It waits on a failing existing test, reported in report 28.

## Predictions

| # | Prediction |
|---|---|
| S1 | On the real data, WCF's administration-of-grace exclusion line reads "(source/wcf/28/4, source/wcf/7/5)". IRI order puts 28/4 before 7/5. No other line changes in either scope, apart from that line's parentheses. |
| S2 | `weigh --scope members` gives one hash for `PYTHONHASHSEED` 0 to 5, and `--scope officers` one hash for 0 to 3. The new hashes are measured, not predicted. |
| S3 | Born, `tests/test_weigh.py`: (a) weigh run in two separate processes with `PYTHONHASHSEED` 0 and 1 (which differ today) gives identical bytes, in each scope; (b) on the real data, the WCF line names both 7.5 and 28.4, in that IRI order; (c) on a fixture, an excluded Holding with two sources lists both, sorted, whatever order they were added in. |
| S4 | No existing test fails. If one does, it is reported before it is amended. Suite: 814 + the born tests, all passing. |
| S5 | Real ingest: 0 violations, 0 warnings. Data unchanged. |
