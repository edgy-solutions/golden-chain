# Lock: the sitting 2 console (overnight order 2026-11-22, item 5)

- **From:** the build agent, 2026-11-22. Committed before the builder change and the content file.
- **On:** [RULING_report_26.md](RULING_report_26.md) message 1 (notes for sitting 2) and message 2, ruling 5 (the rows already ruled); [REPORT_phase1_23.md](REPORT_phase1_23.md) (23a, proposal B, rows 1-6); [REPORT_phase1_25.md](REPORT_phase1_25.md) (Gill on the administrator, rows V1-V4); [REPORT_phase1_26.md](REPORT_phase1_26.md) (the entails row and the LBC 7.2 Holding); the overnight order, item 5.
- **Base:** `phase-0` at `e663931`. Suite 820 passed.

## What is built

- **Content:** `docs/loci/plumb-line-followup-2.json`, format `golden-chain-followup-content/1`, read by the existing builder `tools/console/specs/plumb_line_followup.py`. Three sections:
  - **23a covenant-of-grace**, 10 rows: proposal B (radio); (ii)'s wording from Owen (proposal), with Owen's three full sentences from vol. 19 p. 78 beside it; stance on (ii) (position row); (iii)'s wording from WCF 7.3 (proposal); stance on (iii) (position row); the (ii)-(iii) mark, retire or keep (radio); (ii) entails (iii)? (radio) with the LBC 7.2 Holding shown; the LBC 7.2 Holding (proposal); Coxe holds (i), (ii) or neither (radio); LBC 1677 holds (i), (ii) or neither (radio).
  - **33d baptism-validity**, 9 rows: (2)'s wording, "These three suffice, with no condition on the administering church" (proposal); stance on (2) (position row); V1 Gill's view, with his words (radio); V2 stance on (B) or (C) and its unchurches (two radios, optional); V3 (radio); V4 three edges (radios, optional).
  - **33e instrumentality (not in data)**, 7 rows: (b)'s wording (text), with Gill's head and heads 1-4 of "Sixthly" word for word; tier, clarity (radios); stance and unchurches on (a) and on (b) (four radios, optional).
- **Images (6):** Owen vol. 19 p. 78; WCF 1647 pages 13-14; Gill, Divine Right 1749 p. 14 (all Internet Archive, public domain, viewed by the build agent to propose); the two BSB p. 914 crops already used on sitting 1. No crop is viewed by any model after the build.
- **Builder change:** a `position` row may carry its own `label`. The row shows that label, and its first context line is `The wording in the data now: "<label in data/loci.ttl>".` The build fails on an empty override, or one equal to the label in the data. Rows without an override are built exactly as before.

## Why stances are asked two ways

- **(ii), (iii) and (2)** exist in the data. Their stance rows are `position` rows, so the merge writes Chris's answer to the plumb-line on ingest, keyed by the Position's IRI. The row shows the proposed wording, because the wording in the data is what misled the signer on (2). The stance is on the wording Chris confirms or writes on the same page.
- **(a), (b), Gill's (B)/(C), and the 33e tier and clarity** are not in the data. Their rows are single-field rows, which the merge records as "not data, in the signed record only" (`plumb_merge.apply`, `fids == ["v"]`). How those answers enter `data/plumb-line.ttl` once the Positions are minted is a question for the architect (Q-S2-1 below).

## Predictions

| # | Prediction |
|---|---|
| S1 | The builder change passes all existing tests unamended. Born tests: an override is shown with the data-wording line first; an empty override fails; an override equal to the data label fails; the real sitting-2 content builds (S2). |
| S2 | The real content gives 3 sections, rows `[10, 9, 7]` = 26, fields 29 (3 position rows × 2 + 23 single-field rows), 6 images, 0 locus rows, 0 flag rows. All 3 position rows carry an override. |
| S3 | Merge classification, tested on a signed record made from the spec with every row answered: 23 rows go to "not data"; the 3 position rows write plumb-line Holdings for `covenant-of-grace/established-in-new-covenant`, `covenant-of-grace/made-in-time-after-fall`, `baptism-validity/subject-mode-formula`. |
| S4 | The sitting-1 spec is unchanged: digest of `make_spec(plumb-line-followup-1.json)` without paths and sources stays `ea6d4978e8ed2884`. |
| S5 | `build.py` builds the page under `~/.golden-chain/console/plumb-line-followup/`; build16 recorded in the report. |
| S6 | No `data/*.ttl` change: PREDICTED counts unchanged, ingest 0/0, weigh members `46381316eb30`, officers `91bfab215992`. |
| S7 | Full suite: 820 + born, 0 failures, no existing test amended. A failing existing test is reported before anything is amended. |

## Recorded before building (for the architect)

- **Q-S2-1.** Answers on Positions not yet in the data (33e (a), (b), tier, clarity; Gill's (B) or (C)) are kept in the signed record only. Proposed: when each is minted, its Holding is written from the signed record under that minting's lock, citing this sitting's source, with no further sitting. The alternative is a short sitting 3 to re-ask them.
- **Order on ingest.** If Chris holds (ii) and (iii) both taught or required, the ingest must retire the (ii)-(iii) mark in the same change as the merge. Otherwise the plumb-line is inconsistent in the derived graph. The ingest lock for this sitting will state that order.
- **Batch C is stopped (rule 8).** The 33e rows ask for the wording and the stances now, so the sitting is not held up by it. Nothing in 33e is minted by this console.
