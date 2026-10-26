# Phase-1 report 5 (2026-10-26)

For: the architect.

Covers:
- the rulings on report 4;
- Q5, Q6 and Q16 from report 2.

OCR stays **HELD**. Chris has not yet signed [SIGNOFF_empty_strips.md](SIGNOFF_empty_strips.md).

## The column-rule run: two statements (ruling on report 4)

1. **The clause is FALSIFIED.** The locked clause "every strip carries a cluster" (440/440) missed: 426/440. It is recorded as falsified in [../sources/gill-column-rule.md](../sources/gill-column-rule.md) and in [../sources/goat-yard.md](../sources/goat-yard.md). The lock file is not edited.
2. **The run PASSES goat-yard's criteria, 20/20.**

## What was done

| Commit | Files | What |
|---|---|---|
| 54082e6 | `data/book-of-concord.ttl`, `tests/predictions.py` | The Apology is `gc:childOf` augsburg. The Small Catechism has no parent (1529 predates Augsburg). Supersedes 2(a). |
| a465ee3 | `tools/signing_strips.py`, `tests/test_signing_strips.py` | The strips for Chris, and the measure of where ruled rows start and end (F, L). 3 born tests, exact offsets. |
| 305f22c | `tools/gy_locate_column_rule.py`, `tests/test_gy_locate.py`, `docs/sources/goat-yard.md`, `docs/sources/gill-column-rule.md`, `docs/handoff/SIGNOFF_empty_strips.md` | `--no-deps` recorded: the skipped dependencies and why. A guard that fails loud unless exactly the six substrate modules load. Born tests import each one. The clause is recorded as FALSIFIED and the run as PASSES. The empty-strip hypotheses and the sign-off form. |
| 61b7b19 | `data/loci.ttl`, `data/westminster.ttl`, `tests/predictions.py`, `docs/loci/plumb-line-form-phase1.md` | Q5: the locus `baptism-repetition` (33c, "May baptism be repeated?"), the Position `once-only`, the WCF 28.7 Holding (required, scope all) and Argument `wcf/28/7/001` (Titus 3:5). |
| 2aabb8a | `data/book-of-concord.ttl`, `tests/predictions.py` | Q6: `argument/apology-1531/ix/002` supports `necessary-means-of-grace`, citing "Matt. 28,19" as printed. Argument only; no Holding. |
| b0bf02d | `docs/sources/westminster.md`, `docs/handoff/READING_wcf1647_proofs.md` | Q16: source note (edition, witness, lettered rule), then a reading form for Chris. No strings recorded yet. The 28.7 divisions row now reads baptism-repetition. |
| (this commit) | this report, `HANDOFF_phase1.md` | — |

## Predicted vs actual

Every count was locked before its edit, in a file under `~/.golden-chain/`.

| Change | Lock | Predicted | Actual |
|---|---|---|---|
| Apology childOf augsburg | 01:04:26Z | childOf 0 → 1; effectivelyHolds 33 → 34 (the Apology inherits Augsburg's efficacy Holding only; its own baptism-subjects Holding blocks the other two by locus); other 12 keys unchanged; inconsistency 0 | matched |
| Q5 | 01:13:13Z | Locus 8 → 9, Position 14 → 15, Argument 43 → 44, Holding/holds 33 → 34, answers 14 → 15, supports 43 → 44, effectivelyHolds 34 → 35, warnings 8 → 9, Passage 86 unchanged | matched |
| Q6 | 01:17:01Z | Argument and supports 44 → 45; all else unchanged | matched |
| Empty-strip hypotheses | 01:03:32Z | H1: F(896) ∈ [3400, 3700). H2: L ∈ [7000, 7300) on 896/902/907/908, and the ruled fraction within 0.10 of the peak | **missed**, see below |
| Tests | 206 + 3 + 7 | — | **216 passed** |
| Jena ingest | 0 violations, 9 warnings | — | **0, 9** |

**Hypothesis findings** (rule 6). Full table in [../sources/gill-column-rule.md](../sources/gill-column-rule.md), § "Empty-strip hypotheses".
- **H1 missed.** On p. 896 ruled rows begin at F = 3059, 341 rows early. Yet strips 3100 and 3400 are empty to `locate_column_rule`.
- **H2's L clause** held only on 896 (7112). On 902 (6921), 907 (6448) and 908 (6896) the rule ends *above* the last strip.
  - So the 0.44–0.55 peaks in strip 7000–7300 are not the rule at the fitted line. What carries them is not known.
  - The fraction clause missed on all four. The falsifier (L ≥ 7300) did not fire.
- **Control missed on p. 911** (L = 7160 < 7177).
- These are numbers only; the pixels decide. The strips are prepared, and the form is [SIGNOFF_empty_strips.md](SIGNOFF_empty_strips.md).

## Q5: one Position minted, not two

- **WCF 28.7** ("but once to be administered unto any person") is minted as `once-only`. It carries the Holding (modality required) and an Argument citing Titus 3:5, Schaff's proof.
- **The Gill/LBC Position is not minted.**
  - Gill, *Body of Divinity* P III.1 §2, states the premise. Infant sprinkling "as it is now commonly practised… is a mere invention of men", and the apostles "would neither know nor own it to be the ordinance commanded them by Christ". §4 says sprinkling "cannot… be called a mode of baptism".
  - But that passage prints no proof text, and it draws no conclusion about repetition.
  - LBC 29 is silent: it omits WCF 28.7.
  - With no Argument, rule 2 blocks the Position.

## Q6: one Matt 28:19, two Arguments

Apology IX's only printed proof is "Matt. 28,19". `ix/001` (infant baptism) and `ix/002` (efficacy) now both cite it. They come from the same sentence, so the citation does double duty.

## Q16: the WCF strings wait for Chris

- **Witness proposed:** Edinburgh, Evan Tyler, 1647 (IA `humbleadviceofas00west`, `NOT_IN_COPYRIGHT`). It is the only 1647 printing with proofs that has been fetched. The London first printing with proofs is [U].
- **The proofs are lettered marginal notes**, so the LBC rule applies.
  - The OCR shows the letters, e.g. "baptized m" at 28.4 and "perfon f" at 28.7.
  - It cannot give the note strings, so none is taken from it.
- **The form** [READING_wcf1647_proofs.md](READING_wcf1647_proofs.md) lists the 11 WCF Arguments with Schaff's clause and proofs as a reading aid. Chris fills in the letters, the strings and the pages.
- **`28/1/002` will likely split.** Schaff puts its texts under two clauses: ingrafting (Gal 3:27; Rom 6:5) and newness of life (Rom 6:3, 4).
- No TTL changes, and no count is predicted, until the form is signed.

## Open questions

1. **Notation 33c** for `baptism-repetition` is provisional. Keep it, or renumber?
2. **Modality `required`** on the WCF 28.7 Holding. 28.7 says "but once to be administered". Is that `required`, or a different modality?
3. **The Gill/LBC repetition Position** is unminted (above). Options:
   - leave it until a source gives an Argument;
   - or rule that Gill's §2 premise (with no proof text) suffices for an Argument;
   - or look further in Gill (e.g. the *Exposition* at Acts 19:5, which is not yet read).
4. **The A2 fixture.** Its condition ("if 20/20 passes") is met on goat-yard's criteria. Prepare it now, or after the sign-off?
5. **If H1 is refuted,** the ruling does not cover the case. The form says that OCR then stays held and the architect rules. Confirm that wording.
6. **Matt 28:19 doing double duty** (Q6). Is one proof text for two Positions acceptable, or should `ix/002` carry a note?
7. **Q16 witness.** Is the Edinburgh Tyler 1647 the witness of record, or should the London 1647 printing be sought first?
8. **WCF 28.1 clauses not cited:** admission (1 Cor 12:13), regeneration (Tit 3:5) and remission (Mark 1:4). `union-with-christ` names remission of sins. Should these notes become Arguments once read?
9. Carried over from report 4:
   - (6) the Gill provenance wording;
   - (7) the ADR-0003 Revision 1 readings;
   - (8) the Q12 text to forward to goat-yard;
   - report 3 open question 2.

## Next on "continue"

1. When Chris signs `SIGNOFF_empty_strips.md`, apply the outcome:
   - unhold OCR;
   - or write the goat-yard request file first;
   - or, if H1 is refuted, report and wait.
2. When Chris signs `READING_wcf1647_proofs.md`, lock the counts, then record `gc:asPrinted` and split the Arguments per letter.
3. Otherwise, apply rulings on the open questions above. No new data is minted without a ruling.
