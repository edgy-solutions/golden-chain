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

