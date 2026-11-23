# Lock: weigh fix 1, a flag's source from its own axiom

- **By:** the build agent, 2026-11-22. Committed before the code (rule 6). Git history seals it.
- **On:** [RULING_report_27.md](RULING_report_27.md), "Weigh fixes", item 1: "A flag's source is the sitting named on that flag's own annotated axiom (ADR-0006 R1), never the latest sitting."
- **Defect:** `goldenchain/unchurches.flag_source` returns the `dcterms:source` of the plumb-line's Holding on the Position, not of the flag ([REPORT_phase1_27.md](REPORT_phase1_27.md)).

## The change

- `flag_source(g, position)` returns the `dcterms:source` values of every `owl:Axiom` whose `owl:annotatedSource` is the Position and whose `owl:annotatedProperty` is `gc:unchurches`, **sorted by IRI**, as a list.
- **No fallback.** Report 27 proposed falling back to the Holding's source when there is no axiom. The ruling names the axiom only, so there is no fallback: with no axiom the list is empty and weigh prints "no source", as it does now.
- `weigh.render_body` joins the list with ", ". Nothing else in weigh changes.

## Predictions

| # | Prediction |
|---|---|
| F1 | On the real data, the 4 exclusion lines in `weigh --scope members` all end "flagged by the plumb-line at source/plumb-line/sitting-eb961ddb1e582ed6". Today 3 of them name `sitting-7b23646b2c763ae0` (Apology infants, Augsburg infants, WCF believers-and-their-infants); the circumcision-covenant line already names eb961ddb. |
| F2 | No other line of weigh's output changes, in either scope. The ranking, the excluded Bodies and their rows are unchanged. (The weigh hash is still not a byte-identity check until fix 2.) |
| F3 | Born, in `tests/test_unchurches.py`: (a) on the real data, `flag_source` gives `[sitting-eb961ddb1e582ed6]` for each of the 3 flagged Positions; (b) on a fixture with a flag whose axiom names one sitting and a plumb-line Holding sourced to another sitting, `flag_source` gives the axiom's sitting; (c) on a fixture with a flag and no axiom, `flag_source` is empty and the line reads "no source". |
| F4 | No existing test fails. If one does, it is reported before it is amended (ruling on report 27). Suite: 814 + the born tests, all passing. |
| F5 | Real ingest: 0 violations, 0 warnings. Data unchanged. |
