# goat-yard-archive: terms of consumption (lane G)

- For: any agent touching OCR, extraction, page geometry or Passage IRIs.
- Received from the goat-yard architect via the architect, 2026-10-25. Recorded verbatim below, followed by the build agent's status on each item.

## Terms (2026-10-25)

> - Golden Chain is lane G of goat-yard-archive: read-only consumer of
>   the A2 substrate (page geometry, text_lines, box_sanity,
>   strip_to_native, run_header/endpoint_guard/corpus fingerprint, the
>   truth-console pattern). NOT cv_footnote_presplit, the Hebrew lanes,
>   marker_ledger, or anything private.
> - Pin: tag substrate-v0 on body-path-a2, not yet cut. OCR step remains
>   HELD until it exists. Do not OCR with other tooling meanwhile.
> - Consumption: a separate goat-yard-archive worktree at the tag, pip
>   install -e into our venv. No submodule. Never copy substrate code
>   into this tree.
> - Interface requests: one file each at goat-yard's
>   docs/requests/REQUEST_goldenchain_<date>.md, public-safe, with the
>   motivating measurement. Expect latency; work around first.
> - We supply our own endpoint allowlist to endpoint_guard. Known warts
>   at v0: :11434 hardcoded in some URL construction; two copies of
>   endpoint_guard.
> - Italic-span detection is a Golden Chain lane. Plan: Tesseract
>   per-word italic flag as baseline, against a signed truth set (n
>   stated), locked prediction, mode-midpoint threshold, abstain when
>   unimodal. Not started until OCR is unheld.
> - Any result cited back to goat-yard must satisfy their laws 2-7 and 9
>   (fail loud; deterministic properties in code with mode-midpoint
>   thresholds; predict before spend; clean-run; run headers; zero
>   wrong-pass; sign from pixels). Add these to STANDING RULES as rule
>   10, applying to all OCR and extraction work here regardless of
>   whether it is cited back.
> - ADR-0002 (identity) must, before ratification: put the versification
>   scheme in the passage IRI (segment, default kjv); reserve a
>   sub-verse Anchor resource shape without minting any; state that
>   passage IRIs name text locations only and that every citing resource
>   (Argument, Holding, external region) is distinct. Send the revised
>   ADR text up for review; it goes to the goat-yard architect too.
> - Italic lane rule: the model transcribes, code decides italic/roman
>   from measured slant. Never ask a model whether a word is italic.
> - Truth sets are signed by Chris alone, for both projects. State n
>   before any run and keep it to a single sitting.

## Additions (2026-10-25, later)

> 1. The 1766 Exposition volume-1 scans are public at goatyardarchive.org
>    (/scans, native res). When the italic lane reaches the second
>    typeface, take pages from there. Any 1766 page cited anywhere in
>    this project carries goat-yard's FILE page number and the line
>    "printed = file − 88". No other numbering for those pages, ever.
>
> 2. Column-rule measurement, NOT held on the tag. Goat-yard's column
>    split (fix A) locates the printed double rule between columns and
>    abstains with a flag where none is detected. Before we pin, measure
>    our 20 phase-1 pages (BSB/Tegg pp. 896-915): does each carry a
>    printed inter-column rule, and what is the inter-column gap
>    distribution? Prediction, locked now: the rule is present on all
>    20 (it is visible on p. 183 of the same setting). If it is absent
>    anywhere, the first request file to goat-yard is "column split
>    without a rule" with the gap distribution attached, threshold by
>    mode-midpoint, abstain if unimodal. Use plain image tooling for the
>    measurement (this is a measurement, not an OCR step); record n,
>    method, and the per-page result in docs/sources/. Do not consume
>    goat-yard code for it.
>
> 3. ADR-0002 text must state: the kjv versification table is derived
>    from CrossWire SWORD canon.h, with the three totals (66 / 1,189 /
>    31,102) as its provenance line, in the same form goat-yard uses for
>    truth sets.

## Response on the single rule (2026-10-26)

> - Single rule accepted by construction; no single-rule test exists in
>   goat-yard; thresholds were tuned on vol.1 doubles. RULE_COL_FRAC
>   0.59 per 300-row strip is the risk for our 14 px rule.
> - Pin only to the tag substrate-v0 once Chris confirms it exists at
>   3d0b03e. Then, before any OCR: run goat-yard's locate_column_rule
>   unchanged on pp. 896-915. Lock the prediction now: 20/20 ok, all
>   strips carrying a cluster, max residual <= 15 px. Report per-page
>   status, strips, half_w, residual. Any abstention is a finding and
>   becomes the first request file with per-column ink fractions.
> - If 20/20 passes, prepare a single-rule synthetic fixture in the
>   shape of test_verse_regions._cs_page to offer back to A2.

Prediction locked 2026-10-26, before any run: n = 20 (printed 896–915),
**20/20 ok, every strip carries a cluster, max residual ≤ 15 px**. The
locked file is `~/.golden-chain/gy-locate-column-rule-predictions-locked.txt`.

## Install (ruling on report 4, 2026-10-26)

`pip install -e --no-deps` of the substrate-v0 worktree into the golden-chain venv, accepted by the architect.

Skipped, and why:
- **Package dependencies** (goat-yard `pyproject.toml` at 3d0b03e): python-dotenv 1.2.1, requests 2.32.5, weaviate-client 4.18.3, dspy-ai 3.0.4, baml-py 0.211.1, openai 2.14.0, tenacity 9.1.2, protobuf < 6, pymupdf ≥ 1.27.1.
- **Extra `backend`** (not requested): fastapi, uvicorn, pydantic, httpx, langfuse, passlib, bcrypt, python-multipart, slowapi, sqlalchemy, psycopg2-binary, svix, pyjwt.
- **Extra `pipeline`** (not requested): dagster, dagster-webserver, networkx, matplotlib, nltk, rapidfuzz, minio, pytesseract, dagster-slack, langfuse.
- **Why.**
  - The modules we run need only numpy and Pillow. Those come from our own `measure` extra, with pypdfium2.
  - The skipped set is LLM clients, a vector store, a web backend and an orchestrator. None is used by a measurement, and rule 3 keeps LLM clients out of anything that touches doctrine.
  - `pipeline/__init__.py` imports dagster. So the flat modules are loaded by path (`pipeline/scripts`, `pipeline/reextract` on `sys.path`), never as the `pipeline` package.

Modules loaded by path: `build_page_geometry`, `cv_footnote_presplit`, `verse_regions`, `note_start_detect`, `box_sanity`, `hanging_indent`. They are listed in `SUBSTRATE_MODULES` in `tools/gy_locate_column_rule.py`, and the pin guard fails if the set loaded differs. `tests/test_gy_locate.py` imports each one, so a module that comes to need a skipped dependency fails at test time, not at run time.

## Status (build agent, updated 2026-10-26)

| Item | Status |
|---|---|
| Pin `substrate-v0` | **Pinned 2026-10-26.** Chris confirmed it on origin: annotated tag `2d695735` → commit `3d0b03e0`. Worktree `../goatyard-substrate-v0`, detached at the tag, clean. Installed with `pip install -e --no-deps`, accepted on report 4 (see Install above). OCR is still HELD (see Addition 2). |
| Endpoint allowlist | Golden Chain's own guard (Jena half) is built and tested; the goat-yard `endpoint_guard` is not yet consumed. |
| Rule 10 | Added to [../RULES.md](../RULES.md). |
| ADR-0002 revision | Applied as "Revision 1" in [ADR-0002](../adr/0002-identity-iri-patterns.md). Proposed, for review by both architects. |
| Addition 1 (1766 numbering) | Recorded. No 1766 page is cited yet. |
| Addition 2 (column rule) | Measured: the rule is present on 20/20, as a **single** rule. goat-yard `locate_column_rule` at substrate-v0, run once on pp. 896–915. **The run PASSES goat-yard's criteria, 20/20** (≥ 3 strips and ≥ 50 % per page, residual ≤ 15 px; max 13.3 px). The locked clause "every strip carries a cluster" is **FALSIFIED**: 14 of 440 strips are empty, on pp. 896, 902, 907 and 908. The clause was the architect's and stricter than goat-yard's acceptance. The lock is not edited. The empty strips are a finding, not a defect. Strips are prepared for Chris to sign from pixels ([gill-column-rule.md](gill-column-rule.md)). OCR is unheld only once Chris has signed and the two hypotheses are confirmed, or the request file is written. |
| Addition 3 (provenance line) | In ADR-0002 rule 5. goat-yard has no written truth-set provenance form; the line follows its nearest examples, marked **pending GY form** (ruling Q20). The question is in the GY message. |
| Interface requests filed | None. |
| Single-rule fixture for A2 | **Not prepared.** Its condition, "if 20/20 passes", is met on goat-yard's criteria (ruling on report 4). Preparing it awaits the architect's word (report 5). |
