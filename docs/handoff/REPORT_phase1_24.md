# Report 24: the ruling on report 23 worked; LBC 1677 console built

- **From:** the build agent, 2026-11-22.
- **On:** [RULING_report_23.md](RULING_report_23.md), filed verbatim with the AX1–AX3 lock (`54c930b`), committed before any code.
- **In short:**
  - **A-3 built:** the correction line now names `corrections@golden-chain.org`. AX1–AX3 held.
  - **A-1 refutation check run** for the new row "restated (ii) entails (iii)?". The machine finds no violation. One Body (LBC) holds (ii) and nothing on (iii), which is the shape a ruling once counted as refuting (M6). Both readings go to Chris.
  - **LBC 1677 console built:** `0a73bb5afa616446`, left for Chris. It has 25 rows (34 fields), including the 1.6 row, the WCF leaf-14 folio, and the 7.2–7.3 readings as proposals for him to confirm.
  - **A-4:** catalogue searches only. Nothing titled to the Societies from before 1970 was reachable. An 1875 Gadsby printing for churches is a candidate witness for Articles 1–31 only.
  - **A-5:** Owen's *Hebrews* (Goold) added to the ADR-0009 inclusion console's list. That console is not built.
  - Nothing minted, no Position changed, no data/*.ttl change. Console `eb961ddb1e582ed6` is still unsigned, so sitting 2 is not built.

## A-3. The correction address (ADR-0007 amendment 3)

The lock is "Verification, amendment 3: the lock" in ADR-0007 (`54c930b`).

| Check | Locked | Result |
|---|---|---|
| AX1 | The line contains `corrections@golden-chain.org` exactly once, no other "@", and no "http". The first sentence is replaced; the second and third are unchanged. | **Held.** New test `test_ax1_correction_line_names_exactly_the_chosen_address`. |
| AX2 | Exactly one existing test is edited (the AW4 assertion), plus one born test. The AV4 test is unedited. | **Held.** Only `test_aw4…` changes its "no @" assertion, and it is marked as edited by amendment 3. |
| AX3 | Weigh byte-identical; ingest 0 violations and 3 warnings; no data change; suite 805 + 1. | **Held.** Weigh `71c14a5d187d` / `c8fe9e910b5a`; ingest 0 / 3; `git diff data/` empty; suite 810 passed: 805 + 1 for AX1, + 4 born with the reading rows (a separate commit). |

- The forwarding target is recorded nowhere, as ruled.

## A-1. Refutation check: "restated (ii) entails (iii)?"

**How it was run.** The edge was tried on a scratch copy of `data/` outside the repo. The copy replaced `(ii) gc:excludes (iii)` with `(ii) gc:entails (iii)`. The in-process reasoner (`ingest.derive_rdflib`, the one `tests/test_real_data.py` uses) then derived the consistency graph. The repo's data was not changed.
- **A process note.** A first attempt ran the full ingest on the scratch copy. Ingest writes to the repo's one shared TDB, and a suite run was going at the same time. The ingest failed on a file lock. That suite run then had 14 failures, all in `test_guard_jena`, which compares the shared TDB with the in-process graph. The real ingest was rerun to restore the TDB, and the suite was rerun alone: 810 passed. Refutation checks are now run in-process only.

**Result, mechanical (the rule in [positions-phase1-draft.md](../loci/positions-phase1-draft.md), "The check, both ways").** SHACL: 0 violations. Consistency graph: **0 triples; no Body is inconsistent.** The rule fires when a Body holds P and Q is forbidden to it. No Body forbids (iii), except through (i) excludes (iii), and Gill, who holds (i), holds nothing on (ii).

**Result, by the M6 precedent (E1(ii), [PLAN_step3_minting.md](PLAN_step3_minting.md) M6).** That direction was refused by ruling because Augsburg held P and **nothing** on Q. The machine cannot see that case. Here the shape is the same:
- **LBC** holds (ii) (taught, `source/lbc-1689/7/3`) and has no Holding on (iii).
- **Coxe** has Arguments for (ii) and no Holding at all.
- **WCF** holds (iii) and nothing on (ii). That does not bear on (ii) → (iii).

**What the sources say on the point (for Chris; no judgment here).**
- **LBC 1677, 7.2** (my proposed reading of Chris's photograph, p. 26; he confirms it on the LBC 1677 console): "Moreover Man having brought himself under the curse of the Law by his fall, it pleased the Lord to make a Covenant of Grace". If confirmed, LBC's own words carry (iii)'s timing claim. The data has no LBC Holding on (iii).
- **Owen**, whose words restated (ii) is assembled from: "after the fall he entered into another covenant with mankind" (vol. 19, p. 78).

**The row for sitting 2.** "Restated (ii) entails (iii)?" Answers: yes, no, or other, as written. Beside it, both results above and the two quotations. **Chris decides.** No entails edge is minted until he does.

## A-1. The other sitting-2 changes (recorded; built with sitting 2)

Sitting 2 is built only after `eb961ddb1e582ed6` is signed and ingested. As ruled:
- **Restated (ii)** is cited to Owen and labelled "assembled from Owen's words". The full sentences from vol. 19, p. 78 are shown beside the label.
- **(iii)** is reworded from WCF 7.3, as proposed in report 23.
- **Edges:** keep (i)–(ii) and (i)–(iii). Retire (ii)–(iii): status rejected with a comment, never deleted. Add the entails row above.
- **Row 6 stands:** do Coxe and LBC 1677 hold (ii), (i), or neither on Q-b? "Does not say" is an allowed answer. The existing LBC Holding on (ii) is **not retired** before Chris answers.
- **The Owen/Gill justification passages** (Gill II.5, p. 203; Owen vol. 19, p. 88) go to the phase-2 justification locus as **related**.
- Recorded against the architect (filed in the dispatch, `54c930b`): "formally established in the new covenant" as Owen's date for the covenant of grace.

## A-2. ADR-0010 revision 2

Marked ratified provisionally for phase 3 (`54c930b`). Open point 6: no number is set now. The minimum is fixed, with its reason, before any count is displayed.

## A-4. Gospel Standard: lead 3 followed

Written up in [gospel-standard.md](../sources/phase2/gospel-standard.md), "Ruling on report 23 (A-4)".
- Jisc returned 403 and WorldCat 429; the BL query returned 400. None was retried.
- Internet Archive has only a 1993 item.
- **Google Books:**
  - *Form of Trust Deed and Articles of Faith for Strict Baptist Churches. Revised* (J. Gadsby, 1875, 20 pp.; full view; BL copy cited). This is a separate printing, but for churches and not by the Societies.
  - The earliest record titled to the Societies is from 1970.
- **Lead 1, read as a lead only, never quoted, never a witness.** It dates Articles 1–31 to Gadsby's printings, in their present form by 1872, and Articles 32–35 to 1878–79. So the 1875 printing is a **candidate witness for 1–31 only**. Viewing it needs Chris's leave.
- Chris may ask the Gospel Standard Society directly.
- **Still no witness of record.**

## A-5. Owen in the inclusion console

Owen, *Hebrews*, Goold vols. 19 and 23, is added to ADR-0009 open point 1 (the backfill console) and to [owen-hebrews.md](../sources/phase2/owen-hebrews.md). It is not built. Until Chris signs, Owen is "not yet considered".

## The LBC 1677 console

- **Reading rows added before the build** (the ruling: "your reading … is a proposal like the others"). There are two rows, `7.2.text` and `7.3.text`. Each shows the proposed reading, the page and a page note. Each asks Chris to confirm or correct both the text and the page.
  - A check refuses a build unless each proposed string occurs verbatim in report 23, so the console cannot show a reading the report does not.
  - The 7.2 page, 26, is inferred: the number is unclear in the photograph, and the next page is 27.
  - Built by the implementer (text-only); I reviewed it and normalised the line endings to LF.
- **Photos:** renamed copies in a local photos directory outside the repo, made as mapped in report 23. The private corpus is unchanged. `ch26_2` and `ch27_1` are the same photograph (byte-identical).
- **WCF leaf 14:** IA `humbleadviceofas00west`, `page/n13.jpg` (2150 × 2695, full size). It was fetched for this build and not viewed. The row's proposed "[6]" is the build agent's earlier reading at 800 px (report 22, C-2), and the row says so.
- **Build:** `0a73bb5afa616446` (template v7). It has 8 sections, 25 rows, 34 fields and 11 images. Built from a clean tree at `d7cd93a`; no commit was made during the build.
  - **Size: the page is 87.7 MB.** For comparison, the WCF 1647 console is 15.2 MB. The spec converts each JPEG to PNG with **no resize**, by design, so Chris reads the photograph's own pixels. I did not change that. If the page is too slow to open, a rebuild with downscaled images is a spec change, and it is proposed only (question A-3).
- A README is beside it for Chris.

## Questions

**For the architect:**
- **A-1.** None new. The sitting-2 rows wait on the eb961ddb ingest.
- **A-2.** The M6 precedent: should "holds P and nothing on Q" keep counting as refuting? If so, should the machine report that case (as a warning, say) so a ruling isn't the only place it shows? This is proposed only.
- **A-3.** Only if Chris finds the LBC 1677 page too slow to open: may the spec downscale the photographs, and to what limit? It would be a new build, and the old one would be superseded.

**For Chris:**
- **C-1.** Sign `eb961ddb1e582ed6`, then sitting 2.
- **C-2.** Sign the LBC 1677 console `0a73bb5afa616446`.
- **C-3.** Whether to view the 1875 Gadsby printing (Google Books, full view), and whether to ask the Gospel Standard Society.
