# ADR-0003: Controlled vocabularies and the weigh cost function

- Status: Ratified with changes (§6 remains a proposal); Revision 1 (2026-10-25) recorded as ruled; Revision 2 (2026-11-08) proposed
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

## Revision 2 (2026-11-08; proposed, not ratified)

Drafted by the build agent from the architect's dispatch of 2026-11-08, §§2, 3, 4 and 8, together with the §4 addendum and the revised §4 test cases relayed the same day ([../handoff/DISPATCH_architect_2026-11-08.md](../handoff/DISPATCH_architect_2026-11-08.md)). Nothing in it is built until it is ratified (rule 5). Text quoted from the dispatch is verbatim. Everything else is the build agent's proposal, and each choice the architect has not already made is listed under R2.6.

### R2.1 Tier semantics (replaces the definitions in §3)

Who asserts tier is unchanged: one `gc:tier` per Locus, only in `data/plumb-line.ttl`. The definitions in §3 ("bears on the gospel itself", and so on) are replaced by the plumb-line's own, which also go into the console help (ADR-0006):

> - first:  disagreement means one party is not a Christian. Chris's test: salvation by works, or no profession at all.
> - second: both Christians, but fellowship in one church is broken.
> - third:  both Christians, difference forbearable within one church.
>
> Tier measures where disagreement separates PEOPLE. It is not importance, and it is not modality: a third-tier locus can still be a wall if a body requires what the user forbids.

The weigh arithmetic in §5 is unchanged. In particular, walls are found on every tier, third included, as §5 already says ("whatever the tier").

### R2.2 Modality semantics for the plumb-line (console help text)

> - required:  a church must hold this for Chris to be a member; a condition of membership or office.
> - taught:    held as true and taught; not by itself a condition of membership. Scores as obligatory, same as required; the difference is what the site says.
> - tolerated: not held, but Chris could belong to a church that holds it.
> - forbidden: sin or error such that Chris cannot participate or sit under it. The wall.
> - silent:    no stance; contributes nothing to scoring; pairs with clarity open but is independent of it.

How this fits what is already ratified:

- **These are the plumb-line's answers, in the first person.** §1's table still defines Body modality by what a Body's source commits it to. The four concepts are the same `B vocab/modality/` concepts. §5a's mapping (required and taught → obligatory) is unchanged, and the "taught" line above restates it.
- **Silent writes nothing.** On a Body, silence is not a modality and no Holding is written (§1). The same holds on the plumb-line: a silent row writes no Holding. In §5 the plumb-line, read as the user, then has no stance on that Position, so it "contributes nothing to scoring" by construction. It is not the Body-side `silent` column of §5, which means *unknown*.
- **Silent is independent of clarity.** A silent Position may sit on a settled or contested Locus. An open Locus scores 0 by `clarityW` whatever its Positions say.
- **Silent is a complete verdict.** The console must export it as complete (the console v2 defect; [../handoff/SIGNED_plumb_line_7b23646b2c763ae0.md](../handoff/SIGNED_plumb_line_7b23646b2c763ae0.md)).

### R2.3 `unchurches`: a category, not a score

Two separations had been conflated under tier. "Not a Christian" is about persons: that is tier first. "Not a church" is about bodies: that is this flag.

**Vocabulary and assertion.** `gc:unchurches` is a per-Position boolean, set only by `body/plumb-line`. Proposed form:

- an `owl:DatatypeProperty` with domain `gc:Position`;
- asserted only in the plumb-line graph, and so only in `data/plumb-line.ttl`. As with tier, this is checked in `goldenchain/ingest.py`, not in SHACL;
- written only as `true`, at most once per Position; absence means not flagged.

The sitting writes it from the console v3 checkbox (ADR-0006; dispatch §13), and nothing else may write it.

**Shapes (proposed).** Ingest rejects a Position flagged `unchurches` unless both of these hold:

1. **The plumb-line holds it `forbidden`.** A Body cannot be unchurched for holding what the plumb-line tolerates, teaches or is silent on.
2. **Its Locus is not tier third.** This follows the addendum: "unchurches implies a tier-2 break; a tier-2 break does not imply unchurches." A third-tier difference is by definition "forbearable within one church", so it cannot unchurch.

**Semantics (the dispatch's words).** A Body that holds or practises a Position flagged unchurches:

> is excluded from the candidate set as "not a church by this plumb-line's standard", independent of tier and of conscience walls; its members' standing as Christians is not asserted either way.

**Derivation (proposed).**

- **What triggers it.** A Body is excluded when one of its *effective* Holdings is on a flagged Position with modality `required` or `taught`. Effective means after `childOf` inheritance (§7); a Body's own Holdings override its parent's, as §7 rules. "Holds" is read as `required` or `taught`, the same pair on which `excludes` fires (Revision 1). `tolerated` is R2.6 (1).
- **What does not trigger it.** A §6 derived stance never triggers exclusion, while §6 remains a proposal.
- **Scope.** Any scope triggers it.
- **Where it runs.** The exclusion is computed before walls and cost.

**Display.** The excluded Body is not ranked and shows no cost and no walls. It is listed under its own heading, "Not a church by this plumb-line's standard", and the listing gives:

- the exact wording above;
- for each triggering Holding: the Position, its modality and its `dcterms:source`;
- the plumb-line's flag and its sitting;
- the sentence "Its members' standing as Christians is not asserted either way."

No number is shown for it.

**The consequence, stated plainly.** The flags from the sitting are on `baptism-subjects.believers-and-their-infants` and `baptism-subjects.infants`. When the non-triune formula Positions are minted, they carry the flag too (`triune-name` stays required). By this plumb-line's standard, the following are not churches, though full of Christians:

- every Body that requires or teaches infant baptism. Chris has affirmed that this means Westminster, Heidelberg/Belgic and Protestant Reformed bodies.
- **In the data as it stands, the derivation reaches further than that list.** WCF requires believers-and-their-infants (WCF 28.4), and it is excluded. *The Augsburg Confession teaches infants (AC IX), and so does the Apology (1531) in its own Holding. Both are excluded on the same rule.* That reach follows from "holds or practises" and was not in the list Chris affirmed. It is stated here so that he reads it before ratification.

**What tier-2 break means for display (proposed).** For one Body against the plumb-line, a Locus is a *break* when either of these holds:

- some cell on it is WALL;
- some cell on it costs 0.25 or more, which happens only where the plumb-line's stance is obligatory or forbidden.

The permitted row (0.1, 0.05) is liberty, not disagreement, and never makes a break. A *tier-2 break* is a break on a second-tier Locus.

The addendum's implication then holds by construction, and a test can check it. An unchurches Position is plumb-line `forbidden` (shape 1) on a Locus that is not third tier (shape 2). A triggering Holding is `required` (WALL) or `taught` (0.75). So every excluded Body has a break on that Locus, at tier second or first.

**Test cases (the revised addendum; all three must render differently).**

| Case | Expected rendering |
|---|---|
| (a) a 1689 Reformed Baptist church with hymns and instruments | Ranked. A tier-2 break on worship; no baptism wall; is a church. |
| (b) a Presbyterian church | Not ranked. Listed as "not a church by this plumb-line's standard", with its derivation. It has a tier-2 break, which is implied. |
| (c) a Strict or Primitive Baptist church demanding rebaptism | Ranked, with its wall listed first (§5 ordering). A tier-2 break and a repetition wall; is a church under validity position 3. |

These cases are synthetic test fixtures under `tests/`, not data. Case (a) needs a worship Locus, which is not minted. Case (c) depends on how the validity and repetition Positions are minted (step 3): its wall arises where the Body requires a Position the plumb-line forbids. The fixtures follow the minted shapes. The tests assert three distinct renderings and the implication above.

### R2.4 Instrumentality as a Locus (dispatch §8)

The Dutch-Baptist line runs through three questions, not through efficacy:

- what baptism *is*: the significance Locus, sign or sign-and-seal;
- *how* it works: instrumentality, a new Locus;
- *whom* it is for: the subjects Locus.

The new Locus is "How does baptism benefit the one baptized?", tier second. Its Positions are:

- (a) instrumental (Heidelberg 65–66; WCF 27.3; Belgic 33);
- (b) representational (Gill, Practical III.1);
- (c) ex opere operato, deferred to phase 2.

Minting is step 3, with locked counts. For scoring and vocabulary, Revision 2 records:

- **One Argument per passage per Position**, with the interpretation on the Argument: 1 Pet 3:21 (with Peter's qualifier), Titus 3:5, Acts 22:16, Rom 6:3–4, Col 2:12 and Gal 3:27. No new vocabulary is needed; this is the ADR-0005 Argument.
- **The plumb-line stance is not yet signed.** (b) is to be confirmed as taught. (a) is open between tolerated and forbidden and goes on the follow-up console (dispatch §13).
- **Until (a) is signed, the Locus scores on (b) alone.** The plumb-line is silent on (a), so a Body that holds (a) is scored only through its stance on (b). If that Body is silent on (b), the Locus is *unknown* for it: it lowers coverage and adds no cost. This holds unless an edge between (a) and (b) is minted and §6 is ratified. See R2.6 (5).
- **The tier is not yet in data.** The new Locus has no `gc:tier` until a signed sitting writes it, so ingest warns "Locus has no tier yet" on it. The same applies to 23a, 23b and the validity Locus.

### R2.5 Verification (once ratified)

- **Ingest:**
  - `gc:unchurches` only in the plumb-line graph, only `true`, at most one per Position, and only on gc:Position subjects;
  - shape 1 (plumb-line `forbidden`) and shape 2 (Locus not third tier), each with a refusing test.
- **Weigh:**
  - exclusion before walls and cost;
  - inherited Holdings trigger it, and a child's own Holding on the Locus overrides its parent's;
  - a §6-derived stance never triggers it;
  - each of the three cases renders distinctly;
  - every excluded Body has a tier-2 or tier-1 break on the flagged Locus.
- **Plumb-line silence:** a silent row writes no Holding and changes neither cost nor coverage. This is already tested at ingest, in `tests/test_console_specs.py`.

### R2.6 Open points for the architect

1. **Tolerated.** Does a Body that *tolerates* a flagged Position "practise" it? An example is a Body that administers infant baptism on request without teaching it. Proposed: no, only `required` and `taught` trigger exclusion.
2. **First tier.** May a first-tier Locus carry `unchurches`? Shape 2 allows it, because it forbids only third tier. The addendum speaks only of tier 2.
3. **Bodies that are not churches.** Bodies in the data are documents (Confession, Catechism, Systematic), and from phase 3 there will be Teachers. Proposed: apply the exclusion to every Body class with the exact wording, since a confession speaks for the churches that hold it. Alternatively, Systematic and Teacher Bodies could take a different label.
4. **Tier-2 break.** Is "break" as defined in R2.3 (WALL, or a cell of 0.25 or more) the intended reading for display?
5. **Instrumentality.** Should (a) and (b) be an `excludes` pair, given that §6 is still a proposal?
6. **Other users.** `unchurches` is the plumb-line's standard. Whether it excludes Bodies for other users (user stances, a later phase) is not decided here.
