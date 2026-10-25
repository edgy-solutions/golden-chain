# Handoff: phase 1 (in flight)

- Branch: `phase-0`; `main` was created from the phase-0 commit and pushed.
- State: sources and ADR amendments done. Next is drafting Positions from the sources, then building.

## Done so far

| Commit | What |
|---|---|
| 6d97c03 | BSB inventory and the 156 reconciliation; WCF, LBC and Augsburg source reports; `.gitignore` |
| eb533e3 | ADR 0001–0003 ratified with changes; ADR-0005 proposed; locus rulings (34 is an Argument; scope is 23 + 28–33) |
| 7ce5628 | Architect's provenance note: Gill is PD, front matter excluded, quotation allowed; `gc:pages` locator |

## Remember (not phase 1)

- **The BSB 1984 foreword is a Body.** "Strict Baptist, BSB 1984" reveres Gill and overrides him on three loci:
  - Practical III.1, Gill's introductory remarks on baptism;
  - Practical II.6, church discipline (locus 26);
  - Doctrinal VII.8, the millennium (locus 42): the publishers are amillennial.
- It states numbered propositions on baptism, the church and valid baptisms. It is the worked example of `childOf` with overrides.
- **Tension to rule:** the front matter is excluded from the corpus, but a Body needs a Source. A Holding cites a division reference and stores no text, so the exclusion can hold. To be ruled before it is modelled.

## Next steps

1. Read the phase-1 divisions:
   - Gill: Practical III.1 §§1–6, Doctrinal IV.1–5, Dissertation 1–5;
   - WCF 7, 27, 28;
   - LBC 7, 28, 29;
   - Augsburg II, V, IX, XIII.
   Then propose Positions with their sources.
2. The blank plumb-line form, at `docs/loci/plumb-line-form-phase1.md`.
3. Predict counts, then build:
   - `ontology/core.ttl` and `ontology/shapes.ttl`;
   - the passage canonicaliser and its tests;
   - `data/*.ttl`;
   - the Fuseki config and load;
   - the reasoner and the excludes test;
   - the guard tests;
   - the pre-commit hook.
4. Report, and replace this file with the full phase-1 handoff.
