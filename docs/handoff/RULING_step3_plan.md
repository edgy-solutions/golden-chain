# Ruling on the step-3 plan (Batch A accepted; M1–M11)

Relayed by Chris on 2026-11-08 and filed verbatim, as pasted. It answers [PLAN_step3_minting.md](PLAN_step3_minting.md).

```
ARCHITECT RULINGS — step 3 plan, Batch A accepted as minted; M1-M11.

Two findings first:
F-A. 23a(ii) wording outruns Coxe. Reword (ii) to what Coxe's text
     says, proposed from the pages (ch. II §§10-11), and put both
     the dispatch wording and Coxe's on the follow-up console for
     Chris. The dispatch wording was the architect's paraphrase; the
     Position must say what the source says.
F-B. Gill, Practical III.1 heads 2-4: "baptism is a means of leading
     faith to Christ" reads close to (a). Do not mint (b) as
     "representational only" until Chris has read those heads. Put
     heads 2-4 and "Sixthly" (p. 914) on the follow-up console with
     the question: is Gill's "means" the Spirit working THROUGH the
     rite (a), or the rite setting Christ before faith, the Spirit
     working by the Word (b)? Chris rules; the (b) wording follows
     his answer. The excludes edge waits on the same answer.

M1.  Accepted. A source that prints no Scripture is never an
     Argument; it enters as dcterms:source on a Holding, or as a
     note. A Position still needs >=1 Argument from some source that
     does print Scripture.
M2.  Accepted: source/plumb-line/validity-3, a SourceDivision of
     source/plumb-line, carrying Chris's statement verbatim and the
     signature of the sitting that writes it.
M3.  No new gc: term (rule 6). Notes on Arguments: rdfs:comment.
     Notes on edges: OWL annotated axiom (owl:Axiom with
     owl:annotatedSource/Property/Target) carrying rdfs:comment and,
     where needed, gc:status. Record as ADR-0002 Revision 2 (small).
     Until it lands, TTL comments are acceptable.
M4.  Passages enter an (a) Argument only from a source division whose
     text is about efficacy or instrumentality: WCF 27.3 and 28.6;
     Heidelberg 65 and 69-73 (Harbaugh 1889 or the 1863 Tercentenary
     edition, whichever scan is cleaner, PD either way); Belgic 33-34
     (Schaff, Creeds vol. 3, PD). NOT WCF 28.1, which is significance.
     Each passage comes from the source that prints it; where no
     (a)-source prints a passage (Acts 22:16, likely), (a) has no
     Argument on it and that is recorded, not padded.
M5.  Yes: body/gill is Gill's teaching across his works. Reclassify
     body/gill as gc:Teacher (the class from dispatch §12), with the
     Body of Divinity and the Divine Right as works beneath it. A
     Gill Holding on 23b-no from Divine Right ch. IV, taught.
     WCF holds NO validity position as a document: Hodge and
     Thornwell both claimed it, and the 1845 Old School Assembly
     ruled Romish baptism invalid against Hodge. Validity (1) is
     Hodge's; its Body is phase-2 American Presbyterian. Mint (1)
     only if a Hodge source printing Scripture is found (Systematic
     Theology III, the baptism chapter); otherwise defer (1) to
     phase 2 and mint (2), (3), (4) now. LBC holds no complete
     validity position; LBC 28.2 supports the administrator clause
     of (3) and is cited as such without an LBC Holding.
M6.  Record the refused direction as data: an owl:Axiom for the
     rejected edge with gc:status rejected and an rdfs:comment naming
     the refuting Holding (Augsburg on believers-and-their-infants
     without 23b-yes). Rejected edges never fire and are never
     deleted.
M7.  Noted.
M8.  Yes. Mint whole chapters as Passages: a chapter reference is the
     range from verse 1 to the last verse (canonicaliser expands it;
     IRI passage/kjv/Heb.8-Heb.10). Then cite them. Born test.
M9.  Yes: 23b yes excludes no; 23a (i), (ii), (iii) pairwise exclude.
     Nothing derived (§6 unratified).
M10. Yes: mint LBC holding on 23a(ii), taught, source LBC 7.3,
     status proposed. Chris reads the 1677 margin letters for ch. 7
     when he next has the facsimile open; until then asPrinted comes
     from the transcription, flagged.
M11. Resolve "Gal, 2, 17" to Col 2:17 with a resolutionNote; cite it
     when 7.6 is first used.

Proceed with Batch B (minus (1) unless Hodge prints Scripture) and
Batch C after Chris answers F-B. Lock counts per batch.
```
