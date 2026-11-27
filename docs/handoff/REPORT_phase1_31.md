# Report 31: the quotation-unit page pass, part 1

- **From:** the build agent, 2026-11-26. Branch `phase-0`, pushed.
- **On:** [RULING_report_30.md](RULING_report_30.md), Q-A-1 and Q-A-2. Lock: [LOCK_page_pass_2026-11-26.md](LOCK_page_pass_2026-11-26.md) (`a08a324`), committed before any page was viewed.
- **Where the record is:** [AUDIT_argument_unit_2026-11-26.md](AUDIT_argument_unit_2026-11-26.md), section "Page pass, part 1".
- **Nothing is changed.** No `data/` file and no test.

## One list: what waits on Chris, and on the architect

**On Chris (sign from the pixels; each page is local, under `~/.golden-chain/console/`):**

1. **Sitting 2:** `plumb-line-followup/console_plumb-line-followup_18a4a13dfeffb6e9.html`.
2. **Statements and inclusion:** `statements/console_statements_f3f1af17d9075ba5.html`.
3. **LBC 1677:** `console_lbc-1677_0a73bb5afa616446.html`.
4. **Gill's italic:** `italic-spans/console_italic-spans_9b19159be3098c64.html`.
   - Part 2 of the page pass (Gill *Body* pp. 897-912, 17 Arguments) waits on this one.
   - After part 2, the full re-cut list goes to the architect (Q-A-2).

**On the architect:**

- **Q-P-1. Graves, p. 124: is this one unit or three?**
  - The page reads: "Christ's declaration (Matt. 16: 18), and Paul's statement (Heb. 12: 28), are emphatic commentaries upon the prophecy of Daniel (2: 44)."
  - Each reference is set in parentheses after its own noun, so the build agent proposes **three** units. The first pass said "up to three".
  - All three are in one sentence and one clause, though. If the unit is "the references closing one clause", it is **one**, and the Argument stays as it is.
  - This is the only Argument in part 1 where the answer turns on the reading of the rule rather than on the page.

## What the pass found

| | Arguments |
|---|---|
| Viewed (the 16, plus p. 345 to confirm) | 17 |
| Same cut | 10 (9 of the 16, and p. 345 confirmed) |
| Would split | 7, into 21 units |
| Would merge | 0 |
| Would widen | 0 |
| Signed by Chris, among those that differ | 0 |

**The seven splits:**
- Coxe V §8: 6 units, pp. 105-109.
- Gill *Body* II.15 head 1, the third Argument: 4 units, p. 247.
- Gill *Body* IV.5 "First" 1: 2 units, p. 361.
- Gill *Divine Right* "First" 1, 3 and 4: 2 units each, pp. 45-46.
- Graves ch. X: 3 units (Q-P-1), p. 124.

The audit lists each new IRI proposed, with its printed unit, cites and page.

**After part 1, of the 80 Arguments:** 56 same cut, 7 would split, 0 would merge or widen, and 17 waiting for part 2.

**A first-pass slip, recorded.**
- The first pass read only one `gc:asPrinted` per Argument. Eleven Arguments carry more than one:
  - `gill-body/doctrinal/4/5/001`;
  - ten in Practical III.1, which are all part 2.
- The slip hid 4/5/001's second run, which is why it splits. No first-pass "same" verdict rests on a multi-string Argument.
- Part 2 reads every string.

## Scores

- **P1 held.** The audit has the section, with a verdict and a page for each of the 17 viewed. The counts are updated in a new table; the first-pass table is left as written. The 17 of part 2 are listed as waiting.
- **P2 held.** No full list yet. The part-1 candidates have proposed IRIs, each numbered after the highest in its division. Old IRIs are deprecated, never reused.
- **P3 held.** This commit adds only the audit update, this report and the ruling's "Applied" section.
- **P4 held.** Every page was found. The Triglot is IA `concordiatriglot00unse`, p. 245, leaf n530. No printed reference contradicts `asPrinted`. These are recorded, not resolved:
  - the F6 question on p. 361;
  - the Apology's missing page;
  - Coxe's "former part of ... Rom. 4.";
  - an uncited run on p. 247.
