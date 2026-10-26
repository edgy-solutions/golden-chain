# Phase-1 report 4 (2026-10-26)

For: the architect, and goat-yard for the items marked GY.

Covers:
- the LBC 28/29 letters;
- rulings Q7–Q9, Q11, Q15 and Q20–Q24 on report 2;
- the goat-yard single-rule response;
- the pin and the locked `locate_column_rule` run.

Q5, Q6 and Q16 are not done yet (see "Next").

## What was done

| Commit | Files | What |
|---|---|---|
| 9e845c2 | `data/lbc-1689.ttl`, `docs/sources/lbc-1689.md` | 29.3 (g), 29.4 (h) `gc:asPrinted` from the 1677 facsimile. 26.15 (g) and 27.1 (a)(b)(c) stored for phase 2, not minted. |
| 700a400 | same | 28.1 (a), p. 96, chapter title as printed. 28.2 (b) stored for phase 2 (no administrator locus). |
| 13aa98a | `reasoner/20-consistency.ru`, `tests/test_reasoner.py`, ADR-0003 | Q11: excludes/entails fire only when scopes intersect. Q15: `parents-differ` for two-parent Bodies. ADR-0003 Revision 1. 27 born tests. |
| ed47ee1 | `pyproject.toml`, `docs/sources/goat-yard.md` | Q23: `measure` extra. GY response recorded verbatim. Prediction locked before any run. |
| 36e6134 | `docs/README.md`, ADR-0002, `docs/RULES.md`, `tests/predictions.py`, `docs/sources/gill-column-rule.md` | Q9: data layout. Q20: "pending GY form". Q21: every count is predicted (rule 6). Q22: the run-1 paragraph, the run-2 header, P3/P4 findings. |
| 0996090 | `data/augsburg.ttl`, `data/book-of-concord.ttl`, `ontology/core.ttl`, `ontology/shapes.ttl`, tests | Q7/Q8: the Book of Concord is a `gc:Collection`. Augsburg, Apology and Small Catechism are `dcterms:isPartOf` it, and it has `dcterms:hasPart` them. New shapes: no `gc:childOf` a Collection, and the pair must mirror. 5 born tests. |
| 26a76b6 | `tools/gy_locate_column_rule.py`, `tests/test_gy_locate.py`, `docs/sources/gill-column-rule.md`, `docs/sources/goat-yard.md` | The pin, and the locked run (below). The pin guard has 2 born tests. |
| (this commit) | this report, `HANDOFF_phase1.md` | — |

Also done:
- Q24: `bsb-ocr/` was deleted after a grep found zero citations.
- Q11 and Q15 are recorded in ADR-0003 Revision 1.

## goat-yard `locate_column_rule` at substrate-v0 (GY)

**Pin.** Chris confirmed the tag on origin: annotated tag `2d695735` → commit `3d0b03e0`. The worktree is `../goatyard-substrate-v0`, detached at the tag, clean. The run tool refuses any other commit or a dirty tree.

**Method.** goat-yard code runs unchanged, imported from the worktree:
- the page's own embedded image, 5100 × 7650 px, **not rescaled**;
- `build_page_geometry.process_page`, then `page_ink`, then `locate_column_rule`.

Run once, after a smoke run on p. 183. Full header and method: [../sources/gill-column-rule.md](../sources/gill-column-rule.md).

| Page | Status | Strips with a cluster | half_w | Max residual |
|---|---|---|---|---|
| 896 | ok | **11/22** | 4.0 | 2.1 |
| 897 | ok | 22/22 | 3.0 | 9.5 |
| 898 | ok | 22/22 | 4.5 | 7.7 |
| 899 | ok | 22/22 | 3.5 | 8.7 |
| 900 | ok | 22/22 | 5.0 | 7.4 |
| 901 | ok | 22/22 | 3.5 | 11.7 |
| 902 | ok | **21/22** | 4.0 | 6.9 |
| 903 | ok | 22/22 | 5.5 | 11.6 |
| 904 | ok | 22/22 | 4.0 | 3.1 |
| 905 | ok | 22/22 | 4.0 | 5.1 |
| 906 | ok | 22/22 | 5.0 | 13.3 |
| 907 | ok | **21/22** | 5.0 | 8.3 |
| 908 | ok | **21/22** | 4.0 | 5.4 |
| 909 | ok | 22/22 | 4.5 | 5.3 |
| 910 | ok | 22/22 | 4.0 | 12.6 |
| 911 | ok | 22/22 | 4.5 | 7.9 |
| 912 | ok | 22/22 | 4.0 | 7.6 |
| 913 | ok | 22/22 | 4.2 | 5.8 |
| 914 | ok | 22/22 | 4.0 | 6.5 |
| 915 | ok | 22/22 | 5.0 | 7.7 |

## Predicted vs actual

| Item | Predicted (locked) | Actual |
|---|---|---|
| GY: status | 20/20 ok | **20/20 ok**: held |
| GY: max residual | ≤ 15 px | **13.3 px** (p. 906): held |
| GY: every strip carries a cluster | 440/440 | **426/440: missed** on pp. 896, 902, 907, 908. A finding. |
| Q7/Q8: childOf | 2 → 0 | **0** |
| Q7/Q8: effectivelyHolds | 33, unchanged | 33 |
| Q7/Q8: other 12 keys, SHACL | unchanged; 0 violations, 8 warnings | unchanged; 0, 8 (rdflib and Jena) |
| Tests | 199 + 5 + 2 | **206 passed** |

**Correction found while writing Q22.** P4 (gutter 125–145 px) also missed on **p. 911** (124.5 px). Report 2 and the source doc had named only pp. 896 and 898. This is now recorded as a finding.

## Open questions

1. **Does the run pass? (GY)**
   - 20/20 ok and the residual clause held. The "every strip" clause missed: 14 of 440 strips have no cluster.
   - There was no abstention, so goat-yard's request-file trigger does not fire.
   - I treat the run as **not passed as locked**: OCR stays HELD, and the A2 fixture ("if 20/20 passes") is not prepared. Rule?
2. **The empty strips need pixels.**
   - p. 896, 700–3700: the upper body of the page run 2 flagged.
   - The last strip, 7000–7300, on pp. 896, 902, 907, 908: peak fractions 0.44–0.55 against the 0.59 cut.
   - `presplit` finds no horizontal rule on BSB pages, so the window ends at H − 300. Whether the rule ends inside that strip, or is too faint for 0.59, needs a look at the page. Chris, for the sign-off from pixels?
3. **`pip install -e --no-deps`.** This deviates from "pip install -e".
   - A full install pulls dagster, openai, dspy, weaviate and baml into our venv.
   - `verse_regions` needs only numpy, and its flat modules load by path, not as the `pipeline` package (whose `__init__` imports dagster).
   - Confirm, or I do the full install.
4. **Q7 also removes Apology and Small Catechism `childOf`.** Ruling 2(a) said "both childOf book-of-concord". I read Q7 ("a collection, not a parent") as superseding it for all members. Confirm.
5. **Mirror shapes on Collection membership** (`isPartOf` ↔ `hasPart`) are a build-agent addition. Keep?
6. **Gill provenance wording** may overstate what was seen.
   - [data/gill-body-of-divinity.ttl:10](../../data/gill-body-of-divinity.ttl) says the pages and asPrinted strings were "read from the BSB 2019 page images".
   - Lines 183 and 269 say "(confirmed on the page image)".
   - Those readings rest on pre-hold OCR and renders, and no model viewed pixels. I have not changed the wording. Should it say "read from the BSB OCR and CCEL, to be signed from pixels"?
7. **ADR-0003 Revision 1 readings** for confirmation:
   - (a) a silent parent is not a difference;
   - (b) the child still inherits both parents;
   - (c) only direct parents are compared.
8. **Q12.** The ADR-0002 Revision 1 text is [§ Revision 1 of ADR-0002](../adr/0002-identity-iri-patterns.md), to forward to goat-yard.
9. **Report 3, open question 2** (applying rule 6 to existing `gc:` properties) is still open.

## Next on "continue"

1. Q5: lock predictions, then mint the rebaptism locus. Two Positions: WCF 28.7 "never", and Gill/LBC "infant baptism is no baptism". The Gill and LBC Arguments are read from the text, not assumed.
2. Q6: read Apology IX for efficacy support; add an Argument only if the text gives it.
3. Q16: write the WCF 1647 "with Scripture proofs" source note, then a reading form for Chris (I do not view page images).
4. OCR stays HELD until open question 1 is ruled.
