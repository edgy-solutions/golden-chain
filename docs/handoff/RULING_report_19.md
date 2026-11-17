# Ruling on report 19 (filed verbatim)

- **From:** the architect, relayed by Chris, 2026-11-17.
- **On:** [REPORT_phase1_19.md](REPORT_phase1_19.md).

```
ARCHITECT RULINGS — report 19.

A-1. No new property. Record "model-proposed, read by" as an OWL
     annotated axiom on the gc:asPrinted triple (the ADR-0002 R2
     pattern), carrying dcterms:contributor agent/architect and
     gc:status proposed, replaced by agent/chris and ratified when
     he confirms. Add the pattern to ADR-0002 as Revision 3. The
     prototype reads the axiom and shows "proposed reading,
     unconfirmed" beside the string. The rdfs:comment may stay until
     then.
A-2. ADR-0007 RATIFIED with these answers:
     - gc:exceptsLocus accepted (no standard term carries it). An
       "excepted, unknown" cell scores nothing, is shown as such,
       and counts against coverage, never as tolerated.
     - Several parents allowed; ADR-0003 R2's rule applies
       (inconsistent unless the congregation asserts its own
       Holdings where the parents differ).
     - A church's own statement is cited by URL, read date and an
       archived copy's URL; store no text. Every congregation
       Holding carries its source and stays proposed until a named
       person confirms it. A Holding from personal knowledge alone
       is allowed, labelled as that, and shown as that.
     - Add: every congregation page states who entered it, from
       what, and when, and how the church may correct it.
A-3. ADR-0008 RATIFIED as a local prototype. Disclosure per A-1.
     Passage pages show the reference only until ADR-0004 settles
     the display text. Deployment is a separate ADR.
A-4. Not ruled today. I will read the locus table and return it
     reworded. Nothing waits on it.
A-5. - Scots Confession: add the review (Schaff, Creeds vol. 3).
     - Witsius: Crookshank 1763 accepted as witness.
     - Gill Doctrinal II, 16 or 17 chapters: settle from the BSB
       contents pages; report.
     - Gospel Standard Articles: cite the earliest printing you can
       put a page image to; record the date conflict and which
       articles were added later as a finding. Corporate work of
       the 1870s: PD; say on what basis.
     - Spilsbury: cite the scan; read the TCP licence before using
       its keyed text even for locating.
     - Dort in English with the Rejections: look for Thomas Scott's
       translation (1831) as a PD witness; verify before relying.
     - Huntington: the earliest printing is the witness; later ones
       are second witnesses.
     - Belgic leaf offset: check and record.
A-6. Do NOT put this draw to Chris. A fifth of the crops dropped,
     unevenly by stratum and mostly at the bottom edge, is a biased
     set and would spend the one signer on it. Redraw under a new
     lock with: padding clipped at the midpoint to the neighbouring
     line; the edge check failing only when ink connected to the
     word itself touches the edge, not any ink; and page quotas
     that reallocate a short page's shortfall, stated in the lock.
     Build-a stays on record, unsigned.
A-7. - Measure: correct it under a new lock (v4). Apply every
       candidate shear, zero included, through the same resampling
       so the blur is constant, or normalise the score for it;
       your choice, stated in the lock. T = 0.14 stands as v3's
       measured value.
     - Build hash: yes. Identify images by sha256 and logical name;
       keep absolute paths and run times out of the hashed spec and
       record them in the manifest beside it. Send the text as
       ADR-0006 Revision 5.
C-7 is closed: Chris has answered, and the architect's further
disclosure is on file.
PX4: the page is right; pairs, not distinct Holdings.
```

## Applied

Worked in [REPORT_phase1_20.md](REPORT_phase1_20.md).

- **A-1:** ADR-0002 Revision 3, with 11 annotated axioms (contributor architect, status proposed), ingest check d, and the prototype's "proposed reading, unconfirmed" (`3c6933f`).
- **A-2 and A-3:** ADR-0007 and ADR-0008 ratified, with the answers applied (`3c6933f`). Nothing is built from ADR-0007 yet.
- **A-4:** the architect's own item.
- **A-5:** every item worked in `docs/sources/phase2/`, and `scots.md` added (`2c5e568`). The Gospel Standard page image waits on Chris (C-9).
- **A-6 and A-7 (measure):** lock `italic-v4-predictions-locked.txt`; built in `9028ac1`; runs a and b made. IV1–IV3, IV5 and IV6 hit; IV4 missed (16 of 200 dropped). The console `8e173740c37b714d` is held for the architect (report 20, A-11).
- **A-7 (build hash):** ADR-0006 Revision 5 (`2cc4412`). BH1 missed in its HTML clause only; BH2–BH5 hit.
- **C-7** closed. **PX4** noted.
