# Proposal: ADR-0006 Revision 1, how a second plumb-line sitting enters the data

- Status: **proposed** by the build agent, 2026-11-13 (overnight order, item 2 finding). Nothing is built on it.
- For: the architect.

## The gap

ADR-0006 §10 (ii) sends a plumb-line sitting to `data/plumb-line.ttl`. That works for one sitting only.

- **The file name and the graph.** `goldenchain/ingest.py` `graph_name()` names each named graph by the file stem. So `data/plumb-line.ttl` is `graph/plumb-line`, and a second file would be a second graph.
- **The console refuses.** The console ingest (`tools/console/ingest.py`, `write_addressed`) never overwrites a file whose bytes differ. So a second sitting cannot replace `data/plumb-line.ttl`.
- **The IRIs collide.** Holding IRIs are `holding/plumb-line/<locus>/<position>`, with no sitting in them. If a later sitting changes a modality, it collides with the earlier Holding's IRI.
- **Tier and clarity carry no sitting.** They are bare triples on the Locus (`<locus/x> gc:tier …`).
- **Nothing reaches the data yet.** The follow-up sitting (`plumb-line-followup`, console `c89256e734a61e4f`) therefore writes only `SIGNED_plumb_line_followup_<b16>.md`. None of its locus or position answers reach the data until this is ruled.

## Options

| | Shape | Weigh / reasoner change | Cost |
|---|---|---|---|
| A | One cumulative `data/plumb-line.ttl`, rewritten by each sitting: earlier answers ∪ the new sitting's answers, the newer winning row by row | none | The file's history lives in git and in the per-sitting records, not in the TTL. |
| B | One file per sitting, `data/plumb-line-<build16>.ttl` (its own graph); a later Holding `dcterms:replaces` the earlier one; Holding IRIs gain the sitting | `stances()` must skip replaced Holdings; tier and clarity need reification to say which sitting set them | Changes the ADR-0002 Holding IRI pattern; every consumer must resolve supersession. |
| C | As A, but every changed triple is also recorded as an OWL annotated axiom naming the sitting (the ADR-0002 R2 pattern ruled for notes, M3) | none | More TTL; the change history is queryable. |

## Proposed: A

1. **What a sitting writes.** A plumb-line or plumb-line-followup sitting writes `data/plumb-line.ttl` as a merge:
   - it starts from the committed file;
   - the rows the new sitting answered replace the old values;
   - every other triple is kept as it is.
2. **Holdings.**
   - A Holding whose modality changes takes the new sitting as `dcterms:source`, with the new `dcterms:dateAccepted`.
   - An unchanged Holding keeps its source.
   - The Holding IRI is unchanged, so the ADR-0002 pattern stays.
3. **Tier and clarity.** The last sitting wins. A TTL comment above each Locus line names the sitting that set it. That is a comment, not data; option C would make it data.
4. **unchurches.**
   - Ticked → `gc:unchurches true`.
   - On a follow-up flag row, "withdraw" removes the triple and "confirm" keeps it.
5. **The overwrite guard.**
   - The only path that may replace `data/plumb-line.ttl` is the merge.
   - The merge records, in the file's header comment, every sitting in order (build16 and export sha256) and the sha256 of the file it replaced.
   - It refuses if the committed file's sha256 is not the one the last listed sitting wrote. So a hand edit is never silently merged over.
6. **Sitting SourceDivisions.** Each sitting has its own `source/plumb-line/sitting-<build16>`, as ADR-0006 open point 1 was ruled.
7. **Rows that are not data.** The follow-up's radio, proposal and text rows (F-A, F-B, the Gill paragraph, the LBC letters) stay in the SIGNED Markdown record. Their data changes go by locked prediction, as the WCF 1647 reading did.

## Questions for the architect

1. **Which option: A, B or C?** I recommend A.
2. **Silence in a later sitting.** When a later sitting leaves a Position empty (silent) that an earlier sitting answered, does that remove the Holding, or leave the earlier answer standing?
   - I propose that it removes the Holding. Silence is a complete answer (ADR-0003 R2.2, console v3), and the row was put to Chris again.
   - A row that is not on the later form is untouched.
3. **Tier and clarity provenance.** Is a comment enough (A), or must the sitting that set a tier be data (C)?
