# Lock: item 7, a weigh page and Body pages in the local prototype (2026-11-27)

- **Locked:** 2026-11-27. Committed before the generator is changed and before ADR-0008 Revision 1 is drafted in full. Git history seals it. This file is never edited; misses are recorded in the report.
- **On:** the two-day order, Day 2, item 7 ([RULING_report_31.md](RULING_report_31.md)): "Prototype, local only. Extend the examine/try prototype with a weigh page and a Body page, generated from weigh's output and the data: the three groups (could join; could join with stated differences; could not join), walls shown apart from differences, the "not a church by this site's standard" listing with its derivation and the unsigned-statement line, each claim with its source. No sentence that is not a label, a locator or a signed record. Draft this as ADR-0008 Revision 1, proposed; the prototype may be built ahead of ratification because it is local, read-only and mints nothing."
- **The counts below come from weigh's own output** (`python -m goldenchain.weigh`, scope members) at `9d6dae3`, read before any code is written. They are not typed from memory.

## What is built (the proposal under test)

1. **The generator** `tools/prototype/examine_try.py` gains two page kinds. It writes them next to the existing ones under `~/.golden-chain/prototype/<head12>/`.
   - `weigh.html`: weigh against the plumb-line, scope members.
   - `body/<slug>.html`: one page per Body that weigh weighs or lists.
2. **The source of each number is weigh itself.** The generator calls `goldenchain.weigh` (`weigh()`, `score()`) and `goldenchain.unchurches` on the same rdflib dataset weigh's CLI loads. It does not re-score. Where a page needs a cell's Holding and source, it reads them with weigh's own cell rule, without changing `goldenchain/`.
3. **The groups (the build agent's proposed reading; ADR-0008 Revision 1 puts it to the architect):**

   | Group | A ranked Body is in it when |
   |---|---|
   | could join | no wall, at least one covered locus, and every covered locus's cell is 0 |
   | could join with stated differences | no wall, and at least one covered, non-wall locus has a cell above 0 |
   | could not join | at least one wall |
   | no locus covered (listed apart) | no wall and no covered locus: weigh has nothing to weigh it on |

   - A **wall** is weigh's wall. A **difference** is a covered, non-wall locus whose cell is above 0, and a difference of 0.25 or more is marked as weigh's "break". They are shown in separate lists.
   - The Bodies weigh excludes are not in any group. They are in the listing "Not a church by this site's standard", with its derivation.
4. **Only labels, locators, numbers and ruled wordings.** The fixed words are the banner, the section headings, the group names above, and the ruled wordings imported from `goldenchain.unchurches` and `goldenchain.weigh` (`UNSIGNED`, `HEADING`, `WORDING`, `MEMBERS`, `CONSEQUENCE`). They are imported, not retyped. Nothing else is written.
5. **Every claim carries its source:**
   - each wall and each difference: the Position, the Body's modality against the plumb-line's, and the `dcterms:source` IRIs of the Body's Holding there;
   - each listing row: the Holding's sources and the plumb-line sitting that flags the Position (as weigh prints them).

## Predictions

| # | Prediction |
|---|---|
| WX1 | `weigh.html` puts the 4 ranked Bodies in these groups: **could join**: `body/gill`, `body/lbc-1689`; **could join with stated differences**: `body/small-catechism-1529`, with 1 difference (`locus/baptism-efficacy`, 0.75, marked as a break); **could not join**: none; **no locus covered**: `body/book-of-concord`. |
| WX2 | The listing "Not a church by this site's standard" holds **3** Bodies (`body/apology-1531`, `body/augsburg`, `body/wcf`) and **4** rows, each with its sources and the flagging sitting `source/plumb-line/sitting-eb961ddb1e582ed6`. The unsigned-statement line appears on `weigh.html` and on each of these 3 Body pages. |
| WX3 | There are **7** Body pages, one for each Body weigh weighs or lists, and none for the plumb-line. Each shows its group or the listing, its walls and its differences in separate lists, and every effective Holding with its source IRIs. |
| WX4 | Every existing `examine/` and `try/` page is byte-identical to the build at `9d6dae3` once the commit id in the banner and the footer is replaced by a placeholder on both sides. The page set is the same. `index.html` differs only by the added link to `weigh.html`. |
| WX5 | The banner is on every page. The sentinel test passes on the new pages: no `rdfs:comment`, `gc:resolutionNote`, `gc:quotation` or `gc:derivedBy` string appears. |
| WX6 | Two runs at the same commit are byte-identical, the new pages included. |
| WX7 | weigh's CLI output is byte-identical before and after the change. No file under `data/` or `goldenchain/` changes. The full suite passes with the new tests, and no existing test is changed. |
