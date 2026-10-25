# ADR-0001: Store roles and the single ingest path

- Status: Ratified with changes
- Date proposed: 2026-10-25
- Date ratified: 2026-10-25
- Proposed by: build agent
- Ratified by: architect

## Context

Golden Chain will eventually use four stores: Jena/Fuseki, Neo4j, Weaviate,
Postgres. Each is good at one thing; any of them could silently become a
second source of truth. Standing rule 1 says TTL in git is the only source
of truth, and nothing reaches Neo4j or Weaviate except by scripted
projection from Jena. Standing rule 3 says models route identifiers and
stores render text, which only holds if every rendered string has a
traceable origin.

## Decision

### 1. Roles

| Store | Role | Holds | Written by | Phase |
|---|---|---|---|---|
| **git (TTL)** | Source of truth | `ontology/*.ttl`, `data/*.ttl` | Humans and the build agent, by commit, after review | 0+ |
| **Jena / Fuseki** | Authoritative query and reasoning store | One named graph per TTL file, plus derived graphs (below) | `goldenchain.ingest` only | 1+ |
| **Neo4j** | Derived projection for traversal: armilla paths, inheritance walks, weigh scoring | Nodes and edges keyed by IRI | `goldenchain.project.neo4j` only | ADR required |
| **Weaviate** | Derived projection for semantic search over Passage and Argument text | Objects keyed by IRI (UUIDv5 of the IRI) | `goldenchain.project.weaviate` only | ADR required |
| **Postgres** | Operational data: users, locations, admin, user self-maps | Rows that *reference* IRIs; no doctrinal content | The application | ADR required |

### 2. One ingest path

```
git TTL ──parse──▶ SHACL ──▶ Fuseki (replace named graph per file)
                               │
                               ├─▶ derive (SPARQL CONSTRUCT) ─▶ Fuseki derived graphs
                               │
                               ├─▶ project ─▶ Neo4j
                               └─▶ project ─▶ Weaviate
```

- **Named graphs.** Each TTL file loads into
  `https://w3id.org/golden-chain/graph/{file-stem}`. Loading replaces the
  whole graph, so a load is idempotent and a deleted triple disappears.
- **Derived graphs.** Inference the projection depends on is materialised
  in Jena into `…/graph/derived/{rule-set}`, never committed and always
  rebuildable. This covers symmetric `excludes`, `entails` chains, and
  `childOf` inheritance with overrides. The first two are OWL-expressible.
  **Inheritance with overrides is not**: it is non-monotonic and needs a
  closed-world SPARQL step (ADR-0003 open point). Neo4j never computes
  doctrine-bearing inference; it only traverses what Jena projected.
- **Projection is a full rebuild** in phases 1–2 (drop and reload by
  source graph). Incremental projection needs its own ADR.
- **Fuseki is read-only to applications.** The served Fuseki config has no
  SPARQL Update or Graph Store write endpoint. Ingest uses a separate local
  admin endpoint or `tdb2.tdbloader` offline.
- **Write credentials** for Neo4j and Weaviate are held only by the
  projection job. The application connects with read-only roles.
- **Weaviate text has a recorded origin.** Every string vectorised is (a)
  a verbatim quotation carrying a source locator, (b) Scripture text from
  a licensed or PD translation recorded per Passage, or (c) a label
  authored in TTL. No text is generated at projection time (rule 3).

### 3. Guard test

`tests/test_projection_guard.py` (born with the first projection) asserts,
**per source graph**:

| Count | TTL (rdflib) | Fuseki | Neo4j | Weaviate |
|---|---|---|---|---|
| Distinct subjects per class (Locus, Position, Argument, Passage, Body, Holding) | = | = | = | n/a, or = for Passage/Argument |
| `holds`, `answers`, `supports`, `childOf` edges | = | = | = | n/a |
| Triples (asserted only) | = | = | n/a | n/a |

Counting rule: a Passage cited by two sources counts once *in each source's
row* (membership), while Neo4j holds one node with `sources: [..]`. The guard
compares memberships, not node totals. Totals are checked separately as
distinct IRIs across all graphs.

Divergence fails the build. Per rule 6 it is reported as a finding and
never "fixed" by editing the expected numbers.

## Consequences

- Any change to doctrine-bearing data is a git diff, reviewable and
  revertible.
- Neo4j and Weaviate can be destroyed and rebuilt at any time; they carry
  no backups of their own.
- The app cannot "just add" a node to Neo4j for a feature; it must go
  through TTL. That is friction by design.
- Postgres user self-maps reference Locus/Position IRIs. Renaming an IRI
  breaks them, which is why ADR-0002 forbids renaming.

## Alternatives considered

- **Neo4j as primary with n10s import/export.** Rejected: no SHACL/OWL
  reasoning, and the round-trip loses RDF identity detail.
- **Fuseki with SPARQL Update as the editing surface.** Rejected for
  phases 0–2: edits bypass git review. Could return as an editorial UI
  that *writes TTL to a branch*, not to the store.
- **Single store (Fuseki only).** Viable for phases 0–1, which is exactly
  what we do. The other stores arrive only under their own ADRs.

## Verification

- Phase 1: TTL parses; SHACL passes; the Fuseki per-graph counts equal the
  rdflib counts (guard test, Jena half only).
- Later phases: the full guard table above.
- A config test asserts the served Fuseki config exposes no update
  endpoint.

## Ratification (2026-10-25)

The phase-0 open points are settled as follows.

1. **Toolchain (Q19).**
   - Python 3.11 via `py -3.11`, in a gitignored `.venv`.
   - rdflib and pySHACL for parsing, validation and tests.
   - The Jena `fuseki-server` jar on Java 17 for the local store, with a checked-in `fuseki/config.ttl`. No Docker in phases 0–1.
2. **Reasoner.** The Jena rule reasoner (OWL Micro/Mini family) plus SHACL. A DL reasoner comes only with a DL axiom and its own ADR.
3. **Scripture text (Q20).**
   - No verse text is stored in phases 0–1. A Passage is an IRI with ordinals and nothing more.
   - The choice of translation is **ADR-0004**, reserved until display needs verse text.
   - That ADR must address the KJV's status: public domain in most jurisdictions, but under Crown letters patent **in the UK only**.
4. **Licensed corpus (rule 9).**
   - Licensed source material (e.g. the BSB Gill PDF) is read only by configured path, from `GOLDEN_CHAIN_CORPUS`, outside the working tree.
   - It is never committed or copied into the repo. `.gitignore` excludes `*.pdf`, `*.epub` and `*.docx`.
   - The pre-commit hook refuses PDFs anywhere and, under `data/`, any file that is not `.ttl`, `.py` or `.md`.
   - Derived working copies (OCR) stay outside the repo too.
