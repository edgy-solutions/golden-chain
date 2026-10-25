# ADR-0003: Controlled vocabularies and the weigh cost function

- Status: Proposed
- Date proposed: 2026-10-25
- Date ratified:
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
- **Scope (proposed):** an optional `gc:scope` from `B vocab/scope/`
  {`all` (default), `officers`, `members`}. This expresses e.g. "required
  of officers, tolerated in members". Phase 1(c) will test whether
  Westminster/1689 need it. If ratified, Holding IRIs gain a `/{scope}`
  segment (ADR-0002).
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

**Who asserts tier (proposal):** tier is an editorial judgment, so it is
asserted only in `data/plumb-line.ttl`, as `gc:tier` on the Locus in the
plumb-line named graph. The graph is the provenance. Other Bodies' own
triage, if ever modelled, is a separate property (Q9).

### 4. Clarity: `B vocab/clarity/`

{`settled`, `contested`, `open`}: plumb-line only, one per Locus.

- `open`: no verdict is rendered and the scoring weight is **0**.
- `contested`: the plumb-line holds a Position but marks it as disputed
  among its own; proposed full weight with a visible badge (Q10).
- `settled`: full weight.

### 5. Weigh: cost runs from the user INTO the Body

Cost answers one question: what would it cost *this user* to join *this
Body*? It is not symmetric, and it is not "how different are they".

**Cell cost** `c(u, b)` for one Position, user modality `u`, Body modality
`b` (in the user's applicable scope; members, unless the user marks
office):

| user ↓ / body → | required | taught | tolerated | forbidden | silent |
|---|---|---|---|---|---|
| **obligatory** | 0 | 0 | 0.25 ᴾ | **WALL** ᴾ | unknown |
| **permitted** | 0.1 ᴾ | 0 | 0 | ≈0 → 0.05 ᴳ | unknown |
| **forbidden** | **WALL** ᴳ | 0.75 ᴾ | 0.5 ᴳ (mid) | 0 | unknown |

ᴳ = given in the brief. ᴾ = proposed here; each needs ratification.

Reasons for the proposed cells:
- *obligatory × forbidden = WALL*: the mirror of the given wall. The Body
  would prevent what the user's conscience requires; joining means
  disobeying one or the other.
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
first = 9, second = 3, third = 1 (proposed) and clarityW is
open = 0, contested = 1, settled = 1. Reason for 9/3/1: a geometric step of 3
means one mid-penalty disagreement (0.5) at a tier costs at least as much as two
maximal (0.75) disagreements one tier down (0.5 × 3 = 1.5 ≥ 2 × 0.75 × 1).
At first order that is 4.5, which outweighs five maximal third-order
disagreements (3.75). The factor is a
parameter, kept in one place and covered by a test.

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

### 6. Derived stances via `excludes` (proposal)

`excludes` is symmetric. In Jena's derived graph only (ADR-0001):
- a Body's `required(P)` with `P excludes Q` derives `forbidden(Q)` for
  that Body, unless the Body explicitly holds Q;
- a user's `obligatory(P)` with `P excludes Q` derives `forbidden(Q)` for
  the user at scoring time.
Derived values are marked as derived and listed separately in any
rendering.

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
- **Tier on Locus as a global fact.** It would make a triage judgment look
  like a property of the question. Rejected in favour of plumb-line-asserted
  tier (pending Q9).
- **Silent = tolerated.** Simpler, but it flatters thin data. Rejected.

## Verification

- SHACL: every Holding has exactly one modality from the scheme, at most
  one scope, and ≥1 `dcterms:source`; every Locus in the plumb-line graph
  has exactly one clarity and one tier.
- Unit tests over the full 3×5 cell table; walls are never summed; open
  loci contribute 0 to both numerator and denominator; the tier factor is
  read from one constant.

## Open points

- Q5: ratify or replace the ᴾ cells, especially obligatory × forbidden =
  WALL.
- Q6: tier weights 9/3/1.
- Q7: inheritance override grain: per Locus (child holding *any* Position
  on L replaces all parent Holdings on L; proposed) or per Position.
- Q8: plumb-line-vs-Body distance needs a mapping from body modality to
  user modality (required→obligatory, taught→obligatory?,
  tolerated→permitted, forbidden→forbidden).
- Q9, Q10: see the handoff.
