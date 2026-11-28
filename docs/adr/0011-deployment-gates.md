# ADR-0011: Publish nothing until every deployment gate holds, and check the gates by machine

- Status: Proposed
- Date proposed: 2026-11-27
- Date ratified:
- Proposed by: build agent, on the ruling on report 32, item 8 ([RULING_report_32.md](../handoff/RULING_report_32.md))
- Ratified by: architect

## Context

- **The ruling asks for** "a deployment ADR: what must be true before anything is public (the signed humility and scope statements; BSB's written confirmation; the corrections address; the Documents included page; legal review before any church is named)".
- **What is true now:**
  - No site is served. Weigh, the consoles and the examine/try prototype (ADR-0008) run locally only.
  - The **humility statement** (ADR-0003 R3.2) and the **scope statement** (ADR-0009 Decision 5) are Chris's to write. They are on the statements console `f3f1af17d9075ba5`, which is **open and unsigned**. Until they are signed, weigh prints "The site's statement of its standard is not yet signed."
  - The **BSB 1984 foreword** is recorded as "published 1984; no copyright notice per Chris; publisher's stated position that its books are freely distributable; written confirmation to be sought before public launch" ([RULING_bsb_foreword_status_2026-11-22.md](../handoff/RULING_bsb_foreword_status_2026-11-22.md)). Chris reports that a permission letter is in the works.
  - The **corrections address** `corrections@golden-chain.org` is chosen (ADR-0010 open point 3) and is on the ADR-0007 C6' correction line (AX1). Where it forwards is recorded nowhere, by design.
  - The **Documents included page** (ADR-0009 Decision 4) is ratified with changes, but not built.
  - **No Congregation is in the data.** Weigh's derived listing "not a church by this site's standard" names Bodies that are in the data. Each is a confession or its body, with its derivation.
  - **The GitHub repository is public** (checked 2026-11-27). It already carries the TTL, the signed records and the handoff documents. This ADR is about a *served site*. The repository's own visibility is put to the architect as open point 1.
- **Standing rules served:**
  - 1 (TTL in git is truth): the site is built only from a pushed commit.
  - 3 (no LLM asserts doctrine): nothing on the site is model text.
  - 4 (only PD or licensed text).
  - 5 (ADR before building).
  - 8 (stop when uncertain): a gate that cannot be checked counts as not held.

## Decision

### 1. What "public" means

- Something is public when any page, file or API response derived from `data/` is served at an address that someone other than Chris, the architect and the build agent can reach.
- A local file opened from disk is not public. A page shared by link, even an unlisted one, is public.

### 2. The gates

Nothing is public until every gate holds. Each gate is checked from the repo at the commit to be served, or from a signed record in it.

| # | Gate | Holds when |
|---|---|---|
| D1 | **The humility statement is signed** | `<source/plumb-line/standard-statement>` (ADR-0003 R3.2) is in `data/plumb-line.ttl` with its text, `dcterms:creator <agent/chris>`, `dcterms:created` and the signed record's name. Weigh's "not yet signed" line no longer prints. |
| D2 | **The scope statement is signed** | Chris's scope statement (ADR-0009 Decision 5) is in the data in the same way, from the same signed console (ruling on report 28, Q-I-2). |
| D3 | **BSB's written confirmation is on file** | A record `docs/permissions/bsb.md` states the date of the letter, who wrote it, and what it confirms, in a sentence of Chris's. The letter itself is kept privately and is not committed. Until the record is there, nothing that quotes the BSB foreword is served, and the source is listed under ADR-0009 open point 4 rules. |
| D4 | **The corrections address works** | Chris signs a one-row record saying that a test message to `corrections@golden-chain.org` reached him, with the date. It is re-signed if the address or its forwarding changes. No forwarding address is recorded. |
| D5 | **The Documents included page is built** | ADR-0009 is built under its own lock: the page is generated from the source nodes, the backfill console is signed, and weigh's closing line counts the documents in scope. |
| D6 | **Legal review before any church is named** | A record `docs/permissions/legal-review.md` names the reviewer's role (not the person, unless they consent), the date, the pages reviewed by their generator and commit, and the reviewer's conclusion in their own words. Until it is there, the served site names no church. See Decision 3. |
| D7 | **Every open sitting the pages rest on is signed** | No served page shows a value whose signed record is still open. |
| D8 | **The build is clean** | The site is generated from a pushed commit, with a clean tree. The full suite passes at that commit. |

### 3. What "a church is named" covers (the build agent's reading; open point 2)

- Any Congregation (ADR-0007), by its public name and place.
- Any Body listed under "not a church by this site's standard", whatever its age.
- Any Body's stated judgment shown on its page ("<Body> states that holders of <Position> are not a church").
- While D6 does not hold, the served site may show Loci, Positions, Arguments and Sources. It shows no weigh output that names a Body under a judgment, and no Congregation page.

### 4. How the gates are checked

- A tool, `tools/deploy_gate.py`, reads the repo at the commit and prints one line per gate: holds, or not, with the reason.
  - It exits 0 only if every gate holds.
  - It is the only route to a served build. A deploy script that skips it is a defect.
  - It reads records and data. It never decides a gate from model output.
- **The launch itself is a signed act.** Chris signs a one-row launch console, which shows the gate tool's output for the commit. Nothing is served before that signature.
- After launch, the gate tool runs on every served build. A gate that stops holding takes down the pages that rest on it.

## Consequences

- Easier: what blocks a launch is one list, checked by a tool, not a memory.
- Harder: each gate is a signature or a record, and some depend on people outside the project (BSB, a reviewer).
- Forbidden:
  - serving any page before the launch signature;
  - serving a page that names a church before D6 holds;
  - recording where the corrections address forwards;
  - committing the BSB letter or the legal review's private material.

## Alternatives considered

- **Launch in stages, without church naming first.** This is what Decision 3 allows inside the gates. It is not a separate path: D1-D5, D7 and D8 still hold first.
- **A checklist in prose.** Rejected: it drifts from the data. The gate tool reads the same records the site is built from.
- **The architect signs the launch.** Rejected in this draft: every act that enters the data is Chris's signature. The architect rules on the gates.

## Verification (to be locked before any build)

Sketch only, for review:
- Born tests for `deploy_gate.py` on fixture repos: each gate fails alone when its record or data is missing, and the tool exits nonzero.
- On today's repo, the tool reports D1, D2, D3, D4, D5, D6 and D7 as not held, and exits nonzero.
- No deploy script exists that does not call the gate tool. This is a test over `tools/` and the CI config.
- The gate tool's output has no "@" except the corrections address in D4's line.

## Open points

1. **The repository is public.** The served site is gated here, but the GitHub repository already serves the TTL, the signed records and the handoff documents to anyone. Does this ADR's "public" include the repository? If it does, the gates are already passed in substance, and the repository's visibility is the architect's decision first.
2. **The reach of D6.** The build agent reads "any church" as Congregations and also every Body named under a judgment, including the historical confessions. The architect may narrow it to living churches.
3. **D3's scope.** Does BSB's confirmation need to cover only the foreword quotations? Or also the use of BSB's pagination as the locator for Gill, and the page images read to check each quotation? No image is ever served.
4. **D4's record.** Is a signed "it reached me" enough, or should the test message be sent by someone other than Chris?
