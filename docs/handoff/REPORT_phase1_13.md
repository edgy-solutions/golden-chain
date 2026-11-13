# Report 13: the overnight order of 2026-11-12

- **For:** Chris and the architect.
- **Order:** [ORDER_overnight_2026-11-12.md](ORDER_overnight_2026-11-12.md).
- **Branch:** `phase-0`, pushed through this report's commit (after `3845d50`).

All eight items were worked; none stopped under rule 8. Every prediction was locked (chmod a-w, under `~/.golden-chain/`) before its item, with one exception: item 7 had no lock, which is my omission and is recorded below. The misses are listed as they fell, and no lock was edited. The full suite: 466 passed.

## What was done

| # | Item | Commit | Predictions |
|---|---|---|---|
| 1 | Batch B: validity locus (2)–(4); the repetition Position, option (c), with the Gill *Divine Right* ch. II Holding | `d704ef7` | B1–B7 hit; **B8 missed** |
| 2 | Console v3 (silence is a complete answer; ADR-0003 R2.1–R2.2 help; the unchurches checkbox) and the sitting-1 follow-up console | `15abf36` | **C1 missed**; C2–C6 hit |
| 3 | ADR-0003 R2.3: `gc:unchurches`, ingest check e, the exclusion derivation | `8992b8b` | U1–U7 hit |
| 4 | Weigh, built from ADR-0003 (§5, §5a, R2.3, R2.4); the three R2.3 cases as its first tests | `1589f32` | W1–W5 and R1–R6 hit |
| 5 | Lone narrow glyphs at the gutter, BSB pp. 896–915, measured from pixels | `2bf1461` | N1 hit; **N2–N5 missed** |
| 6 | OCR of the baptism chapter (III.1, pp. 896–915) on substrate-v1 | `a80e076` (code) | O1, O2, O5, O6, O7 hit; **O3, O4 missed** |
| 7 | Batch C preparation: Heidelberg 65–73 and Belgic XXXIII–XXXIV source review. Nothing minted. | `3845d50` | **no lock** (omission) |
| 8 | The Q11 crops console | `dbf592c` | Q1–Q5 hit |

`a80e076` also carries [PROPOSAL_adr0006_r1_second_sitting.md](PROPOSAL_adr0006_r1_second_sitting.md), which came out of item 2.

## The misses

- **B8**
  - *Locked:* "every existing test still passes."
  - *What happened:* the form check refused a Position minted after the form was signed.
  - *Fix:* it is now a subset check, as for loci.
- **C1**
  - *Locked:* 39 fields on the follow-up form.
  - *What happened:* the content gives 37. The lock miscounted.
  - *Record:* the miss is recorded in the test.
- **N2–N5**
  - *What happened:* the locked definition of a "thin final run" counted the printed rule's own uneven edge: 72 runs, 6–15 px left of the rule's centre. So the counts, the set equality and the gap bound all missed as worded.
  - *What the measurement shows:*
    - Of 1,095 left bands, 872 end in text inside the ±120 px window.
    - None of those 872 line-final text runs is 8 px or narrower. The narrowest is 10 px.
    - So goat-yard's rule erasure clips no text on these pages, but the margin is 10 px against 8.
  - *Record:* the note is in [NOTE_goatyard_single_rule_fixture.md](NOTE_goatyard_single_rule_fixture.md).
- **Item 7, no lock.** I locked nothing before the source review. Its counts are what the pages print, so there was nothing to refute. The order says to lock before each item, though, and I did not.
- **O3**
  - *Locked:* CCEL agreement of 93–99% of column words.
  - *What happened:* 0.839 (14,477 of 17,249). Outside p. 914 it is 0.880.
  - *Causes, counted without reading the text:*
    - p. 914 agrees on 0.102 only, though its OCR confidence is normal (median 96). The alignment shows about 1,316 CCEL tokens matched to nothing just before about 780 unmatched OCR tokens from p. 914. That is an order mismatch between the two texts around pp. 914–915, and difflib cannot align a moved block.
    - Line-end hyphenation is not joined: 192 hyphenated first halves, of which 185 differ, and with their second halves about 370 differs.
    - The rest is edition difference, which the lock under-allowed.
- **O4**
  - *Locked:* a legacy italic rate of 3–15%.
  - *What happened:* 0.0279 (493 of 17,655 matched words).
  - *Where the flags fall:* 426 of the 493 flags are on one column, the left column of p. 912, where 426 of its 439 words are flagged. Outside it the rate is about 0.4%.
  - *So:* this is not a usable baseline as it stands (see the item 6 section).

## Weigh: the first real run (item 4)

The plumb-line holds 13 Positions over 7 loci, all at tier second (w = 3). 23a, 23b, 33c-new and 33d are not yet signed. Member scope:

| Body | Walls | Cost (over k loci) | Coverage |
|---|---|---|---|
| gill | 0 | 0.0000 (6) | 0.8571 |
| lbc-1689 | 0 | 0.0000 (5) | 0.7143 |
| apology-1531 | 0 | 1.0000 (2) | 0.2857 |
| small-catechism-1529 | 0 | 1.0000 (1) | 0.1429 |
| book-of-concord | 0 | n/a | 0 |
| wcf | 1 (subjects, 2 cells) | 0.4000 (5) | 0.8571 |
| augsburg | 1 (subjects) | 1.0000 (1) | 0.2857 |

- **With the two dispatch flags overlaid** (a projection only; no flag is in the data until Chris ticks it), wcf, augsburg and apology-1531 are excluded:
  - wcf 28.4, believers-and-their-infants, required;
  - augsburg ix, infants, taught;
  - apology ix, infants, taught.
- **Officer scope:** wcf gains a wall on mode (2 cells), with coverage 1.0 and 4 breaks. augsburg then ranks before wcf.

## Item 6: OCR of the baptism chapter

**Runs.** There are two runs, `~/.golden-chain/ocr-baptism-run1-2026-11-13` and `-run2-`. Both have `clean_run` True at `3845d50`.

A first attempt was stopped and set aside, and it is not used. I had committed item 7 while it ran, so its git state would have been dirty. It is kept as `ocr-baptism-ABORTED-dirty-2026-11-13`.

**What the run used:**
- **Column split:** goat-yard substrate-v1 `locate_column_rule`, unchanged, with no `ink_box`. The regions are head, left, right and foot.
- **Text:** Tesseract 5.5.0 LSTM, `--psm 4`, 850 dpi.
- **Italic flag:** the legacy engine with `tessdata` 4.1.0, matched to the LSTM words by IoU ≥ 0.5.
- **CCEL:** a flag only (agree, differ or unaligned).
- **Repo:** no OCR text and no CCEL text is in it. Everything above is local.

| | Locked | Result | |
|---|---|---|---|
| O1 | split ok 20/20 | 20/20 | hit |
| O2 | LSTM words 16,000–19,000 | 18,150 (head 522, left 8,534, right 8,715, foot 379) | hit |
| O3 | CCEL agree 93–99% of column words | 0.839 (agree 14,477, differ 2,288, unaligned 223, none 261) | **miss** |
| O4 | italic rate 3–15% | 0.0279 (493 / 17,655) | **miss** |
| O5 | match ≥ 90% | 0.9727 | hit |
| O6 | a second run is identical | words and candidates identical (sha256 of each, run 1 against run 2) | hit |
| O7 | n = 200, 100 + 100, sha256 order, built, unsigned | 200 rows, all `signed_italic` null | hit |

**Finding: the truth set is skewed.** 92 of the 100 flagged candidates come from p. 912, because that is where the flags are. The candidates were built exactly as locked.

I propose:
- a page cap, or page-stratified sampling, before any sitting;
- that the architect rule whether the legacy flag is kept as the italic baseline at all.

No model has looked at p. 912. Chris's sitting decides what its left column is.

## Item 7: Batch C preparation

The review is in [../sources/heidelberg-belgic.md](../sources/heidelberg-belgic.md), in the section "Batch C preparation". Every reference was checked on the PD page image.

- **Heidelberg.** Harbaugh, `heidelbergcatech00harb`; leaf n = p + 3. Q.65 and Q.69–73 are the (a)-sources under M4. Harbaugh was chosen over the 1863 Tercentenary edition because its scan is cleaner and it gives verses.
- **Belgic.** Schaff vol. 3, pp. 424–427, with 17 footnotes across XXXIII–XXXIV. Each anchor was placed by sense, because the markers stand in the French column only. The two placements the researcher had doubted are settled.
- **Instrumentality:** nothing is minted until F-B is answered.

## Waiting on Chris

1. **Sign the follow-up console** `c89256e734a61e4f` (sitting 1). It covers F-A (both wordings, and whether (ii)–(iii) exclude), F-B (Gill heads 2–4 and "Sixthly"), the Gill administrator paragraph, the 1677 letters for ch. 7, tiers and values, the unchurches ticks, and your testimony on the BSB foreword (row validity-3-testimony).
   - Batch C (instrumentality) waits on F-B.
   - Its data waits on the architect's item 1 below.
2. **Sign the Q11 crops console** `58b603f5500ae2a8`: two raw crops, p. 913 slab 16 and p. 915 slab 5. For each slab, say what the left and right columns hold between the magenta lines.
   - The architect's prediction is a section head or a blank line on the left in both.
3. **The two dispatch flags** (wcf 28.4; augsburg ix / apology ix). They are ticked in item 1's sitting; weigh shows them only as a projection until then.
4. **The goat-yard notes:** whether to send the single-rule fixture note (with the narrow-glyph measurement) to the goat-yard side.
5. **The italic truth set:** 200 rows are built and unsigned at `~/.golden-chain/ocr-baptism-run1-2026-11-13/candidates.json`. A signing sitting is for later.

## Waiting on the architect (numbering continues: one list)

6. **ADR-0006 R1: how a second plumb-line sitting enters the data.** See [PROPOSAL_adr0006_r1_second_sitting.md](PROPOSAL_adr0006_r1_second_sitting.md). It asks three questions:
   - option A, B or C (I propose A, a cumulative merge);
   - does silence in a later sitting remove a Holding (I propose yes);
   - is tier provenance a comment or data.

   The follow-up sitting's answers reach no TTL until this is ruled.
7. **Case (c)'s wall locus.** In the R2.3 case (c), the wall falls on validity (church-of-our-order, required, against the plumb-line's forbidden), not on repetition. That is how W3 renders it, and W3 was locked and hit. Confirm that this is the intended reading.
8. **The WORDING classes.** The unchurches wording names Congregation and Denomination, which are not classes in the ontology. Should they be minted, or should the wording be reworded?
9. **Check e on a missing tier.** Ingest check e refuses a flag on a Position whose Locus has no tier (my reading of "a tier other than third"). Confirm it.
10. **The narrow-glyph margin.** It is small: 10 px against 8. No change is asked of goat-yard. Is a standing watch wanted for other faces?
11. **The legacy Tesseract model.** The stock 5.5.0 `eng` is LSTM-only and gives no italic flag. Item 6 used `tessdata` 4.1.0 `eng`, the legacy engine (sha256 `daa0c97d…`), for the flag only. Adopt it, or name another italic source.
12. **Harbaugh as the Heidelberg proof source.** It is chosen under M4's "whichever scan is cleaner". The 1889 date comes from the catalogue only. Confirm the choice.
13. **M4: admission by division or by clause.** Eight of the seventeen Belgic footnotes hang on clauses that are not about efficacy. I propose admission by clause, as marked in the source review.
14. **M4's expected gap.** Acts 22:16 *is* printed by (a)-sources: Harbaugh Q.69, Harbaugh Q.71 and Belgic XXXIV p. 426 fn4. So (a) can carry an Argument on it.
15. **Misprinted references.** Each is kept as printed:
    - Harbaugh p. 109 "Rom. v. 11";
    - Schaff p. 425 "Matt. xxvi. 36";
    - Schaff p. 426 "Apoc. i. 6".

    Should a Passage take the corrected reference with an `asPrinted` note? I propose yes, and only for p. 426, which is the only one in an efficacy clause.
16. **Passages printed by both Heidelberg and Belgic.** Nine passages are printed by both. Is that one Argument per source, or one Argument with two sources?
17. **The italic truth set's sampling** (item 6): 92 of the 100 flagged candidates fall on p. 912. Should sampling be page-capped or page-stratified, and is the legacy flag kept as the baseline?
