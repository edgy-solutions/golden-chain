# Report 28: the overnight order of 2026-11-22, worked down the list

- **From:** the build agent, the morning of 2026-11-23.
- **On:** [RULING_report_27.md](RULING_report_27.md) and the overnight order of 2026-11-22 (items 1-10).
- Every item that was built was locked first, and every lock was pushed before its code.

## Waiting on Chris, and on the architect (the single list)

### Chris

1. **Sign the sitting-2 console:** `~/.golden-chain/console/plumb-line-followup/console_plumb-line-followup_b7c9ffb0096a4522.html` (26 rows: 23a, 33d, 33e). Plain words are on every row.
2. **Sign the statements console** (item 6): `~/.golden-chain/console/statements/console_statements_0894df4edd1fe4b1.html`. It has three parts:
   - the standard, in your own words;
   - the scope, in your own words;
   - the 14 documents (12 in the data, plus Owen's *Hebrews* and the 1875 Gadsby printing). Each is proposed "include", except the BSB 1984 foreword, proposed "not now".
   - On the Gadsby row, you also confirm the title page and the Articles I-XXXI span from four page images.
3. **Item 8, the 1875 Gadsby locators and headings:** check them against the pixels before anything is minted ([gospel-standard-1875-locators.md](../sources/phase2/gospel-standard-1875-locators.md)).

### The architect

4. **R3 test amendments (26 tests, held on `hold/adr3-r3` `a193e8b`).** They fall only in the six files R10 named. One amendment changes what a test checks: `test_refuse_two_literals` used to test "written 2 times", which cannot happen in the one form because duplicate triples collapse. It now checks that two literal objects are refused as non-Positions. Rule on all 26.
5. **`hold/weigh-fix-1` and `test_w1_w2_w3`:** carried into `hold/adr3-r3`. Merging R3 to `phase-0` brings fix 1 with it.
6. **The side-branch policy:** changes that need existing tests amended go on pushed `hold/...` branches until ruled. Confirm or change it.
7. **Batch C (item 4), stopped under rule 8 on the Argument unit.** The readings give 117, 114 or 108 Arguments. I propose 114, one per quotation. Also open:
   - Gill's "Sixthly" heads 2 and 6 print references that the plan does not take;
   - the (a)/(b) labels.
8. **Q-S2-1:** how answers on Positions not yet in the data enter it. Proposed: from the signed record at minting. Alternative: a sitting 3.
9. **Ingest order for sitting 2:** if (ii) and (iii) are both held taught or required, retire the (ii)-(iii) mark in the same change as the merge.
10. **Q-I-1 to Q-I-4 (the statements console):**
    - whether `source/plumb-line` is exempt from ADR-0009;
    - how the signed statements and inclusions enter the data (one locked change, proposed);
    - whether Owen is one Source node or one per volume;
    - BSB 1984 "not now", until written confirmation is on file.
11. **Report 25 V-1 and V-2** (Gill on the administrator): still open; they are on the sitting-2 console as rows V1-V4.
12. **The ch07 (g) note:** carried over: the new ch07 (g) note on the LBC 1677 console (`0a73bb5afa616446`, still unsigned) is a proposal for that console's ingest; it enters nothing until Chris signs.
13. **The LBC flip questions:** carried over, for the LBC 1677 console's ingest when Chris signs: whether the flip to `agent/chris`, ratified also rewrites the Argument comments and the axiom comment text, and how the pinned `test_asprinted` test is treated.
14. **Item 9, the phase-2 locus table:**
    - Black Rock (1832) and Fulton (1900) have transcripts only, so no page witness;
    - Brine has no free scan;
    - Hoeksema's *Triple Breach* (English 1942) is restricted;
    - the rights in the CRC 1924 English translation are unknown.
15. **Item 7 results:** I1, I2, I5 and I6 held; I3 missed (35 of 220 spans paired); I4 missed on 4 of 7 pages (fewer references found in the OCR than were hand-minted on 898, 899, 910 and 911). Counts are below. Whether to lock a second definition (a reference before the span, a wider window) is for you; nothing was tried beyond the lock.
16. **Which Gospel Standard edition a Body is weighed on:** the 1875 printing witnesses Articles 1-31 only, and Articles 32-35 have no witness.
17. **"Applied" in RULING_report_27.md:** filled in by this report (below).

## The items, scored

| # | Item | Lock | Commits | Result |
|---|---|---|---|---|
| 1a | Weigh fix 1: a flag's source from its own axiom | [LOCK_weigh_flag_source](LOCK_weigh_flag_source_2026-11-22.md) F1-F5, `ea28fa4` | `194149b`, `2a817d1` on `hold/weigh-fix-1` | Held on the side branch. The existing test `test_weigh::test_w1_w2_w3` fails with the fix (its fixture sets a flag with no axiom), so it was reported before it was amended; the proposed amendment is `2a817d1`, waiting on the architect (list item 5). F1 held on the real data: all 4 exclusion lines name `sitting-eb961ddb1e582ed6`. |
| 1b | Weigh fix 2: every source of a Holding in IRI order; two-process byte test | [LOCK_weigh_sources_sorted](LOCK_weigh_sources_sorted_2026-11-22.md) S1-S5, `bbefc04` | `395f3ef` | S1-S5 held. One hash across PYTHONHASHSEED 0-5: members `46381316eb30`, officers `91bfab215992`. Suite 819, no existing test amended, ingest 0/0. |
| 1c | The note on weigh variance | (a note, no prediction) | `07712fb` | [NOTE_weigh_variance](NOTE_weigh_variance_2026-11-22.md): output first varies at `bc651fe`. Earlier byte-identity claims were verified at their own commits; two statements are marked as not verifiable as stated. |
| 1d | The frozen fixture | [LOCK_frozen_fixture_eight](LOCK_frozen_fixture_eight_2026-11-22.md) X1-X4, `b23ef96` | `4bff5fb` | X1-X4 held. The eight tests read `tests/fixtures/data-8ac7e41/`. Suite 820. "These eight are the last exception." |
| 2 | ADR-0003 R3 | [LOCK_adr3_r3](LOCK_adr3_r3_2026-11-22.md) R1-R10, `ac25d0a` | `f4e8b5a` (code), `a193e8b` (26 PROPOSED amendments), on `hold/adr3-r3` | R1-R10 held on the branch, which runs 828 passed and 16 skipped, weigh members `b5ad57ea0df3` and officers `6a2ffd426bf9`, plumb-line sha `bfb0238c`. The branch includes weigh fix 1. Held until the 26 amendments are ruled on (list item 4). |
| 3 | Gill on the administrator | `LOCK_validity3_gill` | report 25 | Done in REPORT_phase1_25. V-1 and V-2 are rows V1-V4 on sitting 2. |
| 4 | Batch C | [LOCK_batchC_rebased](LOCK_batchC_rebased_2026-11-22.md) B1-B9, `f13ff64` | `e663931` | **Stopped under rule 8.** All 25 Harbaugh and 8 Belgic notes match the page images. Minting stopped on the Argument unit, because the held lock's premise (one reference per proof answer) is false in three places. The readings give 117, 114 or 108 Arguments; Passage is 161 under all three. I propose 114 (list item 7). Nothing was minted. |
| 5 | Sitting 2 console | [LOCK_sitting2_console](LOCK_sitting2_console_2026-11-22.md) S1-S7, `c07d4b4` | `84770b2` | S1-S7 held. 3 sections, rows 10/9/7 = 26, 29 fields, 6 images; the sitting-1 digest is still `ea6d4978e8ed2884`. Page build16 `b7c9ffb0096a4522`. Data unchanged, ingest 0/0. |
| 6 | Statements and inclusion console | [LOCK_statements_console](LOCK_statements_console_2026-11-22.md) T1-T7, `af61a1b` | `c4f18a2` | T1-T7 held. Suite 833, page build16 `0894df4edd1fe4b1`. One inaccuracy in the lock header (not edited): it says the lock was "committed before the builder and the content file", but the content file went in the same commit as the lock, still before the builder. |
| 7 | Italic spans | [LOCK_italic_spans](LOCK_italic_spans_2026-11-22.md) I1-I6, `2831a3e` | `6070831` | I1, I2, I5, I6 held; I3 and I4 missed. See the section below. |
| 8 | Gospel Standard 1875 locators and headings | (proposals, no prediction) | `c6cfe71` | [gospel-standard-1875-locators.md](../sources/phase2/gospel-standard-1875-locators.md). The printing ends at Article XXXI on p. 15, so Articles 32-35 are absent. Article 9 (pp. 10-11) was not viewed. Proposals only, for Chris's check (list item 3). |
| 9 | Phase-2 locus table, the gospel call | (candidates only) | `c6cfe71` | [locus-table-gospel-call.md](../sources/phase2/locus-table-gospel-call.md): 12 sources and 11 rows, candidates only. The bibliographic lead check found scans on the Internet Archive for Gill's *Cause of God and Truth* (1735-38), Fuller's first edition (1785) and Hassell (1886). It found none for Brine's *Refutation* (1743) or the Black Rock Address (transcripts only). HathiTrust and PTS returned 403 and the Google Books API returned 429; none of these refusals was worked around. |
| 10 | The examine/try prototype, regenerated | (no prediction) | none (local output) | `phase-0` at `af61a1b` and `hold/adr3-r3` at `a193e8b`, both `clean_run`. Each has positions 24, arguments 80, holdings 63, cites rows 217, 2 candidate-only passages, and 12 examine + 140 try + 1 index pages. Store sha `ddd27a70` (phase-0) and `630bcfd4` (R3). Output is in `~/.golden-chain/prototype-2026-11-22-phase0` and `-adr3-r3`. |

## Item 7: italic spans on the baptism chapter, the counts

The tool is `tools/italic_spans.py` (`6070831`, 18 born tests, suite 851). It was run twice over pp. 896-915, on OCR run 1 (`00cb18e0`) and v4 slant (`f25ea51e`), into `~/.golden-chain/italic-spans-2026-11-22-a` and `-b`. Counts only. No word text is in this report, nothing was minted, and no image was opened.

| Page | Spans | Paired | Unpaired | References found | Hand-minted cites |
|---|---|---|---|---|---|
| 896 | 3 | 0 | 3 | 1 | - |
| 897 | 6 | 2 | 4 | 5 | 5 |
| 898 | 15 | 6 | 9 | 19 | 20 |
| 899 | 10 | 2 | 8 | 3 | 4 |
| 900 | 13 | 2 | 11 | 13 | 7 |
| 901 | 14 | 0 | 14 | 3 | - |
| 902 | 16 | 1 | 15 | 2 | - |
| 903 | 9 | 1 | 8 | 3 | - |
| 904 | 3 | 0 | 3 | 8 | - |
| 905 | 4 | 2 | 2 | 3 | - |
| 906 | 6 | 0 | 6 | 1 | - |
| 907 | 18 | 1 | 17 | 3 | - |
| 908 | 3 | 0 | 3 | 0 | - |
| 909 | 8 | 2 | 6 | 5 | - |
| 910 | 19 | 2 | 17 | 2 | 5 |
| 911 | 11 | 0 | 11 | 2 | 6 |
| 912 | 15 | 2 | 13 | 3 | - |
| 913 | 16 | 2 | 14 | 5 | - |
| 914 | 14 | 5 | 9 | 10 | 9 |
| 915 | 17 | 5 | 12 | 9 | - |
| **Total** | **220** | **35** | **185** | **100** (94 with a book name, 6 continuations) | **56** |

Other counts: 700 words slanted; 12390 words measured; 2 spans touch a region edge; 5 "ver." forms, counted separately as the lock says.

| # | Prediction | Result |
|---|---|---|
| I1 | Born tests; existing tests unamended | **Held.** 18 born tests; suite 851 = 833 + 18; no existing test amended. |
| I2 | 150-400 spans | **Held:** 220. |
| I3 | At least half the spans paired | **Missed:** 35 of 220 (16%). |
| I4 | On each of the 7 pages, references found ≥ hand-minted cites | **Missed on 4 of 7.** Held on 897 (5/5), 900 (13/7) and 914 (10/9). Missed on 898 (19/20), 899 (3/4), 910 (2/5) and 911 (2/6). |
| I5 | Byte-identical `spans.json` and `summary.json` | **Held.** sha `2afca303` and `0cfb5577` in both runs. Only `run_header.json` differs, by its time, as the lock says. |
| I6 | No data change; nothing minted; no image opened | **Held.** |

What the misses say (counts only; I did not read the OCR text to explain them):

- **I3.** Most italic spans have no Scripture reference within 8 words after them. Either Gill's italic is mostly not quotation followed by its reference, or the reference sits before the quotation or across a region break, which the lock's definition does not pair.
- **I4.** The detector finds fewer references than were hand-minted on four pages. The hand-minted cites came from the page images, where a reference the OCR reads damaged (or a form outside the lock's book list) still counts. The miss shows that a detector run on this OCR alone undercounts references on those pages.

Choices the implementer made where the lock and spec were loose (recorded, not ruled):

- Continuation: at most 6 words, counted from the end of the previous reference.
- Pairing: at most 8 words strictly between the span and the reference. A numeral prefix ("1", "2", "i", "ii") starts the reference.
- "ver." is matched case-sensitively.
- Slant rows that are neither slanted nor abstaining are treated as abstained.
- Book tokens are case-sensitive.

The misses stand as locked. Any second definition (a reference before the span, a wider window, a longer book list) needs its own lock first (list item 15).

## Applied

What was done on each part of [RULING_report_27.md](RULING_report_27.md):

- **The weigh fixes:** fix 2 is on `phase-0` (`395f3ef`). Fix 1 is held on `hold/weigh-fix-1` and carried into `hold/adr3-r3`, because an existing test fails with it; the amendment waits.
- **The frozen fixture:** done (`4bff5fb`). These eight tests are the last exception.
- **ADR-0003 R3:** built on `hold/adr3-r3` (`f4e8b5a`): the Q3 migration, "by this site's standard", and "The site's statement of its standard is not yet signed." It is held for the 26 test amendments (`a193e8b`).
- **Gadsby 1875:** labelled as the proposed witness for Articles 1-31 only. Chris confirms it on the statements console (the Gadsby row, four page images). Articles 32-35 still have no witness.
- **Next, in order:** both weigh fixes done; R3 built and held; sitting 2 built; Batch C stopped under rule 8.
