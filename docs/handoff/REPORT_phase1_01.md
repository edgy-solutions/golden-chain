# Phase-1 report 1 (2026-10-25)

For: the architect.

## What was done

| Commit | Files | What |
|---|---|---|
| 7ce5628 | `docs/sources/gill-body-of-divinity.md` | The provenance note is recorded: Gill is PD; BSB 2019 reprints Tegg 1839, which reprints 1769–70; front matter excluded; verbal permission kept as history only; quotation scope filled. |
| 5036d3d | `docs/handoff/HANDOFF_phase1.md` | The foreword-as-Body note (not phase 1). |
| 02dc53b | `docs/loci/positions-phase1-draft.md`, `docs/loci/plumb-line-form-phase1.md` | Positions, Arguments, Holdings and edges, all *proposed*. The blank plumb-line form has Tier, Clarity and Modality left empty. |
| a4b280a | `.githooks/pre-commit`, `fuseki/config.ttl`, `ontology/vocab.ttl`, `pyproject.toml`, `goldenchain/__init__.py`, `tests/*` | Infrastructure on ratified ADRs only. The hook is active in this clone and passed its own commit. |

**Sources read** for the draft:
- Gill: D IV.1 and IV.5, P III.1 §§1–6, and the Dissertation chapter heads (ch. 5 read in part).
- WCF 7, 25.2, 27 and 28.
- LBC 7, 28 and 29.
- Augsburg II, V, IX and XIII.

## Predicted vs actual

| Item | Predicted | Actual |
|---|---|---|
| Tests (hook 7 + Fuseki config 3 + vocab 5) | 15 pass | **15 pass** |
| Vocabulary schemes / concepts | 5 / 16 | 5 / 16 |
| P III.1 printed pages (PDF − 53) | 896–915 | Matches: OCR spot checks at pp. 898 and 912 |
| Phase-1 Positions (the brief's expectation: Gill, WCF, LBC, and Augsburg as a third on efficacy) | ≥ 2 per contested locus | **10 mintable + 2 blocked**. Loci 23, 28, 29 and 32 have one Position each (F2); Augsburg's two are blocked (F1). |
| Draft counts if accepted | — | Arguments 39 (Gill 25, WCF 9, LBC 5); Holdings 24; excludes 3; entails 1 |

The divergence on Augsburg is a finding, not a fix. See F1.

## The build agent's excludes definition (Q18)

- **P excludes Q** (symmetric): no holder can consistently affirm both.
  - It fires (`gc:inconsistent`) when a Body, after inheritance, holds both P and Q with a modality in {`required`, `taught`}.
  - The architect's provisional ruling (`required` × `required`) is a strict subset of this, so the ruled test passes under either definition.
- **P entails Q** (directed): it fires when a Body holds P as `required` or `taught` and holds Q as `forbidden`.
  - It **never derives a Holding** for a silent Body.
- **Refutation check:** an edge that makes a source Body inconsistent is refuted by the data.
  - E1 (30b `believers-and-their-infants` → 23a `one-covenant-two-administrations`) passes this check.
  - The reverse fails on Gill, who holds 23a and forbids 30b.

## Open questions

1. **Gill as a Body** (`B body/gill`)? The draft proposes 10 Gill Holdings, and the 1984 foreword needs Gill as its `childOf` parent.
2. **F1: Augsburg adduces no Scripture** in II, V, IX or XIII, so its efficacy Position fails rule 2. Options:
   - (a) admit the Small Catechism IV or the Apology IX from the same PD Triglot as Argument sources;
   - (b) relax rule 2 for confession-only Positions;
   - (c) defer.
3. **F3: split locus 33** into significance and efficacy? LBC 29.1 says only "a sign".
4. **F4: the canonical WALL case** needs WCF to *forbid* 30a or 31a, but the text rejects both only by implication (28.3, 28.4, 28.7). Rule the three "?" modalities.
5. **E1**, the first `entails` edge: ratify? Also the definitions above, and whether `taught` × `taught` fires `excludes`.
6. **F5 and F6, proof-text slips and variants:**
   - LBC 29.1 prints "Acts 26.16";
   - LBC 29.2 reads 8:36–37 in the transcription but 8:37–38 in the 1719 OCR;
   - Gill prints "Acts viii. 38", "Gal. iii. 1–4" and "Ps. lxii. 7".
   Cite as printed? A human page-image look is needed for the LBC 29.2 reading, because the working rules bar me from reading images.
7. **F9:** `gc:locator` in Gill's printed numbering, with CCEL's outline label as a second literal?
8. **The versification table source** (rule 4, reported first): the KJV v11n counts from CrossWire SWORD `canon.h` (GPL-2 code; the counts are facts), re-keyed into a `.py` table and checked at 66 / 1,189 / 31,102.
9. **ADR-0005:** ratify the status vocabulary, `B agent/` and the closed Argument shape. Also: edges as ratified as their weaker Position, and the plumb-line resources carrying `ratified` directly.
10. Carried from before:
    - the text-layer discrepancy (no text layer on Gill's pages in the configured file);
    - a sentence cap on quotations;
    - `augsburg/{article}` and the Latin/German layer ruling;
    - 9/3/1 weights vs lexicographic ordering;
    - the foreword-Body vs front-matter-excluded tension;
    - LBC 26, still unread.

## Next, on "continue"

- **With rulings on 1–9:**
  - the canonicaliser and its versification table;
  - `ontology/core.ttl` and `ontology/shapes.ttl`;
  - `data/{gill-body-of-divinity,westminster,lbc-1689,augsburg}.ttl` from the draft, with counts predicted first;
  - the Fuseki load, the reasoner, the excludes and entails tests, and the guard test (Jena half).
- **Without rulings:** stop. Everything left depends on one of them.
