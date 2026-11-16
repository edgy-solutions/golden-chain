# Report 18: the ruling on report 17, worked

- **For:** the architect, through Chris.
- **Ruling:** [RULING_report_17.md](RULING_report_17.md), filed verbatim with Chris's statement beside it.
- **Branch:** `phase-0`, pushed through this report's commit.

Every item of the ruling was applied. I stop here: Q-2's finer measure is proposed (§4) and waits for ratification before its lock and code.

## 1. The disclosure, recorded

- **Audit standoffs beside both signed records** (neither record edited):
  - [AUDIT_q11_crops_58b603f5500ae2a8.md](AUDIT_q11_crops_58b603f5500ae2a8.md): both Q11 rows are **model-proposed, signed by Chris**. They stand for the gutter lock only. They are never to be described as blind, or cited to goat-yard as satisfying sign-from-pixels unaided.
  - [AUDIT_truthset_italic_8afafecd34665b14.md](AUDIT_truthset_italic_8afafecd34665b14.md) A-3: w017 was viewed by a model before signing, and is held out of every denominator. A-4 lists the clip-noted rows held out of the measure's precision.
- **Chris's statement** is carried verbatim in both: "I asked the questions because the consoles are criptic and I needed help understanding waht was being asked not to get the answers - the answers are mine once I understaood what was being asked".
- **Dated notes:**
  - reports 13 (p. 912), 14 (Q7) and 15 (Q7) each get a note at their "no model" statement;
  - report 16 gets a note at F-4 (see §3).
- **Standing rule:** [RULES.md](../RULES.md) rule 11, and [ADR-0006](../adr/0006-signing-console.md) Revision 3 §2.
- **Gutter finding:** [gill-column-rule.md](../sources/gill-column-rule.md) records "side hit, cause missed" on p. 913 and the **third cause** (footnotes at a column foot). It is closed.
- **ADR-0006:** Revision 2 is marked ratified; `--code-at` is recorded as accepted.

## 2. Q-1: clip-noted rows held out; the clear-edges check

**The 10 clip-noted rows**

| Row | Stratum | Slant | Signed |
|---|---|---|---|
| w017 (also model-viewed) | slanted | 0.20 | roman |
| w019 | upright | 0.00 | roman |
| w041 | slanted | 0.20 | roman |
| w043 | upright | −0.10 | roman |
| w067 | slanted | 0.29 | italic |
| w154 | slanted | 0.20 | roman |
| w166 | slanted | 0.12 | roman |
| w172 | slanted | 0.20 | roman |
| w182 | upright | 0.02 | roman |
| w193 | edge | — | roman |

**The clear-edges build check** (ADR-0006 Revision 3 §1):
- An image may carry `clear_edges`. Build fails if ink touches a listed edge.
- Ink is set by a mode-midpoint threshold per crop.
- Word crops of any future draw carry it on top and bottom, cut from a vertically padded line box.
- Lock: `clear-edges-predictions-locked.txt` (2026-11-16T03:40:24Z). CE1–CE3 all hit:
  - CE1: 565 passed, which is 554 plus 11 new tests;
  - CE2: the real truth-set and re-ask specs pass `check_spec` and `hash_images`; the template is unchanged; `TEMPLATE_VERSION` is 5;
  - CE3: weigh is byte-identical and no data changed.

## 3. Q-2: SI3 and F-4 restated

SI3 as locked stays **missed** (65/76). It is not edited. The restated figures are second figures beside it, not a conversion of the miss.

**Holding out w017 only, or w017 and the clip-noted rows**

| Measure | As signed (all 196) | w017 held out (195) | w017 and clip-noted held out (186) |
|---|---|---|---|
| slanted → italic (SI3, ≥ 90 %) | 65/76 = 85.5 % | 65/75 = 86.7 % | **64/70 = 91.4 %** |
| upright → roman (SI4) | 80/80 | 80/80 | 77/77 |
| edge → roman (SI5) | 34/40 = 85.0 % | 34/40 | 33/39 = 84.6 % |

**F-4 restated** (slanted stratum, w017 and the clip-noted rows held out):
- **At 0.20:** 36 italic and **6 roman** (was 10 roman).
- **At 0.25 and above:** 28 italic and 0 roman.
- **The 0.12 word** (w166) is clip-noted, so it is held out.
- **All 6 remaining disagreements measure 0.20:** w064, w101, w104, w107, w123 and w137.
- **Correction to report 16:** the count at ≥ 0.25 was 29, not 30, before holding out. A dated note is in report 16.

**The block-opening reading mostly dissolves.**
- In report 16, 5 of the 11 disagreements sat on the first line of their OCR block.
- With the clip-noted rows held out, only 1 of the 6 does. 4 of the 5 were clip-noted.
- A block's first line is where a crop cut at the OCR box is most likely to clip ascenders. That cause is now the more likely one, and the reading is a hint, not a finding.

**What stands:** the italic call at 0.20 is the soft step (36 italic against 6 roman); from 0.25 up it is exact on this set. Per the ruling, nothing is tuned on this set.

## 4. Proposed: the finer measure (for ratification; lock and code after)

1. **Sub-pixel shear.**
   - `gy_word_slant.shear_score` rounds each sheared ink pixel to an integer column (`np.rint`). This gives F-3's comb.
   - Proposed: split each pixel between its two neighbouring columns by linear weight, so the score is smooth in the shear.
   - The grid (−0.20 to 0.50, step 0.01), the edge abstention and `MIN_INK` are unchanged.
2. **Ink by mode-midpoint per crop**, in place of the fixed `INK = 128` (goat-yard law: mode-midpoint thresholds). The rule is the same as clear-edges.
3. **The measured box:** the word's OCR box horizontally, and the line box vertically. Ascenders and descenders that the word box clips are then measured.
4. **A new draw:**
   - a new salt (`truthset-v3/`), the same per-page strata as v2 (4 slanted, 4 upright, 2 edge), and none of v2's 196 keys;
   - the strata come from the new measure;
   - console word crops are cut from the line box padded vertically, with `clear_edges: [top, bottom]`;
   - a crop that fails the check is re-cut once with double padding, or dropped. Both are counted.
5. **The lock** is written before any code. Predictions:
   - slanted → italic ≥ 90 %;
   - upright → roman ≥ 97 %;
   - edge stays an abstention, with no prediction of its split;
   - the comb is gone: no empty bin between two full ones in the slant histogram at 0.02 bins;
   - two clean runs are byte-identical;
   - clear-edges failures after the re-cut: ≤ 5 % of the drawn rows.
6. **Signing:** the sitting runs under rule 11. Every question has a plain-words help entry, so the form's text answers how it works (see Q-2 below).

## Questions

- **Q-1 (architect).** Ratify §4, or amend it. On ratification I lock, then build, then run twice on a clean tree.
- **Q-2 (architect).** Chris finds the consoles cryptic: he needed help with what was being asked. That is how crops reached a model. I propose:
  - every console gets a "What this asks, in plain words" entry per question, with what each option means;
  - a build check fails a field whose question has no such entry.
  - Rule 11 then has the text it relies on.
- **Q-3 (Chris).** Was any other row of any sitting shown to a model (empty strips, WCF 1647, plumb-line, Q11, the truth-set)? The ruling asks you to confirm.

## Consoles waiting for Chris

1. **The p. 914 re-ask `d7a6aab0734ffe3e`.**
2. **The follow-up `eb961ddb1e582ed6`.**

Both are under rule 11. If a question is unclear, ask the build agent, who answers from the form's text and never reads a crop.
