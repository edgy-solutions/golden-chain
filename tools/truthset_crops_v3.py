"""Truth-set v3 signing crops: each candidate word at its line's full height, padded, and its printed line.

Usage: python tools/truthset_crops_v3.py <truthset-v3-dir> <ocr-run-dir> <out-dir>

<truthset-v3-dir> holds candidates.json (tools/truthset_v3.py). Candidates take the fixed order and ids w001...
of tools/truthset_crops.py. The word crop is the page pixels at the word's OCR x range, from V_PAD above the
line's top to V_PAD below its bottom (the line is the union of its OCR word boxes), clipped to the page. If
ink (build.edge_ink) touches the crop's top or bottom row it is cut again once with RECUT_PAD; if it still
does, the row is dropped (no PNG) and listed in "dropped" with the edge counts. The line crop is the line
padded LINE_PAD with the word's box in it. crops.json lists ids, keys, boxes, sizes and sha256s only (no
stratum, no slant, no word text) and is byte-identical across reruns; time and git state go to run_header.json.
Prediction: ~/.golden-chain/italic-v3-predictions-locked.txt (name only)
Outputs are local only, never commit.
"""

import argparse
import datetime
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TOOLS / "console"))
import build  # noqa: E402
import truthset_crops as tc  # noqa: E402
import truthset_v2  # noqa: E402
from column_rule import REPO, Fail, clean_run, git_state  # noqa: E402

V_PAD = 6
RECUT_PAD = 12
LINE_PAD = tc.LINE_PAD
PREDICTION = "~/.golden-chain/italic-v3-predictions-locked.txt"
README = ("LOCAL ONLY. Truth-set v3 signing crops: pixels of the book pages, with keys, boxes and sha256s. "
          "Never commit, never share the images.\n")


def line_union(words, key):
    """Unpadded union [x0, y0, x1, y1] of the OCR word boxes on the key's line, page coordinates."""
    lk = tc.line_key(key)
    bs = [w["bbox"] for w in words if tc.line_key(w["key"]) == lk]
    if not bs:
        raise Fail(f"{key}: no OCR word on its line")
    return [min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs)]


def word_cut(page, bbox, L, pad):
    """The word crop: word x range, line y range padded by pad, clipped to the page (a 2-D array)."""
    H = page.shape[0]
    return page[max(0, L[1] - pad):min(H, L[3] + pad), bbox[0]:bbox[2]]


def cut_with_recut(page, bbox, L):
    """-> (crop, pad, edges): the first cut that has no ink on its top and bottom rows, else (None, None, edges
    of the last cut)."""
    for pad in (V_PAD, RECUT_PAD):
        crop = word_cut(page, bbox, L, pad)
        e = build.edge_ink(crop)
        if not e["top"] and not e["bottom"]:
            return crop, pad, e
    return None, None, e


def main(truthset_dir, ocr_dir, out):
    git_start = git_state(REPO)
    ts, od, out = Path(truthset_dir), Path(ocr_dir), Path(out)
    cand_p, ocr_p = ts / "candidates.json", od / "ocr.json"
    for p in (cand_p, ocr_p):
        if not p.is_file():
            raise Fail(f"missing: {p}")
    rows = json.loads(cand_p.read_text(encoding="utf-8"))["rows"]
    ocr = json.loads(ocr_p.read_text(encoding="utf-8"))
    words = ocr["words"]
    by_key = {w["key"]: w for w in words}
    inputs = {"candidates.json": tc.sha256_file(cand_p), "ocr.json": tc.sha256_file(ocr_p)}
    pages = {}

    def page_img(p):
        if p not in pages:
            pp = od / "pages" / f"p{p}.png"
            if not pp.is_file():
                raise Fail(f"missing {pp}")
            inputs[f"pages/p{p}.png"] = tc.sha256_file(pp)
            pages[p] = tc.grey(pp)
        return pages[p]

    for r in rows:
        if r["key"] not in by_key:
            raise Fail(f"{r['key']}: not in ocr.json")
    out.mkdir(parents=True, exist_ok=True)
    crops, dropped = [], []
    first_ok = recut_ok = 0
    for n, r in enumerate(tc.order(rows), 1):
        pg = page_img(r["page"])
        H, W = pg.shape
        bb = r["bbox"]
        if bb != by_key[r["key"]]["bbox"]:
            raise Fail(f"{r['key']}: candidate bbox differs from ocr.json")
        if bb[0] < 0 or bb[1] < 0 or bb[2] > W or bb[3] > H or bb[2] <= bb[0] or bb[3] <= bb[1]:
            raise Fail(f"{r['key']}: bbox outside the page")
        i = f"w{n:03d}"
        L = line_union(words, r["key"])
        wc, pad, edges = cut_with_recut(pg, bb, L)
        if wc is None:
            dropped.append({"id": i, "key": r["key"], "edges": edges})
            continue
        if pad == V_PAD:
            first_ok += 1
        else:
            recut_ok += 1
        lb = tc.line_bbox(words, r["key"], (W, H))
        crops.append({"id": i, "key": r["key"], "page": r["page"], "region": r["region"],
                      "word_png": f"{i}_word.png", "word_sha256": tc.save_png(wc, out / f"{i}_word.png"),
                      "word_size": [int(wc.shape[1]), int(wc.shape[0])], "word_pad": pad,
                      "line_png": f"{i}_line.png",
                      "line_sha256": tc.save_png(tc.line_crop(pg, lb), out / f"{i}_line.png"),
                      "box": tc.box_in_line(bb, lb)})
    counts = {"n_candidates": len(rows), "first_cut_ok": first_ok, "recut_ok": recut_ok, "dropped": len(dropped)}
    doc = {"rows": crops, "dropped": dropped, "counts": counts, "candidates_digest": truthset_v2.digest(rows),
           "input": dict(sorted(inputs.items())),
           "params": {"v_pad": V_PAD, "recut_pad": RECUT_PAD, "line_pad": LINE_PAD}}
    (out / "crops.json").write_text(json.dumps(doc, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    git_end = git_state(REPO)
    header = {"run": "truthset-crops-v3",
              "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
              "script_sha256": tc.sha256_file(__file__), "prediction": PREDICTION,
              "golden_chain_git_start": git_start, "golden_chain_git_end": git_end,
              "clean_run": clean_run(git_start, git_end)}
    (out / "run_header.json").write_text(json.dumps(header, indent=1, sort_keys=True), encoding="utf-8",
                                         newline="\n")
    (out / "README.txt").write_text(README, encoding="utf-8", newline="\n")
    print(json.dumps({**counts, "clean_run": header["clean_run"]}))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(usage=__doc__)
    for a in ("truthset_dir", "ocr_dir", "out"):
        ap.add_argument(a)
    a = ap.parse_args()
    try:
        sys.exit(main(a.truthset_dir, a.ocr_dir, a.out))
    except Fail as ex:
        print(f"FAIL: {ex}", file=sys.stderr)
        sys.exit(1)
