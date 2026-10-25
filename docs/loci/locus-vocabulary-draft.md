# Locus vocabulary: draft for ratification

Phase 0, item (d). **Proposal only.** Nothing here is data. Questions are
phrased as questions, not as answers. Tiers are *proposed placeholders* for
the architect; under standing rule 3 no tier enters `data/` except as
authored by the architect in `plumb-line.ttl` (see ADR-0003 and handoff Q9).

## Conventions

- **IRI**: `https://w3id.org/golden-chain/locus/{slug}` (ADR-0002). Slugs
  are kebab-case, never reused, never renamed (deprecate and replace).
- **Gill ref**: Gill's own division, edition-independent.
  `D VI.4` = Doctrinal Book VI ch. 4; `P III.1 §3` = Practical Book III
  ch. 1, Gill's third head; `Diss. 1–5` = the appendix on proselyte
  baptism. Book numbers follow CCEL/first edition, **not** Tegg 1839,
  which renumbers per volume (see source report).
- **Heading**: one of God / Scripture / Man / Christ / Salvation / Church /
  Worship / Last things.
- **Tier**: 1 = first order, 2 = second, 3 = third (proposed).
- **Prac.**: ✓ = drawn from *Practical* Divinity (worship/practice).
- **Named alternative**: who Gill names as holding the view he argues
  against, with evidence class:
  - **T**: the chapter title itself names the alternative.
  - **S**: an explicit "not … as say the X" or equivalent was read in context.
  - **L**: lexical scan hit only (party named ≥1× in chapter, context
    sampled but argument not read). Treat as a lead, not a finding.
  - **—**: no named party found by the scan. *This does not mean Gill
    argues against nobody*: he often writes "the adversaries" or "some"
    without names. Absence is a limit of the heuristic.

  Heuristic reason (rule 7): a word-bounded scan for ~50 party names and
  opponents' names (Arminian, Socinian, Pelagian, Arian, Sabellian, papist,
  paedobaptist, Baxter, Whitby, Lightfoot, Wall, Grotius, etc.) across the
  CCEL text, one sample line per hit. It is cheap and auditable; it
  under-reports, and incidental mentions over-report (e.g. "papist" in a
  list of examples).

## Table (42 loci)

| # | Slug | Question | Gill ref | Heading | Tier | Prac. | Named alternative |
|---|---|---|---|---|---|---|---|
| 1 | `existence-of-god` | Does God exist, and can his being be known from nature? | D I.1 | God | 1 | | Atheists, "deniers of the Being of a God" (S) |
| 2 | `trinity` | Is the one God three distinct Persons? | D I.26–27 | God | 1 | | Arians, Sabellians (S: "not … in the Arian sense", "Nor … in the Sabellian sense"); Socinians (L) |
| 3 | `eternal-generation` | Is the Son eternally begotten of the Father, and the Spirit eternally proceeding? | D I.28 | God | 2 | | Socinians, Sabellians (S) |
| 4 | `deity-of-christ` | Is the Son truly and eternally God? | D I.30 | God | 1 | | Arians, Socinians (S: "Nor God by office, as say the Socinians") |
| 5 | `deity-of-the-spirit` | Is the Holy Spirit a distinct divine Person? | D I.31 | God | 1 | | Socinians (L) |
| 6 | `divine-decree` | Has God decreed whatever comes to pass? | D II.1; D III.4 | God | 2 | | — |
| 7 | `inspiration-of-scripture` | Are the Old and New Testament Scriptures the inspired word of God? | D I.2 | Scripture | 1 | | the Qur'an as rival revelation (L) |
| 8 | `sufficiency-of-scripture` | Is Scripture the sole sufficient rule of faith and practice, without unwritten tradition? | D I.2 | Scripture | 1 or 2 ⚑ | | Papists, "unwritten traditions" (S) |
| 9 | `covenant-of-works` | Was Adam placed under a covenant of works as head of his posterity? | D III.7 | Man | 2 | | — |
| 10 | `imputation-of-adams-sin` | Is Adam's first sin imputed to all his posterity? | D III.10 | Man | 2 | | Pelagians (S: "Not by imitation, as say the Pelagians"); Arminians (S) |
| 11 | `corruption-of-nature` | Is every human by nature wholly corrupted by sin? | D III.11 | Man | 2 | | — |
| 12 | `law-as-rule-of-life` | Is the moral law a rule of life for believers? | D IV.6; P IV.6 | Man | 2 | ✓ (P IV.6) | Papists, "counsels" (L); Socinians, Christ perfecting the law (L) |
| 13 | `incarnation` | Did the Son of God take a true and complete human nature? | D V.1 | Christ | 1 | | Arians (S: "The Arians deny that Christ has an human …"); Sabellians/Patripassians, Socinus (L) |
| 14 | `satisfaction-of-christ` | Did Christ make satisfaction to divine justice for sin by his death? | D VI.5–6; D V.4 | Christ | 1 | | Socinians, Socinus (S) |
| 15 | `extent-of-redemption` | For whom did Christ die: the elect, or all men? | D VI.3–4 | Christ | 2 | | Universal redemption (T: VI.4 "Of those Texts … which seem to Favour Universal Redemption") |
| 16 | `imputed-active-obedience` | Is Christ's active obedience imputed to believers? | D V.3; D VI.8 | Christ | 2 | | — |
| 17 | `election` | Is election unconditional, not grounded on foreseen faith? | D II.2 | Salvation | 2 | | Arminians, Remonstrants (L) |
| 18 | `reprobation` | Has God decreed to pass by some, leaving them in their sin? | D II.3 | Salvation | 2 | | — |
| 19 | `eternal-justification` | Are the elect justified in God's eternal purpose, before faith? | D II.5; D VI.8 | Salvation | 3 | | Baxter, 3× (L); Arminians, papists (L) |
| 20 | `justification-by-faith` | Is justification by imputed righteousness received through faith alone, without works? | D VI.8 | Salvation | 1 | | papists (L, incidental) |
| 21 | `regeneration` | Is regeneration wholly God's act, prior to faith? | D VI.11–12 | Salvation | 2 | | — ("the adversaries", unnamed) |
| 22 | `perseverance` | Will every true believer persevere to final salvation? | D VI.15 | Salvation | 2 | | — |
| 23 | `covenant-administrations` | Are the old and new covenants two administrations of one covenant of grace? | D IV.1–5 | Salvation | 2 | | — ⚑ load-bearing for baptism-subjects |
| 24 | `church-constitution` | Is a gospel church a congregation of believers gathered by mutual consent? | P II.1 | Church | 2 | ✓ | Papists; diocesan and parish/national church (L) |
| 25 | `church-officers` | What standing officers has Christ appointed in his church? | P II.3, II.5 | Church | 2 | ✓ | Diocesan episcopacy (L: "… justify ordination by a diocesan bishop"); popish orders (L) |
| 26 | `church-discipline` | Is the power of discipline and excommunication vested in the congregation? | P II.6 | Church | 2 | ✓ | "papists, prelates, and presbyterians" (S) |
| 27 | `civil-magistrate` | What obedience do believers owe the civil magistrate? | P IV.4 | Church | 3 | ✓ | Papists, clerical exemption (L) |
| 28 | `baptism-perpetuity` | Is water baptism a standing ordinance until Christ returns? | P III.1 §1 | Worship | 2 | ✓ | Socinians, first converts only (S); also unnamed: "ceased" at Christ's death (S) |
| 29 | `johns-baptism` | Was John's baptism the same ordinance as Christian baptism? | P III.1 §1a–d | Worship | 3 | ✓ | — |
| 30 | `baptism-subjects` | Who may be baptized? | P III.1 §3; Diss. 1–5 | Worship | 2 | ✓ | Paedobaptists (S). Rebuts Matt 19:14, household baptisms, Abrahamic covenant/circumcision, Acts 2:39, Rom 11:16, 1 Cor 7:14, antiquity (Origen) |
| 31 | `baptism-mode` | How is baptism administered: immersion, pouring, or sprinkling? | P III.1 §4 | Worship | 2 or 3 ⚑ | ✓ | Sprinkling, pouring (S) |
| 32 | `baptism-formula` | In whose name is baptism administered? | P III.1 §5 | Worship | 1 | ✓ | — |
| 33 | `baptism-significance` | What does baptism signify, and does it effect what it signifies? | P III.1 §6 | Worship | 2 | ✓ | — |
| 34 | `proselyte-baptism-origin` | Is Christian baptism derived from Jewish proselyte baptism? | Diss. 1–5 | Worship | 3 | ✓ | Lightfoot, Dr Wall, Grotius, Paedobaptists (T, S). ⚑ May be an *Argument*, not a Locus (Q11) |
| 35 | `supper-presence` | How is Christ present in the Lord's Supper? | P III.2 §3 | Worship | 2 | ✓ | Papists (L); Socinus (L) |
| 36 | `supper-subjects` | Who may come to the Lord's Supper; is baptism prerequisite? | P III.2 §4 | Worship | 2 | ✓ | Infant communion, third-century practice (S) |
| 37 | `public-prayer` | Are set forms of prayer, including the Lord's Prayer, to be used in public worship? | P III.5–6 | Worship | 3 | ✓ | Papists, Socinians (L) |
| 38 | `singing-in-worship` | Is singing psalms a part of public worship? | P III.7 | Worship | 3 | ✓ | — |
| 39 | `lords-day` | Is the first day of the week the Christian day of worship, in place of the seventh? | P III.8 | Worship | 2 or 3 ⚑ | ✓ | the Jewish sabbath (S) |
| 40 | `intermediate-state` | Does the soul live consciously between death and resurrection? | D VII.2–3 | Last things | 2 | | Socinus, some Arminians, soul-sleep (S); papists, purgatory (L) |
| 41 | `resurrection-of-the-body` | Will the same bodies of the dead be raised? | D VII.4 | Last things | 1 | | Socinians, Quakers (S) |
| 42 | `millennium` | Will Christ reign personally with the saints for a thousand years? | D VII.8 | Last things | 3 | | Whitby (L); "the adversaries of this" (L) |

Considered and left out of the ~40 (available if wanted): `second-coming`
(D VII.5), `eternal-punishment` (D VII.10; Socinians named, S),
`resurrection-of-christ` (D V.6), `repentance` (P I.4), `good-works` (P IV.5),
and the remaining Practical I chapters (graces of internal worship), which
are pastoral rather than contested.

## Baptism loci for phase 1 (proposed scope)

Gill treats these separately within P III.1 or in the Dissertation: 28
`baptism-perpetuity`, 29 `johns-baptism`, 30 `baptism-subjects`, 31
`baptism-mode`, 32 `baptism-formula`, 33 `baptism-significance`, plus 34
`proselyte-baptism-origin` if it is a Locus. 36 `supper-subjects` is where
Gill addresses baptism as a prerequisite to communion; include it or not
(Q12).

## Flags (⚑) summarised

- 8, 31, 39: tier genuinely ambiguous between bodies; the architect's
  call, not mine.
- 23: the paedobaptist case for 30 runs through 23; phase 1 will need at
  least the Positions on 23, or an Argument that cites it.
- 34: Locus vs Argument.
