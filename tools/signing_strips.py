"""Signing strips of the gutter rule, cut from a goat-yard locate_column_rule run.

Usage: python tools/signing_strips.py <run-dir> [<out-dir>] [--full N,N,...] [--foot N,N,...] [--native DIR]
       out-dir defaults to <run-dir>/strips-for-signing
       --full / --foot: pages given a full-length / foot strip (defaults 896,897,898 / 896,902,907,908)
       --native DIR: DIR holds native-resolution p{N}.png; each strip also gets a native crop of the same
       page region, <name>-native.png, overlays mapped by k = native/run per axis (fails if |kx-ky|/ky > 0.005)

<run-dir> holds locate_column_rule.json and pages/p{N}.png (8-bit grey,
ink 0, paper 255). Nothing is copied into the repo.

A strip is raw page pixels: the grey crop exactly as the page PNG holds it,
written as an 8-bit grey PNG. No threshold is applied to anything the signer
sees (ruling on report 6). The run's result is not drawn into the pixels; it
is listed per strip in <out-dir>/strips.json as overlay rectangles in the
strip's own px, for the signing console to draw over the pixels.

strips.json holds a header (script and run JSON sha256, the run's header
verbatim, golden-chain git state, clean_run), one entry per strip (file,
sha256, page, kind, rows, cols, frame_wh, k, line_h, overlay) and per page
the run's strip boundaries, y_end, last strip, foot strip start and empty
strips (strip_fracs entries with no strips[].y_mid, with their peak frac).
The foot strip starts at the y0 of the third-from-last strip_fracs entry (the
first if fewer than 3). README.txt describes the strips.
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

HALF = 300
K_TOL = 0.005
FOOT_PAGES = (896, 902, 907, 908)
FULL_PAGES = (896, 897, 898)
RED, BLUE, GREEN, MAGENTA = "#ff0000", "#0000ff", "#00a000", "#ff00ff"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def centre_at(y, slope, c0):
    return slope * y + c0


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


def strip_bounds(page):
    """((y0, y1) of the last strip_fracs entry, y0 of the foot strip)."""
    sf = page["strip_fracs"]
    if not sf:
        raise Fail("no strip_fracs in run JSON")
    return (sf[-1]["y0"], sf[-1]["y1"]), sf[-3 if len(sf) >= 3 else 0]["y0"]


def page_record(page):
    sp = page["split"]
    last, foot = strip_bounds(page)
    return {"ticks": [e["y0"] for e in page["strip_fracs"]], "y_end": sp["y_range"][1],
            "last_strip": list(last), "foot_y0": foot, "empty_strips": empty_strips(page),
            "line_h": (page.get("line_h") or {}).get("page_line_h")}


def overlays(page, size_wh, y_off, x_off, ky=1.0, kx=1.0, run_rows=None):
    """The run's result as rectangles {x, y, w, h, colour, what} in strip px, clipped to the strip.
    Overlays are in run px, mapped by (ky, kx) (identity for the run strip); tick/dot sizes stay in px.
    y_off/x_off are the crop origin in output px; run_rows = (y0, y1 exclusive) of the run strip."""
    sp = page["split"]
    w, h = size_wh
    out = []

    def my(v):
        return int(round(v * ky)) - y_off

    def mx(v):
        return int(round(v * kx)) - x_off

    def put(y0, y1, x0, x1, colour, what):
        y0, y1, x0, x1 = max(y0, 0), min(y1, h), max(x0, 0), min(x1, w)
        if y0 < y1 and x0 < x1:
            out.append({"x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0, "colour": colour, "what": what})

    for s in sp["strips"]:
        y, cx = my(s["y_mid"]), mx(s["centre"])
        put(y - 1, y + 2, cx - 25 - 12, cx - 25, RED, f"cluster centre, strip y_mid {s['y_mid']}")
        put(y - 1, y + 2, cx + 25, cx + 25 + 12, RED, f"cluster centre, strip y_mid {s['y_mid']}")
    half_w, pad = sp["half_w"], sp["pad"]
    r0, r1 = run_rows if run_rows else (y_off, y_off + h)
    for yp in range(((r0 + 19) // 20) * 20, r1, 20):
        c = centre_at(yp, sp["slope"], sp["c0"])
        for xc in (c - half_w - pad - 6, c + half_w + pad + 6):
            x, yy = mx(xc), my(yp)
            put(yy - 1, yy + 2, x - 1, x + 2, BLUE, "fitted band edge")
    for e in page["strip_fracs"]:
        y = my(e["y0"])
        put(y - 1, y + 2, 0, 20, GREEN, f"strip boundary {e['y0']}")
        put(y - 1, y + 2, w - 20, w, GREEN, f"strip boundary {e['y0']}")
    ye = sp["y_range"][1]
    put(my(ye) - 1, my(ye) + 2, 0, 20, MAGENTA, f"y_end {ye}")
    put(my(ye) - 1, my(ye) + 2, w - 20, w, MAGENTA, f"y_end {ye}")
    return out


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


def save_raw(crop, path):
    """The crop's pixels unchanged, as an 8-bit grey PNG; fails if they did not survive."""
    Image.fromarray(np.ascontiguousarray(crop), "L").save(path)
    if not np.array_equal(np.asarray(Image.open(path)), crop):
        raise Fail(f"{path}: written pixels differ from the page crop")


def strip(run_dir, data, n, y0, name, out_dir, native_dir=None, kind=None):
    """Writes the run strip (and the native one if native_dir); returns their strips.json entries."""
    page = data["pages"][str(n)]
    grey = load_grey(run_dir / "pages" / f"p{n}.png")
    h, w = grey.shape
    xdiv = page["geometry"]["xdiv"]
    x0, x1 = max(xdiv - HALF, 0), min(xdiv + HALF, w)
    crop = grey[y0:h, x0:x1]
    save_raw(crop, out_dir / name)
    lh = (page.get("line_h") or {}).get("page_line_h")
    size = [crop.shape[1], crop.shape[0]]
    out = [{"file": name, "sha256": sha256(out_dir / name), "page": n, "kind": kind, "native": False,
            "rows": [y0, h - 1], "cols": [x0, x1 - 1], "size_wh": size, "frame_wh": [w, h], "k": 1.0,
            "line_h": lh, "overlay": overlays(page, size, y0, x0)}]
    if native_dir is not None:
        ncrop, ky, kx, rows, cols, fwh = native_crop(native_dir, n, grey.shape, y0, h, x0, x1)
        nname = name[:-4] + "-native.png"
        save_raw(ncrop, out_dir / nname)
        nsize = [ncrop.shape[1], ncrop.shape[0]]
        out.append({"file": nname, "sha256": sha256(out_dir / nname), "page": n, "kind": kind,
                    "native": True, "rows": rows, "cols": cols, "size_wh": nsize, "frame_wh": fwh,
                    "k": ky, "run_rows": [y0, h - 1], "line_h": None,
                    "overlay": overlays(page, nsize, rows[0], cols[0], ky, kx, (y0, h))})
    return out


README_LEGEND = """Each PNG is raw page pixels (8-bit grey, as the page render holds them); no threshold
and no overlay is in the pixels. The run's result is listed per strip in strips.json as
rectangles in that strip's px, drawn over the pixels by the signing console:
  red     = cluster centre per strip (two 12x3 px ticks at y_mid, 25 px left and right of the centre; the rule is not covered)
  blue    = fitted band edges (dots every 20 rows at c(y) -/+ (half_w + pad + 6))
  green   = strip boundaries (20 px ticks at both image edges: {ticks})
  magenta = y_end per page (20 px ticks at both image edges: {yends})
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

    made = []
    for n in full_pages:
        made += strip(run_dir, data, n, 0, f"p{n}-gutter-full.png", out_dir, native, "gutter-full")
    for n in foot_pages:
        foot = strip_bounds(data["pages"][str(n)])[1]
        made += strip(run_dir, data, n, foot, f"p{n}-foot.png", out_dir, native, "foot")
    pages = {str(n): page_record(data["pages"][str(n)]) for n in dict.fromkeys(m["page"] for m in made)}
    header = {
        "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "script_sha256": sha256(__file__),
        "run_json_sha256": sha256(jpath),
        "run_header": data.get("header"),
        "native_dir": native,
    }
    git_end = git_state(REPO)
    header.update({"golden_chain_git_start": git_start, "golden_chain_git_end": git_end,
                   "clean_run": clean_run(git_start, git_end)})
    (out_dir / "strips.json").write_text(
        json.dumps({"header": header, "strips": made, "pages": pages}, indent=1))
    write_readme(out_dir, made, data)
    for m in made:
        print(m["file"], m["size_wh"], m["sha256"][:16])


if __name__ == "__main__":
    try:
        main(sys.argv)
    except Fail as e:
        sys.exit(f"signing_strips: {e}")
