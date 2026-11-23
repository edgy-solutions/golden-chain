# Ruling on report 24 (filed verbatim)

- **From:** the architect, relayed by Chris, 2026-11-22.
- **On:** [REPORT_phase1_24.md](REPORT_phase1_24.md).
- **Chris, with it:** "yes on gospel standard". This is his go-ahead for A-4: the 1875 Gadsby printing may be fetched and viewed.

```
ARCHITECT RULINGS — report 24.

Entails check, (ii) -> (iii). Both readings go to Chris as you
 propose, with one addition on the row. LBC's silence on (iii) is
 an artefact of (iii) being worded from WCF: LBC 7.2 as you read it
 ("it pleased the Lord to make a Covenant of Grace", after the
 fall) states the same timing claim. Propose an LBC Holding on
 (iii) from 7.2, status proposed, and show it on the row. The
 Augsburg precedent was a different ground for the same practice,
 not mere silence; silence alone does not refute an edge. Record
 that distinction in ADR-0003 as a note on the refutation check.
Jena collision: recorded. Keeping these checks off the shared
 database is right; add a guard so a check cannot open it while a
 test run holds it.
A-3: accepted.
A-4: the 1875 Gadsby printing is worth having as a witness for
 Articles 1-31, labelled as covering those only. It is Chris's
 go-ahead to give; nothing is fetched without it.
A-5: accepted.
Console size: leave the photographs at full size. Chris tries it
 first. If it is too slow, propose cropping each photograph to the
 page (lossless) before any downscaling; a downscale would need the
 full-size image one click away.
```

## Applied

Worked in [REPORT_phase1_26.md](REPORT_phase1_26.md), 2026-11-22.
- **Entails check:** the LBC Holding on (iii) from 7.2 is proposed (triples in the report) and shown on the sitting-2 row. It is not in data yet: while `(ii) excludes (iii)` stands it would make LBC inconsistent. It goes in with sitting 2, when that edge is retired.
- **ADR-0003:** the note on the refutation check, after Revision 1 (`fdaf2b0`).
- **Guard:** ADR-0001 amendment 1, AY1–AY3 locked (`30f3c6e`) and held; suite 813 passed.
- **A-3, A-5:** accepted; nothing further.
- **A-4:** Google refused the fetch with its bot check (HTTP 429). Not retried. Recorded in [gospel-standard.md](../sources/phase2/gospel-standard.md).
- **Console size:** no action.
