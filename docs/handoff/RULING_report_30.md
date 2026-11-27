# Ruling on report 30 (filed verbatim)

- **From:** the architect, relayed by Chris, 2026-11-26.
- **On:** [REPORT_phase1_30.md](REPORT_phase1_30.md).

```
Q-A-1. Yes. Do the page pass for the 31 now, except Gill pp.
  897-912, which wait until Chris has signed the italic sitting.
  Holding those back was the right call.
Q-A-2. Re-cut, but once, after the page pass is complete, so every
  Argument that differs is handled in a single locked change. One
  unit across the data is worth more than leaving old cuts in
  place. For each re-cut Argument: the old IRI is deprecated with
  dcterms:isReplacedBy and never reused; any Argument Chris has
  signed is listed separately and put to him before it changes.
  Report the full list first; change nothing until ruled.
Merge, the derived-count tests and the page ids: accepted.
```

## Applied

| Item | What | Commit | Result |
|---|---|---|---|
| Q-A-1 | Page pass, part 1 | report 31's commit | 17 viewed (the 16, and p. 345). 10 same, 7 would split into 21 units, 0 merge or widen, 0 signed. Recorded in [AUDIT_argument_unit_2026-11-26.md](AUDIT_argument_unit_2026-11-26.md), "Page pass, part 1"; [REPORT_phase1_31.md](REPORT_phase1_31.md). |
| Q-A-1 | Gill pp. 897-912 | — | Held until Chris signs `9b19159be3098c64`. |
| Q-A-2 | Re-cut once, after part 2 | — | Nothing changed. The part-1 candidates and proposed IRIs are listed. The full list follows part 2. |
| Accepted | Merge, derived counts, page ids | — | Noted. |
