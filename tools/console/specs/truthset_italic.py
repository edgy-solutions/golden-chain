"""Spec builder, instance (vi): the truth-set v2 italic sign-off (Chris), kind "truthset-italic".

Usage: python tools/console/specs/truthset_italic.py <crops-dir> <out-spec.json>

<crops-dir> holds crops.json (written by tools/truthset_crops.py) and the PNGs it lists. Three sections: one
row per word (the word as the OCR cut it, then its printed line with the word boxed; italic, roman, or
"other, as written" with a note), one row for the whole p. 912 left column, one row for the foot of p. 914
left (column footnotes, yes or no). The rows keep crops.json order (a fixed shuffled order). The spec carries
no stratum, no slant and no word text. A "keyboard" block lets one key sign a word row (template v5). Fails
loud on a missing file or a sha256 that differs from crops.json.
Prediction: ~/.golden-chain/r14-q7-truthset-console-predictions-locked.txt
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import build  # noqa: E402
from build import Fail  # noqa: E402

PREDICTION = Path.home() / ".golden-chain" / "r14-q7-truthset-console-predictions-locked.txt"
MAGENTA = "#ff00ff"
INSTRUCTION = (
    "Sign from the pixels. Each word row shows the word as the OCR cut it, then its printed line with the word "
    "boxed (hide the overlay to see the line alone). Say whether the word is italic or roman. Choose "
    "\"other, as written\" with a short note for small caps, numerals, a damaged or wrongly cut word.\n\n"
    "The rows are in a fixed shuffled order; nothing on a row says how any measure classed it. After the words "
    "come two page rows. One sitting: all 198 rows.")
PLAIN_FACE = ('Choose "italic" if the word is printed in italic type, "roman" if it is ordinary non-italic type; if neither fits '
              '(small caps, a numeral, a damaged or wrongly cut word), choose "other, as written" and say what you see.')
PLAIN_COLUMN = ('Choose "italic throughout" if every line of the column is italic, "roman throughout" if every line is non-italic, '
                'or "mixed" if both appear. If none fits, choose "other, as written" and say what you see.')
PLAIN_WHAT = "Say in a few words what this column is. You must write something."
PLAIN_FOOT = ('Choose "yes" if the small type at the foot is footnotes to the column, "no" if it is not. '
              'If neither fits, choose "other, as written" and say what you see.')
HELP = [{"q": "Which keys sign a word?",
         "a": "i = italic, r = roman, o = other, as written (then type the note and press Enter). Each of i and "
              "r records the answer and moves to the next row. Backspace or ArrowLeft goes back one row; "
              "ArrowRight goes forward. Keys are ignored while you type in a box."}]


def field(fid, kind, label, options=None, required=True, *, plain):
    f = {"id": fid, "kind": kind, "label": label, "required": required, "proposed": None, "plain": plain}
    if options:
        f["options"] = list(options)
    return f


def check_png(crops_dir, name, sha):
    p = Path(crops_dir) / name
    if not p.is_file():
        raise Fail(f"crop file missing: {p}")
    if build.sha256_file(p) != sha:
        raise Fail(f"{p}: sha256 differs from crops.json")
    return p


def image(p, sha, caption, overlay=()):
    return {"id": p.stem, "path": str(p.resolve()), "sha256": sha, "caption": caption, "overlay": list(overlay)}


def make_spec(crops_dir):
    cj = Path(crops_dir) / "crops.json"
    if not cj.is_file():
        raise Fail(f"missing {cj}")
    data = json.loads(cj.read_text(encoding="utf-8"))
    images, word_rows = [], []
    for c in data["rows"]:
        pw = check_png(crops_dir, c["word_png"], c["word_sha256"])
        pl = check_png(crops_dir, c["line_png"], c["line_sha256"])
        x0, y0, x1, y1 = c["box"]
        images.append(image(pw, c["word_sha256"], "the word as the OCR cut it"))
        images.append(image(pl, c["line_sha256"], "its printed line, the word boxed",
                            [{"x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0, "colour": MAGENTA, "what": "the word"}]))
        word_rows.append({"id": c["id"], "key": c["key"],
                          "label": f"{c['id']} · p. {c['page']}, {c['region']} column · {c['key']}",
                          "image_ids": [pw.stem, pl.stem], "context": [],
                          "fields": [field("v", "radio", "This word is", ["italic", "roman"], plain=PLAIN_FACE)]})
    ex = data["extra"]
    p912 = check_png(crops_dir, ex["p912_left"]["png"], ex["p912_left"]["sha256"])
    p914 = check_png(crops_dir, ex["p914_left_foot"]["png"], ex["p914_left_foot"]["sha256"])
    images.append(image(p912, ex["p912_left"]["sha256"], "p. 912, the whole left column"))
    images.append(image(p914, ex["p914_left_foot"]["sha256"], "p. 914, left column, from above the small type to the foot"))
    if len({i["id"] for i in images}) != len(images):
        raise Fail("crops.json: repeated file name")
    sources = [{"path": str(cj.resolve()), "sha256": build.sha256_file(cj)}]
    if PREDICTION.is_file():
        sources.append({"path": str(PREDICTION), "sha256": build.sha256_file(PREDICTION)})
    rj = Path(crops_dir) / "run_header.json"
    run_header = json.loads(rj.read_text(encoding="utf-8")) if rj.is_file() else None
    return {"format": build.SPEC_FORMAT, "kind": "truthset-italic", "run_header": run_header,
            "title": "Truth-set v2: italic or roman, word by word", "signer": "Chris",
            "instruction": INSTRUCTION, "sources": sources, "images": images, "help": HELP,
            "keyboard": {"field": "v", "keys": {"i": "italic", "r": "roman", "o": build.OTHER}},
            "sections": [
                {"id": "words", "title": "The words", "image_ids": [], "rows": word_rows},
                {"id": "p912", "title": "Page 912, left column", "image_ids": [], "rows": [
                    {"id": "p912.left", "label": "p. 912, left column", "context": [], "image_ids": [p912.stem],
                     "fields": [field("face", "radio", "The column is", ["italic throughout", "roman throughout", "mixed"],
                                       plain=PLAIN_COLUMN),
                                field("what", "text", "What is this column? (in your words)", plain=PLAIN_WHAT)]}]},
                {"id": "ccel", "title": "Page 914, the foot of the left column", "image_ids": [],
                 "rows": [{"id": "ccel.p914-foot", "label": "p. 914, left column, foot", "context": [],
                           "image_ids": [p914.stem],
                           "fields": [field("v", "radio", "The small type at the foot of p. 914 left: column footnotes?",
                                            ["yes", "no"], plain=PLAIN_FOOT)]}]}],
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
