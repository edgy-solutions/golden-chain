"""Per-word slant from pixels (ruling on report 13, O-4)

Usage: python tools/gy_word_slant.py <ocr-run-dir> <out-dir>

Input is a run-1 OCR directory (ocr.json, regions/, pages/). For every eligible word (column region, at
least three alphanumerics) the region PNG is cropped at the word's bbox and the slant is the shear s in
[-0.20, 0.50] that makes the ink columns most concentrated (sum of squared column counts). A word with
too little ink, or whose best s sits on a grid edge, abstains. The measured slants are split by the
midpoint between the two modes of their histogram; unimodal means no split. Rows carry no word text.
slant.json is byte-identical across reruns; run_header.json holds the time and git state.
Prediction: ~/.golden-chain/o4-word-slant-predictions-locked.txt (locked before this file existed)
Outputs are local only, never commit.
"""

import argparse
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from column_rule import REPO, Fail, clean_run, git_state  # noqa: E402

GRID = np.round(np.arange(-20, 51) / 100, 2)
INK = 128
MIN_INK = 300
MIN_ALNUM = 3
BINS = 35
RANGE = (-0.20, 0.50)
MIN_SEP = 0.10
PREDICTION = "~/.golden-chain/o4-word-slant-predictions-locked.txt"
_ALNUM = re.compile(r"[0-9A-Za-z]")


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def eligible(word):
    return word.get("region") in ("left", "right") and len(_ALNUM.findall(word.get("text") or "")) >= MIN_ALNUM


def shear_score(ink, s):
    """Sum over distinct sheared columns of count^2; ink is a bool array."""
    h = ink.shape[0]
    yc = (h - 1) / 2
    ys, xs = np.nonzero(ink)
    if len(xs) == 0:
        return 0.0
    xp = np.rint(xs - s * (yc - ys)).astype(np.int64)
    counts = np.bincount(xp - xp.min())
    return float((counts.astype(np.float64) ** 2).sum())


def slant(crop_grey):
    ink = np.asarray(crop_grey) < INK
    if int(ink.sum()) < MIN_INK:
        return None, "small"
    scores = [shear_score(ink, float(s)) for s in GRID]
    best = max(scores)
    s = min((float(g) for g, sc in zip(GRID, scores) if sc == best), key=lambda v: (abs(v), v))
    if s == float(GRID[0]) or s == float(GRID[-1]):
        return None, "edge"
    return s, None


def mode_midpoint(values):
    h, edges = np.histogram(values, bins=BINS, range=RANGE)
    centres = (edges[:-1] + edges[1:]) / 2
    lo = int(np.argmax(h))
    last = len(h) - 1
    cands = [i for i in range(lo + 1, len(h))
             if h[i] > h[i - 1] and (i == last or h[i] >= h[i + 1])
             and centres[i] - centres[lo] >= MIN_SEP - 1e-9
             and h[lo:i + 1].min() < h[i] / 2]
    info = {"hist": [int(x) for x in h], "edges": [round(float(e), 4) for e in edges],
            "lo_centre": round(float(centres[lo]), 4), "hi_centre": None, "valley": None, "T": None}
    if not cands:
        return None, info
    hi = max(cands, key=lambda i: (h[i], -i))
    T = float((centres[lo] + centres[hi]) / 2)
    info.update(hi_centre=round(float(centres[hi]), 4), valley=int(h[lo:hi + 1].min()), T=round(T, 4))
    return T, info


def summarise(rows, T, legacy):
    measured = [r for r in rows if r["slant"] is not None]
    slanted = [r for r in measured if r["slanted"]]
    pc = {}
    for r in measured:
        d = pc.setdefault(f"{r['page']}/{r['region']}", {"measured": 0, "slanted": 0})
        d["measured"] += 1
        d["slanted"] += 1 if r["slanted"] else 0
    pc = dict(sorted(pc.items()))
    mx = {"where": None, "share": None}
    if slanted:
        k = max(pc, key=lambda k: (pc[k]["slanted"], k))
        mx = {"where": k, "share": round(pc[k]["slanted"] / len(slanted), 4)}
    return {"eligible": len(rows), "measured": len(measured),
            "abstain_small": sum(1 for r in rows if r["abstain"] == "small"),
            "abstain_edge": sum(1 for r in rows if r["abstain"] == "edge"),
            "T": None if T is None else round(T, 4),
            "unimodal": T is None,
            "slanted": None if T is None else len(slanted),
            "italic_rate": round(len(slanted) / len(measured), 4) if T is not None and measured else None,
            "by_page_column": pc, "max_share_page_column": mx, "legacy": legacy,
            "p912_left_slanted": pc.get("912/left", {}).get("slanted", 0)}


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
        x0, y0, x1, y1 = w["bbox"]
        x0, x1, y0, y1 = x0 - dx, x1 - dx, y0 - dy, y1 - dy
        if x0 < 0 or y0 < 0 or x1 > wd or y1 > h or x1 <= x0 or y1 <= y0:
            raise Fail(f"{w['key']}: bbox outside region image")
        s, why = slant(img[y0:y1, x0:x1])
        rows.append({"key": w["key"], "page": p, "region": r, "slant": s, "abstain": why})
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
    params = {"grid": [float(GRID[0]), float(GRID[-1]), len(GRID)], "ink": INK, "min_ink": MIN_INK,
              "min_alnum": MIN_ALNUM, "bins": BINS, "range": list(RANGE), "min_sep": MIN_SEP,
              "prediction": PREDICTION}
    inp = {"ocr_json_sha256": sha256_file(ocr_path),
           "ocr_run_header_script_sha256": ocr["header"].get("script_sha256"),
           "png_sha256": dict(sorted(shas.items()))}
    out.mkdir(parents=True, exist_ok=True)
    (out / "slant.json").write_text(json.dumps({"summary": summary, "rows": rows, "hist": info,
                                                "params": params, "input": inp},
                                               indent=1, sort_keys=True), encoding="utf-8")
    git_end = git_state(REPO)
    header = {"run": "gy-word-slant",
              "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
              "script_sha256": sha256_file(__file__), "input": inp, "params": params,
              "prediction": PREDICTION, "golden_chain_git_start": git_start,
              "golden_chain_git_end": git_end, "clean_run": clean_run(git_start, git_end)}
    (out / "run_header.json").write_text(json.dumps(header, indent=1, sort_keys=True), encoding="utf-8")
    (out / "README.txt").write_text(
        "LOCAL ONLY. Per-word slant rows (keys and numbers, no word text) derived from the OCR run. "
        "Never commit it.\n", encoding="utf-8")
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
