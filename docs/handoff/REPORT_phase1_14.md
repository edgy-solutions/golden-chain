# Report 14: the rulings on report 13, worked

- **For:** the architect, through Chris.
- **Ruling:** [RULING_report_13.md](RULING_report_13.md), filed verbatim.
- **Branch:** `phase-0`, pushed through this report's commit (after `9a5a955`).

Every item of the ruling was worked. Each count was locked (chmod a-w, under `~/.golden-chain/`) before its code existed, as the ruled habit requires. **Two predictions missed (O-3 C3, O-4 S1).** They are recorded below, and no lock was edited.

- **Full suite:** 513 passed.
- **Weigh output:** unchanged (members `cedb846fb605…`, officers `cebb5eb6ab05…`).
- **Measurement runs:** every one ran on a clean tree, was run twice, and gave byte-identical outputs.

I stop here: the next console waits on Q6 and Q7.

## What was done

| Ruling | What | Commit | Lock: result |
|---|---|---|---|
| W-1 | Derivation from the cells. It follows from ADR-0003 §7 (a per-Locus override) and is not a defect: [FINDING_W1_apology_augsburg.md](FINDING_W1_apology_augsburg.md) | `60cedb3` | none needed (no change) |
| 6 | ADR-0006 R1 (details below this table) | `29ac62d` | A1–A7 hit |
| 7 | weigh renders the consequence words under the case (c) wall, and only under a wall | `8912293` | R7-1–R7-4 hit |
| 8 | `gc:Denomination` and `gc:Congregation` minted as Body subclasses, with no instances | `8912293` | D1–D5 hit |
| 9 | Recorded as confirmed | — | — |
| 10 | The narrow-glyph measurement is a standing step of every pin run on a new face or volume, with the margin reported ([goat-yard.md](../sources/goat-yard.md), status table). The goat-yard note now gives them the number: 10 px against `RULE_RUN_MAX_W` 8, a margin of 2 px | `c37877c` | — |
| 11 | tessdata 4.1.0 legacy is recorded, not adopted | `78199f8` | — |
| 12 | Harbaugh's date, read from the title-page leaf (n4). No date is printed. The LC copyright stamp reads 7 Jan. 1892; the pencilled "1889" is a cataloguer's, not provenance. Cite as *n.d. (LC copyright stamp, 7 Jan. 1892)* | `c37877c` | — |
| 13–16 | Applied in [heidelberg-belgic.md](../sources/heidelberg-belgic.md): admission by clause; Acts 22:16 carries an Argument for (a); the misprint rule applied to Schaff p. 426 only ("Apoc. i. 6" → Rev 1:5, with gc:asPrinted, a resolutionNote, status proposed); one Argument per source | `c37877c` | Batch C counts are locked before minting |
| O-3 | CCEL realigned: line-end hyphens joined, per-page windows, block moves | `ce54aa1` | C1, C2, C4–C6 hit; **C3 missed** |
| O-4 | Run 1's legacy flag recorded as "legacy flag, rejected". Per-word slant measured from pixels | `78199f8`, `6b49963` | S2–S10 hit; **S1 missed** |
| 17 | Truth-set v2 drawn, stratified by page and measured slant. The old 200 stay on record, unsigned | `9a5a955` | T1–T5 hit |

**Item 6 in detail:**
- `data/plumb-line.ttl` is now the deterministic replay of the committed signed sittings (`docs/sittings/plumb-line/`).
- Tier and clarity provenance are 17 annotated axioms, `axiom/tier|clarity/<locus>/to/<value>`, each with `dcterms:source` naming the sitting.
- A born test checks that the replay equals the file byte for byte.
- The overwrite guard refuses a hand-edited file, a missing record and a duplicate sitting.
- Minus its axioms, the graph is isomorphic to the one before.
- A new `tests/conftest.py` stops any test from writing the real records. The item 6 implementer's run of an older test, before it was patched, wrote one stray record into the repo. The implementer deleted it and regenerated the file before anything was committed.

## The misses

- **O-3 C3**
  - *Locked:* "every moved block of ≥ 20 tokens lies on pp. 913–915."
  - *What happened:* 28 moved blocks were found on 9 pages (897–914). Three are of 20 words or more: p. 910 left (32), p. 910 right (21) and p. 914 left (26).
  - *Why:* I expected one displaced passage at pp. 914–915. The movement is in fact spread over the chapter: see finding F-1.
- **O-4 S1**
  - *Locked:* "measured ≥ 95 % of eligible."
  - *What happened:* 11,247 of 12,474 (90.2 %). All 1,227 abstentions are "edge" (the best shear fell on a grid end, −0.20 or +0.50); none are "small".
  - *Note:* the method is not tuned after the run. The truth set carries an edge stratum (40 words), so the signing will show what these words are.

## Findings

**F-1. CCEL gathers Gill's column footnotes after the chapter; the book prints them at the foot of each column.** This answers O-3's "which text has the moved block". It was shown from numbers only; no text was read.
- All 28 moved blocks sit at the foot of their column, at relative height 0.87–0.98.
- They are in smaller type: median word height 66 px, against 78 px for all column words.
- All of them map, in page order, into one CCEL stretch (slice lines ~1382–1474). In that stretch 31 of 216 lines open with a number; in the 1,375 lines before it, 3 do.
- The p. 914 collapse of run 1 (0.102) was that endnote stretch derailing the single global in-order pass. Per-page windows bring p. 914 to 0.903.
- Overall agreement is 0.839 → **0.9185** (agree 15,523, moved 321). 177 of the 200 hyphen joins agree.
- No page got worse: the smallest gain is +0.008.
- CCEL stays a flag source.

**F-2. The slant measure is bimodal, and the italic call is spread over every column.**
- The modes are at −0.01 (upright) and 0.21 (about 12°), with T = 0.10 and an empty valley.
- 562 of 11,247 measured words are slanted, a rate of **5.0 %**, within the prior of 3–15 %.
- Every page but p. 896 has some. No page-column holds more than 6.4 % of them (the most is p. 898 right, with 36).
- **p. 912 left: 27**, where the legacy flag had 426.
- Of the 493 legacy flags, 28 are slanted by this measure. The rejected flag and the pixels disagree almost wholly.

**F-3. A comb in the slant histogram** (record only, no change).
- The high mode's bins read 296 (0.20–0.22), 0 (0.22–0.24) and 196 (0.24–0.26).
- The lower side is uneven in the same way (408, 71, 1,802 at −0.10 to −0.04).
- A smooth slant distribution would not skip a bin. I read this as a rounding artefact of the integer shear (`np.rint`) at the 0.01 grid step. It does not move T or the italic call, since the valley is 0 either way. It does mean the slant *value* is coarse.

## Truth-set v2 (item 17)

- **Size:** 196 candidates. Per page: 4 slanted, 4 upright, 2 edge. P. 896 has no slanted word, so it gives none.
- **Order:** by sha256("truthset-v2/" + key).
- **Contents:** rows carry the key, page, region, bbox, stratum and slant, and no OCR text. Chris reads each word from pixels.
- **Digest:** `34de37bac8975af603abda91cb0c1ae054b309176b89183ff8ec2439b892de7f`. Two builds give the same digest, on a clean tree at `9a5a955`.
- **Overlap:** 1 word is shared with the run-1 candidates. p. 912 left gives 9 rows.
- **Where it lives:** `~/.golden-chain/truthset-v2-2026-11-14-a/` (local; never committed). It is unsigned. **No console is built yet** (Q7).

## Questions for the architect

- **Q1 (from report 13, items 13–16): Belgic XXXIV, Schaff p. 425 fn3.**
  - The clause is "baptism instituted in place of circumcision; received into the Church", citing Col 2:11, 1 Pet 3:21 and 1 Cor 10:2.
  - It is marked "partly" an efficacy clause. Is it admitted to Batch C as an instrumentality (a) Argument, or left out?
- **Q2 (from W-1 §5): Apology IX.**
  - Does it also hold *professing-believers-only* forbidden, as Augsburg IX does by its condemnation?
  - If yes, it is a new Holding with its own source, minted under a lock. apology-1531 would then wall on subjects as augsburg does.
- **Q3 (item 6): confirm three readings in ADR-0006 R1.**
  - (a) Only an explicitly chosen "silent" removes a Holding. An empty modality is "unanswered", and leaves it standing.
  - (b) A radio, proposal or text row is never data, even if abstained.
  - (c) A flag confirmed on a Position the plumb-line does not hold is not written; it is listed in the file's header.
- **Q4 (O-3): I re-ran the alignment, not the OCR.**
  - The defect was in the comparison, and the OCR words are deterministic.
  - Is a full OCR rerun wanted as well?
- **Q5 (O-3): the console row.**
  - F-1 answers "which text has the moved block" from numbers.
  - The ruled row stays for Chris to confirm from pixels: "the small type at the foot of p. 914 left: column footnotes?" Keep it, or drop it given F-1?
- **Q6 (O-4): sign truth-set v2 as drawn, or first a finer slant measure under a new lock?**
  - A finer measure would use sub-pixel shear to remove the comb (F-3) and reduce edge abstentions (S1).
  - My recommendation is to sign first. The signed set is what judges the measure. The strata only shape the sample, and the edge stratum will show what the abstentions are.
- **Q7: the next console.** I propose one console with:
  - the 196 word crops, which Chris signs as italic, roman or other (no model views them);
  - the p. 912 left-column row;
  - the CCEL row (if kept, Q5);
  - help text saying that an empty answer leaves an earlier answer standing, and that "silent" removes it.

  I build it on your word.
