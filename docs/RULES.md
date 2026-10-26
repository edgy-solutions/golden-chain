# Standing rules

These rules come from the phase-0 brief, as amended by the architect. They bind every agent working in this repo.

**Dates and times** (ratification of ADR-0002 Revision 1, 2026-10-25): dates in docs, ADRs and reports are America/Chicago local. Lock-file timestamps stay UTC, with a `Z` suffix, as written; lock files are never rewritten.

1. **TTL in git is the only truth.** Stores, indexes and derived graphs are rebuilt from it.
2. **Every Position traces to a source chapter** and carries at least one Passage via an Argument.
   - Clarified in ADR-0005: at least one Argument from *some* source; a Holding needs no Argument of its own.
3. **No LLM asserts doctrine** in any output.
4. **Only public-domain or licensed text.** Report source, edition and licence first.
   - The pre-commit hook allows only `.ttl`, `.py` and `.md` under `data/`, and refuses PDFs anywhere.
5. **ADR before building.**
6. **Predict counts, then verify.** A divergence is a finding, not a fix.
   - Every count is predicted, derived counts included. A count pinned as measured, not predicted, is a finding (ruling Q21, 2026-10-26; the Passage 87 pin was accepted once).
7. **Tests are born with the change.** Thresholds get a documented reason.
8. **When uncertain, stop and report.**
9. PDF and permission letter live in the private corpus repo at <corpus path>/gill/ — read-only, by configured path, never committed or copied here.
10. **goat-yard laws 2–7 and 9** (goat-yard terms, 2026-10-25). They apply to all OCR and extraction work here, whether or not the result is cited back to goat-yard:
    - fail loud;
    - deterministic properties in code, with mode-midpoint thresholds;
    - predict before spend;
    - clean-run;
    - run headers;
    - zero wrong-pass;
    - sign from pixels.

## Related

- How Golden Chain consumes goat-yard: [sources/goat-yard.md](sources/goat-yard.md).
- Page images of PD texts may be viewed with local tools. Crops are never sent to hosted models (architect, 2026-10-25).
- OCR is HELD until goat-yard tag `substrate-v0` exists.
