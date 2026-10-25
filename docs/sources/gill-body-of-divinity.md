# Source report: John Gill, A Body of Doctrinal and Practical Divinity

Phase 0, item (c). Nothing has been downloaded into this repo. Working copies
used for this survey were held in the agent's session scratchpad only.

## The work

- John Gill (1697–1771). *A Body of Doctrinal Divinity* (London, 1769, 2
  vols) and *A Body of Practical Divinity* (London, 1770, 1 vol), later
  issued together as *A Complete Body of Doctrinal and Practical Divinity*.
- Author died 1771; the text is public domain worldwide.
- Structure (Gill's own division):
  - Doctrinal: Books I–VII, 107 chapters.
  - Practical: Books I–IV, 44 chapters.
  - Appendix: *A Dissertation concerning the Baptism of Jewish Proselytes*,
    5 chapters.
  - Total 156 chapters.

**Predicted vs actual.** Predicted 156 chapters (7 + 4 books + appendix, from
secondary description). Extracted from CCEL headings: 107 + 44 + 5 = 156.
Doctrinal per book 31/16/13/7/14/15/11; Practical 24/6/8/6.

## Candidate sources

| # | Source | Edition | Format | Licence / terms | Text quality |
|---|---|---|---|---|---|
| A | CCEL: [Doctrinal](https://ccel.org/ccel/gill/doctrinal), [Practical](https://ccel.org/ccel/gill/practical) | **Not stated** anywhere in the text or landing page | HTML, ThML XML, UTF-8 TXT, PDF, ePub | Underlying text PD. CCEL terms: "may be used for personal, educational, or non-profit purposes"; republishing or commercial use requires CCEL permission. No copyright claimed on transcription specifically. | Good, clean transcription; chapter headings consistent. Defects seen: OCR-style typos in headings ("OOF", "OFICERS"); **Practical I.8 heading reads "Of the Grace of God" where the Tegg 1839 contents read "Of Hope"** (and I.9 opens "After faith and hope follows love"). Appendix is mislabelled "Book V". Internal outline numbering (e.g. `3e3b3c4f`) is CCEL's normalisation, not Gill's. |
| B | Internet Archive / Princeton Theological Seminary: [v.1](https://archive.org/details/completebodyofdo01gill), [v.2](https://archive.org/details/completebodyofdo02gill) | London: T. Tegg, 1839, 2 vols (BT70 .G5 1839, OCLC 2315397) | Page images (PDF/JP2) + raw OCR | PD; IA "No known copyright"; scans freely reusable | Page images authoritative. OCR is noisy (PTS estimates ~6% error). **Tegg renumbers books per volume**: v.2 Book I = Doctrinal VI, Book V = Practical III. No "CHAP." labels in the body. |
| C | Internet Archive / PTS: [completebodyofdo00gill](https://archive.org/details/completebodyofdo00gill) | Philadelphia: Delaplaine & Hellings, 1810 | Page images + OCR | PD (IA copyright evidence recorded 2008) | Not yet inspected; may be the Staughton abridgment (check before use). |
| D | Wellcome Collection: [1769 Doctrinal](https://wellcomecollection.org/works/bdrtp9zy), [1770 Practical v.3](https://wellcomecollection.org/works/gh24b4qd), [1796 3 vols](https://wellcomecollection.org/works/vjb9pcsc) | First edition 1769–70; Winterbotham 1796 | Page images (IIIF), some OCR | PD; Wellcome images generally CC-BY or PDM (to confirm per item) | Not yet inspected. First edition is the only edition with Gill's own book numbering beyond doubt. |
| E | Monergism ebook | Unstated | ePub, mobi, PDF | Unstated | Not fetchable by automated client (HTTP 403). Not recommended without provenance. |
| F | HathiTrust records (1796, 1810, 1839) | as listed | Page images | PD in US | Duplicates B–D; not inspected (HTTP 403 to automated client). |

## Recommendation

**Cite Gill by his own division; use CCEL as the working text; use the 1839
Tegg page images (B) as the citation witness; confirm book numbering against
the 1769–70 first edition (D) once.**

1. **Citation key is edition-independent.** Positions and Arguments cite
   `Doctrinal VI.4`, `Practical III.1 §3`, `Dissertation 5`, never "Tegg vol.
   2 Book V". Book numbering differs between editions (finding above), so a
   page-or-volume-based key would not be stable. See ADR-0002 (source IRIs).
2. **CCEL (A) is the locator.** Its chapter structure matches Gill's division
   and its text is clean enough to find sections. Its terms of use restrict
   republication, so **no CCEL text enters the repo**: only references, and
   at most short quotations whose wording has been checked against the page
   images (fair use regardless of CCEL terms; PD regardless of edition).
3. **Tegg 1839 (B) is the witness.** Free page images, an explicit PD
   statement, and it is the edition most later reprints follow. Where an
   Argument quotes Gill, the quotation is checked against B and the
   locator records the Tegg volume and page as a secondary pointer.
4. **First edition (D) settles numbering.** One check against the 1769
   Doctrinal and 1770 Practical title pages and contents, before phase 1,
   that Books I–VII / I–IV are Gill's own numbering.
5. **Correct CCEL's Practical I.8 title to "Of Hope"** in any locus
   vocabulary drawn from it.

## What enters the repo from this source (proposal)

- Chapter and section references (as IRIs; ADR-0002).
- Passage references Gill cites, as OSIS ranges.
- Optional short verbatim quotation per Argument, checked against B.
- **No** wholesale text. No CCEL files. No OCR dumps.
