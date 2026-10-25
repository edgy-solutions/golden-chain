# Phase-1 Positions, Arguments and Holdings: draft

- Status: **proposed** (build agent, 2026-10-25). Nothing here is data until it is in TTL with `gc:status proposed`, and nothing is ratified until the architect rules.
- Scope: loci 23 and 28–33 (locus draft, "Phase-1 scope").
- Method:
  - A Position is minted only where a source in hand **affirms** it **and adduces at least one Passage** for it (rule 2).
  - An answer that a source only names or rebuts is listed under "Named, not mintable". It is not minted.
  - Gill's sub-head labels (`§3c`, `§3e3b2`) are CCEL's outline labels. They are allowed on `gc:locator` (ADR-0002), but are not Gill's own wording. Printed pages (`gc:pages`) are filled at build time from the BSB page images: P III.1 = BSB pp. 896–915.
- Texts used:
  - Gill: CCEL (locating), checked against the BSB page images.
  - WCF: Schaff/CCEL 1647 text and proof texts. Schaff's bracketed `[Am. ed. …]` additions are **excluded**.
  - LBC: the bibleresearcher transcription (locating), checked against the IA 1719 witness OCR.
  - Augsburg: Schaff Latin/English (locating). Triglot is the text of record.

## Positions

| # | Position IRI (`B position/…`) | Answer | Affirmed by (division) |
|---|---|---|---|
| 23a | `covenant-administrations/one-covenant-two-administrations` | One covenant of grace in substance, administered in two ways: before Christ (old) and after (new). | Gill D IV.1, D IV.5; WCF 7.5–6 |
| 28a | `baptism-perpetuity/standing-ordinance-to-the-end` | Water baptism is a standing ordinance, to continue until the end of the world. | Gill P III.1 §1, §1d; WCF 28.1; LBC 28.1 |
| 29a | `johns-baptism/same-ordinance` | John's baptism and the apostles' baptism are one and the same ordinance. | Gill P III.1 §1, §1a–d |
| 30a | `baptism-subjects/professing-believers-only` | Only those who profess repentance and faith are to be baptized. | Gill P III.1 §3a–e; Diss. 5; LBC 29.2 |
| 30b | `baptism-subjects/believers-and-their-infants` | Professing believers, and the infants of one or both believing parents. | WCF 28.4 |
| 31a | `baptism-mode/immersion-only` | Baptism is immersion. Immersion is necessary to its due administration. | Gill P III.1 §4; LBC 29.4 |
| 31b | `baptism-mode/pouring-or-sprinkling-sufficient` | Dipping is not necessary. Pouring or sprinkling is right administration. | WCF 28.3 |
| 32a | `baptism-formula/triune-name` | In the name of the Father, and of the Son, and of the Holy Spirit. | Gill P III.1 §5 (§1c); WCF 28.2; LBC 29.3 |
| 33a | `baptism-significance/sign-only` | A sign of union with Christ in his death and resurrection. It does not of itself confer what it signifies. | Gill P III.1 §6a–d, §3e3b2; LBC 29.1 (see F3) |
| 33b | `baptism-significance/sign-and-seal-conferring-grace` | A sign and seal of the covenant of grace. By its right use, the Spirit confers the grace promised to those it belongs to, in God's time. | WCF 27.1–3, 28.1, 28.5–6 |

**Blocked (no Passage in any source in hand; rule 2, F1):**

| # | Would-be Position | Answer | Affirmed by |
|---|---|---|---|
| 30c | `baptism-subjects/infants` | Children are to be baptized; no parental condition stated. | Augsburg IX |
| 33c | `baptism-significance/necessary-means-of-grace` | Necessary to salvation; by it the grace of God is offered; those born again by baptism and the Spirit. | Augsburg IX, II (XIII, V) |

### Named, not mintable (a source rebuts them; none affirms them)

| Locus | Answer named | Named by |
|---|---|---|
| 28 | Baptism ceased at Christ's death | Gill §1 |
| 28 | Only the first converts in a nation (and their children) are baptized (Socinians) | Gill §1 |
| 28 | Baptism was in use before John | Gill §1 |
| 29 | John's baptism differs from Christian baptism | Gill §1a–d (implicit) |

The plumb-line form lists only minted and blocked Positions.

## Arguments

- Each row is one proposed Argument.
  - `supports` is exactly one Position.
  - `cites` is a list of Passages: OSIS, KJV v11n, and canonical per ADR-0002.
- Confession Arguments cite the proof texts attached **to the clause that states the Position**, not every proof text in the paragraph.
- No `gc:quotation` is proposed in phase 1. It is allowed for Gill, but each one needs a page-image check. They are added one by one, later.

### Gill (`B source/gill-body/…`)

| Division | Locator | Supports | Cites |
|---|---|---|---|
| doctrinal/4/1 | — | 23a | Heb.8.7-Heb.8.8, Heb.8.13, Heb.9.1, Heb.9.15, Heb.12.24 |
| doctrinal/4/5 | §1a | 23a | Heb.9.10, Gal.3.24-Gal.3.25 (F6: "Gal. 3:1-4") |
| practical/3/1 | §1d | 28a | Matt.28.19-Matt.28.20, Acts.8.36, Acts.8.38-Acts.8.39, Acts.10.47-Acts.10.48 |
| practical/3/1 | §1 | 29a | Matt.3.13-Matt.3.17, John.4.2, John.3.22-John.3.23, John.3.26, John.4.1-John.4.2 |
| practical/3/1 | §1a | 29a | Matt.3.6-Matt.3.8, Mark.1.4, Acts.2.38, Acts.19.4-Acts.19.5, Mark.16.16, Acts.8.36-Acts.8.37 |
| practical/3/1 | §1b | 29a | Matt.3.6, Matt.3.16, John.3.23, Acts.8.38-Acts.8.39 |
| practical/3/1 | §1c | 29a | Acts.19.5, Acts.8.16, Acts.10.48, Matt.28.19 |
| practical/3/1 | §1d | 29a | Mark.1.4, Acts.8.38 (F6) |
| practical/3/1 | §3a | 30a | Acts.9.18 |
| practical/3/1 | §3b | 30a | Matt.3.6, Acts.2.37-Acts.2.38, Acts.2.41 |
| practical/3/1 | §3c | 30a | Mark.16.16, Acts.8.36, Acts.8.12, Acts.18.8 |
| practical/3/1 | §3d | 30a | John.4.1 |
| practical/3/1 | §3e | 30a | Acts.10.47, Gal.3.2 |
| dissertation/5 | — | 30a | Luke.7.30, Matt.3.7 (F7) |
| practical/3/1 | §4b | 31a | Matt.3.6, Matt.3.13, Matt.3.16, John.3.23 |
| practical/3/1 | §4c | 31a | Mark.1.9 |
| practical/3/1 | §4d | 31a | Rom.6.4, Col.2.12 |
| practical/3/1 | §4e1 | 31a | 1Pet.3.20-1Pet.3.21, Rom.6.4-Rom.6.5, Col.2.12 |
| practical/3/1 | §4e2 | 31a | 1Cor.10.1-1Cor.10.2 |
| practical/3/1 | §5 | 32a | Matt.28.19, Acts.8.16, Acts.10.48 |
| practical/3/1 | §6a | 33a | Rom.6.4-Rom.6.5, Col.2.12 |
| practical/3/1 | §6b | 33a | Mark.1.4, Acts.2.38 |
| practical/3/1 | §6c | 33a | Acts.22.16 |
| practical/3/1 | §6d | 33a | 1Pet.3.21 |
| practical/3/1 | §3e3b2 | 33a | Rom.4.11 |

**Deferred (Q7):**
- Gill's rebuttals: §3e1 on Matt 19:14; §3e2 on the household baptisms; §3e3 on the covenant, circumcision, 1 Cor 7:14 and Acts 2:39.
- §4a, the lexical argument (no Passage).
- §4e3–5.

### WCF (`B source/wcf/…`)

| Division | Clause | Supports | Cites |
|---|---|---|---|
| 7/5 | "differently administered" | 23a | 2Cor.3.6-2Cor.3.9 |
| 7/6 | "not … two covenants … but one and the same" | 23a | Gal.3.14, Gal.3.16, Acts.15.11, Rom.3.21-Rom.3.23, Rom.3.30, Ps.32.1, Rom.4.3, Rom.4.6, Rom.4.16-Rom.4.17, Rom.4.23-Rom.4.24, Heb.13.8 |
| 28/1 | "to be continued … until the end of the world" | 28a | Matt.28.19-Matt.28.20 |
| 28/2 | "in the name of the Father …" | 32a | Matt.3.11, John.1.33, Matt.28.19-Matt.28.20 |
| 28/3 | "pouring or sprinkling" | 31b | Heb.9.10, Heb.9.19-Heb.9.22, Acts.2.41, Acts.16.33, Mark.7.4 |
| 28/4 | "infants of one or both believing parents" | 30b | Gen.17.7, Gen.17.9, Gal.3.9, Gal.3.14, Col.2.11-Col.2.12, Acts.2.38-Acts.2.39, Rom.4.11-Rom.4.12, 1Cor.7.14, Matt.28.19, Mark.10.13-Mark.10.16, Luke.18.15 |
| 27/1 | "signs and seals of the covenant of grace" | 33b | Rom.4.11, Gen.17.7, Gen.17.10 |
| 28/1 | "sign and seal of the covenant of grace" | 33b | Rom.4.11, Col.2.11-Col.2.12 |
| 28/6 | "really exhibited and conferred by the Holy Ghost" | 33b | Gal.3.27, Titus.3.5, Eph.5.25-Eph.5.26, Acts.2.38, Acts.2.41 |

### LBC 1689 (`B source/lbc-1689/…`)

| Division | Supports | Cites |
|---|---|---|
| 28/1 | 28a | Matt.28.19-Matt.28.20, 1Cor.11.26 |
| 29/1 | 33a | Rom.6.3-Rom.6.5, Col.2.12, Gal.3.27, Mark.1.4, Acts.26.16 (F5), Rom.6.2, Rom.6.4 |
| 29/2 | 30a | Mark.16.16, Acts.8.36-Acts.8.37 (F5) |
| 29/3 | 32a | Matt.28.19-Matt.28.20, Acts.8.38 |
| 29/4 | 31a | Matt.3.16, John.3.23 |

### Augsburg

None. Articles II, V, IX and XIII adduce no Scripture (F1).

## Holdings (proposed modality)

The proposed modality follows the text's own force:
- the text states a condition or necessity → `required`;
- it affirms or teaches → `taught`;
- it condemns or rejects → `forbidden`;
- it denies only by implication → **?**, left for the architect.

Every Holding has `dcterms:source` = the division.

| Body | Locus | Position | Modality | Basis (division: words) |
|---|---|---|---|---|
| wcf | 23 | 23a | taught | 7.5–6: "not … two covenants of grace … but one and the same" |
| wcf | 28 | 28a | taught | 28.1: "to be continued in his Church until the end of the world" |
| wcf | 30 | 30b | taught | 28.4: "are to be baptized" |
| wcf | 30 | 30a | **?** (forbidden) | 28.4: "Not only those … but also"; 28.7: "but once to be administered" (F4) |
| wcf | 31 | 31b | taught | 28.3: "rightly administered by pouring or sprinkling" |
| wcf | 31 | 31a | **?** (forbidden) | 28.3: "Dipping … is not necessary" |
| wcf | 32 | 32a | taught | 28.2 |
| wcf | 33 | 33b | taught | 27.1, 27.3, 28.1, 28.6 |
| lbc-1689 | 28 | 28a | taught | 28.1 |
| lbc-1689 | 30 | 30a | taught | 29.2: "the only proper subjects" |
| lbc-1689 | 31 | 31a | required | 29.4: "necessary to the due administration" |
| lbc-1689 | 32 | 32a | taught | 29.3 |
| lbc-1689 | 33 | 33a | taught (F3) | 29.1: "a sign of his fellowship with him" |
| augsburg | 30 | 30a | forbidden | IX: "Damnant Anabaptistas, qui improbant Baptismum puerorum" |
| augsburg | 30 | 30c | taught | IX (blocked, F1) |
| augsburg | 33 | 33c | taught | IX, II (blocked, F1) |
| gill (Q1) | 23 | 23a | taught | D IV.1: "though the covenant is but one, there are different administrations of it" |
| gill | 28 | 28a | taught | P III.1 §1 |
| gill | 29 | 29a | taught | P III.1 §1 |
| gill | 30 | 30a | taught | P III.1 §3 |
| gill | 30 | 30b | forbidden | P III.1 §2: "a mere invention of men"; §3: "not the infants of any" |
| gill | 31 | 31a | taught | P III.1 §4 |
| gill | 31 | 31b | forbidden | P III.1 §2, §4: sprinkling "cannot, with any propriety, be called a mode of baptism" |
| gill | 32 | 32a | taught | P III.1 §5 |
| gill | 33 | 33a | taught | P III.1 §6c: "it has no such virtue in it" |
| gill | 33 | 33b | **?** (forbidden) | P III.1 §3e3b2: "nor is baptism a seal of it" |

The Augsburg Holdings on 30c and 33c cannot exist until their Positions do.

## Edges

### `excludes` (proposed pairs)

| Pair | Evidence |
|---|---|
| 30a ⟂ 30b | Same question; "only" vs "not only … but also" (WCF 28.4; LBC 29.2) |
| 30a ⟂ 30c | Same question; Augsburg IX condemns the "only" |
| 31a ⟂ 31b | Same question; LBC 29.4 "necessary" vs WCF 28.3 "not necessary" |
| 33a ⟂ 33b | Gill §3e3b2 denies the seal; Gill §6c denies "virtue in it" |
| 33a ⟂ 33c | Gill §6c vs Augsburg IX "necessary to salvation" |
| 33b ⟂ 33c? | WCF 28.5: grace and salvation "not so inseparably annexed … that no person can be … saved without it". This is **uncertain**: Lutheran "necessary" is commonly read as ordinary necessity. Left for the architect. |

### `entails` (proposed: the first real edge)

**E1: `30b believers-and-their-infants` entails `23a one-covenant-two-administrations`.**

- WCF grounds 28.4 in the covenant's continuity. Its proof texts are Gen 17:7, 9 *with* Gal 3:9, 14, Col 2:11–12 and Rom 4:11–12. WCF 7.5 lists circumcision among the old administration's ordinances, and 27.5 holds the sacraments of the two Testaments the same in substance.
- The restriction to infants "of believing parents" is what the covenant argument supplies.

**The reverse is refuted by the data.** Gill holds 23a (D IV.1) and forbids 30b (P III.1 §2–3). Under the entails test below, 23a → 30b would make Gill inconsistent. Gill's own rebuttal (§3e3a–b) is the argument against that edge.

**Why E1 is attached to 30b and not 30c.** Augsburg baptizes children without the covenant argument. An edge from 30c would make the reasoner attribute a covenant theology to a Body that never states one.

## Definitions (Q18: the build agent's, for comparison with the architect's)

- **`P excludes Q`** (symmetric): no holder can consistently affirm both P and Q.
  - It fires (`gc:inconsistent`, derived graph) when a Body, after inheritance, holds **both** P and Q with modality in {`required`, `taught`}.
  - The architect's provisional ruling fires only on `required` × `required`. That ruling is a strict subset of mine, so the ruled test passes under either definition.
  - I propose `taught` as well. A Body that *teaches* two incompatible answers is as inconsistent as one that requires them.
- **`P entails Q`** (directed): whoever affirms P is committed to Q.
  - It fires (`gc:inconsistent`) when a Body holds P in {`required`, `taught`} and Q as `forbidden`.
  - It **does not derive a Holding on Q** for a silent Body. Deriving one would put words in a Body's mouth (rule 3), as in the Augsburg case above.
- **The check, both ways:** before an edge is ratified, the reasoner runs over the source Bodies. An edge that makes a source Body inconsistent is refuted by the data and is not asserted. E1 passes this check on the phase-1 Holdings; its reverse fails.

## Findings

- **F1. Augsburg cites no Scripture** in II, V, IX or XIII.
  - Under rule 2, 30c and 33c cannot be minted from Augsburg alone. That includes the "third position on efficacy" that the architect chose Augsburg to supply.
  - Augsburg's Holdings on Positions minted from other sources can still stand: Holdings need a source division, not a Passage. One example is IX's condemnation of 30a.
  - Options for the architect:
    - (a) Admit a second Book of Concord text from the same PD Triglot as the Argument source. The Small Catechism IV cites Mark 16:16, Titus 3:5 and Rom 6:4; the Apology IX also cites Scripture.
    - (b) Relax rule 2 for confession-only Positions.
    - (c) Leave 30c and 33c unminted in phase 1.
- **F2. Locus 23 has a single mintable Position.**
  - LBC 7.3 ("revealed … by farther steps, until the full discovery thereof was completed in the new Testament") omits WCF 7.5–6's "differently administered". It does not deny it.
  - Treating the omission as a distinct Position would be reading a silence. So no LBC Holding on 23 is proposed.
- **F3. Locus 33 asks two questions**: what baptism signifies, and whether it effects it.
  - LBC 29.1 answers only the first ("a sign"). An LBC Holding on 33a therefore asserts "does not confer", which LBC does not say.
  - Proposal: split 33 into `baptism-significance` and `baptism-efficacy`. Otherwise, mark LBC as silent on 33.
- **F4. The canonical WALL case** (ADR-0003 §5: an ordinance withheld) needs WCF to hold 30a or 31a as `forbidden`.
  - WCF rejects both only by implication: 28.4 "not only", 28.3 "not necessary", and 28.7 "but once".
  - The case therefore depends on the **?** rows.
- **F5. LBC proof-text variants.**
  - 29.1 prints "Acts 26.16". The 1719 witness agrees; the transcription notes 22:16 as the likely intent. Proposal: cite as printed and leave the correction to the architect.
  - 29.2: the transcription reads "Act. 8.36,37", but the 1719 OCR reads "Acts 8. 37, 38". It is to be read from the page image before minting.
- **F6. Gill citations to read on the page image:**
  - §1d "Acts 8:38" (2:38 would fit the remission-of-sins clause);
  - D IV.5 §1a "Gal. 3:1-4" (4:1–4 fits "children … under tutors");
  - §4e4 "Ps. 62:7".
  - Each is cited as printed unless the page image differs.
- **F7. Dissertation 5** is cited from the extracted list. Its citations' context is to be read before minting.
- **F8. WCF 7.6 prints "Gal. ii. 17"** for "Christ the substance". Schaff's American edition reads Col 2:17. That proof belongs to the Christ-the-substance clause, not to the Position's clause, so it is not cited.

## Merges proposed (Q13)

| Merge | Evidence |
|---|---|
| Gill's and LBC's answers to 33 as one Position (33a) | Both: a sign of union with Christ in death and resurrection, remission, and newness of life (Gill §6a–c; LBC 29.1). Contingent on F3. |
| Gill's and WCF's answers to 23 as one Position (23a) | Gill D IV.1: "though the covenant is but one, there are different administrations of it". WCF 7.6: "one and the same, under various dispensations". |
| Gill §1c/§5 and WCF 28.2/LBC 29.3 as 32a | Gill reads "in the name of the Lord Jesus" (Acts 8:16) as "a part of the form for the whole". It is the same answer. |

No merge between 30b and 30c is proposed. They differ in scope ("of believing parents" vs unstated).

## Counts if accepted as drafted (prediction for the build)

| Item | Count |
|---|---|
| Positions | 10 minted + 2 blocked |
| Arguments | Gill 25, WCF 9, LBC 5 = **39** |
| Holdings | WCF 8, LBC 5, Augsburg 1 (+2 blocked), Gill 10 = **24** minted |
| `excludes` | 3: 30a⟂30b, 31a⟂31b, 33a⟂33b (the other pairs involve blocked Positions) |
| `entails` | 1 |

Distinct Passages and the triple counts are predicted at build time, after the canonicaliser exists.
