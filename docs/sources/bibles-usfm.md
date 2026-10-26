# Source report: goat-yard's USFM Bibles (KJV, Hebrew, Greek)

Recorded 2026-10-26 (rule 4, reported first). Read-only, private, by
configured path. **No Bible text is stored in this repo or fetched by it.** The
only Bible data in the repo is the versification table from CrossWire SWORD
`canon.h` (ADR-0002, rule 5).

Tags: **[V]** fetched and inspected; **[R]** reported by a secondary source
only; **[U]** unverified.

## Where they are

- In goat-yard's private corpus, under its `bibles` directory. This repo names
  no path. A tool or test reads them only through the environment variable
  `GOLDEN_CHAIN_BIBLES`, which points at that directory.
- When the variable is unset, the data test skips. Nothing is copied into the
  repo, and none of the corpus is committed.

## The three texts

Each directory holds one USFM file per book and an eBible.org `copr.htm`. [V]

| Directory | Text | Books | Licence (from `copr.htm`) | Source files dated |
|---|---|---|---|---|
| `eng-kjv2006_usfm` | King James (Authorized) Version, "the standardized text of 1769, protocanon only, with Strong's numbers added" | 66 | Public Domain. The UK Crown letters patent restrict printing in the UK only. | 14 May 2025 |
| `hbo_usfm` | "The Old Testament in ancient Hebrew, following the Masoretic Text" | 39 | Public Domain | 31 Aug 2023 |
| `grctr_usfm` | "The Greek Textus Receptus New Testament with manuscript annotations by Adam Boyd" | 27 | Public Domain (the annotations dedicated to the PD by Adam Boyd) | 24 Sep 2025 |

The publisher is eBible.org (HTML generated with Haiola). [V]

## The check: USFM KJV against `canon.h`

- **Test:** `tests/test_versification_usfm.py`, using `goldenchain/usfm.py`.
- **Method:** it reads the `\id`, `\c` and `\v` markers of each KJV book, then
  compares the books, the chapters per book and the verses per chapter with
  `goldenchain/versification.py`. It fails loud on an unknown book code, a
  duplicate book, or an out-of-order chapter or verse. Verse bridges are
  listed, and the test expects none.
- **Prediction** (locked 2026-10-26 01:50:49Z): 66 books, 1,189 chapters,
  31,102 verses, 0 differences.
- **Result:** all held. 66 / 1,189 / 31,102, 0 differences, 0 bridges.
- **A difference would be a finding against both witnesses.** Neither
  silently corrects the other.

## Use

- **ADR-0004, when written,** names this USFM KJV as the **display text
  source**. There is no other source and no API, and the text is never copied
  into this repo.
- **The Hebrew and Greek** are recorded here only. Nothing reads them yet.
- **The Strong's numbers** in the KJV files are markup. The count check
  ignores them.
