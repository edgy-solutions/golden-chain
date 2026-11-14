# Finding W-1: why apology-1531 shows no wall where augsburg has one

- **For:** the architect. Answers W-1 in [RULING_report_13.md](RULING_report_13.md).
- **Verdict:** this follows from the spec. It is not a defect: nothing is changed, so there is no new lock or rerun.
- **Source of the cells:** `goldenchain.weigh._cell` and `score`, run over `ingest.union(ingest.derive_rdflib(ds))` at `b58eb21`. The scope is members, and no Holding involved has a `gc:scope`.

## 1. Where augsburg's wall is

The wall is **not** on *infants, taught*. It is on *professing-believers-only, forbidden*.

| Position (locus subjects) | Plumb-line | User stance (§5a) | augsburg | Cell |
|---|---|---|---|---|
| professing-believers-only | required | obligatory | forbidden | **WALL** (CELL[obligatory][forbidden]) |
| infants | forbidden | forbidden | taught | 0.75 (CELL[forbidden][taught]) |

- C(subjects) is the max of the two cells, so it is WALL.
- *Infants, taught* gives 0.75. That is a break, not a wall.
- Report 13's table said only "1 (subjects)". The dispatch-flag line beneath it named "augsburg ix, infants, taught", and the two read as one. That ambiguity is mine.

## 2. What apology-1531 holds

Its effective Holdings, from the derived graph:

| Holding | Modality | How it got there |
|---|---|---|
| `holding/apology-1531/baptism-subjects/infants` | taught | its own |
| `holding/augsburg/baptism-efficacy/necessary-means-of-grace` | taught | inherited (`childOf augsburg`) |

`holding/augsburg/baptism-subjects/professing-believers-only` (forbidden) is **not** among them.

## 3. Why it is not inherited

ADR-0003 §7 (ratified) computes inheritance per Locus:

> If a child Body asserts **any** Holding on Locus L, those Holdings **replace the parent's Holdings on L entirely**. There are no partial merges: a parent Holding on L never survives alongside a child Holding on L, even on a different Position or scope.

The Apology asserts its own Holding on locus subjects (infants). Under §7, that replaces both of augsburg's subjects Holdings, including the forbidden one that makes augsburg's wall. On efficacy the Apology asserts nothing, so it inherits augsburg's Holding there unchanged.

## 4. The score that results

| Locus | w | apology-1531 cell | Kind |
|---|---|---|---|
| subjects | 3 | 0.75 (infants, taught) | cost |
| efficacy | 3 | 0.75 (necessary-means-of-grace, taught) | cost |

- Cost = (3·0.75 + 3·0.75) / (3·0.75 + 3·0.75) = **1.0000 over 2 loci**.
- There are 0 walls.
- Coverage = 6 / 21 = **0.2857**: 7 loci at w = 3, of which 2 are covered.
- augsburg: subjects is a wall, and efficacy is 0.75. Its cost is 1.0000 over 1 locus, coverage 0.2857, with 1 wall.

Both rows match report 13.

## 5. A question for the architect (a data question, not a weigh question)

The number is right for the data as minted. Whether the data is complete is a separate question:

- §7 means a child that restates part of a locus loses its parent's other Positions there.
- The Apology was minted with *infants, taught* only. It was never asked whether Apology IX also holds *professing-believers-only* forbidden, as Augsburg IX does by its condemnation.
- If it does, that is a new Holding with its own source, minted by locked prediction. With it, apology-1531 would wall on subjects as augsburg does.
- I have not minted it. Nothing changes until this is ruled.
