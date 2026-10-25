# Handoff: phase 1 (in flight)

- Branch: `phase-0`. `main` was created from the phase-0 commit and pushed.
- State:
  - The Positions draft and the blank plumb-line form are done.
  - The infrastructure that rests only on ratified ADRs is built (a4b280a).
  - The data TTL is blocked on rulings (below).

## Done so far

| Commit | What |
|---|---|
| 6d97c03 | BSB inventory and the 156 reconciliation; WCF, LBC and Augsburg source reports; `.gitignore` |
| eb533e3 | ADRs 0001–0003 ratified with changes; ADR-0005 proposed; locus rulings |
| 7ce5628 | Architect's provenance note: Gill is PD, front matter excluded, quotation allowed; `gc:pages` |
| 5036d3d | This handoff (first version) |
| 02dc53b | `docs/loci/positions-phase1-draft.md` and `docs/loci/plumb-line-form-phase1.md` |
| a4b280a | Pre-commit hook (active via `core.hooksPath`), read-only `fuseki/config.ttl`, `ontology/vocab.ttl`, `pyproject.toml`; 15 tests pass |

## Blocked on the architect (see the draft's findings)

1. **Gill as a Body** (`B body/gill`).
   - The draft proposes 10 Gill Holdings.
   - The foreword-as-Body (below) needs Gill as its parent.
2. **F1: Augsburg cites no Scripture**, so 30c and 33c are unmintable under rule 2.
   - Options: admit the Small Catechism or the Apology (same PD Triglot); relax rule 2; or defer.
3. **F3: split locus 33** into significance and efficacy, or mark LBC as silent on 33.
4. **F4: the "?" modalities.** WCF on 30a and 31a, and Gill on 33b. The canonical WALL case depends on them.
5. **E1 and the entails/excludes definitions.** The build agent's definitions are in the draft.
6. **F5 and F6: proof-text variants and slips.** Cite as printed?
7. **Versification table source** for the passage canonicaliser (rule 4: report it first). Proposed: the KJV v11n book/chapter/verse counts from CrossWire SWORD (`canon.h`, GPL-2 code). The counts are facts, re-keyed as a `.py` table. Checks: 66 books, 1,189 chapters, 31,102 verses.
8. **ADR-0005 ratification.** The status, agent and closed-Argument shapes wait on it.

## Remember (not phase 1)

- **The BSB 1984 foreword is a Body.** "Strict Baptist, BSB 1984" reveres Gill and overrides him on three loci:
  - Practical III.1, Gill's introductory remarks on baptism;
  - Practical II.6, church discipline (locus 26);
  - Doctrinal VII.8, the millennium (locus 42): the publishers are amillennial.
- It states numbered propositions on baptism, the church, and valid baptisms. It is the worked example of `childOf` with overrides.
- **Tension to rule:** the front matter is excluded from the corpus, but a Body needs a Source. A Holding cites a division reference and stores no text, so the exclusion can hold. To be ruled before it is modelled.

## Next steps

1. After the rulings:
   - the canonicaliser and its versification table;
   - `ontology/core.ttl` and `ontology/shapes.ttl` (ADR-0005);
   - `data/*.ttl` from the draft;
   - the load, the reasoner, the excludes and entails tests, and the guard test (Jena half).
2. Report, and replace this file with the full phase-1 handoff.
