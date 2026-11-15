# Ruling on report 15

- **From:** the architect, relayed by Chris, 2026-11-14.
- **On:** [REPORT_phase1_15.md](REPORT_phase1_15.md).
- Filed verbatim below.

```
ARCHITECT RULINGS — report 15.

Q-C1. Variant N: an Argument cites one note of one division. 117.
      Ruling 16 governs; the dispatch's "one per passage per
      position" was written before source notes were in view and is
      superseded, recorded against the architect. Nothing is lost
      for the `try` view: each passage a note prints is its own
      supports edge into that Argument, so a user starting from 1
      Pet 3:21 still lands on every clause that cites it. Where one
      note's passages need different interpretive comments, they go
      as annotated-axiom comments on the supports edges (ADR-0002
      R2), not as separate Arguments.
Q-C2. Confirmed. If F-B comes back (a): mint the Locus, Position (a)
      and its Arguments only, and stop. (b)'s wording, Gill's four
      references and the excludes edge wait for a ruling, because in
      that case Gill himself is an (a)-source and the plumb-line's
      (b), if Chris still holds it, stands on his own signed
      Argument rather than on Gill.

Apology IX: accepted as minted. A Holding without an Argument is
right for a condemnation that cites no Scripture (M1).
Truth-set console: accepted as built. The fresh salt for row order
is a good touch.
```

## How it is applied (build agent)

- **Q-C1.**
  - Batch C mints variant N of the lock `step3-batchC-predictions-locked.txt`: 117 Arguments if F-B = (b), 113 if F-B = (a).
  - The lock is not edited.
  - The superseded rule keeps its text, with a dated note, in ADR-0003 R2.4 and in PLAN_step3 (Batch C outline).
- **Reading of "supports edge".**
  - In the data, an Argument's edge to a Passage is `gc:cites`; `gc:supports` runs to the Position.
  - So each passage a note prints is its own `gc:cites` triple on that one Argument, as `argument/belgic-confession/34/001` already does.
- **Per-passage comments.**
  - ADR-0002 R2 §2's axiom IRI pattern is written for Position-to-Position edges.
  - If a Batch C note needs a comment on one of its `gc:cites` edges, I propose an IRI pattern for that axiom first.
  - The expected misprint (Rev 1:5) stays a `gc:resolutionNote` on its Argument, as before.
- **Q-C2.** Applied as the lock's C3.
- **Apology IX and the truth-set console:** accepted. Nothing changes.

## Addendum: the architect on the two readings (2026-11-14), filed verbatim

```
Both readings confirmed. gc:cites is the passage-to-Argument edge;
my "supports edge" meant that. Follow the Belgic 34/001 pattern. On
per-passage comments: propose the axiom naming pattern only if a
note actually needs one; do not mint a pattern for a case that has
not arisen.
```

- Applied: Batch C follows `argument/belgic-confession/34/001` (one Argument per note, one `gc:cites` per passage).
- No axiom naming pattern for `gc:cites` edges is proposed unless a Batch C note turns out to need one at mint time.
