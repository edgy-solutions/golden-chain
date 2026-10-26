# Sign-off: empty strips and the run-2 abstentions (from pixels)

For: Chris. Fill this in from the strips themselves, in one sitting. No model has viewed these images, and none may.

**You sign the line-height-matched strips** (ruling on report 6, Frame: "The line-height-matched scale governs. Rerun at the scale that puts median line height nearest 55 and inside 49-61; the 0.703 run stays on record. Cut the (fixed) strips from that run."). The native crop beside each one is there to read from. The strips at 0.703 (3585 × 5377) and at native 5100 × 7650 are superseded; both runs stay on record.

- **Strips:** `C:\Users\cnogr\.golden-chain\gy-locate-column-rule-scale6.947-2026-10-25\strips-for-signing\`.
  - Each `pNNN-….png` has a `pNNN-…-native.png` beside it.
  - The run is **clean** (golden-chain `6a7c5d1`, truth-set form §7).
  - **Raw page pixels** (ruling on report 6, signing strips): "no thresholded content in signing strips. They are raw page pixels plus a drawn overlay of the run's result." Each run strip is 8-bit grey as rendered; each native crop is the embedded 1-bit image.
- **Frame for every row number below:** scale 6.947, **3002 × 4502 px**. Line height is 48–58 px by page (pooled median **55**, pitch 67).
  - A native row is the frame row × 1.6992. Native is 5100 × 7650, line height about 90.
- **Legend:** `README.txt` in that folder. The overlay is drawn over the pixels; the console lets you hide it.
  - Green ticks mark the strip boundaries: 700, 1000, …, 4000.
  - Magenta marks y_end = 4202.
  - Red marks the cluster centre the run found in each strip; blue dots mark the fitted band edges.
  - **The last strip is a partial one, 4000–4202 (202 rows).**
- **Background:** [../sources/gill-column-rule.md](../sources/gill-column-rule.md), § "Rerun at scale 6.947".
  - The numbers there support only; the pixels decide.

Write over the `__` blanks, or sign in the console built from this form (ADR-0006, proposed).

## H1: p. 896 is a chapter opening (`p896-gutter-full.png`, beside it `p896-gutter-full-native.png`)

The run finds strips 700–1900 empty (five strips; peak column ink 0.19–0.41) and strips 2200 onward ruled.

1. Is there a chapter head spanning both columns at the top of the body? __ (yes/no)
2. Row where the column rule starts (nearest green tick): __
   - H1 predicted 3400–3700 native, which is 2001–2177 in this frame.
   - Two numbers are on file, both from earlier runs and in native rows:
     - a continuous ruled run from about 3550 (2089 in this frame);
     - a 47-row ruled run near 3059 (1800 in this frame), the "numeric miss". It came from the cutter's threshold measure, since withdrawn.
3. Between the head and the rule's start, is there two-column text with **no** rule? __ (yes/no; rows __ to __)
4. **H1 (geometry reading: no rule above the chapter opening):** __ (confirmed / refuted). If refuted, what occupies the rows above the rule's start? __

The architect's wording (ruling on report 5, Q5):

> if the pixels refute the geometry reading of H1 (no rule above the chapter opening), OCR stays held and the architect rules. H1's numeric miss (F=3059) does not by itself refute the geometry reading.

## The last strip: what inks the gutter in 4000–4202? (`p896-foot.png`, `p902-foot.png`, `p907-foot.png`, `p908-foot.png`, each with its `-native.png`)

The foot strips cover rows 3400–4501. In the partial last strip the run finds column-ink peaks of 1.00 (896), 0.98 (902), 0.91 (907) and 1.00 (908). The strip is ruled on all four pages.

Two readings are on file. Your reading decides.
- **The architect's locked hypothesis:** the peaks are "the inked edge of justified text (left edge of the right column's stems) or footnote text inside the ±300 px window after the rule ends, not a faint rule".
- **The numbers:** an earlier measure (at scale 7.2) put the rule's end at 7135–7170 native on these pages, which is 4199–4220 in this frame: at or just below y_end. If so, the rule covers nearly all of the last strip.
- **The architect's ruling (report 6):** "if the pixels show the rule itself ending above the foot, my locked hypothesis is refuted, record it, and no request file is needed (no abstention). Chris decides."

| Page | Row where the rule ends | Does it run to the text foot? | Faint near the foot? | What inks the gutter in 4000–4202: rule, justified-text edge, footnote text, catchword, signature mark, other page furniture? |
|---|---|---|---|---|
| 896 | __ | __ | __ | __ |
| 902 | __ | __ | __ | __ |
| 907 | __ | __ | __ | __ |
| 908 | __ | __ | __ | __ |

5. **The locked hypothesis:** __ (confirmed: text edge or footnote ink / refuted: the rule itself ends above the foot / other: __)
6. **Does the rule stop above the foot on every page?** __ (yes / no: it runs to the bottom and is faint near it, which would mean the goat-yard request file)

## Run-2 abstentions (`p897-gutter-full.png`, `p898-gutter-full.png`, each with its `-native.png`)

| Page | Rule present? | Single? | Note |
|---|---|---|---|
| 897 | __ | __ | __ |
| 898 | __ | __ | __ |

## Signature

Signed __ (name, date, one sitting). After that:
- If H1's geometry reading holds and the rule stops above the foot, the locked hypothesis is refuted and recorded, no request file is needed, and OCR is unheld (the run is clean). Report 5 Q4 (the A2 fixture) goes ahead.
- If the rule runs to the foot and is faint there, the request file "column split: single rule faint at the foot" goes to goat-yard first, with the stored per-strip column fractions. OCR is unheld once that file is written.
- If the pixels refute H1's geometry reading, OCR stays held and the architect rules (wording above).
