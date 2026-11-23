# Note: since when weigh's output could vary, and which byte-identity claims it touches

- **By:** the build agent, 2026-11-22, on [RULING_report_27.md](RULING_report_27.md) ("report since which commit the output could vary, and which earlier 'weigh byte-identical' claims rested on a Holding with more than one source").
- **Method:** at each claim's commit, weigh was run in both scopes, in four separate processes with `PYTHONHASHSEED` 0 to 3, in a throwaway worktree. Commits were found with `git log -S` and `git blame`.

## Since when

| What | Commit |
|---|---|
| First Holdings with two `dcterms:source` (WCF one-covenant-two-administrations, sign-and-seal-of-the-covenant) | `4e49471` (2026-10-25) |
| `unchurches.excluded` picks one source with `g.value` | `8992b8b` (2026-11-12) |
| weigh renders excluded Bodies with that source | `1589f32` (2026-11-13) |
| WCF administration-of-grace (two sources, the one later flagged) | `00e7a8e` (2026-11-08) |
| **Output first varies** (the first flags; an excluded row now prints a two-source Holding) | **`bc651fe`** (2026-11-22). Its parent `d81b51e` gives one hash on all four seeds in both scopes. |
| Output stable again | `395f3ef` (weigh fix 2). Members `46381316eb30`, officers `91bfab215992`, on seeds 0 to 5. |

The defect was in the code from `8992b8b`. It could not show until a flag existed in the data.

## The claims

Every "weigh byte-identical", "weigh unchanged" or quoted weigh hash in `docs/` was checked at its commit. Reports 14 to 26, ADR-0001 AY3, ADR-0007, ADR-0008, the handoff's earlier entries and the foreword ruling's Applied: **all made before `bc651fe`, and at each commit the output did not vary across seeds.** They stand as stated.

Two statements rest on the varying output. Each gets a dated note; neither is rewritten:
- [HANDOFF_phase1.md](HANDOFF_phase1.md), the report-27 entry (`9dc56f3`): the hashes `13209f4b689f` / `590965a0a299` are each one of two values.
- [REPORT_phase1_27.md](REPORT_phase1_27.md), E9: "officers gave `590965a0a299` both times". Officers also varies (seeds 1 and 2 give `7dcf90eb14d4`).

The forward-looking lines in ADR-0003 R3.5 and ADR-0009 are verification items, not claims. They are measured when built.
