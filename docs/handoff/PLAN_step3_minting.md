# Plan: step 3 minting (dispatch 2026-11-08 §15, step 3)

2026-11-08. The build agent proposes; the architect rules. All new Positions, Arguments, Holdings and edges are `status proposed`, `proposedBy agent/build-agent`. No doctrine is asserted: labels are the dispatch's wordings, and every Argument points at a printed proof.

The architect's order: "Mint positions as their sources land; lock counts per batch. The follow-up console goes out only when all step-3 positions are minted."

| Batch | Loci | State |
|---|---|---|
| A | 23a covenant of grace; 23b circumcision covenant; retire 23 | Sources verified on page images. Minting now. |
| B | repetition; validity | Waits on M1, M2, M5. |
| C | instrumentality | Waits on M3, M4. |

## Batch A

### Loci (data/loci.ttl)

- `locus/covenant-of-grace`: notation "23a", heading salvation, question "What is the covenant of grace, and when was it made?" (dispatch §5).
- `locus/circumcision-covenant`: notation "23b", heading salvation, question "Was the covenant of circumcision an administration of the covenant of grace, such that the infant seed are in the covenant?"
- `locus/covenant-administrations` is retired (ruling on report 11; ADR-0002 rule 3). Its IRI stays, with `owl:deprecated true` and `dcterms:isReplacedBy` 23a and 23b. Its Position, Holdings and Arguments stay as they are. It is excluded from scoring. Its signed tier (second) carries to 23a and 23b only as a console proposed value, so 23a and 23b have no tier in data until the follow-up console is signed (2 ingest warnings, expected).

### Positions

| IRI under `position/` | Label (dispatch §5) |
|---|---|
| covenant-of-grace/eternal-with-christ | (i) Eternal, made with Christ as head of the elect, one with the covenant of redemption, manifested in time. |
| covenant-of-grace/established-in-new-covenant | (ii) Promised in eternity, formally established in the new covenant; the covenant of redemption distinct. |
| covenant-of-grace/made-in-time-after-fall | (iii) Made in time after the fall, administered under law and gospel. |
| circumcision-covenant/administration-of-grace | Yes. |
| circumcision-covenant/not-an-administration-of-grace | No. |

The 23a(ii) wording outruns Coxe's text ([../sources/coxe-covenants.md](../sources/coxe-covenants.md)); that finding stands for the architect. The locators below fit either wording.

### Edges

- **E1 moves** (ruling on report 11). Remove `believers-and-their-infants gc:entails one-covenant-two-administrations`. Add `circumcision-covenant/administration-of-grace gc:entails baptism-subjects/believers-and-their-infants`. The entails count stays 1.
- No excludes edge is minted between 23b yes and no, or among the 23a positions. Neither was ruled (M9).

### Sources

| IRI under `source/` | Kind | Label |
|---|---|---|
| gill-body/doctrinal/2/15 | division | Doctrinal Divinity, Book II, Chap. XV: Of the Properties of the Covenant of Grace (from p. 247) |
| wcf/7/3 | division | WCF 7.3 |
| coxe-covenants | work | Nehemiah Coxe, *A Discourse of the Covenants that God made with Men before the Law* (London, 1681), Wing C6717 |
| coxe-covenants/2/10, 2/11, 5/8 | divisions | Coxe ch. II §10; ch. II §11; ch. V §8 |
| gill-divine-right | work | John Gill, *The Divine Right of Infant-Baptism, Examined and Disproved* (London, 1749), ESTC T67557 |
| gill-divine-right/4 | division | *Divine Right*, ch. IV |

Leaf maps, checked on the scans: Coxe `n` = p + 9; *Divine Right* `n` = p + 3; WCF 1647 leaf 24 for 7.3 and 7.5.

### Arguments (16)

All proofs below were read on the page images by the build agent. Chris signs from the pixels.

| Argument | Supports | Locator; pages | asPrinted | Cites |
|---|---|---|---|---|
| gill-body/doctrinal/2/15/001 | 23a(i) | "1."; p. 247 | Eph. i. 3, 4. 2 Tim. i. 9. | Eph 1:3–4; 2 Tim 1:9 |
| gill-body/doctrinal/2/15/002 | 23a(i) | "1."; p. 247 | Tit. i. 2. 2 Tim. i. 1. | Titus 1:2; 2 Tim 1:1 |
| gill-body/doctrinal/2/15/003 | 23a(i) | "1."; p. 247 | Psalm lxxxix. 2, 3, 28. and ciii. 17. John xvii. 23, 24. Eph. i. 4. Prov. viii. 23. Mic. v. 2. | Ps 89:2–3, 89:28, 103:17; John 17:23–24; Eph 1:4; Prov 8:23; Mic 5:2 |
| coxe-covenants/2/10/001 | 23a(ii) | II §10; p. 36 | 2 Tim. 1. 9, 10. Tit. 1. 1, 2. | 2 Tim 1:9–10; Titus 1:1–2 |
| coxe-covenants/2/10/002 | 23a(ii) | II §10; p. 37 | Prov. 8. 22,—31. | Prov 8:22–31 |
| coxe-covenants/2/11/001 | 23a(ii) | II §11; p. 38 | Gen. 3. 5. | Gen 3:15 (resolutionNote: misprint, by context) |
| wcf/7/3/001 | 23a(iii) | 7.3, note e; leaf 24 | e Gal.3,21 Rom.8,3 Rom.3,20,21 Gen.3,15 Isa.42,6 | Gal 3:21; Rom 8:3; Rom 3:20–21; Gen 3:15; Isa 42:6 |
| wcf/7/5/002 | 23a(iii) | 7.5, note i; leaf 24 | i 2 Cor.3, 6,7 8,9 | 2 Cor 3:6–9 |
| wcf/7/5/003 | 23b yes | 7.5, note k; leaf 24 | k Heb.8, 9, 10 chapters Rom.4, 11 Col.2,11,12 1 Cor.5,7 | Rom 4:11; Col 2:11–12; 1 Cor 5:7 (resolutionNote: the chapter-level Heb 8–10 is not cited, M8) |
| wcf/28/4/003 | 23b yes | 28.4, note m; leaf 57 | as 28/4/001 | as 28/4/001, with its resolutionNote |
| coxe-covenants/5/8/001 | 23b no | V §8; pp. 105–107 | Gen. 17. 4, 5. Rom. 4. 17. Rom. 4. 11. | Gen 17:4–5; Rom 4:17; Rom 4:11 (resolutionNote: "Rom. 4." and the margin "Gal. 3." are not cited, M8; the "Rom" of 4.11 looks like "Rcm" on leaf 116) |
| gill-divine-right/4/001 | 23b no | First, 1.; p. 45 | Acts vii. 8. Gal. v. 2, 3, 4. | Acts 7:8; Gal 5:2–4 |
| gill-divine-right/4/002 | 23b no | First, 2.; p. 45 | Gen. xvii. 9, 10, 11, 12, 13, 14. | Gen 17:9–14 |
| gill-divine-right/4/003 | 23b no | First, 3.; p. 46 | Gen. xvii. 14. Ps. lxxxix. 34. | Gen 17:14; Ps 89:34 |
| gill-divine-right/4/004 | 23b no | First, 4.; p. 46 | Gen. xvii. 6, 8. ver. 5. | Gen 17:6, 17:8, 17:5 (resolutionNote: "ver. 5." is Gen 17:5 by context) |
| gill-divine-right/4/005 | 23b no | First, 6.; p. 47 | Gal. iii. 16. | Gal 3:16 |

Notes on the table.

- 7.5 note i already supports the retired position (wcf/7/5/001). An Argument supports exactly one Position, so 23a(iii) gets its own Argument. The same holds for 28.4 note m.
- Gill's heads 5 and 7 of the First Enquiry print no Scripture, so they make no Argument (M1).
- The long s is transcribed "s" (Ps. for Pſ.).

### Holdings (+3, taught)

| Holding | Position | dcterms:source |
|---|---|---|
| holding/wcf/covenant-of-grace/made-in-time-after-fall | 23a(iii) | wcf/7/3, 7/5, 7/6 |
| holding/wcf/circumcision-covenant/administration-of-grace | 23b yes | wcf/7/5, 28/4 |
| holding/gill/covenant-of-grace/eternal-with-christ | 23a(i) | gill-body/doctrinal/2/15 |

No Gill Holding is minted on 23b no. The *Divine Right* is not the Body's work (M5). Coxe is not a phase-1 Body.

### Console spec

`plumb_line.make_spec` skips `owl:deprecated` loci. The test keeps its check against the signed form for every unchanged locus, and checks that 23a and 23b appear in place of 23 with their positions.

### Predicted counts

| | Before | After |
|---|---|---|
| Locus | 9 | 11 |
| Position | 15 | 20 |
| Argument | 54 | 70 |
| Passage | 100 | 130 |
| Holding, holds | 47 | 50 |
| effectivelyHolds | 48 | 51 |
| answers | 15 | 20 |
| supports | 54 | 70 |
| excludes, entails, childOf, Body | 5, 1, 1, 8 | unchanged |
| warnings | 0 | 2 |
| violations | 0 | 0 |

Locked in `~/.golden-chain/step3-batchA-predictions-locked.txt` before the change.

## Batch B: repetition and validity (outline)

- **Repetition, taught.** Eph 4:5 (Belgic XXXIV, p. 427, proofs). Booth or Gill *Divine Right* for "infant sprinkling is not baptism". Acts 19:3–5 only with the reading stated.
- **Validity.**
  - (3): Chris's Argument text. Its proofs are LBC 28.2's notes (Matt 28:19; 1 Cor 4:1) and Gill Practical III.1. The BSB foreword, pp. vii–viii, props. 1 and 7, is cited as a source division, with Chris's testimony recorded as testimony.
  - (1): BRPR 1845, p. 469. It prints no Scripture (M1).
  - (2): Booth vol. 2.
  - (4): Graves, ch. X, p. 124.

## Batch C: instrumentality (outline)

- Mint (a) "grace conferred by the Spirit through the sign" and (b) "representational only". (c) ex opere operato is deferred to phase 2.
- Mint the excludes edge between (a) and (b), with the note that (a) as Reformed theology holds it includes representation. Nothing is derived from the edge.
- One Argument per passage per position.
  - (b), from Gill Practical III.1, Sixthly, p. 914: Rom 6:4–5, Col 2:12, Acts 22:16, 1 Pet 3:21.
  - Gill does not cite Titus 3:5, Rom 6:3 or Gal 3:27 in the chapter. His heads 2–4 say baptism is a means of leading faith to Christ. That reads close to (a) and is flagged for Chris before he signs (b).
  - (a): see M4.

## Questions for the architect

- **M1. Sources that print no Scripture.** An Argument must cite at least one Passage. BRPR 1845 (validity 1), Thornwell, the BSB foreword, and two of Gill's First Enquiry heads print none. Proposal: they enter as `dcterms:source` on Holdings (for Bodies) or as notes, never as Arguments.
- **M2. A gc:source for Chris's (3) statement.** Proposal: a plumb-line SourceDivision, e.g. `source/plumb-line/validity-3`, labelled as Chris's signed statement.
- **M3. Notes.** Arguments have no note property, and bare-triple edges cannot carry a note. Rulings require two: the testimony on (3), and the note on the instrumentality excludes edge. Proposal: an ADR adding `gc:note` to Arguments, and a reified or annotated edge for the excludes note. Until then the note is a TTL comment.
- **M4. Per-passage sources for instrumentality (a).** Candidates: WCF 28.1's notes (Titus 3:5; Rom 6:3–4; Gal 3:27; Col 2:11–12), WCF 27.3, Belgic XXXIII's proofs, Heidelberg via Harbaugh 1889. Which source carries each passage?
- **M5. Holdings from a Body's non-confessional works.** May Gill's *Divine Right* ground a `body/gill` Holding? And do WCF and LBC hold a validity position at all?
- **M6. E1(ii)'s refutation is not visible to the machine.** Augsburg holds `believers-and-their-infants` and not 23b yes. Nothing in the data records why direction (ii) was refused.
- **M7. Resolved.** 2 Tim 1:9 is in Gill II.15, p. 247 (also II.10 §4), not II.7, p. 216.
- **M8. Chapter-level references.** WCF 7.5 note k ("Heb.8, 9, 10 chapters"), Coxe "Rom. 4." and "Gal. 3.". Passages are verse ranges, so these are left out of `gc:cites` and recorded in a resolutionNote. Should whole chapters be minted as Passages?
- **M9. Exclusion among the new positions.** Should 23b yes and no be minted as excluding each other? Should the three 23a positions be?
- **M10. LBC 7.3.** It says the covenant was revealed from Gen 3:15 by further steps until its full discovery in the New Testament. That reads like 23a(ii). LBC holds nothing on 23a yet.
- **M11. WCF 7.6 note n.** It prints "Gal, 2, 17", which is probably Col 2:17. It is not cited in Batch A.
