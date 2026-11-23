# Lock: ingest of the signed follow-up console eb961ddb1e582ed6

- **By:** the build agent, 2026-11-22. Committed before the ingest is run (rule 6). Git history seals it.
- **On:** [RULING_report_26.md](RULING_report_26.md): message 1 and ruling 1 ("Ingest the export whose file name ends "(1).json"").
- **Export:** `verdicts_plumb-line-followup_eb961ddb1e582ed6(1).json`, signed "Chris Nogradi", 2026-11-22. It is complete, with 25 rows. The export without "(1)" is superseded and is not ingested.
- **Command:** `tools/console/ingest.py "<(1).json>" <manifest> --code-at 9836117 --write`. The `--code-at` is required by REPORT_phase1_19 PW5.
- **Predicted from:** `tools/console/plumb_merge.apply` and `render`, the spec's field ids, the current `data/plumb-line.ttl` (1 record, 13 Holdings), and the current validation (3 warnings: no tier on covenant-of-grace, circumcision-covenant, baptism-validity).

## Predictions

| # | Prediction |
|---|---|
| E1 | The console ingest passes its checks and writes record `docs/sittings/plumb-line/0002_signed_plumb-line-followup_eb961ddb1e582ed6.json`. It also replaces `data/plumb-line.ttl` with the replay of records 0001 and 0002. |
| E2 | **Tier and clarity**, 3 loci, all new: covenant-of-grace second / contested; circumcision-covenant second / settled; baptism-validity second / settled. |
| E3 | **8 new plumb-line Holdings**, all ratified with source `source/plumb-line/sitting-eb961ddb1e582ed6` and date 2026-11-22. They are: covenant-of-grace/eternal-with-christ taught; covenant-of-grace/established-in-new-covenant tolerated; circumcision-covenant/administration-of-grace forbidden; circumcision-covenant/not-an-administration-of-grace required; baptism-repetition/infant-sprinkling-not-baptism required; baptism-validity/subject-mode-formula forbidden; baptism-validity/church-of-gospel-order required; baptism-validity/church-of-our-order forbidden. The 13 Holdings from sitting 1 are unchanged. Plumb-line Holdings go from 13 to 21. |
| E4 | **3 unchurches flags**, the first in data: circumcision-covenant/administration-of-grace (ticked on its row) and baptism-subjects/believers-and-their-infants and baptism-subjects/infants (confirmed; both are held forbidden). The confirmation for baptism-formula/non-triune is **not written**: no such Position is minted ("when minted", as its label says). It is noted in the ttl as "unchurches confirmed on a Position the plumb-line does not hold". |
| E5 | **Notes in the ttl comment for sitting 0002:** "modality left empty, unanswered": covenant-of-grace.made-in-time-after-fall. "Not data, in the signed record only", 10 rows: fa-wording, ii-iii, validity-3-statement, validity-3-administrator, validity-3-testimony, fb-reading, fb-b-wording, lbc-7-3.argument-001/002/003. There are no "other" notes on a tier, clarity or modality field. |
| E6 | **Real ingest:** 0 violations and **0 warnings** (from 3). Every locus now has a tier. |
| E7 | **Counts** (tests/predictions.py, updated in this commit): Holding 54 to 62; holds 54 to 62; effectivelyHolds 55 to 63 (plumb-line has no parent); Axiom 29 to 38 (+3 tier, +3 clarity, +3 unchurches); warnings 3 to 0. Every other count is unchanged: Locus 12, Position 24, Argument 80, Passage 142, Body 8, excludes 9, entails 1, answers 24, supports 80, childOf 1. |
| E8 | **No plumb-line inconsistency.** eternal-with-christ (taught) excludes established-in-new-covenant (tolerated), and excludes fires only on required/taught pairs. administration-of-grace entails believers-and-their-infants, but the plumb-line holds administration-of-grace forbidden, and entails fires only when P is required or taught. |
| E9 | **Weigh changes in both scopes** (hashes no longer 71c14a5d187d / c8fe9e910b5a). It changes in four ways. WCF gains a wall on circumcision-covenant: administration-of-grace taught against plumb-line forbidden. Gill gains the loci of eternal-with-christ, not-an-administration-of-grace and infant-sprinkling-not-baptism. LBC gains the locus of established-in-new-covenant. The new hashes are measured, not predicted. |
| E10 | **Suite: 813 passed**, with one test amended in this commit. `test_regenerated_graph_is_the_old_graph_plus_axioms` pinned the whole file to sitting 1: it checked the old graph plus exactly 17 axioms. It now checks the same thing on the replay of record 0001 alone, which is what it was written to check (the regeneration of sitting 1). Without that amendment it would be the one failure. |

## Not in this ingest

- **No Holding on (iii)**, made-in-time-after-fall. It was left empty on purpose, pending its rewording in sitting 2.
- **The LBC Holding on (iii) from 7.2** waits for sitting 2, when the (ii)–(iii) `excludes` edge is retired (report 26).
- **The three LBC 7.3 margin confirmations** are recorded in the signed record only. This console showed no LBC image. The LBC 1677 console's answer governs (message 1).
- **The testimony row's console defect** is recorded in an audit beside the signed record. The signed answer stands (ruling 1).
