# Phase-1 report 8 (2026-11-01)

For: the architect.

Covers your rulings on report 7 (written 2026-10-26, received 2026-11-01), with the signer correction: Chris signs every plumb-line sitting. All eleven are applied, and nothing is held on them. Five small questions arose while applying them (below). None blocks Chris's next sitting.

## What was done

| Commit | What |
|---|---|
| `5fb96f0` | ADR-0002: w3id status "merged 2026-10-26 (8b89818)", with a dated editorial correction at the foot of the Ratification section. Not a revision. |
| `bb796b5` | The report 7 rulings below. |
| (this commit) | This report and the handoff. |

Tests: 302 pass with `GOLDEN_CHAIN_BIBLES` set: the 301 before, plus one new shape test. Ingest: 0 violations, 9 warnings.

## Rulings applied

| Q | Ruling | Done |
|---|---|---|
| 1 | Item 1 withdrawn | Nothing to act on. |
| 2 | ADR-0006 ratified provisionally | Status set to "Ratified provisionally, on report 7; the architect will read the text". A Ratification section records (a) and (b). |
| 2a | SourceDivision per sitting; mint `body/plumb-line` as `gc:Editorial`; signer Chris | `gc:Editorial` is in `ontology/core.ttl`, a subclass of `gc:Body`. A shape (`shapes#Editorial`) allows only `body/plumb-line`, so the class has one instance, ever, and a test proves it. The Body is declared in `data/agents.ttl`. The plumb-line spec, the form and the ADR name Chris as signer. |
| 2b | Per-row confirm/correct is enough | Recorded in the ADR. No code change: the console already records a corrected row as a signed reading with register `corrected`. |
| 3 | Page heads: as printed in `gc:asPrinted`; the locator is the IA leaf; the note carries "leaf − 8 gives N" | Applied in the reading form, in the console's instruction and in `westminster.md`. |
| 4 | Spacing convention confirmed | Applied in the form and in the console's instruction. |
| 5 | 7.6: store the printed order | The row's doubt now states the ruling. Chris confirms the order from the crop. |
| 6 | "Gal 3.91,4": as printed; cite Gal 3:9 and 3:14, status proposed | The 28.4 row states the ruling. The TTL is written at ingest, after Chris signs. |
| 7 | Add 28.4 note l and notes n–q now; 28.1 note a is phase 2 | 5 rows added (below). The WCF console is rebuilt; Chris signs the new build. |
| 8 | "since discarded" stands, with its scope | Now "(discarded from the run output folders; not searched machine-wide)". 3 lines in `data/gill-body-of-divinity.ttl`, as locked. |
| 9 | Leave the 33 lines; one line in RULES.md | `docs/RULES.md`: the convention took effect at commit `cc32fb0`, and earlier dates are UTC and are not corrected. |
| 10 | Q6 stands; Q7 moot | No change. |
| 11 | Look after Chris signs; record a finding with a locked prediction now | Recorded in `gill-column-rule.md`, § "Finding (open): two large gutter maxima at 6.947" (below). |

## Counts (locked first)

- **Q2a** (`~/.golden-chain/plumb-line-body-predictions-locked.txt`, 2026-11-01T15:37:19Z): Body 7 → 8, every other count unchanged, ingest 0/9, new shape test passes. **All four held.**
- **Q8** (`discarded-scope-predictions-locked.txt`, 15:39:08Z): exactly 3 lines change, no count changes. **Held.**
- **Consoles** (`console-rebuild-r7-predictions-locked.txt`, 15:46:00Z): **R1–R4 held.**

| Instance | build16 | Built at | Images | Rows | Signer | Replaces |
|---|---|---|---|---|---|---|
| WCF 1647 proofs | `318910c8f421e2e9` | `bb796b5` | 16 | 26 (20 strings, 3 leaves rows, 3 lettering) | Chris | `24f26ea83e4d6bc2` |
| plumb-line | `0cffbb14753c1fa2` | `bb796b5` | 0 | 24 (9 loci, 15 Positions) | Chris | `e61e4575347277b6` |
| empty strips | `88d902a181ba64c1` | `eddbff3` | 14 | 12 | Chris | not rebuilt |

- **Both new builds:** non-provisional; each loads headless with status "incomplete; nothing unexported", no script error and no network request.
- **Empty strips:** its inputs and the console code (`build.py`, `template.html`) are unchanged, so it still ingests.
- **The old WCF proposals** are kept read-only as `~/.golden-chain/wcf1647/proposals-24f26ea83e4d6bc2.json`.

## The five new WCF rows

I read these from IA leaf 57 (PD). Each row carries its doubts on the console.

| Row | Clause | Proposed (as printed) | Doubts |
|---|---|---|---|
| `new/28.4/l` | 28.4 "actually profess faith in and obedience unto Christ" | `l Mark 16. 15, 16 Act; 8.37, 38.` | "Act;" is printed with a semicolon after the ct ligature and no s; the mark after 38 is raised |
| `new/28.5/n` | 28.5 "a great sin to contemn or neglect this ordinance" | `n Luke 7. 30. with Exod .4. 24.25,26.` | ".4." has points on both sides |
| `new/28.5/o` | 28.5 "not so inseparably annexed … saved without it" | `o Rom. 4. 11. Acts 10 2.4. 22, 31,45,47.` | no point between 10 and 2; period or semicolon after 2.4; spacing |
| `new/28.5/p` | 28.5 "all that are baptized are undoubtedly regenerated" | `p Acts 8. 13 23.` | a blot covers the 3 of 13 and whatever follows it |
| `new/28.6/q` | 28.6 "not tied to that moment of time" | `q John 3.5,8.` | printed at 28.6, not 28.5 (Q2 below) |

The Schaff column is blank on these rows. The CCEL page was truncated before ch. 28 when fetched, and Schaff is only a reading aid.

## Finding (open): gutter maxima, Q11

| Page | Slab rows (6.947 frame) | Gutter (px) | Left white | Right white |
|---|---|---|---|---|
| 913 | 3760–3995 | 277 | 237 | 29 |
| 915 | 1175–1410 | 320 | 276 | 35 |

- **Locked** (`gutter-maxima-predictions-locked.txt`, 15:40:14Z):
  - your prediction, that each slab holds a section head or a blank line on one side of the gutter;
  - my consequence from the flank measures, that this side is the left column in both.
- **How it is checked:** neither page is among the signing strips. After the empty-strips sitting, two raw-pixel crops with the slab drawn go to Chris in a console of their own. I do not view them.

## Questions

1. **Who ratifies a plumb-line sitting?** As proposed and ruled "yes", the sitting's SourceDivision and Holdings carry `gc:proposedBy` and `gc:ratifiedBy` `agent/architect`. Chris now signs. Should they stay `agent/architect`, or should `agent/chris` be minted?
   - The writer is unchanged until you rule. The plumb-line sitting is last in your order.
2. **Note q is printed at 28.6**, at "administred q". Its Argument would take `source/wcf/28/6`.
   - Notes n–p are at 28.5, which needs a new `source/wcf/28/5`. The WCF efficacy Holding's `dcterms:source` would then gain 28.5.
   - Proposed: exactly that, by locked prediction at ingest.
3. **Note n** is keyed to "a great sin, to contemne or neglect this Ordinance". That clause comes before the grace clause.
   - I proposed it under the efficacy Position as you ruled. Confirm that n belongs there, and not only o and p.
4. **The locator string** (Q3). Proposed: `gc:secondaryLocator "Edinburgh: Evan Tyler, 1647, IA humbleadviceofas00west leaf 57"`, with the head as printed in `gc:asPrinted` (e.g. "(49)"). Confirm the form.
5. **A dated line after the convention.** One handoff line, "`locate_column_rule` (2026-10-26)", was carried forward in `5d5ec56`, after `cc32fb0`, and names a UTC date. Under Q9 I left it. The other post-convention lines that carry 2026-10-26 are lock timestamps (`T…Z`).

## Next, in your order

1. ~~Rebuild the WCF console~~: done, `318910c8f421e2e9`.
2. Chris signs the empty strips (`88d902a181ba64c1`). Then:
   - ingest;
   - unhold OCR if it is clear;
   - prepare the A2 fixture;
   - build the Q11 crops console.
3. Chris signs WCF `318910c8f421e2e9`. Then:
   - ingest;
   - lock the counts;
   - split the Arguments;
   - add notes l and n–q as Arguments, with Q2–Q4 as ruled.
4. The plumb-line sitting (Chris, `0cffbb14753c1fa2`), after Q1.
5. The ADR ratification cards.
