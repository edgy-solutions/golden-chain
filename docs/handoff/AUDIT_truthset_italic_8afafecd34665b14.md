# Audit standoff: truth-set sitting 8afafecd34665b14

- **About:** [SIGNED_truthset_italic_8afafecd34665b14.md](SIGNED_truthset_italic_8afafecd34665b14.md). That record stands as signed and is not edited.
- **Form:** goat-yard truth-set form v1 (§4 rule 4, "keep the route back to the pixels open"; §5, `fault`; §9, "Adjudication is a standoff record, never an edit").
- **Join:** `(build_hash, row_id)`. The build hash is `8afafecd34665b147d9266fc0d57c2db9aedbf9872dce8ff5339123fa5a8fa46`.
- **Signed record read:** the local signed JSON, sha256 `41e86f3d9dab0e68aba08efb8a69bdf068bf9ffda6cf1034ffb83cbfb324b311`. Its export sha256 is `f7fd95ece12e842927a57bee6d3e6585f5e6d1d76642ea5949e198cf8f623c43`, the same as in the committed record.
- **Written:** 2026-11-15, by the build agent, on Chris's direction.
- **Machine-readable:** [AUDIT_truthset_italic_8afafecd34665b14.json](AUDIT_truthset_italic_8afafecd34665b14.json).

## A-1. Row `ccel.p914-foot`: crop fault, verdict not usable

| | |
|---|---|
| Signed | `v` = **no**; note: "I might be wrong - can see the rest of the page" |
| Disposition | **fault** (§5: the input was not fit to read). The signed "no" is **not usable** as evidence. |
| Basis | Chris, 2026-11-15, relayed: the note means "can**not** see the rest of the page". He confirms the crop did not show enough to judge. It begins at the small type (30 px above the first word of the CCEL-moved blocks), with no body text above for comparison and no note number in view. |
| Consequence | Report 16's SI8 miss and its Q-1 rest on this verdict. Q-1's proposal (withdraw F-1's footnote reading) is **superseded**. F-1 stands as a finding from numbers, **unconfirmed from pixels**. |
| Re-ask | A one-row console showing the whole left column of p. 914, with the measured boundary as a hideable overlay (report 17). |
| Not evidence | After signing, a model outside this repo viewed this crop. Its reading is **not used** here or anywhere, and it is not a verdict. |

## A-2. Row notes the committed record leaves out

`markdown_truthset` at commit `c4c12ca` did not render row notes. The committed Markdown is not rewritten, so the notes are carried here verbatim from the signed JSON. 17 word rows carry a note.

The stratum comes from `candidates.json` and was never shown on the console. "Disagrees" means a word the measure called slanted that Chris signed roman (11 such rows in all).

| Row | Signed | Stratum | Note (Chris, verbatim) | Class | Disagrees |
|---|---|---|---|---|---|
| w017 | roman | slanted | crop cut off at the bottom. | clip | yes |
| w019 | roman | upright | crop cut off at the bottom. | clip | |
| w041 | roman | slanted | crop cut off at the bottom. | clip | yes |
| w043 | roman | upright | crop cuts off top of 't' | clip | |
| w059 | roman | upright | hyphenated word | hyphen | |
| w061 | roman | upright | hyphenated word | hyphen | |
| w067 | italic | slanted | crop chopped top of word | clip | |
| w074 | italic | slanted | word hyphenated | hyphen | |
| w091 | italic | slanted | word hyphenated | hyphen | |
| w121 | roman | upright | word hyphenated | hyphen | |
| w153 | italic | slanted | word hyphenated | hyphen | |
| w154 | roman | slanted | top of word clipped | clip | yes |
| w155 | italic | slanted | hyphenated word | hyphen | |
| w166 | roman | slanted | cropped goes into adjacent line | clip | yes |
| w172 | roman | slanted | clipped top of word | clip | yes |
| w182 | roman | upright | top of word clipped | clip | |
| w193 | roman | edge | clipped word top | clip | |

Two page rows:
- `p912.left`: face **mixed**, what "mostly roman with some part italic", no note.
- `ccel.p914-foot`: see A-1.

**Reading:**
- 10 rows have clip notes and 7 have hyphenation notes.
- **5 of the 11 disagreements** (w017, w041, w154, w166, w172) carry a clip note. This corrects report 16's F-4, which read the 11 without their notes.
- No disposition is changed for the word rows. Each verdict stands as signed. The note says the crop was imperfect, not that the reading failed. Whether a clipped crop's verdict counts toward a measure's score is a question for the architect (report 17).
