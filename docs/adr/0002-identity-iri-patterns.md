# ADR-0002: Identity: IRI patterns under https://w3id.org/golden-chain/

- Status: Proposed
- Date proposed: 2026-10-25
- Date ratified:
- Proposed by: build agent
- Ratified by: architect

## Context

Every resource needs an IRI that never changes: user self-maps in Postgres,
Neo4j nodes, Weaviate objects and other projects all key on it. The
namespace `https://w3id.org/golden-chain/` is filed with w3id (PR #6977,
awaiting merge; see `docs/identity.md`) and redirects path-preserving to
`https://golden-chain.org/id/`. **goat-yard-archive will adopt the Passage
scheme**, so the Passage scheme is a public contract, not an internal
detail.

Below, `B` = `https://w3id.org/golden-chain/`.

## Decision

### General rules

1. **Slash IRIs** for all instances, so each resolves to its own page at
   `golden-chain.org/id/…`. The one exception is the ontology terms (below).
2. **Readable, stable slugs**: lowercase ASCII kebab-case, `[a-z0-9-]+`.
   Passage local parts are the exception and keep OSIS case.
3. **Never renamed, never reused.** A retired IRI stays in the data with
   `owl:deprecated true` and `dcterms:isReplacedBy <new>`.
4. No file extensions, no trailing slash, no query strings, no version
   numbers in instance IRIs.
5. IRIs carry **no source or holder** unless the resource is
   source-specific by nature (Argument, Source, Holding).

### Patterns

| Resource | Pattern | Example |
|---|---|---|
| Ontology (document) | `B ontology` | `B ontology` |
| Ontology terms | `B ontology#{Term}` (prefix `gc:`) | `gc:Position`, `gc:holds` |
| Controlled vocab concept | `B vocab/{scheme}/{concept}` | `B vocab/modality/required` |
| Heading | `B heading/{slug}` | `B heading/worship` |
| Locus | `B locus/{slug}` | `B locus/baptism-subjects` |
| Position | `B position/{locus-slug}/{slug}` | `B position/baptism-subjects/professing-believers-only` |
| Passage | `B passage/{osisRef}` | `B passage/Matt.28.19-Matt.28.20` |
| Source work | `B source/{work}` | `B source/gill-body` |
| Source division | `B source/{work}/{division path}` | `B source/gill-body/practical/3/1`, `B source/wcf/28/4` |
| Argument | `B argument/{work}/{division path}/{nnn}` | `B argument/gill-body/practical/3/1/007` |
| Body | `B body/{slug}` | `B body/plumb-line`, `B body/lbc-1689` |
| Holding (n-ary `holds`) | `B holding/{body}/{locus}/{position}[/{scope}]` | `B holding/wcf/baptism-subjects/believers-and-their-infants` |
| Named graph | `B graph/{file-stem}`; `B graph/derived/{rule-set}` | `B graph/gill-body-of-divinity` |

Notes on each:

- **Ontology terms use a hash namespace** (`B ontology#`). There are ~150
  lines in one document, so one dereference returns the whole vocabulary.
  The ontology carries `owl:versionIRI B ontology/{semver}`.
- **Position** is nested under its Locus because `answers` is functional:
  a Position answers exactly one Locus. A Position is **source-neutral**.
  It is the answer, not someone's statement of it. Who states it lives on
  Arguments and Holdings. Whether two sources' formulations are the *same*
  Position is an editorial decision (Q13), never inferred by a model.
- **Argument** IRIs use an opaque three-digit sequence per source division,
  assigned at minting and never reused. Finer locators (Gill's sub-heads,
  CCEL's `3e3b3c` outline, Tegg page) are literals on `gc:locator`, not
  IRI segments. They vary by edition; IRIs must not.
- **Source division paths** follow the author's own division, not an
  edition's:
  - Gill: `{doctrinal|practical}/{book}/{chapter}` and
    `dissertation/{chapter}`. Book numbers are Gill's (Doctrinal I–VII,
    Practical I–IV), not Tegg 1839's per-volume renumbering.
  - Confessions: `{chapter}/{paragraph}` (WCF 28.4 → `wcf/28/4`).
  - Sub-chapter heads (Gill's "First…Sixthly") may be addressed as
    `…/3/1/s3` if Arguments need it.
- **Body vs Source.** `B body/wcf` is the holder; `B source/wcf` is the
  document. A Confession-type Body is `gc:expressedIn` its Source. They are
  kept separate because Denominations (later) adopt a Source without
  being it.
- **Holding** is a node (n-ary relation) because `holds` carries a modality
  and possibly a scope (ADR-0003). Its IRI is deterministic, so a reload
  never duplicates it.

### Passage scheme (public contract)

1. **Grammar.** `{osisRef}` is an OSIS 2.1.1 `osisRef` restricted to:
   - a single verse `Book.C.V`, e.g. `Rom.6.4`, or
   - a contiguous range `Book.C.V-Book.C.V` within one book, e.g.
     `Rom.6.3-Rom.6.4`, `Matt.28.18-Matt.28.20`, `Acts.8.36-Acts.8.39`.
     Cross-chapter ranges are allowed (`Gen.17.1-Gen.18.2`).
   - Book codes are the OSIS canonical abbreviations (`Gen` … `Rev`,
     `1Cor`, `Phlm`, `Song`, `Ps`), case as OSIS defines it.
2. **Canonical form.** The start precedes the end. A range whose start
   equals its end is written as a single verse. Both ends are fully
   qualified (OSIS requires it). There are **no chapter-only or book-only
   IRIs**: "Psalm 23" is minted as `Ps.23.1-Ps.23.6`, expanded from the
   versification table at mint time, so one span has one IRI.
3. **Discontiguous citations** (Rom 6:3–4, 6) are two Passages. An Argument
   cites a list of Passages.
4. **Cross-book spans** are not Passages; split them.
5. **Versification: KJV** (the CrossWire SWORD `KJV` v11n). It is stated
   in the ontology as `gc:versification "KJV"` on the scheme and is not in
   the IRI. A source using another numbering (e.g. Hebrew Mal 3:19–24 =
   KJV Mal 4:1–6, or psalm superscriptions) is mapped to KJV at ingest,
   and the source's own numbering is kept as a literal.
6. **Ordinals for overlap.** Each Passage carries `gc:book`,
   `gc:startOrdinal`, `gc:endOrdinal` (verse index within the book under
   KJV v11n), so "try" can find every Passage overlapping a verse without
   per-verse IRIs.
7. **Validation.** A canonicaliser `goldenchain.passage.canonical(ref) ->
   iri` plus round-trip and bad-input tests are born with the first
   Passage. SHACL checks the IRI matches the grammar regex.
8. **Cross-project.** goat-yard-archive uses **these same IRIs**
   (`B passage/…`), not its own copies, so a passage is one node across
   projects. (Alternative B below is a neutral namespace; Q14.)

## Consequences

- IRIs are human-readable in Turtle and in URLs, which makes review
  easier.
- Slugs freeze wording decisions early. Bad names must be deprecated, not
  fixed; accept that.
- Position sameness across sources becomes an explicit editorial act.
- Passage IRIs depend on a versification table that must be in the repo
  (a `.py` or `.ttl` table of chapter/verse counts, KJV v11n; data, not
  text, so rule 4 is satisfied, but its source must still be reported).

## Alternatives considered

- **Opaque IRIs (UUIDs) for everything.** Stable but unreviewable. Rejected
  for Locus/Position/Body; used in spirit for Argument (sequence numbers).
- **Hash IRIs throughout.** Simpler to serve, but the whole graph would be
  one document. Rejected for instances.
- **Per-verse IRIs, with ranges as collections.** Heavy (31,102 verse nodes
  before any doctrine) and makes "a range" second-class. Rejected; ordinals
  give overlap without it.
- **Passages under a neutral namespace** (e.g. a second w3id id such as
  `w3id.org/osis-passage/`). Cleaner ownership for goat-yard-archive, at the
  cost of a second w3id PR and a second resolver. Kept open as Q14.
- **An existing Bible LOD scheme.** None found that is stable,
  range-capable and w3id-backed. Not pursued.

## Verification

- SHACL: each class's IRIs match its pattern regex.
- Unit tests: passage canonicalisation round-trips; `Ps.23` →
  `Ps.23.1-Ps.23.6`; `Rom.6.4-Rom.6.4` → `Rom.6.4`; reversed range rejected;
  cross-book rejected; unknown book rejected.
- Guard: no IRI in `data/` outside `B`, except external vocabularies
  (rdf, rdfs, owl, skos, dcterms, sh, xsd).

## Open points

- Q13: who rules two formulations the same Position, and how that is
  recorded.
- Q14: Passage namespace, shared (this ADR) or neutral.
- Q15: scope segment on Holding (`/officers`, `/members`), needed only if
  ADR-0003 adopts scope.
