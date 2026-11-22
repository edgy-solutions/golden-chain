# ADR-0009: State the scope of the published documents included, who decides it, and how it is shown

- Status: Proposed (sent up for review; nothing is built until ratified)
- Date proposed: 2026-11-22
- Date ratified:
- Proposed by: build agent, on the architect's draft ([RULING_site_ground_2026-11-22.md](../handoff/RULING_site_ground_2026-11-22.md), item 2)
- Ratified by: architect

## Context

- The site's second commitment is the scope of published documents included (ADR-0003 Revision 3, proposed, R3.1).
- A reader who weighs Bodies needs to know which documents are in the data and which are not. Otherwise a Body missing from a ranking reads as a judgment on it.
- Today scope is implicit: whatever has a `B source/...` node and a signed record. Phase 2 adds sources (the phase-2 locus table), and ADR-0007 adds Congregations' own statements.
- Standing rules served: 2 (a Position needs a source), 4 (only PD or licensed text), 5 (ADR before building), 8 (stop when uncertain).

## Decision (proposed)

1. **What "in scope" means.** A document is in scope when all of these hold:
   - it is published, in print or publicly posted;
   - it is attributable to a Body or a named author;
   - it is public domain or licensed (rule 4);
   - it has a page witness that can be cited by locator.
2. **Who decides.**
   - The build agent proposes a document, with its witness, its PD or licence status and the Body it would ground. It never adds one silently.
   - The architect rules on the criteria and on borderline cases.
   - Chris includes a document by signing it in. The inclusion is a signed record, as every other act is.
   - A Congregation's own statement enters only through ADR-0007's form and is in scope by that route.
3. **How it is recorded (proposed).** On each source node:
   - `gc:includedBy <agent/chris>`;
   - `gc:includedOn` (an xsd:date);
   - `gc:inclusionRecord` (the signed record's file name).

   A document considered and left out is recorded as `<source/...> gc:excludedFromScope "<reason>"`, with the same three properties. This keeps "not yet included" distinct from "considered and left out".
4. **How it is shown.**
   - A public "Documents included" page lists each in-scope source: title, edition and witness, date, the Body it grounds, and its inclusion record.
   - A second list gives the documents considered and left out, each with its reason.
   - Weigh's output ends with one line: "Weighed over N documents in scope; see Documents included."
   - A Body that is not in the data is never ranked and never described. Absence means "not included", never a judgment.

## Consequences

- Easier: a reader can test the site's coverage against its claims, and a missing tradition is visibly missing, not silently judged.
- Harder: every new source needs an inclusion record, which is one more signature for Chris.
- Forbidden: ranking or describing a Body from a document that is not in scope; adding a source without a signed inclusion.

## Alternatives considered

- **Implicit scope (status quo).** Rejected: the reader cannot tell coverage from judgment.
- **The architect decides inclusion.** Rejected in this draft: every other act that enters the data is Chris's signature. The architect rules on the criteria instead.
- **A scope list in prose only (README).** Rejected: it would drift from the data. Deriving the page from the source nodes keeps them one thing.

## Verification (to be locked before any build, if ratified)

Sketch only, for review:
- every `B source/...` node has `gc:includedBy`, `gc:includedOn` and `gc:inclusionRecord`, or `gc:excludedFromScope`. This is a SHACL check, with the existing sources backfilled under one signed record;
- the Documents included page is generated from the data and lists exactly the in-scope sources;
- weigh's closing line counts them;
- weigh is otherwise byte-identical, with new hashes locked first.

## Open points

1. **Backfill.** The existing sources (WCF, LBC, Gill, BSB, Augsburg and others) entered through earlier signed records. Proposed: one inclusion console that lists them all for Chris to sign as a batch.
2. **Granularity.** Is scope set per document (WCF) or per edition (WCF 1647 vs a later American text, which ADR-0002 already treats as separate Sources)? Proposed: per Source node, so per edition where the data has separate editions.
3. **Systematic works and Teachers.** Are they in scope as Bodies, or only as witnesses for Arguments? Proposed: both are possible, and the page says which role each plays.
4. **Licensed but private texts** (for example the Lee corpus). Proposed: out of the public page's text, listed by title only, with "licensed, not reproduced".
