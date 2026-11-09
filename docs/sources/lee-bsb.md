# Source rule: Bill Lee and the Baptist Standard Bearer

Recorded 2026-11-08, as dispatch 2026-11-08 §12 requires ("Record this as a rule in docs/sources/"). This is a rule, not a source review.

## The rule

1. **Permission.** Lee's verbal grant covers only what he could give. It does not bind his estate.
2. **Private corpus.** Lee's corpus (sermons, writings and notes, held by Chris) stays private. It is read only from a configured path, never from the repo, and nothing from it is copied into the repo.
3. **Before any Lee text appears on the site,** written permission is needed from Lee's estate and from BSB's current principals. Each permission is filed beside the text it covers.
4. **Nothing is modelled before phase 3** from Lee or from BSB: no Body, Holding or Argument.
5. **The 1984 foreword** to BSB's edition of Gill's *Body of Divinity* is not public domain. It is excluded from the corpus and from all data ([gill-body-of-divinity.md](gill-body-of-divinity.md)).
   - It may be read, to propose.
   - It may be **cited** now as a source division, by printed page. That is how it is cited for validity (3): pp. vii–viii, props. 1 and 7 ([../handoff/PROPOSAL_validity_bsb_foreword.md](../handoff/PROPOSAL_validity_bsb_foreword.md), ruling of 2026-11-08).
   - **Nothing from it is quoted** in any committed file: paraphrase and locators only.

## Authorship

The foreword is signed "The Baptist Standard Bearer" (p. xiv). Dispatch §12 says it was authored by Lee under BSB. That attribution comes from Chris's knowledge; the page does not show it. When the phase-3 SourceDivision is minted, it records the attribution as Chris's testimony.

## Phase 3 (design note, from §12)

- `gc:Teacher`, a Body subclass for one person's corpus. `body/bill-lee` is a Teacher. `body/bsb` is a separate institutional Body.
- Lee's corpus will be the first unstructured source. The model proposes "this passage speaks to locus X, position Y", Chris signs each proposed Holding in a console, and the model routes but never asserts.
- Validation: the plumb-line's distance to `body/bill-lee` should be small. If it is not, the scoring is wrong.
