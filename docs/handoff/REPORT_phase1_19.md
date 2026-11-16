# Report 19: the overnight order of 2026-11-15

- **For:** the architect, through Chris; and Chris.
- **Order:** [ORDER_overnight_2026-11-15.md](ORDER_overnight_2026-11-15.md), filed verbatim. **Ruling worked:** [RULING_report_18.md](RULING_report_18.md).
- **Branch:** `phase-0`, pushed through this report's commit.

All seven items were worked. No question stopped the work. Each question is in the single list at the end ([What waits, on whom](#what-waits-on-whom)).

## Item 1. The further disclosure, applied

- **Empty strips.**
  - [AUDIT_empty_strips_88d902a181ba64c1.md](AUDIT_empty_strips_88d902a181ba64c1.md) registers the six foot rows as "architect had described an earlier cut".
  - Those readings went against the architect's, and they stand as signed. The signed record is not edited.
- **LBC 1677 margins.**
  - `gc:asPrinted` on the 11 Arguments of 28.1–29.4 now carries an `rdfs:comment`. It says the reading is model-proposed (read by the architect from Chris's photographs) and awaits Chris's confirmation.
  - Lock `lbc-model-proposed-predictions-locked.txt`, LM1–LM4: **all hit** (11 comments, +11 triples, ch. 7 unchanged, weigh unchanged, 565 passed).
  - Dated notes are in [lbc-1689.md](../sources/lbc-1689.md).
  - The comment is the existing-vocabulary route. A typed property is a question (A-1).
- **The LBC 1677 console**
  - **Rows:** [lbc1677_rows.json](../../tools/console/specs/lbc1677_rows.json), 15 note rows cross-checked against the data (0 mismatches).
  - **The builder:** `tools/console/specs/lbc1677.py` (kind `lbc1677`; commit `e380d33`). It has 21 rows: the witness row, the 15 note rows (confirm or correct, each checked against the data's `asPrinted` at build time) and one "anything unlisted?" row per chapter group. Every field has a plain-words line. 8 tests were born with it.
  - **It cannot be built** until Chris puts the photographs in the private corpus. **The pages needed:**

    | Group | What the photograph must show | File name |
    |---|---|---|
    | title | the title page of the facsimile (edition and year) | `lbc1677_title_1.jpg` |
    | ch07 | ch. 7, paras 1–3, with both margins (notes e, f, *) | `lbc1677_ch07_1.jpg` (and `_2` if it runs over) |
    | ch26 | ch. 26 para 15, with its margin (note g) | `lbc1677_ch26_1.jpg` |
    | ch27 | ch. 27 para 1, with its margin (notes a–c) | `lbc1677_ch27_1.jpg` |
    | ch28 | ch. 28 paras 1–2, p. 96, with its margin (notes a, b) | `lbc1677_ch28_1.jpg` |
    | ch29 | ch. 29 "Of Baptism", sig. H, paras 1–4, with its margin (notes c–h) | `lbc1677_ch29_1.jpg` (and `_2`) |

    - Each photograph shows the whole page, including the margins and the page number or signature mark.
    - JPEG or PNG.
    - They go in one folder of the private corpus, never in this repo.
- **Goat-yard's Hebrew span crop** is recorded as goat-yard's matter (C-3: Chris tells the goat-yard architect).

## Item 2. Plain words on every question (ADR-0006 Revision 4)

- **The check:** `check_plain` fails a field that has no `plain`, a blank one, or one of three or more sentences. It also fails an option field whose `plain` does not name every option as a whole word, and a non-proposal option field whose `plain` does not say "other, as written".
- **The template:** `TEMPLATE_VERSION` is 6, and the page shows the `plain` line under each question.
- **The builders:** all seven carry `plain` strings, drafted from each form's own text.
- **My review changed four strings:**
  - plumb-line modality: "your stance";
  - plumb-line unchurches: the help's own rule (forbidden, not tier third);
  - follow-up proposals: these are wordings to accept, not page readings;
  - "shown on a grey background".
- **The whole-word rule** is my tightening. The implementer found that "no" matched inside "none", and a test is born for it.
- **Lock** `plain-words-predictions-locked.txt`: **PW1–PW5 all hit.**
  - PW1: 575 passed (565 + 10).
  - PW2: `TEMPLATE_VERSION` 6.
  - PW3: the four Fail cases.
  - PW4: weigh `71c14a5d187d` / `c8fe9e910b5a`.
  - PW5: no built console changed. The re-ask `d7a6aab0734ffe3e` and the follow-up `eb961ddb1e582ed6` recompute their build hash with `--code-at` at `11a905f` and `9836117`, and fail without it.
- **Commit:** `25b7d3e`.
- Built consoles are not rebuilt, per the ruling.

## Item 3. Italic: restated, then the finer measure

- **The restatement** of SI3 and F-4, with w017 and the clip-noted rows held out, is [report 18 §3](REPORT_phase1_18.md). It is not repeated here:
  - SI3 as locked stays missed (65/76);
  - with the holdouts it is 64/70 = 91.4 %;
  - at 0.20 the call is 36 italic against 6 roman;
  - from 0.25 up it is exact.

- **The finer measure (v3):**
  - lock `italic-v3-predictions-locked.txt`, taken before any code;
  - `tools/gy_word_slant_v3.py`: sub-pixel shear, ink at the mode midpoint, word x with line y box;
  - draw `tools/truthset_v3.py`: salt `truthset-v3/`, v2 keys excluded;
  - crops `tools/truthset_crops_v3.py`: vertically padded, with the ink-at-edge check on, re-cut once with a larger pad, else dropped;
  - console kind `truthset-italic-v3`, with `clear_edges`;
  - commit `5cd7918`. 28 tests were born with it.
- **Runs:** a and b on a clean tree, at `5cd7918`, outputs under `~/.golden-chain/` (`slant-v3-…`, `truthset-v3-…`, `truthset-v3-crops-…`, each `-a` and `-b`).

| | Predicted | Got | |
|---|---|---|---|
| FM1 measure | eligible 12474; abstain_small ≤ 10; abstain_edge ≤ 1227; bimodal; T in [0.07, 0.13] | 12474; 0; 87; bimodal (measured 12387, slanted 692); **T = 0.14** | **missed** (T only) |
| FM2 the comb gone | no empty bin between non-empty neighbours; no bin below a quarter of the smaller neighbour where both are ≥ 40 | no empty bin; **bin −0.02..0 holds 43, between 1953 and 7272** (a quarter of 1953 is 488) | **missed** |
| FM3 draw | n in [190, 200]; 0 shared with v2; only p. 896 may be short (of slanted) | n 191 (slanted 75, upright 80, edge 36); 0 shared; 196 v2 keys excluded; digest `ef084dd5…`. **Short pages:** 896 (slanted 3), 904 (slanted 2), 908 (slanted 2), 907 (edge 1), 909 (edge 0), 910 (edge 1) | **missed** (last clause) |
| FM4 crops dropped | ≤ 5 % of n after one re-cut at ± 12 px | **37 of 191 = 19.4 %**: 154 first cut, 0 re-cut, 37 dropped | **missed** |
| FM5 reproducible | slant, candidates and crops byte-identical; clean_run true; one build hash from a and b | byte-identical (only the header time differs); clean_run true in all six headers; **build hashes differ**: `015bfeed482a5083` (a), `03a299fb575fc4c3` (b) | **missed** (last clause) |
| FM6 suite, weigh, data | pass, same, none | 622 passed (586 + 36: italic v3 28, LBC 1677 8); weigh `71c14a5d187d` / `c8fe9e910b5a`; no data change, at `5cd7918` | hit |
| FM7, FM8 | slanted → italic ≥ 90 %; upright → roman ≥ 97 % | judged after Chris signs | — |

- **FM2, the cause found (not fixed).** The split is linear between pixels, so any non-zero shear blurs every row a little and lowers the sum-of-squares score. Shear 0 (no blur) is favoured.
  - Per-value counts near zero: −0.03: 1029, −0.02: 42, −0.01: 1, 0.00: 7271, 0.01: 1, 0.03: 20.
  - The comb moved; it did not go.
  - A correction (normalising the score for blur, or resampling every shear including 0) is a design change. It is put to the architect (A-7), not made.
- **FM4, the drops.**
  - By side: bottom 22, top 8, both 7.
  - By stratum: slanted 18, upright 13, edge 6.
  - Kept: slanted 57, upright 67, edge 30 (154).
  - The re-cut never helped (0 of 37). My hypothesis, unverified: the leading is tight, so a larger pad reaches the next line's ink. This was not checked by viewing any crop (rule 11 and the image rules).
- **FM5, why the hashes differ.** The spec records each crop's absolute path (`…-crops-2026-11-15-a` vs `-b`) and run b's header time. That accounts for all 310 differing lines; no other line differs. The PNGs and `crops.json` are byte-identical.
  - v2's "one build hash" (report 15, TC5) came from building once and rebuilding from the same crops directory. The v3 lock asked for one hash from a and from b, which this build cannot give while paths are in the spec.
  - The lock is not edited. Whether the build hash should exclude paths and times is a question (A-7).
- **The console**, built and left for Chris:
  - `~/.golden-chain/console/truthset-italic-v3/build-a/console_truthset-italic-v3_015bfeed482a5083.html`;
  - 154 rows; `README_WHICH_TO_SIGN.txt` names build-a;
  - `TEMPLATE_VERSION` 6, with plain words on every question;
  - no model has seen any crop of this draw.

## Item 4. Phase-2 source reviews (review only)

[docs/sources/phase2/](../sources/phase2/README.md) holds eight reviews. They store no text, only titles, imprints, headings, catalogue identifiers and URLs. Nothing is minted.

| Work | Witness found | Locators |
|---|---|---|
| Witsius | Crookshank's English, PD; 1763 and 1798–1804 scans on IA; **no scan of the 1822 London edition** | I.1–9 (covenant of works), II, III.8 (justification) by heading |
| Dort | Schaff's Latin (his English is abridged and has no Rejections); 1619 English (STC 7066) unscanned | all unconfirmed |
| Belgic 27–29, 33–36 | Schaff, printed pages | by article and page; Schaff prints no paragraph numbers |
| Spilsbury 1643 | Wing S4976, TCP A61127 | none yet (licence of the TCP text unread) |
| Gill | as phase 1 | Doctrinal II.5, VI.7–8; Practical III.1 (administrator, Tegg ii. 621–622) |
| Fuller | 1785 Northampton on IA | none yet (no contents read) |
| Gospel Standard | 1878–79 periodical | article numbers by heading; dates conflict |
| Huntington | *The Law Established by the Faith of Christ*, a 1786 sermon | its numbered heads |

## Item 5. Phase-2 locus table (PROPOSED, a document only)

- **The table:** [PROPOSAL_phase2_loci.md](PROPOSAL_phase2_loci.md), with nine rows and the order's questions.
- **Candidate Positions** are my wording, for the architect to reword. Each is tied to an item-4 or phase-1 locator, or marked "none located". No locator has been read for content.
- **Chris's words of 2026-11-15** are recorded verbatim on row 1, unsigned, as the seed of a future plumb-line Argument. They are not attached to any Position.

## Item 6. Congregations (design only)

- [ADR-0007](../adr/0007-congregation-onboarding.md), proposed.
- A Congregation is `gc:childOf` its parent Body.
- An exception that names an alternative is a Holding, which uses the ADR-0003 §7 per-Locus override.
- An exception that names none needs one new property, `gc:exceptsLocus`. The cell is then "excepted, unknown", never tolerated.
- The ADR includes a console form Chris could fill for a church he knows, built from the data, with plain words on every question.
- Weigh's rendering marks each cell inherited, own or excepted.
- No instances are minted.

## Item 7. The `examine` / `try` prototype (local, read-only)

- **Tool and ADR:**
  - `tools/prototype/examine_try.py` is static HTML from the Jena TDB2 store, with no server and no script.
  - [ADR-0008](../adr/0008-examine-try-prototype.md) is proposed. Commit `8d4de2f`.
- **Only data strings:**
  - The query's predicate allow-list is the only way data reaches a page. The 86 free-text strings in the data (`rdfs:comment`, `resolutionNote`, `quotation`, `derivedBy`) were searched for on every page: 0 found.
  - Every page carries the PROTOTYPE banner.
- **Output:** `~/.golden-chain/prototype/run-a` and `run-b`, at `8d4de2f`, clean run.

**Lock `prototype-examine-try-predictions-locked.txt`:**

| | Predicted | Got | |
|---|---|---|---|
| PX1 pages | 1 + 12 + 140 = 153 | 153 | hit |
| PX2 Positions / Arguments, per locus | 24 / 80, 11 3 7 3 2 11 9 5 8 4 12 5 | the same, counted on the pages | hit |
| PX3 cites rows | 217 | 217 | hit |
| PX4 Holdings shown, each once | 54 | **55 cells** | **missed** |
| PX5 banner; no free text | every page; none | 153/153; 0 | hit |
| PX6 two runs identical; local only | yes | `diff -r` identical | hit |
| PX7 suite, weigh, data | pass, same, none | 586 passed (575 + 11), same, none | hit |

**PX4 missed.** The data has 54 distinct effective Holdings over 7 Bodies, but the tables show one cell per (Body, Holding). The Apology 1531 inherits Augsburg's `baptism-efficacy/necessary-means-of-grace` by `gc:childOf`, so that Holding appears twice. The prediction counted distinct Holdings where the page counts pairs. The page is right; the lock is not edited.

## What waits, on whom

### Chris

- **C-1.** Sign the p. 914 re-ask `d7a6aab0734ffe3e` (`~/.golden-chain/console/region-reask/build1/`).
- **C-2.** Sign the follow-up `eb961ddb1e582ed6` (`~/.golden-chain/console/plumb-line-followup/`).
- Both C-1 and C-2 predate plain words. If a row is unclear, ask the build agent: the answer comes from the form's text, and your question is recorded.
- **C-3.** Tell the goat-yard architect that the Hebrew span crop is theirs.
- **C-4.** Put the LBC 1677 photographs in the private corpus (the table under item 1). The console is then built and left for you.
- **C-5.** Sign the italic v3 console, build-a `015bfeed482a5083` (`~/.golden-chain/console/truthset-italic-v3/`, 154 rows). FM7 and FM8 are judged from your signature. Rule 11 applies: if a row is unclear, ask, and the answer comes from the form's text. You may prefer to wait for the architect's word on A-6 (whether a draw with 19 % of crops dropped should be signed at all).
- **C-6.** Sign your words of 2026-11-15 when the phase-2 justification Locus exists (row 1 of the proposal).
- **C-7.** Report 18 Q-3, still open: was any other row of any sitting shown to a model?
- **C-8.** Once ADR-0007 is ratified: which church first, if any.

### The architect

- **A-1.** A typed property for "model-proposed / read by", in place of the `rdfs:comment` on the 11 LBC Arguments. It needs an ADR. Until then the prototype shows those `asPrinted` strings without the disclosure (ADR-0008 open point 1).
- **A-2.** [ADR-0007](../adr/0007-congregation-onboarding.md): ratify or amend. Its open points:
  - `gc:exceptsLocus` or a new modality;
  - several parents;
  - citing a church's statement by URL and read date.
- **A-3.** [ADR-0008](../adr/0008-examine-try-prototype.md): ratify or amend. Its open points:
  - the asPrinted disclosure;
  - passage pages without verse text;
  - any deployment (a separate ADR).
- **A-4.** [PROPOSAL_phase2_loci.md](PROPOSAL_phase2_loci.md): reword the questions and Positions, and decide:
  - the splits on rows 1 and 2;
  - rows 6 and 7 against Locus 23;
  - whether row 8 (Trinity) gets a contrary Position.
- **A-5.** Source gaps and questions from item 4:
  - the Scots Confession had no review (the order names Scots 18);
  - no scan of the 1822 Witsius (the 1763 Crookshank is proposed instead);
  - Gill's Doctrinal Book II has 16 chapters in the BSB tally and 17 in another listing;
  - the Gospel Standard Articles' date (1872 or 1878) and their UK PD status (corporate authorship);
  - the licence of Spilsbury's TCP text;
  - no scan of the 1619 English Dort;
  - which Huntington printing is the witness (1786 or 1788);
  - Belgic's leaf offset is unchecked.
- **A-6.** Italic v3, the draw:
  - 37 of 191 crops were dropped (FM4 missed: 19.4 % against ≤ 5 %), so the strata are uneven (slanted 57 of 75 kept);
  - should Chris sign this draw as it stands, or wait for a redrawn set with a different padding design (for example, padding clipped at the midpoint to the neighbouring line);
  - and six pages, not one, came up short in the draw (FM3): the slanted and edge words run out on some pages before the quota.
- **A-7.** Italic v3, the measure and the build:
  - FM2: the linear split favours shear 0 (cause above). Should the measure be corrected under another lock, or the dip at −0.02..0 be accepted?
  - FM1: T came out at 0.14, just outside the locked range. Does T stand as measured?
  - FM5: should the console build hash leave out absolute image paths and run-header times, so that two clean runs give one hash? That is a change to ADR-0006's build hash and needs a revision.
