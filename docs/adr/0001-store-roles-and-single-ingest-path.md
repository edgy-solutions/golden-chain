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

## Amendment 1: the shared-database guard (2026-11-22; ruling on report 24)

**Why.** There is one TDB2 store, `fuseki/databases/gc`. `ingest.build_tdb2` deletes and rebuilds it, and `fuseki.serve` opens it. The suite also builds it (from tiny test data) and serves it. In report 24, an ingest run on a scratch data copy collided with a suite run: the ingest failed on a file lock and the suite had 14 failures in `test_guard_jena`. The ruling: "add a guard so a check cannot open it while a test run holds it."

**Decision.**
1. A new module `goldenchain/dblock.py` gives `hold(purpose, path=LOCK)`, a context manager. `LOCK` is `fuseki/run/gc.lock` (gitignored).
   - It takes a **non-blocking, exclusive OS lock** on an open handle: `msvcrt.locking` on Windows, `fcntl.flock` elsewhere. The OS releases it when the process exits, even if killed, so there is no stale lock.
   - It is **re-entrant within one process** (a depth count). Nested holds in the holding process succeed. Only the outermost exit releases.
   - If another process holds it, it raises `DatabaseBusy` (a `RuntimeError`) **at once**, before anything is written. The message names the database path and, where readable, the holder's pid, purpose and start time (from a sidecar file `gc.lock.holder` written after acquiring).
2. `ingest.build_tdb2` takes the hold as its first act, before writing `fuseki/run/` or touching the database. `fuseki.serve` holds it for the server's life.
3. `tests/conftest.py` gets a **session-scoped autouse fixture** that holds it for the whole test run (purpose "pytest session"). So any other process that tries to build or serve while the suite runs gets `DatabaseBusy`.
4. `python -m goldenchain.ingest` already reports any exception and exits 1. A busy database prints `INGEST FAILED: DatabaseBusy: ...` and exits 1, with the database untouched.
5. Nothing else changes. In-process checks (`load_dataset`, `derive_rdflib`, on a scratch `GOLDEN_CHAIN_DATA`) never open the database and need no hold.

## Verification, amendment 1: the lock (2026-11-22, before any code for it)

Git history seals this lock.

- **AY1. Busy is refused, untouched.** While a process holds the lock, a second process running `python -m goldenchain.ingest` on a scratch `GOLDEN_CHAIN_DATA` exits 1, prints `DatabaseBusy` on stderr, and leaves `fuseki/databases/gc` unchanged (same file names, sizes and mtimes) and `fuseki/run/gc.trig` unchanged. Born test: the test session itself is the holder.
- **AY2. Re-entrant and released.** On a tmp lock path: a nested hold in one process succeeds; after the outermost exit, another process can take it; after a holder process is killed, another process can take it.
- **AY3. Nothing else moves.** No existing test file is edited (`tests/conftest.py` gains the fixture; it holds no test). The suite is 810 + the born tests, all passing. Weigh byte-identical (`71c14a5d187d` / `c8fe9e910b5a`). Ingest, run alone, gives 0 violations and 3 warnings. `git diff data/` is empty.
