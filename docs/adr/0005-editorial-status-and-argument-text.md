# ADR-0005: Editorial status, provenance, and Argument text

- Status: Proposed (records the architect's ruling on Q4 of 2026-10-25; the
  vocabulary and shapes below are the build agent's and need ratification)
- Date proposed: 2026-10-25
- Date ratified:
- Proposed by: build agent
- Ratified by: architect

ADR-0004 is reserved for the Scripture translation (ADR-0001, Ratification
§3).

## Context

- **Rule 3**: no LLM asserts doctrine in any output.
- **Rule 2**: every Position traces to a source chapter and carries at least one Passage via an Argument.

In phase 1 the build agent drafts Positions, Arguments and Holdings from the
sources. A draft is a proposal about what a source says. It is not doctrine,
and it becomes data only when the architect ratifies it.

The architect ruled (Q4) that:
- Positions, Arguments and holds edges carry `status: proposed` and `proposedBy` until ratified.
- Argument text is a quotation (within the quotation scope) or absent, never a paraphrase.
- This is enforced as a SHACL shape.

## Decision

### 1. Status vocabulary: `B vocab/status/`

| Concept | Meaning |
|---|---|
| `proposed` | Drafted. Not data the product may present as a source's teaching without the label "proposed". |
| `ratified` | Accepted by the architect. |

Deprecation stays `owl:deprecated` (ADR-0002); it is not a status.

### 2. Properties

| Property | Range | On |
|---|---|---|
| `gc:status` | `B vocab/status/*`, exactly 1 | `gc:Position`, `gc:Argument`, `gc:Holding` |
| `gc:proposedBy` | `gc:Agent`, exactly 1 | the same |
| `gc:ratifiedBy` | `gc:Agent`, exactly 1 iff status = ratified | the same |
| `dcterms:dateAccepted` | `xsd:date`, exactly 1 iff status = ratified | the same |

- **Agents** are `B agent/{slug}`: `B agent/build-agent` and `B agent/architect`. This is a new pattern alongside ADR-0002's table.
- The build agent never writes `ratified`. Ratification is a commit by, or on the instruction of, the architect.

### 3. Argument text

- An Argument carries **no prose of its own**. Its content is:
  - `gc:source`: exactly one source division IRI;
  - `gc:locator`: optional literals naming Gill's sub-head, e.g. `"§3, Fourthly"`;
  - `gc:pages`: optional, the printed pages in the working text (ADR-0002);
  - `gc:cites`: one or more Passages;
  - `gc:supports`: exactly one Position.
- **`gc:quotation`** is the only text property allowed on an Argument. It is a verbatim quotation from the source division, within the quotation scope.
- **The quotation scope is filled** (architect, 2026-10-25): display and quotation are permitted.
  - Gill's text is public domain.
  - Every quotation is verified against the page image.
  - Front matter is excluded.
  - The confessions keep "reference only" until a quotation source is ruled for each (their source reports).
  - The shape therefore allows **at most one `gc:quotation`** per Argument, and only together with the two properties below.
- The Argument shape is **`sh:closed`**, with `rdf:type` and the properties above. Any other text property (`rdfs:comment`, `dcterms:description`, `skos:note`, `rdfs:label`) fails validation. A paraphrase therefore has nowhere to go.
- A `gc:quotation` requires:
  - **`gc:quotationCheckedAgainst`**: the page image read, as a literal naming the edition and printed page, e.g. `"BSB 2019 p. 899"`;
  - **`gc:pages`**: the printed page or pages.
- OCR output is never a quotation source. It only finds the page.
- No sentence cap is set. If one is ruled, the shape enforces it as a length bound.

### 4. Edges between Positions

`entails` and `excludes` are plain triples between Positions. They have no
status of their own: an edge is as ratified as the **less ratified** of its
two Positions.

## Consequences

- Every phase-1 resource the build agent drafts is visibly `proposed`. A query for ratified doctrine returns nothing until the architect acts. That is correct.
- No summary text exists anywhere in the data. Rendering an Argument shows the source division, locators and Passages, and the reader goes to the page.
- Ratification is a diff: `status` flips and `ratifiedBy` and `dateAccepted` are added.

## Alternatives considered

- **`prov:wasAttributedTo` and `bibo:status`** instead of `gc:` terms. Workable, but the brief names `status` and `proposedBy`, and one `gc:` vocabulary keeps the SHACL shapes simple. PROV alignment can be added as `rdfs:subPropertyOf` later.
- **Reifying `entails` and `excludes` edges** (RDF-star or relation nodes) to give them their own status. Heavier, and rdflib's RDF-star support is incomplete. Rejected for phase 1. It is revisited if the architect wants to ratify an edge independently of its Positions.
- **An open Argument shape with a "summary" field marked proposed.** Rejected: that would be an LLM paraphrase of doctrine (rule 3).

## Verification

- SHACL tests:
  - A Position, Argument or Holding without `gc:status`, or without `gc:proposedBy`, fails.
  - `ratified` without `gc:ratifiedBy` or `dcterms:dateAccepted` fails.
  - An Argument carrying `gc:quotation` without `gc:quotationCheckedAgainst` or without `gc:pages` fails.
  - An Argument carrying two `gc:quotation`s fails.
  - An Argument carrying `rdfs:comment` fails (closed shape).
- A guard test asserts that no resource in `data/` other than the plumb-line has `gc:status vocab/status/ratified` unless `gc:ratifiedBy` is `B agent/architect`.

## Open points

- Ratify `B agent/{slug}` as an ADR-0002 pattern.
- Status on edges (§4): is "as ratified as the weaker Position" acceptable?
- The plumb-line's own resources are authored by the architect. Do they carry `status ratified` directly, or skip status? Proposed: they carry it, with `proposedBy` and `ratifiedBy` both `B agent/architect`, so the shape stays uniform.
