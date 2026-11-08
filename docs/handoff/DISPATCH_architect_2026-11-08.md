# Architect dispatch, 2026-11-08

Relayed by Chris on 2026-11-08 and filed verbatim, as pasted. Chris's covering line and the closing note addressed to him are left out. Two later relays from the same day, both received during step 1, are filed below the dispatch, also verbatim: the §4 addendum, and the §7 correction with the revised §4 test cases.

Rulings in it are the architect's. Work done under it is recorded in the handoff, the reports and the ADRs, never by editing this file.

```
ARCHITECT DISPATCH — 2026-11-08. Plumb-line sitting signed; doctrine
discussion rulings; new loci; ADR-0003 Revision 2; phase-2 sources.
Read whole before acting. Order of work is at the end.

== 1. THE SIGNED SITTING ==
Chris has signed plumb-line console 7b23646b2c763ae0 (export
2026-11-08T20:24:43Z, name Chris Nogradi, date 2026-11-08). Ingest it
AS IS. It carries "complete": false solely because johns-baptism.
same-ordinance has modality null, which is deliberate silence
(clarity open). Silence is a legitimate plumb-line stance under the
form; the console wrongly treats it as incomplete. The set is
complete. Record the console defect; fix in v3 (below). Every "other"
entry and every note in the export is a mint request or a flag
request and is ruled on below; do not treat them as free text.

== 2. TIER: SEMANTICS AS CHRIS DEFINES THEM ==
Record in ADR-0003 Revision 2 and in the console help:
- first:  disagreement means one party is not a Christian. Chris's
          test: salvation by works, or no profession at all.
- second: both Christians, but fellowship in one church is broken.
- third:  both Christians, difference forbearable within one church.
Tier measures where disagreement separates PEOPLE. It is not
importance, and it is not modality: a third-tier locus can still be
a wall if a body requires what the user forbids.

== 3. MODALITY: SEMANTICS FOR THE PLUMB-LINE (console help text) ==
- required:  a church must hold this for Chris to be a member; a
             condition of membership or office.
- taught:    held as true and taught; not by itself a condition of
             membership. Scores as obligatory, same as required; the
             difference is what the site says.
- tolerated: not held, but Chris could belong to a church that holds
             it.
- forbidden: sin or error such that Chris cannot participate or sit
             under it. The wall.
- silent:    no stance; contributes nothing to scoring; pairs with
             clarity open but is independent of it.

== 4. NEW DIMENSION: unchurches (ADR-0003 Revision 2) ==
Two separations were conflated under tier: "not a Christian" (about
persons; tier first) and "not a church" (about bodies). Add a per-
Position boolean gc:unchurches, settable ONLY by body/plumb-line
(shape). Semantics: a Body that holds or practices a Position flagged
unchurches is excluded from the candidate set as "not a church by
this plumb-line's standard", independent of tier and of conscience
walls; its members' standing as Christians is not asserted either
way. Display it as a category exclusion with that exact wording, not
as a score. Chris's flags from the sitting (notes on the rows):
- baptism-subjects.believers-and-their-infants: unchurches
- baptism-subjects.infants: unchurches
- baptism-formula: every non-triune-name Position, when minted,
  unchurches. triune-name stays required.
Consequence Chris has affirmed and the record must carry: under his
plumb-line, Westminster, Heidelberg/Belgic and Protestant Reformed
bodies are not churches, though full of Christians. State it plainly
where it is derived; do not soften it.

== 5. COVENANT LOCUS: SPLIT (from the "other" on covenant-
administrations) ==
Replace the fused locus with two:
23a "What is the covenant of grace, and when was it made?"
   Positions: (i) eternal, made with Christ as head of the elect, one
   with the covenant of redemption, manifested in time — GILL
   (source: Body, Doctrinal Book II, covenant chapters; mint with
   proofs: 2 Tim 1:9, Titus 1:2, and what Gill cites); (ii) promised
   in eternity, formally established in the new covenant; covenant of
   redemption distinct — COXE (Discourse of the Covenants, 1681, PD);
   (iii) made in time after the fall, administered under law and
   gospel — WCF 7.3-6.
   Plumb-line: (i) taught; (ii) and (iii) tolerated; clarity
   CONTESTED (Chris's words: between Gill and the federalists, to
   settle after reading Witsius). Tier second.
23b "Was the covenant of circumcision an administration of the
   covenant of grace, such that the infant seed are in the
   covenant?" Positions: yes — WCF 7.5-6, 28.4, Heidelberg 74; no —
   Gill (Divine Right of Infant Baptism Examined, PD) and Coxe (dual-
   aspect reading of Gen 17). Plumb-line: yes forbidden; no taught;
   clarity settled; tier second. The existing entails edge E1 moves
   here: 23b-yes entails believers-and-their-infants.
Record an architect finding: Gill DOES speak of the one covenant
"administered" under both testaments; his departure from Westminster
is specifically that the covenant of circumcision is not that
administration. The fused locus had misdescribed him.

== 6. REPETITION POSITION (from the once-only note) ==
Mint under baptism-repetition: "Baptism is administered once. The
sprinkling of an infant is not baptism, so the baptism of a
professing believer who was sprinkled in infancy is his first
baptism, not a repetition." Plumb-line: taught. Sources: Eph 4:5 for
"one baptism"; Gill, Divine Right, or Booth, Paedobaptism Examined,
for "infant sprinkling is not baptism". CAUTION: do not use Acts
19:3-5 as a proof without checking entailment: Gill read v. 5 as
Luke's report of John's baptism, not a rebaptism by Paul, because he
held John's baptism to be the same ordinance; the plumb-line is
silent on that locus. Any Argument from Acts 19 must state which
reading it depends on.
once-only (WCF 28.7) stays at taught for the plumb-line.

== 7. VALIDITY LOCUS (from the repetition-locus note) — mint now ==
"What makes a baptism valid?" Tier second. Positions:
(1) subject and formula suffice; Romish baptism valid — WCF 28, and
    Hodge against Thornwell (Thornwell, Collected Writings vol 3,
    PD; Hodge, Systematic Theology, PD).
(2) subject, mode and formula — mainstream Baptist; LBC 29 read with
    28.2.
(3) (2) plus an administering church of gospel order DEFINED BY
    DOCTRINE — Chris's position; the BSB 1984 foreword reads this way
    (its propositions 1, 7; model that foreword as a Body only in
    phase 3, see §12, but it may be cited now as a source division).
(4) (2) plus an administering church of OUR order, by identity or
    succession — Landmark; source J. R. Graves, Old Landmarkism
    (1880, PD).
Plumb-line: (3) taught; (1) and (2) tolerated; (4) forbidden. Chris's
own statement, verbatim, as the Argument text for (3): "A baptism is
valid when three things hold: the subject is a professing believer;
the administration is according to the Word (immersion, in the
triune name); and the administrator is a church of gospel order, not
identity or succession. A baptism lacking any of the three is no
baptism." Proof texts for (3) to be proposed by you from LBC 28.2's
notes (Mat 28.19; 1 Cor 4.1) and Gill Practical III.1 on the
administrator; Chris signs.
Dependencies to model, not hard-code: (3) depends on the church
locus (LBC 26; Belgic 29; Scots 18; WCF 25.4-5), phase 2; "gospel
order" in the plumb-line reduces to the first-tier justification
test plus right administration, so when the justification locus
exists there is an entails from it into (3). Validity itself stays
tier second.

== 8. INSTRUMENTALITY LOCUS — mint now (phase-1 extension) ==
The Dutch-Baptist line does not run through the efficacy locus; it
runs through three questions: what baptism IS (significance: sign vs
sign-and-seal), HOW it works (instrumentality — missing), and WHOM
it is for (subjects). Mint:
"How does baptism benefit the one baptized?" Tier second. Positions:
(a) instrumental — the Spirit works through the rite to confirm faith
    (Heidelberg 65-66; WCF 27.3; Belgic 33);
(b) representational — the rite sets the reality before faith; faith
    exercised on the reality is strengthened; the Spirit works by the
    Word and the water represents (Gill, Practical III.1);
(c) ex opere operato — phase 2 (Trent; no PD English source chosen
    yet).
Arguments: ONE per passage per position, interpretation on the edge:
1 Pet 3:21 (incl. Peter's qualifier "not the putting away of the
filth of the flesh, but the answer of a good conscience"); Titus 3:5;
Acts 22:16 ("calling on the name of the Lord"); Rom 6:3-4; Col 2:12
("through the faith of the operation of God"); Gal 3:27. This locus
is the first where the `try` view is essential: a user starting from
1 Pet 3:21 must see both readings and the qualifier.
Plumb-line stance NOT yet signed: Chris holds (b) taught; on (a) he
has not decided between tolerated and forbidden. Put (a) on the
follow-up console as an open question with that framing.

== 9. EFFICACY LOCUS: RULINGS AND CORRECTIONS ==
- Tier second, ratified (Chris's sitting). Reason on record: WCF 28.6
  grounds whatever is conferred in the Spirit's work and Christ's
  merit, "to such as that grace belongeth unto", not in the recipient
  or the water; by the plumb-line's first-tier test it is not a works
  gospel. Chris: forbidden stands.
- ARCHITECT ERROR, record as a finding: the architect said
  Heidelberg 73-74 "says similar things" to WCF 28.6. It does not.
  Heidelberg 72-73 is sign-and-pledge-of-assurance language and
  denies the outward washing is the washing away of sin. Heidelberg
  maps to sign-only on this locus, with its own Arguments (HC 69-73),
  not to grace-conferred.
- Phase-2 refinement: grace-conferred-in-right-use hides a range
  (Mercersburg/Nevin, The Mystical Presence, PD; Princeton/Hodge,
  Systematic Theology, PD; New School practice near sign-only).
  Mint separately when American Presbyterian bodies enter.
- The architect's suggested fourth position ("sign and pledge of
  assurance") is WITHDRAWN as premature; revisit only if Heidelberg's
  Arguments do not fit sign-only on inspection.

== 10. SIGNIFICANCE LOCUS ==
Heidelberg 66 ("signs and seals") is the seal position; Heidelberg
74 is the full paedobaptist case (covenant inclusion, sign of the
covenant, circumcision "instead of which baptism is instituted") and
is a source for 23b-yes, sign-and-seal, and the succession claim. The
plumb-line's reading of Rom 4:11 (sealed righteousness to Abraham
personally; baptism does not succeed circumcision) is Gill's and is
already the union-with-christ composite (LBC 29.1): required. An
architect misreading that Chris held sign-succession is withdrawn.

== 11. PHASE-2 LOCI AND SOURCES (record; do not mint) ==
Loci: covenant of works with Adam (positions: yes — WCF 7.2, LBC
19.1/20.1, Gill "Of the Covenant of Works"; no — Hoeksema, Murray
(both copyrighted: reference only), and the Huntington line of Strict
Baptists (PD; verify before claiming)); the Sinai covenant (covenant
of works / typical national covenant / administration of grace;
Chris: Sinai IS the covenant of works, with Huntington, against
Murray and Hoeksema who read Sinai as grace); church marks (Belgic
29, Scots 18, WCF 25.4-5, LBC 26) with a derived, conditional check:
"by this Body's own stated marks, under the plumb-line's judgment of
its baptism, it fails a mark" — display as conditional, never hard-
code the conclusion; Trinity (tier first); justification (tier
first); conditional time salvation (for Primitive Baptist bodies);
administrator/validity is now phase 1 (§7).
Third confession family for phase 2: the Three Forms of Unity
(Belgic, Heidelberg, Dort) with Hoeksema's Declaration of Principles
(1951, PRC) as a Body under them — NOT more Lutheran material.
Sources to add: Witsius, Economy of the Covenants (1822 English, PD)
— the Dutch root of both Gill and the 1689 federalists; Coxe; Gill,
Divine Right of Infant Baptism; Booth; Graves; Nevin; Hodge;
Thornwell vol 3; Huntington (identify the covenant-of-works texts).

== 12. BILL LEE AND THE BAPTIST STANDARD BEARER ==
Chris holds Bill Lee's sermons, writings and notes (Lee has died).
- Add Body subclass gc:Teacher (a person's corpus). body/bill-lee is
  a Teacher; body/bsb is a separate institutional Body; the 1984
  foreword is a SourceDivision authored by Lee under BSB. Model
  nothing from them before phase 3.
- Permission: Lee's verbal grant covers only what he could give and
  does not bind his estate. Corpus stays private, by configured
  path. Before any Lee text appears on the site: written permission
  from the estate and from BSB's current principals, filed beside
  the text. Record this as a rule in docs/sources/.
- Phase 3 design note: Lee's corpus is the first unstructured source
  and the first real use of Weaviate: embed sermons; the model
  PROPOSES "passage speaks to locus X, position Y"; Chris signs each
  proposed Holding in a console; model routes, never asserts.
  Validation: the plumb-line's distance to body/bill-lee should be
  small; if it is not, scoring is wrong before anything else.

== 13. CONSOLE v3 ==
- silence (modality null) is a complete verdict; status must say so.
- help panel carries §2 and §3 verbatim.
- an unchurches checkbox per Position row, enabled only on the plumb-
  line console, once ADR-0003 Revision 2 is ratified.
- follow-up console for this sitting (new build) with rows: 23a (i)-
  (iii) stances to confirm as written; 23b confirm; validity (1)-(4)
  confirm as written; instrumentality (a) stance (open), (b) confirm;
  repetition position confirm; unchurches confirm on the three
  flagged rows. Chris signs; agent proposes nothing doctrinal.

== 14. ARCHITECT FINDINGS TO RECORD (against the architect) ==
Heidelberg/WCF efficacy conflation (§9); Gill sign-succession
misread (§10); fused covenant locus misdescribed Gill (§5); foot-
strip hypothesis refuted (report 10); "every strip" clause stricter
than goat-yard's acceptance (report 6). All on record as falsified or
withdrawn; none edited.

== 15. ORDER OF WORK ==
1. Ingest the signed sitting as is; record the console defect.
2. Draft ADR-0003 Revision 2 (tier semantics §2, modality text §3,
   unchurches §4, instrumentality as a locus §8). Proposed until
   ratified; send up.
3. Mint 23a/23b (§5), the repetition position (§6), the validity
   locus (§7), the instrumentality locus (§8), with proofs and
   locked counts. Status proposed throughout.
4. Console v3 and the follow-up sitting (§13). Chris signs.
5. Ingest; first real `weigh` run of the plumb-line against Gill,
   WCF, LBC, Augsburg; report distances and every wall and every
   unchurches exclusion with its derivation.
6. Continue standing items: A2 single-rule fixture; Q11 crops
   console; OCR of the baptism chapters on v1 with the italic-flag
   baseline.
Predict counts before every step. Stop and report after 2 and after
5. Push as you go.
```

## §4 addendum (relayed 2026-11-08, during step 1)

```
§4 addendum: unchurches implies a tier-2 break; a tier-2 break does
not imply unchurches. Test cases for the shape and the display: a
Strict Baptist church requiring hymns (tier-2 break, is a church); a
Presbyterian church (tier-2 break and unchurches); a Primitive
Baptist church demanding rebaptism (tier-2 break and repetition
wall, is a church under validity position 3). All three must render
differently.
```

## §7 correction and §4 test cases revised (relayed 2026-11-08, during step 1)

Chris relayed this with his own line: "so fyi some stricts do require rebaptism to my knowledge so keep this in mind". The revised test cases replace the addendum's. Case (c) now names Strict as well as Primitive Baptists.

```
§7 correction: do NOT assume the BSB 1984 foreword holds validity
position 3. Its proposition 7 ("churches of New Testament origin and
order") may be position 4 (succession) in doctrinal dress. Read it
and propose; Chris rules. The plumb-line's position 3 may have no
published source on the shelf; if so, the plumb-line's own signed
Argument carries it (ADR-0006), and finding a published source is a
phase-2 task.
§4 test cases, revised: (a) a 1689 Reformed Baptist church with
hymns and instruments — tier-2 break on worship, no baptism wall, is
a church; (b) a Presbyterian church — tier-2 break, unchurches; (c)
a Strict or Primitive Baptist church demanding rebaptism — tier-2
break and repetition wall, is a church under position 3. All three
render differently.
```
