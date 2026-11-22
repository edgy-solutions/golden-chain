"""Tall line boxes: do they hold two printed lines? Measurement only (tall-box lock).

Usage: python tools/tallbox_bands.py <ocr-run-dir> <truthset-v4-dir> <truthset-v4-crops-dir> <out-dir>

Selection S: the v4 drops (drops.json of the crops dir) whose granted pad on a failing side is 0 (crop_rows' top
equals the line box's y0 on a top failure, or its bottom equals y1 on a bottom failure), recomputed from the OCR
line boxes with truthset_crops_v4.line_boxes and crop_rows (P = 12). Measure B: the line box (the union of the OCR
word boxes of the word's line) is cut from the page, build.ink_mask gives the ink, the row profile p[y] is the ink
pixels per row. Rule T (two_bands): m = max p; a gap row has p <= 0.05 m; the box shows two bands if a run of >= 3
consecutive gap rows touches neither the first nor the last row, the ink above it and below it are each >= 20 % of
the box's ink, and the inked extent on each side (first to last row with p > 0.05 m) is >= 15 px; if several runs
qualify, the one with the most balanced ink split. Control K: the same rule on each distinct line of the kept v4
rows (crops.json). Numbers from page pixels in code; no image is viewed; nothing is fixed here.
bands.json is byte-identical across reruns; time and git state go to run_header.json.
Prediction: ~/.golden-chain/tallbox-bands-predictions-locked.txt (name only)
Outputs are local only, never commit.
"""

import argparse
import datetime
import json
import sys
from pathlib import Path

import numpy as np

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TOOLS / "console"))
import build  # noqa: E402
import truthset_crops as tc  # noqa: E402
import truthset_crops_v4 as c4  # noqa: E402
from column_rule import REPO, Fail, clean_run, git_state  # noqa: E402

PREDICTION = "~/.golden-chain/tallbox-bands-predictions-locked.txt"
PARAMS = {"gap_frac": 0.05, "min_run": 3, "min_share": 0.2, "min_band_px": 15}
README = ("LOCAL ONLY. Tall-box band measurement: numbers from the book's page pixels, with keys and boxes. "
          "Never commit.\n")


def two_bands(p):
    """Rule T. p: 1-D int array, ink pixels per row of a line box. -> None or {"run": [r0, r1_exclusive],
    "share_above", "share_below", "band_above_px", "band_below_px"}."""
    p = np.asarray(p)
    n = len(p)
    m = int(p.max()) if n else 0
    if m == 0:
        return None
    thr = PARAMS["gap_frac"] * m
    gap = p <= thr
    total = int(p.sum())
    best = None
    y = 0
    while y < n:
        if not gap[y]:
            y += 1
            continue
        r0 = y
        while y < n and gap[y]:
            y += 1
        r1 = y
        if r1 - r0 < PARAMS["min_run"] or r0 == 0 or r1 == n:
            continue
        above, below = int(p[:r0].sum()), int(p[r1:].sum())
        if 5 * above < total or 5 * below < total:  # min_share 0.2, in integers
            continue
        ext = []
        for side in (p[:r0], p[r1:]):
            rows = np.flatnonzero(side > thr)
            ext.append(int(rows[-1] - rows[0] + 1) if len(rows) else 0)
        if min(ext) < PARAMS["min_band_px"]:
            continue
        sa, sb = above / total, below / total
        if best is None or abs(sa - sb) < best[0]:
            best = (abs(sa - sb), {"run": [r0, r1], "share_above": round(sa, 4), "share_below": round(sb, 4),
                                   "band_above_px": ext[0], "band_below_px": ext[1]})
    return None if best is None else best[1]


def measure(page_img, L):
    """Rule B and T on the line box L = [x0, y0, x1, y1] cut from the page."""
    cut = page_img[L[1]:L[3], L[0]:L[2]]
    return two_bands(build.ink_mask(cut).sum(axis=1))


def main(ocr_dir, ts_dir, crops_dir, out):
    git_start = git_state(REPO)
    od, ts, cd, out = Path(ocr_dir), Path(ts_dir), Path(crops_dir), Path(out)
    paths = {"ocr.json": od / "ocr.json", "candidates.json": ts / "candidates.json",
             "crops.json": cd / "crops.json", "drops.json": cd / "drops.json"}
    for p in paths.values():
        if not p.is_file():
            raise Fail(f"missing: {p}")
    inputs = {k: tc.sha256_file(p) for k, p in paths.items()}
    words = json.loads(paths["ocr.json"].read_text(encoding="utf-8"))["words"]
    cand = {r["key"]: r for r in json.loads(paths["candidates.json"].read_text(encoding="utf-8"))["rows"]}
    crops = json.loads(paths["crops.json"].read_text(encoding="utf-8"))["rows"]
    drops = json.loads(paths["drops.json"].read_text(encoding="utf-8"))["rows"]
    by_key = {w["key"]: w for w in words}
    lines = c4.line_boxes(words)
    pages = {}

    def page_img(p):
        if p not in pages:
            pp = od / "pages" / f"p{p}.png"
            if not pp.is_file():
                raise Fail(f"missing {pp}")
            inputs[f"pages/p{p}.png"] = tc.sha256_file(pp)
            pages[p] = tc.grey(pp)
        return pages[p]

    def line_of(key):
        if key not in by_key:
            raise Fail(f"{key}: not in ocr.json")
        w = by_key[key]
        lk = (w["page"], w["region"], tc.line_key(key))
        return w, lk, lines[lk]

    selected = []
    for d in drops:
        if d["key"] not in cand:
            raise Fail(f"{d['key']}: not in candidates.json")
        w, lk, L = line_of(d["key"])
        pg = page_img(w["page"])
        others = [b for k, b in lines.items() if k[:2] == lk[:2] and k != lk]
        top, bottom = c4.crop_rows(L, cand[d["key"]]["bbox"], others, pg.shape[0], c4.PAD)
        side = d["side"]
        if not ((side in ("top", "both") and top == L[1]) or (side in ("bottom", "both") and bottom == L[3])):
            continue
        selected.append({"id": d["id"], "key": d["key"], "side": side, "box_height": L[3] - L[1],
                         "pad_top": L[1] - top, "pad_bottom": bottom - L[3], "two_bands": measure(pg, L)})
    seen, ctrl, ctrl_two = set(), 0, []
    for c in crops:
        w, lk, L = line_of(c["key"])
        if lk in seen:
            continue
        seen.add(lk)
        ctrl += 1
        m = measure(page_img(w["page"]), L)
        if m is not None:
            ctrl_two.append({"key": c["key"], "box_height": L[3] - L[1], "two_bands": m})
    n_two = sum(s["two_bands"] is not None for s in selected)
    doc = {"selected": selected, "control": {"n": ctrl, "two_bands": len(ctrl_two), "lines": ctrl_two},
           "params": PARAMS, "input": dict(sorted(inputs.items()))}
    out.mkdir(parents=True, exist_ok=True)
    (out / "bands.json").write_text(json.dumps(doc, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    git_end = git_state(REPO)
    header = {"run": "tallbox-bands", "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
              "script_sha256": tc.sha256_file(__file__), "prediction": PREDICTION,
              "golden_chain_git_start": git_start, "golden_chain_git_end": git_end,
              "clean_run": clean_run(git_start, git_end)}
    (out / "run_header.json").write_text(json.dumps(header, indent=1, sort_keys=True), encoding="utf-8",
                                         newline="\n")
    (out / "README.txt").write_text(README, encoding="utf-8", newline="\n")
    print(json.dumps({"n_selected": len(selected), "n_two_bands": n_two, "control_n": ctrl,
                      "control_two_bands": len(ctrl_two)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(usage=__doc__)
    for a in ("ocr_dir", "truthset_dir", "crops_dir", "out"):
        ap.add_argument(a)
    a = ap.parse_args()
    try:
        sys.exit(main(a.ocr_dir, a.truthset_dir, a.crops_dir, a.out))
    except Fail as ex:
        print(f"FAIL: {ex}", file=sys.stderr)
        sys.exit(1)
