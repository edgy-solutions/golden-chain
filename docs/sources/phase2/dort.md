# Source report: Canons of Dort (1618-19)

Phase 2 review only. Research 2026-11-15. Nothing stored in the repo; no text, no paraphrase. Tags: **[V]** verified on a page fetched; **[R]** reported by a secondary source; **[U]** unknown / not found. Locators below are candidates from memory of the Heads' structure, **all [U] until read against page images**; none were checked.

## The work
- Synod of Dordrecht, Nov 1618 to May 1619; Canons adopted 1619. Latin original. [R]
- Structure as printed in Schaff's Latin: **four Heads** (III and IV combined under one heading, one run of articles, one Rejection set); First 18 arts., Second 9, Third/Fourth 17, Fifth 15; each Head has "Rejectio Errorum" numbered in roman (I: 9, II: 7, III/IV: 9, V: 9). [V, CCEL structure page creeds3.iv.xvi]
- Locator scheme: `Head.Article` (III/IV cited as "III/IV", articles 1-17 continuous), and `Head.Rejection.N` for errors.

## Editions
| # | Edition | Status |
|---|---|---|
| A | Schaff, *Creeds of Christendom* vol. 3 (New York: Harper, 1877; 1878 printing). Schaff d. 1893. Latin complete (c. pp. 551-574, approximate). **English is an abridgment** taken from the Reformed (Dutch) Church in America's *Constitution*: **positive articles only; Preface, Rejections and Sentence omitted.** [V, CCEL note] | PD US and UK. Witness for article numbering and the Latin Rejections. English page range [U] |
| B | *The iudgement of the synode holden at Dort, concerning the fiue Articles ... as also their sentence touching Conradus Vorstius*, London: John Bill, 1619. STC 7066 (variant 7066a). In EEBO. [R, catalogues] | PD by age. Translator unnamed [U]. Candidate witness for English text with Rejections. EEBO-TCP record not found (a catalogue number "A888680" was seen once and not trusted) [U] |
| C | CRC Publications 2011 translation (and other modern versions) | **Not PD. Do not use.** |

## Scans
- Schaff vol. 3, archive.org: `creedsofchristen187803scha` (1878; the repo's existing Belgic witness; leaf = page + 15 was checked only near pp. 331-427, **recheck at pp. 551+**), `creedschristendo03scha` (1877), `creedsofchristen0003phil` (1905), `TheCreedsOfChristendomV3` (1919). [R, metadata]
- 1619 English: no open scan found. archive.org holds only a 1974 reprint, `judgementofsynod0000syno` (reprint, not PD as an edition). EEBO images are licensed. [R]
- CCEL `ccel.org/ccel/schaff/creeds3/creeds3.iv.xvi.html` used for structure only; no CCEL text copied.

## Proposed witness
Schaff 1877/78 for numbering and the Latin; for English Rejections, the 1619 Bill printing (STC 7066) read from the architect's own library access. Never cite the abridged English for a Rejection.

## Candidate locators [U until checked on the image]
| Topic | Candidates | Note |
|---|---|---|
| Call of the gospel | II.5, II.6; III/IV.8, III/IV.9 | Suggested in the brief; headings not seen |
| Faith as gift | I.6; II.7; III/IV.10, III/IV.14 | III/IV.14 is where gift/instrument wording is expected |
| Faith as instrument | III/IV.14; Rejections of II | Search the Latin for the instrument wording; do not assume |
| Perseverance | Head V, arts. 1-15 (whole Head); V.3, V.7-8 as nearer candidates; V Rejections | |
| Justification | II.7?; III/IV; V | Little explicit justification expected; search Latin for "iustific-" |

## Open questions
1. Printed page ranges of each Head in the Schaff English, and leaf offset at pp. 551+.
2. Is Schaff's English a faithful abridgment of 1619, or re-edited? (He cites the RCA Constitution.)
3. Open scan or TCP text of STC 7066; the translator.
4. Every locator above needs a text-only read of the page by the architect.
5. Confirm Schaff does not renumber III/IV articles.

## Ruling on report 19 (A-5), worked 2026-11-17: Thomas Scott's 1831 English as a PD witness

The ruling: "look for Thomas Scott's translation (1831) as a PD witness; verify before relying." **Found and verified on page images.**

- **Edition:**
  - Title: *The Articles of the Synod of Dort, and its Rejection of Errors: with the History of Events which made way for that Synod, as published by the authority of the States-General; and the Documents confirming its Decisions*.
  - "Translated from the Latin, with notes, remarks, and references, by Thomas Scott, Rector of Aston Sandford, Bucks."
  - Utica: William Williams, Genesee Street, 1831, with New York and other sellers. [V title page, n6]
  - archive.org `articlesofsynodo00syno`, Princeton Theological Seminary scan, 334 images, marked NOT_IN_COPYRIGHT. [V]
  - Other scans: HathiTrust 008893087. The London 1818 edition is `india.history.resource.18439`. [R, not opened]
- **Public domain:**
  - US: printed 1831.
  - UK: Scott died 1821 [R, catalogue authority dates].
  - The American additions (below) were published 1831 and their authors are not named, so they are past any UK term for anonymous works (70 years from publication).
- **The text Scott translated:** he says his is a literal translation of the articles "as contained in the *Sylloge Confessionum*, Oxford, 1804". This is from his introduction, p. 87, viewed. Collation against Schaff's Latin: [U].
- **Structure** [V on images]:
  - Scott calls the Heads "Chapters": I (p. 87), II (p. 99), III & IV together (p. 105), V (p. 116).
  - Articles are numbered in arabic, 1, 2, 3, ...
  - Each chapter has its **Rejection of Errors**, also numbered in arabic. The first begins p. 94 [V]. The others are at about p. 101 (II), p. 111 (III/IV) and p. 121 (V) [R: IA OCR running heads, used for locating only; not checked on the image].
  - Scott's own notes are footnotes, keyed by symbols. They are his, not the Synod's, and a locator never points into them.
- **Leaf map:** the scan's page_numbers.json gives leaf = page + 18 (1-based). BookReader n = page + 17, checked at n104 = p. 87, n111 = p. 94, n116 = p. 99, n122 = p. 105, n133 = p. 116 and n317 = p. 300. [V]
- **Caution: not all of the volume is Scott's.** It also prints a "Harmony of Confessions" (e.g. p. 300 has the Welsh Calvinistic Methodists' Confession, which dates from 1823, after Scott's death). Only the Canons and their Rejections are the witness.
- **Witness proposed:**
  - Scott 1831 for the English of the articles and the Rejections.
  - Schaff's Latin stays the witness for numbering.
  - The 1619 STC 7066 is no longer needed for the Rejections.
- **Locator scheme unchanged:** `Head.Article` and `Head.Rejection.N`. Scott's chapter numbers are the Heads, and III & IV is one run.
- The candidate locators above stay [U] until the architect reads the text. Scott's English page for each is now findable.
