# Ruling on report 31, and the two-day order of 2026-11-26 (filed verbatim)

- **From:** the architect, relayed by Chris, 2026-11-26.
- **On:** [REPORT_phase1_31.md](REPORT_phase1_31.md).
- **The paste arrived cut off** partway through item 8, at "8. Two drafts, proposed, not". The text below ends where the paste ended. Nothing has been added to it. The rest of item 8 is put to the architect as a question (Q-O-1, below).

```
ARCHITECT RULING — report 31.
Q-P-1. Three units for Graves. Each reference is bracketed after
  its own noun, so each is its own quotation unit; sharing a
  sentence does not join them. The slip (one string read per
  Argument) is recorded; part 2 reads every string.

TWO-DAY ORDER, 2026-11-26. Chris is away for about two days and
four consoles are unsigned, so take only work that needs no
signature. Lock before each item. Push as you go. A change that
needs an existing test amended goes to a hold/ branch. Research
items are propose-only: quotations of at most three sentences with
locator, or "does not say in the sections read"; store no other
text; mint nothing. Do not view Gill pp. 897-912 or any image in
an open sitting. If a fetch is refused, do not work around it;
record it and move on. One report at the end of each day, each
with a single list of what waits on Chris and on the architect.

DAY 1

1. Justification, in the form of the 23a research. Questions to
   put to each source:
   J-a. Is faith an instrument in justification, or the reception
        and evidence of a justification already passed?
   J-b. When are the elect justified: from eternity, in Christ's
        resurrection, or upon believing? Does the source
        distinguish several senses or moments?
   J-c. Does it call faith a condition, and in what sense?
   Sources: WCF 11 and Larger Catechism 32, 70-73; LBC 11 (1677
   photographs if Chris has them, else the 1719 printing, marked);
   Gill, Body, Doctrinal II.5 (with its sub-entry on justification
   as an immanent act) and the chapter on justification in Book
   VI; Owen, The Doctrine of Justification by Faith (1677);
   Witsius, Economy, III.8; Heidelberg 59-61; Belgic 22-23.
   Deliver the table, and proposed Positions worded only from the
   sources. Record Chris's unsigned words of 2026-11-15 beside the
   table; attach them to nothing.

2. The gospel call, same form, for the rows already in the phase-2
   table. Questions: is the gospel to be published to all; is it
   an offer and in what sense; is saving faith the duty of the
   unregenerate; is unbelief a sin and of what kind; what may a
   preacher exhort the unconverted to. Sources with a page
   witness only: Gill, Cause of God and Truth; Fuller, Gospel
   Worthy (1785); the 1875 Gadsby printing, Articles 24, 26, 29
   and neighbours; Canons of Dort II and III-IV with the
   Rejections (Scott 1831); WCF 7.3, 10 and LBC 7.2, 10.

3. The church, same form. Questions: of whom is a visible church
   constituted; what are its marks; who governs it and who speaks
   for it; who may administer the ordinances. Sources: LBC 26;
   WCF 25, 30, 31; Belgic 27-32; Scots 16, 18; Gill, Body,
   Practical Book II. Join this to the Gill-on-the-administrator
   findings already made.

DAY 2

4. More of Gill, read by machine. Under the standing pin rules
   (column rule, narrow-glyph margin, line height reported): OCR
   and v4 slant on Doctrinal Book II (the covenant chapters and
   II.5) and Practical Book II. Report counts and the pool rates
   of words that do not crop cleanly. No text enters the repo.
   Draw nothing for signing yet.

5. Footnotes. Design and measure, under a lock, a rule that
   separates column footnotes from body text on the baptism
   chapter, from geometry only (position, type height, the
   boundary). Chris's signed notes on p. 913 and p. 914 are the
   test cases. Report where it agrees and disagrees with them.
   Change no OCR output yet.

6. The second typeface. If goatyardarchive.org's public scans can
   be fetched, take about 20 pages of the 1766 Exposition, cite
   each by FILE page with "printed = file − 88", and run the v4
   slant measure on them. Report whether it is bimodal and where
   the threshold falls. Build nothing for signing.

7. Prototype, local only. Extend the examine/try prototype with a
   weigh page and a Body page, generated from weigh's output and
   the data: the three groups (could join; could join with stated
   differences; could not join), walls shown apart from
   differences, the "not a church by this site's standard"
   listing with its derivation and the unsigned-statement line,
   each claim with its source. No sentence that is not a label, a
   locator or a signed record. Draft this as ADR-0008 Revision 1,
   proposed; the prototype may be built ahead of ratification
   because it is local, read-only and mints nothing.

8. Two drafts, proposed, not
```

**[The paste ends here. The rest of item 8, and anything after it, was not received.]**

## Questions back

- **Q-O-1. Item 8 was cut off** after "Two drafts, proposed, not". The build agent will not guess what the two drafts are. Item 8 is held until the full text is resent. Days 1 and 2, items 1-7, go ahead.

## Applied

| Item | What | Commit | Result |
|---|---|---|---|
| Q-P-1 | Graves is three units | this commit | Noted in the audit's re-cut list: `graves-old-landmarkism/10/001` becomes 10/002-004, as proposed. The list stays unapplied until the full list after part 2 is ruled (Q-A-2). |
| The slip | One string read per Argument | — | Recorded in report 31. Part 2 reads every string. |
| Order, items 1-7 | Day 1 and Day 2 work | later commits | Each item has its own lock, committed before its work. |
| Order, item 1 | Justification | lock `991da11`; research this commit | [RESEARCH_justification_2026-11-26.md](RESEARCH_justification_2026-11-26.md): the table for 8 sources, the lock scored (2 misses: Belgic J-b, Witsius J-c), 6 Positions proposed, Chris's words beside the table. Nothing minted. |
| Order, item 8 | Two drafts | — | Held. The text was truncated (Q-O-1). |
