"""Spec builder: the italic-spans sign-off (Chris), kind "italic-spans".

Usage: python tools/console/specs/italic_spans.py <crops-dir> <out-spec.json>

<crops-dir> holds crops.json (written by tools/italic_span_crops.py) and the PNGs it lists. One section, one row
per span: the band (a few printed lines, the span's words boxed, one box per printed line it touches), a radio
saying what the boxed words are, and an optional note. The rows keep crops.json order (a fixed shuffled order).
The spec carries no pairing, no reference and no word text; it fails if a crops.json row carries a key named
paired, paired_ref_key or ref (draw.json is never read here). Keyboard: letters a-g sign options 1-7 (the
keyboard check accepts single lowercase characters only, so not digits) and o is "other, as written". Fails loud
on a missing file or a sha256 that differs from crops.json.
Lock: docs/handoff/LOCK_italic_console_2026-11-26.md
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import build  # noqa: E402
from build import Fail  # noqa: E402
import truthset_italic as v2  # noqa: E402  (its helpers and colour; that file is not changed)

FORBIDDEN = ("paired", "paired_ref_key", "ref")
INSTRUCTION = (
    "Sign from the pixels. Each row shows a few printed lines from Gill's chapter on baptism, with a run of "
    "italic words boxed (it may run onto a second line). Say what the boxed words are. The rows are in a fixed "
    "shuffled order; nothing on a row says how any measure classed it.")
OPTIONS = ["a Scripture quotation, with its reference after it",
           "a Scripture quotation, with its reference before it",
           "a quotation, with no reference near it",
           "not a quotation: emphasis",
           "not a quotation: a foreign word",
           "not a quotation: a title",
           "not a quotation: other"]
PLAIN_V = ("Choose one of: " + "; ".join(OPTIONS) + '. "Reference" means a Scripture reference such as a book, '
           'chapter and verse, printed near the words. If the box is not on italic words, or you cannot tell, '
           'choose "other, as written" and say what you see.')
PLAIN_NOTE = ('Optional: anything worth recording about these words or their image, such as a crop that cuts off '
              'part of the words or a box in the wrong place. Leave it empty if there is nothing to say.')
KEYS = dict(zip("abcdefg", OPTIONS))
HELP = [{"q": "Which keys sign a row?",
         "a": "a to g choose the seven options in the order listed (a is the first, g the seventh); o = other, as "
              "written (then type the note and press Enter). Each of a to g records the answer and moves to the "
              "next row. Backspace or ArrowLeft goes back one row; ArrowRight goes forward. Keys are ignored "
              "while you type in a box."}]


def make_spec(crops_dir):
    cj = Path(crops_dir) / "crops.json"
    if not cj.is_file():
        raise Fail(f"missing {cj}")
    data = json.loads(cj.read_text(encoding="utf-8"))
    images, rows = [], []
    for c in data["rows"]:
        bad = [k for k in FORBIDDEN if k in c]
        if bad:
            raise Fail(f"crops.json: row {c.get('id')} carries {bad}; the console must not know the pairing")
        p = v2.check_png(crops_dir, c["png"], c["sha256"])
        overlay = [{"x": b["x"], "y": b["y"], "w": b["w"], "h": b["h"], "colour": v2.MAGENTA,
                    "what": "the italic words"} for b in c["boxes"]]
        images.append(v2.image(p, c["sha256"], "the span's printed lines, the italic words boxed", overlay))
        rows.append({"id": c["id"], "key": c["key"],
                     "label": f"{c['id']} · p. {c['page']}, {c['region']} column",
                     "image_ids": [p.stem], "context": [],
                     "fields": [v2.field("v", "radio", "The boxed words are", OPTIONS, plain=PLAIN_V),
                                v2.field("note", "text", "Note (optional)", required=False, plain=PLAIN_NOTE)]})
    if len({i["id"] for i in images}) != len(images):
        raise Fail("crops.json: repeated file name")
    sources = [{"path": str(cj.resolve()), "sha256": build.sha256_file(cj)}]
    rj = Path(crops_dir) / "run_header.json"
    run_header = json.loads(rj.read_text(encoding="utf-8")) if rj.is_file() else None
    return {"format": build.SPEC_FORMAT, "kind": "italic-spans", "run_header": run_header,
            "title": "Gill's italic: what each span is", "signer": "Chris",
            "instruction": INSTRUCTION, "sources": sources, "images": images, "help": HELP,
            "keyboard": {"field": "v", "keys": {**KEYS, "o": build.OTHER}},
            "sections": [{"id": "spans", "title": "The spans", "image_ids": [], "rows": rows}],
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
