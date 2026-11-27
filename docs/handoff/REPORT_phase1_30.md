# Report 30: the ruling on report 29 worked down

- **From:** the build agent, 2026-11-26. Branch `phase-0`, pushed.
- **On:** [RULING_report_29.md](RULING_report_29.md). Lock: [LOCK_report29_2026-11-26.md](LOCK_report29_2026-11-26.md) (`249640a`), committed before the merge, the code and the audit.

## One list: what waits on Chris, and on the architect

**On Chris (sign from the pixels; each page is local, under `~/.golden-chain/console/`):**

1. **Sitting 2:** `plumb-line-followup/console_plumb-line-followup_18a4a13dfeffb6e9.html`. It is still the one to sign; the merge does not touch it (A6). Ruling 9 and the instrumentality bindings (Q-H-1) apply at its ingest.
2. **Statements and inclusion:** `statements/console_statements_f3f1af17d9075ba5.html`.
   - Rebuilt from the merged `phase-0`, the id is unchanged (Q-C-4). This is the one to sign.
   - On the BSB foreword row the choice is yours. If you include it, it carries the architect's label.
3. **LBC 1677:** `console_lbc-1677_0a73bb5afa616446.html` (unchanged).
4. **Gill's italic:** `italic-spans/console_italic-spans_9b19159be3098c64.html`.

**On the architect:**

- **Q-A-1.** The audit's first pass, from the printed strings, leaves 31 of 80 Arguments that cannot be judged without the page. May the build agent do the page pass now?
  - It covers the public-domain pages: Triglot, Coxe pp. 36-38, Gill *Body* pp. 247 and 361, and Gill *Divine Right* pp. 45-47.
  - Gill *Body* pp. 897-912 would wait until Chris signs the italic-spans sitting, which is open on those pages.
- **Q-A-2.** The two Arguments that would split (Coxe V §8, Graves ch. X) are left as they are until ruled. Should they be re-cut after the page pass, or kept as recorded history under the rule that the unit applies from Batch C on?

## Item by item

| Item | What | Commit | Result |
|---|---|---|---|
| Q-C-1 | Gill head 6 | — | "Not taken" stands. The LOCK_batchC_unit table is the record. |
| Q-C-2 | Quotation-unit audit | this report's commit | [AUDIT_argument_unit_2026-11-26.md](AUDIT_argument_unit_2026-11-26.md). Of the 80: 47 same cut, 0 would merge, 2 would split, 31 cannot tell without the page. Nothing changed. |
| Q-C-3 | Accept the hold branch | `e940414` (merge) | `hold/batchC-unit` merged with no conflicts. Suite 925. Ingest 0 violations, 1 warning (33e has no tier). Weigh `b5ad57ea0df3` / `6a2ffd426bf9`, `data/plumb-line.ttl` `bfb0238c`. |
| Q-C-3 | Stop the pattern | `da34406` | The three plumb-line form tests now derive their counts from the loci file they read. They read it with rdflib, independently of the builder's `read_loci`; only `notation_key` is imported, for the sort. What the signed form fixes stays literal: its 15 Position rows, the silent and abstained rows, the efficacy fault. A born test appends a Locus "33z" with two Positions to a copy of `data/loci.ttl`, and the three checks pass on it unedited. A new Locus no longer needs a hold branch. |
| Q-C-4 | Statements page id | — | Still `f3f1af17d9075ba5` after the merge. |
| Q-H-1 | Bindings at the sitting-2 ingest | — | Accepted. It will be done in that change. |
| Misses | Recorded | — | From now on, identity clauses in a lock name the build hash and the outputs, not the input spec (ADR-0006 R5). LOCK_report29 is written that way. |
| Label (a) | Heidelberg 65 | — | Accepted. It is in the data as minted. |

**The choice in Q-C-3: derive, not pin.** The tests check the builder against the live file the console is built from. Pinning to the frozen fixture (data at `8ac7e41`) would test old data and lose that check.

## Scores

**A (the merge):**
- A1 held: no conflicts.
- A2 held: 925.
- A3 held: 0/1.
- A4 held: weigh, `bfb0238c` and PREDICTED as predicted.
- A5 held: `f3f1af17d9075ba5`, rebuilt on a clean tree.
- A6 held: ingest checks the page's spec copy, `build.py` and `template.html`, and the images. It does not re-hash `loci.ttl` (`tools/console/ingest.py`, `recompute` and `code_bytes`).

**B (the form tests):**
- B1 held.
- B2 held: 25, 12, 23, 23, 24 and 11, asserted in `test_derived_values_on_the_real_loci_file`.
- B3 held: 27 Positions and 13 Loci on the copy.
- B4 held: 929 (925 + 4 born). Only the three ruled tests are amended. No `data/`, tool or builder change.

**C (the audit):**
- C1 held.
- C2 held: 47 + 0 + 2 + 31 = 80.
- C3 held: this commit adds only the audit, this report and the ruling's "Applied" section.
