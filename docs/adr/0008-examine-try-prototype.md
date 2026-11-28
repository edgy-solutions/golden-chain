# ADR-0008: A read-only local prototype of `examine` and `try`

- Status: Ratified as a local prototype (ruling on report 19, A-3)
- Date proposed: 2026-11-15
- Date ratified: 2026-11-17
- Proposed by: build agent (overnight order 2026-11-15, item 7)
- Ratified by: architect

A prototype only. It is generated locally, it is not deployed, and every page
says so. Nothing here commits the project to a reader, a server or a design.

## Context

- The data is queryable (Jena TDB2, ADR-0001) and weigh scores Bodies, but no
  page shows a reader what the data holds for one question (`examine`) or one
  Scripture passage (`try`).
- Rule 3: no model asserts doctrine. A reader page is where a model's prose
  would most easily slip in. The prototype must show that pages can be built
  from the data alone.
- Rule 4: no Bible text is stored. A passage page shows the reference, never
  the verse.

## Decision (proposed)

1. **A static generator**, `tools/prototype/examine_try.py`. It queries the
   TDB2 store that ingest builds (`tdb2.tdbquery`, union default graph). The
   same SPARQL runs over the rdflib mirror for tests and as a cross-check.
   It writes HTML under `~/.golden-chain/prototype/<head12>/`, outside the
   repo. No server, no script, no external URL.
2. **Two page kinds and an index.**
   - `examine/<locus>.html`: the Locus label and question; each Position with
     its Arguments (source, locator, secondary locator, `gc:asPrinted`, status,
     proposedBy, ratifiedBy) and the passages each cites (linked); a Holdings
     table (Body × Position, modality and scope), from effective Holdings.
   - `try/<passage>.html`: the passage reference and every Argument that cites
     it by `gc:cites`, grouped by Position, with its Locus linked. A passage
     cited only by `gc:citesCandidate` gets no page (it is listed, unlinked,
     as "candidate" on the locus page).
3. **Only data strings.** A page renders labels, questions, locators,
   `gc:asPrinted`, osisRefs, vocabulary labels and IRI tails, and nothing else.
   It never renders `rdfs:comment`, `gc:resolutionNote`, `gc:quotation`,
   `gc:derivedBy` or any free text. The only fixed words are a banner and the
   section headings. A test enforces this with sentinel strings.
4. **The banner**, on every page: "PROTOTYPE — local only, not deployed.
   Generated from the data at <head12>; every line below is a label, a locator
   or a signed record."
5. **Deterministic.** Everything is sorted by IRI. The git HEAD and the store's
   `gc.trig` sha256 go in a footer and in `run_header.json`. Two runs are
   byte-identical.

## Consequences

- One tool and one test file. No data, ontology or shape changes.
- `gc:asPrinted` strings that are model-proposed (LBC 1677, ruling on report
  18) are shown as data with their status. The page does not show the
  `rdfs:comment` that says so, by Decision 3. Open point 1 asks whether that is
  acceptable for a prototype.

## Alternatives considered

- **A live server over Fuseki.** Rejected for a prototype: more surface, and
  nothing to look at that static pages cannot show.
- **Render `rdfs:comment`.** Rejected: comments are written by the build agent
  or the architect, so they are model prose.

## Verification (locked first)

`prototype-examine-try-predictions-locked.txt`, PX1–PX7: 153 pages (1 index,
12 examine, 140 try); 24 Positions and 80 Arguments with the per-locus counts;
217 cites rows; 54 effective Holdings over 7 Bodies; the banner on every page
and no excluded string anywhere; two runs byte-identical; suite and weigh
unchanged and no data changed.

## Open points

1. A model-proposed `asPrinted` is shown without its disclosure comment. Should
   the page mark it (needs a typed property; see report 19), or is the status
   enough for a local prototype? (Architect.)
2. Is a passage page with only references, no verse text, useful? A reader
   would need their own Bible open. A licensed or PD text is a separate ADR.
   (Architect.)
3. Is any of this to be deployed later? (Architect; a separate ADR.)

## Ratification (2026-11-17; ruling on report 19, A-3)

Ratified as a local prototype. The open points are answered:

1. **Disclosure**, per A-1 ([ADR-0002 Revision 3](0002-identity-iri-patterns.md)):
   - the tool reads the `owl:Axiom` on each `gc:asPrinted` triple;
   - while the axiom's status is `proposed`, it prints "proposed reading, unconfirmed" beside the string;
   - the query's allow-list gains `owl:annotatedSource`, `owl:annotatedProperty` and `owl:annotatedTarget`;
   - the axiom's `rdfs:comment` is still never read.
2. **Passage pages show the reference only** until ADR-0004 settles the display text. That is already so, because no verse text is stored.
3. **Deployment** is a separate ADR.


## Revision 1 (proposed 2026-11-27, on the two-day order, Day 2, item 7): a weigh page and Body pages

- Status: **Proposed.** The order allows the prototype to be built ahead of ratification, because it is local, read-only and mints nothing ([RULING_report_31.md](../handoff/RULING_report_31.md)). It is built under the lock [LOCK_item7_weigh_body_pages_2026-11-27.md](../handoff/LOCK_item7_weigh_body_pages_2026-11-27.md).
- The order, verbatim: "Extend the examine/try prototype with a weigh page and a Body page, generated from weigh's output and the data: the three groups (could join; could join with stated differences; could not join), walls shown apart from differences, the "not a church by this site's standard" listing with its derivation and the unsigned-statement line, each claim with its source. No sentence that is not a label, a locator or a signed record."

### Decision (proposed)

1. **Two page kinds**, written by the same generator next to the others:
   - `weigh.html`: weigh against the plumb-line, scope members;
   - `body/<slug>.html`: one per Body that weigh weighs or lists. The plumb-line gets none.
   - `index.html` gains one link, to `weigh.html`. No existing page changes.
2. **Weigh is the only scorer.** The pages come from `goldenchain.weigh` and `goldenchain.unchurches`, run on the same rdflib dataset as weigh's CLI. The generator never re-scores. For a cell's Holding and source it reads weigh's own cell rule. Nothing in `goldenchain/` changes.
3. **The three groups, as the build agent reads them** (open point 1):

   | Group | A ranked Body is in it when |
   |---|---|
   | could join | no wall, at least one covered locus, and every covered locus's cell is 0 |
   | could join with stated differences | no wall, and at least one covered, non-wall locus has a cell above 0 |
   | could not join | at least one wall |
   | no locus covered (listed apart) | no wall and no covered locus |

   - A Body weigh excludes is in no group. It is in the listing "Not a church by this site's standard", with its derivation: the Holding's Position, its modality, its sources, and the plumb-line sitting that flags the Position.
   - The fourth line is not one of the order's groups. Without it a Body that weigh has nothing to weigh on would be shown as "could join" (open point 2).
4. **Walls apart from differences.** A Body page lists its walls, then its differences, under separate headings.
   - A **difference** is a covered, non-wall locus whose cell is above 0. One at 0.25 or more is marked "break", as weigh's R2.7 (4) defines it.
   - Each wall and each difference shows the Position, the Body's modality against the plumb-line's, and the source IRIs of the Body's Holding there.
5. **The words on the page.** These are the only words on the new pages:
   - labels, IRI tails, vocabulary tails and numbers;
   - the banner, the section headings and the group names;
   - the ruled wordings, imported from code and never retyped: `unchurches.UNSIGNED` (the unsigned-statement line), `HEADING`, `WORDING` and `MEMBERS`, and `weigh.CONSEQUENCE`.

   The ruled wordings are sentences. They are not labels, locators or signed records (open point 3).
6. **The same guards as the ratified prototype:** the banner on every page, no `rdfs:comment`, `gc:resolutionNote`, `gc:quotation` or `gc:derivedBy`, everything sorted by IRI, and two runs byte-identical.

### Verification

The lock's WX1-WX7: the groups and the listing as weigh's output gives them at `9d6dae3`; 7 Body pages; the existing pages unchanged; the banner and sentinels; determinism; and weigh's CLI output, `data/` and `goldenchain/` unchanged.

### Open points

1. **The groups' reading.** Is "could join with stated differences" any nonzero cell, as proposed, or only a break (a cell of 0.25 or more)? With the data at `9d6dae3` the two readings give the same groups, because the one difference is 0.75.
2. **The fourth line.** Should a Body with no covered locus be listed apart, as proposed? Or should it be left off the weigh page?
3. **The ruled wordings.** Do `UNSIGNED`, `HEADING`, `WORDING`, `MEMBERS` and `CONSEQUENCE` count as allowed fixed words under "no sentence that is not a label, a locator or a signed record"? The order names the unsigned-statement line, so at least that one is required.
4. **Scope.** Only "members" is generated. Should there be an "officers" weigh page too?
5. **Comparison views** (ADR-0003 R3.3, weighing from another Body's Holdings) are not generated. Are they wanted in the prototype?
