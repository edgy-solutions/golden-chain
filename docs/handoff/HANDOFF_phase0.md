# Handoff: phase 0

- Branch: `phase-0` (local; not pushed)
- State: **phase 0 complete; stopped at (g).** Phase 1 not begun.
- Waiting on: architect ratification of ADR-0001..0003 and answers below.

## Done

| Item | Output |
|---|---|
| (a) git status | Empty repo: no commits on any branch, no files, clean. Remote `edgy-solutions/golden-chain` has no refs. `main` does not exist (Q2). |
| (b) w3id | Recorded in [identity.md](../identity.md): PR perma-id/w3id.org#6977, open, mergeable, no reviews. Fork not touched. |
| (c) Gill source | [sources/gill-body-of-divinity.md](../sources/gill-body-of-divinity.md). Recommendation: cite Gill's own division; CCEL is the locator; Tegg 1839 page images (IA) are the witness; no CCEL text in the repo. |
| (d) Loci | [loci/locus-vocabulary-draft.md](../loci/locus-vocabulary-draft.md): 42 loci (God 6, Scripture 2, Man 4, Christ 4, Salvation 7, Church 4, Worship 12, Last things 3); 17 from Practical Divinity; 30 with a named alternative (S/T/L evidence classes), 12 with none found. |
| (e) ADRs | [0001](../adr/0001-store-roles-and-single-ingest-path.md), [0002](../adr/0002-identity-iri-patterns.md), [0003](../adr/0003-controlled-vocabularies-and-scoring.md), plus [0000-template](../adr/0000-template.md) (Q1). |
| (f) Layout | [docs/README.md](../README.md). |

## Predicted vs actual

| What | Predicted | Actual | Note |
|---|---|---|---|
| Gill chapters | 156 (107 D + 49 P incl. appendix) | 107 + 44 + 5 = 156 | Match |
| Doctrinal per book | — | 31/16/13/7/14/15/11 | |
| Practical per book | — | 24/6/8/6 + Diss. 5 | |
| CCEL book numbering = Tegg 1839 book numbering | equal | **diverges** | Tegg renumbers books per volume (v.2 Book V = Practical III). Finding; it drove the edition-independent citation key in ADR-0002. |
| CCEL headings correct | yes | **one wrong** | Practical I.8: CCEL "Of the Grace of God"; Tegg contents "Of Hope". |

## Findings that are not questions

- No `python` on PATH; the `py` launcher has 3.9, 3.10, 3.11. Java 17 is on
  PATH (enough for Jena 5 / Fuseki 5).
- CCEL's terms ("personal, educational, or non-profit"; ask before
  republishing) restrict the transcription even though Gill's text is PD,
  so the plan keeps CCEL text out of the repo.
- The CCEL outline numbering (`3e3b3c4f`) is CCEL's normalisation, so it is
  usable as a locator literal but never as identity.
- In the named-alternative column, "—" means the heuristic found no name,
  not that Gill argues against no one.

## Open questions for the architect

1. **ADR template.** The brief cites "the template already in the repo";
   the repo was empty. Accept `docs/adr/0000-template.md` or supply yours.
2. **Branches.** No `main` exists; `phase-0` holds the root commit. Create
   `main` from the ratified `phase-0`? Push `phase-0` to origin now?
3. **Source policy.** Ratify the plan in the source report: Gill's own
   division as the key, CCEL as locator, Tegg 1839 as witness, no CCEL text
   in the repo. Are short verbatim quotations (checked against the page
   images) allowed on Arguments, and if so, what length cap?
4. **Rule 3 and authored data.** In phase 1 I would draft Positions,
   Arguments, `excludes` edges and confession Holdings. Proposal: every
   drafted resource carries `prov:wasAttributedTo <build-agent>` and
   `gc:reviewStatus "proposed"` until you ratify it; Argument text is a
   verbatim quotation or absent, **never a paraphrase**. Agree?
5. **Cost cells.** Ratify or replace the proposed (ᴾ) cells in ADR-0003
   §5, above all *obligatory × forbidden = WALL*.
6. **Tier weights** 9/3/1 (ADR-0003 §5).
7. **Inheritance override grain.** Per Locus (proposed) or per Position?
8. **Plumb-line vs Body distance.** What mapping from body modality to
   user modality (ADR-0003 Q8)?
9. **Tier ownership.** Is tier asserted by plumb-line (proposed) or a
   global property of the Locus? The brief lists it on Locus.
10. **Contested weight.** Full weight with a badge (proposed), or reduced?
11. **`proselyte-baptism-origin`**: is it a Locus, or an Argument under
    `baptism-subjects`? Gill wrote it as an appendix serving that locus.
12. **Phase 1 baptism scope.** The six P III.1 loci (28–33), plus 34? Plus
    36 `supper-subjects` (baptism as prerequisite)? Plus 23
    `covenant-administrations`, which the paedobaptist case rests on?
13. **Position sameness.** When Gill, WCF and LBC state "the same" answer,
    who rules them one Position, and how is that recorded?
14. **Passage namespace.** goat-yard-archive reuses `B passage/…` as-is
    (proposed), or a neutral namespace (second w3id PR) before any
    Passage is minted?
15. **Scope on Holdings** (`all|officers|members`): adopt now so phase
    1(c) can express officer-vs-member modality, or wait for the phase 1
    report?
16. **Third confession.** "Structurally different": options are the
    Augsburg Confession 1530 (Lutheran; article form; gives baptism and
    Supper loci a third distinct answer), the Heidelberg Catechism (Q&A
    form, Reformed), or Schleitheim 1527 (Anabaptist; seven articles, not
    systematic). I lean Augsburg. Needs a PD English translation reported
    under rule 4 before ingest.
17. **Plumb-line content.** Phase 1(d) needs the plumb-line's baptism
    positions and clarity flags. Under rule 3 I cannot choose them. Will
    you supply them, or should I prepare a blank form (loci × positions ×
    modality/clarity) for you to fill?
18. **What "excludes fires" means for 1(e).** Proposal: `excludes` is
    asserted per Position pair (editorial, not inferred from sharing a
    Locus). The reasoner adds the symmetric closure and
    `entails ∘ excludes ⊑ excludes`. A SPARQL/SHACL check flags any Body
    that requires or teaches two mutually excluding Positions. The phase 1
    test asserts the symmetric edge appears between the paedo and credo
    Positions on `baptism-subjects`. Agree?
19. **Python toolchain.** Python 3.11 via `py -3.11`, a gitignored `.venv`,
    rdflib + pySHACL for tests, and the Jena `fuseki-server` jar for
    1(e)? (ADR-0001 open points 1–2.)
20. **Scripture text licence** (later): KJV is Crown-patent in the UK.
    Phase 1 stores references only, so this can wait, but it needs an ADR
    before any verse text enters any store.

## If told "continue" (after ratification)

Phase 1 per the brief, in order: amend the ADRs per your answers;
`ontology/core.ttl` + `ontology/shapes.ttl`; the passage canonicaliser and
its tests; the baptism loci from Gill (with predicted counts stated
first); WCF and LBC Holdings; the plumb-line from your input (Q17); local
Fuseki load and reasoner; guard tests; pre-commit hook; then stop and
report.

Before any of that: a source report for WCF and LBC 1689 texts (edition,
licence) per rule 4.
