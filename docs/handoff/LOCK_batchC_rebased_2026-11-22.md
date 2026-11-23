# Lock: Batch C (instrumentality) on F-B = (b), variant N, rebased to today's base (overnight order 2026-11-22, item 4)

- **From:** the build agent, 2026-11-22. Committed before any Batch C data.
- **On:** the held lock `~/.golden-chain/step3-batchC-predictions-locked.txt` (C1–C6, not edited); [RULING_report_15.md](RULING_report_15.md) Q-C1 (variant N) and Q-C2; [RULING_report_26.md](RULING_report_26.md) ("F-B is answered (b). Proceed with Batch C"); the overnight order, item 4 ("Mint (b)'s label only as 'proposed, wording pending'").
- **Why rebased:** the held lock's base was the tree after `37724cf`. Since then the data gained 8 plumb-line Holdings, 3 tiers, 3 flags and 20 axioms. The held lock's *deltas* are kept; only the base counts move. A delta that differs from the held lock's is a miss against the held lock.
- **Base:** `phase-0` after the frozen-fixture commit. PREDICTED there: Locus 12, Position 24, Argument 80, Passage 142, Body 8, Holding 62, excludes 9, entails 1, holds 62, answers 24, supports 80, childOf 1, effectivelyHolds 63, warnings 0, Axiom 38.

## What is minted

- **Locus** `<locus/baptism-instrumentality>`, label "Instrumentality of baptism", notation "33e", question "How does baptism benefit the one baptized?" (the dispatch of 2026-11-08 §8, word for word). Under `heading/worship`. No tier in data: the tier is set by a sitting.
- **Position (a)** `<position/baptism-instrumentality/instrumental>`, label "The Spirit works through the rite to confirm faith." (dispatch §8 (a), word for word). Status proposed.
- **Position (b)** `<position/baptism-instrumentality/representational>`, status proposed. **Label:** "Wording pending. F-B answered (b): the rite sets Christ before faith; the Spirit works by the Word." The second sentence is the option Chris signed on console eb961ddb, word for word. Chris's note on that row ("quote gill exactly rather than paraphrase") governs the final wording, which goes to sitting 2 with Gill's words.
- **Excludes** (a)–(b), one triple, with the plan's note as a TTL comment ("(a) as Reformed theology holds it includes representation"). Nothing is derived from it (M3 still open).
- **Arguments, variant N:**
  - Harbaugh, one per printed proof answer: Q.65 ×4, Q.69 ×4, Q.70 ×3, Q.71 ×4, Q.72 ×5, Q.73 ×5 = 25, all supporting (a).
  - Belgic, one per note: XXXIII p. 424 fn2, fn3; XXXIV p. 426 fn1–fn5; p. 427 fn2 = 8, all supporting (a). p. 426 fn1 carries "Apoc. i. 6" as `gc:asPrinted`, resolved to Rev 1:5 with a resolution note, status proposed.
  - Gill, Practical III.1 "Sixthly", p. 914, 4, supporting (b): Rom 6:4–5 and Col 2:12 (head 1), Acts 22:16 (head 3), 1 Pet 3:21 (head 4). This is the plan's rule for (b), as the held lock counts it.
- **Sources:** `source/heidelberg-harbaugh` (SourceWork) and 6 SourceDivisions (Q.65, 69–73); `source/belgic-confession/33` (new). Gill's `source/gill-body/practical/3/1` exists and is reused.
- **Every reference is re-read on the page images before it is minted** (Harbaugh `heidelbergcatech00harb`, leaf = p + 3; Schaff `creedsofchristen187803scha`, leaf = p + 15; BSB Gill PDF p. 967). A reference that differs from [heidelberg-belgic.md](../sources/heidelberg-belgic.md) is a recorded miss, and the image governs.

## Predictions

| # | Prediction |
|---|---|
| B1 | Locus 12 → 13. warnings 0 → 1 (the new Locus has no tier). |
| B2 | Position 24 → 26, answers 24 → 26, excludes 9 → 10. |
| B3 | Argument and supports 80 → 117 (25 + 8 + 4). |
| B4 | Passage 142 → 161. The 19 new: 1Cor.3.5, 1Cor.3.7, 1Cor.6.11, 1John.1.7, 1John.5.6, 2Cor.4.13, Acts.8.36-Acts.8.38, Col.2.11, Eph.4.22-Eph.4.24, Eph.5.26, Ezek.16.4, Gen.17.11, Gen.9.13, Heb.9.14, Isa.4.4, John.19.34, Rev.1.5, Rom.10.17, Rom.6.3. Gill adds none (Rom.6.4-Rom.6.5, Col.2.12, Acts.22.16, 1Pet.3.21 exist). |
| B5 | Unchanged: Body 8, Holding 62, holds 62, effectivelyHolds 63, entails 1, childOf 1, Axiom 38. |
| B6 | Weigh, both scopes, byte-identical to the base (members `46381316eb30`, officers `91bfab215992`): the plumb-line holds nothing on the new Locus, so it is not a stance Locus. |
| B7 | Real ingest: 0 violations, 1 warning (the tier). SHACL conforms. |
| B8 | Full suite: the frozen-fixture count plus the born tests, 0 failures, no existing test amended. If an existing test fails, it is reported before it is amended (ruling on report 27), and the mint moves to a `hold/` branch. |
| B9 | Misprints: exactly 1 (Schaff p. 426 "Apoc. i. 6"). |

## Recorded before minting (for the architect)

- **Gill's other references in "Sixthly".** Head 2 prints Mark 1:4 and Acts 2:38 ("for the remission of sins"); head 6 prints 1 John 5:3 and John 14:15, 21, 23. The plan takes 4 for (b) and none of these. Head 2's two bear on (b) as directly as head 3's. Not minted; a question.
- **Gill head 1 is one note with two references.** Ruling 16 ("an Argument cites one note of one division") would make it one Argument, giving 3 for Gill and 116 in all. The held lock counts 4 under both variants, and Q-C1 names 117. I mint 117 as ruled, and record the difference.
- **(b)'s label** as above is my reading of "proposed, wording pending". The final wording is Chris's, on sitting 2.
- **(a)'s label** is the dispatch's wording. It has not been on a console.
