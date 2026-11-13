"""Q11 crops: the two wide-gutter slabs at 6.947 scale (pp. 913 slab 16, 915 slab 5), cut raw for signing.

Usage: python tools/q11_crops.py <gill.pdf> <run-json> <out-dir>

<run-json> is a column_rule.py --scale 6.947 run (column_rule.json). The tool checks the PDF sha256, the
scale (6.947) and slab_rows (235) against its header, re-renders each page, re-measures it with
column_rule.measure and fails unless the slab matches the run's entry. It writes, per target, the page rows
y-r .. y+2r (all columns) as an 8-bit grey PNG, unchanged pixels, no threshold, no drawing; then
q11_crops.json (header, per-crop frame, the run's and fresh entries, overlay rectangles in crop px) and
README.txt. Needs numpy, pillow, pypdfium2.
"""

import datetime
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import column_rule  # noqa: E402
from column_rule import OFFSET, REPO, Fail, clean_run, git_state  # noqa: E402

TARGETS = ((913, 16), (915, 5))
SCALE = 6.947
SLAB_ROWS = 235
KEYS = ("y", "rule", "rule_x", "rule_w", "left_white", "right_white", "gutter")
MAGENTA, BLUE = "#ff00ff", "#00b0ff"
PREDICTION = "~/.golden-chain/gutter-maxima-predictions-locked.txt"

README = """Q11 crops: the two wide-gutter slabs (p. 913 slab 16, p. 915 slab 5) at scale 6.947.

Each PNG is the raw page render (8-bit grey, as the renderer holds it): no threshold, nothing drawn into the
pixels. Rows are the slab's rows (y .. y+235) with one slab's height above and below. The overlay (magenta
lines at the slab's top and bottom row; blue bars for the measured gutter) is listed in q11_crops.json and
is drawn by the signing console, not in the pixels. Nobody but Chris views these images.
"""


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def crop_and_overlay(grey, entry, r):
    """(crop, [y0, y1], overlay) for the slab `entry`; Fails if the rows would be clipped."""
    H, W = grey.shape
    y = entry["y"]
    y0, y1 = y - r, y + 2 * r
    if y0 < 0 or y1 > H:
        raise Fail(f"slab y={y}: rows {y0}..{y1} fall outside the page (0..{H})")
    gx0, gw = entry["rule_x"] - entry["left_white"], entry["gutter"]
    overlay = [
        {"x": 0, "y": r - 2, "w": W, "h": 2, "colour": MAGENTA, "what": "slab top (row y)"},
        {"x": 0, "y": 2 * r, "w": W, "h": 2, "colour": MAGENTA, "what": f"slab bottom (row y+{r})"},
        {"x": gx0, "y": r - 8, "w": gw, "h": 4, "colour": BLUE, "what": "measured gutter, top"},
        {"x": gx0, "y": 2 * r + 4, "w": gw, "h": 4, "colour": BLUE, "what": "measured gutter, bottom"},
    ]
    return grey[y0:y1, :], [y0, y1], overlay


def check_remeasure(run_entry, fresh_entry):
    """Fails unless the fresh slab entry equals the run's on KEYS."""
    if fresh_entry is None:
        raise Fail(f"re-measure found no slab for run entry {run_entry}")
    if any(run_entry.get(k) != fresh_entry.get(k) for k in KEYS):
        raise Fail(f"re-measure differs: run {run_entry} vs fresh {fresh_entry}")
    return True


def main(argv):
    if len(argv) != 3:
        raise Fail(__doc__)
    import pypdfium2 as pdfium
    pdf_path, run_path, out = Path(argv[0]), Path(argv[1]).expanduser(), Path(argv[2])
    git_start = git_state(REPO)
    run = json.loads(run_path.read_text(encoding="utf-8"))
    h = run["header"]
    pdf_sha = sha256_file(pdf_path)
    if pdf_sha != h.get("pdf_sha256"):
        raise Fail("pdf sha256 differs from the run header's")
    if h.get("scale") != SCALE or h.get("slab_rows") != SLAB_ROWS:
        raise Fail(f"run scale/slab_rows {h.get('scale')}/{h.get('slab_rows')}, expected {SCALE}/{SLAB_ROWS}")
    r, (fw, fh) = SLAB_ROWS, h["frame_wh"]
    out.mkdir(parents=True, exist_ok=True)
    pdf = pdfium.PdfDocument(str(pdf_path))
    crops = []
    for p, n in TARGETS:
        found = [s for s in run["pages"][str(p)]["slabs"] if s["slab"] == n]
        if len(found) != 1:
            raise Fail(f"p.{p}: run has {len(found)} entries for slab {n}")
        entry = found[0]
        grey = column_rule.render(pdf, p, SCALE)
        if grey.shape != (fh, fw):
            raise Fail(f"p.{p}: render {grey.shape}, header frame (h, w) {(fh, fw)}")
        fm = [s for s in column_rule.measure(grey < 128, r)["slabs"] if s["slab"] == n]
        check_remeasure(entry, fm[0] if fm else None)
        crop, rows, overlay = crop_and_overlay(grey, entry, r)
        name = f"q11-p{p}-slab{n}.png"
        Image.fromarray(np.ascontiguousarray(crop), "L").save(out / name)
        if not np.array_equal(np.asarray(Image.open(out / name)), crop):
            raise Fail(f"{name}: written pixels differ from the page crop")
        crops.append({"file": name, "sha256": sha256_file(out / name), "page": p, "slab": n, "rows": rows,
                      "cols": [0, int(crop.shape[1])], "frame_wh": [fw, fh],
                      "slab_rows_in_frame": [entry["y"], entry["y"] + r], "measured": entry,
                      "remeasured": fm[0], "overlay": overlay})
    git_end = git_state(REPO)
    header = {
        "run": "q11-crops",
        "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "script_sha256": sha256_file(__file__), "pdf_sha256": pdf_sha,
        "source_run": {"path": str(run_path), "sha256": sha256_file(run_path), "utc": h.get("utc")},
        "scale": SCALE, "slab_rows": r, "frame_wh": [fw, fh], "pdf_offset": OFFSET,
        "prediction": PREDICTION,
        "golden_chain_git_start": git_start, "golden_chain_git_end": git_end,
        "clean_run": clean_run(git_start, git_end),
    }
    (out / "q11_crops.json").write_text(json.dumps({"header": header, "crops": crops}, indent=1, default=str),
                                         encoding="utf-8", newline="\n")
    (out / "README.txt").write_text(README, encoding="utf-8", newline="\n")
    print(json.dumps({"files": [c["file"] for c in crops], "sha256": [c["sha256"] for c in crops],
                      "shapes": [[c["rows"][1] - c["rows"][0], c["cols"][1]] for c in crops],
                      "remeasure_ok": True}))


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Fail as e:
        sys.exit(f"FAIL: {e}")
