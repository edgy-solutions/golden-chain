"""Ruled-row measurement and signing strips for the gutter rule, from a goat-yard locate_column_rule run.

Usage: python tools/signing_strips.py <run-dir> [<out-dir>]
       out-dir defaults to <run-dir>/strips-for-signing

<run-dir> holds locate_column_rule.json and pages/p{N}.png (8-bit grey,
ink 0, paper 255). Nothing is copied into the repo.

Part A, for every page in the run JSON, writes <out-dir>/ruled_rows.json:
- c(y) = slope*y + c0; window(y) = columns [round(c(y)-half_w-pad),
  round(c(y)+half_w+pad)] inclusive; ink = grey < 110.
- row y is RULED when the ink count in window(y) >= 2*half_w.
- F = first y >= 700 with >= 45 of rows [y, y+49] ruled (None if none).
- L = last y < H with >= 45 of rows [y-49, y] ruled (None if none).
- ruled_frac_last_strip = fraction of rows 7000..7299 that are ruled.
- empty strips: strip_fracs entries whose (y0+y1)/2 is no strips[].y_mid,
  with their peak frac.

Part B writes RGB signing strips (human viewing only; never sent to a
hosted model) and README.txt describing them.
Needs numpy, pillow.
"""

import datetime
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from column_rule import Fail  # noqa: E402

INK = 110
Y_MIN = 700
RUN = 50
NEED = 45
LAST_STRIP = (7000, 7300)
HALF = 300
FOOT_PAGES = (896, 902, 907, 908)
FULL_PAGES = (896, 897, 898)
FOOT_Y0 = 6700
DEFINITIONS = [
    "c(y) = slope*y + c0",
    "window(y) = columns [round(c(y)-half_w-pad), round(c(y)+half_w+pad)] inclusive",
    "ink = grey < 110",
    "row y is RULED when the ink count in window(y) >= 2*half_w",
    "F = first y >= 700 such that >= 45 of rows [y, y+49] are ruled (None if none)",
    "L = last y < H such that >= 45 of rows [y-49, y] are ruled (None if none)",
    "ruled_frac_last_strip = fraction of rows 7000..7299 that are ruled",
    "empty strips = strip_fracs entries whose (y0+y1)/2 is not any strips[].y_mid, with peak frac",
]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def centre_at(y, slope, c0):
    return slope * y + c0


def ruled_rows(ink, slope, c0, half_w, pad):
    """Boolean per row: ink count in the fitted window >= 2*half_w."""
    h, w = ink.shape
    out = np.zeros(h, dtype=bool)
    for y in range(h):
        c = centre_at(y, slope, c0)
        lo = max(round(c - half_w - pad), 0)
        hi = min(round(c + half_w + pad), w - 1)
        if hi >= lo:
            out[y] = int(ink[y, lo:hi + 1].sum()) >= 2 * half_w
    return out


def first_run_start(ruled, y_min=Y_MIN):
    """F: first y >= y_min with >= NEED of rows [y, y+RUN-1] ruled."""
    cs = np.concatenate([[0], np.cumsum(ruled.astype(int))])
    for y in range(y_min, len(ruled) - RUN + 1):
        if cs[y + RUN] - cs[y] >= NEED:
            return y
    return None


def last_run_end(ruled):
    """L: last y < H with >= NEED of rows [y-RUN+1, y] ruled."""
    cs = np.concatenate([[0], np.cumsum(ruled.astype(int))])
    for y in range(len(ruled) - 1, RUN - 2, -1):
        if cs[y + 1] - cs[y + 1 - RUN] >= NEED:
            return y
    return None


def frac_ruled(ruled, y0, y1):
    return float(ruled[y0:y1].mean())


def empty_strips(page):
    mids = {s["y_mid"] for s in page["split"].get("strips", [])}
    out = []
    for e in page["strip_fracs"]:
        if (e["y0"] + e["y1"]) / 2 not in mids:
            out.append({"y0": e["y0"], "y1": e["y1"], "peak_frac": float(max(e["frac"]))})
    return out


def load_grey(path):
    img = np.asarray(Image.open(path))
    if img.ndim != 2:
        raise Fail(f"{path}: not single-channel grey")
    return img


def measure(run_dir, data):
    res = {}
    for n, page in data["pages"].items():
        sp = page["split"]
        if "slope" not in sp:
            raise Fail(f"p{n}: no fit in run JSON (status {sp.get('status')})")
        grey = load_grey(run_dir / "pages" / f"p{n}.png")
        ruled = ruled_rows(grey < INK, sp["slope"], sp["c0"], sp["half_w"], sp["pad"])
        res[n] = {
            "H": int(grey.shape[0]),
            "F": first_run_start(ruled),
            "L": last_run_end(ruled),
            "ruled_frac_last_strip": frac_ruled(ruled, *LAST_STRIP),
            "empty_strips": empty_strips(page),
        }
    return res


def draw_overlays(rgb, page, y_off, x_off):
    sp = page["split"]
    h, w = rgb.shape[:2]

    def put(y0, y1, x0, x1, col):
        y0, y1, x0, x1 = max(y0, 0), min(y1, h), max(x0, 0), min(x1, w)
        if y0 < y1 and x0 < x1:
            rgb[y0:y1, x0:x1] = col

    red, blue, green, mag = (255, 0, 0), (0, 0, 255), (0, 160, 0), (255, 0, 255)
    for s in sp["strips"]:
        y = int(round(s["y_mid"])) - y_off
        cx = int(round(s["centre"])) - x_off
        put(y - 1, y + 2, cx - 25 - 12, cx - 25, red)
        put(y - 1, y + 2, cx + 25, cx + 25 + 12, red)
    half_w, pad = sp["half_w"], sp["pad"]
    for yp in range(((y_off + 19) // 20) * 20, y_off + h, 20):
        c = centre_at(yp, sp["slope"], sp["c0"])
        for xc in (c - half_w - pad - 6, c + half_w + pad + 6):
            x = int(round(xc)) - x_off
            put(yp - y_off - 1, yp - y_off + 2, x - 1, x + 2, blue)
    for e in page["strip_fracs"]:
        y = e["y0"] - y_off
        put(y - 1, y + 2, 0, 20, green)
        put(y - 1, y + 2, w - 20, w, green)
    ye = sp["y_range"][1] - y_off
    put(ye - 1, ye + 2, 0, 20, mag)
    put(ye - 1, ye + 2, w - 20, w, mag)


def strip(run_dir, data, n, y0, name, out_dir):
    page = data["pages"][str(n)]
    grey = load_grey(run_dir / "pages" / f"p{n}.png")
    h, w = grey.shape
    xdiv = page["geometry"]["xdiv"]
    x0, x1 = max(xdiv - HALF, 0), min(xdiv + HALF, w)
    rgb = np.stack([grey[y0:h, x0:x1]] * 3, axis=-1).copy()
    draw_overlays(rgb, page, y0, x0)
    Image.fromarray(rgb, "RGB").save(out_dir / name)
    return {"file": name, "page": n, "rows": [y0, h - 1], "cols": [x0, x1 - 1],
            "size_wh": [rgb.shape[1], rgb.shape[0]]}


README_LEGEND = """Overlay legend:
  red     = cluster centre per strip (two 12x3 px ticks at y_mid, 25 px left and right of the centre; the rule is not covered)
  blue    = fitted band edges (dots every 20 rows at c(y) -/+ (half_w + pad + 6))
  green   = strip boundaries (20 px ticks at both image edges: 700, 1000, ..., 7300)
  magenta = y_end = 7350 (20 px ticks at both image edges)

Run-2 strips for 897/898 already exist at
~/.golden-chain/column-rule-2026-10-25/strips/gutter-p897.png and gutter-p898.png
(different method; left alone).
"""


def write_readme(out_dir, made):
    lines = ["Signing strips (page pixel coordinates; rows/cols inclusive).", ""]
    for m in made:
        lines.append(f"{m['file']}: page {m['page']}, rows {m['rows'][0]}..{m['rows'][1]}, "
                     f"cols {m['cols'][0]}..{m['cols'][1]}")
    (out_dir / "README.txt").write_text("\n".join(lines) + "\n\n" + README_LEGEND)


def main(argv):
    if len(argv) not in (2, 3):
        raise Fail(__doc__)
    run_dir = Path(argv[1]).expanduser()
    out_dir = Path(argv[2]).expanduser() if len(argv) == 3 else run_dir / "strips-for-signing"
    jpath = run_dir / "locate_column_rule.json"
    data = json.loads(jpath.read_text())
    out_dir.mkdir(parents=True, exist_ok=True)

    res = measure(run_dir, data)
    header = {
        "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "script_sha256": sha256(__file__),
        "run_json_sha256": sha256(jpath),
        "definitions": DEFINITIONS,
    }
    (out_dir / "ruled_rows.json").write_text(
        json.dumps({"header": header, "pages": res}, indent=1))
    for n, r in res.items():
        print(n, r["F"], r["L"], f"{r['ruled_frac_last_strip']:.3f}",
              [e["y0"] for e in r["empty_strips"]])

    made = []
    for n in FULL_PAGES:
        made.append(strip(run_dir, data, n, 0, f"p{n}-gutter-full.png", out_dir))
    for n in FOOT_PAGES:
        made.append(strip(run_dir, data, n, FOOT_Y0, f"p{n}-foot.png", out_dir))
    write_readme(out_dir, made)
    for m in made:
        print(m["file"], m["size_wh"])


if __name__ == "__main__":
    try:
        main(sys.argv)
    except Fail as e:
        sys.exit(f"signing_strips: {e}")
