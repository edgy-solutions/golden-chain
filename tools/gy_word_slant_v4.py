"""Per-word slant, measure v4 (as v3, with one Gaussian-smoothed shear score the same for every shear)

Usage: python tools/gy_word_slant_v4.py <ocr-run-dir> <out-dir>

As tools/gy_word_slant_v3.py (same inputs, outputs, eligibility, box, ink, grid, abstentions, histogram split,
comb) with one change, the shear score: every ink pixel is sheared to x' = x - s*(yc - y), deposited by linear
split onto a grid of 1/4 px, the profile is convolved with one fixed Gaussian (sigma 1 px, truncated at 4 sigma)
and the score is the sum of squares of the smoothed profile. Every shear, zero included, takes this path, so the
blur is the same at every shear and phase. Rows carry no word text. slant.json is byte-identical across reruns;
run_header.json holds the time and git state.
Prediction: ~/.golden-chain/italic-v4-predictions-locked.txt (name only)
Outputs are local only, never commit.
"""

import argparse
import datetime
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TOOLS / "console"))
from column_rule import REPO, Fail, clean_run, git_state  # noqa: E402
from gy_word_slant import (BINS, GRID, MIN_ALNUM, MIN_INK, MIN_SEP, RANGE, eligible,  # noqa: E402
                           mode_midpoint, sha256_file, summarise)
import build  # noqa: E402
from truthset_crops import line_key  # noqa: E402

PREDICTION = "~/.golden-chain/italic-v4-predictions-locked.txt"
COMB_MIN = 40


OVERSAMPLE = 4
SIGMA_PX = 1.0
_HALF = int(round(4 * SIGMA_PX * OVERSAMPLE))
_T = np.arange(-_HALF, _HALF + 1, dtype=np.float64)
KERNEL = np.exp(-0.5 * (_T / (SIGMA_PX * OVERSAMPLE)) ** 2)
KERNEL /= KERNEL.sum()


def score_positions(xp):
    """Sum of squares of the Gaussian-smoothed profile of the positions xp (pixels): each position is deposited
    by linear split onto a grid of 1/OVERSAMPLE px, the profile is convolved with the fixed kernel (sigma 1 px,
    truncated at 4 sigma, sum 1; the profile is padded so no mass is lost), and the squares are summed."""
    xp = np.asarray(xp, dtype=np.float64)
    if xp.size == 0:
        return 0.0
    u = OVERSAMPLE * xp
    f = np.floor(u)
    w = u - f
    k = (f - f.min()).astype(np.int64) + _HALF
    n = int(k.max()) + 2 + _HALF
    prof = np.bincount(k, weights=1.0 - w, minlength=n) + np.bincount(k + 1, weights=w, minlength=n)
    sm = np.convolve(prof, KERNEL, mode="full")
    return float((sm ** 2).sum())


def shear_score_v4(ink, s):
    """x' = x - s*(yc - y) for every ink pixel, then score_positions. The same path for every s, zero included."""
    h = ink.shape[0]
    yc = (h - 1) / 2
    ys, xs = np.nonzero(ink)
    if len(xs) == 0:
        return 0.0
    return score_positions(xs.astype(np.float64) - s * (yc - ys.astype(np.float64)))


def slant(crop_grey):
    ink = build.ink_mask(np.asarray(crop_grey))
    if int(ink.sum()) < MIN_INK:
        return None, "small"
    scores = [shear_score_v4(ink, float(s)) for s in GRID]
    best = max(scores)
    s = min((float(g) for g, sc in zip(GRID, scores) if sc == best), key=lambda v: (abs(v), v))
    if s == float(GRID[0]) or s == float(GRID[-1]):
        return None, "edge"
    return s, None


def line_ranges(words):
    """line key -> [y0, y1] (page coordinates): min y0 .. max y1 over every OCR word on the line."""
    out = {}
    for w in words:
        lk = line_key(w["key"])
        y0, y1 = w["bbox"][1], w["bbox"][3]
        if lk in out:
            out[lk] = [min(out[lk][0], y0), max(out[lk][1], y1)]
        else:
            out[lk] = [y0, y1]
    return out


def measured_box(bbox, line_y):
    """Page-coordinate box: the word's x range by the line's y range."""
    return [bbox[0], line_y[0], bbox[2], line_y[1]]


def comb(h):
    """Bins i (0 < i < len-1): empty between occupied ones; and deep dips (neighbours >= COMB_MIN, bin below a quarter)."""
    empty, dips = [], []
    for i in range(1, len(h) - 1):
        if h[i] == 0 and h[i - 1] > 0 and h[i + 1] > 0:
            empty.append(i)
        m = min(h[i - 1], h[i + 1])
        if m >= COMB_MIN and h[i] < m / 4:
            dips.append(i)
    return {"empty_between": empty, "deep_dip": dips}


def main(run_dir, out):
    git_start = git_state(REPO)
    run_dir, out = Path(run_dir), Path(out)
    ocr_path = run_dir / "ocr.json"
    if not ocr_path.is_file():
        raise Fail(f"missing {ocr_path}")
    ocr = json.loads(ocr_path.read_text(encoding="utf-8"))
    splits = ocr["header"].get("splits", {})
    words = ocr["words"]
    elig = [w for w in words if eligible(w)]
    if not elig:
        raise Fail("empty eligible set")
    lines = line_ranges(words)
    shas, pages, regs, rows = {}, {}, {}, []
    for w in elig:
        p, r = w["page"], w["region"]
        if str(p) not in splits:
            raise Fail(f"p.{p}: no split in ocr.json header")
        if p not in pages:
            pp = run_dir / "pages" / f"p{p}.png"
            if not pp.is_file():
                raise Fail(f"missing {pp}")
            shas[f"pages/p{p}.png"] = sha256_file(pp)
            with Image.open(pp) as im:
                pages[p] = im.size[0]
        if (p, r) not in regs:
            rp = run_dir / "regions" / f"p{p}-{r}.png"
            if not rp.is_file():
                raise Fail(f"missing {rp}")
            shas[f"regions/p{p}-{r}.png"] = sha256_file(rp)
            regs[(p, r)] = np.asarray(Image.open(rp).convert("L"))
        img = regs[(p, r)]
        h, wd = img.shape
        dx = 0 if r == "left" else pages[p] - wd
        dy = int(splits[str(p)]["ytop"])
        bx0, by0, bx1, by1 = measured_box(w["bbox"], lines[line_key(w["key"])])
        x0, x1, y0, y1 = bx0 - dx, bx1 - dx, by0 - dy, by1 - dy
        if x0 < 0 or y0 < 0 or x1 > wd or y1 > h or x1 <= x0 or y1 <= y0:
            raise Fail(f"{w['key']}: measured box outside region image")
        s, why = slant(img[y0:y1, x0:x1])
        rows.append({"key": w["key"], "page": p, "region": r, "slant": s, "abstain": why,
                     "box": [x0, y0, x1, y1]})
    values = [r["slant"] for r in rows if r["slant"] is not None]
    T, info = mode_midpoint(values)
    for r in rows:
        r["slanted"] = None if (T is None or r["slant"] is None) else bool(r["slant"] >= T)
    by_key = {r["key"]: r for r in rows}
    fl = [w for w in words if w.get("italic") is True]
    in_rows = [by_key[w["key"]] for w in fl if w["key"] in by_key]
    legacy = {"flagged": len(fl), "eligible": len(in_rows),
              "measured": sum(1 for r in in_rows if r["slant"] is not None),
              "slanted": sum(1 for r in in_rows if r["slanted"])}
    summary = summarise(rows, T, legacy)
    summary["comb"] = comb(info["hist"])
    params = {"grid": [float(GRID[0]), float(GRID[-1]), len(GRID)], "ink": "mode-midpoint per crop",
              "min_ink": MIN_INK, "min_alnum": MIN_ALNUM, "bins": BINS, "range": list(RANGE),
              "min_sep": MIN_SEP, "measure": "v4", "shear": "linear split onto 1/4 px, Gaussian sigma 1 px truncated 4 sigma, same for every shear", "oversample": OVERSAMPLE, "sigma_px": SIGMA_PX, "box": "word x, line y",
              "prediction": PREDICTION}
    inp = {"ocr_json_sha256": sha256_file(ocr_path),
           "ocr_run_header_script_sha256": ocr["header"].get("script_sha256"),
           "png_sha256": dict(sorted(shas.items()))}
    out.mkdir(parents=True, exist_ok=True)
    (out / "slant.json").write_text(json.dumps({"summary": summary, "rows": rows, "hist": info,
                                                "params": params, "input": inp},
                                               indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    git_end = git_state(REPO)
    header = {"run": "gy-word-slant-v4",
              "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
              "script_sha256": sha256_file(__file__), "input": inp, "params": params,
              "prediction": PREDICTION, "golden_chain_git_start": git_start,
              "golden_chain_git_end": git_end, "clean_run": clean_run(git_start, git_end)}
    (out / "run_header.json").write_text(json.dumps(header, indent=1, sort_keys=True), encoding="utf-8",
                                         newline="\n")
    (out / "README.txt").write_text(
        "LOCAL ONLY. Per-word slant rows (keys, boxes and numbers, no word text) derived from the OCR run, "
        "measure v4. Never commit it.\n", encoding="utf-8", newline="\n")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(usage=__doc__)
    ap.add_argument("run_dir")
    ap.add_argument("out")
    a = ap.parse_args()
    try:
        sys.exit(main(a.run_dir, a.out))
    except Fail as ex:
        print(f"FAIL: {ex}", file=sys.stderr)
        sys.exit(1)
