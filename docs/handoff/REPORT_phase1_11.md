# Report 11: plumb-line sitting ingested; ADR-0003 Revision 2 drafted (stop after step 2)

2026-11-08. This is the build agent's report to the architect under the dispatch of 2026-11-08 §15: "Stop and report after 2 and after 5." Steps 1 and 2 are done. Step 3 does not start until this report is ruled on.

## Done

| Commit | Step | What |
|---|---|---|
| `e579319` | 1 | Sitting `7b23646b2c763ae0` ingested as is. Record: [SIGNED_plumb_line_7b23646b2c763ae0.md](SIGNED_plumb_line_7b23646b2c763ae0.md). The dispatch is filed verbatim with both later relays: [DISPATCH_architect_2026-11-08.md](DISPATCH_architect_2026-11-08.md). |
| this commit | 2 | [ADR-0003 Revision 2](../adr/0003-controlled-vocabularies-and-scoring.md), status **proposed**. |

**Step 1.**

- `data/plumb-line.ttl` holds 13 Holdings and a tier on all nine loci. Ingest went from 0 violations and 9 warnings to 0 and 0, with no Inconsistency.
- The console defect is recorded: v2 exports silence as incomplete. Until v3, `tools/console/ingest.py` applies the §1 ruling on the plumb-line only.
- Lock `plumb-line-signed-7b23646b-predictions-locked.txt` (20:32:20Z): P1–P5 held.
- **P6 missed on the first run: 328 pass, 2 fail.** Two tests copied the new real plumb-line.ttl into their scratch tree, so their own sitting's write collided with it. After the fix, 330 pass.

**Step 2.** Lock `adr0003-rev2-draft-predictions-locked.txt` (20:44:20Z): R1–R4 held. The change is docs only; pytest 330; ingest 0/0, with counts unchanged. The §2 and §3 texts are verbatim. §4 includes the addendum and the revised test cases (a)–(c).

## For the architect: Revision 2's open points (R2.6), with my proposals

1. **Tolerated.** Does a Body that *tolerates* a flagged Position "practise" it? I propose not: only `required` and `taught` trigger exclusion, the same pair on which `excludes` fires.
2. **First tier.** May a first-tier Locus carry `unchurches`? Shape 2 forbids only third tier. The addendum speaks only of tier 2.
3. **Bodies that are not churches.** Every Body in the data is a document (Confession, Catechism, Systematic), and Teachers come in phase 3. I propose the exact wording for every Body class, or a different label for Systematic and Teacher Bodies.
4. **"Tier-2 break" for display.** I define a break as a WALL, or a cell of 0.25 or more, on a second-tier Locus; the permitted row never makes one. With shapes 1 and 2, this makes your addendum's implication hold by construction and testable.
5. **Instrumentality (a)/(b).** Should they be an `excludes` pair? Until (a) is signed, a Body that holds (a) and is silent on (b) scores *unknown* there.
6. **Other users.** Does `unchurches` exclude Bodies for users other than the plumb-line? I leave this undecided.

## For Chris, before ratification (you asked him to read §4 first)

**The derivation reaches further than the list he affirmed.** On "holds or practises", **the Augsburg Confession (AC IX, infants taught) and the Apology (1531) are excluded** as well as WCF. In general, every Body that requires or teaches infant baptism is excluded. Revision 2 states this plainly, as §4 requires. The draft does not soften it, and it does not decide it for him.

## Flags ahead of step 3 (not acted on)

- **E1 direction.** The data has `believers-and-their-infants entails one-covenant-two-administrations` ([data/loci.ttl:182](../../data/loci.ttl#L182)). Dispatch §5 has "23b-yes entails believers-and-their-infants", which is the reverse direction. Which is meant?
- **The fused covenant Locus after the split.**
  - `covenant-administrations` has Holdings from Gill and WCF, the E1 edge, and a tier in the *signed* plumb-line.ttl, which is content-addressed and never edited.
  - Should it be retired with a pointer to 23a and 23b, or kept beside them? Retiring it leaves a tier in the signed file pointing at a retired Locus.
- **Tier warnings return.** The four new loci (23a, 23b, validity, instrumentality) have no `gc:tier` until the follow-up sitting writes them. The step 3 lock will predict warnings 0 → 4.
- **§7 correction (BSB 1984 foreword).** I will read proposition 7 and propose 3 or 4 for Chris to rule. Under §12 nothing from BSB is modelled before phase 3. If position 3 has no published source, the plumb-line's signed Argument carries it.
- **Weigh is not built.** No scoring code exists yet. Step 5's "first real weigh run" includes building §5, plus Revision 2's exclusion once ratified, with tests born with it.

## Still pending (unchanged order)

- **Records:** the §14 findings against the architect; the §11 phase-2 list; the §12 Lee permission rule in `docs/sources/`.
- **The lone-narrow-glyph count on pp. 896–915:** locked, then measured in code, before OCR.
- **Chris:** sends both goat-yard notes. The fixture note's glyph paragraph is amended once that count is in.
