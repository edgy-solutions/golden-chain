# Report 20: the ruling on report 19, worked

- **From:** the build agent, 2026-11-17.
- **On:** [RULING_report_19.md](RULING_report_19.md) (filed verbatim, `4b94b00`).
- **In short:**
  - A-1 to A-3, A-5 and A-7 (build hash) are done and pushed.
  - A-7 (measure v4) and A-6 (the redraw) are locked, built and run: the measure is corrected (T 0.11, the comb gone), the draw is full (200), and one build hash comes from two runs; but 16 crops (8 %) still dropped, so the console is held for the architect's word (A-11).
  - A-4 is the architect's own item.
  - C-7 is closed; PX4 is noted.

## A-1. "Read by" as an annotated axiom (ADR-0002 Revision 3), `3c6933f`

- **No new property.** Each of the 11 architect-read LBC `gc:asPrinted` strings carries an `owl:Axiom` with:
  - annotated source the Argument;
  - property `gc:asPrinted`;
  - target the string;
  - `dcterms:contributor <agent/architect>` and `gc:status <vocab/status/proposed>`;
  - an `rdfs:comment` "read by".
- The Arguments' "model-proposed" `rdfs:comment` stays, as the ruling allows.
- Ingest check d now requires, on every asPrinted axiom:
  - exactly one contributor that is a `gc:Agent`;
  - status proposed or ratified;
  - a target that is the asserted string.
- The three ch. 7 transcription strings get no axiom (they were not read by a model).
- The prototype reads the axiom and prints "proposed reading, unconfirmed" beside the string.
- When Chris confirms on the LBC 1677 console, the contributor becomes `agent/chris` and the status `ratified`. The console's ingest does that flip; it is not hand-edited.
- 9 tests were born (`tests/test_asprinted_axiom.py`, plus the prototype test).

## A-2 and A-3. ADR-0007 and ADR-0008 ratified, `3c6933f`

- **ADR-0007:** its Ratification section applies the architect's answers, point by point, to the open points and to the Decision items they amend: several parents are allowed; a Holding from personal knowledge is allowed, labelled; the church is cited by URL, read date and archived URL. It adds the page statement (who entered it, from what and when; how the church may correct it). The ruling itself is filed verbatim.
  - **Nothing is built from it yet.** The order did not say to build. Before building, its Verification needs a lock. Asked below (A-9).
- **ADR-0008:** ratified as a local prototype.
  - The disclosure is per A-1.
  - Passage pages show the reference only (as built).
  - Deployment is a separate ADR, not drafted.

## A-5. Phase-2 sources, `2c5e568`

Each file's last section records the ruling and what was done. No text is stored.

| Ruling | Done | Tag |
|---|---|---|
| Scots: add the review (Schaff vol. 3) | [scots.md](../sources/phase2/scots.md): pp. 437–479, Scots and Latin columns, Art. N plus printed page; 7 article starts checked on images, 6 from OCR text only | [V]/[R] |
| Witsius: Crookshank 1763 | the witness of record; the 1798 contents are for orientation only | ruled |
| Gill Doctrinal II: 16 or 17 | **16.** On the BSB contents images, "Of Justification as an Immanent Act" (p. 203) is an unnumbered sub-entry of II.5 "Of Adoption as an Immanent Act" (p. 201). The Tegg OCR promoted it to a chapter. | [V] |
| Gospel Standard: earliest printing with a page image | **Not reached.** *The Gospel Standard* vols. 38 (1872), 44 (1878) and 45 (1879) are located as PDFs, but this session's permission check refused the download, and I did not work around it. Waits on Chris (C-9). The date conflict (arts. 1–31 in 1872 or 1878; arts. 32–35 added in 1878 or April 1879; footnotes later) is recorded as a finding. PD basis: a corporate, anonymous-on-its-face work of the 1870s; UK term 70 years from publication (CDPA s.12(3)); the named amenders are also more than 70 years dead; US pre-1930. | [R] |
| Spilsbury: cite the scan; read the TCP licence | Scan cited (IA microfilm, 49 images; title page viewed; the date's last digit is cropped). TCP A61127 README read: CC0 1.0 for the keyed text, not the page images. The keyed text may be used for locating; it is not stored. | [V] |
| Dort in English with the Rejections: Scott 1831 | **Found and verified** on page images: Utica, William Williams, 1831, IA `articlesofsynodo00syno` (Princeton, not in copyright). Scott says he translated literally from the *Sylloge Confessionum* (Oxford, 1804). Chapters I (p. 87), II (99), III & IV (105) and V (116), and the first Rejection of Errors (p. 94), were seen; the other Rejections were located from running heads. Caution: the volume's appended "Harmony" is not Scott's. | [V] |
| Huntington: the earliest printing | The 1786 first printing (Denew and Grant; title viewed) is the witness. 1788 and the *Works* are second witnesses. | [V] |
| Belgic leaf offset | BookReader n = page + 15, checked at four pages (and on the Scots pages). It holds across the deleted leaves 432–433 because n skips them while scandata's leaf count does not. | [V] |

## A-7 (build hash). ADR-0006 Revision 5, `2cc4412`

Lock `build-hash-r5-predictions-locked.txt`, locked at `3c6933f`.

| # | Predicted | Result | |
|---|---|---|---|
| BH1 | v3 specs a and b rebuilt: one build16; spec copies byte-identical; the manifests differ only in local, spec_path and utc; HTML identical given the same git state | one build16 `21c0b8a562143ccd`; spec copies byte-identical; the manifests differ in local, spec_path, utc **and html_sha256**; the git fields are the same | **missed** (HTML) |
| BH2 | no drive path, `/Users/`, `\Users\`, `utc` or `run_header` in the spec copies | none in either | hit |
| BH3 | consoles under /1 still ingest; the `--code-at` tests pass unedited | unedited, pass | hit |
| BH4 | 631 + new, 0 failed; only old-rule tests edited, each named | **646 passed** (15 born), 0 failed. Edited: the `make_export` helper, `test_build_hash_is_the_stated_rule`, `test_template_version_in_header_and_manifest`, and `test_template_version_is_6` (renamed `_7`). The last two are version-pin tests that the lock's wording did not foresee. | hit (two unforeseen edits named) |
| BH5 | weigh and ingest unchanged | 71c14a5d187d / c8fe9e910b5a; 0 violations, 3 warnings | hit |

- **BH1, the cause.** The two HTML files differ in 4 characters, all in the run header's time inside the page's data (`04:48:51` against `04:53:29`).
  - R5 kept the run header on the page (item 5: "the page header and the export take the run header from the local block"). So two runs can never give byte-identical HTML.
  - The build hash, which is what Chris signs, is one. The lock's HTML clause was wrong, and it is not edited.
  - The v4 lock (IV5) predicts this difference instead.
- These were verification builds into the scratchpad, never put to Chris (A-6).

## A-7 (measure) and A-6 (redraw). Italic v4

Lock `italic-v4-predictions-locked.txt`, locked 2026-11-17T13:22:40Z at `2c5e568` before any v4 code existed. The choices are stated in the lock, as ordered:

- **Measure (A-7): the "same resampling" option.**
  - For every candidate shear, zero included, each ink pixel is deposited by linear split onto a 1/4-px grid.
  - The profile is then smoothed with one fixed Gaussian (σ = 1 px).
  - The Gaussian dominates the deposit's blur, so the blur is the same at every shear and every phase. A born test bounds the phase effect below 0.5 %.
  - Everything else is v3's.
  - T = 0.14 stands as v3's value.
- **Padding (A-6):**
  - word x by line y, padded 12 px;
  - each side clipped at the midpoint to the nearest other line overlapping the word's x range, never inside the line's own box;
  - one cut, no re-cut.
- **Edge (A-6):** ink at the top or bottom fails only if it is 8-connected to ink inside the word's OCR box.
  - Carried into the console's build check as ADR-0006 **Revision 6** (`word_box` beside `clear_edges`). That is my application of the ruling to the console, written for the architect to read (A-8).
- **Quotas (A-6):**
  - per stratum, total = quota × pages;
  - pass 1 takes up to the quota on each page;
  - the shortfall is then given round-robin in ascending page order to pages that still have words.
- **New salt** `truthset-v4/`; v2 and v3 keys are excluded.

Built and committed in `9028ac1`. Runs a and b were made on a clean tree, with no commit during them. Inputs: `ocr-baptism-run1-2026-11-13`; the v2 and v3 candidates were excluded. Outputs (local only): `~/.golden-chain/slant-v4-2026-11-17-{a,b}`, `truthset-v4-2026-11-17-{a,b}`, `truthset-v4-crops-2026-11-17-{a,b}`, and `console/truthset-italic-v4/`.

| # | Predicted | Result | |
|---|---|---|---|
| IV1 | eligible 12474; small ≤ 10; edge ≤ 150; bimodal; T in [0.08, 0.16]; slanted in [550, 850] | 12474; 0; 84; bimodal; **T = 0.11**; slanted 700 (measured 12390) | hit |
| IV2 | the comb gone: no empty bin between occupied ones, no deep dip | none of either. Bin −0.02..0 holds 2696, between 4023 and 1252 (v3: 43 between 1953 and 7272). | hit |
| IV3 | n = 200 (80/80/40); 0 shared with v2 or v3; reallocation listed | 200 (80/80/40); 0 and 0; slanted: pp. 896, 904 and 908 short by 4 each, 12 words given one each to 12 pages; edge: 8 pages short by 11, given to 8 pages; upright: none short. Digest `49788cb9…` | hit |
| IV4 | dropped ≤ 4 of 200; none more than 2 in any stratum | **16 of 200 (8 %)**: upright 9, slanted 5, edge 2; top 10, bottom 5, both 1 | **missed** |
| IV5 | a and b byte-identical; clean_run true; one build hash; HTML differs only in the run header | slant.json, candidates.json, crops.json and drops.json byte-identical; clean_run true in all six run headers; **one build hash `8e173740c37b714d`**; HTML differs in 3 characters, the run header's time | hit |
| IV6 | suite passes, no existing test edited; weigh and ingest unchanged; no data change | **698 passed** (52 born), 0 failed, no existing test edited; weigh 71c14a5d187d / c8fe9e910b5a; ingest 0 violations, 3 warnings; no `data/` change | hit |
| IV7, IV8 | after signing | not signed (below) | — |

**The drops (IV4).** This is from numbers only: crop geometry and edge counts in code. No crop was viewed.
- **Little room.** The midpoint clip leaves little room. Among the kept rows the median pad actually given is 3 px above and 3 px below (12 asked): the leading is tight.
- **10 of the 16 had 0 px on the failing side.** The neighbouring line's box meets or overlaps this line's, so the clip stopped at the line's own box.
  - Those 10 also have unusually tall line boxes, 105–141 px against about 80 px for the others.
  - My hypothesis, unverified: the OCR grouped two printed lines into one line key, so the union box spans them.
- **6 of the 16 had the full 12 px on the failing side** (5 top, 1 bottom). Ink connected to the word reaches more than 12 px beyond the line box. The cause is unknown.
- **Kept:** slanted 75, upright 71, edge 38 (184).

**Not put to Chris.**
- The miss is smaller than v3's (8 % against 19.4 %), but it is again uneven by stratum (upright loses 9 of 80).
- A-6 ruled out spending the one signer on a biased set, so I did not decide this myself.
- The console is built: build-a `8e173740c37b714d`, 184 rows, not provisional. Its README says HOLD.
- Asked as A-11 below.

## Noted

- **C-7 closed** on the architect's word (Chris answered; the further disclosure is on file).
- **PX4:** the page is right; pairs, not distinct Holdings. No change.
- **Italic v3 build-a `015bfeed482a5083`** stays on record, unsigned. Report 19's C-5 is withdrawn.

## What waits, on whom

### Chris

- **C-1.** Sign the p. 914 re-ask `d7a6aab0734ffe3e` (`~/.golden-chain/console/region-reask/build1/`).
- **C-2.** Sign the follow-up `eb961ddb1e582ed6` (`~/.golden-chain/console/plumb-line-followup/`).
- **C-3.** Tell the goat-yard architect that the Hebrew span crop is theirs (if not yet done).
- **C-4.** Put the LBC 1677 photographs in the private corpus. The console is then built, and your confirmations flip the 11 axioms to `agent/chris`, ratified.
- **C-5.** Report 19's C-5 is withdrawn (do not sign italic v3). The italic v4 console `8e173740c37b714d` is built but **on hold** until the architect answers A-11.
- **C-6.** Sign your words of 2026-11-15 when the phase-2 justification Locus exists.
- **C-8.** ADR-0007 is ratified: which church first, if any.
- **C-9.** The Gospel Standard volumes 38 (1872), 44 (1878) and 45 (1879) from biblicalstudies.org.uk. Either allow the build agent to fetch them, or download them into the private corpus. Until then there is no witness of record for the Articles.

### The architect

- **A-4.** The locus table (yours; nothing waits on it).
- **A-8.** Read ADR-0006 Revision 6, the word-connected edge check carried into the console. Ratify, or say otherwise.
- **A-9.** ADR-0007: build now? First its Verification would be locked as amended (provenance line, the coverage count for "excepted, unknown", proposed until a named person confirms).
- **A-10.** The phase-2 candidate locators (Scots, Dort/Scott, Huntington, Spilsbury) are proposals from headings. They wait for your reading of the texts before any Position cites them.
- **A-11.** Italic v4: the draw dropped 16 of 200 crops (IV4 missed; upright 9, slanted 5, edge 2). Choose one:
  - (a) Chris signs the 184 as they stand.
  - (b) **Proposed.** Redraw under a new lock in which a dropped row is replaced by the next word of the same page and stratum in order-key order, with the reallocation as now. The strata stay full, and the drop rule is unchanged.
  - (c) As (b), and also treat a line box taller than a stated multiple of the page's median line height as two printed lines merged by the OCR, clipping at the word's own box instead.
- **A-12.** BH1's HTML clause missed, because R5 keeps the run header on the page. Accept that the HTML differs between runs while the build hash does not? (IV5 assumed so and hit.)
