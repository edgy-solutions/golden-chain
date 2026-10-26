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
PREDICTED = {
    "Locus": 9, "Position": 15, "Argument": 45, "Passage": 86, "Body": 7, "Holding": 34,
    "excludes": 5, "entails": 1, "holds": 34, "answers": 15, "supports": 45, "childOf": 1,
    "effectivelyHolds": 35, "warnings": 9,
}
