# ADR-0007: Onboard a Congregation as "subscribes to Body X, with these exceptions"

- Status: Ratified, with the answers below (ruling on report 19, A-2)
- Date proposed: 2026-11-15
- Date ratified: 2026-11-17
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

## Ratification (2026-11-17; ruling on report 19, A-2)

Ratified with these answers, filed verbatim in [RULING_report_19.md](../handoff/RULING_report_19.md). Where an answer differs from the proposed text above, the answer governs.

1. **`gc:exceptsLocus` is accepted** (open point 1). An "excepted, unknown" cell:
   - scores nothing;
   - is shown as "excepted, unknown";
   - counts against coverage, never as tolerated.
2. **Several parents are allowed** (open point 2; supersedes Decision 1's "one parent" and the deferral under Alternatives). ADR-0003 R2's rule applies: the Congregation is inconsistent unless it asserts its own Holdings wherever its parents differ.
3. **Sources** (open point 3; amends Decision 5):
   - A church's own statement is cited by URL, read date and an archived copy's URL. No text is stored.
   - Every Congregation Holding carries its source and stays `proposed` until a named person confirms it.
   - A Holding from personal knowledge alone is allowed. It is labelled as that and shown as that. This supersedes Decision 6's "a church whose statement is not public is not onboarded" for such Holdings.
4. **Added: every Congregation page states**:
   - who entered it, from what, and when;
   - how the church may correct it.
   The confirmer is named (the "named person" of answer 3). Decision 6's "no person is named" still holds for the church's pastors, elders and members.
5. Open point 4 (which church first) stays with Chris.

Nothing is built yet. The next step is a lock of the Verification section above, amended for answers 1–4. That means:
- a synthetic Congregation with two parents;
- a personal-knowledge Holding;
- coverage counting the excepted cell;
- the page statement.
The build follows in a separate commit.

## Verification, as amended: the lock (2026-11-22T14:50Z, before any ADR-0007 code; ruling on report 20, A-9)

Locked at golden-chain 5285db3 by this commit. It is the authority for the build and is never edited; a miss is
recorded beside it. Synthetic fixtures only: no real Congregation is minted, and no data/*.ttl file is written or
changed, until Chris signs one.

### The build choices

These are the build agent's proposals where the ADR and its answers leave a choice. Each is open to the architect;
the ones marked Q are asked in the report.

- **C1.** `gc:exceptsLocus` (domain `gc:Congregation`, range `gc:Locus`) goes in ontology/core.ttl. Its provenance
  rides on an `owl:Axiom` `<axiom/exceptsLocus/{slug}/{locus-tail}>`, the pattern of the `gc:asPrinted` axioms:
  `dcterms:source`, `gc:locator` (when from a statement), `gc:status`, `gc:proposedBy`.
- **C2.** reasoner/10-inheritance.ru: a Body on the path that excepts Locus L blocks L exactly as a Holding on L
  does (the parent's Holdings on L are dropped and none are added). reasoner/20-consistency.ru is unchanged. So on
  a Locus where both parents speak and differ, an exception without an alternative still leaves the Congregation
  inconsistent (parents-differ): answer 2 says "unless it asserts its own Holdings", and an exception is not a
  Holding. **Q:** should an exception clear parents-differ?
- **C3. Sources (answer 3).**
  - A statement is `<source/congregation/{slug}/statement> a gc:SourceWork`, with `rdfs:label` (title),
    `rdfs:seeAlso <URL>`, `gc:readOn` (xsd:date) and `gc:archivedCopy <archived URL>`. No text is stored.
  - Personal knowledge is `<source/congregation/{slug}/personal-knowledge> a gc:PersonalKnowledge` (new,
    `rdfs:subClassOf gc:Source`), with `dcterms:creator <agent/chris>` and `dcterms:created` (date).
  - Every Congregation Holding and exception axiom has a `dcterms:source` that is one of the two. A
    statement-based one also has `gc:locator`.
- **C4. Status.** Answer 3 governs Decision 4 and the form's "gc:ratifiedBy <agent/chris>". Every Holding, every
  exception and the Congregation itself are written `gc:status` proposed and `gc:proposedBy <agent/chris>`, with
  no `gc:ratifiedBy`. Confirmation is a later act and is not built. When a Congregation carries `gc:ratifiedBy`,
  the page names that agent as the confirmer. **Q:** does Chris's signature on the form count as the confirmation?
- **C5. The Congregation node.**
  - `rdfs:label` (public name and place);
  - `gc:childOf` each parent;
  - `dcterms:source` and `gc:locator` for where the statement names its parents (or the personal-knowledge source);
  - `gc:proposedBy`;
  - `dcterms:created` (the signing date).

  The TTL file's header comment names the signed record and the build hash (the plumb-line pattern). The file is
  data/congregation-{slug}.ttl (ingest globs data/*.ttl). Only console ingest writes it, with --write, from a
  signed export, and it is never overwritten.
- **C6. The page statement (answer 4).** Fixed wording, built from data:
  - "entered by: <label of gc:proposedBy>, on <dcterms:created>, from: <each source: title (URL, read <date>,
    archived <URL>) | personal knowledge (<creator label>)>"
  - "confirmed by: <label of gc:ratifiedBy> | not yet confirmed (every row here is proposed)"
  - "correction: The church may correct this page by writing to the maintainers of Golden Chain. A correction is
    read against the church's own statement, signed, and then replaces the entry; until then the entry stands as
    proposed."

  **Q:** the correction route (the text has no contact detail yet).
- **C7. The console form, kind `congregation`** (the ADR table, amended).
  - Parents are given when the form is built (one or more Bodies in the data) and are shown by label.
  - A "modality" select is added to every row that writes a Holding. A Holding needs one, and the ADR table
    lacked it.
  - Every row that writes a Holding or an exception has a "basis" radio (the church's statement / personal
    knowledge). "Where" is required when the basis is the statement.
  - Church level: name; statement title, URL, read date and archived URL; a basis radio (published statement /
    personal knowledge only).
  - Optional fields use the console's `required: false`. Ingest checks the conditions for this kind.
  - Where the parents agree on a Locus, the row offers "as the parents", "excepts: holds another" and "excepts: no
    alternative stated".
  - Where they differ, it offers "holds this one" (choose below) and "excepts: no alternative stated", and its
    plain-words line says the parents differ.
  - Each Locus where every parent is silent gets one row: a select with `empty_means` "unanswered".
  - No row text is written by a model. Every label comes from `rdfs:label` in the data.
- **C8. Weigh.**
  - `render_body` adds lines for a `gc:Congregation` only (ranked or excluded):
    - "subscribes to: <parents>";
    - "exceptions: N", with each excepted Locus's notation and label;
    - the C6 statement;
    - a "cells:" block, one line per Locus where the Congregation has an effective Holding or an exception, in
      Locus IRI order. Each line reads "inherited from <parent>", "own (statement, <locator>)", "own (personal
      knowledge)" or "excepted, unknown".
  - In the excluded block, a reason from an inherited Holding says "inherited from <parent>" beside its source.
  - No scoring rule changes. Every other Body renders byte-identically.

### Predictions (each a born test unless stated)

- **AV1. Effective Holdings.**
  - The synthetic world has parents P1 and P2 and Loci L1..L6:
    - L1: both parents agree; the Congregation C says nothing.
    - L2: both agree; C holds another Position from its statement (Decision 2).
    - L3: both agree; C excepts with no alternative (Decision 3).
    - L4: the parents differ; C holds its own.
    - L5: both parents are silent; C holds a Position from personal knowledge.
    - L6: the parents differ; C says nothing.
  - C's effective Holdings are exactly: P1's and P2's on L1 and L6; C's own on L2, L4 and L5; none on L3.
- **AV2. Consistency.**
  - parents-differ fires for C on L6 only. It does not fire on L4, which C overrides, or on L3, where the parents
    agree.
  - A second fixture, with the parents differing on an excepted Locus, still fires parents-differ there (C2 as
    built).
- **AV3. Coverage.**
  - C's coverage denominator includes L3's weight, and its numerator does not.
  - L3 adds no cost and no break, and is never shown as tolerated.
  - A one-parent fixture with and without the exception differs in coverage by exactly L3's weight over the
    denominator.
- **AV4. Weigh renders for C:**
  - "inherited from" on L1 and L6, naming each parent;
  - "own (statement, <locator>)" on L2 and L4;
  - "own (personal knowledge)" on L5;
  - "excepted, unknown" on L3;
  - the header lines and the C6 statement, with "not yet confirmed";
  - with `gc:ratifiedBy` added in the fixture, "confirmed by: <label>".
- **AV5.** An exclusion triggered by an inherited Holding names the parent's Holding's source and says "inherited
  from".
- **AV6. SHACL.** There is a violation for each of:
  - (a) an exception and an own Holding on the same Locus;
  - (b) `gc:exceptsLocus` on a non-Congregation;
  - (c) a Congregation Holding without `dcterms:source`;
  - (d) an exception without its axiom's source;
  - (e) a statement-based Holding without `gc:locator`.

  The AV1 fixture conforms.
- **AV7. Console.**
  - The spec built from the AV1 parents passes every build check, the plain-words check included.
  - Ingest of a synthetic signed export, with --ttl-out to tmp, writes TTL that, loaded beside the fixture parents,
    reproduces AV1.
  - "Other, as written" mints nothing for that row and is listed as a question in the signed record.
  - An export that breaks a C7 condition is refused.
  - Without --ttl-out and --write, nothing is written under data/.
- **AV8. Real data untouched.**
  - Weigh is byte-identical (members 71c14a5d187d, officers c8fe9e910b5a).
  - Ingest shows 0 violations, and the tests/predictions.py counts are unchanged.
  - No data/*.ttl file changes.
  - The full suite passes. No existing test is edited, except one that pins KINDS or the ontology's property list
    (each is named).


## Verification, amendment 2: the lock (2026-11-22T17:16Z, before any code for it; ruling on report 21)

Locked at golden-chain 18f4de3 by this commit, before any code that implements it. It amends C2, C4 and C7 and
the AV predictions named below. The lock of 2026-11-22T14:50Z above is never edited: where this section
supersedes a clause, that clause stays on record beside it. Synthetic fixtures only: no real Congregation is
minted, and no data/*.ttl file is written or changed.

### The build choices, amended

- **C2' (supersedes C2's last two sentences).** An exception clears parents-differ on that Locus.
  reasoner/20-consistency.ru's parents-differ rule gains one guard: it does not fire for Body B on Locus L when
  `B gc:exceptsLocus L`. An excepted Locus inherits nothing, so nothing conflicts. Its cell stays "excepted,
  unknown". Inheritance (10-inheritance.ru) is unchanged.
- **C4' (answers C4's Q: no).** Chris's signature is the entry, shown as "entered by". The ingest never writes
  `gc:ratifiedBy` (unchanged). "Confirmed by" is reserved for a named person who speaks for that church, and that
  act is not built. The page line becomes:
  - with no `gc:ratifiedBy`: "  not yet confirmed by the church";
  - with `gc:ratifiedBy`: "  confirmed by: <label>" (unchanged).
  The parenthesis "(every row here is proposed)" goes.
- **C6' (answers C6's Q).** The three lines (entered by, confirmed, correction) state who entered it, from what,
  and that the church may send a correction. The CORRECTION wording is unchanged. No address, email or URL is
  added; the contact detail waits on Chris choosing one.
- **C7' (amends C7's "Where they differ" item).** Where the parents differ, the row offers three answers:
  "holds this one", "excepts: no alternative stated" and **"says nothing: keeps both"** (code `keeps-both`).
  - "says nothing: keeps both" takes no position, modality, scope, basis or where. An export that fills any of
    them on that answer is refused.
  - It mints nothing: no Holding, no exception, no axiom.
  - It is recorded as an answer: the signed record has a section "## Answered, nothing minted" with one line per
    such row, "- <row label>: says nothing: keeps both (its standards differ here)". It is not listed under
    questions.
  - The plain-words line for a differ row names all three answers.
  - Rows where the parents agree, and silent rows, are unchanged.
- **C8' (adds to C8).** Where parents-differ fires for a Congregation on Locus L, weigh's cells block keeps the
  "inherited from <parent>" line for each parent and adds, after them, one line
  "    - <locus>: its standards differ here and its statement does not say". No other Body's page changes.

### Predictions, amended (each a born test)

- **AW1 (supersedes AV2's second clause, which stays on record).** In the fixture where the parents differ on a
  Locus that C excepts, parents-differ does **not** fire there, and C's cell there is "excepted, unknown".
  AV2's first clause holds unchanged: in the AV1 fixture, parents-differ fires for C on L6 only.
- **AW2. The form.**
  - Every differ row offers exactly the three answers of C7', in that order, with codes `holds-this`,
    `no-alternative`, `keeps-both`. Agree rows and silent rows have the same answers as before.
  - The spec built from the AV1 parents passes every build check, the plain-words check included.
- **AW3. Ingest.**
  - In the AV7 synthetic export, L6 answered "says nothing: keeps both" (instead of abstained) ingests. The TTL,
    loaded beside the fixture parents, reproduces AV1, and parents-differ fires for C on L6.
  - The TTL has no triple about L6, and its `gc:proposedBy <agent/chris>` count is unchanged (1 + 4).
  - The signed record has "## Answered, nothing minted" with the L6 line, and L6 is not under questions.
  - "says nothing: keeps both" with any of position, modality, scope, basis or where filled is refused, and
    nothing is written.
- **AW4. Weigh.**
  - For C in the AV1 fixture, the cells block has the two "inherited from" lines on L6 followed by
    "its standards differ here and its statement does not say", and no such line on any other Locus.
  - The confirmation line is "  not yet confirmed by the church"; with `gc:ratifiedBy` in the fixture it is
    "  confirmed by: <label>".
  - The correction line has no "@" and no "http".
- **AW5. Real data untouched.**
  - Weigh is byte-identical (members 71c14a5d187d, officers c8fe9e910b5a).
  - Ingest shows 0 violations, and the tests/predictions.py counts are unchanged.
  - No data/*.ttl file changes.
  - The full suite passes.
  - Edited existing tests, named in the report: `test_av2_parents_differ_still_fires_on_an_excepted_locus`
    (superseded by AW1; kept, renamed to say it is superseded, and inverted), the AV4 assertion on
    "not yet confirmed (every row here is proposed)", and the AV7 fixture's L6 abstain (AV7's own tests keep
    passing with L6 abstained as well as answered).
