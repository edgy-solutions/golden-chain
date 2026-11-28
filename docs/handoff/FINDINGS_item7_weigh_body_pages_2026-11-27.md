# Findings: item 7, a weigh page and Body pages in the local prototype (2026-11-27)

- **From:** the build agent, 2026-11-27.
- **Lock:** [LOCK_item7_weigh_body_pages_2026-11-27.md](LOCK_item7_weigh_body_pages_2026-11-27.md) (`7a33551`), committed before the generator was changed.
- **Built at:** `e9fb45a`.
  - It changes `tools/prototype/examine_try.py` and adds `tests/test_prototype_weigh_body.py`, with 20 tests.
  - [ADR-0008 Revision 1](../adr/0008-examine-try-prototype.md) is proposed in the same commit.
  - The code was written by the implementer subagent from the build agent's spec. The build agent reviewed it, checked that it writes no text of its own, and ran every check below.
- **Where it ran:**
  - Two builds were made from a clean worktree at `e9fb45a`, with `--store rdflib`.
  - The outputs are `~/.golden-chain/item7-build-a` and `item7-build-b` (local, not committed).
  - The baseline is the build at `9d6dae3`, in `~/.golden-chain/item7-baseline-9d6dae3`.
- **Local, read-only.** Nothing was minted. No file under `data/` or `goldenchain/` changed.

## The lock, scored (never edited)

| # | Prediction | Result | |
|---|---|---|---|
| WX1 | could join: gill, lbc-1689; with stated differences: small-catechism-1529 (1 difference, baptism-efficacy 0.75, break); could not join: none; no locus covered: book-of-concord | As predicted. Small Catechism shows `locus/baptism-efficacy` (tier second), cell 0.75, marked as a break, on `position/baptism-efficacy/necessary-means-of-grace`: "taught" against the plumb-line's "forbidden", with its sources. | **Hit** |
| WX2 | listing of 3 Bodies (apology-1531, augsburg, wcf), 4 rows, each with sources and the flagging sitting `sitting-eb961ddb1e582ed6`; the unsigned line on weigh.html and on the 3 Body pages | 3 Bodies and 4 rows, and the sitting appears in all 4 rows. The unsigned line appears on `weigh.html` (above the groups and above the listing) and once on each of the 3 Body pages. | **Hit** |
| WX3 | 7 Body pages, none for the plumb-line; group or listing, walls and differences apart, every effective Holding with sources | **7 pages**: apology-1531, augsburg, book-of-concord, gill, lbc-1689, small-catechism-1529 and wcf. Walls and Differences are separate sections. The Holdings rows are checked against the data by the new tests. | **Hit** |
| WX4 | existing pages byte-identical to the `9d6dae3` build once the commit id is replaced; same page set; index differs only by the weigh link | All **172** existing pages match once the commit id is replaced. No page is gone, and 8 are new. `index.html` differs by one line, `<p><a href="weigh.html">Weigh</a></p>`. | **Hit** |
| WX5 | banner on every page; sentinel test passes on the new pages | Both checked by the new tests on a synthetic dataset, with sentinels in `rdfs:comment`, `gc:resolutionNote` and `gc:derivedBy`. | **Hit** |
| WX6 | two runs byte-identical | 182 files, identical | **Hit** |
| WX7 | weigh's CLI output byte-identical; no `data/` or `goldenchain/` change; suite passes; no existing test changed | The CLI output at `e9fb45a` is byte-identical to `9d6dae3`'s. Between the lock and the build, `tests/`, `data/` and `goldenchain/` differ only by the new test file. Suite at `e9fb45a`, run by the build agent from the clean worktree: **993 passed, 1 skipped**. | **Hit** |

## What differs from the spec (not from the lock)

1. **The new pages are opt-in in `build()`.** The parameter is `weigh_pages=False` by default. The CLI (`main()`) passes `True`, so the built prototype is as locked.
   - The reason: two existing tests call `build()` with its defaults and assert the page count, and the order forbids changing an existing test.
   - Turning the default on would need those two tests amended, on a hold/ branch.
2. **Wording the spec left open.** These are the implementer's choices, and every word is still a label, a number or a fixed heading:
   - a list line reads `[Class] walls N; differences N; cost X over N loci; coverage Y`;
   - an empty source list prints "no source", as weigh's own output does;
   - a difference's Positions are a nested list under its locus.

## For the architect

The open points are in ADR-0008 Revision 1:
1. the groups' reading;
2. the fourth line, "no locus covered";
3. whether the ruled wordings count as signed records;
4. officers scope;
5. comparison views.

One more: should `build()` make the new pages by default? That would amend two existing tests, on a hold/ branch.
