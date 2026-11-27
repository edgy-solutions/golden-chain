# Lock: the quotation-unit page pass, part 1 (ruling on report 30, Q-A-1)

- **From:** the build agent, 2026-11-26. Committed before any page is viewed.
- **On:** [RULING_report_30.md](RULING_report_30.md), and [AUDIT_argument_unit_2026-11-26.md](AUDIT_argument_unit_2026-11-26.md) (the first pass).

## Scope

**Part 1, now: 16 Arguments.**
- The 14 "cannot tell" Arguments outside Gill *Body* pp. 897-912:
  - Apology Art. IX (2), in the Triglot;
  - Coxe pp. 36-38 (3);
  - Gill *Body* pp. 247 (3) and 361 (1);
  - Gill *Divine Right* pp. 45-47 (5).
- The 2 "would split" Arguments, so their re-cut count is known:
  - Coxe pp. 105-109 (1);
  - Graves p. 124 (1).
- Gill *Body* p. 345 (Doctrinal IV.1, Introduction) is viewed too, to confirm the first pass's "same cut" from the page.

**Part 2, later: 17 Arguments.** Gill *Body* pp. 897-912 wait until Chris has signed the italic-spans sitting (`9b19159be3098c64`).

## Method

- **Who views:** the build agent views each public-domain page itself.
  - The BSB pages are rendered from the PDF in the private corpus (read-only) into the scratchpad. They are never committed.
  - The IA scans (Coxe, Gill *Divine Right*, Graves) and the Triglot are viewed online.
- **Allowed:** no goat-yard crop, no signing strip, no OCR and no text layer. No subagent views an image.
- **What is judged:** for each Argument, the printed unit (ADR-0005 as amended): a run of references closing one clause, or one quoted verse with its references, as the page prints it. The verdict is one of:
  - same cut;
  - would merge, naming the Arguments;
  - would split, naming how many units and the references of each;
  - would widen: the printed run has references the Argument does not cite. This is counted as a split or a widening, and stated.
- **Signed Arguments:** every Argument found to differ is checked against the signed records (`docs/handoff/SIGNED_*.md`) and the sittings. If Chris has signed it, it is listed separately, to be put to him.

## Predictions

| # | Prediction |
|---|---|
| P1 | The audit file gains a "page pass, part 1" section with a verdict for each of the 16 (plus p. 345) and the page each verdict rests on. The first-pass columns are updated, and the 17 of part 2 are listed as waiting. |
| P2 | The full re-cut list is reported only after part 2 (Q-A-2: one locked change). Part 1 lists its candidates and proposes new IRIs: each numbered after the highest existing in its division. An old IRI is never reused; it is deprecated with `dcterms:isReplacedBy`. |
| P3 | No `data/` change, no test change. The commit adds only the audit update, the report and the ruling file's "Applied" section. |
| P4 | If a page cannot be found online, or the printed reference does not match the data, it is recorded, not resolved by guessing. |

A miss is recorded, not edited.
