# Source report: Augsburg Confession (1530)

Phase 1, before ingest (rule 4). Research done 2026-10-25. Working copies
were held in the session scratchpad only; nothing is in this repo.

Tags: **[V]** fetched and inspected; **[R]** reported by a secondary source
only; **[U]** unverified.

## What enters the repo (phase 1)

**No confession text.** Holdings cite division IRIs only, as for WCF and
LBC. Augsburg needs one extra rule, because it has two authoritative texts
that differ on a phase-1 point (below).

## The work

- Presented on 25 June 1530 at the Diet of Augsburg. The German was read aloud and the Latin handed over. Both autographs are lost. [V: Bente, Triglot introduction]
- **28 articles**: I–XXI are articles of faith and XXII–XXVIII concern abuses corrected, with a preface and a conclusion. [V]
- Critical editions number sentences within each article. **Latin and German are counted independently.** [V]
- **Two authoritative texts, German and Latin.** [V: Jacobs 1911]
  - Triglot prints the 1580 Dresden German and the 1584 Leipzig Latin.
  - Schaff and Jacobs 1911 follow the 1531 Latin *editio princeps*.
  - The 1540 *Variata* is a different text and is not in scope.

### The phase-1 variant: Article IX (Of Baptism)

Described, not quoted. [V: Triglot Latin and German; Schaff; Jacobs 1911]

- **Necessity.** The Latin says baptism is necessary *to salvation* (*ad salutem*); the German says only that it is necessary.
- **Condemnation of the Anabaptists.**
  - The Latin condemns two claims: that infant baptism is not right, *and* that children are saved without baptism.
  - The German condemns only the first.
- **Children.** The Latin speaks of children "received into God's grace"; the German speaks of children becoming "well-pleasing to God".

**Consequence for Holdings.** A Holding that rests on a clause found only in
the Latin (e.g. necessity *to salvation*) cites `B source/augsburg/9` and
carries `gc:locator "Latin IX.3 (Triglot)"` with `gc:textLayer "la"`. It
also records that the German lacks the clause. Whether one Body takes a
reading present in only one authoritative text is an editorial question
(open question 1). Until it is ruled, such a Holding stays `proposed` and is
flagged.

## Candidate sources

| # | Source | Edition / base | Licence / terms | Quality |
|---|---|---|---|---|
| A | bookofconcord.org (`/augsburg-confession/`) | **Triglot Concordia (CPH, 1921), English translated from the Latin.** [V: Bente preface] | Site: "These texts are in the public domain and may be freely copied." [V] Footer: "Original Content Copyright 1998–2024 BookOfConcord.Org". Terms of Service page did not load. [U] | Clean, anchored by section. English of the Latin only. |
| B | IA `triglottaconcord0000unse` (Triglot 1921, 1574 images) | German, Latin and English | 1921 US publication: PD | Latin and English OCR good; German Fraktur OCR poor, page images fine. [V] |
| C | CCEL Schaff vol. 3, *Confessio Augustana*; images IA `creedsofchristen028262mbp` | 1531 Latin *editio princeps*, with German additions in brackets and Variata in notes. English by C. P. Krauth (1868/1874). [V] | `DC.Rights` "Public Domain"; CCEL republication policy. [V] | Best single source for Latin/German/Variata comparison. |
| D | Jacobs 1911 *People's Edition*, IA `thebookofconcord00unknuoft` | English from the 1530–31 Latin *editio princeps*, German insertions bracketed [V] | PD | Good OCR. |
| E | Jacobs 1882, IA `jacobs_concord` | English that Jacobs (1911) says is a reprint of a 1586 translation; Schaff attributes it to Krauth. **Provenance conflict.** [V] | PD | Not inspected. |
| F | Henkel 1851/1854; Ludwig/Schott 1848 | English from the **German** [R] | PD by age | **Not located.** These are the only known PD English renderings of the German. |
| G | Tappert 1959; Kolb–Wengert 2000; McCain 2005 | Modern | Copyrighted | **Do not use.** |

## Recommendation

| Role | Source |
|---|---|
| Reading text, English | Triglot 1921 English (A or B). The IA scan (B) is the source of record, because the site's terms are unread. |
| Original languages | The Triglot Latin and German columns, read from the page images (B). Schaff (C) for the *editio princeps* readings. |
| Cross-check | Jacobs 1911 (D). |
| Never | Any post-1930 translation (G). |

Augsburg is not taken as one English text. Any Holding that depends on a
point where the Latin and German differ records which layer it rests on.

## Citation scheme

`B source/augsburg/{article}`, with arabic article numbers, e.g.
`B source/augsburg/9`.

- **Sentence sections are locators, not IRI segments.** The Latin and German count them differently, and ADR-0002 keeps edition-specific numbering out of IRIs.
- The preface is `B source/augsburg/preface`; the conclusion is `B source/augsburg/conclusion`.
- This departs from the `{chapter}/{paragraph}` confession pattern in ADR-0002: Augsburg has articles with language-dependent sections, not paragraphs. It is recorded for ratification (open question 2).

## Phase-1 divisions

| Article | Topic | Phase-1 locus |
|---|---|---|
| II | Original sin | context for baptism-subjects; Latin and German wording differ, not yet read |
| V | Ministry; word and sacraments as means; Anabaptists condemned | baptism-significance (means of grace) |
| IX | Baptism: necessity; grace offered; infants to be baptized; Anabaptists condemned | baptism-subjects, baptism-significance, baptism-perpetuity |
| XIII | Use of the sacraments: signs of God's will, to awaken and confirm faith | baptism-significance |

Augsburg is **silent** on baptism mode and on covenant administrations (not
read as a positive statement). Under ADR-0003 silence scores as unknown.
No Holding is drafted for those loci.

## Open questions

1. **Augsburg's layered text.** When the Latin and German differ, does `B body/augsburg` hold the Latin reading, the German reading, or only what both share? I propose the common core as the Holding, with Latin-only clauses as separate `proposed` Holdings that carry `gc:textLayer`. The ruling is the architect's.
2. Ratify `B source/augsburg/{article}`, with sections as locators.
3. Read the bookofconcord.org Terms of Service manually before using the site; until then use the IA scan.
4. A PD English of the German (Henkel/Schott) has not been located. It is not needed while no text is stored.
