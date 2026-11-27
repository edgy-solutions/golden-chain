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
