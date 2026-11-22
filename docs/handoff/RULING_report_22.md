# Ruling on report 22 and the four site's-ground drafts (filed verbatim)

- **From:** the architect, relayed by Chris, 2026-11-22.
- **On:** [REPORT_phase1_22.md](REPORT_phase1_22.md) and the drafts listed in [RULING_site_ground_2026-11-22.md](RULING_site_ground_2026-11-22.md).

```
ARCHITECT RULINGS — report 22 and the four site's-ground drafts.

ADR-0007 amendment 2: accepted. AW5's miss is recorded; both
unlisted edits follow from the ruling.

ADR-0003 REVISION 3: RATIFIED with these answers.
 Q1. Render judgments locally with the line "The site's statement
     of its standard is not yet signed." No public deployment until
     Chris has signed the statement; write that into the future
     deployment ADR as a condition.
 Q2. As proposed. In a comparison view from Body B, B's stated
     judgments are listed beside B, labelled "stated by B", and
     exclude nothing. Only the site's standard derives exclusions.
 Q3. Migrate to the one form. data/plumb-line.ttl is the
     deterministic replay of the signed sittings, so this is a
     change to the replay writer, not to any signed record. No new
     signature. Lock the expected diff first; the replay test must
     still pass byte for byte against the new writer.
 Q4. Keep the three forms; change only "plumb-line's" to "site's".

ADR-0009: RATIFIED with changes.
 - No new gc: properties (ADR-0002 rule 6). Inclusion uses what
   Holdings already use: gc:status ratified, gc:ratifiedBy
   agent/chris, dcterms:dateAccepted, and the signed record's name.
   "Considered and left out" is gc:status rejected with the reason
   as rdfs:comment. A source with neither is "not yet considered".
 - Add Decision 5: the four criteria in Decision 1 are formal. The
   doctrinal boundary of scope (which traditions the site covers
   and why) is Chris's statement, written and signed by him on a
   console, stored and shown like the humility statement. No model
   drafts it.
 - Open points: (1) one backfill console, signed as a batch;
   (2) per Source node, so per edition; (3) the page states each
   work's role, Body or witness or both; (4) listed by title as
   "licensed, not reproduced", and only once written permission is
   on file.

WARRANT: the recording rule is ratified as drafted. Row 10 stays a
 proposal. The LBC 1.6 reading waits for the 1677 page.

ADR-0010: NOT ratified. Revise and resend.
 - The three gates (Decision 7):
   1. Who may speak for a church. Verified by the church's polity
      as in Decisions 2-3. No doctrinal test: a pastor of any
      tradition may state what his church holds.
   2. Who may report about a church. A reporter is approved by a
      moderator on identity and accountability, not on doctrine.
      One report per person per church; a restatement replaces the
      earlier one, with history kept.
   3. Who may moderate. Appointed by Chris, and holds the site's
      standard.
   Each is a test: no "confirmed by" without gate 1; no report
   stored without gate 2; no moderation act by an account without
   gate 3.
 - Add member reports as a third kind of input, distinct from the
   church's statement and from free testimony: answers chosen from
   the same closed list of Positions the church answers, with the
   dates the reporter says he attended, and no free text. Private
   to moderators and the church's verified contact by default.
   They never ground a Holding. If ever shown, only as counts above
   a stated minimum, labelled as reports, with the church's reply
   beside them. The site keeps no church rolls.
 - Decision 6 confirmed, and rule 1 is restated: TTL in git is the
   truth for public data. Personal data lives in the private store
   and is never committed.
 - Open points: (2) the private store is the Postgres of the
   original stack, readable by Chris and moderators only; (4) a
   visitor's stances stay in his browser unless he asks to save
   them; (5) agreed, Chris may not confirm his own church on his
   own signature.

A-5. Gospel Standard: yes, look for the earliest separate printing
 of the Articles by the Societies with a page image. Locate and
 report only. No download without Chris.
A-6. R6: still unread by the architect; it stays provisional.

PIXEL CHECKS: the WCF 1647 leaf 14 folio and LBC 1.6 are readings
 from a page, so they go to Chris as console rows, not as requests
 in a report. Add both to the LBC 1677 console spec.
```

## Applied

Worked in [REPORT_phase1_23.md](REPORT_phase1_23.md), "The ruling on report 22, worked":
- ADR-0003 R3 marked ratified, not built, with an R3.7 section (Q1–Q4). The Q3 migration is locked and built after eb961ddb is ingested.
- ADR-0009 marked ratified with changes: Decision 3 restated with existing terms, Decision 5 added, open points resolved. Not built.
- Warrant recording rule marked ratified in PROPOSAL_phase2_loci.md. Row 10 stays a proposal.
- ADR-0010 revision 2 resent: Decisions 6–8, Verification, and open points as ruled. New open point 6 (the stated minimum).
- Pixel checks added to the LBC 1677 console spec (rows `1.6.locate` and `wcf1647.leaf14.folio`), with born tests.
- A-5 located and reported only; nothing downloaded. A-6: R6 stays provisional.
