# Report 12: step 3 Batch A′ minted; Batch B stops on four sourcing questions

2026-11-08. This is the build agent's report to the architect on the [ruling on the step-3 plan](RULING_step3_plan.md). Batch A′ (the ruling's follow-ups to A) is done. Batch B stops under rule 8: what remains of it needs your rulings, not lookups.

## Done

| Commit | What |
|---|---|
| `1093740` | Batch A′: the ruling, filed verbatim; [ADR-0002 Revision 2](../adr/0002-identity-iri-patterns.md) (proposed); `gc:Teacher` and `vocab/status/rejected`; ingest check d; F-A, M5, M6, M8, M9, M10 and M11 minted as specified in [PLAN_step3_minting.md](PLAN_step3_minting.md) "Batch A′". |

- **Lock.** `step3-batchA2-predictions-locked.txt` (03:36:32Z). P1–P6 held.
  - Argument 74, Passage 136, Holding 52, effectivelyHolds 53, excludes 9, Axiom 1; the other counts are unchanged.
  - pytest 380; ingest 0 violations and 2 warnings (tier on 23a and 23b, which the console sets).
- **Ingest check d.** A rejected axiom's triple must be absent, and any other axiom's triple must be present. Born tests prove both directions on fixtures.

## Flags from Batch A′ (minted as ruled; for your eye)

1. **F-A narrows (ii) against (iii).** Coxe II §§10–11 (pp. 36–38) never says "covenant of grace" or "established in the new covenant". With Coxe's wording, (ii) and (iii) differ only on whether an eternal covenant of redemption precedes the promise. Many Westminster divines held that too, so the M9 (ii)–(iii) exclusion may not hold. It is minted, and the console will ask Chris.
2. **M6: the refuting Holding is on `infants`.** My M6 question said "Augsburg holds believers-and-their-infants", and that was wrong. The data has `holding/augsburg/baptism-subjects/infants` (taught), and Augsburg holds nothing on 23b. The axiom's comment names the Holding that exists.
3. **M8: the IRI form.** The ruling's example `passage/kjv/Heb.8-Heb.10` is chapter-only, which ADR-0002 Passage rule 2 forbids, and that rule is shared with goat-yard. The canonicaliser expands it to `Heb.8.1-Heb.10.39`, which is what is minted. A born test pins the expansion (Revision 2 item 5).
4. **LBC 7.3 note g is not cited** (salvation of the OT saints; it does not separate (ii) from (iii)). **WCF 7.6 note o is not minted** (not ruled).

## Batch B: what was found

All locators were checked on PD page images by the build agent unless marked otherwise.

- **Validity (1) is deferred to phase 2 (M5).**
  - Hodge, *Systematic Theology* III, §6 "Validity of the Sacraments" (pp. 523–525) prints no Scripture. The only reference on those pages is Gal. iii. 26, which closes §5 on the Lutherans.
  - §7 "Baptism" (pp. 526–539) does not treat validity; its Scripture is all on mode (from the OCR).
  - The leaf map is n = p + 11, not + 12. [hodge-thornwell](../sources/hodge-thornwell.md) is updated.
- **Validity (4) is ready.** Graves ch. X, p. 124, cites Matt 16:18, Heb 12:28 and Dan 2:44, with ch. VI p. 64 as the secondary locator.
- **Validity (3).** LBC 28.2 note (b), "Mat. 28. 19. 1 Cor. 4. 1.", as you read it from the 1677 facsimile, is ready as its Argument, with no LBC Holding (M5).
- **Gill, Practical III.1 opening** (Tegg 1839 vol. 2, pp. 621–622; BSB p. 896):
  - Gill says baptism "is not a church ordinance": it is administered out of the church, in order to admission. "Admission to baptism lies solely in the breast of the administrator", who may admit one the church thinks unfit.
  - His example is Saul, baptized by Ananias "without any previous knowledge and consent of the church", Acts ix. 18–28.
  - "Matt. iii. 1" on p. 622 is about John as the *first* administrator. It belongs to head I, that baptism is peculiar to the gospel, not to who may administer.
- **Repetition: no Baptist source found prints Scripture at the place that holds the clause.**
  - Booth vol. 2 p. 280 note ‡ (earlier [V]).
  - Gill, *Divine Right* ch. II pp. 5–6: one who embraces believers' baptism "receives the true Baptism", and infant baptism must first be proved valid before renouncing it can be charged.
  - Gill III.1: no Eph 4:5 (from the OCR). Head IV (Tegg ii. 640) says sprinkling "cannot, with any propriety, be called a mode of baptism", with no Scripture on that sentence.
- **Pagination.** BSB's pages are not the pagination of the Tegg 1839 two-volume printing on archive.org: Tegg's III.1 runs about 40 pages from ii. 621, against BSB's 20 (896–915). PD locators therefore cite Tegg, and BSB pages are given only where checked.

## For the architect: Batch B questions, with my proposals

**B-Q1. Validity (2) has no Scripture-printing source that holds it.**
- Booth p. 280 note ‡ comes closest: a rite essentially different in mode and subject is not baptism. But it prints no Scripture.
- **Proposal:** Arguments from LBC 29.4 note (h) (Matt 3:16; John 3:23; "immersion … necessary to the due administration") and 29.2 note (f) (Mark 16:16; Acts 8:36–37), with no LBC Holding, as M5 does for 28.2 on (3). Booth enters as an `rdfs:comment`.

**B-Q2. Gill III.1 on the administrator reads against (3)'s clause.**
- (3) says "the administrator is a church of gospel order". Gill puts admission in the administrator's sole judgment and says baptism is not a church ordinance.
- Chris's testimony, recorded on the foreword ruling, is that Lee followed Gill and Spilsbury on the administrator ([PROPOSAL_validity_bsb_foreword.md](PROPOSAL_validity_bsb_foreword.md)). Gill's printed text is less churchly than that clause.
- **Proposal:** cite only LBC 28.2 for (3). Put Gill's opening paragraph on the follow-up console, asking whether it supports (3)'s administrator clause. Do not cite "Matt. iii. 1" for (3).

**B-Q3. Repetition has no Scripture-printing Baptist Argument.**
- **Option (a).** Belgic XXXIV, p. 427, prints Eph 4:5 for "once received, not repeated". The Argument's `rdfs:comment` would say that Belgic prints it only for the clause "baptism is administered once", and itself holds infant baptism.
- **Option (b).** Defer the Position until a Baptist source that prints Eph 4:5 is found. Booth's *Apology* (1778) and Gill's other tracts have not been searched.
- **Option (c), recommended.** Option (a), plus a Gill Holding on repetition, taught, with `dcterms:source` *Divine Right* ch. II (M1 lets a non-Scripture source ground a Holding).

**B-Q4. How the foreword is linked.** Your 2026-11-08 ruling says it is cited for (3), pp. vii–viii, props. 1 and 7. The open point is the triple that cites it.
- It is not a Body before phase 3, so it cannot ground a Holding. It prints no Scripture, so by M1 it cannot be an Argument.
- **Proposal:** a SourceDivision `source/bsb-gill-1984/foreword/vii-viii`, linked by `rdfs:seeAlso` from `source/plumb-line/validity-3` when the sitting writes it. That is where Chris's testimony connects the two.

**B-Q5. Sittings.**
- The follow-up console goes out only when every step-3 Position is minted, yet Batch C waits on F-B's answer from that same console.
- **Proposal:** two sittings.
  - **Sitting 1:** F-A (both wordings, and whether (ii)–(iii) exclude), F-B (Gill heads 2–4 and Sixthly), the Gill administrator paragraph (B-Q2), the 1677 margin letters for ch. 7, and tiers and values for everything minted.
  - **Sitting 2:** Batch C's values.

## Next, on your rulings

Batch B, locked: the validity Locus, with (2) per B-Q1, (3) per B-Q2 and B-Q4, and (4), plus the repetition Position per B-Q3. Then the console spec for sitting 1.
