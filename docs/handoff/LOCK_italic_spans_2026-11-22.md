# Lock: italic spans on the baptism chapter, paired with Scripture references (overnight order 2026-11-22, item 7)

- **From:** the build agent, 2026-11-22. Committed before the tool and the run.
- **Order:** "run v4 over the baptism chapter (pp. 896-915); group adjacent italic words into spans; pair each span with the following Scripture reference in the OCR; report found, paired and unpaired, by page; compare with the hand-minted references, as counts; mint nothing; no model views a crop."
- **Base:** `phase-0` `c4f18a2` (the statements console). Suite 833 passed.

## Inputs (local only, never committed)

- **OCR:** `~/.golden-chain/ocr-baptism-run1-2026-11-13/ocr.json`, sha256 `00cb18e04b2dfc9e…`. This is the OCR that every slant run measured.
- **v4 slant:** `~/.golden-chain/slant-v4-2026-11-17-a/slant.json`, sha256 `f25ea51e30c8e741…`. It covers 20 pages and 12 474 rows: 700 slanted, 11 690 upright, 84 abstained.
  - Measure v4 is the one Chris signed a truth set for: build-a `8e173740`, ruling on report 21, A-11.
  - Its slant.json is byte-identical on rerun (its own lock). So this lock uses the existing run and re-checks the sha256 rather than rerunning it.
  - A rerun would need a clean checkout. The main checkout is in use overnight.

## The tool: `tools/italic_spans.py <ocr-run-dir> <slant-run-dir> <out-dir>`

- **Join.** Slant rows are joined to OCR words by `key`, in the column regions only (left, right). Reading order is (page, region left before right, block, par, line, word).
- **Span.** A maximal run of words in reading order, within one page and one region, built as follows:
  - Every measured word in the run is slanted.
  - Unmeasured words (no slant row, too small to measure) between slanted words are included as bridges.
  - An upright or an abstained word ends the span.
  - Leading and trailing unmeasured words are trimmed.
  - A span holds at least one slanted word.
  - Spans do not cross a region or a page. The number of spans touching a region's first or last word is reported.
- **Reference.** Detected on OCR word text, by regex only:
  - a book token from a fixed list of the abbreviations Gill uses (in the tool, tested), with an optional preceding "1"/"2"/"i"/"ii" token;
  - then a lowercase roman chapter token (`^[ivxlc]+[.,;]?$`);
  - then a token beginning with a digit.
  - A **continuation** (roman chapter and digit, with no book) counts as a reference only when it starts within 6 words after the end of a previous reference.
  - "ver." forms are counted separately and are not references.
- **Pairing.** A span is paired with the first reference that:
  - starts after the span's last word, in the same page and region;
  - has at most 8 words between them;
  - comes before the next span starts.
  Each reference pairs with at most one span.
- **Outputs:** `~/.golden-chain/italic-spans-<date>-a/`, never committed.
  - `spans.json` holds keys, counts and the run header. It holds no word text.
  - `summary.json` holds the counts by page.
- **Hand-minted comparison.** Count the `gc:cites` of the 21 Arguments `argument/gill-body/practical/3/1/001`-`021`, by the first page of `gc:pages`. There are 56 by the data today:
  - 897: 5; 898: 20; 899: 4; 900: 7; 910: 5; 911: 6; 914: 9.
  The comparison is counts only. No reference is minted or matched to a Passage.

## Predictions

| # | Prediction |
|---|---|
| I1 | The tool's tests are born with it (span grouping, bridges, trimming, upright and abstain ends, the region boundary, the reference regex, continuation, the pairing window, one span per reference). Existing tests pass unamended. |
| I2 | The total number of spans over pp. 896-915 is between 150 and 400. |
| I3 | At least half the spans are paired. |
| I4 | On each of the 7 pages with hand-minted references, the references detected are at least the hand-minted cites on that page. |
| I5 | Two runs give byte-identical `spans.json` and `summary.json` (no time in either; the time is in `run_header.json`). |
| I6 | No `data/*.ttl` change; nothing is minted; no image is opened by any model. |

## What the report gives

For each page: words measured, slanted, spans, paired, unpaired, references detected, hand-minted cites. Then the totals. No word text appears, and no span is identified by its words.
