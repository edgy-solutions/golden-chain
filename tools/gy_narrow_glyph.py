"""Lone narrow glyphs at the gutter: does goat-yard's rule erasure clip real line ends? (overnight order, item 5)

Usage: python tools/gy_narrow_glyph.py <gill.pdf> <first> <last> <out-dir>

The single-rule fixture note (docs/handoff/NOTE_goatyard_single_rule_fixture.md) observes that inside
the +/-120 px gutter window every ink run of RULE_RUN_MAX_W (8) px or less is treated as rule, so a
narrow glyph ending a left-column line there would be erased and the band would end before it. This
measures it on real pages, from pixels, with goat-yard consumed unchanged at substrate-v1 (the loader
of tools/gy_locate_column_rule.py; nothing is copied).

Per page: the native embedded image (as gy_locate_column_rule), process_page, page_ink,
locate_column_rule, analyze_page_s1. Per S1 band (measure_band):
- left band: the rightmost ink run of the raw page ink over the band's own box (the split already bounds
  the left box at the rule's left edge); thin = width <= RULE_RUN_MAX_W and inside the window
  [xdiv_at - W, xdiv_at + W), xdiv_at = round(split centre at the band's mid-row), as _make_band;
  shift = raw rightmost ink x + 1 - band right_ink_x; gap = white columns before the run.
- right band: the mirror (leftmost run; shift = band left_ink_x - raw leftmost ink x).
Prediction: ~/.golden-chain/item5-narrow-glyph-predictions-locked.txt (locked before this file existed).
"""

import datetime
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from column_rule import OFFSET, REPO, Fail, bitmap, git_state  # noqa: E402
import gy_locate_column_rule as G  # noqa: E402


def runs(v):
    """[(start, end)) of True runs in a 1-D bool array."""
    out, i, n = [], 0, len(v)
    while i < n:
        if v[i]:
            j = i
            while j < n and v[j]:
                j += 1
            out.append((i, j))
            i = j
        else:
            i += 1
    return out


def measure_band(ink, band, col, xdiv_at, max_w=8, window=120):
    """One S1 band against the raw ink. Returns None for an empty band."""
    x0, x1, y0, y1 = band["x0"], band["x1"], band["y0"], band["y1"]
    rs = runs(ink[y0:y1, x0:x1].any(axis=0))
    if not rs:
        return None
    if col == "left":
        end_run, prev = rs[-1], (rs[-2] if len(rs) > 1 else None)
        a, b = x0 + end_run[0], x0 + end_run[1]
        gap = (end_run[0] - prev[1]) if prev else None
        shift = b - band["right_ink_x"]
    else:
        end_run, nxt = rs[0], (rs[1] if len(rs) > 1 else None)
        a, b = x0 + end_run[0], x0 + end_run[1]
        gap = (nxt[0] - end_run[1]) if nxt else None
        shift = band["left_ink_x"] - a
    w = b - a
    in_window = (xdiv_at - window) <= a and b <= (xdiv_at + window)
    return {"col": col, "y0": y0, "y1": y1, "run": [a, b], "width": w, "gap": gap,
            "xdiv_at": xdiv_at, "in_window": in_window, "thin": w <= max_w and in_window, "shift": int(shift)}


def main(pdf_path, first, last, out):
    import pypdfium2 as pdfium

    git_start = git_state(REPO)
    root, BPG, VR = G.goatyard()
    out = Path(out)
    (out / "pages").mkdir(parents=True, exist_ok=True)
    config = BPG.build_config(BPG.DEFAULT_UPSCALE, BPG.DEFAULT_FULL_WIDTH_DEPTH,
                              BPG.compute_module_sha256(root / "pipeline" / "scripts" / "cv_footnote_presplit.py"),
                              BPG.get_git_head(root), BPG.get_git_dirty(root))
    pdf = pdfium.PdfDocument(pdf_path)
    bands = []
    for p in range(first, last + 1):
        grey = np.where(bitmap(pdf, p), 0, 255).astype(np.uint8)
        path = out / "pages" / f"p{p}.png"
        Image.fromarray(grey, mode="L").save(path)
        record, missing = BPG.process_page("bsb-gill", p + OFFSET, path, path.name, "measure", config)
        if missing or record is None:
            raise Fail(f"p.{p}: image not written")
        ink = VR.page_ink(np.asarray(Image.open(path).convert("L")))
        split = VR.locate_column_rule(ink, record)
        if split["status"] != "ok":
            raise Fail(f"p.{p}: split {split['status']}")
        s1 = VR.analyze_page_s1(ink, record)
        for col in ("left", "right"):
            for band in s1[col]:
                xd = int(round(VR.split_centre(split, (band["y0"] + band["y1"]) / 2)))
                m = measure_band(ink, band, col, xd, VR.RULE_RUN_MAX_W, VR.GUTTER_WINDOW_W)
                if m:
                    bands.append({"page": p, **m})
    left = [b for b in bands if b["col"] == "left"]
    right = [b for b in bands if b["col"] == "right"]
    thin_l = [b for b in left if b["thin"]]
    shift_l = [b for b in left if b["shift"] > 0]
    summary = {
        "n_left": len(left), "n_right": len(right),
        "left_thin_final": len(thin_l), "left_shift_gt0": len(shift_l),
        "left_sets_equal": {(b["page"], b["y0"]) for b in thin_l} == {(b["page"], b["y0"]) for b in shift_l},
        "left_final_in_window": sum(b["in_window"] for b in left),
        "left_thin_widths": sorted(b["width"] for b in thin_l),
        "left_thin_gaps": sorted(b["gap"] for b in thin_l if b["gap"] is not None),
        "left_max_shift": max((b["shift"] for b in left), default=0),
        "left_shift_gap_ge20": sum(1 for b in shift_l if (b["gap"] or 0) >= 20),
        "right_thin_lead": sum(b["thin"] for b in right),
        "right_shift_gt0": sum(b["shift"] > 0 for b in right),
        "width_hist_left_final": {w: sum(1 for b in left if b["width"] == w) for w in range(1, 21)},
    }
    rec = {"header": {"run": "gy-narrow-glyph",
                      "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                      "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      "pdf_sha256": hashlib.sha256(Path(pdf_path).read_bytes()).hexdigest(),
                      "pages_printed": [first, last], "pdf_offset": OFFSET,
                      "goatyard": {"tag": G.TAG, "commit": G.PINNED},
                      "constants": {"RULE_RUN_MAX_W": VR.RULE_RUN_MAX_W, "GUTTER_WINDOW_W": VR.GUTTER_WINDOW_W,
                                    "INK": VR.INK},
                      "prediction": "~/.golden-chain/item5-narrow-glyph-predictions-locked.txt",
                      "golden_chain_git_start": git_start, "golden_chain_git_end": git_state(REPO)},
           "summary": summary, "bands": bands}
    (out / "narrow_glyph.json").write_text(json.dumps(rec, indent=1), encoding="utf-8")
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    try:
        sys.exit(main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]))
    except Fail as ex:
        print(f"FAIL: {ex}", file=sys.stderr)
        sys.exit(1)
