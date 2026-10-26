# Source report: Westminster Confession of Faith (1646/1647)

Phase 1, before ingest (rule 4). Research done 2026-10-25. Working copies
were held in the session scratchpad only; nothing is in this repo.

Tags: **[V]** fetched and inspected; **[R]** reported by a secondary source
only; **[U]** unverified.

## What enters the repo (phase 1)

**No confession text.** Phase 1 stores Holdings whose `dcterms:source` is a
division IRI (`B source/wcf/28/4`), with no quotation (the quotation scope is
unfilled; see the Gill report). The texts below are *read* to draft
Holdings; they are not stored. This report still names the edition so that
every division reference points at a known text.

## The work

- Drafted by the Westminster Assembly, 1643–46.
  - Presented to Parliament in 1646 without proofs.
  - Reissued in 1647 "with the Quotations and Texts of Scripture annexed" (Edinburgh: Evan Tyler). [V: title page]
- **33 chapters**, each with numbered paragraphs. [V]
- Paragraph counts for phase-1 chapters: ch. 7 = 6; ch. 25 = 6; ch. 27 = 5; ch. 28 = 7. [V]

### Original (1647) vs American revision

- The American revision was adopted by the Presbyterian Church: Synod 1788, General Assembly 1789. [R]
- It changes 20.4, 23.3 and 31.2 (the civil magistrate). Later changes: 24.4 in 1887; 16.7, 22.3 and 25.6 in 1903. The 1903 PCUSA additions of chapters 34–35 and declaratory statements are [U].
- **Chapters 7, 27 and 28** in the American edition:
  - Proof-text substitutions only, per Schaff's "Am. ed." apparatus. [V]
  - One article dropped: "the" before "effects" in 27.2. [V]
  - The confession text of the phase-1 divisions is otherwise unaffected.
- **25.2** (the visible church "and of their children") carries an "Am. ed." marker in Schaff that was not resolved (open question 2). It sits next to the infant-baptism material.

## Candidate sources

| # | Source | Edition | Licence / terms | Quality |
|---|---|---|---|---|
| A | CCEL, Schaff, *Creeds of Christendom* vol. 3, WCF "with the American Alterations" (`ccel.org/ccel/schaff/creeds3`) | The 1647 text, spelling modernised by Schaff. Latin in parallel; American changes marked. Print source 1889 (Baker reprint). | ThML `DC.Rights` "Public Domain" [V]. CCEL policy [V]: "may be used for personal, educational, or non-profit purposes. Contact us for permission to republish CCEL works or to use them commercially." | Clean. English and Latin are interleaved and need parsing. |
| B | OPC, `opc.org/wcf.html` | **American revised text**, no proof-texts. [V: 23.3, 24.4, 25.6, 31.2 read in revised form] | Footer "© 2026 The Orthodox Presbyterian Church". [V] | Clean, but the wrong text layer. **Do not use as base.** |
| C | IA `humbleadviceofas00west`: Edinburgh, Evan Tyler, 1647 (Princeton Theological Seminary scan, 76 images) | 1647, original spelling | IA `possible-copyright-status: NOT_IN_COPYRIGHT` [V] | Page images authoritative. OCR is poor (long s). |
| D | IA `confessionoffait1675west` (1675) | 1675 | `NOT_IN_COPYRIGHT` [V] | Not inspected. |
| E | IA `creedsofchristen028262mbp`: Schaff vol. 3, Harper 1919 | Page images of A | PD in the US (1877/1919; Schaff died 1893) | Image witness for A. |

Not checked: Wikisource, HathiTrust, denominational sites (presumed
American text). [U]

## Recommendation

| Role | Source |
|---|---|
| Text of record | **The 1647 text.** |
| Reading text | Schaff (A), taking the original reading, never the "Am. ed." insertion. |
| Witness and tiebreaker | The 1647 Tyler page images (C). |
| Never | OPC (B) as a base. |

- **Body identity.** `B body/wcf` is the 1647 Confession.
- **The American text is not a variant of it.** If needed later, it becomes a separate Source and Body (e.g. `B source/wcf-1789`, `B body/wcf-1789`), because Denominations adopt one or the other. ADR-0002 bars version markers in IRIs, so `wcf/20/4@1647`-style suffixes are not used.

## Citation scheme

`B source/wcf/{chapter}/{paragraph}`, arabic numerals (ADR-0002), e.g.
`B source/wcf/28/4`. Proof-texts are not confession text; they are not
ingested in phase 1. They may later become `gc:cites` Passages on the
division, marked with their edition.

## Proof texts as printed (ruling Q16, 2026-10-26)

The phase-1 WCF Arguments cite Passages taken from Schaff's English proof apparatus (A). That supersedes "not ingested in phase 1" in the citation scheme above. Ruling Q16 asks for `gc:asPrinted` strings from the 1647 apparatus "with Scripture proofs", using the same lettered rule as the LBC (ADR-0005, as amended for report 2 Q1).

**Edition**
- *The Humble Advice of the Assembly of Divines … concerning a Confession of Faith: with the Quotations and Texts of Scripture annexed.* [V: title page]
- The proofs first appeared in the London printing of 1647. [R] No image of that printing has been inspected. [U]

**Witness of record (proposed)**
- C: Edinburgh, Evan Tyler, 1647. IA `humbleadviceofas00west`, Princeton Theological Seminary scan, 76 images, `NOT_IN_COPYRIGHT`. [V]
- It is the only 1647 printing with proofs that has been fetched. Whether it is a reprint of the London printing, and whether the two letter their notes identically, is [U].
- Proposed `gc:secondaryLocator`: `"Edinburgh: Evan Tyler, 1647, p. (48)"`, in the same form as the LBC's.

**How the proofs are printed**
- Lettered marginal notes keyed to clauses. [V from OCR letters only]
  - The OCR shows letters in the text of ch. 28, e.g. "baptized m", "it n", "regenerated p", "time r", "perfon f".
  - The note texts cannot be recovered from it (long s, broken sigla). **No string comes from the OCR.**
- Ch. 28 falls on printed pp. (48)–(49). [V from the OCR page markers; one of them reads "(43)"] The pages for chs. 7 and 27 are [U].
- Whether the letters run per chapter, and whether they skip j and v, is [U].

**Rule (as for the LBC)**
- Each lettered note is its own Argument.
- The letter opens `gc:asPrinted` and is the Argument's only `gc:asPrinted`.
- Several notes may support one Position.

**Not yet recorded.** No model views page images. The strings are to be read by the architect on [../handoff/READING_wcf1647_proofs.md](../handoff/READING_wcf1647_proofs.md), and nothing changes in TTL until that form is signed.
- Some current Arguments group proofs that Schaff prints under different clauses. For example, `28/1/002` cites both the ingrafting note (Gal 3:27; Rom 6:5) and the newness-of-life note (Rom 6:3, 4). Under the rule those split.
- Argument counts are predicted once the letters are known.

## Phase-1 divisions

| Division | Topic | Phase-1 locus |
|---|---|---|
| 7.5–7.6 | One covenant of grace, administered differently under law and gospel | covenant-administrations |
| 25.2 | Visible church includes believers "and their children" | context for baptism-subjects |
| 27.1–27.5 | Sacraments: signs and seals; sacramental union; efficacy; two only; Old Testament and New Testament sacraments | baptism-significance |
| 28.1 | Nature of baptism | baptism-perpetuity, baptism-significance |
| 28.2 | Element and minister | baptism-formula |
| 28.3 | Mode: dipping not necessary; pouring or sprinkling | baptism-mode |
| 28.4 | Subjects: professing adults and the infants of one or both believing parents | baptism-subjects |
| 28.5–28.6 | Neglect a great sin, but grace and salvation not inseparably annexed; efficacy not tied to the moment of administration | baptism-significance |
| 28.7 | Once only | baptism-repetition (ruling Q5) |

The locus column is a drafting aid. The Holdings themselves are proposed in
TTL with `status: proposed`.

## Open questions

1. CCEL republication permission is moot while no text enters. It is needed before any quotation is stored.
2. The American reading at 25.2: re-check against Schaff's markup or a 1789 printing. It does not affect phase-1 Holdings, which follow 1647.
3. The 1788/1789 date and the 1903 additions need a primary source. They matter only if `wcf-1789` is ever modelled.
