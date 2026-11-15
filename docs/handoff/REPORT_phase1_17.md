# Report 17: the Q11 sitting, the p. 914 crop fault, and a new console check

- **For:** the architect, through Chris.
- **Branch:** `phase-0`, pushed through this report's commit. Before it: `0a96672` (Q11 record and the audit) and `11a905f` (console code).
- **Full suite:** 554 passed.
- **Weigh:** byte-identical (`71c14a5d187d…`, `c8fe9e910b5a…`). No `data/*.ttl` changed.

I stop here. One console waits for Chris (the p. 914 re-ask), and the follow-up still waits. There are three questions below.

## 1. The Q11 sitting (`58b603f5500ae2a8`)

- **Signed by:** Chris, 2026-11-15.
- **Record:** [SIGNED_q11_crops_58b603f5500ae2a8.md](SIGNED_q11_crops_58b603f5500ae2a8.md).
- **Lock:** `q11-signed-58b603f5-predictions-locked.txt` (15:59:55Z).

| Lock | Predicted | Result |
|---|---|---|
| QS1 | ingest passes every check | **missed on the first try** (details below) |
| QS2 | records written; no data change; weigh identical; suite 540 | records, data and weigh hit. **Suite count missed:** 554, because 14 tests (`--code-at` and this report's check) were added after the lock |
| QS3 | p. 913: left has a head, a blank line or a short line; right is full-measure | hit. Left: "a short line" and "something else" |
| QS4 | p. 915: as QS3 | hit. Left: "a section head" |

**The QS1 miss.**
- Ingest refused with "console code changed since build". The console was built at `dbf592c`, on older console code.
- The fix is `ingest --code-at COMMIT` (`785d7d6`). It reads the console code from the commit the manifest names, and only if that start was clean (ADR-0006 item 8: "recomputed from the spec, the code and the image files").
- Its lock `ingest-code-at-predictions-locked.txt` (CA1–CA5) all hit. The record says "console code read from commit dbf592c… (--code-at)".
- The follow-up `eb961ddb1e582ed6` will need the same flag.

**Against the gutter-maxima lock (2026-11-01).**
- The lock said: "a section head or a blank line on one side; that side is the left in both". Its refutation condition, full-measure on both sides, is not met.
- **p. 915:** a hit. The left is a section head.
- **p. 913:** the side is right (left), but the content is not what the lock named. Chris's note says the left white comes from "four short footnote lines, notes 24–27, small type; … both columns are in the footnote zone here … not a section head or blank line".
- The lock named the side correctly and the cause wrongly on p. 913. I record it as **side hit, cause missed**.

**Bearing on F-1.** p. 913's note is a pixel-signed sighting of numbered small-type footnotes at a column foot, on the page before p. 914. It supports F-1's reading. It does not confirm it for p. 914; the re-ask below asks that.

## 2. The p. 914 foot: a crop fault, not a "no"

- **Chris's direction (2026-11-15):**
  - his note "I might be wrong - can see the rest of the page" means "cannot";
  - the crop did not show enough to judge. It began 30 px above the small type, with no body text above for comparison and no note number in view.
- **The signed record stands as signed.** Beside it, an audit standoff (truth-set form §9) gives the row **fault** and says its verdict is **not usable**: [AUDIT_truthset_italic_8afafecd34665b14.md](AUDIT_truthset_italic_8afafecd34665b14.md).
- **Report 16's Q-1 is superseded.** F-1 stands as a finding from numbers, **unconfirmed from pixels**. SI8's miss stays in the record, with the fault beside it.
- **Not evidence:** after signing, a model outside this repo viewed that crop. Its reading is not used anywhere.

**The re-ask console: `d7a6aab0734ffe3e`.**
- **Lock:** `p914-reask-predictions-locked.txt` (16:08:23Z). RA1–RA4 all hit.
- **What it shows:** one row. The image is the whole left column of p. 914 (2480 × 6600). Its sha256 equals the OCR run's input.
- **Overlay:** a magenta box from the measured boundary (y = 6127) to the foot. "show overlay" hides it.
- **Question:** "The small type at the foot of p. 914 left: column footnotes?" with yes, no, or "other, as written".
- **Build:**
  - fit to window, with zoom;
  - not provisional; 0.5 MB;
  - two builds gave the same hash and byte-identical HTML;
  - built on the clean tree at `11a905f`.

## 3. A new console build check (ADR-0006 Revision 2, proposed)

- **Chris's rule:** "a crop offered for a 'what is this region' question must include enough of its surroundings to answer it."
- **The check:** a row may carry `region_question` (the image, the region, the crop box and the source size). Build **fails** unless the crop shows context of at least max(region size, 300 px) on each side, unless the crop reaches that edge of the source.
- **Against the old p. 914 crop:** it fails: "lacks context above: 30 px shown, 473 needed".
- **Scope:** rows without the block are unchanged.
- **Status:** written as **Revision 2, proposed** in [ADR-0006](../adr/0006-signing-console.md), for ratification.

## 4. A correction to report 16's F-4

- **The defect:** the Markdown renderer at `c4c12ca` dropped row notes. F-4 read the 11 disagreements without them.
- **What the notes show:**
  - 17 word rows carry a note: 10 about a clipped crop and 7 about hyphenation.
  - **5 of the 11** "slanted, signed roman" words carry a clip note: w017, w041, w154, w166 and w172.
- **What this changes:** part of SI3's shortfall may be a crop cause, not a measure cause. F-4's 0.20 reading is weaker than stated.
- **Where the notes are now:** the renderer prints notes (`11a905f`). The committed record is not rewritten; the notes are in the audit standoff.

## Questions

- **Q-1 (architect). Clipped crops in the score.**
  - Five disagreements are clip-noted, and so are five other rows.
  - Should a clip-noted word row count toward a measure's score, or be held out as a fault-like row?
  - My proposal: hold them out of the measure's precision, list them, and re-crop on any future draw with the line box padded vertically. The clip notes suggest the line crop cuts ascenders and descenders.
- **Q-2 (architect).** Report 16's Q-2, the italic measure, is still open. It now reads with Q-1: on the 6 remaining disagreements, F-4 rests on fewer words.
- **Q-3 (Chris).** The p. 915 note reads like advice pasted from a chat ("If you want to be thorough, add in the note: …"). The radio answers stand as signed. Did a model view the p. 915 crop? If so, the record should say so, as it does for p. 914.

## Consoles waiting for Chris

1. **The p. 914 re-ask `d7a6aab0734ffe3e`** (`~/.golden-chain/console/region-reask/build1/`). One row.
2. **The follow-up `eb961ddb1e582ed6`.** Batch C (variant N) waits on its F-B answer.
   - At ingest it needs `--code-at` with the commit its manifest names.
   - The truth-set sitting was signed "Chris Nograd". Please check the name on this one.
