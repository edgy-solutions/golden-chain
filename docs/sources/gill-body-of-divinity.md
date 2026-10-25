# Source report: John Gill, A Body of Doctrinal and Practical Divinity

Phase 0, item (c); amended in phase 1 after the architect review of
2026-10-25. The working text is now the Baptist Standard Bearer edition
(section *Working text* below), which supersedes the phase-0 recommendation.
That recommendation is kept at the end of this report as history.

Nothing from any edition is in this repo. Working copies are held outside
the working tree only (rule 9).

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

## Working text (ratified 2026-10-25): Baptist Standard Bearer 2019

| Field | Value |
|---|---|
| Title | *A Complete Body of Doctrinal and Practical Divinity: or a System of Evangelical Truths, Deduced from the Sacred Scriptures*. "A New Edition". |
| Publisher | The Baptist Standard Bearer, Inc., Paris, Arkansas. Reprinted 2019. |
| ISBN | 978-1-57978-023-4 (ISBN-10 1579780237) |
| Underlying edition | A photographic reprint of the 1839 London edition (Tegg, per the architect). It reproduces that edition's "Advertisement" signed **London, June 1839**: "a verbatim reprint of the original, in 3 vols. quarto … excepting … typographical errors". The original imprint is replaced by the BSB's, so the scan itself does not name the 1839 publisher (finding 1). |
| Licence (architect, 2026-10-25) | **Gill's text is public domain.** BSB 2019 is a faithful reproduction of the 1839 London edition. Per its Advertisement, that edition is a verbatim reprint of Gill's own 1769–70 quarto. A faithful reproduction of a PD text acquires no new copyright, so Gill's words are used, displayed and quoted freely. **BSB front matter is excluded** from the corpus and from all data: the publisher's foreword (dated 20 October 1984), imprint and back-matter catalogue. The 1839 portrait and memoir are PD but are not Gill's text and are not used. The publisher's **verbal permission** is noted here as history only and is **not relied on**. (The architect's note says this is not legal advice.) |
| Location | The private corpus, read-only, by configured path: `$GOLDEN_CHAIN_CORPUS/gill/9781579780234_A Complete Body of Doctrinal & Practical Divinity.pdf`. Never committed, never copied into this repo (rule 9; `*.pdf` is gitignored). |
| Identity | SHA-256 `cdfd7fdc519766d8a63ba8fc83e26a2ae7f437d752d0be58ff49dfd00ccb0f22`; 260,232,644 bytes. A guard can check the configured file against this hash before any page locator is trusted. |

### Inventory

- **Pages:** 1086 PDF pages, not encrypted. Produced with Adobe Acrobat Pro DC 19.10, created 2019-02-07. Page size 432 × 648 pt (6 × 9 in).
- **Text layer: none on Gill's pages** in the file at the configured path (hash above).
  - Every page is a single image XObject with no fonts and no text operators.
  - The only extractable text is on six BSB catalogue pages (PDF pp. 1080–1085).
  - There is no outline or bookmarks.
  - The architect's note quotes OCR text from this edition ("3reeman", "BaptiR"). That text did not come from this file: it may be a viewer's on-the-fly OCR, or another copy (open question).
  - For locating headings, local Tesseract 5.5 OCR is held in the session scratchpad, outside the repo. OCR is never a quotation source.
- **Layout:**

  | PDF pages | Content |
  |---|---|
  | 1–6 | Title pages and imprint |
  | 5 | 1839 Advertisement |
  | 7–15 | Publisher's foreword |
  | 16–17 | Contents |
  | 18 onward | Memoir |
  | from printed p. xxxiii | Introduction |
  | — | Doctrinal Divinity, printed pp. 1–696 |
  | — | Practical Divinity, printed pp. 697–994 |
  | — | Dissertation, printed pp. 995–1024 |
  | 1078 onward | Index |
  | 1085–1086 | Back matter |

- **Pagination:** printed page numbers are continuous across the whole work, and the book is a single volume. In the body, **PDF page = printed page + 53**, checked at printed pp. 345, 876, 896, 915 and 995.

### Reconciliation against the 156-chapter tally

Predicted: **156**. Counted from the BSB contents (PDF pp. 16–17):

| Part | Chapters per book | Total |
|---|---|---|
| Doctrinal I–VII | 31 / 16 / 13 / 7 / 14 / 15 / 11 | 107 |
| Practical I–IV | 24 / 6 / 8 / 6 | 44 |
| Dissertation | 5 | 5 |
| **All** | | **156** ✓ |

The per-book counts match the phase-0 CCEL tally exactly.

**Body headings spot-checked** against the contents, for the phase-1 chapters and their neighbours:

| Chapter(s) | Printed pages | PDF pages | Result |
|---|---|---|---|
| Doctrinal IV.1–6 | from 345 | 398–421 | BOOK IV and CHAP. I–VI headings present, in order |
| Practical III.1–2 | 896, 915 | 949, 968 | BOOK III, *Of Baptism*, CHAP. II *Of the Lord's Supper* |
| Dissertation 1–5 | 995–1024 | 1048–1077 | CHAP. I–V headings present |

### Does BSB follow Gill's own division? Yes.

BSB numbers the books Doctrinal I–VII and Practical I–IV in both the contents and the body headings (e.g. "BOOK IV" before Doctrinal IV.1; "BOOK III" before Practical III.1). Chapters are labelled "CHAP." in the body. The citation scheme (`Doctrinal VI.4`, `Practical III.1 §3`, `Dissertation 5`) maps one-to-one onto it.

### Deviations and findings

1. **BSB is not the same setting as the IA 1839 scan (B).**
   - BSB's printed pages are the pagination of the 1839 edition it reproduces. The BSB foreword cites Practical III.1 at "pp. 896–915" and Doctrinal VII.8 at "pp. 643–667", and both match the BSB contents.
   - Both descend from London 1839, but:
     - BSB is one volume with continuous pagination, Gill's book numbers, and CHAP. labels.
     - The IA copy is two volumes, renumbers books per volume (v.2 Book V = Practical III), restarts its pagination (Practical I.8 at v.2 p. 420; BSB p. 753), and showed no CHAP. labels in phase 0.

   **Consequence:** IA and BSB page locators are not interchangeable. The tiebreaker role (wording) is unaffected.
2. **Contents titles differ from body titles in places.** This is variation within the edition, not a change of division:
   - Doctrinal IV.2: the contents read "Of the Covenant of Grace in the Patriarchal State"; the body reads "Of the Exhibitions of the Covenant of Grace in the Patriarchal State". IV.3 is similar.
   - Practical I.8: the BSB contents read "Of the Grace of Hope". The IA v.2 contents read "Of Hope", and its body reads "Of the Grace of Hope".

   **Rule:** chapter titles in TTL follow the **body heading** of the working text.
3. **CCEL's Practical I.8 title "Of the Grace of God" is confirmed wrong** against both BSB and IA. The correct title is "Of the Grace of Hope", which replaces the phase-0 "Of Hope".
4. **OCR limits.** Some contents numbers are illegible in OCR (Practical II.2–4; Doctrinal I.8 shows as ";"). The entries are present and in sequence, so the count is unaffected. Wording that matters is read from the page image, never from OCR.

## Roles of the sources (ratified 2026-10-25)

| Source | Role |
|---|---|
| **BSB 2019** (above) | **Working text.** The page image is the check for every quotation. Its printed pages are a stable optional secondary locator, `gc:pages` (ADR-0002, Ratification). Pages never go in an IRI. |
| **CCEL** (A) | Clean cross-check for locating passages and Gill's sub-heads ("First… Sixthly"). CCEL's *files* never enter the repo (CCEL terms). A quotation is Gill's words checked against the BSB page image, not copied from CCEL. |
| **IA 1839 scan** (B) | **Tiebreaker on disputed wording** only. Its pagination is different from BSB's (finding 1). |
| **Citation key** | Gill's own division, unchanged: `B source/gill-body/{doctrinal\|practical}/{book}/{chapter}`, `B source/gill-body/dissertation/{n}`. |
| **Quotation scope (filled 2026-10-25)** | **Display and quotation permitted.** Gill's text is PD. Every quotation is verified against the BSB page image, and the page is recorded. Front matter is excluded. No sentence cap was set (open question). Argument text is a verbatim quotation or absent, never a paraphrase (ADR-0005). |

## What enters the repo from this source

- Chapter and section references, as IRIs (ADR-0002), with an optional `BSB p.` locator literal.
- Passage references Gill cites, as OSIS ranges.
- Verbatim quotations of Gill, each checked against the BSB page image, with the printed page recorded.
- Nothing from the BSB front matter (foreword, imprint, catalogue).
- **No** PDF, page image, OCR output or wholesale text from any edition.

## Phase-0 recommendation (superseded 2026-10-25; history)


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
