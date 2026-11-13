"""Spec builder, instance (v): the Q11 wide-gutter slabs sign-off (Chris).

Usage: python tools/console/specs/q11_crops.py <crops-dir> <out-spec.json>

<crops-dir> holds q11_crops.json (written by tools/q11_crops.py) and the PNGs it lists. One section, one
row per crop (pp. 913, 915), three fields each: what the left column holds, what the right column holds
(checkboxes), a note. Image ids are the PNG file stems. Fails loud on a missing file or a sha256 that
differs from q11_crops.json.
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import build  # noqa: E402
from build import Fail  # noqa: E402

PREDICTION = Path.home() / ".golden-chain" / "gutter-maxima-predictions-locked.txt"
SIDE = ["full-measure text on every line", "a section head", "a blank line",
        "a short line (paragraph end, or other)", "something else (say in the note)"]
INSTRUCTION = (
    "Sign from the pixels. Each image is the raw page (no threshold) at the scale the gutter was measured. "
    "The magenta lines bound the slab; the blue bars show the measured gutter (left white + rule + right "
    "white). Hide the overlay to see the page alone. For each slab, say what each column holds between the "
    "magenta lines.")


def field(fid, kind, label, options=None, required=True):
    f = {"id": fid, "kind": kind, "label": label, "required": required, "proposed": None}
    if options:
        f["options"] = list(options)
    return f


def image_entries(crops_dir, data):
    out = []
    for c in data["crops"]:
        p = Path(crops_dir) / c["file"]
        if not p.is_file():
            raise Fail(f"crop file missing: {p}")
        if build.sha256_file(p) != c["sha256"]:
            raise Fail(f"{p}: sha256 differs from q11_crops.json")
        s0, s1 = c["slab_rows_in_frame"]
        out.append({"id": p.stem, "path": str(p.resolve()), "sha256": c["sha256"],
                    "caption": f"p.{c['page']} slab {c['slab']}: rows {c['rows'][0]}-{c['rows'][1]} of the "
                               f"6.947 frame (slab rows {s0}-{s1} between the magenta lines)",
                    "frame": {"rows": c["rows"], "cols": c["cols"], "frame_wh": c["frame_wh"], "k": 1.0},
                    "overlay": c.get("overlay", [])})
    if len({i["id"] for i in out}) != len(out):
        raise Fail("q11_crops.json: repeated file name")
    return out


def make_spec(crops_dir):
    qj = Path(crops_dir) / "q11_crops.json"
    if not qj.is_file():
        raise Fail(f"missing {qj}")
    data = json.loads(qj.read_text(encoding="utf-8"))
    images = image_entries(crops_dir, data)
    rows = []
    for c, im in zip(data["crops"], images):
        m = c["measured"]
        rows.append({"id": f"p{c['page']}-slab{c['slab']}",
                     "label": f"p.{c['page']}, slab {c['slab']} (gutter {m['gutter']} px: left white "
                              f"{m['left_white']}, right white {m['right_white']})",
                     "image_ids": [im["id"]], "context": [], "fields": [
                         field("left", "checkbox", "Left column, between the lines, holds", SIDE),
                         field("right", "checkbox", "Right column, between the lines, holds", SIDE),
                         field("note", "text", "Note (optional)", required=False)]})
    sources = [{"path": str(qj.resolve()), "sha256": build.sha256_file(qj)}]
    if PREDICTION.is_file():
        sources.append({"path": str(PREDICTION), "sha256": build.sha256_file(PREDICTION)})
    return {"format": build.SPEC_FORMAT, "kind": "q11-crops",
            "title": "Q11: the two wide-gutter slabs (pp. 913, 915)", "signer": "Chris",
            "instruction": INSTRUCTION, "sources": sources, "run_header": data["header"], "images": images,
            "sections": [{"id": "slabs", "title": "What lies beside the wide gutter", "text": "",
                          "image_ids": [], "rows": rows}],
            "withheld": [], "help": [], "signature": {"fields": ["name", "date"]}}


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
