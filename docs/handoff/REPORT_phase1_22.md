# Report 22: the ruling on report 21 worked; the site's-ground drafts sent up

- **From:** the build agent, 2026-11-22.
- **On:** [RULING_report_21.md](RULING_report_21.md) and [RULING_site_ground_2026-11-22.md](RULING_site_ground_2026-11-22.md), both filed verbatim (`a44dd6e`).
- **In short:**
  - A-11 (i) is worked (`ab0fb49`). The v4 console README now says SIGN. The population statement and the 16 drops sit beside the future record.
  - ADR-0007 amendment 2 was locked before code (`a44dd6e`) and built (`77a62a1`). AW1 to AW4 held. **AW5 missed on its edit list:** two existing tests it did not name also had to change. Both are named below.
  - C-9: vol. 43 (1877) was seen (`18f4de3`). Still no witness of record for the Articles.
  - The four site's-ground drafts are sent up (`a271f90`). Nothing is built.
  - Six questions for the architect, and one check for Chris, are listed at the end.

## A-11 (i). Truth set v4, `ab0fb49`

- [POPULATION_truthset_italic_v4_8e173740.md](POPULATION_truthset_italic_v4_8e173740.md) holds the population statement:

  | stratum | pool | do not crop cleanly | share |
  |---|---|---|---|
  | slanted | 471 | 47 | 9.98 % |
  | upright | 11 409 | 726 | 6.36 % |
  | edge | 7 | 0 | — |

- It also lists the 16 drops: id, stratum, page, key, side and slant. The edge rows show "— (abstained)", because the slant measure abstains on edge words.
- It names the record to come, `SIGNED_truthset_italic_v4_8e173740c37b714d.md`.
- Recorded against the architect, as ruled: the 10 % ceiling was set without the pool rate.
- There is no v6 from these pages. TB2 is falsified, and both tall-box findings stay open with no cause.
- The local README (`~/.golden-chain/console/truthset-italic-v4/README_WHICH_TO_SIGN.txt`) says **SIGN build-a, 184 rows**, with the population statement.

## ADR-0007 amendment 2 (C2, C4, C6, C7-L6)

### The lock, `a44dd6e`

- The lock is the ADR's section "Verification, amendment 2". It was committed at 2026-11-22T17:16Z, before any code. It holds C2', C4', C6', C7', C8' and predictions AW1 to AW5.
- Per the ruling, no local lock copy was made. Git history seals it.

### The build, `77a62a1`

| file | change |
|---|---|
| `reasoner/20-consistency.ru` | C2': parents-differ skips a Locus the Congregation excepts |
| `goldenchain/weigh.py` | C4': "not yet confirmed by the church", or "confirmed by: <label>". C8': the differ line in the cells block |
| `tools/console/specs/congregation.py` | C7': differ rows offer three answers; the third is "says nothing: keeps both" (code `keeps-both`) |
| `tools/console/ingest.py` | `keeps-both` mints nothing and refuses any filled field. The record gains "## Answered, nothing minted" (left out when empty) |
| `tests/test_congregation.py` | AW1 to AW4 born tests; the edits below |

- **C6** needed no code. The correction line already states the route in words, with no address. AW4 checks that it has no "@" and no "http".

### Results against the lock

- **AW1 held.** In the excepted fixture, parents-differ does not fire, and the cell is "excepted, unknown". AV2's first clause holds.
- **AW2 held.** Differ rows offer exactly the three answers, in order. The spec passes every build check.
- **AW3 held.**
  - L6 answered "keeps both" ingests with no L6 triple.
  - The `gc:proposedBy` count is unchanged, and parents-differ fires on L6.
  - The record has the "Answered, nothing minted" line.
  - Every filled field is refused, and nothing is written.
- **AW4 held.** It shows the two inherited lines, then the differ line, on L6 only; both confirmation lines; and a correction line with no "@" or "http".
- **AW5 missed, on its list of edited tests only.** Its other clauses held:
  - 800 passed (was 791);
  - ingest 0 violations, 3 warnings;
  - weigh members `71c14a5d187d` and officers `c8fe9e910b5a`, both byte-identical;
  - no data/*.ttl change.
- **The edits AW5 listed:**
  - The AV2 second-clause test was renamed `test_av2_second_clause_superseded_by_aw1_parents_differ_does_not_fire_on_an_excepted_locus` and inverted.
  - The AV4 "not yet confirmed" string was updated.
  - The AV7 fixture still abstains L6 by default. AW3 answers it in its own test, so that listed edit was not needed.
- **The edits AW5 did not list.** Both follow directly from the ruling (C7-L6, C8'), and each carries a comment in the test saying so:
  1. `test_av4_weigh_renders_the_congregation`: the expected cells list gains `"    - locus/l6: its standards differ here and its statement does not say"`. The AV1 fixture has differing parents on L6, so C8' adds the line there.
  2. `test_av7_spec_passes_every_build_check_and_is_built_from_the_data`: the differ row's options now include "says nothing: keeps both".
- The lock is not edited. The miss is recorded here.

## p. 914 and R6

- p. 914 is recorded as ruled: F-1 is confirmed for that one column only, and the boundary is not re-measured. When footnotes are separated from body text for OCR, that step gets its own lock, and Chris's note is its first test case.
- ADR-0006 R6 stays provisional, waiting for the architect's reading.

## C-9. Gospel Standard vol. 43 (1877), `18f4de3`

- It is recorded in [gospel-standard.md](../sources/phase2/gospel-standard.md) (sha256 `06f2ed75…`, 557 PDF pages, folio = PDF − 1).
- The index has no entry for the Articles. The November number (pp. 465–512) has no notice.
- "My Farewell" (p. 553) says "As stated on our last wrapper…". So the November 1877 announcement was a wrapper item, and the scan does not contain it.
- None of vols. 38, 43, 44 and 45 gives the witness.
- **Proposed:** look for a separate printing of the Articles by the Societies. No new download is asked for until the architect chooses a route.

## The site's ground: four drafts sent up, `a271f90`

Nothing is built. The details are in [RULING_site_ground_2026-11-22.md](RULING_site_ground_2026-11-22.md), "Drafts sent up".

1. ADR-0003 Revision 3 (R3.1–R3.6).
2. [ADR-0009](../adr/0009-scope-of-documents.md), the scope of documents.
3. The warrant rule, and row 10 of [PROPOSAL_phase2_loci.md](PROPOSAL_phase2_loci.md):
   - WCF 1.6 is located in the 1647 Tyler printing, leaves 13–14.
   - LBC 1.6 is located in the 1719 printing, pp. 29–30. The 1677 page is not read.
   - No Position wording is proposed.
4. [ADR-0010](../adr/0010-church-accounts.md), church accounts.

## Questions

**For the architect:**
- **A-1.** "The three gates" in item 4 are defined nowhere in the repo. Please state them (ADR-0010, Decision 7).
- **A-2.** ADR-0003 R3, questions Q1–Q4.
- **A-3.** ADR-0009, open points 1–4 (backfill, granularity, Teachers, licensed private texts).
- **A-4.** ADR-0010, the private-store split: the one place rule 1 yields to privacy. Also its open points 2, 4 and 5.
- **A-5.** The Gospel Standard witness route (a separate printing by the Societies?).
- **A-6.** The R6 text (standing).

**For Chris:**
- **C-1.** Sign v4 build-a `8e173740c37b714d` (now SIGN, 184 rows).
- **C-2.** Check the folio on WCF 1647 leaf 14 (IA `humbleadviceofas00west`) from the pixels. At the build agent's resolution it reads "[6]", where [4] is expected.
- **C-3.** A correction contact address, for ADR-0007 C6 (do not invent one).
- **C-4.** A photograph of the LBC 1677 facsimile page for 1.6.
- **Standing:** the C-2, C-3 (if not yet done), C-4, C-6 and C-8 items of earlier reports, and the follow-up `eb961ddb1e582ed6`.
