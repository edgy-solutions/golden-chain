# Ruling on report 32 (Day 1 research), with item 8 resent and item 9 (filed verbatim)

- **From:** the architect, relayed by Chris, 2026-11-27.
- **On:** [REPORT_phase1_32.md](REPORT_phase1_32.md) and the three research files of Day 1.
- **Answers Q-O-1:** item 8 of the two-day order is resent in full below, and item 9 is added.

```
ARCHITECT RULINGS — report 32 (Day 1 research). Nothing is minted
by these; they fix the candidates for phase 2.

GENERAL. A borderline cell is "does not say in its own words". Keep
the quotation in a separate column, "bears on", so nothing is lost
and nothing is claimed. A Position answers one question and its
label is one source's words; do not join clauses from two places
into one label.

JUSTIFICATION
- J-P1 to J-P4 and J-P6 accepted as candidates, on three loci:
  J-a (what faith is in justification), J-b (when), J-c (condition).
- J-P5: one Position, labelled with LC Q. 32's words alone. Owen is
  a second source for it; his limit ("no more may be intended...")
  is quoted on his own Argument, not folded into the label.
- Heidelberg Q. 59 and the "if only" of Q. 60: do not say. Move
  both to "bears on".
- Recorded against the architect: the claim that Witsius counts a
  moment "in God's decree". He counts none from eternity.

THE GOSPEL CALL
- The four borderline G-c cells (Gill pp. 165, 169; WCF 7.3; LBC
  7.2; Dort II.5): do not say. Move to "bears on G-c". G-c is
  answered by Fuller alone until the Gospel Standard articles are
  read. Look for a place where Gill states in his own words whether
  saving faith is the duty of the unregenerate; report the lead, do
  not supply it.
- Fuller does not stand under G-P3 on these pages. If the 1785 text
  uses "offer" elsewhere, find it; otherwise his "proposal of
  peace" stands as his own wording.
- G-P5 is one Position on G-d. The different grounds (corruption of
  nature; duty) are recorded on each source's Argument.
- G-P4 joins answers to two questions. Split it: Gill p. 91 on G-b;
  Gill pp. 156-157 on G-a, with a note that it is said of Christ's
  own preaching to Israel. Replace row 2c's paraphrase with those
  quotations.
- G-P1, G-P2, G-P3, G-P6, G-P7 accepted as candidates.

THE CHURCH
- C-P1 to C-P5, C-P7, C-P8 accepted as candidates.
- Scots XVIII p. 462 answers C-b (where the true kirk is known),
  not C-a. C-a for Scots: does not say.
- C-P6: Belgic stands apart from WCF. WCF has synods determining
  "ministerially"; the Belgic articles read give the council of the
  church and say nothing of synods. Word a separate candidate from
  Belgic XXX.
- Laying on of hands (LBC 26.9; Gill p. 868): record as a locus
  candidate of its own. Do not develop it now.
- Row 4c: drop it. No source names marks for it, and reading
  26.6-26.8 as marks would be our judgment.
- Read WCF 27.4 and Scots XXII now; LBC 28.2 on the 1677 page once
  that sitting is signed.
- Gill II.3 p. 867 (the essence of ordination) and pp. 874-876:
  show them on sitting 2's administrator rows if not already there.

ITEM 8, resent in full, and item 9:
8. Two drafts, proposed, not built:
   - a deployment ADR: what must be true before anything is public
     (the signed humility and scope statements; BSB's written
     confirmation; the corrections address; the Documents included
     page; legal review before any church is named);
   - a projection ADR for Neo4j and Weaviate under ADR-0001: what
     is projected, the guard test, and what each store is for.
9. If time remains: the argument-unit audit's full re-cut list for
   every Argument outside Gill pp. 897-912, ready for ruling.
```

## Applied

| Item | What | Commit | Result |
|---|---|---|---|
| General | Borderline cells become "does not say in its own words"; quotations kept in a "bears on" column; one source's words per label; one question per Position | `85712ea` | Applied in the three research files below. |
| Justification | J-P1 to J-P4, J-P6 candidates on J-a, J-b, J-c; J-P5 on LC Q. 32 alone, Owen on his own Argument; Heidelberg Q. 59 and Q. 60 to "bears on"; the Witsius claim recorded against the architect | `85712ea` | [RESEARCH_justification_2026-11-26.md](RESEARCH_justification_2026-11-26.md). |
| Gospel call | Four G-c cells to "bears on G-c"; G-c answered by Fuller alone; Fuller off G-P3; G-P5 one Position; G-P4 split (G-P4a on G-b, G-P4b on G-a, with the note on Christ's preaching to Israel); G-P1-3, 6, 7 candidates | `85712ea` | [RESEARCH_gospel_call_2026-11-26.md](RESEARCH_gospel_call_2026-11-26.md). As ruled, the lock now scores one P2 miss: Gill G-c (predicted yes). The label source for G-P5 (Fuller) is the build agent's choice, put to the architect. |
| Row 2c | Paraphrase replaced by Gill's quotations | `85712ea` | [PROPOSAL_phase2_loci.md](PROPOSAL_phase2_loci.md): two rows, G-P4a and G-P4b. |
| The church | C-P1 to C-P5, C-P7, C-P8 candidates, each relabelled from one source; Scots XVIII p. 462 moved to C-b, Scots C-a does not say; C-P6 WCF only; C-P6b new from Belgic XXX | `85712ea` | [RESEARCH_church_2026-11-26.md](RESEARCH_church_2026-11-26.md). The Scots C-a cell now scores as held. |
| Laying on of hands | A locus candidate of its own, not developed | `85712ea` | [PROPOSAL_phase2_loci.md](PROPOSAL_phase2_loci.md) §11: LBC 26.9 and Gill p. 868, recorded only. |
| Row 4c | Dropped | `85712ea` | Removed from [PROPOSAL_phase2_loci.md](PROPOSAL_phase2_loci.md) §4, with a note. |
| Searches | A Gill lead on duty-faith; "offer" elsewhere in Fuller 1785 | this commit | [FINDINGS_ruling32_reads_2026-11-27.md](FINDINGS_ruling32_reads_2026-11-27.md), under lock `5fdbcd8`. No gospel "offer" located in Fuller 1785. Two Gill leads (CGT I, Numb. XXVIII, pp. 149-152; III, p. 68) are reported, not supplied. |
| New reads | WCF 27.4 and Scots XXII now; LBC 28.2 after the 1677 sitting is signed | this commit | Same file. WCF 27.4 and Scots XXII both answer C-d; entering them waits on the architect. LBC 28.2 waits on `0a73bb5afa616446`. |
| Sitting 2 | Gill II.3 p. 867 and pp. 874-876 on the administrator rows, if not already there | later commit | Checked first. If a test must change, the change goes to a hold/ branch. |
| Items 8 and 9 | Two ADR drafts; the re-cut list | later commits | Proposed, not built. |
