# Phase-1 report 3 (2026-10-26)

For: the architect. It answers the rulings on report 2 (Q1–Q4 and the column rule). Q5–Q24 of report 2 stand unanswered and are not repeated here.

## What was done

| Commit | Files | What |
|---|---|---|
| aa8f927 | `data/lbc-1689.ttl` | Q1: LBC 29.1 split into one Argument per lettered note. (c), (d), (e) become `argument/lbc-1689/29/1/001`–`003`, all supporting `union-with-christ`. The 22→26 resolution note sits on (d) only. |
| aa8f927 | `ontology/shapes.ttl`, `tests/test_shapes.py` | Q1 shape: a `gc:asPrinted` opening with `(x) ` must be the Argument's only `gc:asPrinted`. Unlettered inline citations (Gill: up to 7 strings on one Argument) stay legal. 3 tests. |
| aa8f927 | `docs/adr/0005-…md` | Q1 recorded as an amendment ("one Argument per lettered note"; rule 2 is per Position). |
| aa8f927 | `docs/adr/0002-…md` | Q4: general rule 6, "standard vocabulary first"; `dcterms` for anything bibliographic. |
| aa8f927 | `docs/sources/lbc-1689.md` | Q2 confirmed spacing recorded; Q3 letters for 28.1, 29.3, 29.4 awaited from Chris. |
| aa8f927 | `docs/sources/gill-column-rule.md`, `docs/sources/goat-yard.md` | The single-rule finding is recorded as the evidence a "column split on a single rule" request would carry: n, method, per-page table, gutter distribution, run-1 abstentions. Not filed: it waits on your pixel sign-off and goat-yard's answer. |
| (this commit) | this report, `HANDOFF_phase1.md` | — |

`phase-0` is pushed (as instructed).

## Predicted vs actual

| Item | Predicted (locked 2026-10-26T00:27:52Z) | Actual |
|---|---|---|
| Argument | 41 → 43 | **43** |
| supports | 41 → 43 | **43** |
| Passage | 86, unchanged | 86 |
| Other 11 keys | unchanged | unchanged |
| SHACL | 0 violations, 8 warnings | 0, 8 (the new shape passes on the real data) |
| Tests | 169 + 3 new | **172 passed** |

## Open questions

1. **WCF letters its proofs too.** Ruling Q1 says "apply the same rule everywhere a confession letters its proofs". The 10 WCF Arguments cite each clause's proof texts but record no `gc:asPrinted` and no note letters (report 2 Q16), so I cannot tell which of them bundle several notes. The witness of record is the 1647 Tyler page images (PD; `docs/sources/westminster.md`). Options:
   - (a) I download those IA pages and read the note letters locally (page images of PD texts, local viewing only; no OCR, no model sees them);
   - (b) Chris reads them, as with LBC.

   Until then the WCF Arguments are not split.
2. **Rule 6 applied backwards?** These existing `gc:` properties look bibliographic. I have not migrated any of them:
   - `gc:paginationOf`: a citation of the reprint whose pagination is used. Candidate: `dcterms:bibliographicCitation`.
   - `gc:quotationCheckedAgainst`: the witness a quotation was checked against. Candidate: `dcterms:source`, but on an Argument that already means something else.
   - `gc:pages`: no `dcterms` term; `bibo:pages` exists. Keep it?
   - `gc:locator` / `gc:secondaryLocator`: no standard term I know carries "division within the source".

   Migrate `gc:paginationOf` only? Keep the rest?
3. **LBC 28.1, 29.3, 29.4** stay unsplit and unlettered until Chris's photographs arrive (Q3).

## Next on "continue"

1. Apply Q1 to WCF per your answer to open question 1, and the LBC letters when they arrive.
2. Apply your answer on open question 2.
3. Otherwise hold: OCR waits for `substrate-v0`; the column request waits for goat-yard's answer and your sign-off.
