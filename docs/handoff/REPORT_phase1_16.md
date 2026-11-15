# Report 16: the truth-set v2 sitting, signed and ingested

- **For:** the architect, through Chris.
- **Sitting:** truth-set console `8afafecd34665b14`, signed by Chris on 2026-11-15. The record is [SIGNED_truthset_italic_8afafecd34665b14.md](SIGNED_truthset_italic_8afafecd34665b14.md).
- **Lock:** `~/.golden-chain/truthset-signed-8afafecd-predictions-locked.txt` (2026-11-15T15:49:27Z). It was written before the export was opened.
- **Branch:** `phase-0`, pushed through this report's commit.

**Two predictions missed (SI3, SI8).** They are recorded below; the lock is not edited. SI1, SI2 and SI4–SI7 hit.
- Ingest passed every check: 198 rows, complete, not provisional.
- No data changed. Weigh is byte-identical (`71c14a5d187d…`, `c8fe9e910b5a…`).
- Full suite: 540 passed.

I stop here: both misses carry a question.

## The sitting against the measure

The strata come from `candidates.json` and were never shown on the console.

| Stratum | Rows | Signed italic | Signed roman | Other / none |
|---|---|---|---|---|
| slanted (measure says italic) | 76 | 65 | **11** | 0 |
| upright (measure says roman) | 80 | 0 | 80 | 0 |
| edge (measure abstained) | 40 | 6 | 34 | 0 |

| Lock | Predicted | Result |
|---|---|---|
| SI3 | slanted → italic ≥ 90 % | **missed: 65/76 = 85.5 %** |
| SI4 | upright → roman ≥ 97 % | hit: 80/80 |
| SI5 | edge → roman ≥ 75 % | hit: 34/40 = 85.0 % |
| SI6 | other or unanswered ≤ 19 | hit: 0 |
| SI7 | p. 912 left is not "italic throughout" | hit: "mixed"; Chris: "mostly roman with some part italic" |
| SI8 | the CCEL row: yes | **missed: no** |

## The misses

- **SI3**
  - *Locked:* "of slanted-stratum rows answered italic or roman, ≥ 90 % italic."
  - *What happened:* 65 of 76 (85.5 %).
  - *Why:* see F-4. The 11 false italic calls all sit in the lower part of the high mode.
- **SI8**
  - *Locked:* "the CCEL row: yes (column footnotes; report 14, F-1)."
  - *What happened:* Chris answered **no**: the small type at the foot of p. 914 left is not column footnotes.
  - *Why:* F-1 was a reading from numbers only (position, type size, and the CCEL endnote stretch). The pixels do not bear it out on the one column shown. See Q-1.

## Findings

**F-4. The italic call is exact from 0.25 up and unreliable at 0.20.**
- All 11 roman-signed "slanted" words measured 0.20 (10 words) or 0.12 (1 word).
  - At 0.20: 36 italic and 10 roman.
  - At 0.25 and above: 30 italic and 0 roman.
- 5 of the 11 sit on the first line of their OCR block (keys `…/2.1.1.1`, `…/1.1.1.2`). Among the 65 signed italic, 1 does.
  - This points to block-opening lines (a first line, a heading, an initial) as one cause.
- F-3's comb puts the 0.20–0.22 bin directly against an empty 0.22–0.24 bin. The integer shear may push some upright-but-irregular words onto the 0.20 step.
- This is a reading of 11 words. **The method is not tuned on this sample:** a threshold chosen here cannot be judged on the same set.

**F-5. The upright call held, and the abstentions lean roman but not safely.**
- 80 of 80 upright words are roman.
- The edge abstentions are 34 roman and 6 italic. An abstention cannot be read as roman: 15 % of them are italic.

**F-6. The p. 912 left column is mostly roman** ("mixed": "mostly roman with some part italic").
- This agrees with the measure (27 slanted words there).
- It refutes the rejected legacy flag (426 there).

## Questions for the architect

- **Q-1. F-1 against SI8.** Chris's pixels say the p. 914 left foot is not column footnotes. F-1 rested on that reading for all 28 moved blocks. I propose:
  - F-1's "column footnotes" reading is withdrawn. The numbers stand: 28 blocks at the column foot, smaller type, and one CCEL stretch.
  - CCEL stays a flag source, as it already is. Nothing in data depends on F-1.
  - Should Chris say in one line what the small type is, or should a console row ask it?
- **Q-2. The italic measure, next.** I propose a finer measure under a new lock, judged on a **fresh** draw, not on this set. It would use sub-pixel shear (removing F-3's comb) and a check of block-opening lines. Until then, the per-word italic call stands as "slanted at T = 0.10, precision about 0.86 on this sample", and nothing is minted from it.
  - Or: is a narrower rule wanted now (italic only at ≥ 0.25), to be confirmed on a fresh draw?
