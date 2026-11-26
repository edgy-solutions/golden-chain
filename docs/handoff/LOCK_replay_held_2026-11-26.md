# Lock: the replay holds answers on Positions not yet in the data (ruling on report 28, item 8)

- **From:** the build agent, 2026-11-26. Committed before the code.
- **On:** [RULING_report_28.md](RULING_report_28.md) item 8: "from the signed record at minting. The replay holds an answer on a Position not yet in the data and applies it when the Position exists. Born test: replay before and after minting gives the same file as a single replay after." Also [LOCK_sitting2_console_2026-11-22.md](LOCK_sitting2_console_2026-11-22.md) Q-S2-1.

## The gap, and what is proposed

A sitting row on a Position not yet in the data is a single-field row (`fields == ["v"]`). For example, sitting 2's `instrumentality.a-stance` and `instrumentality.a-unchurches` are such rows. Its id does not name the Position, and the Position's slug is chosen only when it is minted: Batch C's lock has `baptism-instrumentality/instrumental`, while the row says `instrumentality.a`. So the replay cannot tell from the record alone which Position an answer is on.

**Proposed: a committed bindings file**, `docs/sittings/plumb-line-bindings.json` (format `golden-chain-plumb-bindings/1`). Each binding names:

- a sitting (build16);
- a target, either `position/<locus>/<position>` or `locus/<locus>`;
- the sitting's row ids that answer it: `modality` and optionally `unchurches` for a Position; `tier` and/or `clarity` for a locus.

A binding is written by whichever comes second, under its own lock (Q-S2-1 as ruled): the change that mints the target, or the ingest of the sitting that answers it. If the sitting comes first, its answer is held until the target is minted. If the target comes first, the answer applies at the ingest.

**The replay.** For each record in order:
- If a binding names its sitting and the target exists in `data/loci.ttl`, the bound rows are applied as one Position row (or locus row), at that sitting's place in the order. They keep that sitting's source and date. A later sitting can still change the answer, as for any other row.
- Values carry over as follows:
  - a stance value is the modality word;
  - "unchurches" means the flag is ticked, and "does not unchurch" means it is not;
  - tier and clarity values are taken as they are.
- A bound row whose target is not yet in the data is noted `held for <target>, not yet in the data`.
- An unbound single-field row stays `not data, in the SIGNED record only`, as now.
- With no bindings file, or none for a sitting, the output is byte-identical to today's.

**R2.3 still holds.** A held answer that, once applied, ticks unchurches on a stance other than forbidden, or on a tier-third locus, fails the replay and names the row. The minting change that makes it applicable stops there (rule 8), and nothing is dropped silently.

**The default.** `replay(records)` reads the committed bindings file and `data/loci.ttl` itself. That way the existing real-data test (`test_plumb_merge`, the replay equals `data/plumb-line.ttl`) keeps holding after a minting, unamended. Tests pass their own bindings and Position set.

## Predictions

| # | Prediction |
|---|---|
| H1 | Born tests; the full suite passes with no existing test amended. |
| H2 | With the bindings file present and empty (`"bindings": []`), `data/plumb-line.ttl` is byte-identical (sha `bfb0238c…`), and ingest is 0/0. |
| H3 | The ruled test holds. Take records where one sitting answers a Position not yet in the data, and a binding for it. Replaying before the minting gives the answer held, with the TTL noting it held. Replaying after the minting gives the same bytes as a single replay after the minting. Its Holdings, flags, tiers and clarities equal those of the same answers given as Position rows; only the comment lines differ. |
| H4 | A held answer that breaks R2.3 fails the replay once its target exists, naming the row. |
| H5 | The bindings file fails loud on each of these: a sitting with no record; a row id not in that record; a row bound twice; a target bound twice for one sitting; a row that is not single-field. |
| H6 | Weigh unchanged (members `b5ad57ea0df3`, officers `6a2ffd426bf9`). PREDICTED counts unchanged. |

## Recorded for the architect

- **Q-H-1.** Sitting 2 is not signed, so no binding is written now. When Batch C mints `baptism-instrumentality`, its lock binds:
  - `instrumentality.a-stance` and `a-unchurches` to `(a)`;
  - `b-stance` and `b-unchurches` to `(b)`;
  - `tier` and `clarity` to the locus.

  That is, if Chris has signed sitting 2 by then. A binding needs the sitting's record (H5), so if sitting 2 is signed after Batch C, the sitting-2 ingest writes the bindings in the same change instead, and they apply at once.
