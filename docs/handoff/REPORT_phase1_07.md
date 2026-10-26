# Phase-1 report 7 (2026-10-25)

For: the architect.

Covers your reply to report 6: the signing console (blocking item 2) and the rulings on the frame, the last strip, the signing strips, the Gill wording and the Bible check.

**Blocking item 1 did not reach me.** It arrived as `<snipped>`. Please resend it. Nothing below acts on it. Your note on the signing strips ("If the current cutter thresholds, that may be the bug in item 1") suggests it concerns the cutter, which is now fixed (below).

OCR stays **HELD**. Chris has not signed yet.

## What was done

| Commit | What |
|---|---|
| 6a7c5d1 | The signing console, [ADR-0006](../adr/0006-signing-console.md) (proposed): `tools/console/` (build, ingest, template, three spec builders), 49 tests. The raw-pixel cutter. The report 4 Q6 wording. The WCF page-head finding. |
| fd44eaa | The rerun at 6.947 recorded against its lock; the sign-off form recut for those strips. |
| eddbff3 | A fix to the empty-strips spec builder, found at the first real build (below). |
| (this commit) | This report and the handoff. |

Tests: 301 pass with `GOLDEN_CHAIN_BIBLES` set (300 and 1 skip without it). Ingest: 0 violations, 9 warnings.

## Rulings applied

| Ruling | Done |
|---|---|
| Frame | s0 = 7.2 × 55/57 = **6.947**, locked first. Its median line height is **55.0**, inside 49–61, so it governs. No further render was made. Clean at `6a7c5d1`; all six clauses L1–L6 held. The 0.703 and native runs stay on record. [gill-column-rule.md](../sources/gill-column-rule.md), § "Rerun at scale 6.947". |
| Signing strips | `signing_strips.py` cuts raw page pixels (8-bit grey; the native crop is the embedded 1-bit image) and records the run's result as an overlay: strip ticks, y_end, cluster centres, band edges. It computes no ruled-row measure. The old threshold numbers (F, L, ruled fractions) are withdrawn; they stay on record. |
| Last strip | Your wording is in the form. The form's hypothesis choice reads "refuted: the rule itself ends above the foot", and refuting it needs no request file. |
| Report 4 Q6 | Applied: "read from CCEL and the pre-hold OCR (since discarded); to be signed from pixels". 3 lines changed, as predicted. Ingest 0/9. |
| Report 6 Q4 | I viewed the WCF 1647 leaves (Internet Archive, PD) and proposed the 15 proof strings. I did not view the goat-yard crops or the signing strips. |
| Bible check | Accepted; no change. |

## Signing console (ADR-0006, proposed)

- **Built as directed:**
  - one self-contained HTML per sitting, with every image inline as a data URI and its sha256 beside it;
  - a CSP that allows no network; no external script, style or font;
  - controls per row, including a click on the image to record a page row;
  - typed non-verdicts (`abstain`, `fault`);
  - Export, which writes the build hash, the run header and every image sha;
  - a warning on close when anything is unexported.
- **The ingest** recomputes the build hash by code written separately from the build, and checks every image against its file. It refuses a provisional build unless `--provisional` is passed.
- **The three instances are built from clean trees**, under `~/.golden-chain/console/<kind>/`. Counts were locked first in `~/.golden-chain/console-builds-predictions-locked.txt` (03:07:31Z); C1–C5 held.

| Instance | build16 | Built at | Images | Rows | Signer |
|---|---|---|---|---|---|
| (i) empty strips | `88d902a181ba64c1` | `eddbff3` | 14 | 12 | Chris |
| (iii) WCF 1647 proofs | `24f26ea83e4d6bc2` | `fd44eaa` | 16 | 21 (15 strings, 3 page-head rows, 3 lettering) | Chris |
| (ii) plumb-line | `e61e4575347277b6` | `fd44eaa` | 0 | 24 (9 loci, 15 Positions) | the architect |

- **Checked headless only.** Each page loads in headless Chrome with status "incomplete; nothing unexported", no script error, and no network request.
  - Earlier, a provisional WCF build was filled, exported and ingested end to end by a script. The ingest refused it without `--provisional`, as designed.
  - Nobody has signed in a browser yet. The trial output is disposable and is not a record.
- **Finding:** the first real empty-strips build failed. Native crops carry `line_h` None ("not measured here"), and the spec builder compared None with an int. The test fixture had no such strip. Fixed in `eddbff3`; the fixture now matches the cutter.
- **ADR ratification cards** come after these sittings, as you directed. Not built yet.

## The WCF 1647 proposals

- **What was read:** 15 strings from IA leaves 23–25 and 54–57 (sha256 in `~/.golden-chain/wcf1647/leaves/SHA256SUMS`).
  - Every row shows its crop and the page head beside the proposal. Each doubt is printed on its row.
  - The Markdown form ([READING_wcf1647_proofs.md](READING_wcf1647_proofs.md)) is the readable statement of the same questions.
- **Finding: the page heads do not follow leaf − 8.** The text runs on across these leaves, so the heads are misprinted:

| Leaf | 23 | 24 | 25 | 54 | 55 | 56 |
|---|---|---|---|---|---|---|
| Head as printed | [13] | (14) | (17) | (56) | (46) | (48) |

## Questions

1. **Item 1.** Please resend it (above).
2. **ADR-0006.** Ratify, change or reject. Two points are open in the ADR:
   - (a) **Plumb-line Holdings need a `dcterms:source`** of class `gc:SourceDivision`. Proposed: one SourceDivision per signed sitting, `B source/plumb-line/sitting-<build16>`, identified by the export's sha256. Also, `B body/plumb-line` is not minted. Until you rule, the plumb-line writer writes nothing to `data/`.
   - (b) **Whole-string confirmation.** For the WCF strings the console offers confirm / correct per row, not one tile per token. A corrected row is recorded as a signed reading, not a pixel signature. Is that enough?
3. **Misprinted page heads.** Cite the head as printed, or the corrected page?
   - Proposed: as printed, with "leaf − 8 gives N" in the note. That is how `westminster.md` and the form now read for 7.5 (14; 16) and 27.1 (46; 47).
4. **Spacing convention.** Proposed: a wrapped line is joined with one space, and all other spacing is kept as printed. The form states this on every row it applies to. Confirm.
5. **WCF 7.6, reading order.** The note runs out of the margin into a full-width foot line. Proposed: the margin first, then the foot line left to right, ending with `Act.15.11.`. Schaff puts Acts second. Chris confirms from the crop. Is the printed order the one to store?
6. **WCF 28.4, "Gal 3.91,4".** That is what is printed; Schaff has Gal. iii. 9, 14.
   - Proposed: store it as printed in `gc:asPrinted`, and cite the Passages Gal 3:9 and 3:14 with a note that the print reads "3.91,4".
   - The alternative is to hold the Passage until you rule.
7. **Notes not on the form:**
   - 28.4 note l (Mark 16.15,16; Acts 8.37,38);
   - 28.1 note a (Mat. 28.19);
   - the 28.5 notes n–q.

   None is keyed to a phase-1 Position as the form stands. Add them, or leave them for phase 2?
8. **"Since discarded" (report 4 Q6 wording).** I confirmed that the pre-hold OCR is gone from the folders the OCR runs wrote to. I did not search the whole machine. Does the wording stand, or should I search first?
9. **Dates written before the convention.** 33 lines in `docs/` carry the calendar date 2026-10-26, which was a UTC date; the local date was 2026-10-25. Lock-file timestamps (with `T…Z`) are not counted.
   - Proposed: leave them as written, as history, the same way lock files are kept, and use local dates from now on.
   - Or rule a one-time correction (a locked count first).
10. **Report 6 Q6 and Q7 were not ruled.**
    - Q6: the Bible note names no path; it says "goat-yard's private corpus, under its `bibles` directory". It stands unless you rule otherwise.
    - Q7 (citing the truth-set form by commit) is moot: Revision 1 is ratified with that citation.
11. **Large per-strip gutter maxima** at 6.947: 277 px on p. 913 and 320 px on p. 915, against medians of 76 and 78.5. The medians are in the band and the run passes. The maxima are not explained. They matter only if a request file goes to goat-yard. Look before Chris signs, or after?

## Next on "continue"

1. When Chris signs the empty-strips console:
   - ingest the export to `SIGNED_empty_strips_<build16>.md`;
   - apply the outcome per the form;
   - if it is clear, prepare the A2 fixture and unhold OCR.
2. When Chris signs the WCF console:
   - ingest it;
   - lock the counts;
   - record `gc:asPrinted` and split the Arguments, applying your rulings on Q3–Q7.
3. On ADR-0006's ratification: the plumb-line sitting (yours), then the ratification cards.
