# ADR-0005: Editorial status, provenance, and Argument text

- Status: **Ratified provisionally** (architect, 2026-10-25, ruling 9:
  "ratified provisionally on your description; I will read the text").
  Amended the same day with the rule-2 clarification (ruling 2), the
  quotation cap (carried item), and the citation properties ruled for
  printed slips (ruling 6) and locators (ruling 7). Amendments are marked
  *amended*.
- Date proposed: 2026-10-25
- Date ratified: 2026-10-25 (provisional)
- Proposed by: build agent
- Ratified by: architect

ADR-0004 is reserved for the Scripture translation (ADR-0001, Ratification
§3).

## Context

- **Rule 3**: no LLM asserts doctrine in any output.
- **Rule 2**: every Position traces to a source chapter and carries at least one Passage via an Argument.
  - *Amended, clarified (architect, ruling 2):* a Position needs **at least one Argument from some source**. A Holding does not need an Argument of its own.
  - Augsburg holds the efficacy Position. The Apology IX and the Small Catechism IV, from the same PD Triglot, supply its Arguments, each credited to its own source Body.
  - Rule 2 is not relaxed. The Position shape enforces it (`^gc:supports` min 1); the Holding shape requires `dcterms:source` but no Argument.

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

- **Agents** are `B agent/{slug}`: `B agent/build-agent` and `B agent/architect`. This is a new pattern, now listed in ADR-0002's table.
- The build agent never writes `ratified`. Ratification is a commit by, or on the instruction of, the architect.
- *Amended:* the shape allows `gc:ratifiedBy` only as `B agent/architect`.
- A Holding whose modality is read by implication carries `gc:derivedBy "implication"` (ruling 4).

### 3. Argument text

- An Argument carries **no prose of its own**. Its content is:
  - `gc:source`: exactly one source division IRI;
  - `gc:locator`: *amended* to **at most one**. It is the primary locator: the author's own printed division, e.g. `"Thirdly, 2."` (ruling 7);
  - `gc:secondaryLocator`: *amended*, optional literals: the BSB/1839 printed page and the CCEL outline label (ruling 7);
  - `gc:pages`: optional, the printed pages in the working text (ADR-0002);
  - `gc:cites`: one or more Passages, resolved to what was meant;
  - `gc:supports`: exactly one Position.
- *Amended, for citations printed with a slip or variant (ruling 6):*
  - `gc:asPrinted`: the citation exactly as printed in the witness the locator names;
  - `gc:citesCandidate`: each reading of a printed citation that cannot be resolved without a ruling. No candidate is picked;
  - `gc:resolutionNote`: at most one, and only together with `gc:asPrinted`. It is an editorial note on why the citation resolves as it does or why candidates are recorded. Like the status properties, it is editorial and never doctrine.
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
  - Phase-1 data cites by locator only. Verbatim Gill quotation waits for verified OCR, which is HELD on goat-yard `substrate-v0`.
- *Amended:* **the sentence cap is 3 sentences per Argument, for display** (architect). Gill is PD, so the cap is a **UI choice, not a legal one**.
  - The shape enforces it with a regex that allows at most two sentence breaks. A break is `.`, `!` or `?` followed by whitespace and a capital.
  - The regex errs strict: an abbreviation such as "Mr. Smith" counts as a break.

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

These three were ratified provisionally with the ADR (ruling 9), subject to the architect's reading of the text:

- `B agent/{slug}` as an ADR-0002 pattern. It is now listed in ADR-0002's table.
- Status on edges (§4): "as ratified as the weaker Position".
- The plumb-line's own resources carry `status ratified` directly, with `proposedBy` and `ratifiedBy` both `B agent/architect`.
