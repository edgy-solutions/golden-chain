# Phase-1 report 2 (2026-10-25)

For: the architect (and the goat-yard architect for items marked GY).

## What was done

| Commit | Files | What |
|---|---|---|
| dba4257 | `goldenchain/passage.py`, `goldenchain/versification.py`, tests | Passage canonicaliser; KJV v11n table from CrossWire `canon.h` (66 / 1,189 / 31,102), checked by `tests/test_versification.py`. |
| 40c75c2 | `ontology/core.ttl`, `ontology/shapes.ttl`, `ontology/vocab.ttl`, tests | Core ontology, SHACL shapes (closed Argument, status, quotation cap), status vocabulary. |
| 27239ad | `goldenchain/ingest.py`, `jena.py`, `fuseki.py`, `reasoner/*.ru`, tests | Reasoner (inheritance; excludes/entails consistency), Jena TDB2 ingest, read-only Fuseki, guard tests (Jena half). |
| 4e49471 | `data/*.ttl` (7 files), `tests/predictions.py`, `tests/test_real_data.py` | Phase-1 data: loci, Gill, WCF, LBC, Augsburg, Book of Concord, agents. |
| e1bdd96 | ADR-0002, ADR-0005, `docs/RULES.md`, `docs/sources/goat-yard.md`, plumb-line form | ADR-0002 revision 1 (GY: v11n segment, reserved Anchor, locations only, table provenance). ADR-0005 ratified provisionally and amended. Rules 1–10. goat-yard terms and additions recorded verbatim. |
| 1840cf2 | `tools/column_rule.py`, `docs/sources/gill-column-rule.md` | GY addition 2: column-rule measurement on pp. 896–915. |
| d145a67 | `data/lbc-1689.ttl`, `tests/predictions.py`, `docs/sources/lbc-1689.md` | LBC 29 ruling: 29.1 (d) "Act. 26. 16" resolved to Acts 22:16; 29.2 (f) Acts 8:36-37; candidates withdrawn; lettered `gc:asPrinted`; 1677 facsimile (2000) recorded as witness. |

Nothing is pushed. The working tree is clean.

## Predicted vs actual

| Item | Predicted | Actual |
|---|---|---|
| Data counts (14 keys, locked before first generate) | Locus 8, Position 14, Argument 41, Body 7, Holding 33, excludes 5, entails 1, holds 33, answers 14, supports 41, childOf 2, effectivelyHolds 33, warnings 8 | **All match.** Passage 87 was measured and pinned, not predicted (Q22). |
| SHACL violations | 0 | 0 (8 warnings: `gc:tier` missing on 8 loci, by design until the plumb-line). |
| Jena (Fuseki on real TDB2) vs rdflib | Agree | effectivelyHolds 33, consistency 0, holds 33, 10 graphs, 1,930 quads (1,897 source + 33 derived). Agree. |
| Column rule present (GY, architect's locked prediction) | 20/20 | **20/20**, as a *single* rule (median 14 px = 1.19 pt). Gutter median 131 px = 11.1 pt. Run 1 abstained on pp. 897, 898, 902 (method defect, on record); run 2 is a clean rerun. Build-agent predictions P3, P4 missed (Q23). |
| LBC 29 ruling: Passage | 87 → 86 (only Acts 8:37-38 leaves; 2:41, 8:12, 22:16, 8:36-37 stay cited by Gill/WCF) | **86**. Other 13 keys unchanged, as predicted. |
| Tests | all pass | **169 passed.** |

## Open questions

1. **LBC 29.1 Argument granularity.** Notes (c), (d), (e) are now three lettered `gc:asPrinted` strings on one Argument that supports `union-with-christ`. If "each Argument tied to its clause" means one Argument per note, 29.1 splits into three, and (d) (remission of sins) and (e) (newness of life) need a Position to support. I did not split. Rule?
2. **asPrinted spacing in (d).** The ruling gives both "Act. 26.16" and "Act. 26. 16". I used the quoted `gc:asPrinted` value, "Act. 26. 16". Confirm from the page.
3. **Letters for 28.1, 29.3, 29.4.** Not in the ruling, so those Arguments carry no `gc:asPrinted`. Read them from the facsimile?
4. **Edition property.** The 1677 witness is recorded as `dcterms:bibliographicCitation` on `source/lbc-1689` (no new `gc:` term). Acceptable, or mint `gc:edition`?
5. **WCF 28.7 rebaptism Holding** remains blocked: no locus.
6. **Apology IX** supports `infants`, not efficacy. Confirm the Holding set.
7. **`augsburg` childOf `book-of-concord`?** Currently not.
8. **`gc:Collection`** class for Book of Concord: confirm.
9. **Seven data files**, not the four in the instruction (loci, agents, and Book of Concord added).
10. **grace-conferred ⟂ necessary-means** is not asserted as excludes or entails.
11. **Scope is ignored** in excludes/entails firing.
12. **Passage IRIs** await the ADR-0002 review by both architects (GY).
13. **Inconsistency IRI pattern** is new in ADR-0002 rev. 1.
14. **Apology/SC Holdings** are build-agent proposals.
15. **Diamond inheritance** through two parents is untested on real data.
16. **WCF asPrinted strings** are not recorded.
17. **Gill F6 candidates** are not picked (ruling 6).
18. **Dissertation 5** deferred; **Triglot pages** unverified.
19. **Column rule (GY):** single, not double. Does goat-yard fix A accept a single rule? Your sign-off from pixels is pending on pp. 897, 898, 902 and on the run-1 abstention. Strips: `~/.golden-chain/column-rule-2026-10-25/strips/`.
20. **Truth-set provenance form** is undefined in goat-yard (GY); ADR-0002 rule 5 follows the nearest examples.
21. **Passage 87** was pinned as measured, not predicted.
22. **P3/P4 misses** in the column-rule run.
23. `tools/column_rule.py` needs pypdfium2, numpy, pillow, which are not in `pyproject.toml`. Add an optional `measure` extra?
24. **Pre-hold OCR** in the session scratchpad (`bsb-ocr/`) is unused and will be discarded.

## Next on "continue"

1. Apply rulings on Q1–Q4 (LBC) and any others given.
2. On "push": push `phase-0`.
3. Otherwise hold: OCR waits for `substrate-v0`; the plumb-line form waits for you.
