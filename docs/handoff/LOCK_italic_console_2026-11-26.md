# Lock: the italic-spans console, what Gill's italic is (ruling on report 28, item 15)

- **From:** the build agent, 2026-11-26. Committed before the tool, the spec builder and the page.
- **On:** [RULING_report_28.md](RULING_report_28.md) item 15. [LOCK_italic_spans_2026-11-22.md](LOCK_italic_spans_2026-11-22.md) and its two misses (I3, I4) stand; no second definition is locked here.
- **Inputs (local, never committed):** `~/.golden-chain/italic-spans-2026-11-22-a/spans.json` (sha `2afca303…`, 220 spans: 35 paired, 185 unpaired) and the OCR run `~/.golden-chain/ocr-baptism-run1-2026-11-13` (`ocr.json` sha `00cb18e0…`, page images `pages/p<N>.png`).

## What is built

- **`tools/italic_span_crops.py <spans-dir> <ocr-run-dir> <out-dir>`.** It draws the 40 spans and cuts one band per span: the span's line or lines, with two lines either side in the same page and column, at full column width. The span's words are given as boxes, one box per printed line of the span. Outputs are `crops.json`, the PNGs and `run_header.json`, all local only.
- **The draw.** Spans in reading order, by page, column (left, then right) and word key.
  - Paired: round-robin over pages in ascending order, round k taking each page's k-th paired span, until 20 are taken.
  - Unpaired: the same, until 20 are taken.
  - The draw is fixed by the inputs; no random seed.
- **The console, new kind `italic-spans`.** One row per span, in a fixed shuffled order (sha256 of a salt and the span's first key, as the truth-set consoles do). Nothing on a row says whether the span was paired, or how anything measured it.
- **Each row** shows the band with the span boxed. Chris chooses one of:
  1. a Scripture quotation, with its reference after it;
  2. a Scripture quotation, with its reference before it;
  3. a quotation, with no reference near it;
  4. not a quotation: emphasis;
  5. not a quotation: a foreign word;
  6. not a quotation: a title;
  7. not a quotation: other.

  He can also choose "other, as written" with a note (for example, the box is not on italic words). There is an optional note on every row.
- **Ingest.** The signed record goes to `docs/handoff/SIGNED_italic_spans_<b16>.md` by the generic path, with no TTL. The counts are made afterwards by a separate tool, under its own lock, joining the signed answers to `spans.json`.

## Predictions

| # | Prediction |
|---|---|
| C1 | Born tests on synthetic pages and OCR only. The full suite passes with no existing test amended. |
| C2 | 40 rows: 20 paired, 20 unpaired. The paired rows cover all 14 pages that have a paired span (897-900, 902, 903, 905, 907, 909, 910, 912-915). Round 1 adds 897, 898, 899, 900, 905 and 909. The unpaired rows cover all 20 pages, one each. |
| C3 | Every band has two lines above and two below the span's lines, except where the column has fewer: at most 6 of the 40 bands are short. Each band is 5 to 7 lines. |
| C4 | Two runs give byte-identical `crops.json`, PNGs and spec. The time is in `run_header.json` only. |
| C5 | No OCR word text appears in `crops.json`, the spec or the page. A born test plants a sentinel word in the synthetic OCR and finds it in none of them. |
| C6 | No `data/*.ttl` change. The build agent opens no crop and no page, and no model views them. The page's build16 is recorded in the report. |

A miss is recorded, not edited.
