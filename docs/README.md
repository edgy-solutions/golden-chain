# docs/

Golden Chain: *the faith and practice of the churches.*

## Layout

```
docs/
  README.md          this index
  identity.md        namespace, w3id redirect, PR status
  adr/               architecture decision records
    0000-template.md
    NNNN-kebab-title.md       Proposed until the architect ratifies
  sources/           one report per source before ingest (rule 4):
                     edition, format, licence, text quality, citation key
  loci/              locus vocabulary drafts; after ratification, the
                     rationale for the list (the list itself lives in TTL)
  handoff/           HANDOFF_phase{N}.md: in-flight state and numbered
                     open questions; superseded, not edited, per phase
```

Repository layout this assumes (built in phase 1 and later, not now):

```
ontology/            core.ttl, shapes.ttl (SHACL)
data/                *.ttl, plus .py and .md only (pre-commit hook, rule 4)
src/goldenchain/     ingest, passage canonicaliser, projections
tests/               guard tests, born with the change they test (rule 7)
fuseki/              config.ttl for local Fuseki (read-only service config)
```

### data/ (phase 1; ruling Q9, 2026-10-26)

Seven files. Each file is one named graph at ingest.

| File | Holds |
|---|---|
| `loci.ttl` | Headings, Loci and Positions, with `excludes` / `entails` between Positions |
| `agents.ttl` | The architect and build agents named in `gc:proposedBy` / `gc:ratifiedBy` |
| `gill-body-of-divinity.ttl` | Gill: the Body, its Source and divisions, Holdings, Arguments, cited Passages |
| `westminster.ttl` | WCF: the same shape |
| `lbc-1689.ttl` | LBC (1677 witness; slug kept): the same shape |
| `augsburg.ttl` | Augsburg: Body, Source, Holdings |
| `book-of-concord.ttl` | The Book of Concord `gc:Collection`, Apology and Small Catechism: Bodies, Sources, Holdings, Arguments |

A Passage is declared in every file that cites it. The union graph merges
the duplicate triples, so a Passage counts once.

## Index

| Doc | Status |
|---|---|
| [identity.md](identity.md) | Current |
| [ADR-0001 Store roles and the single ingest path](adr/0001-store-roles-and-single-ingest-path.md) | Ratified with changes 2026-10-25 |
| [ADR-0002 Identity: IRI patterns](adr/0002-identity-iri-patterns.md) | Ratified with changes 2026-10-25 |
| [ADR-0003 Controlled vocabularies and scoring](adr/0003-controlled-vocabularies-and-scoring.md) | Ratified with changes 2026-10-25 (§6 proposal) |
| ADR-0004 Scripture translation | Reserved: written when display needs verse text |
| [ADR-0005 Editorial status, provenance, Argument text](adr/0005-editorial-status-and-argument-text.md) | Proposed |
| [Source: Gill, Body of Divinity (BSB working text)](sources/gill-body-of-divinity.md) | Report, amended 2026-10-25 |
| [Source: Westminster Confession](sources/westminster.md) | Report |
| [Source: Second London Baptist Confession](sources/lbc-1689.md) | Report |
| [Source: Augsburg Confession](sources/augsburg.md) | Report |
| [Locus vocabulary draft](loci/locus-vocabulary-draft.md) | Proposal, amended with rulings |
| [Handoff, phase 0](handoff/HANDOFF_phase0.md) | Open |
