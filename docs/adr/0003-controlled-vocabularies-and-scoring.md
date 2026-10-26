# ADR-0003: Controlled vocabularies and the weigh cost function

- Status: Ratified with changes (§6 remains a proposal); Revision 1 (2026-10-25) recorded as ruled
- Date proposed: 2026-10-25
- Date ratified: 2026-10-25
- Proposed by: build agent
- Ratified by: architect

## Context

Golden Chain compares Bodies with each other and with a user. Comparison is
arithmetic over identifiers. Rule 3 forbids a model from asserting doctrine,
so every input to the arithmetic must be a value from a closed, published
vocabulary, attached to a traceable source or editorial act. Four
vocabularies are needed, plus a cost function that is deliberately
asymmetric.

Below, `B` = `https://w3id.org/golden-chain/`. All schemes are
`skos:ConceptScheme`s and members are `skos:Concept`s (ADR-0002 pattern
`B vocab/{scheme}/{concept}`).

## Decision

### 1. Body-side modality: `B vocab/modality/`

Carried by a `gc:Holding` (Body, Position, modality[, scope]).

| Concept | Definition (what the Body's source commits it to) |
|---|---|
| `required` | Holding or practising the Position is a condition of membership, communion, or office in the Body. Dissent is grounds for exclusion or discipline. |
| `taught` | The Body affirms and teaches the Position, but dissent does not by itself bar membership. |
| `tolerated` | The Body does not teach the Position but permits it among those in its scope. |
| `forbidden` | The Body rejects the Position. Holding or practising it is grounds for discipline or exclusion. |

- **Silence is not a modality.** No Holding means the Body's sources say
  nothing; scoring treats it as *unknown* (§5), never as `tolerated`.
- **Scope (ratified):** `gc:scope` from `B vocab/scope/` {`all`, `officers`,
  `members`}. Default `all`, and an absent scope means `all`. It expresses
  e.g. "required of officers, tolerated in members". Holding IRIs gain a
  `/{scope}` segment except for `all` (ADR-0002).
- Each Holding carries `dcterms:source` → a Source division
  (e.g. `B source/wcf/28/4`). No Holding without one.

### 2. User-side modality: `B vocab/user-modality/`

Stored in Postgres against Position IRIs (later phase), not in TTL.

| Concept | Meaning for the user |
|---|---|
| `obligatory` | I must hold or practise this. |
| `permitted` | I may hold or practise this; I can live with it either way. |
| `forbidden` | I must not hold or practise this, nor submit to it. |

`user-modality/forbidden` and `modality/forbidden` are **distinct
concepts**: one is a conscience claim, the other a disciplinary one.

### 3. Tier: `B vocab/tier/`

{`first`, `second`, `third`}: first-order (bears on the gospel itself);
second-order (Christians who differ normally cannot share one church
order); third-order (members of one congregation may differ). The language
is the familiar "theological triage" distinction; the definitions here are
operational, for scoring only.

**Who asserts tier (ratified):**
- Tier is a property **of the Locus**: exactly one `gc:tier` per Locus.
- Its source is `data/plumb-line.ttl`. That is the only file that may assert `gc:tier`, and the plumb-line named graph is the provenance.
- There is one authority. Tier is **not** per Body, and no Body-specific tier is modelled.

### 4. Clarity: `B vocab/clarity/`

{`settled`, `contested`, `open`}: plumb-line only, one per Locus.

- `open`: no verdict is rendered and the scoring weight is **0**.
- `contested`: the plumb-line holds a Position but marks it as disputed
  among its own. **Full weight** (ratified). The flag is for display and
  honesty, not for scoring.
- `settled`: full weight.

### 5. Weigh: cost runs from the user INTO the Body

Cost answers one question: what would it cost *this user* to join *this
Body*? It is not symmetric, and it is not "how different are they".

**Cell cost** `c(u, b)` for one Position, user modality `u`, Body modality
`b` (in the user's applicable scope; members, unless the user marks
office):

| user ↓ / body → | required | taught | tolerated | forbidden | silent |
|---|---|---|---|---|---|
| **obligatory** | 0 | 0 | 0.25 | **WALL** | unknown |
| **permitted** | 0.1 | 0 | 0 | 0.05 | unknown |
| **forbidden** | **WALL** | 0.75 | 0.5 | 0 | unknown |

All cells ratified 2026-10-25.

Reasons for the cells:
- *obligatory × forbidden = WALL* (ratified as a hard wall). The Body
  would prevent what the user's conscience requires; joining means
  disobeying one or the other.
  - **Canonical case: an ordinance withheld.** A user holds believer's
    baptism by immersion obligatory for themselves. They join a Body that
    forbids rebaptism of those baptized as infants, and so refuses to
    administer it.
  - The ordinance the user's conscience requires is withheld by the Body's
    discipline. No amount of agreement elsewhere makes that joinable.
- *forbidden × taught = 0.75*: the user would sit under teaching they
  reject, but would not be made to practise it. Worse than tolerated (0.5),
  not a wall.
- *obligatory × tolerated = 0.25*: the user may still do it, but alone and
  untaught.
- *permitted × required = 0.1*: the user can comply, at a small cost in
  liberty.

**Locus cost.** `C(L) = max` over Positions on L of `c(u_P, b_P)`. Max,
not sum, because mutually exclusive Positions on one Locus would otherwise
count the same disagreement twice.

**Weights.** `w(L) = tierW(L) × clarityW(L)`, where tierW is
first = 9, second = 3, third = 1, and clarityW is open = 0,
contested = 1, settled = 1.

- **Reason for 9/3/1 (architect's wording):** "geometric; a single
  second-order disagreement should outweigh any number of third-order
  ones".
- **Finding: the weights do not meet the reason as stated** (recorded,
  not fixed; rule 6).
  - With 9/3/1, one maximal second-order disagreement costs 3 × 0.75 = 2.25.
  - Three maximal third-order disagreements cost 3 × 1 × 0.75 = 2.25, which ties it, and four exceed it.
  - No finite geometric factor makes one outweigh *any number*. Only a lexicographic comparison does: compare by tier first, then by cost within tier.
  - The handoff asks which is intended.
- **Starting weights only.** They are revisited after the first two test
  users.
- **Hard walls are not weighted.** They never enter the sum, whatever the
  tier.
- The factors are parameters, kept in one constant and covered by a test.

**Body score** against a user:
1. **Walls**: the list of loci where any cell is WALL, whatever the tier.
   Walls are not summed into cost; they are reported first.
2. **Cost**: `Σ_L w(L)·C(L) / Σ_L w(L)·0.75` over loci where the user has
   a stance and the Body is not silent, in [0, 1]. (0.75 is the largest
   finite cell.)
3. **Coverage**: the fraction of the user's weighted loci where the Body
   is not silent. Shown beside cost, so silence never reads as agreement.

Ordering: by (wall count ascending, cost ascending), with coverage
displayed. No textual verdict is generated. The UI renders the numbers,
the loci, and the stored Holdings with their sources.

**Open loci score zero** by `clarityW = 0`, and also show no plumb-line
verdict.

### 5a. Plumb-line as a user (ratified)

To weigh a Body against the plumb-line, the plumb-line's Holdings are read
as user stances.

| Plumb-line modality | Read as user modality |
|---|---|
| `required` | `obligatory` |
| `taught` | `obligatory` |
| `tolerated` | `permitted` |
| `forbidden` | `forbidden` |

**Reason:** the plumb-line asserts truth, so what it teaches it holds.
`taught` therefore maps to `obligatory`, not `permitted`.

### 6. Derived stances via `excludes` (proposal; not ratified)

`excludes` is symmetric. In Jena's derived graph only (ADR-0001):
- a Body's `required(P)` with `P excludes Q` derives `forbidden(Q)` for
  that Body, unless the Body explicitly holds Q;
- a user's `obligatory(P)` with `P excludes Q` derives `forbidden(Q)` for
  the user at scoring time.
Derived values are marked as derived and listed separately in any
rendering.

**When `excludes` "fires" (provisional ruling, Q18):** a Body that holds
both Positions of an `excludes` pair as `required` is **derived
inconsistent** by the reasoner. The phase-1 test asserts exactly that.
The build agent's own definition is in the phase-1 handoff, for the
architect to compare.

### 7. Inheritance with overrides (ratified)

`childOf` inheritance is computed **per Locus**:
- If a child Body asserts **any** Holding on Locus L, those Holdings
  **replace the parent's Holdings on L entirely**.
- There are no partial merges: a parent Holding on L never survives
  alongside a child Holding on L, even on a different Position or scope.
- On loci where the child asserts nothing, the parent's Holdings are
  inherited unchanged.

This is non-monotonic (ADR-0001), so it runs as a closed-world SPARQL step
into the derived graph, before scoring.

## Consequences

- Every number the system shows decomposes into vocabulary values with
  sources. No prose is generated (rule 3).
- `silent ≠ tolerated` means sparse Bodies look *uncertain*, not
  *agreeable*. Coverage makes that visible.
- Without scope, confessions that bind officers more than members will be
  mis-scored. That is why scope is proposed now.
- Inheritance (childOf with overrides) changes a Body's Holdings, so it must
  be computed before scoring, in Jena's derived graph.

## Alternatives considered

- **Symmetric distance** (e.g. Hamming over Positions). Rejected by the
  brief: the cost of joining is not the cost of being joined.
- **Sum over Positions per Locus.** Double-counts mutually exclusive
  answers. Rejected in favour of max.
- **Tier per Body** (each Body's own triage). Rejected at ratification:
  one authority. Tier is a Locus property sourced from the plumb-line file.
- **Reduced weight for contested loci.** Rejected: the flag is for honesty,
  not discounting.
- **Per-Position inheritance override.** Rejected: partial merges produce
  Bodies no source describes.
- **Silent = tolerated.** Simpler, but it flatters thin data. Rejected.

## Verification

- SHACL: every Holding has exactly one modality from the scheme, at most
  one scope, and ≥1 `dcterms:source`. Every Locus has exactly one tier, and
  `gc:tier` triples appear only in the plumb-line graph. Every Locus in the
  plumb-line graph has exactly one clarity.
- Tests: the plumb-line mapping table, and per-Locus override (a child
  Holding on L removes *every* parent Holding on L).
- Unit tests over the full 3×5 cell table; walls are never summed; open
  loci contribute 0 to both numerator and denominator; the tier factor is
  read from one constant.

## Open points

- §6 (derived `forbidden` from `required` + `excludes`) is still a
  proposal. The Q18 ruling defines only the inconsistency check.
- Revisit 9/3/1 after the first two test users.
- The 9/3/1 reason vs the arithmetic (finding above): keep the weighted sum
  with this known bound, or order lexicographically by tier?

## Revision 1 (2026-10-25; architect's rulings on report 2, Q11 and Q15)

Recorded as ruled; implemented in `reasoner/20-consistency.ru`; tests in
`tests/test_reasoner.py`. The E1 firing definitions (report 1) stand: excludes
on {required, taught}², and entails on P ∈ {required, taught} with Q forbidden.

1. **Scope in firing (Q11).** `excludes` and `entails` fire only when the two
   Holdings' scopes **intersect**. An absent scope is `all` and intersects
   everything. Two explicit scopes intersect only if they are equal.
   - The born test is "officers-required vs members-tolerated on excluded
     Positions must not fire". It passes, but tolerated never fires anyway, so
     scope is not what keeps it quiet. The tests that exercise scope are
     the 3 × 3 scope grids for excludes and for entails, both with required Holdings.
2. **Two parents (Q15).** A Body with two parents whose effective Holdings
   differ on a Locus is **inconsistent** (rule `parents-differ`), unless it
   asserts its own Holdings on that Locus. No parent is ever picked.
   - "Differ" compares (Position, modality, scope) as sets per Locus, never
     Holding IRIs, because two Bodies' Holdings always have distinct IRIs.
   - *Readings confirmed by the architect (ruling on report 4, Q7, 2026-10-25):*
     - (a) A parent that is **silent** on the Locus is not a difference. The rule
       fires only when both parents speak there.
     - (b) The child **still inherits** both parents' Holdings on that
       Locus (§7 is unchanged), so the inconsistency is visible
       and neither parent is chosen.
     - (c) Only **direct** parents are compared. A diamond further up flags the
       Body that has the two parents, not its descendants.
   - IRI: `B inconsistency/{body}/parents-differ/{locus}`. `gc:involves`
     names the differing Positions.
