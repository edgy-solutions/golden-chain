# Lock: the statements console, with the ADR-0009 inclusion batch (overnight order 2026-11-22, item 6)

- **From:** the build agent, 2026-11-22. Committed before the builder and the content file.
- **On:** ADR-0003 Revision 3, R3.2 (the humility statement); [ADR-0009](../adr/0009-scope-of-documents.md) Decisions 1-5 and its open points 1-4 as resolved by the ruling; [RULING_report_27.md](RULING_report_27.md) (the 1875 Gadsby printing, Articles 1-31 only, "Chris confirms on a console"); the overnight order, item 6.
- **Base:** `phase-0` `84770b2` (the sitting-2 commit). Suite 824 passed.

## What is built

- **A new console kind, `statements`.** A new builder, `tools/console/specs/statements.py`, reads a content file and `data/*.ttl`. The ingest takes the generic path: it writes only `docs/handoff/SIGNED_statements_<build16>.md`. It writes no TTL and adds no plumb-line sitting.
  - *Why a new kind:* under `plumb-line-followup`, a signed record would enter the plumb-line merge and add a sitting to `data/plumb-line.ttl`. These answers are not plumb-line Holdings.
- **Content:** `docs/consoles/statements-1.json`, format `golden-chain-statements-content/1`. Three sections:
  1. **The standard**, 1 row. One empty free-text field, required. Plain words: it must say three things. The standard can be wrong, Scripture is its judge, and the witnesses are shown so that the reader can test it. No suggested wording.
  2. **The scope**, 1 row. One empty free-text field, required. Plain words: it must say which traditions the site covers, and why. No suggested wording.
  3. **Documents included**, 14 rows, signed as one batch.
     - Each row has a radio (include / leave out / not now) carrying the build agent's proposal, and an optional reason box.
     - The three options are ADR-0009's three states: ratified, rejected, and not yet considered.
     - Each row shows the witness, the PD basis, and the role (grounds a Body, or a witness only).
     - The rows are the 12 SourceWork nodes in the data other than `source/plumb-line`, then Owen's *Hebrews* (Goold vols. 19 and 23) and the 1875 Gadsby printing (new).
     - The Gadsby row also asks Chris to confirm, from 4 page images, the title page and that Articles I-XXXI run from p. 8 to p. 15.
- **Proposals:**
  - "include" on 13 rows.
  - "not now" on `source/bsb-gill-1984`, because the data says written confirmation is still to be sought, and ADR-0009 open point 4 lists a licensed text only once permission is on file.
- **Images (4):** 1875 Gadsby printing, PDF pages 4, 11, 18 and 19. They are rendered from the private corpus to `~/.golden-chain/statements/` and never committed. It is a public-domain page; the build agent viewed it for report 27 to propose.
- **Builder refusals:**
  - a listed source that is not a SourceWork in the data;
  - a row marked new whose IRI is already in the data;
  - any suggested wording on the two statement rows (a `proposed`, `value` or `default` key);
  - `source/plumb-line` listed;
  - a duplicate source.

## Predictions

| # | Prediction |
|---|---|
| T1 | Existing tests pass unamended. The born tests are in a new file, `tests/test_statements_console.py`. |
| T2 | The real content gives 3 sections, with rows `[1, 1, 14]` = 16 and fields 31 (2 text fields, 14 radios, 14 reason boxes, 1 witness check). It has 4 images, 2 statement rows with no proposed value, 13 radios proposing "include" and 1 proposing "not now". |
| T3 | Each refusal above fails the build (one born test each). |
| T4 | A signed `statements` record gives exactly one output, `docs/handoff/SIGNED_statements_<build16>.md`. It writes no TTL and no plumb-line record. `statements` is in `build.KINDS` and `ingest.KINDS`. |
| T5 | `build.py` builds the page under `~/.golden-chain/console/statements/`. The build16 is recorded in the report. |
| T6 | No `data/*.ttl` change. The PREDICTED counts are unchanged, ingest gives 0/0, and the weigh hashes are unchanged. |
| T7 | Full suite: the base total plus the born tests, 0 failures. A failing existing test is reported before anything is amended. |

## Recorded before building (for the architect)

- **Q-I-1.** `source/plumb-line` (the signed sittings) is not offered. It is the site's own standard (ADR-0006), not a published document weighed against it. Proposed: exempt it from ADR-0009, so the Documents-included page leaves it out rather than listing it as "not yet considered". The alternative is a 15th row.
- **Q-I-2.** How the signed answers enter the data. Proposed: one locked change, after the sitting, that writes:
  - the standard statement as `<source/plumb-line/standard-statement>` with `rdfs:comment`;
  - the scope statement likewise;
  - the ADR-0009 triples (`gc:status`, `gc:ratifiedBy`, `dcterms:dateAccepted`, the record's name) on each source signed in, and `rdfs:comment` reasons on each left out.
  The two new sources (Owen, Gadsby) are minted in that change as SourceWork nodes, with the labels shown on the console.
- **Q-I-3.** Owen is offered as one Source node covering both Goold volumes. The alternative is one node per volume, since ADR-0009 open point 2 says "per edition".
- **Q-I-4.** BSB 1984 is proposed "not now" (above). The architect may rule it "include" on the publisher's stated position.
