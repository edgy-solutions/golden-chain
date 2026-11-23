# Report 26: the ruling on report 24 worked; the foreword ruling applied

- **From:** the build agent, 2026-11-22.
- **On:** [RULING_report_24.md](RULING_report_24.md) (`25d1870`) and [RULING_bsb_foreword_status_2026-11-22.md](RULING_bsb_foreword_status_2026-11-22.md) (`d81b51e`). Report 25 (validity (3) and Gill) went up separately (`024ce18`).
- **In short:**
  - **LBC Holding on (iii) from 7.2:** proposed, for the sitting-2 entails row. It is not put into data now: while the (ii)–(iii) `excludes` edge stands, it would make LBC inconsistent. It goes in with sitting 2, when that edge is retired.
  - **ADR-0003 note** on the refutation check: silence alone does not refute an edge (`fdaf2b0`).
  - **Shared-database guard:** locked as ADR-0001 amendment 1, AY1–AY3 (`30f3c6e`), then built by the implementer and reviewed by me. AY1–AY3 held; suite 813 passed (810 + 3 born).
  - **A-4:** Google refused the 1875 Gadsby fetch with its bot check. Not retried. Chris can download it himself.
  - **Foreword ruling:** status recorded as ruled; propositions 3 and 7 and conclusion 1(a) quoted with pages; the testimony correction recorded. **Console `eb961ddb` still shows the old row**, and a rebuild needs Chris's word.

## Entails check: the LBC Holding on (iii) (proposed)

**What is proposed.** These triples are shown here and on the sitting-2 row. They are not in data.
```
<source/lbc-1689/7/2> a gc:SourceDivision ;
    rdfs:label "LBC 7.2"@en ;
    dcterms:isPartOf <source/lbc-1689> .

<body/lbc-1689> gc:holds <holding/lbc-1689/covenant-of-grace/made-in-time-after-fall> .
<holding/lbc-1689/covenant-of-grace/made-in-time-after-fall> a gc:Holding ;
    gc:position <position/covenant-of-grace/made-in-time-after-fall> ;
    gc:modality <vocab/modality/taught> ;
    dcterms:source <source/lbc-1689/7/2> ;
    gc:status <vocab/status/proposed> ;
    gc:proposedBy <agent/build-agent> .
```
- **The ground.** LBC 7.2, as proposed from Chris's photograph (p. 26; on the LBC 1677 console for him to confirm): "Moreover Man having brought himself under the curse of the Law by his fall, it pleased the Lord to make a Covenant of Grace". This is the timing claim of (iii), after the fall. The modality, taught, follows WCF's Holding on (iii); Chris confirms or corrects it on the row.

**Why it is not in data yet.**
- `data/loci.ttl` still asserts `(ii) gc:excludes (iii)`. LBC holds (ii) as taught (`source/lbc-1689/7/3`).
- Under ADR-0003 Revision 1, `excludes` fires on taught with taught. Adding the Holding now would make LBC inconsistent in the derived graph.
- The ruling on report 23 retires that edge on sitting 2. So the Holding goes in with the same change, after `eb961ddb` is ingested.
- It also waits on two answers from Chris: the 7.2 reading and its page (LBC 1677 console `0a73bb5afa616446`, row `7.2.text`), and the Holding itself (sitting 2).

**On the row.** "Restated (ii) entails (iii)?" now shows, beside the two results of report 24:
- the proposed LBC Holding on (iii), from 7.2, marked proposed;
- the ruling's note that LBC's silence was an artefact of (iii) being worded from WCF;
- with the Holding, LBC holds both (ii) and (iii), so the M6 shape (holds P, nothing on Q) no longer applies to LBC. Coxe still holds nothing on (iii).

**Counts.** With the Holding, the Holdings count and the LBC source divisions each go up by one. The prediction is locked with the sitting-2 build, before the data change.

## ADR-0003: the note on the refutation check

Added after Revision 1 (`fdaf2b0`):
- The E1 reverse was refused because Augsburg baptizes infants on a different ground, not because it is silent on the circumcision covenant.
- Silence alone does not refute an edge.
- Where a Body's silence comes from a Position worded from another Body's text, its own words are read, and a Holding proposed if they state it.
- This answers part of report 24's A-2. The machine check is unchanged. A warning for "holds P, nothing on Q" is not built, since that shape is no longer evidence.

## The shared-database guard (ADR-0001 amendment 1)

The lock is "Verification, amendment 1: the lock" in ADR-0001 (`30f3c6e`), committed before any code.

| Check | Locked | Result |
|---|---|---|
| AY1 | While a process holds the lock, `python -m goldenchain.ingest` on a scratch data copy exits 1 with `DatabaseBusy`, and the database and `gc.trig` are unchanged. | **Held.** `test_ay1_busy_ingest_refused_and_database_untouched` (the test session is the holder). |
| AY2 | Re-entrant in one process; released at the outermost exit; a killed holder does not block. | **Held.** `test_ay2_nested_hold_and_release_on_outermost_exit`, `test_ay2_killed_holder_does_not_block`. |
| AY3 | No existing test file edited; suite 810 + born; weigh byte-identical; ingest alone 0 / 3; no data change. | **Held.** Only `tests/conftest.py` gains the session fixture. Suite **813 passed**. Weigh `71c14a5d187d` / `c8fe9e910b5a`. Ingest 0 violations, 3 warnings. `git diff data/` empty. |

- **What was built.** `goldenchain/dblock.py`: `hold(purpose, path)`, a non-blocking OS lock on byte 0 of `fuseki/run/gc.lock` (msvcrt on Windows, flock elsewhere), re-entrant per process, with a holder sidecar giving pid, purpose and start time. `build_tdb2` and `fuseki.serve` take the hold first and keep their old bodies unchanged as `_build_tdb2` and `_serve`.
- **Built by** the implementer, text-only. I reviewed the diff, normalised line endings to LF, and reran the suite and the ingest myself.
- **Still true.** The suite builds the shared database from its tiny test data, so the real ingest is rerun after a suite run. That is unchanged; the guard only stops the two from overlapping.

## A-4. The 1875 Gadsby printing

Written up in [gospel-standard.md](../sources/phase2/gospel-standard.md), "Ruling on report 24 (A-4)".
- The Books API returned HTTP 429 (daily quota). The full-view PDF link redirected to Google's bot-check page. Neither was retried; nothing was downloaded or viewed.
- **For Chris:** open Google Books `9J6XTR8IeaoC`, download the full-view PDF, and put it in the private corpus. I then view it to propose a witness labelled "Articles 1–31 only".

## A-3, A-5, console size

- A-3 and A-5: accepted; nothing further.
- Console size: no action. Chris tries the LBC 1677 console at full size first.

## The foreword ruling

Filed verbatim and applied (`d81b51e`). Details are in its "Applied" section.
- **Status** recorded as ruled in `data/bsb-gill-1984.ttl` (comment and citation only; weigh unchanged; validation 0 / 3) and in the source docs.
- **Quoted with pages**, transcribed from the page images: proposition 3 (p. vii), proposition 7 (p. viii), conclusion 1(a) (p. xiii). Conclusion 1(a) replaces its paraphrase in report 25.
- **The testimony correction** is recorded in the foreword proposal file and in the handoff. Past reports are not edited.
- **Not done: console `eb961ddb1e582ed6`.** Row `validity-3-testimony` still says "not public domain" and offers the mixed string as "Your words as recorded". Fixing it is a rebuild with a new id. The 23a dispatch said not to rebuild it. The proposed row: propositions 3 and 7 with pages, the status as ruled, and a free-text answer in Chris's own words, with no proposed wording.

## Questions

**For the architect:**
- **A-1.** The foreword's source division is labelled "propositions 1 and 7" (ruling B-Q4). This ruling names 3 and 7 for validity. Should the label become 1, 3 and 7? Not changed.
- **A-2.** Report 25's V-1 and V-2 stand.

**For Chris:**
- **C-1.** Console `eb961ddb`: rebuild it with the corrected testimony row (new id; any answers in progress are lost), or sign it as it is and record your testimony in the row's note?
- **C-2.** The 1875 Gadsby PDF: download it from Google Books into the private corpus, if you want it as a witness.
- **C-3.** Sign the LBC 1677 console `0a73bb5afa616446`.
