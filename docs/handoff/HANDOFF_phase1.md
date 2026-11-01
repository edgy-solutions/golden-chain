# Handoff: phase 1 (in flight)

- Branch: `phase-0`, pushed through `e443f71` on 2026-11-01 on the architect's instruction (rulings on reports 9 and 10).
- **The architect's order (report 10):** push (done) → console fix (v2) → re-pin substrate-v1 → A2 fixture → Q11 crops console → OCR of the baptism chapters → plumb-line sitting → ADR cards.
  - **Console v2** (landed): fit-to-window by default, help panel, "other, as written" on every choice, `min_ticks`, template v2. Locked: `console-v2-predictions-locked.txt` (20:03:34Z); C1, C2 and C4 held (318 pass; ingest 0/9; no signed record touched). Checked in headless Chrome on a fixture build: fit, zoom, resize, help, other-text gating, completeness and export. Next: rebuild the plumb-line console from a clean tree (C3: new hash, replacing `0cffbb14`).
  - **Re-pin:** first Chris sends goat-yard [NOTE_goatyard_substrate_v1.md](NOTE_goatyard_substrate_v1.md) (the two corrections). Then lock: all three runs reproduce v0's numbers exactly. Any difference is a finding first. OCR runs on v1 only.
  - **Ruled on report 9, not yet done:** (1) the page head in `gc:secondaryLocator` ("IA humbleadviceofas00west leaf 57, head (49)"), with `gc:asPrinted` holding the lettered note only, and the letter check widened to the WCF style with a test; (2) `gc:clause` on every lettered Argument. (2) is held for report 11: "the transcription" is unnamed. The WCF clause text on file is Schaff via CCEL (permission open) and LBC transcriptions are "never stored", so rule 4 needs a source. The literal needs a way to carry "proposed, unsigned", and the ADR-0005 amendment needs recording.
- Latest report: [REPORT_phase1_10.md](REPORT_phase1_10.md): the empty strips signed; H1 confirmed; the rule runs to the foot, solid (a case the form did not plan for), the strip-screenshot incident. Ruled 2026-11-01 together with report 9 (below).
- **Signed 2026-11-01: empty strips**, build `88d902a181ba64c1`, by Chris: [SIGNED_empty_strips_88d902a181ba64c1.md](SIGNED_empty_strips_88d902a181ba64c1.md). Locked: `empty-strips-signed-88d902a1-predictions-locked.txt` (19:54:25Z); E1–E3 held. Export and signed JSON are read-only beside the manifest.
- **Signed 2026-11-01: WCF 1647 proofs**, build `318910c8f421e2e9`, by Chris: [SIGNED_wcf1647_318910c8f421e2e9.md](SIGNED_wcf1647_318910c8f421e2e9.md). Signed ahead of the empty strips, out of the architect's order; nothing depends on that order.
  - Recorded against `~/.golden-chain/wcf-signed-318910c8-predictions-locked.txt` (17:32:49Z); W1–W4 held. Export, signed JSON and the superseded `24f26ea83e4d6bc2` export are kept read-only beside the manifest.
  - 26 rows: 59 fields confirmed, 1 corrected (28.4 note l: `l Mark 16. 15, 16 Acts 8.37, 38.`; I had proposed `Act;`).
  - Rows l–p were checked by Chris against the whole IA leaf 57, not the console crop: the image box scrolls sideways and, at his window width, hid the right end of the margin notes. The crop files hold the whole margin.
  - Chris's notes: leaf 54's head (56) is a misprint for 46 (agrees with leaf − 8); the 1647 clause text reads "not necessary: but" (28.3), "annexed unto it, as that no person" (28.5 o), "or, that all…" (28.5 p), "moment of time, wherein" (28.6 q); "Gal 3.91,4" is likely 3.9, 14 (agrees with the ruling). On the superseded build only, unsigned: "v skipped on 38".
  - Findings, accepted on report 8: (a) fit each image to the window, with a zoom control: **held** until report 9 Q1, because a template change breaks `code_sha` for the two unsigned builds; (b) "not answered", not "unknown": done in `d476a43`.
  - Recorded in `8ab5c87` (`report8-wcf-ttl-predictions-locked.txt`, 17:57:38Z; T1–T5 held): 20 WCF Arguments, one per signed note; Argument 54, Passage 100. Held: the head, the "leaf − 8" note, the n clause (report 9 Q2–Q3).
- Report 10 ruled: OCR **unheld** (foot hypothesis refuted; "runs to the foot, solid"; no request); the sitting **stands**; help panel and "other, as written" from the next console version; five form defects accepted.
- Waiting on Chris: (1) send the goat-yard note; (2) later, the plumb-line sitting on the rebuilt v2 console (signer Chris). `0cffbb14753c1fa2` is superseded once v2 is built and is never signed. The writer is unblocked (report 8 Q1, `d476a43`): `gc:ratifiedBy agent/chris`, `dcterms:dateAccepted` = signature date.
- Then: the ADR ratification cards.
- Console CLIs: `tools/console/specs/<kind>.py <input> <spec.json>`, then `tools/console/build.py <spec.json> --out-dir DIR` (DIR must exist), then `tools/console/ingest.py <verdicts.json> <manifest.json> [--write]`. Build from a clean tree, or the build is provisional.
- State: data, ontology, shapes, reasoner, Jena ingest and Fuseki are built; counts match the locked predictions; 318 tests pass with `GOLDEN_CHAIN_BIBLES` set (one skips without it); ingest 0 violations, 9 warnings.

## How to rebuild and check

- `.venv/Scripts/python.exe -m pytest -q` (redirect to a log; ~45 s).
- Ingest: `python -m goldenchain.ingest` (needs `GOLDEN_CHAIN_JENA_HOME`, `GOLDEN_CHAIN_FUSEKI_HOME`; Jena 5.6.0 under `~/.golden-chain/jena`).
- Data TTL was first generated by a session-scratchpad script that is **not** in the repo and is now stale (since Q5). Never regenerate from it. The TTL in git is the truth (rule 1): edit `data/*.ttl` directly, then re-run the prediction check.
- A count change: lock the prediction first (a file under `~/.golden-chain/`), then edit, then update `tests/predictions.py` with a comment saying why. Every count is predicted, derived ones included (Q21).

## Rulings in force (beyond the ADRs)

- Phase 1, report 1 rulings (Gill as `body/gill`; 33a/33b split; implication Holdings; E1; cite as printed; locator scheme; CrossWire canon.h; ADR-0005 provisional).
- LBC: witness is the 1677 first printing, facsimile edition 2000; slug `lbc-1689` kept; one Argument per lettered note. Letters for 26.15, 27.1 and 28.2 are stored for phase 2 in [../sources/lbc-1689.md](../sources/lbc-1689.md).
- Report 2 rulings, Q1–Q24 (2026-10-26). Done: Q1–Q9, Q11, Q15, Q20–Q24. Q16: source note and reading form done; strings await the form. Q17–Q19 need no action.
- The Book of Concord is a `gc:Collection`; its members are `dcterms:isPartOf` it, never `childOf` it. The Apology is `childOf` augsburg; the Small Catechism has no parent (ruling on report 4).
- WCF proofs: Edinburgh, Tyler 1647 is the witness of record; London 1647, if found, is a second witness (report 5, Q7). One Argument per lettered note, as for the LBC. The 28.1 admission, regeneration and remission notes become Arguments for the composite 33a Position once read and signed (Q8).
- Rulings on reports 3–5 and ADR-0002 Revision 1 (ratified by both architects; the date convention is at the top of `docs/RULES.md`) applied (report 6). Held: report 4 Q6 (the Gill provenance wording; report 6, Q5).
- Reply to report 6 (frame, last strip, signing strips, console): applied in report 7. Item 1 deleted by the architect (2026-10-26); "Everything else in that block stands, with the console first."
- w3id PR #6977 merged 2026-10-26 (merge commit `8b89818`); the IRI base is live ([../identity.md](../identity.md)). No data change.
- Report 7 rulings (written 2026-10-26, received 2026-11-01), applied in report 8: ADR-0006 ratified provisionally; `body/plumb-line` minted as `gc:Editorial` (one instance, ever, enforced by a shape); Chris signs every plumb-line sitting; WCF page heads as printed, locator = IA leaf, note "leaf − 8 gives N"; spacing convention; 7.6 printed order; "Gal 3.91,4" as printed with Gal 3:9, 3:14 proposed; 28.1 note a is phase 2; local dates from commit `cc32fb0` (RULES.md).
- Rulings on reports 9 and 10 (2026-11-01):
  - **Report 10.** Q1: `foot.stops` reads "no, not faint"; the foot hypothesis is refuted; OCR is unheld; no request; the p. 897 note is a finding. Q2: the sitting stands; every console gets a help panel and an "other, as written" option on each verdict. Q3: all five form defects accepted.
  - **Report 9.** The console fix lands now, with a template bump and the plumb-line console rebuilt. The page head goes in `gc:secondaryLocator`; `gc:asPrinted` holds the lettered note only; the letter check is fixed for the WCF style. `gc:clause` is a pointer, not evidence: a proposed, unsigned literal on every lettered Argument. Both plumb-line writer fixes are accepted. The prediction slips are findings. Agent IRI and the four WCF Holdings: not ruled separately (report 9 Q4–Q5 stand as applied).
  - **Substrate-v1.** Send goat-yard the two corrections, then re-pin as a locked step.
- Bible text: none stored or fetched. The USFM Bibles are read by `GOLDEN_CHAIN_BIBLES` only ([../sources/bibles-usfm.md](../sources/bibles-usfm.md)). ADR-0004 will name the USFM KJV as the display text source.

## goat-yard (lane G)

- Terms, additions and responses are verbatim in [../sources/goat-yard.md](../sources/goat-yard.md).
- Pinned: worktree `../goatyard-substrate-v0` at tag `substrate-v0` (3d0b03e0), installed with `pip install -e --no-deps`. Tool: `tools/gy_locate_column_rule.py`.
- `locate_column_rule` (2026-10-26, UTC). The native run PASSES goat-yard's criteria, 20/20, but was "made at the wrong scale"; its "every strip" clause is FALSIFIED and is never edited. Reruns at 7.2 and at the architect's 0.703 frame both pass 20/20, and were rerun **clean** at `d32f888`. **The line-height-matched frame governs** (ruling on report 6): scale 6.947, median 55, clean at `6a7c5d1`, L1–L6 held. The strips to sign are cut from it.
- Run headers record golden-chain `git_start` / `git_end` / `clean_run`. A run is citable only if it is clean: commit first, then run.
- **OCR is UNHELD** (ruling on report 10, Q1). Chris signed the 6.947 strips on 2026-11-01. OCR work begins on substrate-v1 once the re-pin is clean. The A2 fixture comes after the re-pin. Finding for the OCR column split: on p. 897 the rule divides the footnote ([../sources/gill-column-rule.md](../sources/gill-column-rule.md)).
- Addition 1: any 1766 Exposition page is cited by goat-yard FILE page number with the line "printed = file − 88". None cited yet.
- No interface requests filed.

## Remember (not phase 1)

- The BSB 1984 foreword is a Body ("Strict Baptist, BSB 1984"), `childOf` Gill with overrides on Practical III.1, II.6 (locus 26) and Doctrinal VII.8 (locus 42). The front-matter exclusion vs. a Body's Source must be ruled before it is modelled.
- The Q5 locus (rebaptism) is where the foreword's "no baptism, no church" lands later.
- **33c, the Gill/LBC Position** ("infant baptism is no baptism"), blocked correctly in phase 1 (architect, report 5). It comes in phase 2 from Gill's *The Divine Right of Infant Baptism Examined and Disproved* (PD), which argues it with proofs. That is a new phase-2 source: a source report first (rule 4).
- **Phase-2 candidates for that Position**, in the architect's order (report 5, Q3); read neither until then:
  1. Gill, *The Divine Right of Infant Baptism Examined and Disproved*;
  2. Gill, *Exposition* at Acts 19:5, in goat-yard's corpus, cited by its region IRI.
- LBC 26 is phase 2.
