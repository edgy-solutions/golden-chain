# Report 27: eb961ddb ingested; ruling 2 applied; the 1875 Gadsby printing seen

- **From:** the build agent, 2026-11-22.
- **On:** [RULING_report_26.md](RULING_report_26.md) (both messages, filed verbatim).
- **In short:**
  - **Follow-up console `eb961ddb` ingested**, from the "(1).json" export only. The lock was committed first ([LOCK_ingest_eb961ddb_2026-11-22.md](LOCK_ingest_eb961ddb_2026-11-22.md)). E1–E8 held. **E9 and E10 missed:** weigh changed more than predicted, and 8 more tests were pinned to the data before the sitting (see below).
  - **The three unchurches flags now take WCF, the Apology and Augsburg out of the ranking.** Weigh lists them as "Not a church by this plumb-line's standard". This is the first time the real data has done so.
  - **Two defects found in what weigh prints about an exclusion.** It names the wrong sitting as a flag's source. When a Holding has two sources it picks one at random, so the weigh output and its hash change from run to run. Fixes are proposed below; they are not built.
  - **Ruling 2 applied:** propositions 1 and 7 are the source for (3), and proposition 3 is quoted only for the recursion. Recorded against the architect.
  - **The testimony row's defect** is recorded in an audit beside the signed record. The signed answer stands.
  - **1875 Gadsby printing:** Chris placed the PDF; I viewed it and propose it as the witness for Articles 1–31.

## The ingest, scored

| # | Locked | Result |
|---|---|---|
| E1 | Record 0002 written; `data/plumb-line.ttl` is the replay of 0001 and 0002 | **Held.** |
| E2 | Tier and clarity on 3 loci: covenant-of-grace second / contested; circumcision-covenant and baptism-validity second / settled | **Held.** |
| E3 | 8 new plumb-line Holdings; 13 → 21 | **Held.** |
| E4 | 3 flags written; non-triune not written (no such Position yet) | **Held.** |
| E5 | Notes: 1 unanswered (made-in-time-after-fall), 10 not-data rows, no "other" | **Held.** |
| E6 | Real ingest 0 violations, 0 warnings (from 3) | **Held.** |
| E7 | Holding / holds 62, effectivelyHolds 63, Axiom 38, warnings 0; all else unchanged | **Held** (`test_counts_match_predictions` passed). |
| E8 | No plumb-line inconsistency | **Held.** |
| E9 | Weigh changes in both scopes; WCF **gains a wall** on circumcision-covenant | **Missed.** See below. |
| E10 | Suite 813 passed, with one test amended in the lock commit | **Missed.** 8 failed, 805 passed. After the amendments below: **814 passed** (813 + 1 born). |

**E9, what happened.** Both hashes changed, as predicted (from `71c14a5d187d` / `c8fe9e910b5a`). They are not stable: see the second defect below. Two runs gave members `13209f4b689f` and `72a2d3c329e7`; officers gave `590965a0a299` both times. The miss is in what changed:

> **Note, 2026-11-22 (ruling on report 27): not verifiable as stated.** The officers hash also varies with the process's hash seed: seeds 0 and 3 give `590965a0a299`, seeds 1 and 2 give `7dcf90eb14d4` ([LOCK_weigh_sources_sorted_2026-11-22.md](LOCK_weigh_sources_sorted_2026-11-22.md)). My two runs happened to agree. After weigh fix 2 (`395f3ef`) the hashes are stable: members `46381316eb30`, officers `91bfab215992`. The text above is not rewritten.
- I predicted a new **wall** for WCF. Instead, three Bodies are **not ranked**, and weigh lists them as "Not a church by this plumb-line's standard":
  - **WCF:** believers-and-their-infants required (28.4), and administration-of-grace taught (7.5).
  - **The Apology and Augsburg:** infants taught (IX).
- The cause is the flags. Before this sitting no Position carried an unchurches flag, so weigh had no exclusion to apply (ADR-0003 R2.3). Sitting 2 confirmed the two baptism-subjects flags and ticked the circumcision-covenant one, so weigh now excludes every Body that holds a flagged Position as required or taught. I read the merge code for the lock, but did not trace the flags through weigh. That is why the lock missed this.
- **Gill:** cost 0 over 9 loci (was 6); coverage 0.90.
- **LBC:** cost 0 over 6 loci (was 5); coverage 0.60. Its taught "established-in-new-covenant", against the plumb-line's tolerated, costs nothing.
- **Small Catechism** is unchanged apart from coverage (0.10).

**Defect found: the flag's sitting is misreported.**
- `goldenchain/unchurches.flag_source` returns the source of the plumb-line's **Holding**, not of the flag. So weigh says the two baptism-subjects flags were set by "sitting-7b23646b2c763ae0". The flag axioms in `data/plumb-line.ttl` say they were set by `sitting-eb961ddb1e582ed6`, which is right: sitting 1 made the Holdings, and sitting 2 confirmed the flags.
- **Proposed fix (not built):** `flag_source` reads the `dcterms:source` of the provenance axiom on that Position's `gc:unchurches`, and falls back to the Holding's source only when there is no axiom. A test is born with it: on the real data, the baptism-subjects flags report eb961ddb. Only weigh's wording changes; the ranking and exclusions do not. **Needs your go-ahead** (rule 5).

**Second defect: weigh's output changes from run to run.**
- WCF's Holding on administration-of-grace cites two sources, `source/wcf/7/5` and `source/wcf/28/4`. `goldenchain/unchurches.excluded` takes one with `g.value(h, DCTERMS.source)`, and which one it gets varies between runs. So the exclusion line cites 7.5 in one run and 28.4 in the next, and the weigh hash changes with it.
- This was latent: before this sitting no Body was excluded, so the line was never printed.
- **Proposed fix (not built):** list every source of the Holding, sorted, in the row and in the printed line. A test is born with it: weigh renders byte-identically in two runs on the real data, and the WCF line names both 7.5 and 28.4.
- **Until it is fixed,** the weigh hash check is not a byte-identity check on the real data. The ranked Bodies' lines are stable.

**E10, what happened.** The lock found the one test pinned to the plumb-line file. It missed 8 tests in four files that were pinned to the data **before** this sitting: no tier on the new loci, no plumb-line Holding there, and no flag in the real data. All 8 failed. Each is amended to check what it was written to check, on the data it was written for:

| Test | Was | Now |
|---|---|---|
| `test_step3_batch_a::test_new_loci_have_no_tier` (×2) | no tier on covenant-of-grace or circumcision-covenant, anywhere | no tier in the source files; the plumb-line supplies it |
| `test_step3_batch_a::test_only_gill_holds_circumcision_no` | Gill is the only Holding on not-an-administration-of-grace | the same, in the source files (the plumb-line now holds it, required) |
| `test_step3_batch_b::test_locus_33d_has_no_tier` | no tier on baptism-validity | no tier in the source files |
| `test_step3_batch_b::test_no_lbc_holding_on_validity_positions` | no Holding at all on the three validity Positions | none in the source files (the plumb-line now holds all three) |
| `test_unchurches::test_real_data_no_flags_empty` | real data excludes no one | the same, with the plumb-line's flags stripped first |
| `test_unchurches::test_real_data_with_flags` | the two baptism-subjects flags exclude WCF, Augsburg and the Apology, one row each | the same, after stripping the committed flags (otherwise WCF also has the circumcision row) |
| `test_weigh::test_real_data_smoke` | real data excludes no one, then the flags are added | the same, with the flags stripped first |

- "Source files" means `data/*.ttl` without `data/plumb-line.ttl`. The flags are stripped by a new helper, `gcfix.strip_flags`, which removes the `gc:unchurches` triples and their provenance axioms.
- **Born:** `test_unchurches::test_real_data_as_committed_sitting_eb961ddb` checks the exclusions in the committed data. WCF has two rows, believers-and-their-infants (required) and administration-of-grace (taught). Augsburg and the Apology have one each (infants, taught).
- `test_real_data_with_flags` had already expected these three Bodies to be excluded by the two baptism-subjects flags. My lock should have found it.
- **Disclosed:** I amended these tests myself after the run, and did not stop first. Each amendment keeps the test's own check and only narrows the data to what the test was written for. If you want any of them done otherwise, I will redo it.

## Ruling 1: the audit beside the signed record

[AUDIT_plumb_line_followup_eb961ddb1e582ed6.md](AUDIT_plumb_line_followup_eb961ddb1e582ed6.md):
- **D-1.** Row `validity-3-testimony`. As built, the row said "not public domain" and offered the mixed string as "Your words as recorded". Chris's testimony is his "other, as written" text, and only that. The signed answer stands.
- **D-2.** The three LBC 7.3 margin confirmations were made with no LBC image on this console. They are in the signed record only. The LBC 1677 console's answer governs.

## Ruling 2: propositions 1 and 7

- [lee-bsb.md](../sources/lee-bsb.md) item 5 now quotes proposition 1 (p. vii) and proposition 7 (p. viii) for validity (3). Proposition 3 is kept there, marked "for the recursion only".
- Proposition 3 is quoted in [PROPOSAL_validity_bsb_foreword.md](PROPOSAL_validity_bsb_foreword.md), "Corrections recorded", where the recursion and the church-Locus dependency are recorded.
- [REPORT_phase1_25.md](REPORT_phase1_25.md) carries a correction note after its "for comparison" block. The comparison with Gill rests on proposition 7 and stands.
- The foreword ruling's Applied gains a "Corrected by the ruling on report 26" section. The source division's label stays "propositions 1 and 7", which answers report 26's A-1. Data is unchanged.
- Report 26's C-1 (rebuild eb961ddb?) is moot: it was signed and is not rebuilt.

## The 1875 Gadsby printing (A-4)

Written up in [gospel-standard.md](../sources/phase2/gospel-standard.md), "The 1875 Gadsby printing, seen".
- **The title page** reads: *Form of Trust Deed and Articles of Faith for Strict Baptist Churches. Revised.* London: J. Gadsby, "Gospel Standard" Office, 1875.
- **Articles I–XXXI** run from p. 8 to p. 15, and XXXI is the last article. Printed page = PDF page − 3.
- **Proposed witness:** "1875 Gadsby printing: witness for Articles 1–31 only; does not witness Articles 32–35 (1878–79)."
- It goes to Chris on a console (the title page and the I–XXXI span) before anything enters data.

## Next

- **Sitting 2**, built from the rows already ruled:
  - 23a under proposal B, with (iii) reworded;
  - the entails row, with the LBC 7.2 Holding shown;
  - validity (2) relabelled, so the three "suffice, with no condition on the administering church";
  - the administrator question, with Gill's words;
  - (b) worded from Gill, heads 2–4 and "Sixthly".
- Then Batch C on F-B = (b).
- **On the LBC 1677 console,** the question whether Chris checked the three LBC 7.3 margin confirmations against the facsimile.

## Questions

**For the architect:**
- **A-1.** The two weigh fixes as proposed (`flag_source` from the flag's axiom; every source of a Holding, sorted): go?
- **A-1a.** The 8 test amendments after the run: accept, or redo?
- **A-2.** The exclusions of WCF, the Apology and Augsburg follow from flags Chris signed. Do you want them noted anywhere beyond this report and the weigh output?
- **A-3.** The 1875 witness label as proposed: ratify, for the console?

**For Chris:**
- **C-1.** Sign the LBC 1677 console `0a73bb5afa616446` when ready. It is already built, so the question on the 7.3 margins goes on its follow-up console.
