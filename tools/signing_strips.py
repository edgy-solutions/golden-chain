"""Ruled-row measurement and signing strips for the gutter rule, from a goat-yard locate_column_rule run.

Usage: python tools/signing_strips.py <run-dir> [<out-dir>] [--full N,N,...] [--foot N,N,...] [--native DIR]
       out-dir defaults to <run-dir>/strips-for-signing
       --full / --foot: pages given a full-length / foot strip (defaults 896,897,898 / 896,902,907,908)
       --native DIR: DIR holds native-resolution p{N}.png; each strip also gets a native crop of the same
       page region, <name>-native.png, overlays mapped by k = native/run per axis (fails if |kx-ky|/ky > 0.005)

<run-dir> holds locate_column_rule.json and pages/p{N}.png (8-bit grey,
ink 0, paper 255). Nothing is copied into the repo.

Part A, for every page in the run JSON, writes <out-dir>/ruled_rows.json:
- c(y) = slope*y + c0; window(y) = columns [round(c(y)-half_w-pad),
  round(c(y)+half_w+pad)] inclusive; ink = grey < 110.
- row y is RULED when the ink count in window(y) >= 2*half_w.
- F = first y >= Y_MIN with >= 45 of rows [y, y+49] ruled (None if none).
  (Y_MIN = header constants RULE_Y_TOP_PX of the run JSON, 700 if absent)
- L = last y < H with >= 45 of rows [y-49, y] ruled (None if none).
- ruled_frac_last_strip = fraction of rows of the page's last strip_fracs
  entry (y0, y1) that are ruled. The foot strip starts at the y0 of the
  third-from-last entry (the first if fewer than 3). Both, the frame width W
  and the run's line_h are recorded per page.
- empty strips: strip_fracs entries whose (y0+y1)/2 is no strips[].y_mid,
  with their peak frac.

Part B writes RGB signing strips (human viewing only; never sent to a
hosted model) and README.txt describing them.
Needs numpy, pillow.
"""

import datetime
import hashlib
import math
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from column_rule import REPO, Fail, clean_run, git_state  # noqa: E402

INK = 110
Y_MIN = 700
RUN = 50
NEED = 45
HALF = 300
K_TOL = 0.005
FOOT_PAGES = (896, 902, 907, 908)
FULL_PAGES = (896, 897, 898)
DEFINITIONS = [
    "c(y) = slope*y + c0",
    "window(y) = columns [round(c(y)-half_w-pad), round(c(y)+half_w+pad)] inclusive",
    "ink = grey < 110",
    "row y is RULED when the ink count in window(y) >= 2*half_w",
    "F = first y >= Y_MIN (header constants RULE_Y_TOP_PX, 700 if absent) such that >= 45 of rows [y, y+49] are ruled (None if none)",
    "L = last y < H such that >= 45 of rows [y-49, y] are ruled (None if none)",
    "ruled_frac_last_strip = fraction of rows y0..y1-1 of the page's last strip_fracs entry that are ruled",
    "foot strip starts at the y0 of the third-from-last strip_fracs entry (the first if fewer than 3)",
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


def y_min(data):
    return int(data.get("header", {}).get("constants", {}).get("RULE_Y_TOP_PX", Y_MIN))


def strip_bounds(page):
    """((y0, y1) of the last strip_fracs entry, y0 of the foot strip)."""
    sf = page["strip_fracs"]
    if not sf:
        raise Fail("no strip_fracs in run JSON")
    return (sf[-1]["y0"], sf[-1]["y1"]), sf[-3 if len(sf) >= 3 else 0]["y0"]


def measure(run_dir, data):
    res = {}
    ymin = y_min(data)
    for n, page in data["pages"].items():
        sp = page["split"]
        if "slope" not in sp:
            raise Fail(f"p{n}: no fit in run JSON (status {sp.get('status')})")
        grey = load_grey(run_dir / "pages" / f"p{n}.png")
        ruled = ruled_rows(grey < INK, sp["slope"], sp["c0"], sp["half_w"], sp["pad"])
        last, foot = strip_bounds(page)
        res[n] = {
            "H": int(grey.shape[0]),
            "W": int(grey.shape[1]),
            "line_h": page.get("line_h"),
            "F": first_run_start(ruled, ymin),
            "L": last_run_end(ruled),
            "last_strip": list(last),
            "foot_y0": foot,
            "ruled_frac_last_strip": frac_ruled(ruled, *last),
            "empty_strips": empty_strips(page),
        }
    return res


def draw_overlays(rgb, page, y_off, x_off, ky=1.0, kx=1.0, run_rows=None):
    """Overlays in run px, mapped by (ky, kx) (identity for the run strip); tick/dot sizes stay in px.
    y_off/x_off are the crop origin in output px; run_rows = (y0, y1 exclusive) of the run strip."""
    sp = page["split"]
    h, w = rgb.shape[:2]

    def my(v):
        return int(round(v * ky)) - y_off

    def mx(v):
        return int(round(v * kx)) - x_off

    def put(y0, y1, x0, x1, col):
        y0, y1, x0, x1 = max(y0, 0), min(y1, h), max(x0, 0), min(x1, w)
        if y0 < y1 and x0 < x1:
            rgb[y0:y1, x0:x1] = col

    red, blue, green, mag = (255, 0, 0), (0, 0, 255), (0, 160, 0), (255, 0, 255)
    for s in sp["strips"]:
        y = my(s["y_mid"])
        cx = mx(s["centre"])
        put(y - 1, y + 2, cx - 25 - 12, cx - 25, red)
        put(y - 1, y + 2, cx + 25, cx + 25 + 12, red)
    half_w, pad = sp["half_w"], sp["pad"]
    r0, r1 = run_rows if run_rows else (y_off, y_off + h)
    for yp in range(((r0 + 19) // 20) * 20, r1, 20):
        c = centre_at(yp, sp["slope"], sp["c0"])
        for xc in (c - half_w - pad - 6, c + half_w + pad + 6):
            x, yy = mx(xc), my(yp)
            put(yy - 1, yy + 2, x - 1, x + 2, blue)
    for e in page["strip_fracs"]:
        y = my(e["y0"])
        put(y - 1, y + 2, 0, 20, green)
        put(y - 1, y + 2, w - 20, w, green)
    ye = my(sp["y_range"][1])
    put(ye - 1, ye + 2, 0, 20, mag)
    put(ye - 1, ye + 2, w - 20, w, mag)


def native_crop(native_dir, n, grey_shape, y0, y1, x0, x1):
    """Native grey crop of run rows y0..y1-1, cols x0..x1-1 -> (crop, k_y, k_x, rows, cols, frame_wh)."""
    path = Path(native_dir) / f"p{n}.png"
    if not path.is_file():
        raise Fail(f"p{n}: native page missing: {path}")
    nat = load_grey(path)
    h, w = grey_shape
    hn, wn = nat.shape
    ky, kx = hn / h, wn / w
    if abs(kx - ky) / ky > K_TOL:
        raise Fail(f"p{n}: native/run aspect mismatch k_x={kx:.4f} k_y={ky:.4f}")
    r0, r1 = math.floor(y0 * ky), min(hn - 1, math.ceil(y1 * ky) - 1)
    c0, c1 = math.floor(x0 * kx), min(wn - 1, math.ceil(x1 * kx) - 1)
    return nat[r0:r1 + 1, c0:c1 + 1], ky, kx, [r0, r1], [c0, c1], [wn, hn]


def strip(run_dir, data, n, y0, name, out_dir, native_dir=None):
    """Writes the run strip (and the native one if native_dir); returns the README entries."""
    page = data["pages"][str(n)]
    grey = load_grey(run_dir / "pages" / f"p{n}.png")
    h, w = grey.shape
    xdiv = page["geometry"]["xdiv"]
    x0, x1 = max(xdiv - HALF, 0), min(xdiv + HALF, w)
    rgb = np.stack([grey[y0:h, x0:x1]] * 3, axis=-1).copy()
    draw_overlays(rgb, page, y0, x0)
    Image.fromarray(rgb, "RGB").save(out_dir / name)
    lh = (page.get("line_h") or {}).get("page_line_h")
    out = [{"file": name, "page": n, "rows": [y0, h - 1], "cols": [x0, x1 - 1],
            "size_wh": [rgb.shape[1], rgb.shape[0]], "frame_wh": [w, h], "line_h": lh}]
    if native_dir is not None:
        crop, ky, kx, rows, cols, fwh = native_crop(native_dir, n, grey.shape, y0, h, x0, x1)
        nrgb = np.stack([crop] * 3, axis=-1).copy()
        draw_overlays(nrgb, page, rows[0], cols[0], ky, kx, (y0, h))
        nname = name[:-4] + "-native.png"
        Image.fromarray(nrgb, "RGB").save(out_dir / nname)
        out.append({"file": nname, "page": n, "rows": rows, "cols": cols,
                    "size_wh": [nrgb.shape[1], nrgb.shape[0]], "frame_wh": fwh,
                    "native": True, "run_rows": [y0, h - 1], "k": ky})
    return out


README_LEGEND = """Overlay legend:
  red     = cluster centre per strip (two 12x3 px ticks at y_mid, 25 px left and right of the centre; the rule is not covered)
  blue    = fitted band edges (dots every 20 rows at c(y) -/+ (half_w + pad + 6))
  green   = strip boundaries (20 px ticks at both image edges: {ticks})
  magenta = y_end per page (20 px ticks at both image edges: {yends})

Run-2 strips for 897/898 already exist at
~/.golden-chain/column-rule-2026-10-25/strips/gutter-p897.png and gutter-p898.png
(different method; left alone).
"""


def write_readme(out_dir, made, data):
    lines = ["Signing strips (page pixel coordinates; rows/cols inclusive).", ""]
    for m in made:
        if m.get("native"):
            lines.append(f"{m['file']}: page {m['page']}, rows {m['rows'][0]}..{m['rows'][1]}, "
                         f"cols {m['cols'][0]}..{m['cols'][1]}, page {m['frame_wh'][0]} x {m['frame_wh'][1]} px (native), "
                         f"maps run rows {m['run_rows'][0]}..{m['run_rows'][1]} x k={m['k']:.4f}, "
                         "native line height not measured here")
            continue
        lh = "line height n/a" if m["line_h"] is None else f"line height {m['line_h']} px"
        lines.append(f"{m['file']}: page {m['page']}, rows {m['rows'][0]}..{m['rows'][1]}, "
                     f"cols {m['cols'][0]}..{m['cols'][1]}, page {m['frame_wh'][0]} x {m['frame_wh'][1]} px, {lh}")
    nums = list(dict.fromkeys(m["page"] for m in made))
    ticks = sorted({e["y0"] for n in nums for e in data["pages"][str(n)]["strip_fracs"]})
    yends = "; ".join(f"p{n} {data['pages'][str(n)]['split']['y_range'][1]}" for n in nums)
    legend = README_LEGEND.format(ticks=", ".join(map(str, ticks)), yends=yends)
    (out_dir / "README.txt").write_text("\n".join(lines) + "\n\n" + legend)


def parse(argv):
    argv, opts = list(argv), {"full": FULL_PAGES, "foot": FOOT_PAGES}
    for flag in ("full", "foot"):
        if f"--{flag}" in argv:
            i = argv.index(f"--{flag}")
            try:
                opts[flag] = tuple(int(x) for x in argv[i + 1].split(","))
            except (IndexError, ValueError):
                raise Fail(f"--{flag} needs N,N,...")
            del argv[i:i + 2]
    native = None
    if "--native" in argv:
        i = argv.index("--native")
        if i + 1 >= len(argv):
            raise Fail("--native needs DIR")
        native = argv[i + 1]
        del argv[i:i + 2]
    if len(argv) not in (2, 3):
        raise Fail(__doc__)
    return argv, opts["full"], opts["foot"], native


def main(argv):
    git_start = git_state(REPO)
    argv, full_pages, foot_pages, native = parse(argv)
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
        "native_dir": native,
        "definitions": DEFINITIONS,
    }
    git_end = git_state(REPO)
    header.update({"golden_chain_git_start": git_start, "golden_chain_git_end": git_end,
                   "clean_run": clean_run(git_start, git_end)})
    (out_dir / "ruled_rows.json").write_text(
        json.dumps({"header": header, "pages": res}, indent=1))
    for n, r in res.items():
        print(n, r["F"], r["L"], f"{r['ruled_frac_last_strip']:.3f}",
              [e["y0"] for e in r["empty_strips"]])

    made = []
    for n in full_pages:
        made += strip(run_dir, data, n, 0, f"p{n}-gutter-full.png", out_dir, native)
    for n in foot_pages:
        made += strip(run_dir, data, n, res[str(n)]["foot_y0"], f"p{n}-foot.png", out_dir, native)
    write_readme(out_dir, made, data)
    for m in made:
        print(m["file"], m["size_wh"])


if __name__ == "__main__":
    try:
        main(sys.argv)
    except Fail as e:
        sys.exit(f"signing_strips: {e}")
