# ADR-0009: State the scope of the published documents included, who decides it, and how it is shown

- Status: Ratified with changes, 2026-11-22 ([RULING_report_22.md](../handoff/RULING_report_22.md)). Not yet built; the build is locked first.
- Date proposed: 2026-11-22
- Date ratified: 2026-11-22
- Proposed by: build agent, on the architect's draft ([RULING_site_ground_2026-11-22.md](../handoff/RULING_site_ground_2026-11-22.md), item 2)
- Ratified by: architect

## Context

- The site's second commitment is the scope of published documents included (ADR-0003 Revision 3, proposed, R3.1).
- A reader who weighs Bodies needs to know which documents are in the data and which are not. Otherwise a Body missing from a ranking reads as a judgment on it.
- Today scope is implicit: whatever has a `B source/...` node and a signed record. Phase 2 adds sources (the phase-2 locus table), and ADR-0007 adds Congregations' own statements.
- Standing rules served: 2 (a Position needs a source), 4 (only PD or licensed text), 5 (ADR before building), 8 (stop when uncertain).

## Decision

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
3. **How it is recorded (as ratified: no new `gc:` properties, ADR-0002 rule 6).** Inclusion uses what Holdings already use. On each source node:
   - `gc:status <vocab/status/ratified>`;
   - `gc:ratifiedBy <agent/chris>`;
   - `dcterms:dateAccepted` (an xsd:date);
   - the signed record's name, recorded as Holdings record it.

   A document considered and left out is `gc:status <vocab/status/rejected>`, with the reason as `rdfs:comment`. A source with neither status is **"not yet considered"**. This keeps the three states apart.

   *(Drafted, and withdrawn by the ruling: `gc:includedBy`, `gc:includedOn`, `gc:inclusionRecord`, `gc:excludedFromScope`.)*
4. **How it is shown.**
   - A public "Documents included" page lists each in-scope source: title, edition and witness, date, the Body it grounds, and its inclusion record.
   - A second list gives the documents considered and left out, each with its reason.
   - Weigh's output ends with one line: "Weighed over N documents in scope; see Documents included."
   - A Body that is not in the data is never ranked and never described. Absence means "not included", never a judgment.
5. **The four criteria are formal; the doctrinal boundary is Chris's statement (added by the ruling).** The criteria in Decision 1 are formal tests only. The doctrinal boundary of scope (which traditions the site covers, and why) is **Chris's statement, written and signed by him on a console**, stored and shown like the humility statement (ADR-0003 R3.2). **No model drafts it.**

## Consequences

- Easier: a reader can test the site's coverage against its claims, and a missing tradition is visibly missing, not silently judged.
- Harder: every new source needs an inclusion record, which is one more signature for Chris.
- Forbidden: ranking or describing a Body from a document that is not in scope; adding a source without a signed inclusion.

## Alternatives considered

- **Implicit scope (status quo).** Rejected: the reader cannot tell coverage from judgment.
- **The architect decides inclusion.** Rejected in this draft: every other act that enters the data is Chris's signature. The architect rules on the criteria instead.
- **A scope list in prose only (README).** Rejected: it would drift from the data. Deriving the page from the source nodes keeps them one thing.

## Verification (to be locked before any build)

Sketch only, for review:
- every `B source/...` node that has `gc:status ratified` also has `gc:ratifiedBy <agent/chris>`, `dcterms:dateAccepted` and its record's name; every one with `gc:status rejected` has an `rdfs:comment`. This is a SHACL check, with the existing sources backfilled under one signed record;
- a source with neither status is listed as "not yet considered", never as included;
- no scope-boundary text appears in the data until Chris's signed statement supplies it (Decision 5);
- the Documents included page is generated from the data and lists exactly the in-scope sources;
- weigh's closing line counts them;
- weigh is otherwise byte-identical, with new hashes locked first.

## Open points: resolved by the ruling (2026-11-22)

1. **Backfill.** One backfill console that lists the existing sources (WCF, LBC, Gill, BSB, Augsburg and others), signed by Chris as a batch.
   - *Added by the ruling on report 23 (A-5):* the same console also offers Owen, *Exposition of the Epistle to the Hebrews*, in the Goold edition (vols. 19 and 23), which is not yet a Source in the data. See [owen-hebrews.md](../sources/phase2/owen-hebrews.md).
2. **Granularity.** Per Source node, so per edition where the data has separate editions.
3. **Systematic works and Teachers.** The page states each work's role: Body, witness, or both.
4. **Licensed but private texts.** Listed by title as "licensed, not reproduced", and **only once written permission is on file**.

## Points resolved by the ruling on report 28 (2026-11-26, item 10)

1. **The site's own standard (Q-I-1).** `source/plumb-line` (the signed sittings) is not a published document under this ADR. It is not offered for inclusion, and it is not counted in weigh's closing line. The Documents included page lists it under its own heading, **"the site's standard"**, apart from the sources.
2. **How the signed statements and inclusions enter the data (Q-I-2).** In one locked change, as proposed: the humility statement, the scope statement, and every inclusion row of one signed statements console together.
3. **Owen (Q-I-3).** Owen's *Exposition of the Epistle to the Hebrews* is one Source. Volume and page are the locator.
4. **The BSB 1984 foreword (Q-I-4).** Chris decides on the row. If he includes it, its entry is labelled **"short extracts only; written confirmation to be sought before launch"**. (The architect's reason: the foreword is already cited for validity (3), and short quotation was ruled permitted, so "not now" would contradict the data.)
