# ADR-0006: Sign from pixels in a self-contained console, bound by hashes

- Status: Ratified provisionally, on report 7; the architect will read the text (ruling, report 7 Q2)
- Date proposed: 2026-10-25
- Date ratified: 2026-10-26 (provisionally)
- Proposed by: build agent
- Ratified by: architect

Built on the architect's directive in the reply to report 6 ("SIGNING
CONSOLE"). This ADR states what was built so a test can check it. Nothing
writes to `data/` through the console until this ADR is ratified (open
point 1).

## Context

- Sign-offs today are Markdown forms with `__` blanks (`SIGNOFF_empty_strips.md`,
  `READING_wcf1647_proofs.md`, `plumb-line-form-phase1.md`). Nothing binds a
  filled blank to the picture it was read from, and the strings are copied
  into TTL by hand.
- Rule 10 (goat-yard laws): sign from pixels; clean run; run headers; zero
  wrong-pass. goat-yard's truth-set form v1 (`docs/forms/TRUTH_SET_FORM.md`
  at `a0a30d4`, cited in ADR-0002 rule 5) gives the record: a draw, an offer
  carrying a digest of every image offered, and a signed ingest (§1–§4);
  typed non-verdicts (§5); hash and naming rules (§8).
- goat-yard's consoles (`glyph_signer.py`, `render_adjudication.py`,
  `ingest_pass2.py` on `apparatus-next`) are the pattern: verdicts bound to
  the build, the crop shown as the runner cuts it, export before closing.
  No goat-yard code is copied.
- Ruling on report 6 (signing strips): "no thresholded content in signing
  strips. They are raw page pixels plus a drawn overlay of the run's result."

## Decision

1. **Three records per sitting** (truth-set form §1):
   - **Draw** (`spec`): a JSON written by a spec builder in
     `tools/console/specs/` from committed or run records. It holds the
     instruction as given to the signer (verbatim), the source records with
     their sha256, the run header verbatim, the images (path and sha256),
     the rows and their controls, and `withheld` (rows held back, with the
     reason).
   - **Offer** (`manifest`): `tools/console/build.py` writes one HTML per
     sitting and a manifest with `build_hash`, `spec_sha256`,
     `code_sha256`, `html_sha256`, the image sha256s, the golden-chain git
     state at the start and end of the build, and `provisional`.
   - **Sign** (`signed`): `tools/console/ingest.py` checks an export
     against its manifest and writes the signed record.
2. **The page is self-contained.** Every image is inline as a
   `data:image/png;base64` URI, and its sha256 is printed beside it. A
   Content-Security-Policy meta allows no network (`default-src 'none'`).
   There are no external scripts, styles or fonts.
3. **Raw pixels, overlay drawn.** Each image is the crop exactly as the
   cutter wrote it. A run's result (ticks, band edges, strip bounds) is an
   SVG layer drawn over it, which the signer can hide. No threshold is
   applied to anything the signer sees.
4. **Controls per row:** radio, checkbox, select or text, as the spec says,
   and `pick-row`: a click on an image records a page row, mapped to the
   page frame by the crop's recorded origin and scale.
   Every row also offers the typed non-verdicts `abstain` (could not read)
   and `fault` (input unfit), each with a note (truth-set form §5). A
   field left blank is `unknown`, never `false`.
5. **The signer types as little as possible.** Wherever a value can be
   chosen (a strip tick, a vocabulary term), it is a control, not a text
   box. Where a proposed string is shown, the controls are `confirm` /
   `correct` (with text) / `abstain` / `fault`. A row whose value was
   corrected is recorded as a **signed reading**, not a pixel signature
   (truth-set form §4.2).
6. **Build hash.** `build_hash` is the sha256 of the UTF-8 bytes of
   `json.dumps({"spec_sha256", "code_sha256", "images": {id: sha256}},
   ensure_ascii=False, sort_keys=True, indent=1)`.
   - `spec_sha256` is taken over the spec serialised by the same rule.
   - `code_sha256` is the sha256 of `build.py`'s bytes followed by the
     template's bytes.
   - `build16` is its first 16 hex digits and names the files.
7. **Export before closing.** The Export button downloads
   `verdicts_<kind>_<build16>.json`. It holds the format id, `build_hash`,
   the run header, the image sha256s, every row's state and values, the
   signature (name and date), `complete`, and the export time.
   - The page warns on close (`beforeunload`) if anything has changed
     since the last export.
   - Local storage is a best-effort draft only. The download is the record.
8. **Ingest fails loud** and writes nothing on any failure. It checks:
   - the format;
   - `build_hash`, recomputed from the spec, the code and the image files
     by code written separately from `build.py` (truth-set form §8.5);
   - every image sha256 against its file;
   - `complete`;
   - no row with both a value and a non-verdict;
   - a signature;
   - `provisional` false, unless the caller passes `--provisional`, which
     the signed record then carries.
9. **Files** (truth-set form §8): digests are taken by the rule in item 6,
   and files are written LF-only. Names are content-addressed. A write to
   an existing name with different bytes is refused. Each file is staged,
   verified, then renamed.
   - The spec, manifest, HTML and exports live under `~/.golden-chain/console/`.
     They are never committed: the crops are corpus pixels.
   - The committed result is per instance (item 10). It cites the
     `build_hash` and the sha256 of the export.
10. **Instances and where the verdicts land:**
    - (i) the empty-strips sign-off (Chris) → `docs/handoff/SIGNED_empty_strips_<build16>.md`;
    - (ii) the plumb-line, as a loci × positions grid with tier, clarity
      and modality selectors (Chris signs every sitting; ruling, report 7
      Q2a) → `data/plumb-line.ttl`;
    - (iii) the WCF 1647 proof reading, with the build agent's proposed
      strings beside the page crops (Chris) →
      `docs/handoff/SIGNED_wcf1647_<build16>.md`. (Every instance is named
      `SIGNED_<kind>_<build16>.md`.) TTL then changes by
      locked prediction, as the reading form says.
    - ADR ratification cards come after these.

## Consequences

- A verdict is about a known picture: its sha256 is in the export, and the
  ingest reproduces it from the file.
- The Markdown forms become the human-readable statement of each sitting's
  questions. Their blanks are filled by the ingest, never by hand.
- A console built from an uncommitted tree is provisional, and its verdicts
  cannot be cited in an ADR or a tier change unless the architect rules it.
- Harder: a change to a question means a new spec and a new build hash. An
  export for the old build no longer ingests against the new one.

## Alternatives considered

- **Keep the Markdown forms.** Lost: nothing binds a blank to its pixels.
- **Link images by file path** (goat-yard's pass-2 notes). Lost: the page
  stops being self-contained, and a moved file breaks the record silently.
- **Hash the HTML as the build hash.** Lost: the page would have to carry
  its own digest. The manifest carries `html_sha256` instead.

## Verification

Tests in `tests/test_console*.py`, born with the code:

- the HTML has the CSP meta, and no `http:`/`https:` in any `src`, `href`
  or `url(`;
- every image is a data URI whose decoded bytes hash to the sha256 printed
  beside it;
- the build hash is computed by the rule in item 6, and a fixed spec gives a
  fixed hash;
- each ingest refusal (wrong build hash, a changed image byte, incomplete,
  value plus abstain, no signature, provisional) is proven by mutation;
- a same-name/different-bytes write is refused;
- the three instance writers, on fixture exports.

## Ratification (provisional, 2026-10-26)

Ruled on report 7, Q2. The architect will read the text; this section records what was ruled.

- **Open point 1, ruled (a): yes.** One `gc:SourceDivision` per signed sitting, `B source/plumb-line/sitting-<build16>`, identified by the export's sha256.
  - `B body/plumb-line` is minted now, as its own subclass `gc:Editorial` of `gc:Body` (`ontology/core.ttl`), with one instance, ever. A shape enforces that (`ontology/shapes.ttl`, `shapes#Editorial`). The Body is declared in `data/agents.ttl`.
  - **The signer of every plumb-line sitting is Chris.**
- **Open point 2, ruled (b): enough.** Per-row confirm / correct is the right grain for a printed citation string. Per-token pixel signatures are for OCR truth sets. A corrected row is a signed reading with register `corrected`, per the form.

## Open points (as proposed; ruled above)

1. **Plumb-line Holdings need a source.** The shape requires a
   `dcterms:source` of class `gc:SourceDivision` on every Holding. Proposed:
   `B source/plumb-line/sitting-<build16>`, one SourceDivision per signed
   sitting, typed `gc:SourceDivision`. Its `dcterms:identifier` would be the
   export's sha256, and `status ratified` with `proposedBy` and `ratifiedBy`
   both `B agent/architect` (ADR-0005). Also open: `B body/plumb-line` is not
   minted in `data/agents.ttl` yet. Until this is ruled, the plumb-line
   writer is built and tested on fixtures and writes nothing to `data/`.
2. **Per-tile signing.** For the WCF strings the console offers `confirm` /
   `correct` per row, not one tile per token. Is a whole-string confirmation
   enough, given that a corrected row is recorded as a signed reading?

## Revision 1 (2026-11-14; ruled on report 13, item 6): how a later plumb-line sitting enters the data

Ruled: option A of [PROPOSAL_adr0006_r1_second_sitting.md](../handoff/PROPOSAL_adr0006_r1_second_sitting.md), with two additions (replay; provenance as data) and the silence rule. Ruling text: [RULING_report_13.md](../handoff/RULING_report_13.md). Points marked *(reading)* are the build agent's, for the architect to confirm.

1. **The record.**
   - Every signed `plumb-line` and `plumb-line-followup` record is committed. That is the `signed_<kind>_<build16>.json` the ingest writes, which carries the export's sha256.
   - It goes under `docs/sittings/plumb-line/` as `NNNN_signed_<kind>_<build16>.json`, numbered in signing order from `0001`, and is never overwritten.
   - *(reading)* The directory is outside `data/` because the pre-commit hook admits only `.ttl`, `.py` and `.md` there.
2. **The product.**
   - `data/plumb-line.ttl` is the deterministic product of replaying the records in order, starting from an empty file. One function does it: `replay(records) -> bytes`.
   - Born test: replaying the committed records gives the committed file, byte for byte.
3. **The merge, row by row.** The newer sitting wins row by row. A row that is not on a later form is untouched.
   - **Locus row (verdict):** a given tier or clarity replaces the earlier one; `other` leaves the earlier one standing.
   - **Position row, modality:**
     - A modality writes or replaces the Holding. A new or changed Holding takes this sitting as its `dcterms:source` and its signature date as `dcterms:dateAccepted`; an unchanged one keeps its earlier source and date.
     - `silent`, chosen, is **verdict: silent**. It removes the Holding and any `gc:unchurches` on that Position.
     - Left empty is **unanswered**, and nothing changes.
     - `other` leaves the earlier answer standing.
   - **Position row, unchurches checkbox (console v3):** when the row's modality is answered, ticked writes the flag and unticked removes it. Ticked on an unanswered modality: the merge fails.
   - **Flag row (follow-up):** `confirm` writes the flag and `withdraw` removes it. On a Position the plumb-line does not hold after the merge, nothing is written, and the header says so.
   - **Abstain and fault rows:** untouched.
   - **Radio, proposal and text rows:** these are not data. They stay in the SIGNED Markdown record.
   - **After the merge:** every flag must stand on a Position the plumb-line holds forbidden, at a Locus whose tier is not third (ADR-0003 R2.3; ingest check e). Otherwise the merge fails and nothing is written.
4. **Provenance as data.**
   - Each `gc:tier`, `gc:clarity` and `gc:unchurches` triple has one `owl:Axiom` (the ADR-0002 R2 pattern) naming the sitting that set it, by `dcterms:source`, with an `rdfs:comment`.
   - The IRIs are `axiom/tier/<locus>/to/<tier>`, `axiom/clarity/<locus>/to/<clarity>` and `axiom/unchurches/<locus>/<position>/to/true`.
   - Holdings carry `dcterms:source` as before. Nothing else is annotated.
5. **The overwrite guard.**
   - The merge is the only path that writes `data/plumb-line.ttl`.
   - Before merging, it replays the committed records and refuses unless the result equals the committed file. So a hand edit is never merged over.
   - The file's header lists every sitting in order: build16, kind, signature date, export sha256, and the sha256 of the product it replaced.
6. **Silence and unanswered** *(reading)*.
   - "Verdict: silent" is the modality option `silent`, chosen on a verdict row.
   - "Unanswered" is a modality left empty, or a row in abstain or fault.
   - Dispatch 2026-11-08 §1 still holds for completeness: an empty field does not make an export incomplete. The two differ only in the merge, where unanswered never removes.
   - The follow-up form `c89256e734a61e4f` re-asks no Position that sitting 1 holds, so this reading changes nothing on it.
   - Any later form that re-asks a held Position must say, in its help, that empty leaves the earlier answer standing and that `silent` removes it.

## Revision 2 (proposed 2026-11-15, on Chris's direction; RATIFIED 2026-11-15, ruling on report 17): a region question shows its surroundings

1. **The rule (Chris, 2026-11-15).** "A crop offered for a 'what is this region' question must include enough of its surroundings to answer it."
2. **Why.** The truth-set sitting `8afafecd34665b14` asked whether the small type at the foot of p. 914 left was column footnotes. The crop began 30 px above that type, so it showed no body text for comparison and no note number. The signed "no" is a crop fault ([AUDIT_truthset_italic_8afafecd34665b14.md](../handoff/AUDIT_truthset_italic_8afafecd34665b14.md)).
3. **The check (build).** A row that asks what a region is carries `region_question`: `image_id`, `roi`, `crop_box` and `source_wh`, all in the source image's frame. Build fails unless all of the following hold:
   - the image is on the row;
   - the ROI lies inside the crop, and the crop lies inside the source;
   - above and below the ROI there is context of at least max(ROI height, 300 px), unless the crop reaches that edge of the source;
   - left and right follow the same rule with the ROI width, unless the crop spans the whole source width.
4. **Scope.** Rows without `region_question` are unchanged. A whole-source image always passes. Word-level rows (is this word italic) are not region questions.

## Revision 3 (ruled 2026-11-15, report 17 Q-1): clear edges, and no reading for the signer

1. **Clear edges.** An image may carry `clear_edges` (top, bottom, left, right).
   - Build fails if ink touches the outermost row or column of a listed edge.
   - Ink is any pixel below the mode-midpoint threshold: the midpoint of the paper mode (values ≥ 128) and the ink mode (values < 128).
   - Word crops of any future draw carry `clear_edges: [top, bottom]`, cut from a line box padded vertically.
   - Why: 10 of the 196 truth-set word crops, cut flush at the OCR box, carry Chris's note that the crop clipped the word ([AUDIT_truthset_italic_8afafecd34665b14.md](../handoff/AUDIT_truthset_italic_8afafecd34665b14.md)).
2. **No one reads a crop for the signer during a sitting** ([RULES.md](../RULES.md) rule 11).
   - Questions about the form are answered from its text.
   - A row a model was shown is registered **model-proposed**.
   - `--code-at` (ingest) is accepted as keeping item 8's check strict.

## Revision 4 (ruled 2026-11-15, ruling on report 18): plain words on every question

1. **Every field carries `plain`.** It is one or two sentences saying what is
   asked, what each option means, and what to choose when none fits (the
   ruling's words). The page shows it under the question.
2. **The build check** (`check_plain`, `TEMPLATE_VERSION` 6) fails a field when:
   - `plain` is missing, blank or not a string;
   - it has three or more sentences;
   - it is an option field and `plain` does not name each option as a whole word;
   - it is an option field that is not a proposal radio and `plain` does not
     say "other, as written".
3. **Built consoles are not rebuilt.** The two waiting for Chris (re-ask
   `d7a6aab0734ffe3e`, follow-up `eb961ddb1e582ed6`) ingest with `--code-at`
   at their build commits. If Chris finds a row unclear, the build agent
   answers from the form's text and records that he asked (rule 11).
4. Lock: `plain-words-predictions-locked.txt`, PW1–PW5. The results are in
   report 19.

## Revision 5 (ruled 2026-11-17, ruling on report 19, A-7): the build hash names images, not where they lie

Report 19 found that two clean runs of the same draw gave two build hashes
(`015bfeed482a5083`, `03a299fb575fc4c3`). Their spec copies differed only in
absolute paths (each image, and `crops.json`) and in `run_header.utc`; every
image's bytes were the same. The architect ruled: identify images by sha256
and logical name; keep absolute paths and run times out of the hashed spec,
and record them in the manifest beside it.

1. **The input spec is unchanged.** Spec makers still give each image and
   source a `path`, and may give a `run_header`. An image or source may also
   give `name`, its logical name. Without one, the name is the file's basename.
2. **The build splits the spec in two.**
   - The **hashed spec** is the input spec with every `path` replaced by
     `name` and `run_header` removed. The spec copy beside the manifest is the
     hashed spec, so it holds no absolute path and no run time.
   - The **local block** holds what was removed: the image paths by id, the
     source paths by name, and the run header. It is written into the
     manifest, which is not hashed (it already holds the build's time and git
     state).
3. **A name is a relative POSIX path:** non-empty, no backslash, no drive or
   colon, not starting with `/`, no `..` part. Image names are unique. Two
   sources may share a name only if they share the sha256. The build fails
   loud otherwise.
4. **The rule is otherwise item 6 unchanged.**
   - `spec_sha256 = sha256(canon(hashed spec))`.
   - `build_hash = sha256(canon({"spec_sha256", "code_sha256", "images": {id: sha256}}))`.

   An image is thus fixed by its id, its logical name and its sha256 (all
   three are in the hashed spec), and never by where it lies.
5. **The manifest format becomes `golden-chain-console-manifest/2`,** with a
   `local` block. The page header and the export take the run header from
   the local block. The page's embedded spec is the hashed spec, so the page
   carries no absolute path. `TEMPLATE_VERSION` 7.
6. **Ingest dispatches on the manifest format.**
   - **`/2`:** the image files are found at the manifest's local paths. Each
     must hash to the hashed spec's sha256 for its id. A spec copy that holds
     a `path` or a `run_header` is refused.
   - **`/1`** (every console built before this revision): ingests as before,
     with `--code-at` at its build commit.
   - The build hash is still recomputed by ingest's own code (truth-set form
     8.5).
7. **Built consoles are not rebuilt.** Truth-set v3 build-a stays on record,
   unsigned (ruling on report 19, A-6).
8. Lock: `build-hash-r5-predictions-locked.txt`, BH1–BH5.

## Revision 6 (2026-11-17, from the ruling on report 19, A-6; carried into the console by the build agent, for the architect to read): the edge check counts the word's own ink

Report 19 dropped 37 of 191 truth-set v3 crops, mostly at the bottom edge. The
crop tool and the console's `clear_edges` check both failed on any ink at the
edge, and the next line's ink reaches a padded word crop. The architect ruled
that the edge check fails only when ink connected to the word itself touches
the edge, not any ink. This revision carries that rule into the console's
build check, so that the crop tool and the console apply one rule.

1. **An image entry may carry `word_box: [x0, y0, x1, y1]`** (pixel
   coordinates in that image, x1 and y1 exclusive) beside `clear_edges`. It is
   allowed only with `clear_edges`. It must be four integers with
   0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height, or the build fails.
2. **With `word_box`,** the ink on a named edge counts only if it lies in an
   8-connected ink component (same ink mask as Revision 3) that has a pixel
   inside the box. Ink belonging to any other component (the neighbouring
   line, a rule, a speck) does not fail the check.
3. **Without `word_box`,** the check is unchanged: any ink on a named edge
   fails it.
4. **One implementation.** The component test lives in `build.py`, and the
   crop tool imports it.
5. **`word_box` is in the hashed spec** (it is not a path or a run time). The
   page does not show it, and `TEMPLATE_VERSION` stays 7.
6. **Built consoles are not rebuilt.**
7. Lock: `italic-v4-predictions-locked.txt` (C, IV4, IV5).
