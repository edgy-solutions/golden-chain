# ADR-0007: Onboard a Congregation as "subscribes to Body X, with these exceptions"

- Status: Proposed
- Date proposed: 2026-11-15
- Date ratified:
- Proposed by: build agent (overnight order 2026-11-15, item 6)
- Ratified by: architect

Design only. No Congregation instance is minted under this ADR until it is
ratified, and then only from a signed console record.

## Context

- `gc:Congregation` (one local church) is in the ontology with no instances
  (ruling on report 13, item 8).
- Most churches describe themselves by reference to a confession: "we hold the
  1689 Confession", sometimes "except chapter 26.x", or "with the following
  reservations". Golden Chain has to record that without re-keying the church's
  text (rule 4) and without a model asserting what the church holds (rule 3).
- ADR-0003 §7 already gives `gc:childOf` with a **per-Locus override**: a child's
  Holdings on a Locus replace the parent's Holdings there entirely; on every
  other Locus the parent's Holdings are inherited. That is "subscribes to X,
  with these exceptions" in all but one case (Decision 3).

## Decision (proposed)

1. **A Congregation subscribes by `gc:childOf`.** `<body/congregation/{slug}>
   a gc:Congregation ; gc:childOf <body/{x}>`. One parent. `{slug}` follows
   ADR-0002's slug rules. The parent is a Body already in the data (a
   Confession, Denomination or Teacher). Weigh's inheritance is unchanged.
2. **An exception that names an alternative is a Holding.** The Congregation
   holds a Position of the excepted Locus, with modality and scope as ADR-0003
   defines them. By §7 it replaces the parent on that Locus. Its source is the
   church's own published statement (Decision 5).
3. **An exception that names no alternative** ("we do not hold 26.x", nothing
   further) cannot be written today: a child with no Holding on a Locus
   inherits. Proposed: one new property, `gc:exceptsLocus` (domain
   `gc:Congregation`, range `gc:Locus`). The inheritance step drops the
   parent's Holdings on that Locus and adds none, so the cell is **unknown**,
   never "tolerated" (`silent ≠ tolerated`, ADR-0003). SHACL: an excepted Locus
   carries no Holding of the Congregation's own (otherwise Decision 2 applies).
4. **Provenance.**
   - Every Holding and every `gc:exceptsLocus` carries `gc:status`,
     `gc:proposedBy` and, once signed, `gc:ratifiedBy <agent/chris>`, as for
     Arguments (ADR-0005).
   - The record of a Congregation is the signed console record
     (`SIGNED_congregation_<build16>.md`), not the build agent's reading of a
     web page.
5. **Sources.**
   - A Congregation's Holdings cite a `gc:SourceWork` for the church's own
     statement (constitution, statement of faith, membership covenant), by
     title, URL or printed edition, and the date it was read. A locator
     (article or section number) goes in `gc:locator`.
   - No text of it is stored, as with every non-PD source (rule 4).
   - A statement that only names the parent ("we hold the LBC 1689") is enough
     for Decision 1. Each exception needs its own locator.
6. **Privacy.**
   - Only a church's public statement is used.
   - No person is named: no pastor, elder or member.
   - A church Chris knows but whose statement is not public is not onboarded.
   - The slug is the church's public name and place.

## The console form (kind `congregation`, proposed)

Chris fills one form per church. Every question carries its plain-words line
(ADR-0006 Revision 4). The form shows no image.

| Section | Row | Field | Kind | Options |
|---|---|---|---|---|
| The church | name | public name and place | text | |
| | statement | title and URL (or printed edition) of its statement of faith; date read | text ×2 | |
| | parent | which Body it subscribes to | select | the Bodies in the data, by label |
| | parent-locator | where the statement says so (article / section) | text | |
| Per Locus where the parent has a Holding (one row each, the parent's Position shown by label) | as-parent | does the church hold this as the parent does? | radio | "as the parent", "excepts: holds another", "excepts: no alternative stated" |
| | instead | if another, which | select | the other Positions of that Locus, by label |
| | where | locator in the church's statement | text | |
| | scope | members, officers or all | select | the ADR-0003 scope vocabulary |
| Loci where the parent is silent | own | does the statement take a position? | select, `empty_means: "unanswered"` | the Locus's Positions |

- Every choice field also has "other, as written" (the console adds it).
- The rows are generated from the data: the parent's effective Holdings, the
  Loci and their Positions, all by `rdfs:label`. No row text is written by a model.
- Ingest writes the Congregation, its `gc:childOf`, its Holdings and its
  `gc:exceptsLocus` triples from the signed export only, with
  `gc:ratifiedBy <agent/chris>`. An "other, as written" answer mints nothing:
  it goes to the report as a question for the architect.

## How weigh renders it

- A Congregation is scored like any Body, on its effective Holdings (ADR-0003
  §5–§7). No scoring rule changes.
- `render_body` adds a header line built from data: the parent's label, and
  "exceptions: N" with each excepted Locus's notation and label.
- Each cell is marked `inherited` (from the parent) or `own` (the church's
  Holding). An `exceptsLocus` Locus shows as `excepted, unknown`.
- Ranking, walls, cost, coverage and exclusion (R2.3) are unchanged. An
  exclusion triggered by an inherited Holding names the parent's Holding as
  its source.

## Consequences

- One new property (`gc:exceptsLocus`), one SHACL shape, one change to the
  inheritance step. Everything else is existing vocabulary.
- A Congregation that differs from its parent only by exceptions costs a few
  triples, not a copy of the parent.
- Weigh output for existing Bodies is unchanged (no Congregation exists).

## Alternatives considered

- **Copy the parent's Holdings onto the Congregation.** Rejected: it hides
  what is inherited and breaks when the parent's data is corrected.
- **Model an unstated exception as a Holding with modality `silent`.** Rejected:
  silent writes no stance (weigh reading 1), and that would blur "the
  church says nothing" with "the church denies the parent's Position".
- **Several parents** (a church holding LBC 1689 and a catechism). Deferred: §7
  has one override order; two parents need a precedence rule.

## Verification (on ratification, locked first)

- A synthetic Congregation in tests (not in data) has `childOf` LBC 1689, one
  Decision-2 exception and one Decision-3 exception. Its effective Holdings
  equal the parent's minus the two Loci, plus the one own Holding. Weigh
  renders `own`, `inherited` and `excepted, unknown`.
- Weigh is byte-identical for every existing Body.
- The console spec passes the plain-words check.

## Open points

1. Is `gc:exceptsLocus` acceptable, or should an unstated exception be a
   Holding with a new modality? (Architect.)
2. Several parents: needed for phase 2? (Architect.)
3. Can a church's statement be cited by URL alone, with the read date, when it
   has no printed edition? (Architect.)
4. Which church first, if any? (Chris, once ratified.)
