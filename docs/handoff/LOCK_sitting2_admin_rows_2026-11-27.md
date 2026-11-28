# Lock: Gill II.3 pp. 867 and 874-876 on sitting 2's administrator row (2026-11-27)

- **Locked:** 2026-11-27, before the content file is edited or the console is rebuilt. Git history seals it. This file is never edited; misses are recorded in the report.
- **On:** [RULING_report_32.md](RULING_report_32.md): "Gill II.3 p. 867 (the essence of ordination) and pp. 874-876: show them on sitting 2's administrator rows if not already there."
- **Checked first:** [docs/loci/plumb-line-followup-2.json](../loci/plumb-line-followup-2.json), row `gill-view`.
  - It already has one p. 867 sentence: "The election and call of them, with their acceptance, is ordination."
  - It does not have the p. 867 sentence on the essence of ordination, and has nothing from pp. 874-876.
- **The change:** context lines only, on row `gill-view`. No row, field, option or image is added, and no label is changed.
  - Each quotation is copied from [RESEARCH_church_2026-11-26.md](RESEARCH_church_2026-11-26.md), where it was read on the page image (BSB, printed ≤ 895). None is from pp. 897-912, and no crop is viewed.
  - One plain-words line goes with them: pp. 874-876 are about the Supper, not baptism, and Gill sets the two apart.
- **The placement is the build agent's choice:** all on `gill-view`, the row that already holds Gill's words on who may administer and who makes the administrator.

## Predictions

| # | Prediction |
|---|---|
| A1 | The sitting 2 form tests pass **unamended**: 3 sections, rows [10, 9, 7], 26 rows, 29 fields, 6 images. |
| A2 | The full suite passes with no test changed, so nothing goes to a hold/ branch. |
| A3 | The rebuilt console has a new build hash, different from `18a4a13dfeffb6e9`. The old page is superseded and is not signed. |
| A4 | `gill-view` gains exactly 5 context lines (p. 867; p. 874; p. 875; p. 876; the plain-words note). |
