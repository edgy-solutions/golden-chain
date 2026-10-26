# ADR-0006: Sign from pixels in a self-contained console, bound by hashes

- Status: Proposed
- Date proposed: 2026-10-25
- Date ratified:
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
      and modality selectors (the architect) → `data/plumb-line.ttl`,
      after ratification (open point 1);
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

## Open points

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
