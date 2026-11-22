# ADR-0010: Church accounts for phase 3: who speaks for a church, how it is verified, and what stays private

- Status: Proposed (phase 3; sent up for review; nothing is built until ratified)
- Date proposed: 2026-11-22
- Date ratified:
- Proposed by: build agent, on the architect's draft ([RULING_site_ground_2026-11-22.md](../handoff/RULING_site_ground_2026-11-22.md), item 4)
- Ratified by: architect

## Context

- ADR-0007 C4' (ruling on report 21) reserves "confirmed by" for a named person who speaks for that church. Until then, a Congregation page says "not yet confirmed by the church". That confirmation act is not built.
- C6' says the church may send a correction. The contact route waits on Chris choosing an address.
- Phase 3 brings people into the data: church representatives, and visitors with their own stances (ADR-0003 R3.3, proposed). People bring personal data, and testimony is not a source (the BSB-foreword ruling: testimony is recorded as testimony, not as the source).
- Standing rules served: 1 (TTL in git is truth), 2, 3, 8 and 11, and the privacy constraints on personal data.

## Decision (proposed)

1. **A church account** is a person's standing to speak for one Congregation. It is held by a named person and recorded with the Congregation's IRI, the person's office, the polity basis (2) and the verification (3).
2. **Who speaks, by polity.**
   - The church's own statement or constitution decides who speaks for it. That is recorded with its source and locator, as any other claim of the church's (the warrant rule, item 3).
   - Where the statement is silent, the proposed default is a serving officer (an elder, pastor, deacon or the equivalent) whose office can be checked from a public listing by the church.
   - The polity classes (congregational, presbyterian, episcopal) are labels for display. They never replace the church's own words.
3. **Verification is recorded.** For each account the record holds:
   - how the person was verified (for example a reply from an address on the church's own domain, a listing on the church's site, or a signed letter);
   - who verified it;
   - the date.

   Chris signs the verification on a console, as every act that enters the data is signed. The public page says "confirmed by <name>, <office>, on <date>", and nothing more about the evidence.
4. **Statement and testimony are separate.**
   - A church's **statement** is a published document, a Source (ADR-0007 C3; ADR-0009, proposed). Only a statement grounds a Holding or an exception.
   - A person's **testimony** (an account of practice, history or meaning) is recorded as testimony. It never becomes the `dcterms:source` of a Holding. It may be attached as a note, as the BSB-foreword ruling did.
   - A confirmation by an account holder confirms that the entry matches the church's statement. It does not turn testimony into a source.
5. **Testimony is private by default.**
   - Testimony is not shown on a public page unless its giver consents, item by item, on a recorded act.
   - Withdrawing consent removes it from public pages. The record of the withdrawal is kept.
6. **Where personal data lives (proposed).**
   - Git holds only the public facts: the Congregation, "confirmed by <name>, <office>, <date>", and the verification's kind.
   - Contact details, verification evidence and private testimony are kept in a private store, never committed. This is the same discipline as the private corpus.
   - **Q:** the architect is asked to confirm this split. It is the one place where "TTL in git is truth" (rule 1) yields to privacy.
7. **The three gates.** *Not defined in the repository.* The draft names "the three gates" without stating them, and no earlier document defines them. The build agent does not guess them. **Q:** the architect is asked to state the three gates, so they can be written here as conditions a test can check.

## Consequences

- Easier: a church can confirm or correct its own page, and the site can say so honestly.
- Harder: personal data, consent and verification must be handled, with a private store beside the git truth.
- Forbidden: testimony as the source of a Holding; publishing testimony without consent; "confirmed by" from anyone who is not verified as speaking for that church; committing contact details or verification evidence.

## Alternatives considered

- **Chris's signature counts as confirmation.** Rejected by the ruling on report 21 (C4: "No").
- **Self-registration without verification.** Rejected: "confirmed by" would mean nothing.
- **All personal data in git, encrypted.** Rejected in this draft: history keeps it forever, and keys leak. A separate private store can be deleted.

## Verification (to be locked before any build, if ratified)

Sketch only, for review:
- a Congregation page shows "confirmed by" only when a signed verification record exists for a named account;
- no committed file contains contact details or verification evidence (a test over data/ and docs/);
- no Holding has a testimony node as its `dcterms:source` (SHACL);
- testimony without a consent record never appears in public output;
- the three gates, once stated, are each a test.

## Open points

1. **The three gates** (Decision 7).
2. **The private store** (Decision 6): what it is, where it lives, and who may read it.
3. **Correction contact** (ADR-0007 C6'): waits on Chris choosing an address.
4. **Visitor stances** (ADR-0003 R3.3): whether they live in the same private store and are never kept server-side unless the visitor asks.
5. **Chris's own church**: per C4, it shows "not yet confirmed by the church" unless an officer confirms. If Chris holds an office there, may he confirm it? Proposed: not on his own signature alone, since he is also the one who entered it.
