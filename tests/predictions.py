# Predicted counts for the real dataset, written before ingest (the refutation baseline).
# Keys: Locus, Position, Argument, Passage, Body, Holding (distinct typed subjects);
# excludes, entails, holds, answers, supports, childOf (asserted triples, union of source graphs);
# effectivelyHolds (derived triples); warnings (SHACL warning count).
# Filled by the main session; None makes tests/test_real_data.py::test_counts_match_predictions fail loud.
# Locked 2026-10-25T19:24:54Z before the first generate (scratchpad predictions-locked.txt),
# except Passage: 87 was measured, not predicted independently, and is pinned here as the baseline.
# Ruling Q21 (2026-10-26): acceptable once. From now on every count is predicted, derived ones
# included; a count pinned as measured is a finding.
# LBC 29 ruling (2026-10-25): Passage 87 -> 86 predicted and locked before regenerating (only
# Acts.8.37-Acts.8.38 drops; Acts 2:41, 8:12, 22:16 and 8:36-37 stay cited elsewhere); matched.
# LBC 29.1 split into one Argument per lettered note (ruling, report 2 Q1): Argument and
# supports 41 -> 43, locked 2026-10-26T00:27:52Z before regenerating; matched.
# Rulings Q7, Q8 (Book of Concord is a Collection; members dcterms:isPartOf, not childOf):
# childOf 2 -> 0, effectivelyHolds 33 unchanged, locked 2026-10-26T00:42:45Z; matched.
# Ruling on report 4: apology childOf augsburg (small-catechism has no parent): childOf 0 -> 1,
# effectivelyHolds 33 -> 34 (Apology inherits only augsburg/baptism-efficacy; its own infants
# Holding overrides baptism-subjects), locked 2026-10-26T01:04:26Z; matched.
# Ruling Q5 on report 2: locus baptism-repetition (33c) with WCF 28.7 once-only only (the Gill/LBC
# Position is not minted; rule 2): Locus 8->9, Position 14->15, Argument/supports 43->44, Holding/holds
# 33->34, answers 14->15, effectivelyHolds 34->35, warnings 8->9 (gc:tier, one per Locus), Passage 86
# unchanged (Titus 3:5 already cited by 28.6), locked 2026-10-26T01:13:13Z; matched.
# Ruling Q6 on report 2: Apology IX Argument 002 for necessary-means-of-grace (Matt 28:19), no
# Holding: Argument/supports 44 -> 45, locked 2026-10-26T01:17:01Z; matched.
# Ruling Q2a on report 7: body/plumb-line minted as gc:Editorial: Body 7 -> 8, all else unchanged,
# locked 2026-11-01T15:37:19Z.
# WCF sitting 318910c8 with report 8 Q2-Q4: one Argument per signed lettered note (28.1 b, e, f, g;
# 28.4 l; 28.5 n, o, p; 28.6 q): Argument/supports 45 -> 54, Passage 86 -> 100 (14 new refs), all else
# unchanged, locked 2026-11-01T17:57:38Z.
# Plumb-line sitting 7b23646b signed 2026-11-08 (dispatch §1): data/plumb-line.ttl, 13 Holdings and a tier
# on all nine loci: Holding/holds 34 -> 47, effectivelyHolds 35 -> 48, warnings 9 -> 0, all else
# unchanged, locked 2026-11-08T20:32:20Z.
# Step 3 Batch A (PLAN_step3_minting, ruling on report 11): loci 23a/23b minted, 23 retired (owl:deprecated), E1 moved; Locus 9->11, Position/answers 15->20, Argument/supports 54->70, Passage 100->130, Holding/holds 47->50, effectivelyHolds 48->51, warnings 0->2 (tier on 23a, 23b), locked 2026-11-09T02:36:51Z; matched.
# Batch A′ locked 2026-11-09T03:36:32Z (~/.golden-chain/step3-batchA2-predictions-locked.txt); matched (P1-P6 held; pytest 380).
# Step 3 Batch B (RULING_report_12) locked 2026-11-13T05:37:39Z (~/.golden-chain/step3-batchB-predictions-locked.txt). B1-B7 matched; B8 MISSED: the first full run had 1 failure + 9 errors, because the plumb-line
# form check refused a Position minted after the form was signed. The check now requires the form's Positions to be a
# subset of the ttl's (as for loci); pytest 402 passed.
PREDICTED = {
    "Locus": 12, "Position": 24, "Argument": 80, "Passage": 142, "Body": 8, "Holding": 53,
    "excludes": 9, "entails": 1, "holds": 53, "answers": 24, "supports": 80, "childOf": 1,
    "effectivelyHolds": 54, "warnings": 3, "Axiom": 1,
}
