# Ruling on report 27 (filed verbatim)

- **From:** the architect, relayed by Chris, 2026-11-22.
- **On:** [REPORT_phase1_27.md](REPORT_phase1_27.md).

```
ARCHITECT RULINGS — report 27.

Ingest: accepted. E9 and E10 are recorded as misses; neither lock
 is edited.

Weigh fixes: build both, each under its own lock.
 1. A flag's source is the sitting named on that flag's own
    annotated axiom (ADR-0006 R1), never the latest sitting.
 2. Where a Holding cites several sources, weigh lists all of them
    in IRI order. No choice among them, so the output is stable.
 Then report since which commit the output could vary, and which
 earlier "weigh byte-identical" claims rested on a Holding with
 more than one source. Those claims are marked "not verifiable as
 stated" by dated note; none is rewritten. Add a test that runs
 weigh twice in separate processes and compares bytes.

Test amendments: accepted, not redone. But a test pinned to the
 live plumb-line breaks at every sitting and invites this again.
 Move those eight to a frozen fixture copy of the data they were
 written for, in one commit, with the list of tests. From now on a
 failing existing test is reported before it is amended, as rule 8
 says; these eight are the last exception.

Exclusions: no further note. They follow from Chris's signed flags
 and are displayed with their derivation. Build ADR-0003 Revision 3
 now, since the sitting is in: the Q3 migration under its
 expected-diff lock, the wording "by this site's standard", and
 the line "The site's statement of its standard is not yet signed."

Gadsby 1875: accepted as the proposed witness for Articles 1-31
 only, so labelled. Chris confirms on a console. Articles 32-35
 still have no witness.

Next, in order: the two weigh fixes; R3; sitting 2; Batch C.
```

## Applied

Worked in [REPORT_phase1_28.md](REPORT_phase1_28.md), 2026-11-23:

- **The weigh fixes:**
  - Fix 2 is on `phase-0` (`395f3ef`; S1-S5 held). The note on weigh variance is `07712fb`.
  - Fix 1 is held on `hold/weigh-fix-1` (`194149b`), because the existing `test_w1_w2_w3` fails with it. The proposed amendment, `2a817d1`, waits on the architect.
- **The frozen fixture:** `4bff5fb` (X1-X4 held). These eight are the last exception.
- **ADR-0003 R3:** built on `hold/adr3-r3` (`f4e8b5a`; R1-R10 held), covering:
  - the Q3 migration;
  - "by this site's standard";
  - "The site's statement of its standard is not yet signed."

  It is held for the 26 proposed test amendments (`a193e8b`).
- **Gadsby 1875:** labelled as the proposed witness for Articles 1-31 only. Chris confirms it on the statements console. Articles 32-35 have no witness.
- **Next, in order:**
  - both weigh fixes are done;
  - R3 is built and held;
  - the sitting 2 console is built (`84770b2`);
  - Batch C is stopped under rule 8 on the Argument unit (`e663931`).
