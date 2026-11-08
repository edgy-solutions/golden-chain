# Signed sitting: plumb-line, console 7b23646b2c763ae0

Ingested 2026-11-08 under the architect's dispatch of that day, §1 ([DISPATCH_architect_2026-11-08.md](DISPATCH_architect_2026-11-08.md)): ingested as is. The instance record is [data/plumb-line.ttl](../../data/plumb-line.ttl). This page records provenance, the prediction outcome and the console defect. It is written by hand, because the plumb-line kind writes TTL and no reading form.

## Provenance

- Signer: Chris (Chris Nogradi), 2026-11-08
- Export: exported_utc 2026-11-08T20:24:43.962Z, `complete` false (see the defect below). The other three plumb-line exports Chris downloaded are superseded and were not ingested.
- build_hash: 7b23646b2c763ae09ecfdd02d8b98b14accc3f69ebe57215ff2c84cba6e3081e
- export sha256: 5177fca1de7490a4baa038dc4b6dc94aa566c1d7c721e7c16a54b5dace116d47 (4836 bytes)
- manifest sha256: e6b95f6f41fa8f5fed0f0619ad983357d7ba906a1bd1de7e3f47ab0e634aa734
- signed_utc: 2026-11-08T20:33:40Z; provisional: false
- The export and `signed_plumb-line_7b23646b2c763ae0.json` are kept read-only in `~/.golden-chain/console/plumb-line/`. The TTL's SourceDivision `source/plumb-line/sitting-7b23646b2c763ae0` carries the export sha as its identifier.

## Console defect (console v2; to be fixed in v3)

Console v2 treats a plumb-line modality that is left empty as an unanswered field, so it exported this sitting with `complete: false`. The only empty field is the modality on `johns-baptism.same-ordinance`. That is deliberate silence (clarity open), a legitimate stance and a complete verdict (dispatch §1). The defect is in the console, not in the sitting.

Until v3, [tools/console/ingest.py](../../tools/console/ingest.py) applies the ruling. On the plumb-line only, a verdict row whose modality is null is read as silent and writes nothing. `complete: false` is accepted only when every unanswered required field is such a null. Every other gap, on every kind, still fails. The TTL names the silent rows in a comment.

Console v3 (dispatch §13) must export silence as complete.

## Predictions (locked 2026-11-08T20:32:20Z, `~/.golden-chain/plumb-line-signed-7b23646b-predictions-locked.txt`)

The baseline, at 455d9cf: pytest 327 pass; ingest 0 violations and 9 warnings (all nine "Locus has no tier yet").

| | Prediction | Outcome |
|---|---|---|
| P1 | ingest.py reads a null plumb-line modality as silent; tests +3 | held |
| P2 | code_sha matches; export copied byte-identical, read-only | held |
| P3 | `--write` writes the signed record and data/plumb-line.ttl, nothing else under data/ | held |
| P4 | 13 Holdings; tier on 9 loci (8 second, johns-baptism third); clarity on 8; 2 others; 1 silent; no abstain or fault | held |
| P5 | ingest 0 violations, 0 warnings; Holding and holds 34→47, effectivelyHolds 35→48, all else unchanged; no Inconsistency | held |
| P6 | pytest 330 pass | **missed on the first run**: 328 pass, 2 fail. Then 330 after the fix below. |

**The P6 miss.** `test_plumb_line_ttl_conforms_with_the_real_data` and `test_plumb_ttl_writes_nothing_for_other_as_written` copy every `data/*.ttl` into a scratch tree and then write their own sitting's plumb-line.ttl there. The real data/plumb-line.ttl now exists, so the write refused with "exists with different bytes". This was a collision in the test fixtures, not in the ingest. Both loops now skip plumb-line.ttl, because the test's own sitting stands in for it. After that fix, 330 pass.

## Notes and "other" entries (requests, not data)

Under dispatch §1, every note and every "other" entry is a mint request or a flag request. The architect ruled each one, and none was written as data by this step.

| Row | Field | As written | Ruled in |
|---|---|---|---|
| covenant-administrations.locus | clarity (other) | 23a clarity contested; 23b settled. | §5 |
| covenant-administrations.one-covenant-two-administrations | modality (other) | split into 23a (Gill's position, taught) and 23b (circumcision as administration including infants, forbidden). | §5 |
| baptism-subjects.believers-and-their-infants | note | unchurches: a body practicing this is not a church; its members may be Christians | §4 |
| baptism-subjects.infants | note | unchurches: a body practicing this is not a church; its members may be Christians | §4 |
| baptism-formula.locus | note | tier second; non-triune formula positions unchurches | §4 |
| baptism-repetition.locus | note | the validity locus and its four positions (the text is in the export) | §7 |
| baptism-repetition.once-only | note | Baptism is administered once. The sprinkling of an infant is not baptism, so the baptism of a professing believer who was sprinkled in infancy is his first baptism, not a repetition | §6 |

The apostrophe in "Gill's" was a curly quote in the export. It is shown here as a plain one.
