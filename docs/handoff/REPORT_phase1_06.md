# Phase-1 report 6 (2026-10-26)

For: the architect.

Covers your rulings on reports 3, 4 and 5 and on ADR-0002 Revision 1, plus the Bible-text note.

OCR stays **HELD**. Chris has not yet signed the recut [SIGNOFF_empty_strips.md](SIGNOFF_empty_strips.md).

## What was done

| Commit | Files | What |
|---|---|---|
| 280adc9 | `tools/column_rule.py`, `tools/gy_locate_column_rule.py`, `tools/signing_strips.py`, `goldenchain/usfm.py`, tests | `--scale` render, with the frame and line height in the header. `--native` crops beside each signing strip. golden-chain `git_start` / `git_end` / `clean_run` in every run header (truth-set form §7). The USFM KJV check against `canon.h`. 38 new tests since report 5 (254 in all; the USFM data test skips when `GOLDEN_CHAIN_BIBLES` is unset). |
| d32f888 | ADR-0002, ADR-0003, `data/loci.ttl`, `westminster.md`, `READING_wcf1647_proofs.md`, `gill-column-rule.md`, `goat-yard.md`, `bibles-usfm.md`, `SIGNOFF_empty_strips.md` | Rulings applied (below). Reruns at 7.2 and 0.703 recorded against their locks. Strips recut. |
| (this commit) | this report, `HANDOFF_phase1.md`, `SIGNOFF_empty_strips.md`, `gill-column-rule.md`, `goat-yard.md` | The clean rerun recorded; the form points at the clean strips. |

## Rulings applied

| Ruling | Done |
|---|---|
| ADR-0002 Revision 1 ratified | Status line: ratified, subject to goat-yard's sign-off on (a) the kjv segment, (b) the reserved Anchor, (c) locations only. "Pending GY form" is replaced by a citation of `docs/forms/TRUTH_SET_FORM.md` v1. Rule 5 gains the second-v11n paragraph (a mapping table to kjv, with its own provenance line, born with the first non-kjv Passage). |
| Report 3, Q2 | ADR-0002 has a new section on existing `gc:` properties and standard terms: `paginationOf`, `quotationCheckedAgainst`, `pages` (`bibo:pages` considered), `locator` / `secondaryLocator`. Nothing migrated. |
| Report 4, Q5 | Mirror shapes kept. No change. |
| Report 4, Q7 | ADR-0003 Revision 1 readings (a)(b)(c) marked confirmed. |
| Report 5, Q1 | `loci.ttl` comment: 33a–c are one family; the notation is a display label, the slug is the identity. No triple changed. |
| Report 5, Q2, Q6 | No change needed. |
| Report 5, Q3 | Both phase-2 candidates are in the handoff, in your order. Neither is read. |
| Report 5, Q5 | Your wording is in the sign-off form verbatim. |
| Report 5, Q7 | `westminster.md`: Tyler is the witness of record; London 1647, if found, is a second witness, and differences are findings. |
| Report 5, Q8 | Three rows added to the reading form (1 Cor. xii. 13; Tit. iii. 5; Mark i. 4). They become Arguments for the composite 33a Position once read and signed. No TTL yet. |
| SCALE 1–3 | Done; results below. Strips recut with native crops. |
| SCALE 4 (Q4, OCR) | Waiting, as ruled. |

## Scale: results

Every px is in the frame named beside it. The full tables are in [../sources/gill-column-rule.md](../sources/gill-column-rule.md).

| Run | Frame | Line height | Result against its lock |
|---|---|---|---|
| Native (pin run, on record as "made at the wrong scale") | 5100 × 7650 | 90 (81–98) | — |
| Scale 7.2 (goat-yard step 2) | 3111 × 4666 | 57 (49–61) | R1–R4 held. **R5 missed**: 235/240 strips, not 233. My strip mapping was wrong. |
| Scale 8.2963 = 0.703 (your ruling) | 3585 × 5377 | 64 (57–68) | **A1, A2 held**: 20/20 ok, max residual 9.8 px. D2, D3 held. **D1 missed** (W 3585, not 3584: rounding). **D4 missed**: 15 strips, not 14, because goat-yard keeps the 177-row partial last strip. D5's totals follow from D4; the empty set on 896 matched. |

- **Your step-1 prediction missed.** You predicted a native line height of 70–85 px. The measure is 90 (81–98), taken before the lock.
- **The runs were first provisional** under goat-yard's truth-set form §7: they were made from an uncommitted tools tree, with no golden-chain git state in their headers.
  - The tools now record `git_start`, `git_end` and `clean_run`.
  - After committing (`d32f888`), I reran all five (two tools at two scales, plus the strips), locked first (C1–C3).
- **The reruns are clean,** and the measurements are identical: `pages`, `ruled_rows.json`, and all 14 strip PNGs byte for byte.
- **C3 missed on the letter.** The gy headers' `prediction` text changed because I passed the new lock's reference. No measurement is affected.
- **Chris signs the strips from the `-clean` folder.**

## Questions

1. **Which frame governs?** Three instructions point three ways:
   - your ruling: 0.703 of native, which gives line height 64, outside goat-yard's 49–61;
   - goat-yard step 2: re-render to about 55 px, which is scale 7.2;
   - goat-yard's truth-set form §6.1: "Native page pixels, one convention, and the page size stated in the record (vol.1: 3584 × 5400). No consumer rescales silently."
   I followed your ruling for the strips Chris signs. Both runs pass goat-yard's criteria. The question matters for any request file's numbers, which must be in one frame (gutter: 80 px at 7.2, 92 px at 0.703). Should goat-yard be asked?
2. **The last strip.** Your locked hypothesis is that the peaks are a text edge or footnote ink, not the rule.
   - The numbers lean the other way. A threshold at the midpoint puts the rule's end at 5016–5040 in the 0.703 frame. That covers 0.66–0.79 of the partial strip, against peaks of 0.64–0.76.
   - The same arithmetic fits the native run (0.45–0.57 against 0.44–0.55).
   - So the peaks look like the rule itself, ending above the foot. Chris's reading decides. The form asks him what inks the strip.
3. **A fix to `signing_strips` needs a ruling.** Its RULED threshold (window ink ≥ 2·half_w) sits at the rule-width mode, not at a mode midpoint, so it breaks law 9. Its 50-row run is shorter than one line pitch, so a line of type crossing the gutter passes as rule.
   - That explains p. 907's L = 4528 (fraction 0.141) and p. 896's early F = 2148.
   - A scratch midpoint measure (locked M1–M4) fixed the last strip: M3 and M4 held. M1 missed (m = 4 on two pages) and M2 missed (896 still caught early).
   - Proposed: a threshold of ceil(m/2), with m the page mode, plus a run length of at least 2 line pitches. Lock a prediction, then change the tool with born tests. F and L only support the reading; the pixels decide.
4. **Report 3 Q1: who reads the WCF 1647 pages?** The ruling says I view the pages locally ("PD, no OCR, no hosted model"). I am a hosted model: whatever I view is sent to me.
   - A memory note of 2026-10-25 records your correction that I may view PD page images with local tools, and that the restriction is on sending goat-yard crops to hosted models.
   - The reading form, as approved, says "No model has viewed them, and none may".
   - Until this is settled, I have not downloaded or viewed the pages, and Chris reads and signs. If my viewing is allowed, I fill PROPOSED rows, Chris signs each, and `westminster.md` records who proposed and who signed.
5. **Report 4 Q6: the Gill provenance wording is held.** The ruling's replacement text says "read from the BSB text layer". The BSB pages have no text layer: one CCITT image per page. The readings came from local Tesseract OCR of page renders, made before the OCR hold.
   - Proposed instead: "read from local OCR of the BSB page renders (made before the OCR hold) and CCEL; to be signed from pixels".
   - Predicted change: 3 lines in `data/gill-body-of-divinity.ttl` (10, 183, 269), and 0 status changes (all are already `proposed`).
6. **The Bible note names no path.** The instruction was to record the Bibles at "<corpus path>/dr-voluminous/bibles". The standing rule is that the private corpus is never named in committed docs.
   - [../sources/bibles-usfm.md](../sources/bibles-usfm.md) says "goat-yard's private corpus, under its `bibles` directory", read through `GOLDEN_CHAIN_BIBLES`.
   - Confirm, or rule that the name may appear.
7. **The ADR-0002 citation.** `TRUTH_SET_FORM.md` v1 is on goat-yard's branch `apparatus-next` (commit `a0a30d4`), not at `substrate-v0`. The ADR cites it by commit. If it should wait for a tag, say so.

## Bible text

- No Bible text is stored or fetched. The repo holds only the `canon.h` versification table.
- **The USFM KJV check held:** 66 books, 1,189 chapters, 31,102 verses, 0 differences, 0 bridges, locked first.
- **The source note is [../sources/bibles-usfm.md](../sources/bibles-usfm.md):** KJV (1769 standardized text, eBible.org, PD), Hebrew (Masoretic), Greek (TR). All three are read-only, private, by configured path.
- ADR-0004, when written, names the USFM KJV as the display text source.

## Next on "continue"

1. When Chris signs the recut sign-off form, apply the outcome. If it is clear, prepare the A2 fixture (Q4) and unhold OCR.
2. Apply the rulings on Q1–Q7 above.
3. When Chris (or I, per Q4) fills the WCF reading form, lock the counts, then record `gc:asPrinted` and split the Arguments.
