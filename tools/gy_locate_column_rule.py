"""goat-yard's locate_column_rule, unchanged, on BSB Gill printed pages (GY response, 2026-10-26).

Usage: python tools/gy_locate_column_rule.py <gill.pdf> <first> <last> <out-dir> [--scale S] [--prediction TEXT]

goat-yard is consumed from a worktree at tag substrate-v0, never copied
(docs/sources/goat-yard.md). The worktree is GOLDEN_CHAIN_GOATYARD, default
../goatyard-substrate-v0. It must be clean and at PINNED, or the run fails.

Per page:
- the page's single embedded image (5100 x 7650, 1 bpp), the same bitmap as
  tools/column_rule.py, written as an 8-bit grey PNG (ink 0, paper 255) in
  <out-dir>/pages/; nothing is rescaled. With --scale S the PNG is instead
  column_rule.render(pdf, p, S): a pypdfium2 grey render, anti-aliased, not
  thresholded; all pages must share the first page's size;
- goat-yard's geometry writer: build_page_geometry.process_page (presplit
  with its default upscale and full-width depth) gives the record;
- verse_regions.page_ink on the grey image, then verse_regions.locate_column_rule.

For every strip the per-column ink fraction over the search window is stored
too, so an abstention can become a request file without a rerun.
- "line_h": goat-yard's own S1 (verse_regions.analyze_page_s1) page line height,
  per-column basis, median band height and median band pitch (line_height);
  the header's "line_height" summarises it against goat-yard's 55 px design
  height (band 49..61). --prediction TEXT overrides the header's prediction.
Needs numpy, pypdfium2, pillow (the `measure` extra).
"""

import datetime
import hashlib
import importlib.metadata
import json
import os
import statistics
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from column_rule import OFFSET, REPO, Fail, bitmap, clean_run, git_state, render  # noqa: E402

PINNED = "3d0b03e0ac8d67b1e9e53947faf98205205082b5"
TAG = "substrate-v0"
# Every worktree module we load, by path. Installed --no-deps (docs/sources/goat-yard.md):
# a module outside this list, or one needing a skipped dependency, fails loud.
SUBSTRATE_MODULES = frozenset({"build_page_geometry", "cv_footnote_presplit", "verse_regions",
                               "note_start_detect", "box_sanity", "hanging_indent"})


def git(root, *args):
    out = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, timeout=30)
    if out.returncode != 0:
        raise Fail(f"git {' '.join(args)} failed in {root}: {out.stderr.strip()}")
    return out.stdout.strip()


def goatyard():
    root = Path(os.environ.get("GOLDEN_CHAIN_GOATYARD")
                or Path(__file__).resolve().parents[2] / "goatyard-substrate-v0").resolve()
    head = git(root, "rev-parse", "HEAD")
    if head != PINNED:
        raise Fail(f"goat-yard worktree {root} is at {head}, not {TAG} ({PINNED})")
    if git(root, "status", "--porcelain"):
        raise Fail(f"goat-yard worktree {root} is dirty")
    if git(root, "rev-parse", f"{TAG}^{{commit}}") != PINNED:
        raise Fail(f"tag {TAG} does not point at {PINNED}")
    sys.path.insert(0, str(root / "pipeline" / "scripts"))
    sys.path.insert(0, str(root / "pipeline" / "reextract"))
    import build_page_geometry as BPG
    import verse_regions as VR
    loaded = {n for n, m in list(sys.modules.items())
              if Path(getattr(m, "__file__", None) or "/").resolve().is_relative_to(root)}
    if loaded != SUBSTRATE_MODULES:
        raise Fail(f"goat-yard modules loaded {sorted(loaded)}, expected {sorted(SUBSTRATE_MODULES)}")
    return root, BPG, VR


def strip_fracs(ink, record, VR):
    """The per-strip column ink fractions locate_column_rule computes internally, for the record."""
    xdiv = record.get("xdiv")
    if not xdiv:
        return None
    xdiv = int(xdiv)
    H, W = ink.shape
    rules = [r for r in (record.get("rules") or []) if r is not None]
    y_end = (min(rules) - 20) if rules else (H - 300)
    lo, hi = max(0, xdiv - VR.RULE_SEARCH_PX), min(W, xdiv + VR.RULE_SEARCH_PX)
    out = []
    for y in range(VR.RULE_Y_TOP_PX, y_end - VR.RULE_STRIP_PX // 2, VR.RULE_STRIP_PX):
        ys1 = min(y + VR.RULE_STRIP_PX, y_end)
        out.append({"y0": y, "y1": ys1, "x0": lo,
                    "frac": [round(float(f), 4) for f in ink[y:ys1, lo:hi].mean(axis=0)]})
    return out


def line_height(s1):
    lh = s1["line_h"]
    first = lh.get("left") or lh.get("right")
    bands = {c: sorted(s1[c], key=lambda b: b["y0"]) for c in ("left", "right")}
    heights = [b["y1"] - b["y0"] for c in bands for b in bands[c]]
    pitches = [b2["y0"] - b1["y0"] for c in bands for b1, b2 in zip(bands[c], bands[c][1:])]
    return {"page_line_h": first["page_line_h"] if first else None,
            "basis": {c: v["basis"] for c, v in lh.items()},
            "band_h_med": statistics.median(heights) if heights else None,
            "pitch_med": statistics.median(pitches) if pitches else None,
            "n_bands": len(heights)}


def line_height_summary(per_page):
    hs = [v["page_line_h"] for v in per_page if v and v["page_line_h"] is not None]
    pitches = [v["pitch_med"] for v in per_page if v and v["pitch_med"] is not None]
    med = statistics.median(hs) if hs else None
    return {"page_line_h_median": med, "page_line_h_range": [min(hs), max(hs)] if hs else None,
            "pitch_median": statistics.median(pitches) if pitches else None,
            "ratio_to_55": round(med / 55, 3) if med is not None else None,
            "goat_yard_band": [49, 61]}


PREDICTION = ("20/20 ok; every strip carries a cluster; max residual <= 15 px "
              "(~/.golden-chain/gy-locate-column-rule-predictions-locked.txt)")


def main(pdf_path, first, last, out, scale=None, prediction=PREDICTION):
    import pypdfium2 as pdfium

    git_start = git_state(REPO)
    root, BPG, VR = goatyard()
    out = Path(out)
    (out / "pages").mkdir(parents=True, exist_ok=True)
    vr_path = root / "pipeline" / "reextract" / "verse_regions.py"
    config = BPG.build_config(BPG.DEFAULT_UPSCALE, BPG.DEFAULT_FULL_WIDTH_DEPTH,
                              BPG.compute_module_sha256(root / "pipeline" / "scripts" / "cv_footnote_presplit.py"),
                              BPG.get_git_head(root), BPG.get_git_dirty(root))
    header = {
        "run": "gy-locate-column-rule",
        "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "pdf_sha256": hashlib.sha256(Path(pdf_path).read_bytes()).hexdigest(),
        "pages_printed": [first, last], "pdf_offset": OFFSET,
        "goatyard": {"tag": TAG, "commit": PINNED, "dirty": False,
                     "verse_regions_sha256": hashlib.sha256(vr_path.read_bytes()).hexdigest()},
        "geometry_config": config,
        "constants": {k: getattr(VR, k) for k in dir(VR) if k.startswith("RULE_")} | {"INK": VR.INK},
        "frame": "native embedded image, 5100 x 7650 px, not rescaled",
        "versions": {"python": sys.version.split()[0], "numpy": np.__version__,
                     "pypdfium2": importlib.metadata.version("pypdfium2"),
                     "pillow": importlib.metadata.version("pillow")},
        "prediction": prediction,
    }
    pdf = pdfium.PdfDocument(pdf_path)
    pages, frames, frame_wh = {}, {}, None
    for p in range(first, last + 1):
        grey = np.where(bitmap(pdf, p), 0, 255).astype(np.uint8) if scale is None else render(pdf, p, scale)
        if scale is not None:
            if frame_wh is None:
                frame_wh = grey.shape[::-1]
                header["frame"] = f"pypdfium2 render, scale {scale}, grey, {frame_wh[0]} x {frame_wh[1]} px"
            elif grey.shape[::-1] != frame_wh:
                raise Fail(f"p.{p}: frame {grey.shape[::-1]} differs from first page {frame_wh}")
        path = out / "pages" / f"p{p}.png"
        Image.fromarray(grey, mode="L").save(path)
        record, missing = BPG.process_page("bsb-gill", p + OFFSET, path, path.name, "measure", config)
        if missing or record is None:
            raise Fail(f"p.{p}: image not written")
        ink = VR.page_ink(np.asarray(Image.open(path).convert("L")))
        split = VR.locate_column_rule(ink, record)
        frames[p] = f"{grey.shape[1]}x{grey.shape[0]}"
        lh = line_height(VR.analyze_page_s1(ink, record))
        pages[p] = {"geometry": {k: record.get(k) for k in ("page", "xdiv", "rules", "mode", "flags", "error")},
                    "split": split, "strip_fracs": strip_fracs(ink, record, VR),
                    "line_h": lh}
    header["line_height"] = line_height_summary([r["line_h"] for r in pages.values()])
    git_end = git_state(REPO)
    header.update({"golden_chain_git_start": git_start, "golden_chain_git_end": git_end,
                   "clean_run": clean_run(git_start, git_end)})
    (out / "locate_column_rule.json").write_text(json.dumps({"header": header, "pages": pages}, indent=1))
    for p, r in pages.items():
        s = r["split"]
        print(p, s["status"], s.get("reason", ""), "strips", f"{s.get('n_rule')}/{s.get('n_strips')}",
              "half_w", s.get("half_w"), "resid", s.get("max_resid"), "xdiv", r["geometry"]["xdiv"],
              "rules", r["geometry"]["rules"], "line_h", r["line_h"]["page_line_h"],
              "frame", frames[p])


if __name__ == "__main__":
    argv, opts = sys.argv[1:], {}
    for flag, key, conv in (("--scale", "scale", float), ("--prediction", "prediction", str)):
        if flag in argv:
            i = argv.index(flag)
            opts[key] = conv(argv[i + 1])
            del argv[i:i + 2]
    try:
        if len(argv) != 4:
            raise Fail(__doc__)
        main(argv[0], int(argv[1]), int(argv[2]), argv[3], **opts)
    except Fail as e:
        sys.exit(f"FAIL: {e}")
