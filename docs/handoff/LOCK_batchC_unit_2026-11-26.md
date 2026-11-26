# Lock: Batch C re-locked on the quotation unit (ruling on report 28, item 7)

- **From:** the build agent, 2026-11-26. Committed before the mint, together with the ADR-0005 amendment.
- **On:** [RULING_report_28.md](RULING_report_28.md) item 7. It supersedes the predictions of [LOCK_batchC_rebased_2026-11-22.md](LOCK_batchC_rebased_2026-11-22.md) (B1-B9, `f13ff64`), which stopped under rule 8 with nothing minted. That lock is not edited. Everything it says that is not changed here stands: the Locus, the two Positions' IRIs, the excludes, the sources, and re-reading each reference on the page images.
- **Base:** `phase-0` after the R3 merge (`59e156e`). PREDICTED there: Locus 12, Position 24, Argument 80, Passage 142, Body 8, Holding 62, excludes 9, entails 1, holds 62, answers 24, supports 80, childOf 1, effectivelyHolds 63, warnings 0, Axiom 38. Weigh: members `b5ad57ea0df3`, officers `6a2ffd426bf9`.

## The unit (ADR-0005, as amended in this commit)

One Argument per quotation unit as the source prints it. Several references printed under one unit stay one Argument, with one `gc:cites` per reference.

- **Harbaugh:** a quoted verse with the reference(s) printed after it is one unit. A further quotation brought in by "Again:" is its own unit. That gives 23:
  - Q.65 ×4;
  - Q.69 ×3 ("Matt. xxviii. 19; Mark xvi. 15, 16." is one unit);
  - Q.70 ×2 ("Eph. iv. 22-24; Rom. vi. 4." is one unit);
  - Q.71 ×4;
  - Q.72 ×5;
  - Q.73 ×5.
- **Belgic (Schaff):** one footnote is one unit, giving 8. This is unchanged.
- **Gill, Practical III.1 "Sixthly", p. 914:** a head's run of inline references closing one clause is one unit. Each head is its own Argument, as the data already has it for `baptism-efficacy/sign-only` (Arguments 018-021).

## Gill's heads 2 and 6 (ruling: "take a reference only where the clause it stands on is about how baptism benefits; list the rest as 'not taken' with the clause")

I read these from the BSB page images (PDF pp. 967-968; PD text, quoted in docs only).

| Head | References as printed | The clause they stand on | Proposed |
|---|---|---|---|
| 2 (p. 914) | "Mark i. 4. Acts ii. 38." (one unit) | "It was practised both by John and by the apostles of Christ, for the remission of sins ... not that that is the procuring and meritorious cause of it, which only is the blood of Christ; but they who submit unto it, may, by means of it, be led, directed, and encouraged to expect it from Christ." | **Taken** for (b). The clause says what the rite is for and how it serves that end: by means of it, the baptized are directed to expect remission from Christ. |
| 6 (p. 915) | "1 John v. 3." | "Yielding obedience to this ordinance of Christ, is an evidence of love to God and Christ" | **Not taken.** The clause is about what obedience shows, not how baptism benefits. |
| 6 (p. 915) | "John xiv. 15, 21, 23." (one unit) | "and such who from a principle of love to Christ, keep his commandments, may expect according to his promise, to have fresh manifestations of his and his Father's love, and to have communion with Father, Son, and Spirit" | **Not taken.** The clause speaks of a benefit, but to those who "keep his commandments" in general, not of this ordinance. This is the closest call; see Q-C-1. |

Head 5 prints no reference of its own ("In the same passage", that is, 1 Pet 3:21 under head 4).

So Gill supports (b) with 4 Arguments: heads 1, 2, 3 and 4.

## Labels

- **(a)** `position/baptism-instrumentality/instrumental`: **"The Holy Ghost confirms faith by the use of the sacraments."**
  - This is Heidelberg Q.65's answer in its own words, as Harbaugh prints it on p. 107 (leaf n110, read from the image): "From the Holy Ghost, who works faith in our hearts by the preaching of the Gospel, and confirms it by the use of the sacraments."
  - "it" becomes "faith". Nothing else is changed. Status proposed.
  - It replaces the dispatch's wording ("The Spirit works through the rite to confirm faith."), which has not been on a console.
- **(b)** `position/baptism-instrumentality/representational`: unchanged from the 2026-11-22 lock. Its label reads "Wording pending. F-B answered (b): the rite sets Christ before faith; the Spirit works by the Word." Status proposed, until Chris answers on sitting 2.

## Predictions

| # | Prediction |
|---|---|
| U1 | Locus 12 → 13. warnings 0 → 1 (the new Locus has no tier). |
| U2 | Position 24 → 26, answers 24 → 26, excludes 9 → 10. |
| U3 | Argument and supports 80 → 115: Harbaugh 23 and Belgic 8 support (a); Gill 4 (heads 1-4) support (b). |
| U4 | Passage 142 → 161: the same 19 new Passages as B4. Gill adds none: Mark.1.4 and Acts.2.38 already exist, like Rom.6.4-Rom.6.5, Col.2.12, Acts.22.16 and 1Pet.3.21. |
| U5 | Unchanged: Body 8, Holding 62, holds 62, effectivelyHolds 63, entails 1, childOf 1, Axiom 38. |
| U6 | Weigh, both scopes, is byte-identical to the base (members `b5ad57ea0df3`, officers `6a2ffd426bf9`). `data/plumb-line.ttl` is unchanged (`bfb0238c…`). |
| U7 | Real ingest: 0 violations and 1 warning (the tier). SHACL conforms. |
| U8 | Full suite: 875, plus the italic-console and replay tests if they land first, plus the born tests, with 0 failures and no existing test amended. If an existing test fails, it is reported before it is amended, and the mint moves to a `hold/` branch (ruling on report 28, item 6). |
| U9 | Misprints: exactly 1 (Schaff p. 426 "Apoc. i. 6" → Rev 1:5, with `gc:asPrinted` and a resolution note). |
| U10 | Four Arguments carry several references, each as its own `gc:cites`: Q.69 (2), Q.70 (2), Gill head 1 (2) and Gill head 2 (2). `gc:asPrinted` follows the 2026-11-22 lock. Gill's four (b) Arguments carry the same strings as Arguments 018-021 on the same heads. Harbaugh and Belgic carry it only on the misprint (U9), so no new transcription enters the data. |

A miss is recorded, not edited.

## Recorded for the architect

- **Q-C-1.** Gill head 6, John 14:15, 21, 23, is proposed "not taken", because its clause is about keeping his commandments in general. If the architect reads the clause as about how this ordinance benefits, it becomes one more (b) Argument (U3 116) and three new Passages (U4 164), under a new lock.
- **Q-C-2.** The amended unit is applied to this mint. Existing Arguments are not re-cut by this change. I have not checked whether any existing Argument departs from the unit. If the architect wants that checked, it is a separate locked change.
- **Q-H-1 (from LOCK_replay_held).** Sitting 2 is not signed, so this mint writes no binding. The sitting-2 ingest writes the instrumentality bindings when it comes.
