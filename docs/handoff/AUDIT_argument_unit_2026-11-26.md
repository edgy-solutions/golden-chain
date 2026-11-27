# Audit: the existing Arguments against the quotation unit (ruling on report 29, Q-C-2)

- **From:** the build agent, 2026-11-26.
- **On:** [LOCK_report29_2026-11-26.md](LOCK_report29_2026-11-26.md), C1-C3, and ADR-0005 as amended (the unit is the quotation unit as the source prints it).
- **Nothing is changed:** no data and no test.

**Scope:** the 80 Arguments in `data/` at `72c4afb`, before Batch C.

**First pass: from the printed strings only.** Every one of the 80 carries `gc:asPrinted`. No page was viewed for this pass.

**Why no page yet:** Gill's *Body*, pp. 897-914, are the pages of Chris's open italic-spans sitting (`9b19159be3098c64`). Under rule 11 and the sitting practice, the build agent does not look at those pages until it is signed. The other pages are named below for a second pass.

## Counts by source

| Source | Arguments | Same cut | Would merge | Would split | Cannot tell without the page |
|---|---|---|---|---|---|
| WCF (1647) | 25 | 25 | 0 | 0 | 0 |
| LBC 1689 | 14 | 14 | 0 | 0 | 0 |
| Belgic Confession (Schaff) | 1 | 1 | 0 | 0 | 0 |
| Luther, Small Catechism (Triglot) | 2 | 2 | 0 | 0 | 0 |
| Apology (Triglot) | 2 | 0 | 0 | 0 | 2 (Art. IX; the data has no page number) |
| Gill, *Body of Divinity* (BSB) | 26 | 5 | 0 | 0 | 21 (pp. 247, 361, 897-912) |
| Gill, *Divine Right* | 5 | 0 | 0 | 0 | 5 (pp. 45-47) |
| Coxe, *Covenants* | 4 | 0 | 0 | 1 | 3 (pp. 36-38) |
| Graves, *Old Landmarkism* | 1 | 0 | 0 | 1 | 0 |
| **Total** | **80** | **47** | **0** | **2** | **31** |

## The basis for each column

**Same cut (47).**
- **The confessions (40):** WCF, LBC 1689 and the Belgic Argument. They have been cut one Argument per lettered note since ADR-0005's amendment on report 2. A lettered note is the confession's quotation unit, and each `gc:asPrinted` opens with its note mark. Where one note supports two Positions it is two Arguments, one per Position, which the unit allows. Examples: WCF 28.4 note m, 7.5 note i, and LBC 29.2-29.4 notes f-h.
- **The Small Catechism (2):** each Argument is the quoted verse with the reference the text gives ("in the last chapter of Mark", "Titus, chapter three"). That is the Harbaugh-type unit.
- **Gill, *Body*, Doctrinal IV.1, Introduction (1):** the string is one syntactic run ("the epistle to the Hebrews, chap. viii. 7, 8, 13. and ix. 1, 15. and xii. 24.").
- **Gill, *Body*, Practical III.1 "Sixthly" 1-4 (4):** checked against p. 914 for Batch C (LOCK_batchC_unit, the heads table).

**Would split (2).** The string itself shows more than one printed unit. How many units each becomes needs the page.
- `coxe-covenants/5/8/001`: it spans pp. 105-109, and its string runs prose between references ("Gen. 17. 4, 5. Rom. 4. 17. Rom. 4. Read diligently Gal. 3. Rom. 4. 11. Gen. 17.").
- `graves-old-landmarkism/10/001`: three parenthetical references, separated by ellipses ("(Matt. 16: 18) ... (Heb. 12: 28) ... Daniel (2: 44)"). That is up to three units on p. 124.

**Would merge (0).** No two Arguments on one Position share one printed unit, as far as the strings show. Gill *Body* Doctrinal II.15, head 1 (p. 247) has three Arguments on one Position. They are three runs if the page prints them in three clauses, and one unit if it prints them in one. That is why they are counted under "cannot tell".

**Cannot tell without the page (31).** Each is one inline run, or a single reference, in a treatise. A string cannot show whether the run closes one clause or whether the page prints more references in the same run.
- The second pass needs these pages: Triglot (Apology Art. IX), Coxe pp. 36-38, Gill *Body* pp. 247, 361 and 897-912 (after the italic sitting is signed), and Gill *Divine Right* pp. 45-47.
- All are public domain. The build agent may view them to propose (report 6, Q4).

## Each Argument, by column

- **Same cut (47):** `belgic-confession/34/001`, `gill-body/doctrinal/4/1/001`, `gill-body/practical/3/1/018`, `gill-body/practical/3/1/019`, `gill-body/practical/3/1/020`, `gill-body/practical/3/1/021`, `lbc-1689/28/1/001`, `lbc-1689/28/2/001`, `lbc-1689/29/1/001`, `lbc-1689/29/1/002`, `lbc-1689/29/1/003`, `lbc-1689/29/2/001`, `lbc-1689/29/2/002`, `lbc-1689/29/3/001`, `lbc-1689/29/3/002`, `lbc-1689/29/4/001`, `lbc-1689/29/4/002`, `lbc-1689/7/3/001`, `lbc-1689/7/3/002`, `lbc-1689/7/3/003`, `small-catechism-1529/4/001`, `small-catechism-1529/4/002`, `wcf/27/1/001`, `wcf/28/1/001`, `wcf/28/1/002`, `wcf/28/1/003`, `wcf/28/1/004`, `wcf/28/1/005`, `wcf/28/1/006`, `wcf/28/1/007`, `wcf/28/2/001`, `wcf/28/3/001`, `wcf/28/4/001`, `wcf/28/4/002`, `wcf/28/4/003`, `wcf/28/5/001`, `wcf/28/5/002`, `wcf/28/5/003`, `wcf/28/6/001`, `wcf/28/6/002`, `wcf/28/7/001`, `wcf/7/3/001`, `wcf/7/5/001`, `wcf/7/5/002`, `wcf/7/5/003`, `wcf/7/6/001`, `wcf/7/6/002`
- **Would merge (0):** none.
- **Would split (2):** `coxe-covenants/5/8/001`, `graves-old-landmarkism/10/001`
- **Cannot tell without the page (31):** `apology-1531/ix/001`, `apology-1531/ix/002`, `coxe-covenants/2/10/001`, `coxe-covenants/2/10/002`, `coxe-covenants/2/11/001`, `gill-body/doctrinal/2/15/001`, `gill-body/doctrinal/2/15/002`, `gill-body/doctrinal/2/15/003`, `gill-body/doctrinal/4/5/001`, `gill-body/practical/3/1/001`, `gill-body/practical/3/1/002`, `gill-body/practical/3/1/003`, `gill-body/practical/3/1/004`, `gill-body/practical/3/1/005`, `gill-body/practical/3/1/006`, `gill-body/practical/3/1/007`, `gill-body/practical/3/1/008`, `gill-body/practical/3/1/009`, `gill-body/practical/3/1/010`, `gill-body/practical/3/1/011`, `gill-body/practical/3/1/012`, `gill-body/practical/3/1/013`, `gill-body/practical/3/1/014`, `gill-body/practical/3/1/015`, `gill-body/practical/3/1/016`, `gill-body/practical/3/1/017`, `gill-divine-right/4/001`, `gill-divine-right/4/002`, `gill-divine-right/4/003`, `gill-divine-right/4/004`, `gill-divine-right/4/005`


## Page pass, part 1 (ruling on report 30, Q-A-1; LOCK_page_pass_2026-11-26 P1-P4)

- **From:** the build agent, 2026-11-26. Lock `a08a324`, committed before any page was viewed.
- **How:**
  - The build agent viewed each page itself, from the public-domain scan.
  - The BSB pages were rendered from the PDF in the private corpus into the scratchpad. The rest were viewed online at the Internet Archive.
  - No OCR, no text layer, no crop and no subagent were used.
  - Nothing is changed in `data/` or in a test.
- **The first pass above is left as it was written.** The counts below replace its columns for the 16 Arguments viewed.

### Counts after part 1

| Source | Arguments | Same cut | Would merge | Would split | Would widen | Waiting (part 2) |
|---|---|---|---|---|---|---|
| WCF (1647) | 25 | 25 | 0 | 0 | 0 | 0 |
| LBC 1689 | 14 | 14 | 0 | 0 | 0 | 0 |
| Belgic Confession (Schaff) | 1 | 1 | 0 | 0 | 0 | 0 |
| Luther, Small Catechism (Triglot) | 2 | 2 | 0 | 0 | 0 | 0 |
| Apology (Triglot) | 2 | 2 | 0 | 0 | 0 | 0 |
| Gill, *Body of Divinity* (BSB) | 26 | 7 | 0 | 2 | 0 | 17 (pp. 897-912) |
| Gill, *Divine Right* | 5 | 2 | 0 | 3 | 0 | 0 |
| Coxe, *Covenants* | 4 | 3 | 0 | 1 | 0 | 0 |
| Graves, *Old Landmarkism* | 1 | 0 | 0 | 1 | 0 | 0 |
| **Total** | **80** | **56** | **0** | **7** | **0** | **17** |

### Each Argument viewed

| Argument | Page viewed | Verdict | What the page prints |
|---|---|---|---|
| `apology-1531/ix/001` | Triglot p. 245 (English), IA `concordiatriglot00unse`, leaf n530 | same | "Matt. 28, 19" appears once in Art. IX, in one sentence ("according to Christ's command"). It is one printed unit that supports two Positions, so it makes two Arguments, one per Position. The unit allows that, as at WCF 28.4 note m. |
| `apology-1531/ix/002` | the same | same | The same unit as ix/001, on the other Position. |
| `coxe-covenants/2/10/001` | p. 36, leaf n45 | same | One marginal note: "2 Tim. 1. 9, 10. Tit. 1. 1, 2." |
| `coxe-covenants/2/10/002` | p. 37, leaf n46 | same | One inline reference closing one clause: "Prov. 8. 22,—31." |
| `coxe-covenants/2/11/001` | p. 38, leaf n47 | same | One inline reference in the serpent clause: "Gen. 3. 5." It matches `asPrinted`. Its resolution to Gen. 3:15 is not a unit question. |
| `coxe-covenants/5/8/001` | pp. 105-109, leaves n114-n118 | **would split, 6 units** | §8 prints six references across five pages, each closing its own clause. See the re-cut candidates. |
| `gill-body/doctrinal/2/15/001` | BSB p. 247 | same | One run: "Eph. i. 3, 4. 2 Tim. i. 9." |
| `gill-body/doctrinal/2/15/002` | BSB p. 247 | same | One run: "Tit. i. 2. 2 Tim. i. 1." |
| `gill-body/doctrinal/2/15/003` | BSB p. 247 | **would split, 4 units** | Four runs, each closing its own clause. See the re-cut candidates. |
| `gill-body/doctrinal/4/1/001` | BSB p. 345 | same (first pass confirmed) | One run: "the epistle to the Hebrews, chap. viii. 7, 8, 13. and ix. 1, 15. and xii. 24." |
| `gill-body/doctrinal/4/5/001` | BSB p. 361 | **would split, 2 units** | "First", head 1, prints two runs in one paragraph. "Heb. ix. 10." closes "The time of reformation". "Gal. iii. 1, 2, 3, 4. and iii. 24, 25." closes the schoolmaster clause. |
| `gill-divine-right/4/001` | p. 45, leaf n48 | **would split, 2 units** | "First" 1 prints "Acts vii. 8." (the Covenant of Circumcision given to Abraham) and "Gal. v. 2, 3, 4." (fell from Grace). Each closes its own clause. |
| `gill-divine-right/4/002` | p. 45, leaf n48 | same | One run closing one clause: "Gen. xvii. 9, 10, 11, 12, 13, 14." |
| `gill-divine-right/4/003` | p. 46, leaf n49 | **would split, 2 units** | "First" 3 prints "Gen. xvii. 14." (a covenant that might be broken) and "Ps. lxxxix. 34." (God will not break it). |
| `gill-divine-right/4/004` | p. 46, leaf n49 | **would split, 2 units** | "First" 4 prints "Gen. xvii. 6, 8." (the temporal things promised) and "ver. 5." (the change of name). |
| `gill-divine-right/4/005` | p. 47, leaf n50 | same | One reference: "Gal. iii. 16." |
| `graves-old-landmarkism/10/001` | p. 124, IA `oldlandmarkismw00gravgoog`, leaf n130 | **would split, 3 units** (Q-P-1 ruled three units, 2026-11-26; see RULING_report_31) | Three parenthesised references, each set after its own noun: "Christ's declaration (Matt. 16: 18)", "Paul's statement (Heb. 12: 28)" and "the prophecy of Daniel (2: 44)". All three are in one sentence. |

No Argument viewed would merge or widen.

### Re-cut candidates (part 1 only; not the full list)

Under Q-A-2, the full list comes after part 2, and nothing changes until it is ruled.

The new IRIs below are **proposed**:
- Each is numbered after the highest existing Argument in its division.
- Each old IRI would be deprecated with `dcterms:isReplacedBy` and never reused.
- Each new Argument keeps the old one's `gc:supports`, `gc:source` and `gc:locator`.
- The Passages already exist, because each unit cites a subset of what the old Argument cites.

| Old Argument | New (proposed) | Unit as printed | Cites | Page |
|---|---|---|---|---|
| `coxe-covenants/5/8/001` | `coxe-covenants/5/8/002` | "Gen. 17. 4, 5." | Gen.17.4-Gen.17.5 | 105 |
| | `coxe-covenants/5/8/003` | "Rom. 4. 17." | Rom.4.17 | 106 |
| | `coxe-covenants/5/8/004` | "Rom. 4." | Rom.4.1-Rom.4.25 | 106 |
| | `coxe-covenants/5/8/005` | marginal note "Read diligently Gal. 3." | Gal.3.1-Gal.3.29 | 106 |
| | `coxe-covenants/5/8/006` | "Rom. 4. 11." | Rom.4.11 | 107 |
| | `coxe-covenants/5/8/007` | "Gen. 17." | Gen.17.1-Gen.17.27 | 109 |
| `gill-body/doctrinal/2/15/003` | `gill-body/doctrinal/2/15/004` | "Psalm lxxxix. 2, 3, 28. and ciii. 17." | Ps.89.2-Ps.89.3, Ps.89.28, Ps.103.17 | 247 |
| | `gill-body/doctrinal/2/15/005` | "John xvii. 23, 24." | John.17.23-John.17.24 | 247 |
| | `gill-body/doctrinal/2/15/006` | "Eph. i. 4." | Eph.1.4 | 247 |
| | `gill-body/doctrinal/2/15/007` | "Prov. viii. 23. Mic. v. 2." | Prov.8.23, Mic.5.2 | 247 |
| `gill-body/doctrinal/4/5/001` | `gill-body/doctrinal/4/5/002` | "Heb. ix. 10." | Heb.9.10 | 361 |
| | `gill-body/doctrinal/4/5/003` | "Gal. iii. 1, 2, 3, 4. and iii. 24, 25." | Gal.3.24-Gal.3.25. The F6 candidates (Gal. 3:1-4 or Gal. 4:1-4) are carried over unresolved. | 361 |
| `gill-divine-right/4/001` | `gill-divine-right/4/006` | "Acts vii. 8." | Acts.7.8 | 45 |
| | `gill-divine-right/4/007` | "Gal. v. 2, 3, 4." | Gal.5.2-Gal.5.4 | 45 |
| `gill-divine-right/4/003` | `gill-divine-right/4/008` | "Gen. xvii. 14." | Gen.17.14 | 46 |
| | `gill-divine-right/4/009` | "Ps. lxxxix. 34." | Ps.89.34 | 46 |
| `gill-divine-right/4/004` | `gill-divine-right/4/010` | "Gen. xvii. 6, 8." | Gen.17.6, Gen.17.8 | 46 |
| | `gill-divine-right/4/011` | "ver. 5." | Gen.17.5 | 46 |
| `graves-old-landmarkism/10/001` | `graves-old-landmarkism/10/002` | "(Matt. 16: 18)" | Matt.16.18 | 124 |
| | `graves-old-landmarkism/10/003` | "(Heb. 12: 28)" | Heb.12.28 | 124 |
| | `graves-old-landmarkism/10/004` | "Daniel (2: 44)" | Dan.2.44 | 124 |

That is 7 old Arguments becoming 21 new ones. The numbers become final only in the full list after part 2. Part 2 (Gill *Body*, Practical III.1) is in a different division, so it cannot take these numbers.

**Signed:** none of the seven.
- No Argument in `data/` carries `gc:ratifiedBy`; only Holdings and Sources do.
- No `docs/handoff/SIGNED_*.md` record names any of the seven.

### Recorded, not resolved (P4)

- **A first-pass slip.** The first pass read one `gc:asPrinted` per Argument, but eleven Arguments carry more than one:
  - `gill-body/doctrinal/4/5/001` (2);
  - ten of the part-2 Arguments: Practical III.1 001-004, 006, 008, 009, 012, 015 and 017.

  So 4/5/001's second string, "Gal. iii. 1, 2, 3, 4. and iii. 24, 25.", was missed. The first-pass basis ("one inline run, or a single reference") is wrong for it, though its column ("cannot tell") stood. Every "same" verdict of the first pass rests on an Argument with one string. Part 2 reads every string.
- **p. 361, "Gal. iii. 1, 2, 3, 4."** The page prints "iii", as `asPrinted` records. The F6 question (Gal. 3:1-4 or 4:1-4) is not a unit question and is left as it is.
- **p. 247, an aside.** The right column prints "Heb. viii. 7, 8, 13. and ix. 15. and xii. 24.", which no Argument cites. It is outside this audit's scope.
- **The Apology Arguments carry no page.** The page is Triglot p. 245 (English). Adding `gc:pages "245"` would be a data change, so it is only noted here.
- **Coxe "Rom. 4." (p. 106)** is introduced as "the former part of that forementioned Rom. 4.", while the data cites the whole chapter. That is a resolution question, not a unit question, and is left as it is.

### Waiting for part 2 (17)

Gill *Body*, Practical III.1, `gill-body/practical/3/1/001` to `017`, pp. 897-912. They are not viewed until Chris has signed the italic-spans sitting `9b19159be3098c64`.
