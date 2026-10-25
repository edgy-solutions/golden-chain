# Predicted counts for the real dataset, written before ingest (the refutation baseline).
# Keys: Locus, Position, Argument, Passage, Body, Holding (distinct typed subjects);
# excludes, entails, holds, answers, supports, childOf (asserted triples, union of source graphs);
# effectivelyHolds (derived triples); warnings (SHACL warning count).
# Filled by the main session; None makes tests/test_real_data.py::test_counts_match_predictions fail loud.
# Locked 2026-10-25T19:24:54Z before the first generate (scratchpad predictions-locked.txt),
# except Passage: 87 was measured, not predicted independently, and is pinned here as the baseline.
# LBC 29 ruling (2026-10-25): Passage 87 -> 86 predicted and locked before regenerating (only
# Acts.8.37-Acts.8.38 drops; Acts 2:41, 8:12, 22:16 and 8:36-37 stay cited elsewhere); matched.
PREDICTED = {
    "Locus": 8, "Position": 14, "Argument": 41, "Passage": 86, "Body": 7, "Holding": 33,
    "excludes": 5, "entails": 1, "holds": 33, "answers": 14, "supports": 41, "childOf": 2,
    "effectivelyHolds": 33, "warnings": 8,
}
