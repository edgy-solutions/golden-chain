# Report 15: the rulings on report 14, worked

- **For:** the architect, through Chris.
- **Ruling:** [RULING_report_14.md](RULING_report_14.md), filed verbatim.
- **Branch:** `phase-0`, pushed through this report's commit (after `1f5e8a0`).

Every item of the ruling was worked. Each count was locked (chmod a-w, under `~/.golden-chain/`) before its code or data existed. **No prediction missed.**

- **Full suite:** 540 passed.
- **Weigh output:** only the Apology's block changed (Q2). Members are now `71c14a5d187d…` and officers `c8fe9e910b5a…`.
- **Measurement runs:** every one ran on a clean tree, was run twice, and gave byte-identical outputs.

I stop here: three consoles wait for Chris, and Batch C waits on F-B and two questions below.

## What was done

| Ruling | What | Commit | Lock: result |
|---|---|---|---|
| W-1, F-1–F-3 | Accepted; recorded | `9836117` | — |
| Check before signing | The follow-up console did **not** ingest under R1 (details below this table). It is rebuilt as **`eb961ddb1e582ed6`** | `961ad68` | — |
| Q1 | Belgic XXXIV p. 425 fn3 is left out of instrumentality (a). It is recorded in [heidelberg-belgic.md](../sources/heidelberg-belgic.md) as a phase-2 source for 23b-yes and sign-of-the-covenant. 1 Pet 3:21 enters (a) only by an efficacy clause (p. 426 fn4; Harbaugh Q.72) | `9836117` | — |
| Q2 | Apology IX, read on the page (details below) | `37724cf` | AP1–AP6 hit |
| Q3–Q6 | Recorded: R1 (a)–(c) confirmed; no OCR rerun; the CCEL row kept; sign first | `9836117` | — |
| Q7 | The truth-set signing console, built as its own console (details below) | `1f5e8a0` | TC1–TC7 hit |
| Then | Batch C counts locked and held (details below) | — | C1–C6 held, not run |

**The follow-up check in detail:**
- `c89256e734a61e4f` was built on template v3. It read a modality left empty as "silent", and said so in its status line and in the ingest record.
- R1 §6 requires an empty modality to be unanswered, with `silent` removing the Holding only when chosen.
- Console v4 (`961ad68`) renders an empty modality as unanswered: "N left empty, unanswered (earlier answers stand)".
- A new help entry, "What if I leave a modality empty, or choose silent?", says that an empty answer leaves the earlier answer standing and that `silent` removes it.
- v3 specs still check and render their old wording, so the replay of sitting 1 is unchanged byte for byte.
- An end-to-end test checks the merge: an empty modality's Holding stands; a chosen `silent` removes its Holding.
- The rebuild `eb961ddb1e582ed6` has the same images and rows as before. All 9 modality fields are `unanswered`. It is not provisional.
- `README_WHICH_TO_SIGN.txt` beside it marks `c89256e734a61e4f` as superseded.

**Q2 in detail:**
- The Triglot pp. 244–245 were read on the page images.
- Apology IX condemns the rejection of infant baptism. The Latin §52 has "damnamus". §53 has "impie sentiunt, qui damnant baptismum parvulorum". The English on p. 245 says the same.
- Minted: `holding/apology-1531/baptism-subjects/professing-believers-only`, forbidden.
  - Locator: "Art. IX §52-53 (Triglot p. 244, Latin; p. 245, English)".
  - Status: proposed. It has no Argument, because the condemnation cites no Scripture.
- Apology now walls on subjects, with Augsburg's line. Its cost is 1.0000 over 1 locus, and its coverage is 0.2857.
- Lock: `r14-q2-apology-ix`.

## Q7: the truth-set console

- **Build:** `8afafecd34665b14`, template v5, not provisional. Two builds gave the same hash and identical HTML.
- **Location:** `~/.golden-chain/console/truthset-italic/build1/` (local; never committed).

**Rows**
- The 196 words come first, in an order set by sha256("truthset-v2-console/" + key). This is a new salt: it is not the draw's order, and it is not by page.
- Each word row shows the word crop as the OCR cut it (its size is exactly the bbox size). Under it is the printed line (the union of the line's OCR boxes, padded 12 px) with the word boxed in magenta.
- Each word row asks "italic", "roman" or "other, as written" with a short note.
- Next is the p. 912 left column (the whole region). It asks "italic throughout", "roman throughout" or "mixed", and "What is this column? (in your words)".
- Last is the CCEL row: "The small type at the foot of p. 914 left: column footnotes?" (yes / no). The image runs from 30 px above the first word of the CCEL-moved blocks down to the foot of the column.

**Keyboard**
- `i` is italic and `r` is roman. Each records the answer and moves to the next row.
- `o` is other: it focuses the note, and Enter moves on.
- Backspace or ArrowLeft goes back one row; ArrowRight goes forward.
- A key does nothing on a row whose question lacks that option.
- All 198 rows are on one page.

**Blind**
- No row carries a stratum, a slant value, or any OCR text.
- On the real spec, a search finds no "slanted", "upright", "edge", "slant" or "stratum". The one `"text"` is the kind of the p. 912 "what" field.
- No model has viewed any of the crops.
  *Dated note, 2026-11-15 ([RULING_report_17.md](RULING_report_17.md)): this statement is corrected, not rewritten. The architect, a hosted model, disclosed that it viewed the Q11 crops (p. 913 slab 16, p. 915 slab 5) and truth-set word w017 before signing, and the p. 914 foot crop after signing. Chris confirms whether any other row was shown to a model.*

**Locks:** TC1 198 rows; TC2 394 images; TC3 blind; TC4 0 rows off in crop size or box; TC5 crops.json and all 394 PNGs byte-identical over two clean runs (`truthset-console-2026-11-14-{a,b}`), with one build hash; TC6 3.2 MB; TC7 the headless keyboard test.

**Ingest:** `--write` writes `docs/handoff/SIGNED_truthset_italic_<build16>.md`. It holds a table of id, key and answer, then the two page rows, and no text or images.

## Batch C: locked, held

- **Lock:** `step3-batchC-predictions-locked.txt` (2026-11-14T21:06:23Z). Its base is the tree after `37724cf`.
- **Sources:**
  - Harbaugh Q.65 and Q.69–73: 25 references.
  - Belgic XXXIII and XXXIV: 8 admitted notes, 24 references.
  - Gill "Sixthly", for (b): 4 references.
- **The same in either case:** Locus 12 → 13; tier warnings 3 → 4; 19 new Passages (142 → 161), all from the (a) side; 7 new SourceDivisions; Holdings unchanged; weigh byte-identical.
- **If F-B = (b):** Positions 24 → 26, and excludes 9 → 10.
- **If F-B = (a):** see Q-C2.

## Questions for the architect

- **Q-C1: which Argument unit for Batch C?**
  - Ruling 16 says "an Argument cites one note of one division", as `belgic-confession/34/001` does. That gives variant N: Belgic 8, and 117 Arguments in all.
  - PLAN_step3 says "one Argument per passage per position". That gives variant P: Belgic 24, and 133 Arguments in all.
  - Harbaugh (25) and Gill (4) are the same under both.
  - Both variants are locked. Which applies?
- **Q-C2: if F-B comes back (a), what is minted?**
  - The lock's C3 mints only the Locus, Position (a) and its Arguments (Position 25; Arguments N 113 or P 129).
  - (b)'s wording, Gill's 4 and the excludes edge would stop for a ruling.
  - Confirm, or rule otherwise.

## Consoles waiting for Chris

1. **The follow-up console `eb961ddb1e582ed6`** (`~/.golden-chain/console/plumb-line-followup/`). Do not sign `c89256e734a61e4f`, which is superseded. Batch C waits on its F-B answer.
2. **The Q11 crops console `58b603f5500ae2a8`.**
3. **The truth-set console `8afafecd34665b14`** (`~/.golden-chain/console/truthset-italic/build1/`): 198 rows in one sitting.
