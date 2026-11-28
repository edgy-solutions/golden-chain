# Lock: item 9, the full re-cut list for every Argument outside Gill pp. 897-912 (2026-11-27)

- **Locked:** 2026-11-27. Committed before the check below is run. Git history seals it. This file is never edited; misses are recorded in the list.
- **On:** the ruling on report 32, item 9 ([RULING_report_32.md](RULING_report_32.md)): "If time remains: the argument-unit audit's full re-cut list for every Argument outside Gill pp. 897-912, ready for ruling."
- **What it rests on:**
  - the audit [AUDIT_argument_unit_2026-11-26.md](AUDIT_argument_unit_2026-11-26.md);
  - its page pass, part 1 (lock `a08a324`), which viewed every Argument outside Gill pp. 897-912 and found 56 same cut, 7 that would split into 21 units, and none that would merge or widen.
- **No page is viewed for this item.** The units as printed are the ones part 1 read from the pages. This item checks the proposed new IRIs and cites against the data by machine and writes the list. Nothing in `data/` or in any test changes.

## The check (read-only, rdflib over `data/` at the commit of this lock)

1. Every Argument IRI in the data, by division (the IRI path up to its last segment).
2. For each of the 7 old Arguments: its `gc:cites` and `gc:citesCandidate` Passages, `gc:supports`, source and locator.
3. For each of the 21 proposed units: whether its IRI is already used; whether it is numbered on from the highest existing Argument in its division, with no gap; whether each Passage it cites exists; and whether it cites a subset of the old Argument's cites.

## Predictions

| # | Prediction |
|---|---|
| R1 | The full list outside Gill pp. 897-912 is the part-1 list: **7** old Arguments become **21** new ones, and the other **56** Arguments outside those pages are unchanged. |
| R2 | None of the 21 proposed IRIs is in use in the data. |
| R3 | In each division, the proposed numbers follow the highest existing Argument with no gap. |
| R4 | Each proposed unit cites a subset of its old Argument's `gc:cites`. Together, a split's units cover all of the old Argument's `gc:cites`. |
| R5 | Every Passage a proposed unit cites already exists in the data. |
| R6 | No file under `data/` or `tests/` changes. The list is a new file in `docs/handoff/`. |
