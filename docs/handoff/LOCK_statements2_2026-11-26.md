# Lock: statements console, second content file (ruling on report 28, item 10, Q-I-4)

- **From:** the build agent, 2026-11-26. Committed before the content file and its test.
- **On:** [RULING_report_28.md](RULING_report_28.md) item 10, Q-I-4: "the architect's view differs from your proposal ... Chris decides on the row; if he includes it, label it 'short extracts only; written confirmation to be sought before launch'". [LOCK_statements_console_2026-11-22.md](LOCK_statements_console_2026-11-22.md) T1-T7 stand. `docs/consoles/statements-1.json` is not edited.
- **Why a new page:** the unsigned page `0894df4edd1fe4b1` proposes "not now" on the BSB foreword, for a reason the architect has ruled contradicts the data. Chris should not sign a page that pre-fills a proposal the architect has overruled. Batch C (LOCK_batchC_unit_2026-11-26) also adds a Source the page does not list: `source/heidelberg-harbaugh`.

## What changes

`docs/consoles/statements-2.json` is `statements-1.json` with exactly these differences:

1. **`source/bsb-gill-1984`:** "proposed" goes from "not now" to "include". "status" gains the label the architect gives for inclusion, verbatim: "If included, it is labelled: short extracts only; written confirmation to be sought before launch (architect, ruling on report 28)." The existing status words stay before it.
2. **One new row, `source/heidelberg-harbaugh`, after `source/belgic-confession`.** Proposed "include". The witness is Harbaugh's Heidelberg Catechism with proof-texts (Reading, Pa.: Daniel Miller, n.d.; LC copyright stamp 7 Jan. 1892), Internet Archive `heidelbergcatech00harb`. The row is not marked "new", because Batch C mints it first.

Nothing else differs. The builder (`tools/console/specs/statements.py`) is unchanged.

## Order

This lands after the Batch C mint. The builder refuses a non-new IRI that is not a SourceWork in the data, so the Harbaugh row cannot be built before Batch C.

## Predictions

| # | Prediction |
|---|---|
| S1 | A born test (`tests/test_statements2_content.py`) checks the content: the two files differ only in item 1 (two keys of one row) and item 2 (one added row), and the label sentence is present verbatim. |
| S2 | The builder accepts `statements-2.json` with the Batch C data and no code change. |
| S3 | The page's build16 differs from `0894df4edd1fe4b1`, which is superseded. The new build16 is recorded in the report. |
| S4 | The full suite passes, and no existing test is amended. There is no `data/` change. |

A miss is recorded, not edited.
