# docs/

Golden Chain: *the faith and practice of the churches.*

## Layout (proposed in phase 0)

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

## Index

| Doc | Status |
|---|---|
| [identity.md](identity.md) | Current |
| [ADR-0001 Store roles and the single ingest path](adr/0001-store-roles-and-single-ingest-path.md) | Proposed |
| [ADR-0002 Identity: IRI patterns](adr/0002-identity-iri-patterns.md) | Proposed |
| [ADR-0003 Controlled vocabularies and scoring](adr/0003-controlled-vocabularies-and-scoring.md) | Proposed |
| [Source: Gill, Body of Divinity](sources/gill-body-of-divinity.md) | Report |
| [Locus vocabulary draft](loci/locus-vocabulary-draft.md) | Proposal |
| [Handoff, phase 0](handoff/HANDOFF_phase0.md) | Open |
