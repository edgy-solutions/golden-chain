# Handoff: phase 1 (in flight)

- Branch: `phase-0`, pushed through report 14's commit on 2026-11-14 (after `9a5a955`). The architect says "Push as you go".
- **Now (2026-11-22): eb961ddb ingested; ruling on report 26 worked** ([REPORT_phase1_27.md](REPORT_phase1_27.md); [RULING_report_26.md](RULING_report_26.md); lock [LOCK_ingest_eb961ddb_2026-11-22.md](LOCK_ingest_eb961ddb_2026-11-22.md), `8ac7e41`).
  - Record 0002 (`--code-at 9836117`, the "(1).json" export). 8 plumb-line Holdings (21 in all); tier and clarity on covenant-of-grace (second / contested), circumcision-covenant and baptism-validity (second / settled); 3 unchurches flags, the first in data. Ingest 0 violations, **0 warnings**. Counts: Holding 62, effectivelyHolds 63, Axiom 38.
  - **Weigh now excludes WCF, the Apology and Augsburg** ("Not a church by this plumb-line's standard"). Hashes: members `13209f4b689f`, officers `590965a0a299`. E9 and E10 missed (a wall was predicted; 8 tests pinned to the data before the sitting, amended and disclosed). Two weigh defects, fixes proposed (A-1), not built: `unchurches.flag_source` reports the Holding's sitting, not the flag's; `unchurches.excluded` picks one of a Holding's sources at random, so the weigh hash is not stable (WCF administration-of-grace: 7.5 or 28.4).
    - *Note, 2026-11-22 (ruling on report 27): the two hashes in this entry are **not verifiable as stated**; each is one of two values the output took, by hash seed. Stable since weigh fix 2 (`395f3ef`): members `46381316eb30`, officers `91bfab215992`. Not rewritten.*
  - Audit beside the signed record: [AUDIT_plumb_line_followup_eb961ddb1e582ed6.md](AUDIT_plumb_line_followup_eb961ddb1e582ed6.md) (the testimony row's defect; the LBC 7.3 confirmations made with no image, so the LBC 1677 console governs).
  - Ruling 2: propositions **1 and 7** are the source for (3); proposition 3 is quoted only for the recursion (lee-bsb.md, the foreword proposal's corrections).
  - 1875 Gadsby PDF placed by Chris (private corpus, `gospel-standard/`); viewed; Articles I–XXXI on pp. 8–15 (printed = PDF − 3); witness proposed.
  - **Next:** sitting 2 (23a under B, (iii) reworded, the entails row with the LBC 7.2 Holding, validity (2) relabelled, the administrator question and (b) from Gill's words); Batch C on F-B = (b); the 7.3-margins question on the LBC 1677 follow-up.
- **Before it (2026-11-22): validity (3) and Gill researched** ([REPORT_phase1_25.md](REPORT_phase1_25.md); [DISPATCH_validity3_gill_2026-11-22.md](DISPATCH_validity3_gill_2026-11-22.md); lock `c30b99c`).
  - **Proposed (B):** Gill's view is a distinct Position. His essentials are immersion and a profession of faith; a baptized, called administrator is the ordinary rule but "not essential to the Ordinance" (DR 1749, p. 14). "Not a church ordinance" means before and in order to membership (III.1, p. 896). (C) fits his ordinary rule only. Q4: does not say. Sitting-2 rows V1–V4 in the report.
  - Tracts: 8 located with IA witnesses, twelve not confirmed; DR 1749 ch. II, the Reply pp. iii–14 and the 1765 sermon read.
  - **Foreword ruling filed and applied** ([RULING_bsb_foreword_status_2026-11-22.md](RULING_bsb_foreword_status_2026-11-22.md)): status recorded as ruled (data comment and citation, source docs); propositions 3 and 7 and conclusion 1(a) quoted with pages; the testimony correction recorded. **Console `eb961ddb` still shows the old row** ("not public domain", the mixed testimony as "your words"); rebuild waits on Chris (the 23a dispatch said not to rebuild it).
  - **Ruling on report 24 worked** ([REPORT_phase1_26.md](REPORT_phase1_26.md)): LBC Holding on (iii) from 7.2 proposed, to go into data with sitting 2 (with the (ii)–(iii) retirement); ADR-0003 note (`fdaf2b0`); shared-database guard (ADR-0001 am. 1, `30f3c6e`; `goldenchain/dblock.py`): a second process gets `DatabaseBusy` while the suite or an ingest holds `fuseki/run/gc.lock`. Suite 813. Gadsby 1875: Google bot check, not retried.
  - **Waiting on Chris:** rebuild `eb961ddb` with the corrected testimony row, or sign as is; download the Gadsby 1875 PDF if wanted; sign LBC 1677 `0a73bb5afa616446`.
  - **Waiting on the architect:** report 25's V-1 and V-2.
- **Before it (2026-11-22): ruling on report 23 worked; LBC 1677 console built** ([REPORT_phase1_24.md](REPORT_phase1_24.md); [RULING_report_23.md](RULING_report_23.md)).
  - Commits: `54c930b` (ruling filed; AX1–AX3 locked); `456b396` (A-3 built: correction line names `corrections@golden-chain.org`); `c737db9` (7.2/7.3 reading rows); `d7cd93a` (A-4, A-5 docs); the report-24 commit.
  - **Refutation check for "(ii) entails (iii)?":** mechanically clean. LBC holds (ii) and nothing on (iii), which is the M6 shape. Both readings go on the sitting-2 row; Chris decides. Run refutation checks **in-process only** (`ingest.derive_rdflib` on a scratch `GOLDEN_CHAIN_DATA`). Ingest writes to the one shared TDB, and a concurrent run breaks `test_guard_jena`.
  - **LBC 1677 console `0a73bb5afa616446`** is in `~/.golden-chain/console/lbc1677/` with README_SIGN.txt: 25 rows, 34 fields, 87.7 MB (photos not resized, by design). The photos dir is `~/.golden-chain/console/lbc1677-photos/`.
  - Sitting 2 (proposal B rows, restated (ii) with Owen p. 78 beside it, (iii) from WCF 7.3, edges, the entails row, row 6) is built after the eb961ddb ingest. Then the R3 Q3 lock, then the ADR-0009 inclusion console (now with Owen).
  - Suite 810 passed. Ingest 0 violations, 3 warnings. Weigh unchanged.
  - **Waiting on the architect:** report 24's A-2 (M6 as a machine warning?) and A-3 (downscale only if the page is too slow).
  - **Waiting on Chris:** sign `eb961ddb1e582ed6`; sign LBC 1677 `0a73bb5afa616446`; whether to view the 1875 Gadsby printing, and whether to ask the GS Society.
- **Before it (2026-11-22): dispatch 23a researched; ruling on report 22 worked** ([REPORT_phase1_23.md](REPORT_phase1_23.md); [DISPATCH_23a_2026-11-22.md](DISPATCH_23a_2026-11-22.md); [RULING_report_22.md](RULING_report_22.md)).
  - Commits: `55272ce` (dispatch, ruling and lock filed); the report-23 commit (research, ADR edits, console spec rows).
  - **Proposed for 23a: B, KEEP, RESTATED.** Owen states two covenants (vol. 19, p. 78); Gill rejects two by name (II.7, p. 217). (iii) reworded from WCF 7.3; the (ii)–(iii) edge to retire. Sitting 2 is built only after eb961ddb is ingested and the architect rules.
  - ADR-0003 R3 and ADR-0009 ratified, not built. The R3 Q3 replay-writer migration gets its own expected-diff lock after the eb961ddb ingest. ADR-0010 revision 2 resent.
  - The LBC 1677 console spec has rows `1.6.locate` and `wcf1647.leaf14.folio`. The console is not built: Chris's photographs (in the private corpus, `lbc-1677/`) need renamed local copies (mapping in report 23), plus the IA leaf-14 page.
  - Correction contact chosen: `corrections@golden-chain.org`. Not yet on the C6' line (AW4 forbids "@"; waits on a ruling).
  - Suite 805 passed. Ingest 3 warnings. Weigh unchanged.
  - **Waiting on the architect:** report 23's A-1 to A-5.
  - **Truth set v4 signed and ingested** ([SIGNED_truthset_italic_v4_8e173740c37b714d.md](SIGNED_truthset_italic_v4_8e173740c37b714d.md); `--code-at 9028ac1`). IV7 held (70/75 = 93.3 %), IV8 held (71/71); edge 38 roman.
  - **Waiting on Chris:** sign `eb961ddb1e582ed6` (then ingest it); go-ahead for the LBC 1677 console.
- **Before it (2026-11-22): ruling on report 21 worked; site's-ground drafts sent up** ([REPORT_phase1_22.md](REPORT_phase1_22.md); [RULING_report_21.md](RULING_report_21.md); [RULING_site_ground_2026-11-22.md](RULING_site_ground_2026-11-22.md)).
  - Commits:
    - `18f4de3` (C-9, vol. 43: no witness);
    - `a44dd6e` (ADR-0007 amendment 2 locked; both rulings filed);
    - `ab0fb49` (v4 population statement; README SIGN);
    - `a271f90` (four drafts: ADR-0003 R3, ADR-0009, warrant row 10, ADR-0010; nothing built);
    - `77a62a1` (amendment 2 built: AW1–AW4 held; AW5 missed on its edit list).
  - Suite 800 passed. Ingest 3 warnings. Weigh is unchanged (`71c14a5d187d` and `c8fe9e910b5a`).
  - **Waiting on the architect:**
    - the four drafts;
    - "the three gates" (undefined);
    - the R3 Q1–Q4;
    - the ADR-0009 open points;
    - the ADR-0010 private store;
    - the Gospel Standard route;
    - the R6 text.
  - **Waiting on Chris:**
    - sign v4 build-a `8e173740c37b714d`;
    - check the WCF leaf 14 folio "[6]";
    - a correction address;
    - a photograph of the LBC 1677 page for 1.6;
    - C-2, C-3?, C-4, C-6 and C-8;
    - the follow-up `eb961ddb1e582ed6`.
- **Before it (2026-11-22): ruling on report 20 worked** ([REPORT_phase1_21.md](REPORT_phase1_21.md); [RULING_report_20.md](RULING_report_20.md)).
  - Commits: `1a7d746` (ruling filed), `5285db3` (A-12 born test; ADR-0006 R6 ratified provisionally, A-8), `610471e` (ADR-0007 Verification locked before code), `56004c5` (truth-set v5 draw with replacement and ceiling; crops v5; console kind truthset-italic-v5; tall-box measure), `07682a5` (ADR-0007 build, A-9: AV1 to AV8 held, synthetic only, no real Congregation minted).
  - **Italic v5:**
    - The lock is `italic-v5-predictions-locked.txt`.
    - **The ceiling tripped on slanted** (9 of 80 first choices failed; the limit is 8), so nothing was replaced, cropped or built.
    - Edge is nearly exhausted: 7 words left after the v2 to v4 exclusions, so n is 167.
    - V1, V3 and V4 (edge) missed.
    - v4 build-a `8e173740c37b714d` stays on record, unsigned.
  - **Tall-box measure:**
    - The lock is `tallbox-bands-predictions-locked.txt`.
    - 0 of 10 show two bands, so TB2 missed. The control is 0 of 174.
    - It does not support the merged-lines reading. Those 10 and the 6 with the full 12 px stay open, with no cause recorded.
  - **A-10:** the architect's reading is not an authority. The phase-2 locators stay proposals until a Position needs one. Then the build agent reads the page and proposes, and Chris signs.
  - A-5 is accepted. BH1 is recorded as missed (the lock's clause was wrong, not the build).
  - **C-1 is signed (2026-11-22):** the p. 914 re-ask `d7a6aab0734ffe3e` answered **yes**, column footnotes ([record](SIGNED_region_reask_d7a6aab0734ffe3e.md)). F-1 is confirmed from pixels for that one column. Chris's note says the boundary y = 6127 starts one footnote line low (not measured).
  - **C-9 is worked** (`ce2af7c`, [gospel-standard.md](../sources/phase2/gospel-standard.md)). None of vols. 38, 44 and 45 indexes the Articles, and vol. 45's scan lacks pp. 293–400. The 1879 notice on p. 292 says the Societies had Articles by October 1877. Still no witness of record.
  - **Waiting on Chris:** C-2, C-3 (if not yet done), C-4, C-6 and C-8; vol. 43 (1877) into the private corpus (the new C-9); and the follow-up `eb961ddb1e582ed6`. There is nothing new to sign.
  - **Waiting on the architect:**
    - A-4;
    - the italic truth set after the ceiling (report 21 recommends signing v4 build-a);
    - the ADR-0007 questions C2, C4, C6 and C7-L6;
    - the p. 914 boundary (re-measure under a lock?);
    - the R6 text.
- **Before it (2026-11-17): ruling on report 19 worked** ([REPORT_phase1_20.md](REPORT_phase1_20.md); [RULING_report_19.md](RULING_report_19.md)).
  - Commits: `3c6933f` (A-1 asPrinted axioms, ADR-0002 R3; ADR-0007 and ADR-0008 ratified), `2cc4412` (ADR-0006 R5, build hash by name and sha256, manifest /2, TEMPLATE_VERSION 7), `2c5e568` (A-5 sources, scots.md), `9028ac1` (italic v4 measure, draw and crops; ADR-0006 R6 word-connected edge, proposed).
  - Italic v4: lock `italic-v4-predictions-locked.txt`; T 0.11, the comb gone, n 200 after reallocation, one build hash `8e173740c37b714d` from runs a and b; **IV4 missed** (16 of 200 dropped). The console is **on hold** (README says HOLD) until the architect answers A-11.
  - Italic v3 build-a `015bfeed482a5083` stays on record, unsigned (never sign it).
  - **Waiting on Chris:** C-1, C-2, C-3 (if not yet done), C-4, C-6, C-8 and C-9 (the Gospel Standard volumes).
  - **Waiting on the architect:** A-4, and A-8 to A-12.
- **Before it (2026-11-15, overnight order): all seven items worked** ([REPORT_phase1_19.md](REPORT_phase1_19.md); [ORDER_overnight_2026-11-15.md](ORDER_overnight_2026-11-15.md); [RULING_report_18.md](RULING_report_18.md)). Commits `4b53ccc` (further disclosure; LBC asPrinted model-proposed), `25b7d3e` (plain words, ADR-0006 R4, TEMPLATE_VERSION 6), `8d4de2f` (phase-2 source reviews, PROPOSAL_phase2_loci.md, examine/try prototype, ADR-0008 proposed), `e380d33` (LBC 1677 console builder), `5cd7918` (italic v3). **Waiting on Chris:** C-1 to C-8 in report 19 (sign the re-ask, the follow-up, the italic v3 console build-a `015bfeed482a5083`; LBC 1677 photographs into the private corpus). **Waiting on the architect:** A-1 to A-7 (typed model-proposed property; ADR-0007; ADR-0008; the locus table; source gaps; italic v3 draw drops 19.4 % and the FM2 dip; build hash without paths). Italic v3 lock: FM1-FM5 missed in part, FM6 hit, FM7-FM8 after signing.
- **Before it (2026-11-15): ruling on report 17 worked** ([REPORT_phase1_18.md](REPORT_phase1_18.md); [RULING_report_17.md](RULING_report_17.md)). The architect disclosed that it viewed the Q11 crops and w017 before signing: Q11 rows are **model-proposed, signed by Chris**; w017 is out of every denominator; clip-noted rows are out of the measure's precision (audits beside both records). **RULES.md rule 11:** no one reads a crop for the signer during a sitting; answer from the form's text. ADR-0006 R2 ratified, R3 (clear edges) ruled. Waiting on the architect: report 18 Q-1 (the finer measure, proposed; lock after ratification) and Q-2 (plain-words help as a build check). Waiting on Chris: report 18 Q-3 (any other row shown to a model?). Before it: Q11 signed and ingested; the p. 914 foot is a crop fault ([REPORT_phase1_17.md](REPORT_phase1_17.md)). The truth-set p. 914 row's "no" is not usable ([audit standoff](AUDIT_truthset_italic_8afafecd34665b14.md)); report 16's Q-1 is superseded; F-1 stands from numbers, unconfirmed from pixels. New build check: a region question must show its surroundings (ADR-0006 Revision 2, **proposed**). Waiting on the architect: report 17 Q-1 (clipped crops in the score), Q-2 (italic measure). **Waiting on Chris:** the p. 914 re-ask `d7a6aab0734ffe3e`, the follow-up, and report 17 Q-3 (the p. 915 note). Consoles built before `11a905f` ingest with `--code-at <manifest's git start>` (`785d7d6`). Before it: truth-set v2 signed ([REPORT_phase1_16.md](REPORT_phase1_16.md); SI3, SI8 missed). [RULING_report_15.md](RULING_report_15.md) is filed: Batch C mints **variant N** (one Argument per note of one division: 117 if F-B = (b); if F-B = (a), only the Locus, (a) and its 113 Arguments, then stop). Apology IX and the truth-set console are accepted. Before it: [RULING_report_14.md](RULING_report_14.md) worked in [REPORT_phase1_15.md](REPORT_phase1_15.md): console v4 (`961ad68`), Apology IX (`37724cf`; weigh members `71c14a5d187d`, officers `c8fe9e910b5a`), truth-set console template v5 (`1f5e8a0`). Batch C lock: `step3-batchC-predictions-locked.txt`, held. Local runs: `truthset-console-2026-11-14-{a,b}`. `data/plumb-line.ttl` is a replay product (ADR-0006 R1): never hand-edit it; a later sitting merges through `tools/console/ingest.py`.
- **The architect's order (dispatch 2026-11-08 §15; [DISPATCH_architect_2026-11-08.md](DISPATCH_architect_2026-11-08.md), with its §4 addendum):** (1) ingest the signed plumb-line sitting as is and record the console defect: **done**; (2) draft ADR-0003 Revision 2 (tier §2, modality §3, unchurches §4 with the addendum, instrumentality §8), proposed, then **stop and report**: **ratified 2026-11-08** with the R2.6 answers ([RULING_report_11.md](RULING_report_11.md)). Chris confirmed the Augsburg/Apology exclusion and that tolerated triggers; (3) mint 23a/23b, the repetition position, the validity locus and the instrumentality locus, with proofs and locked counts, all proposed. Rulings for it ([RULING_report_11.md](RULING_report_11.md)): retire the fused covenant Locus (keep its IRI, `dcterms:isReplacedBy` 23a and 23b, out of scoring); its signed tier (second) carries to 23a and 23b as proposed values; E1 is retired with it and re-examined in both directions, with the refutation check locked ((i) 23b-yes → believers-and-their-infants survives; (ii) the reverse is refuted by Augsburg); instrumentality (b) is "representational ONLY", with an `excludes` edge to (a) carrying its note; tier warnings 0 → 4 are expected; (4) console v3 and the follow-up sitting (Chris signs); (5) ingest, then the first real `weigh` of the plumb-line against Gill, WCF, LBC and Augsburg, then **stop and report**. Weigh is built here from ADR-0003 as the spec, with the three R2.3 cases as its first tests and their renderings locked before the code exists; (6) standing items: the Q11 crops console, then OCR of the baptism chapters on v1 with the italic-flag baseline. The lone-narrow-glyph measurement on pp. 896–915 comes before OCR: lock a count first, then measure from pixels in code. Predict counts before every step.
  - **Step 3 sources (Chris chose "add the PD sources now"; the architect's order, relayed 2026-11-08):**
    - **First, the four that unblock phase-1 Positions:** Coxe 1681; Gill, *Divine Right of Infant Baptism*; Booth, *Paedobaptism Examined*; Graves, *Old Landmarkism* 1880. **Reviewed 2026-11-08:** [coxe-covenants](../sources/coxe-covenants.md), [gill-divine-right](../sources/gill-divine-right.md), [booth-paedobaptism-examined](../sources/booth-paedobaptism-examined.md), [graves-old-landmarkism](../sources/graves-old-landmarkism.md).
    - **Then** Heidelberg and Belgic (instrumentality (a), significance). **Reviewed 2026-11-08:** [heidelberg-belgic](../sources/heidelberg-belgic.md).
    - **Then** Hodge and Thornwell (validity position 1). **Reviewed 2026-11-08:** [hodge-thornwell](../sources/hodge-thornwell.md).
    - **BSB foreword, ruled 2026-11-08:** it holds validity (3) and is cited for it, pp. vii–viii, props. 1 and 7. Chris's testimony (Lee followed Gill and Spilsbury on the administrator; a church may be gathered de novo) is recorded as testimony, not as the source ([PROPOSAL_validity_bsb_foreword.md](PROPOSAL_validity_bsb_foreword.md)). *Corrected 2026-11-22 ([RULING_bsb_foreword_status_2026-11-22.md](RULING_bsb_foreword_status_2026-11-22.md)): that record mixed Chris's words with the architect's; the Spilsbury and succession details were the architect's. Chris's own words are those he signs on row `validity-3-testimony`.* The §12 rule is in [../sources/lee-bsb.md](../sources/lee-bsb.md).
    - **Minting plan:** [PLAN_step3_minting.md](PLAN_step3_minting.md), with Batches A, B and C and questions M1–M11 for the architect.
      - **Batch A done (`00e7a8e`):** 23a/23b and five Positions minted, 23 retired (owl:deprecated), E1 moved, 16 Arguments, 3 Holdings; console spec skips deprecated loci. Lock `step3-batchA-predictions-locked.txt` (2026-11-09T02:36:51Z), A1–A6 held: pytest 357 pass; ingest 0 violations, 2 warnings (tier on 23a, 23b).
      - **Ruling on M1–M11 and F-A/F-B:** filed verbatim, [RULING_step3_plan.md](RULING_step3_plan.md).
      - **Batch A′ done (`1093740`):** F-A, M3 (ADR-0002 Revision 2, proposed; ingest check d), M5 (`gc:Teacher`; Gill on 23b-no), M6 (rejected axiom), M8, M9, M10, M11. Lock `step3-batchA2-predictions-locked.txt` (03:36:32Z), P1–P6 held: pytest 380; ingest 0/2.
      - **Batch B stopped under rule 8** on [REPORT_phase1_12.md](REPORT_phase1_12.md) B-Q1–B-Q5: (2) and repetition have no source that holds them and prints Scripture; Gill III.1's administrator paragraph (checked, Tegg ii. 621–622) reads against (3)'s clause; how the foreword is linked; two sittings. Validity (1) is deferred to phase 2: Hodge ST3 §6 prints no Scripture. (4) is ready (Graves p. 124).
      - **Batch C** waits on Chris's F-B answer (follow-up console).
    - **Step-3 findings for the next report** (against the architect, §14 style; none acted on):
      1. Gill does speak of one covenant "administered" under both testaments (the dispatch's own finding, to record).
      2. Acts 19:5: Gill reads vv. 4–5 as Paul's words, not Luke's report. The dispatch has the speaker wrong and the conclusion right ([gill-divine-right](../sources/gill-divine-right.md)).
      3. 23a(ii)'s wording outruns Coxe; a closer label is proposed ([coxe-covenants](../sources/coxe-covenants.md)).
      4. Coxe's "dual-aspect reading of Gen 17" is the architect's paraphrase; Coxe's term is a covenant of peculiarity.
      5. Hodge's *Systematic Theology* does not name Rome. The verdict is in the 1845 Princeton Review article, whose Hodge authorship is attributed, not printed ([hodge-thornwell](../sources/hodge-thornwell.md)).
      6. Validity (1), "subject and formula suffice", omits the administrator that both the 1845 article and WCF 28.2 require.
      7. Schaff's Heidelberg prints no proofs, so 23b-yes from Q.74 needs Passages from elsewhere ([heidelberg-belgic](../sources/heidelberg-belgic.md)).
    - **Each review gives:** the edition, a public-domain check, the scan location and the proposed locators. No text is stored.
    - **Minting:** Positions are minted as their sources land, with counts locked per batch.
    - **The follow-up console goes out only when every step-3 Position is minted.**
    - Viewing PD page images online to propose locators is within the rules (report 3 Q1; report 6 Q4). Subagents stay text-only.
  - **A2 fixture: done 2026-11-08.** F4 and F7 missed on the first lock (fixture defects); re-locked as v2 and all predictions held ([../sources/goat-yard.md](../sources/goat-yard.md), the fixture row). [NOTE_goatyard_single_rule_fixture.md](NOTE_goatyard_single_rule_fixture.md) offers it to A2; Chris sends it.
  - **Console v2** (landed): fit-to-window by default, help panel, "other, as written" on every choice, `min_ticks`, template v2. Locked: `console-v2-predictions-locked.txt` (20:03:34Z); C1, C2 and C4 held (318 pass; ingest 0/9; no signed record touched). Checked in headless Chrome on a fixture build: fit, zoom, resize, help, other-text gating, completeness and export. Committed `a6755dc`. Plumb-line console rebuilt clean from `a6755dc`: build **`7b23646b2c763ae0`** (C3 held), `~/.golden-chain/console/plumb-line/`. It replaces `0cffbb14`, which is never signed.
  - **Re-pin: done 2026-11-01** at `e4b1435`. Lock `substrate-v1-repin-predictions-locked.txt` (20:51:20Z), V1–V5 held: the three runs reproduce v0 exactly ([../sources/gill-column-rule.md](../sources/gill-column-rule.md)). Correction (1) to goat-yard was withdrawn (architect); (2) stands and was accepted. [NOTE_goatyard_substrate_v1.md](NOTE_goatyard_substrate_v1.md) now carries (2) only and promises goat-yard the result. Chris sends it when convenient; nothing waits on it.
  - **Ruled on report 9, not yet done:** (1) the page head in `gc:secondaryLocator` ("IA humbleadviceofas00west leaf 57, head (49)"), with `gc:asPrinted` holding the lettered note only, and the letter check widened to the WCF style with a test; (2) `gc:clause` on every lettered Argument. (2) is held for report 11: "the transcription" is unnamed. The WCF clause text on file is Schaff via CCEL (permission open) and LBC transcriptions are "never stored", so rule 4 needs a source. The literal needs a way to carry "proposed, unsigned", and the ADR-0005 amendment needs recording.
- **The overnight order of 2026-11-12** ([ORDER_overnight_2026-11-12.md](ORDER_overnight_2026-11-12.md)): all eight items have been worked. The report is [REPORT_phase1_13.md](REPORT_phase1_13.md).
  - **Commits:** `d704ef7` (Batch B), `15abf36` (console v3 and the follow-up), `8992b8b` (unchurches), `1589f32` (weigh), `2bf1461` (narrow glyph), `a80e076` (OCR tool and the ADR-0006 R1 proposal), `3845d50` (Batch C prep), `dbf592c` (Q11 console).
  - **Misses:** B8, C1, N2–N5, O3, O4. Item 7 had no lock.
  - **Open:** 17 items in one list, 1–5 for Chris and 6–17 for the architect.
  - **Consoles waiting for Chris:** the p. 914 re-ask **`d7a6aab0734ffe3e`** (`~/.golden-chain/console/region-reask/build1/`) and the follow-up **`eb961ddb1e582ed6`** (v4; ingest with `--code-at`; `c89256e734a61e4f` is superseded, never sign it). Signed 2026-11-15: truth-set `8afafecd34665b14` ([record](SIGNED_truthset_italic_8afafecd34665b14.md), [audit](AUDIT_truthset_italic_8afafecd34665b14.md)) and Q11 `58b603f5500ae2a8` ([record](SIGNED_q11_crops_58b603f5500ae2a8.md)).
  - **OCR runs (local):** `~/.golden-chain/ocr-baptism-run{1,2}-2026-11-13`; the 200 truth-set candidates are unsigned.
  - **Batch C** waits on F-B. Its proofs are verified in [heidelberg-belgic](../sources/heidelberg-belgic.md).
- Previous report: [REPORT_phase1_12.md](REPORT_phase1_12.md): Batch A′ minted; Batch B questions B-Q1–B-Q5. Previous: [REPORT_phase1_11.md](REPORT_phase1_11.md): the plumb-line sitting ingested; ADR-0003 Revision 2 proposed, with six open points; the Augsburg/Apology reach of `unchurches` for Chris; step 3 flags (E1 direction, the fused Locus after the split, tier warnings 0 → 4, the BSB foreword, weigh not yet built).
- **Signed 2026-11-08: plumb-line**, build `7b23646b2c763ae0`, by Chris: [SIGNED_plumb_line_7b23646b2c763ae0.md](SIGNED_plumb_line_7b23646b2c763ae0.md), instance [data/plumb-line.ttl](../../data/plumb-line.ttl). Ingested as is: the null modality on johns-baptism.same-ordinance is silence (console v2 defect, fixed in v3; ingest.py applies the ruling meanwhile). Locked `plumb-line-signed-7b23646b-predictions-locked.txt` (20:32:20Z); P1–P5 held; P6 missed on the first run (328 pass, 2 fail; a test-fixture collision), 330 after the fix. All nine tier warnings are cleared; no Inconsistency.
- **Signed 2026-11-01: empty strips**, build `88d902a181ba64c1`, by Chris: [SIGNED_empty_strips_88d902a181ba64c1.md](SIGNED_empty_strips_88d902a181ba64c1.md). Locked: `empty-strips-signed-88d902a1-predictions-locked.txt` (19:54:25Z); E1–E3 held. Export and signed JSON are read-only beside the manifest.
- **Signed 2026-11-01: WCF 1647 proofs**, build `318910c8f421e2e9`, by Chris: [SIGNED_wcf1647_318910c8f421e2e9.md](SIGNED_wcf1647_318910c8f421e2e9.md). Signed ahead of the empty strips, out of the architect's order; nothing depends on that order.
  - Recorded against `~/.golden-chain/wcf-signed-318910c8-predictions-locked.txt` (17:32:49Z); W1–W4 held. Export, signed JSON and the superseded `24f26ea83e4d6bc2` export are kept read-only beside the manifest.
  - 26 rows: 59 fields confirmed, 1 corrected (28.4 note l: `l Mark 16. 15, 16 Acts 8.37, 38.`; I had proposed `Act;`).
  - Rows l–p were checked by Chris against the whole IA leaf 57, not the console crop: the image box scrolls sideways and, at his window width, hid the right end of the margin notes. The crop files hold the whole margin.
  - Chris's notes: leaf 54's head (56) is a misprint for 46 (agrees with leaf − 8); the 1647 clause text reads "not necessary: but" (28.3), "annexed unto it, as that no person" (28.5 o), "or, that all…" (28.5 p), "moment of time, wherein" (28.6 q); "Gal 3.91,4" is likely 3.9, 14 (agrees with the ruling). On the superseded build only, unsigned: "v skipped on 38".
  - Findings, accepted on report 8: (a) fit each image to the window, with a zoom control: **held** until report 9 Q1, because a template change breaks `code_sha` for the two unsigned builds; (b) "not answered", not "unknown": done in `d476a43`.
  - Recorded in `8ab5c87` (`report8-wcf-ttl-predictions-locked.txt`, 17:57:38Z; T1–T5 held): 20 WCF Arguments, one per signed note; Argument 54, Passage 100. Held: the head, the "leaf − 8" note, the n clause (report 9 Q2–Q3).
- Report 10 ruled: OCR **unheld** (foot hypothesis refuted; "runs to the foot, solid"; no request); the sitting **stands**; help panel and "other, as written" from the next console version; five form defects accepted.
- Waiting on Chris: (1) send both goat-yard notes (substrate-v1 and the single-rule fixture); the fixture is on origin. The fixture note's paragraph on lone narrow glyphs becomes a measurement (the architect's item 2), so amend it before it is sent, once the count is in; (2) read §4 of ADR-0003 Revision 2 when it is drafted.
- Then: the ADR ratification cards.
- Console CLIs: `tools/console/specs/<kind>.py <input> <spec.json>`, then `tools/console/build.py <spec.json> --out-dir DIR` (DIR must exist), then `tools/console/ingest.py <verdicts.json> <manifest.json> [--write]`. Build from a clean tree, or the build is provisional.
- State: data, ontology, shapes, reasoner, Jena ingest and Fuseki are built; counts match the locked predictions; 318 tests pass with `GOLDEN_CHAIN_BIBLES` set (one skips without it); ingest 0 violations, 9 warnings.

## Observations recorded (not data)

- **Chris, 2026-11-22** (filed at the architect's order, [DISPATCH_23a_2026-11-22.md](DISPATCH_23a_2026-11-22.md)): "the difference between (i) and (ii), if there is one, resembles the supra- and infralapsarian difference, since it turns on whether grace must have sinners in view." It is his observation and is attached to no Position.

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
  - **Substrate-v1.** Send goat-yard the two corrections, then re-pin as a locked step. Amended 2026-11-01: correction (1) is withdrawn (goat-yard: the commit names the design lock, rerun-8, and the tag names the validating run, rerun-9); (2) stands. Re-pin scope: column-split reproduction only, with `ink_box` at v1.1 and its helper.
- Bible text: none stored or fetched. The USFM Bibles are read by `GOLDEN_CHAIN_BIBLES` only ([../sources/bibles-usfm.md](../sources/bibles-usfm.md)). ADR-0004 will name the USFM KJV as the display text source.

## goat-yard (lane G)

- Terms, additions and responses are verbatim in [../sources/goat-yard.md](../sources/goat-yard.md).
- Pinned: worktree `../goatyard-substrate-v1` at tag `substrate-v1` (`301bde5c`), installed with `pip install -e --no-deps`; re-pinned from v0 on 2026-11-01 at `e4b1435` (column-split reproduction only; `ink_box` at v1.1). Tool: `tools/gy_locate_column_rule.py`. The v0 worktree is kept.
- `locate_column_rule` (2026-10-26, UTC). The native run PASSES goat-yard's criteria, 20/20, but was "made at the wrong scale"; its "every strip" clause is FALSIFIED and is never edited. Reruns at 7.2 and at the architect's 0.703 frame both pass 20/20, and were rerun **clean** at `d32f888`. **The line-height-matched frame governs** (ruling on report 6): scale 6.947, median 55, clean at `6a7c5d1`, L1–L6 held. The strips to sign are cut from it.
- Run headers record golden-chain `git_start` / `git_end` / `clean_run`. A run is citable only if it is clean: commit first, then run.
- **OCR is UNHELD** (ruling on report 10, Q1). Chris signed the 6.947 strips on 2026-11-01. The re-pin is clean (V1–V5 held: all three runs identical to v0), so OCR work runs on v1. The A2 fixture is done; the Q11 crops console is next. Finding for the OCR column split: on p. 897 the rule divides the footnote ([../sources/gill-column-rule.md](../sources/gill-column-rule.md)).
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
- **§11 phase-2 additions (Chris, 2026-11-08), for the administrator question:** Gill, Practical III.1 on the administrator; Spilsbury, *A Treatise Concerning the Lawful Subject of Baptism* (1643, PD), if a scan exists. Validity (3) depends on the church Locus (phase 2); the foreword's prop. 3 (no baptism, no church) lands there.
