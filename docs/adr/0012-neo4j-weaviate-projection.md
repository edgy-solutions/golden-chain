# ADR-0012: Project to Neo4j and Weaviate only what Jena holds, for traversal and search, and guard every count

- Status: Proposed
- Date proposed: 2026-11-27
- Date ratified:
- Proposed by: build agent, on the ruling on report 32, item 8 ([RULING_report_32.md](../handoff/RULING_report_32.md))
- Ratified by: architect

## Context

- **The ruling asks for** "a projection ADR for Neo4j and Weaviate under ADR-0001: what is projected, the guard test, and what each store is for".
- **ADR-0001 sets:**
  - the roles: git TTL is truth; Jena/Fuseki is the authoritative query store; Neo4j and Weaviate are derived projections, each "ADR required";
  - the single ingest path;
  - full-rebuild projection;
  - read-only application roles;
  - the guard table.
- **What is true now:**
  - Only the Jena half exists (`tests/test_guard_jena.py`).
  - Weigh runs in `goldenchain/weigh.py` over the rdflib mirror (`ingest.derive_rdflib`), with the derived graphs `graph/derived/inheritance` and `graph/derived/consistency`. **Weigh does not need Neo4j.** ADR-0001's Neo4j row still lists "weigh scoring".
  - The examine/try prototype (ADR-0008) is static and queries TDB2. No view needs either store yet.
  - No verse text is stored (ADR-0001 ratification 3; ADR-0004 reserved).
- **Standing rules served:**
  - 1: no store but git is a source.
  - 3: no model asserts doctrine, so nothing is generated at projection or at search.
  - 5: ADR before building.
  - 6: the guard's expected numbers are never edited to pass.

## Decision

### 1. What each store is for

| Store | For | Not for |
|---|---|---|
| **Neo4j** | Read-only **traversal views**: a Body's `childOf` chain; where an effective Holding was inherited from; the Arguments, and their Positions, that cite the same Passage; the `excludes` and `entails` neighbourhood of a Position. | Weigh, the site's judgments, or any inference. **Proposed amendment to ADR-0001:** "weigh scoring" leaves Neo4j's row. Weigh stays in `goldenchain.weigh` over Jena and rdflib. |
| **Weaviate** | **Search over strings the data already holds**: Locus labels and questions, Position labels, and Argument quotations with their locators. A hit returns IRIs. The page then renders the TTL strings, as ADR-0008 renders them. | Generating, summarising or reranking text; Scripture text (none is stored); any answer to a question. No generative or Q&A module is enabled. |

### 2. What is projected

All of it is read from Fuseki by SPARQL, over the named source graphs and the derived graphs. Nothing is computed in the target store.

- **Neo4j nodes:** one per IRI of class `Locus`, `Position`, `Argument`, `Passage`, `Body`, `Holding`, `SourceWork` and `Congregation`.
  - Properties are only `iri`, `rdfs:label`, and a fixed whitelist of literals: `status`, `tier`, `clarity`, `modality`, `scope`, `locator`, `secondaryLocator`, `asPrinted`, `osisRef`, `startOrdinal`, `endOrdinal`. Each node also gets `graphs`, the list of source graphs it is a member of.
  - No person node is projected (ADR-0010's privacy rules), and no `rdfs:comment`, `gc:resolutionNote` or free text is projected.
- **Neo4j edges:** `holds`, `answers`, `supports`, `childOf`, `cites`, `excludes`, `entails`, `unchurches` and `exceptsLocus` as asserted. `effectivelyHolds` and the symmetric `excludes` come from the derived graphs. Each edge carries its `graph`, and a derived edge carries its rule set.
- **Weaviate objects:** one collection each for `Locus`, `Position` and `Argument`.
  - The object id is UUIDv5 of the IRI.
  - Its properties are `iri`; the text field (label, question or quotation); `text_sha256`; `locator` (Arguments); and `graph`.
  - The embedding model is pinned by name and version in the projection header.
- **A projection header**, stored in each store (one meta node; one meta object) and in `run_header.json`, records:
  - the git commit;
  - the sha256 of `gc.trig`;
  - the counts;
  - the projection script's sha256;
  - the embedding model.

### 3. The guard test, `tests/test_projection_guard.py`

It is born with the first projection. It runs against throwaway local instances built from the tiny fixture data (as the Jena half does), and against the real projection in a check mode.

- **ADR-0001's table, per source graph:** distinct subjects per class, and edges per predicate, are equal in rdflib, Fuseki, Neo4j and (for the three text classes) Weaviate. Passages are counted by membership, as ADR-0001 states.
- **The IRIs are one to one:** every node and object IRI exists in Jena, and every Jena subject of a projected class exists in the store.
- **The text is the TTL's text:** every Weaviate object's `text_sha256` equals the sha256 of its TTL literal, and every Neo4j literal property equals its TTL value.
- **The whitelist:** no node, edge or object has a property outside Decision 2. No node or edge is missing `graph` or `graphs`.
- **Read-only:** a write with the application's credentials fails on both stores.
- **Deterministic:** two projections of the same commit give the same counts and the same sorted list of (IRI, property-hash) pairs.
- **Weigh is independent:** `goldenchain.weigh` imports no Neo4j or Weaviate client, and weigh's locked output hashes are unchanged by a projection.
- A divergence fails the build. Under rule 6 it is reported as a finding, never fixed by editing the expected numbers.

### 4. When it is built

- Neither store is built until a view that needs it is ruled:
  - for Neo4j, a traversal view;
  - for Weaviate, search.
- Each build is then locked first, with this guard born with it.
- Both run locally first, and are served only under ADR-0011's gates.

## Consequences

- Easier: each store has one stated job, and any value it shows can be traced by IRI and hash to a TTL line.
- Harder: two more services to run, and a guard that needs live instances in the suite.
- **A risk of search:** semantic search ranks by closeness of wording, and a reader may take a near match for agreement in doctrine. Every search result page is labelled "matched by wording, not by doctrine", and it shows no score.
- Forbidden:
  - writing to either store from the application;
  - computing any doctrine-bearing result in Neo4j;
  - storing or showing text in Weaviate that is not byte-equal to a TTL literal;
  - projecting a person.

## Alternatives considered

- **No Neo4j: SPARQL property paths over Fuseki** (`gc:childOf+`, and so on). This is viable for every traversal listed above. Neo4j earns its place only if an interactive graph view needs it. The build agent puts this to the architect (open point 1) rather than assume it.
- **Jena's text index (Lucene) in place of Weaviate.** Keyword search, no vectors and no extra service. It avoids the near-match risk, but finds nothing a reader words differently.
- **Incremental projection.** ADR-0001 requires its own ADR. It is not proposed.

## Verification (to be locked before any build)

Sketch only, for review:
- the guard above, on the fixture data, with every count derived from the fixture, not typed;
- on the real data, the guard's per-graph table, printed in the projection's report;
- a test over `goldenchain/` that no module other than `goldenchain.project.*` imports a Neo4j or Weaviate client with write credentials.

## Open points

1. **Is Neo4j needed?** Fuseki property paths cover the traversals listed. Keep Neo4j in ADR-0001, or strike it until a view proves the need?
2. **The embedding model:** a local model (no text leaves the machine), or a hosted one? All the projected text is PD quotation or labels already in the public repository.
3. **Running the services locally:** the phase 0-1 ratification says no Docker. Neo4j and Weaviate would need their own binaries, or a ruling for Docker in phase 2.
4. **The ADR-0001 amendment** (weigh leaves Neo4j's row): ratify it here, or as an amendment to ADR-0001?
5. **Congregations in Neo4j:** projected as nodes once they exist (ADR-0007), with no person. Or held back until ADR-0011's D6 holds?
