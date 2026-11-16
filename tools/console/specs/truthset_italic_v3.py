"""Spec builder, instance (viii): the truth-set v3 italic sign-off (Chris), kind "truthset-italic-v3".

Usage: python tools/console/specs/truthset_italic_v3.py <crops-dir> <out-spec.json>

<crops-dir> holds crops.json (written by tools/truthset_crops_v3.py) and the PNGs it lists. One section, one row
per word: the word at its line's full height (the top and bottom edges must be free of ink, checked by the
build), then its printed line with the word boxed; "italic" or "roman" (or "other, as written" with a say), and
an optional note. The rows keep crops.json order (a fixed shuffled order). The spec carries no stratum, no
slant and no word text. A "keyboard" block lets one key sign a row (template v5). Fails loud on a missing file
or a sha256 that differs from crops.json.
Prediction: ~/.golden-chain/italic-v3-predictions-locked.txt (name only; never read here)
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import build  # noqa: E402
from build import Fail  # noqa: E402
import truthset_italic as v2  # noqa: E402  (its helpers and keyboard help; the v2 file is not changed)

PREDICTION = "~/.golden-chain/italic-v3-predictions-locked.txt"
INSTRUCTION = (
    "Sign from the pixels. Each row shows one word at the height of its printed line, then the line with the "
    "word boxed (hide the overlay to see the line alone). Say whether the word is italic or roman. Choose "
    "\"other, as written\" with a short note for small caps, numerals, a damaged or wrongly cut word.\n\n"
    "The rows are in a fixed shuffled order; nothing on a row says how any measure classed it.")
PLAIN_V = ('Is the word in the word image (also boxed in the line image) printed in italic, sloping type, or in roman, '
           'upright type? Choose "italic" or "roman"; if it is neither, part of each, or you cannot tell, choose '
           '"other, as written" and say what you see.')
PLAIN_NOTE = ('Optional: anything worth recording about this word or its images, such as a crop that cuts off part '
              'of the word or a word broken by a hyphen. Leave it empty if there is nothing to say.')


def make_spec(crops_dir):
    cj = Path(crops_dir) / "crops.json"
    if not cj.is_file():
        raise Fail(f"missing {cj}")
    data = json.loads(cj.read_text(encoding="utf-8"))
    images, rows = [], []
    for c in data["rows"]:
        pw = v2.check_png(crops_dir, c["word_png"], c["word_sha256"])
        pl = v2.check_png(crops_dir, c["line_png"], c["line_sha256"])
        x0, y0, x1, y1 = c["box"]
        iw = v2.image(pw, c["word_sha256"], "the word at the height of its printed line")
        iw["clear_edges"] = ["top", "bottom"]
        images.append(iw)
        images.append(v2.image(pl, c["line_sha256"], "its printed line, the word boxed",
                               [{"x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0, "colour": v2.MAGENTA, "what": "the word"}]))
        rows.append({"id": c["id"], "key": c["key"],
                     "label": f"{c['id']} · p. {c['page']}, {c['region']} column · {c['key']}",
                     "image_ids": [pw.stem, pl.stem], "context": [],
                     "fields": [v2.field("v", "radio", "This word is", ["italic", "roman"], plain=PLAIN_V),
                                v2.field("note", "text", "Note (optional)", required=False, plain=PLAIN_NOTE)]})
    if len({i["id"] for i in images}) != len(images):
        raise Fail("crops.json: repeated file name")
    sources = [{"path": str(cj.resolve()), "sha256": build.sha256_file(cj)}]
    rj = Path(crops_dir) / "run_header.json"
    run_header = json.loads(rj.read_text(encoding="utf-8")) if rj.is_file() else None
    return {"format": build.SPEC_FORMAT, "kind": "truthset-italic-v3", "run_header": run_header,
            "title": "Truth-set v3: italic or roman, word by word", "signer": "Chris",
            "instruction": INSTRUCTION, "sources": sources, "prediction": PREDICTION, "images": images,
            "help": v2.HELP,
            "keyboard": {"field": "v", "keys": {"i": "italic", "r": "roman", "o": build.OTHER}},
            "sections": [{"id": "words", "title": "The words", "image_ids": [], "rows": rows}],
            "withheld": [], "signature": {"fields": ["name", "date"]}}


def main(argv):
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        build.write_spec(argv[1], make_spec(argv[0]))
    except (Fail, KeyError) as ex:
        print(f"FAIL: {ex!r}" if isinstance(ex, KeyError) else f"FAIL: {ex}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
