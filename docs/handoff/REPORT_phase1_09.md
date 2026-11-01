# Phase-1 report 9 (2026-11-01)

For: the architect.

Covers:
- your rulings on report 8;
- Chris's WCF 1647 sitting (`318910c8`);
- A2's drafted substrate-v1 notice.

Applied: Q1, Q2, Q5, most of Q4, the WCF ingest and console finding (b). Held, with questions below: the head in `gc:asPrinted` (Q4), the clause on the Argument (Q3) and the console template change.

## What was done

| Commit | What |
|---|---|
| `8e1ed37` | Chris's WCF sitting `318910c8` ingested: [SIGNED_wcf1647_318910c8f421e2e9.md](SIGNED_wcf1647_318910c8f421e2e9.md). 59 fields confirmed, 1 corrected (note l, "Acts"). |
| `d476a43` | Q1, Q5, finding (b); two plumb-line writer defects fixed (below). |
| `8ab5c87` | Q2–Q4: the 20 signed strings recorded; the split; notes l and n–q added. |
| (this commit) | This report and the handoff. |

Tests: 307 pass with `GOLDEN_CHAIN_BIBLES` set. Ingest: 0 violations, 9 warnings.

## Rulings applied

| Q | Done |
|---|---|
| 1 | `agent/chris` minted. The Status shape's `ratifiedBy` allows `agent/architect` and `agent/chris`. New shape `shapes#PlumbLineHolding`: a Holding of `body/plumb-line` without `gc:ratifiedBy agent/chris` is a violation; a test proves both ways. The writer now writes `gc:proposedBy agent/build-agent` and `gc:ratifiedBy agent/chris`. **The plumb-line writer is unblocked.** |
| 2 | `source/wcf/28/5` minted; notes n–p take it, note q takes `28/6`. The efficacy Holding's `dcterms:source` is now 28/5 and 28/6. |
| 3 | Note n is `28/5/001` under the 33b Position. **Recording the clause is held** (question 3). |
| 4 | The edition is once on `source/wcf`, as `dcterms:bibliographicCitation`. Every WCF Argument has `gc:secondaryLocator "IA humbleadviceofas00west leaf N"`. **The head in `gc:asPrinted` is held** (question 2). |
| 5 | "(2026-10-26, UTC)". One line. |
| WCF sitting | Ingested, locked, split; l and n–q added (below). |
| Finding (b) | A blank optional answer renders "not answered". The verdict JSON is unchanged. The already-written `SIGNED_wcf1647_…md` keeps "unknown": it is content-addressed, and the record stands as signed. |
| Finding (a) | **Held** (question 1). |

## Two defects found in the plumb-line writer (fixed in `d476a43`)

The writer had a test, but nothing validated its output against the shapes. A new test does: it writes a sitting beside the real `data/` and requires 0 violations.

The old writer's output fails the shapes at `8e1ed37` in two ways:
- **Each Holding** is `ratified` with no `dcterms:dateAccepted`, so it fails Status. Now: `dcterms:dateAccepted` is the signature date. The ingest refuses a date that is not `YYYY-MM-DD`.
- **The sitting's SourceDivision** has no `dcterms:isPartOf`, so it fails SourceDivision. Now: `dcterms:isPartOf <source/plumb-line>`, minted as a `gc:SourceWork` in `data/agents.ttl`. ADR-0006's ruled IRI `source/plumb-line/sitting-<build16>` implies that parent.

Both are applied because Q1 unblocks the writer, and it would otherwise write invalid data. Both can be reversed before the plumb-line sitting, which is last in your order. Please confirm (question 6).

## The WCF Arguments (sitting `318910c8`, Q2–Q4)

- **The strings.** Each was taken by script from the signed JSON, never retyped. All 20 stored strings were checked equal to the signed ones. Each is its Argument's only `gc:asPrinted`.
- **The resolution note.** `28/4/001` has a `gc:resolutionNote` for "Gal 3.91,4" (report 7 Q6, with Chris's note).

| Argument | Note | Position | Cites (new Passages in bold) |
|---|---|---|---|
| `28/1/002` | d | union-with-christ | Gal 3:27; Rom 6:5 (lost Rom 6:3–4 to 007) |
| `28/1/004` | b | union-with-christ (33a) | **1 Cor 12:13** |
| `28/1/005` | e | union-with-christ (33a) | Titus 3:5 |
| `28/1/006` | f | union-with-christ (33a) | Mark 1:4 |
| `28/1/007` | g | union-with-christ | Rom 6:3–4 |
| `28/4/002` | l | believers-and-their-infants | **Mark 16:15–16; Acts 8:37–38** |
| `28/5/001` | n | grace-conferred-in-right-use (33b) | **Luke 7:30; Exod 4:24–26** |
| `28/5/002` | o | grace-conferred-in-right-use | Rom 4:11; **Acts 10:2, 4, 22, 31, 45**; Acts 10:47 |
| `28/5/003` | p | grace-conferred-in-right-use | **Acts 8:13; Acts 8:23** |
| `28/6/002` | q | grace-conferred-in-right-use | **John 3:5; John 3:8** |

## Counts (locked first)

- **The WCF ingest** (`wcf-signed-318910c8-predictions-locked.txt`, 17:32:49Z): W1–W4 held.
- **Q1, Q5 and (b)** (`report8-q1-q5-predictions-locked.txt`, 17:51:40Z): P2–P5 held.
  - **P1 missed its baseline.** I wrote SourceWork 6 → 7; it was 7 before the edit and is 8 after. The delta held. The count was not measured before locking. Since then, every baseline is measured before the lock.
  - **P6:** ingest 0/9 held. Tests: 307, against 306 predicted. The extra one is the signature-date guard's own test.
- **Q2–Q4** (`report8-wcf-ttl-predictions-locked.txt`, 17:57:38Z), baselines measured first. **T1–T5 held:**
  - Argument and supports 45 → 54, Passage 86 → 100, SourceDivision 20 → 21;
  - `gc:cites` 128 → 146, `gc:asPrinted` 52 → 72, `gc:secondaryLocator` 57 → 77, `gc:resolutionNote` 6 → 7;
  - every other count unchanged.

## Substrate-v1 (A2's drafted notice)

Checked from Golden Chain's side against the tag. It is accurate in substance, with two corrections and two notes:

1. **Rerun 8 or 9?** Tag `substrate-v1` is commit `301bde5`, and its message says "(rerun-8 lock)". The notice says "the rerun-9 commit". One of them needs correcting.
2. **A second consumer-visible change.** `analyze_page_s1`'s return dict gains `"median_line_h"`. It is additive, but Golden Chain calls that function (`tools/gy_locate_column_rule.py`, line 170). The notice names only `ink_box`.
3. **"Their pin run."** Golden Chain has three runs on v0: native, 0.703 and 6.947, and 6.947 governs. The diff from `3d0b03e0` leaves `locate_column_rule`, `page_ink`, the `RULE_*` and `INK` constants and `build_page_geometry` unchanged, so all three should reproduce. The diff is additive, in `verse_regions.py`, `build_verse_regions.py`, its test and one response doc.
4. **When Golden Chain re-pins.** Proposed: after the empty-strips sitting is ingested. The step is locked, and a rerun at 6.947 under v1 is predicted identical to the v0 run in every strip and band. That tests the notice's claim from our side. Nothing already built changes.

## Questions

1. **The console fix (finding a) breaks the two unsigned builds.** The ingest recomputes `code_sha` from the current `build.py` and `template.html`, and refuses on a mismatch. A template bump therefore makes empty strips `88d902a1` and plumb-line `0cffbb14` un-ingestable, not only future builds. Signed builds are unaffected, as you said.
   - **Proposed:**
     - if Chris has **not** opened the empty strips: land the fix now and rebuild both;
     - if he **has**: he signs `88d902a1` as built; the fix lands after its ingest, and the plumb-line console is then rebuilt.
   - The alternative is to keep each console version's code frozen and have the ingest choose it by `code_sha`. That is more machinery than one sitting needs.
   - **For Chris:** have you opened `console_empty_strips_88d902a181ba64c1.html`?
2. **The head in `gc:asPrinted` (Q4) conflicts with report 2 Q1.** That rule says a lettered note is its Argument's only `gc:asPrinted`. Adding "(49)" would put two values there.
   - The shape would not catch it today. Its letter test, `^[(][a-z][)] `, knows the LBC "(c) …" style but not the WCF "c Rom…" style. So for WCF the rule is currently unenforced. That is a finding in its own right.
   - **Proposed:** put the head in `gc:secondaryLocator`, as "IA humbleadviceofas00west leaf 57, head (49)". Put "leaf − 8 gives N" in `gc:resolutionNote` on the two Arguments whose head is misprinted:
     - `7/5/001`: (14), where leaf − 8 gives 16;
     - `27/1/001`: (46), where leaf − 8 gives 47.
   - Also widen the shape's letter test to `^([(][a-z][)]|[a-z]) `, with a test.
   - **Or:** amend the rule and the shape to allow exactly one lettered note plus one head matching `^[(\[][0-9]+[)\]]$`.
   - The heads are signed (one per row, all confirmed), so either takes one locked edit.
3. **"Record the clause on the Argument" (Q3).** The Argument shape is closed. The only property that could carry the clause is `gc:quotation`, and that needs `gc:quotationCheckedAgainst` and `gc:pages`. WCF data is "Reference only; no quotation", and the CCEL permission question is open. Also, the clause text was not a signed row.
   - **Proposed:** for now a TTL comment only, naming the clause's role ("neglect a great sin": the necessity clause). That is done.
   - If you want the clause as data, it needs a new property (ADR-0005 amended), with the 1647 text signed from pixels at a later sitting.
4. **"gc:proposedBy agent/build" (Q1).** The minted IRI is `agent/build-agent` (the test fixture uses `agent/build`). I used `agent/build-agent`. Confirm.
5. **"Never a doctrinal Holding" (Q1) and four WCF Holdings** ratified by `agent/architect` on 2026-10-25 (report 1, ruling 4): `believers-and-their-infants`, `professing-believers-only`, `mode-indifferent/officers` and `immersion-only/officers`.
   - My reading: they record what the WCF holds, which is a data ruling about a source, not a doctrine. They stand unchanged. Confirm.
   - Should a shape also stop `agent/chris` ratifying anything except plumb-line items? Today Status allows either ratifier on any node.
6. **The writer fixes** (above): `dcterms:dateAccepted` as the signature date (Chris's local date), and `source/plumb-line` as the SourceWork. Confirm.

## Next, in your order

1. Chris signs the empty strips (`88d902a181ba64c1`), after question 1. Then:
   - ingest;
   - unhold OCR if it is clear;
   - prepare the A2 fixture;
   - build the Q11 crops console;
   - re-pin to substrate-v1 as locked step 4 above.
2. The console fix (finding a), timed by question 1.
3. The plumb-line sitting (Chris). The writer is unblocked.
4. The ADR ratification cards.
5. Questions 2–3, when ruled: one locked edit each.

`8e1ed37` and later are not pushed.
