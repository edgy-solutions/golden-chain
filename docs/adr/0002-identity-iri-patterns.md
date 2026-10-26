# ADR-0002: Identity: IRI patterns under https://w3id.org/golden-chain/

- Status: Ratified. **Revision 1 ratified by both architects (2026-10-25)**: the Golden Chain architect, and goat-yard's on (a) the `kjv` segment, (b) the reserved Anchor and (c) Passage IRIs naming locations only.
- Date proposed: 2026-10-25
- Date ratified: 2026-10-25
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
6. **Standard vocabulary first** (architect, report 2 Q4, 2026-10-25).
   Mint a `gc:` property only when no standard vocabulary term carries the
   meaning. For anything bibliographic, prefer `dcterms` (`dcterms:source`,
   `dcterms:bibliographicCitation`, `dcterms:isVersionOf`, …). First use:
   the LBC witness edition on `B source/lbc-1689` is a
   `dcterms:bibliographicCitation`.

### Patterns

| Resource | Pattern | Example |
|---|---|---|
| Ontology (document) | `B ontology` | `B ontology` |
| Ontology terms | `B ontology#{Term}` (prefix `gc:`) | `gc:Position`, `gc:holds` |
| Controlled vocab concept | `B vocab/{scheme}/{concept}` | `B vocab/modality/required` |
| Heading | `B heading/{slug}` | `B heading/worship` |
| Locus | `B locus/{slug}` | `B locus/baptism-subjects` |
| Position | `B position/{locus-slug}/{slug}` | `B position/baptism-subjects/professing-believers-only` |
| Passage (*revised, proposed*) | `B passage/{v11n}/{osisRef}` | `B passage/kjv/Matt.28.19-Matt.28.20` |
| Anchor (*reserved, none minted*) | `B anchor/{v11n}/{osisRef}/{selector}` | — |
| Source work | `B source/{work}` | `B source/gill-body` |
| Source division | `B source/{work}/{division path}` | `B source/gill-body/practical/3/1`, `B source/wcf/28/4` |
| Argument | `B argument/{work}/{division path}/{nnn}` | `B argument/gill-body/practical/3/1/007` |
| Body | `B body/{slug}` | `B body/plumb-line`, `B body/lbc-1689` |
| Holding (n-ary `holds`) | `B holding/{body}/{locus}/{position}[/{scope}]` | `B holding/wcf/baptism-subjects/believers-and-their-infants` |
| Agent (ADR-0005, ratified) | `B agent/{slug}` | `B agent/architect` |
| Inconsistency (derived only, *proposed*) | `B inconsistency/{body}/{rule}/{locus}/{position}/{locus}/{position}` | `B inconsistency/x/excludes/baptism-mode/immersion-only/baptism-mode/mode-indifferent` |
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
5. **Versification is in the IRI** (*revised*): the segment `{v11n}`
   names the scheme, lowercase. The default and, for now, the only one is
   `kjv` (the CrossWire SWORD `KJV` v11n). Each Passage also carries
   `gc:versification "kjv"`. A source using another numbering (e.g. Hebrew Mal 3:19–24 =
   KJV Mal 4:1–6, or psalm superscriptions) is mapped to KJV at ingest,
   and the source's own numbering is kept as a literal.

   **Provenance of the `kjv` table** ([goldenchain/versification.py](../../goldenchain/versification.py)):

   > Derived from CrossWire SWORD `include/canon.h` (KJV v11n), fetched 2026-10-25; verse counts re-keyed as facts, no code copied. Totals: 66 books / 1,189 chapters / 31,102 verses. Checked by `tests/test_versification.py`, and book by book against an independent USFM KJV by `tests/test_versification_usfm.py` (no differences, 2026-10-25).

   The line carries the elements of goat-yard's ratified truth-set form v1 (goat-yard-archive `docs/forms/TRUTH_SET_FORM.md` at commit `a0a30d4`, branch `apparatus-next`, published 2026-10-25; the later commit `1e6a923` amends only the verse-heading rect tolerance, not the provenance elements): what it is derived from, the date, the stated totals and the check. That form is written for page-span truth sets; this table borrows its provenance elements only.

   **A second v11n** (ratification of Revision 1): when one is minted, the mapping table between it and `kjv` is a repo artefact with its own provenance line in this form. It is born with the first non-`kjv` Passage.
6. **Ordinals for overlap.** Each Passage carries `gc:book`,
   `gc:startOrdinal`, `gc:endOrdinal` (verse index within the book under
   KJV v11n), so "try" can find every Passage overlapping a verse without
   per-verse IRIs.
7. **Validation.** A canonicaliser `goldenchain.passage.canonical(ref) ->
   iri` plus round-trip and bad-input tests are born with the first
   Passage. SHACL checks the IRI matches the grammar regex; ingest checks
   every Passage IRI with `goldenchain.passage.parse`.
8. **Cross-project.** goat-yard-archive uses **these same IRIs**
   (`B passage/…`), not its own copies, so a passage is one node across
   projects. (Alternative B below is a neutral namespace; Q14.)
9. **Passage IRIs name text locations only** (*revised*). A Passage carries
   its location (versification, book, osisRef, ordinals) and nothing else;
   the SHACL Passage shape is closed. Every resource that *cites* a
   location is distinct from it and has its own IRI: an Argument, a
   Holding, or an external region (e.g. a goat-yard page region). None of
   them is ever typed `gc:Passage` or merged into one.
10. **Sub-verse Anchor, reserved** (*revised*). A location finer than a
    verse (a clause, a word span) will be a `gc:Anchor` at
    `B anchor/{v11n}/{osisRef}/{selector}`, linked by `gc:inPassage` to its
    Passage. The selector grammar is not decided. **No Anchor is minted**
    until it is; a SHACL shape fails any `gc:Anchor`.

    **Requirement on the future grammar** (ratification of Revision 1): it
    must allow a text-anchored selector (a quoted phrase) alongside any
    offset form. Offsets depend on an edition's text, and Gill's lemmas
    are phrases. This constrains the grammar; it does not decide it.

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

## Ratification (2026-10-25)

- **Q13, Position sameness.**
  - The default is **one Position per distinct answer**, with every source that states it credited (by its Arguments and Holdings).
  - The build agent *proposes* merges, with evidence: the divisions compared and why the answers are the same. The **architect rules** on them.
  - A ruled merge deprecates the losing IRI (`owl:deprecated true`, `dcterms:isReplacedBy`), per general rule 3.
  - Proposals are listed in the phase handoff; no merge is applied silently.
- **Q14, Passage namespace.** Passages stay under `B passage/…`. goat-yard-archive adopts these IRIs, and there is no second namespace. Alternative B is closed.
- **Q15, scope.** Adopted (ADR-0003 §1).
  - The Holding pattern is `B holding/{body}/{locus}/{position}` when scope is `all`, the default.
  - For other scopes it is `B holding/{body}/{locus}/{position}/{scope}`, with `{scope}` ∈ {`officers`, `members`}.
  - Omitting the segment for `all` keeps the common case short. It is unambiguous because the segment count differs.

- **Page locator (architect, 2026-10-25).** The printed pages of a work's working text are stable, so they are an optional field beside the division reference, never part of an IRI.
  - The field is `gc:pages`, a literal: `"896"`, `"896-915"`, or roman for front matter.
  - It may appear on a Source division or an Argument.
  - The edition it refers to is stated once on the work, as `gc:paginationOf` on `B source/gill-body`, with the value `"BSB 2019 (ISBN 9781579780234), reproducing the 1839 London pagination"`.
  - Another edition's pages are never written to `gc:pages`.

## Open points (phase 1)

- **Augsburg source divisions: ruled (architect, 2026-10-25).** `B source/augsburg/{roman-article}`, lowercase (`B source/augsburg/ix`). Latin is the primary layer; German is a second literal. Sentence sections go in `gc:locator`, never in the IRI.
- **Book of Concord members** follow the same rule: `B source/apology-1531/ix`, `B source/small-catechism-1529/4` (the Small Catechism's parts are numbered, not articles). *Proposed.*
- **LBC chapters** keep the LBC's own numbers (`B source/lbc-1689/29/4`). The WCF↔LBC chapter concordance is data, not identity.

## Revision 1 (2026-10-25; ratified by both architects 2026-10-25)

Requested by the goat-yard terms before goat-yard-archive adopts the scheme:

1. The versification scheme is a segment of the Passage IRI:
   `B passage/{v11n}/{osisRef}`, default `kjv`. Rule 5 is rewritten.
   - Before: `B passage/Rom.6.4`. After: `B passage/kjv/Rom.6.4`.
   - Why: a second scheme (e.g. a Hebrew or LXX v11n) can then be minted without colliding, and a consumer never has to read the ontology to interpret an IRI.
2. A sub-verse Anchor resource shape is reserved (rule 10); none is minted.
3. Passage IRIs name text locations only; every citing resource is distinct (rule 9).
4. The `kjv` table carries a provenance line: derived from CrossWire SWORD `canon.h`, totals 66 / 1,189 / 31,102 (rule 5). Requested by goat-yard addition 3.

Effect on data: every phase-1 Passage is already minted in the revised form
(87 Passages at the time; 86 since the LBC 29 ruling). If review changes the form, they are regenerated by the
canonicaliser; no Passage IRI has been published outside this repo.

## Existing `gc:` properties and standard terms (ruling on report 3, Q2, 2026-10-25)

Nothing is migrated: general rule 6 (standard vocabulary first) is forward-looking. Why each property stays in `gc:`:
- **`gc:paginationOf`** has a specific meaning: "the pagination used is this edition's". No standard term says that.
- **`gc:quotationCheckedAgainst`**: no standard term.
- **`gc:pages`**: `bibo:pages` exists and was considered. Adding a vocabulary for one term fails the spirit of rule 6.
- **`gc:locator` and `gc:secondaryLocator`**: no standard term.
