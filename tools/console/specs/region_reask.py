"""Spec builder, instance (vii): the p. 914 foot re-ask, on the whole left column.

Usage: python tools/console/specs/region_reask.py <crops-dir> <ocr-run-dir> <out-spec.json>

<crops-dir> holds crops.json (tools/truthset_crops.py) and run_header.json; <ocr-run-dir>/regions/p914-left.png
is the whole left column, which must hash to crops.json's input entry. One row, one image (the whole column,
as is), one magenta box from the measured boundary to the foot. The row carries a region_question, so build
refuses a crop that does not show enough surroundings. Fails loud on a missing file or a sha256 mismatch.
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent.parent))
import build  # noqa: E402
from build import Fail  # noqa: E402
from truthset_crops import FOOT_PAD  # noqa: E402

PREDICTION = Path.home() / ".golden-chain" / "p914-reask-predictions-locked.txt"
REGION = "regions/p914-left.png"
PLAIN_YN = ('Choose "yes" if the small type at the foot is footnotes to the column, "no" if it is not. '
            'If neither fits, choose "other, as written" and say what you see.')
INSTRUCTION = (
    "Sign from the pixels. This re-asks the p. 914 foot row of the truth-set sitting (8afafecd34665b14), "
    "whose crop began at the small type and showed nothing above it: that verdict is recorded as a crop fault. "
    "Here is the whole left column, fit to the window; zoom in as needed. The magenta box starts at the "
    "measured boundary (hide the overlay to see the page alone). Compare the type inside the box with the "
    "body text above it, and look for note numbers. Answer yes or no, or 'other, as written' with what it "
    "is. If you cannot tell, choose fault or abstain and say why.")
HELP = [{"q": "What if the image does not show enough?",
         "a": "If the image does not show enough to judge, that is a fault, not a no."}]


def make_spec(crops_dir, ocr_dir):
    cj = Path(crops_dir) / "crops.json"
    if not cj.is_file():
        raise Fail(f"missing {cj}")
    data = json.loads(cj.read_text(encoding="utf-8"))
    png = Path(ocr_dir) / REGION
    if not png.is_file():
        raise Fail(f"missing {png}")
    sha = build.sha256_file(png)
    if sha != data["input"].get(REGION):
        raise Fail(f"{png}: sha256 differs from crops.json input entry")
    W, H = build.png_wh(png.read_bytes())
    boundary_y = data["extra"]["p914_left_foot"]["box_region"][1] + FOOT_PAD
    if not 0 < boundary_y < H:
        raise Fail(f"boundary {boundary_y} is outside the region height {H}")
    img = {"id": "p914-left", "path": str(png.resolve()), "sha256": sha, "caption": "p. 914, the whole left column",
           "overlay": [{"x": 0, "y": boundary_y, "w": W, "h": H - boundary_y, "colour": "#ff00ff",
                        "what": "the CCEL-moved block, as measured (top edge = measured boundary)"}]}
    row = {"id": "p914.left-foot", "label": "p. 914, left column: the small type at the foot",
           "image_ids": [img["id"]], "context": [],
           "fields": [{"id": "v", "kind": "radio", "required": True, "proposed": None,
                       "label": "The small type at the foot of p. 914 left: column footnotes?",
                       "options": ["yes", "no"], "plain": PLAIN_YN}],
           "region_question": {"image_id": img["id"], "roi": [0, boundary_y, W, H], "source_wh": [W, H],
                               "crop_box": [0, 0, W, H]}}
    sources = [{"path": str(cj.resolve()), "sha256": build.sha256_file(cj)},
               {"path": str(png.resolve()), "sha256": sha}]
    if PREDICTION.is_file():
        sources.append({"path": str(PREDICTION), "sha256": build.sha256_file(PREDICTION)})
    rh = Path(crops_dir) / "run_header.json"
    return {"format": build.SPEC_FORMAT, "kind": "region-reask", "title": "p. 914 foot: the re-ask",
            "signer": "Chris", "instruction": INSTRUCTION, "sources": sources,
            "run_header": json.loads(rh.read_text(encoding="utf-8")) if rh.is_file() else None,
            "images": [img],
            "sections": [{"id": "foot", "title": "The p. 914 foot", "text": "", "image_ids": [], "rows": [row]}],
            "withheld": [], "help": HELP, "signature": {"fields": ["name", "date"]}}


def main(argv):
    if len(argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        build.write_spec(argv[2], make_spec(argv[0], argv[1]))
    except (Fail, KeyError) as ex:
        print(f"FAIL: {ex!r}" if isinstance(ex, KeyError) else f"FAIL: {ex}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
