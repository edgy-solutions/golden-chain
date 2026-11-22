# ADR-0010: Church accounts for phase 3: who speaks for a church, how it is verified, and what stays private

- Status: Proposed, revision 2 (phase 3; resent 2026-11-22 after the ruling on report 22, which did not ratify revision 1; nothing is built until ratified)
- Date proposed: 2026-11-22 (revision 1); revised 2026-11-22 (revision 2)
- Date ratified:
- Proposed by: build agent, on the architect's draft ([RULING_site_ground_2026-11-22.md](../handoff/RULING_site_ground_2026-11-22.md), item 4)
- Ratified by: architect

## Context

- ADR-0007 C4' (ruling on report 21) reserves "confirmed by" for a named person who speaks for that church. Until then, a Congregation page says "not yet confirmed by the church". That confirmation act is not built.
- C6' says the church may send a correction. The contact route waits on Chris choosing an address.
- Phase 3 brings people into the data: church representatives, and visitors with their own stances (ADR-0003 R3.3, proposed). People bring personal data, and testimony is not a source (the BSB-foreword ruling: testimony is recorded as testimony, not as the source).
- Standing rules served: 1 (TTL in git is truth, for public data; restated below), 2, 3, 8 and 11, and the privacy constraints on personal data.
- **Revision 2** applies the ruling on report 22 ([RULING_report_22.md](../handoff/RULING_report_22.md)): the three gates (Decision 7), member reports (Decision 8), Decision 6 confirmed with rule 1 restated, and open points 2, 4 and 5 answered.

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

   Chris signs the verification on a console, as every act that enters the data is signed. **Chris may not confirm his own church on his own signature** (open point 5, agreed by the ruling). The public page says "confirmed by <name>, <office>, on <date>", and nothing more about the evidence.
4. **Statement and testimony are separate.**
   - A church's **statement** is a published document, a Source (ADR-0007 C3; ADR-0009, proposed). Only a statement grounds a Holding or an exception.
   - A person's **testimony** (an account of practice, history or meaning) is recorded as testimony. It never becomes the `dcterms:source` of a Holding. It may be attached as a note, as the BSB-foreword ruling did.
   - A confirmation by an account holder confirms that the entry matches the church's statement. It does not turn testimony into a source.
5. **Testimony is private by default.**
   - Testimony is not shown on a public page unless its giver consents, item by item, on a recorded act.
   - Withdrawing consent removes it from public pages. The record of the withdrawal is kept.
6. **Where personal data lives (confirmed by the ruling).**
   - **Rule 1, restated:** TTL in git is the truth for **public** data. Personal data lives in the private store and is **never committed**.
   - Git holds only the public facts: the Congregation, "confirmed by <name>, <office>, <date>", and the verification's kind.
   - Contact details, verification evidence, private testimony and member reports (Decision 8) are kept in the private store. This is the same discipline as the private corpus.
   - **The private store** is the Postgres of the original stack, readable by Chris and moderators only (open point 2, ruled).
   - **A visitor's stances** stay in the visitor's browser unless the visitor asks to save them (open point 4, ruled).
7. **The three gates (stated by the ruling). Each is a test.**
   1. **Who may speak for a church.** Verified by the church's polity, as in Decisions 2 and 3. **No doctrinal test:** a pastor of any tradition may state what the church holds.
      - *Test:* no "confirmed by" without gate 1.
   2. **Who may report about a church.** A reporter is approved by a moderator on identity and accountability, **not on doctrine**. One report per person per church; a restatement replaces the earlier one, with history kept.
      - *Test:* no report stored without gate 2.
   3. **Who may moderate.** Appointed by Chris, and holds the site's standard.
      - *Test:* no moderation act by an account without gate 3.
8. **Member reports: a third kind of input (added by the ruling).** Distinct from the church's statement (Decision 4) and from free testimony.
   - **Form:** answers chosen from the same closed list of Positions the church answers, with the dates the reporter says they attended. **No free text.**
   - **Privacy:** private to moderators and the church's verified contact by default.
   - **Never grounds a Holding.**
   - **If ever shown:** only as counts above a stated minimum, labelled as reports, with the church's reply beside them.
   - **The site keeps no church rolls.**

## Consequences

- Easier: a church can confirm or correct its own page, and the site can say so honestly.
- Harder: personal data, consent and verification must be handled, with a private store beside the git truth.
- Forbidden: testimony or a member report as the source of a Holding; publishing testimony without consent; showing member reports except as counts above the stated minimum with the church's reply; free text in a member report; church rolls; "confirmed by" from anyone who is not verified as speaking for that church; Chris confirming his own church on his own signature; committing contact details, verification evidence or member reports.

## Alternatives considered

- **Chris's signature counts as confirmation.** Rejected by the ruling on report 21 (C4: "No").
- **Self-registration without verification.** Rejected: "confirmed by" would mean nothing.
- **All personal data in git, encrypted.** Rejected in this draft: history keeps it forever, and keys leak. A separate private store can be deleted.

## Verification (to be locked before any build, once ratified)

Sketch only, for review:
- a Congregation page shows "confirmed by" only when a signed verification record exists for a named account;
- no committed file contains contact details or verification evidence (a test over data/ and docs/);
- no Holding has a testimony node as its `dcterms:source` (SHACL);
- testimony without a consent record never appears in public output;
- gate 1: no "confirmed by" without a gate-1 verification record;
- gate 2: no member report stored without a moderator's gate-2 approval; one current report per person per church, with replaced reports kept in history;
- gate 3: no moderation act by an account not appointed by Chris;
- a member report with any free-text field is refused; no member report is a `dcterms:source`;
- public output shows member reports only as counts at or above the stated minimum, labelled as reports, with the church's reply;
- a verification of Chris's own church signed only by Chris is refused.

## Open points

1. ~~The three gates~~: stated by the ruling (Decision 7).
2. ~~The private store~~: the Postgres of the original stack, readable by Chris and moderators only (Decision 6).
3. **Correction contact** (ADR-0007 C6'): Chris chose `corrections@golden-chain.org` (2026-11-22, an alias he set up on the site's domain). Not yet built: putting it on the correction line changes ADR-0007 AW4, which checks the line has no "@", so the change waits on a ruling and its own lock.
4. ~~Visitor stances~~: in the visitor's browser unless the visitor asks to save them (Decision 6).
5. ~~Chris's own church~~: agreed, not on his own signature (Decision 3).
6. **New, for the architect: the stated minimum** for showing member-report counts (Decision 8). No number is proposed by the build agent.
