# Report 21: the ruling on report 20, worked

- **From:** the build agent, 2026-11-22.
- **On:** [RULING_report_20.md](RULING_report_20.md) (filed verbatim, `1a7d746`).
- **In short:**
  - A-12 and A-8 are done (`5285db3`).
  - A-11: both locks were written before any code, then built (`56004c5`) and run twice on a clean tree.
    - **The v5 draw stopped at the ceiling.** Slanted had 9 of 80 first choices fail, over the limit of 8. So nothing was replaced, cropped or built. The figures are below.
    - **The tall-box measure does not support the merged-lines reading.** None of the 10 cases shows two bands.
  - A-9: ADR-0007's Verification was locked first (`610471e`) and then built (`07682a5`). AV1 to AV8 all held, on synthetic fixtures. One gap in the lock's form is raised as question C7-L6.
  - A-10, A-5 and BH1 are recorded.
  - C-1: Chris signed the p. 914 re-ask **yes** (column footnotes). His note says the measured boundary starts one line low.
  - **One thing to know:** the auto-mode permission check refused a local lock file for ADR-0007. The lock lives in the committed ADR instead. See "Noted".

## A-12. The build hash is what is signed, `5285db3`

- ADR-0006 R5 gains item 9.
- The test `test_r5_pages_of_two_runs_differ_only_in_the_run_header_time` builds twice with two run times. It checks four things:
  - the build hashes are equal;
  - each page holds its own time exactly once and never the other run's;
  - with the time replaced by a placeholder, the two pages are byte-identical;
  - so the diff outside that field is empty.

## A-8. ADR-0006 Revision 6, `5285db3`

R6 is marked "ratified provisionally on report 20 (ruling on report 20, A-8). The architect will read the text."

## A-11. Truth-set v5 and the tall-box measure

### The locks, before code

Both locks were made read-only on 2026-11-22 at `5285db3`, before any v5 or tall-box code existed. The code is `56004c5`, with 41 born tests (suite: 740 passed).

- **`~/.golden-chain/italic-v5-predictions-locked.txt`** locks:
  - **The replacement rule (condition 1):** first the next untaken word of the same page and stratum, in order-key order. If the page is exhausted, the round-robin over pages in ascending order from the lowest.
  - **The drops listing (condition 2).**
  - **The ceiling (condition 3):** the draw stops before any replacement if 10 · replaced > first choices in any stratum.
  - Predictions V1 to V9.
- **`~/.golden-chain/tallbox-bands-predictions-locked.txt`** locks:
  - **Rule T:** gap rows are those at or under 5 % of the row maximum. T looks for a run of 3 or more of them touching neither end, with at least 20 % of the ink on each side and each band at least 15 px tall.
  - The selection and the control.
  - Predictions TB1 to TB4.

### The v5 draw: the ceiling tripped

The draw used SALT `truthset-v5/` on the 20 pages 896 to 915, with every v2, v3 and v4 key excluded. Runs a and b gave byte-identical `candidates.json` and `drops.json`, with clean_run true in both. The two run headers differ only in their time.

| stratum | first choices | failing | share | ceiling |
|---|---|---|---|---|
| slanted | 80 | 9 | 11.25 % | **exceeded** (limit 8) |
| upright | 80 | 4 | 5.00 % | held |
| edge | 7 | 0 | 0 % | held |

As locked, the draw stopped before any replacement and exited 3. No crops and no console were made. Build-a 8e173740 (v4) stays on record, unsigned.

**Edge is nearly exhausted.** After the v2, v3 and v4 exclusions, only 7 edge words remain in the 20 pages, against a target of 40. So the first-choice draw is 167 words, not 200. The lock did not foresee this. Any further draw from these pages that excludes all earlier sets is short in edge by the same amount.

**The population (condition 2).** These are measured over every word of every pool, after the exclusions. They are for scale and did not affect the draw.

| stratum | pool | do not crop cleanly | share |
|---|---|---|---|
| slanted | 471 | 47 | 9.98 % |
| upright | 11 409 | 726 | 6.36 % |
| edge | 7 | 0 | 0 % |

A set built under this crop rule judges the measure on words that crop cleanly. About 10 % of slanted words and 6 % of upright words on these pages do not.

**Every dropped word (condition 2).** All 13 are first choices. None was replaced.

| stratum | page | key | failing side | slant |
|---|---|---|---|---|
| slanted | 899 | 899/left/2.1.1.2 | bottom | 0.11 |
| slanted | 903 | 903/right/1.1.1.1 | top | 0.25 |
| slanted | 907 | 907/right/1.1.31.3 | top | 0.25 |
| slanted | 910 | 910/right/1.1.1.2 | top | 0.25 |
| slanted | 911 | 911/left/1.9.7.6 | bottom | 0.25 |
| slanted | 912 | 912/right/1.1.19.5 | top | 0.11 |
| slanted | 912 | 912/left/1.1.19.8 | top | 0.26 |
| slanted | 915 | 915/right/1.1.15.1 | bottom | 0.32 |
| slanted | 915 | 915/right/1.1.1.3 | top | 0.25 |
| upright | 904 | 904/left/1.1.43.1 | bottom | 0.02 |
| upright | 910 | 910/left/1.2.6.1 | bottom | -0.04 |
| upright | 914 | 914/right/5.1.1.3 | bottom | -0.04 |
| upright | 915 | 915/right/1.1.30.8 | top | 0.01 |

By side: top 7, bottom 6, both 0.

**The predictions, scored.** The misses are recorded and the lock is unedited.

| # | predicted | measured | |
|---|---|---|---|
| V1 | n = 200 (80/80/40); 0 shared | 167 (80/80/7); 0 shared | **missed** (edge exhausted) |
| V2 | failures in [8, 26] | 13 | held |
| V3 | ceiling trips, on upright | trips, on **slanted** (9/80); upright 4/80 | **missed** as written |
| V4 | pool shares: slanted 3–10 %, upright 6–16 %, edge 2–12 % | 9.98 %, 6.36 %, 0 % (of 7) | slanted held, upright held, edge **missed** |
| V5, V6 | if the ceiling holds | not reached | (candidates and drops byte-identical; clean_run true) |
| V7 | suite passes; weigh 71c14a5d187d / c8fe9e910b5a; 0 violations; no data change | 740 passed; both hashes unchanged; 0 violations; no data change | held |
| V8, V9 | after signing | no console | not reached |

**The ceiling sits on the pool rate.** The slanted pool fails at 9.98 %, and the ceiling is 10 %. A fresh draw of 80 slanted words then exceeds 8 failures about 40 % of the time (binomial, p = 47/471: 0.405). That holds for any new salt. A redraw would pass or trip by chance, and drawing again until one passes would pick a seed by its outcome. I have not redrawn.

### The tall-box measure: two bands in none

| # | predicted | measured | |
|---|---|---|---|
| TB1 | exactly w023, w073, w102, w137, w140, w159, w160, w174, w189, w200; boxes 105..141 px | the same 10; 105..141 px | held |
| TB2 | at least 8 of 10 show two bands | **0 of 10** | **missed** |
| TB3 | at most 5 % of control lines | 0 of 174 distinct lines (from the 184 kept rows) | held |
| TB4 | a/b byte-identical; clean_run true | `bands.json` identical; clean_run true | held |

As the lock says, **the measurement does not support the merged-lines reading.** No cause is recorded beyond what T measures.

For scale only (unlocked; numeric, no image viewed), I checked the tool against hand-computed profiles. They agree. Nine of the ten boxes do have an interior gap of 3 or more rows. But in every case, the far side of any such gap holds at most 5.4 % of the box's ink and at most 22 px of rows. T requires at least 20 % and 15 px on each side. So each box is one dominant band holding about 95 % or more of its ink.

Both open findings stay open:
- these 10;
- the 6 with the full 12 px.

## A-9. ADR-0007

The Verification, as amended, was locked first. It is the last section of ADR-0007 (`610471e`, 2026-11-22T14:50Z), committed before any ADR-0007 code. The build followed in `07682a5`, with 51 born tests in `tests/test_congregation.py`. All of it was tested on synthetic fixtures, and no real Congregation is minted.

**What was built:**
- **C1, C3:** `gc:exceptsLocus`, `gc:PersonalKnowledge`, `gc:readOn` and `gc:archivedCopy` in `ontology/core.ttl`.
- **C2:** `reasoner/10-inheritance.ru` blocks an excepted Locus on the path, the same way an own Holding does. `20-consistency.ru` is unchanged. The Jena and rdflib paths agree on an exceptsLocus case.
- **SHACL (a) to (e)** in `ontology/shapes.ttl`.
  - The IRI patterns are widened only for the ADR's own forms: `body/congregation/{slug}`, `holding/congregation/…` and `source/congregation/{slug}/statement`.
  - A Holding of any other Body must still cite a SourceDivision.
- **C6, C8:** `weigh.render_body` adds, for a Congregation only (ranked or excluded):
  - "subscribes to", "exceptions", "entered by", "confirmed by" and "correction";
  - a "cells:" block of "inherited from", "own (statement, …)", "own (personal knowledge)" and "excepted, unknown";
  - "inherited from <parent>" on an excluded reason.
- **C7:** `tools/console/specs/congregation.py` builds the form from the data.
  - Ingest checks every C7 condition. It also refuses a few contradictions beyond them: "no alternative" with a Position filled, a statement "where" under personal knowledge, and a malformed URL.
  - Every row it mints is proposed by agent/chris, with no ratifiedBy.
  - It writes `data/congregation-{slug}.ttl` only with `--write`, and never overwrites one.

| # | measured | |
|---|---|---|
| AV1 | C effectively holds P1's and P2's Holdings on L1 and L6; its own on L2, L4 and L5; none on L3 | held |
| AV2 | parents-differ fires on L6 only; it still fires on an excepted Locus where the parents differ | held |
| AV3 | L3's weight is in the denominator only; one parent with and without the exception differs by exactly w(L3)/(w(L1)+w(L3)); no cost, break or tolerated row | held |
| AV4 | every cell kind; "not yet confirmed"; "confirmed by: <label>" when ratifiedBy is added; other Bodies unchanged | held |
| AV5 | an exclusion from an inherited Holding names the parent's source and says "inherited from" | held |
| AV6 | a violation for each of (a) to (e); the AV1 fixture conforms | held |
| AV7 | the spec passes every build check; signed export → `--ttl-out` → reproduces AV1; "other, as written" mints nothing and is listed; each broken condition is refused; nothing is written under data/ without the flags | held (but see Q4 below) |
| AV8 | weigh 71c14a5d187d / c8fe9e910b5a; ingest 0 violations; no data/*.ttl change; suite 791 passed; no existing test edited | held |

**Questions for the architect.** C2, C4 and C6 are from the lock; C7-L6 arose in the build.
- **C2.** Should an exception clear parents-differ? As built, it does not (AV2).
- **C4.** Does Chris's signature count as the confirmation? As built, every row is proposed and the page says "not yet confirmed".
- **C6.** The correction route. The text has no contact detail yet.
- **C7-L6 (new).** The lock's row for a Locus where the parents differ offers only "holds this one" and "excepts: no alternative stated". So "the church's statement says nothing here", which is AV1's L6, has no option. AV7 reproduces L6 by abstaining the row, which mints nothing.
  - The trouble is that abstaining also means "the signer could not tell".
  - **Proposal:** add a third option, "says nothing: keeps both", to the differ row. It would mint nothing, as now, and the record would show it as an answer, not an abstention. This needs your word, because it amends C7.

## C-1. The p. 914 re-ask, signed

Chris signed `d7a6aab0734ffe3e` on 2026-11-22. The record is [SIGNED_region_reask_d7a6aab0734ffe3e.md](SIGNED_region_reask_d7a6aab0734ffe3e.md).
- It was ingested with `--code-at 11a905f`, not provisional, and the build hash recomputed.
- The ingest ran from a clean worktree at `56004c5`, so the ADR-0007 work in progress could not touch it.
- The build agent did not view the image.

**The verdict: yes.** The small type at the foot of p. 914 left is column footnotes. Chris's note, verbatim:

> the magenta is most of the footnote except one line above it. It does container the part of the footnote that is aligned with the left most column of the footnote section. I cannot see the entire footnote so do not know the extent of how much of the footnote is covered

**What follows:**
- **F-1 is confirmed from pixels for this one column.** F-1 is report 14's reading that the moved blocks are column footnotes. Until now it stood "from numbers, unconfirmed from pixels" (truth-set audit, A-1).
  - It is not extended to the other 27 moved blocks without their own pixels.
- **Report 16's Q-1 stays superseded.** Q-1 proposed withdrawing F-1.
- **SI8 stays recorded as missed and is not edited.** SI8 predicted "yes" and was scored against the faulted verdict. The usable verdict now agrees with what SI8 locked.
- **New, from Chris's note:**
  - **(a)** the measured boundary, y = 6127, starts one footnote line low;
  - **(b)** he could not see the footnote's full extent in the image.
  - Neither is measured yet. I record no cause.
  - If the boundary matters for a later measure, a lock would come first. That measure would be a row profile of that column foot, numeric only.

## A-10. Phase-2 locators

The architect corrected the premise: their reading is not an authority. The phase-2 locators stay proposals until a Position needs one. When it does, the build agent reads the page and proposes, and Chris signs, as in phase 1. This is recorded in the handoff.

## A-5 and BH1

- **A-5:** accepted, including Gill Doctrinal II = 16 and Scott 1831 for Dort. The refused download stays refused.
- **BH1:** recorded as missed. The architect ruled that the lock's clause was wrong, not the build.

## Noted

- **A permission check refused one lock file.** I tried to write ADR-0007's Verification lock as a read-only local file, `~/.golden-chain/adr0007-verification-predictions-locked.txt`. The auto-mode permission check refused the write ("Undermining Oversight"), and I did not work around it. The lock was committed instead, as the last section of ADR-0007 (`610471e`), timed 2026-11-22T14:50Z, before any ADR-0007 code. Git history is its seal. If you want the local read-only copy as well, Chris can allow that write, or make the file himself from the ADR section.
- **X's edge limit assumed 40 first choices.** With only 7, the integer rule would trip on a single failure. Edge had 0 failures, so it did not matter here.

## What waits, on whom

### The architect

1. **A-11: what happens to the italic truth set.** Replacement is stopped by its ceiling, and edge cannot be refilled from these pages. The choices I see:
   - **(i)** Sign v4's build-a 8e173740 as it is: 184 words, with its 16 drops listed (report 20) and the population statement above.
   - **(ii)** Set a new ceiling from the measured pool rates, locked before a v6 draw.
   - **(iii)** Widen the pages, which means new OCR and a new lock.

   I recommend (i). Its drops (8 %) match the pool rates measured here, and it needs no new draw.
2. **ADR-0007:** questions C2, C4 and C6 from the lock, and C7-L6 from the build (see A-9).
3. **ADR-0006 R6:** the text, for full ratification (A-8).

4. **p. 914 (C-1):** Chris's note says the measured boundary starts one footnote line low. Should the boundary be measured again, under a lock?

### Chris

- C-1 is done (signed 2026-11-22).
- Still waiting: C-2, C-3 (if not yet done), C-4, C-6, C-8 and C-9, and the follow-up console `eb961ddb1e582ed6`. Nothing new from this report: no v5 console was built.
