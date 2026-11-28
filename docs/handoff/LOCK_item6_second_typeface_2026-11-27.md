# Lock: item 6, the second typeface: v4 slant on about 20 pages of the 1766 Exposition (2026-11-27)

- **Locked:** 2026-11-27. Committed before any request is made to goatyardarchive.org and before any tool for this item is written. Git history seals it. This file is never edited; misses are recorded in the report.
- **On:** the two-day order, Day 2, item 6 ([RULING_report_31.md](RULING_report_31.md)): "The second typeface. If goatyardarchive.org's public scans can be fetched, take about 20 pages of the 1766 Exposition, cite each by FILE page with "printed = file − 88", and run the v4 slant measure on them. Report whether it is bimodal and where the threshold falls. Build nothing for signing."
- The standing addition ([../sources/goat-yard.md](../sources/goat-yard.md), Additions 1): "Any 1766 page cited anywhere in this project carries goat-yard's FILE page number and the line "printed = file − 88". No other numbering for those pages, ever."

## Fetching

1. **Check first.** `robots.txt` is read first, then the `/scans` listing.
   - If either is refused (an HTTP error, a login, a bot check or a robots rule against `/scans`), the refusal is recorded and **the item stops**. No other route is tried.
2. **How it is fetched.** Plain HTTP GETs, with a generic client name and no personal detail, one at a time, with a pause of at least 2 s between files.
3. **Which pages (fixed here, before the listing is seen).**
   - From the listing of volume 1, the body files are those with printed ≥ 1, so FILE ≥ 89.
   - Twenty FILE pages are taken, evenly spaced from the first body file to the last: FILE = first + round(i x (last − first) / 19), for i = 0 to 19.
   - If a chosen file is missing, the next existing file above it is taken.
4. **Where they go.**
   - The scans are kept locally, outside the repo (`~/.golden-chain/item6-scans/`), with their sha256s.
   - No scan, crop or OCR text is committed.
   - The build agent does not view them. Nothing is drawn.

## Method

1. **OCR:** a new tool, `tools/gy_ocr_scans.py`. It is the baptism OCR pipeline (`tools/gy_ocr_baptism.py`: goat-yard's split at substrate-v1, the same regions, engines, PSM and matching), imported, not copied, with these differences:
   - the input is a directory of scan files, not the BSB PDF;
   - each page is converted to 8-bit grey at its native size;
   - Tesseract's `--dpi` is the DPI the file records. If the file records none, it is 300, and this is reported;
   - pages are keyed by FILE number;
   - there is no CCEL alignment and no candidate draw;
   - a page whose column rule is not located is recorded and skipped.
2. **Slant:** `tools/gy_word_slant_v4.py`, unchanged, on that run.
3. **Runs** are made from a worktree at a pushed commit. They must be `clean_run`. Outputs go to `~/.golden-chain/item6-*`.
4. **Tests:** the new tool is born with tests. No existing test is changed.

## Predictions

| # | Prediction |
|---|---|
| E1 | No fetch is refused: `robots.txt` and the listing allow `/scans`. |
| E2 | goat-yard's column rule is located (status ok) on **at least 18 of the 20** pages. goat-yard's thresholds were tuned on volume 1's double rules. |
| E3 | v4 slant is **bimodal**: the tool makes a slanted call. |
| E4 | The threshold T is **0.06-0.20**. |
| E5 | T **differs from the BSB setting's 0.11 by at least 0.02**: the second typeface has its own threshold. |
| E6 | The slanted share of the measured rows is **3-20 %**. |
| E7 | The OCR gives **at least 300 words a page** on average. |
| E8 | The run is `clean_run`, and the full suite passes with the new tests and no existing test changed. |
