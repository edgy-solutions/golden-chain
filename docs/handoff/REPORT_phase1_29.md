# Report 29: the ruling on report 28 worked down

- **From:** the build agent, 2026-11-26. Branches `phase-0` (at `b3b17e3`, plus this report) and `hold/batchC-unit` (`f639051`, `67de543`), both pushed.
- **On:** [RULING_report_28.md](RULING_report_28.md), items 4-17.

## One list: what waits on Chris, and on the architect

**On Chris (sign from the pixels; each page is local, under `~/.golden-chain/console/`):**

1. **Sitting 2:** `plumb-line-followup/console_plumb-line-followup_18a4a13dfeffb6e9.html`.
   - The earlier page `b7c9ffb0096a4522` is superseded. The R3 merge changed one help sentence ("this site's standard"), so its build16 moved (LOCK_merge_adr3_r3 M6, a miss).
   - Ruling 9 (retire the (ii)-(iii) mark) applies at its ingest.
   - Its instrumentality answers then bind to Batch C's Positions (ruling 8).
2. **Statements and inclusion:** `statements/console_statements_f3f1af17d9075ba5.html`.
   - It replaces `0894df4edd1fe4b1`, which is superseded.
   - On the BSB foreword row, the proposal is now "include", for the architect's reason (Q-I-4). If you include it, it carries the label "short extracts only; written confirmation to be sought before launch". The choice is yours.
   - One row is added: Harbaugh's Heidelberg Catechism, a new Source in Batch C.
   - This page was built from the hold branch, so it waits on the architect accepting Batch C (Q-C-3). If Batch C changes, the page is rebuilt.
3. **LBC 1677:** `console_lbc-1677_0a73bb5afa616446.html` (unchanged). Rulings 12-13 apply at its ingest, approved in advance.
4. **Gill's italic:** `italic-spans/console_italic-spans_9b19159be3098c64.html`, 40 rows (ruling 15).
   - Keys a-g choose the seven options, and o chooses "other, as written". The console's key check allows letters only, so the digits 1-7 the lock named could not be used.

**On the architect:**

- **Q-C-1.** Gill head 6, John 14:15, 21, 23, is "not taken". Its clause is about keeping his commandments in general (LOCK_batchC_unit, table). The alternative takes it as a fifth (b) Argument with three new Passages.
- **Q-C-2.** The ADR-0005 unit is applied from Batch C on. Existing Arguments were not checked against it. Should they be?
- **Q-C-3.** Accept `hold/batchC-unit` into `phase-0`? It carries the mint, the three `test_console_specs` amendments (as for Batch B) and the `hand_minted` fix in `tools/italic_spans.py` (below). The merge touches no file `phase-0` changed since `72c4afb`.
- **Q-C-4.** Statements-2 is stacked on the hold branch, because its builder needs the Harbaugh Source. The alternative was to build it without the Harbaugh row now and add the row in a third file later. I chose to stack it.
- **Q-H-1** (LOCK_replay_held). The instrumentality bindings are written by the sitting-2 ingest, since sitting 2 is not yet signed.

## Item by item

| Item | What | Lock | Commit | Result |
|---|---|---|---|---|
| 4-5 | Merge `hold/adr3-r3` | [LOCK_merge_adr3_r3](LOCK_merge_adr3_r3_2026-11-26.md) M1-M6 | `59e156e` | Merged, with the 27 ruled amendments. M1-M5 held; M6 missed (see Scores). |
| 6 | Side-branch policy | — | — | Applied at once: Batch C needed three existing tests amended, so it is on `hold/batchC-unit`, pushed (below). |
| 7 | Batch C on the quotation unit | ADR-0005 amended, [LOCK_batchC_unit](LOCK_batchC_unit_2026-11-26.md) U1-U10, `72c4afb` | `f639051` on `hold/batchC-unit` | Minted: Locus 33e, (a) "The Holy Ghost confirms faith by the use of the sacraments." (Heidelberg 65), (b) "proposed, wording pending", 35 Arguments (Harbaugh 23, Belgic 8 for (a); Gill heads 1-4 for (b)). Gill head 6 not taken, with its clauses in the lock (Q-C-1). **Held, not merged**: see Q-C-3. |
| 8 | Replay holds answers on Positions not yet in the data | [LOCK_replay_held](LOCK_replay_held_2026-11-26.md) H1-H6, `4d7a1d8` | `b3b17e3` | `tools/console/plumb_merge.py` reads a committed bindings file, `docs/sittings/plumb-line-bindings.json` (empty for now). A bound answer whose target is not yet in `data/loci.ttl` is noted "held for <target>, not yet in the data" in the TTL comments. Once the target exists, it is applied at its own sitting's place in the order, through the same row code as a real row. 16 born tests, including the ruled one (before and after minting equals a single replay after). |
| 9 | Retire the (ii)-(iii) mark at the sitting-2 merge | — | — | Waits on Chris signing sitting 2. It will be done in the sitting-2 ingest change. |
| 10 | Q-I-1 to Q-I-3 | — | `4a52926` | Done in docs (ADR-0009). |
| 10 | Q-I-4, the BSB row | [LOCK_statements2](LOCK_statements2_2026-11-26.md) S1-S4, `72c4afb` | `67de543` on `hold/batchC-unit` | `docs/consoles/statements-2.json`: the BSB row proposes "include" and carries the architect's label; Harbaugh's row is added. Page `f3f1af17d9075ba5`; `0894df4edd1fe4b1` is superseded. It sits on the hold branch because its builder needs the Harbaugh Source, which Batch C mints (Q-C-4). |
| 12-13 | LBC 1677 ingest | approved in advance | — | Waits on Chris signing `0a73bb5afa616446`. The ingest will flip the axiom's contributor and status, remove the "model-proposed" comment, and move the pinned asPrinted test to the frozen fixture. |
| 14, 16 | Documents and Bodies | — | `4a52926` | Done in docs. |
| 15 | Italic-spans console | [LOCK_italic_console](LOCK_italic_console_2026-11-26.md) C1-C6, `4d7a1d8` | `66a98b8` | 40 rows, 20 paired and 20 unpaired. Page `9b19159be3098c64`, built on a clean tree. |
| 17 | Noted | — | — | — |

### Batch C: what the hold branch changes beyond the mint

The mint itself made no existing test fail on its counts. Four existing tests failed, reported here before amending (ruling 6):

1. `tests/test_console_specs.py::test_plumb_line_spec_matches_form`, `::test_plumb_line_ttl_writer` and `::test_plumb_line_null_modality_is_silence`. The plumb-line form is built from live `data/loci.ttl`, so a new Locus adds rows. They are amended on the hold branch exactly as Batch B amended them (`d704ef7`): the ids gain `baptism-instrumentality`, the titles gain "33e", Position rows go 23 → 25, locus rows 11 → 12, Holdings 21 → 23, holds 21 → 23, tiers 10 → 11. `check_against_form` was already a subset check, so no builder code changed.
2. `tests/test_italic_spans.py::test_hand_minted_real_counts` expected 9 hand-minted references on p. 914 and got 15. The cause is in the tool, not the test: `tools/italic_spans.hand_minted` summed cites per Argument, and the four Gill (b) Arguments repeat the cites of 018-021. The tool now counts each (locator, reference) pair once. That gives 56 in all and 9 on p. 914, on both the old and the new data. **That test is not amended.**

Suite on the hold branch: 907 after the mint (896 + 11 born), 909 after statements-2 (+2 born). Ingest 0 violations, 1 warning (the tier). Weigh `b5ad57ea0df3` / `6a2ffd426bf9`, unchanged. `data/plumb-line.ttl` unchanged.

### A spec error of mine

The mint spec gave `gc:resolutionNote` with `@en`. The SHACL shape wants a plain `xsd:string`, and ingest refused it. The implementer wrote a plain string, which is right. The data is correct; the spec was wrong.

## Scores

**LOCK_merge_adr3_r3:** M1-M5 held. **M6 missed:** the sitting-2 page's build16 moved from `b7c9ffb0096a4522` to `18a4a13dfeffb6e9`. The R3 merge changed one help sentence ("this site's standard"), which the lock did not foresee. The statements page kept `0894df4edd1fe4b1`, as predicted.

**LOCK_italic_console:**
- C1 held: suite 896, no existing test amended.
- C2 held.
- **C3 partly missed:** 5 short bands, within the "at most 6". But 4 bands fall outside 5-7 lines: s14 has 3, s29 and s30 have 4, and s38 has 9, because its span covers 5 lines.
- **C4 missed as worded:** `crops.json`, `draw.json`, the 40 PNGs and the page's build16 are identical across runs. The input spec is not byte-identical, because it holds the run's image paths and the run header.
- C5 held.
- C6 held: page `9b19159be3098c64`.

**LOCK_batchC_unit:**
- U1-U7 held: Locus 13, warnings 1; Position and answers 26, excludes 10; Argument and supports 115; Passage 161; the rest unchanged; weigh and plumb-line unchanged; ingest 0/1.
- **U8 missed:** three existing tests needed amending. The lock's own fallback applied (reported, then held on a `hold/` branch). The lock should have foreseen this from Batch B, which amended the same three tests for the same reason. Its base total (875) was also stale: it was 896 by then.
- U9 and U10 held (born tests).

**LOCK_statements2:**
- S1 and S2 held (born tests).
- S3 held: `f3f1af17d9075ba5`.
- S4 held: suite 909, no existing test amended, no `data/` change in that commit.

**LOCK_replay_held:** H1-H6 held. Suite 912 (896 + 16 born), no existing test amended. With the empty bindings file, `data/plumb-line.ttl` is byte-identical (`bfb0238c`). Ingest 0/0. Weigh `b5ad57ea0df3` / `6a2ffd426bf9`. One wording choice by the implementer: the held line reads `held for <target>, not yet in the data: <target> (<row ids>)`, one line per target.
