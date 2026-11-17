"""Truth-set v4 signing crops: each candidate word at its line's height, clipped between neighbouring lines.

Usage: python tools/truthset_crops_v4.py <truthset-v4-dir> <ocr-run-dir> <out-dir>

<truthset-v4-dir> holds candidates.json (tools/truthset_v4.py). Candidates take the fixed order and ids w001...
of tools/truthset_crops.py. The word crop is the page pixels at the word's OCR x range, from P = 12 px above the
line's top to P below its bottom (the line is the union of its OCR word boxes), each side clipped at the
midpoint between this line and the nearest other line of the same page and region whose x range overlaps the
word's (crop_rows), never cutting inside the line's own box, and clipped to the page. One cut, no re-cut. If
word ink (build.word_edge_ink: ink 8-connected to ink inside the word's OCR box) touches the crop's top or
bottom row the row is dropped (no PNG) and listed in "dropped" with the edge counts. The line crop is the line
padded LINE_PAD with the word's box in it. crops.json lists ids, keys, boxes, sizes and sha256s only (no
stratum, no slant, no word text) and is byte-identical across reruns; drops.json lists the dropped rows by
stratum and side (the spec builder never reads it); time and git state go to run_header.json.
Prediction: ~/.golden-chain/italic-v4-predictions-locked.txt (name only)
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

PAD = 12
LINE_PAD = tc.LINE_PAD
PREDICTION = "~/.golden-chain/italic-v4-predictions-locked.txt"
README = ("LOCAL ONLY. Truth-set v4 signing crops: pixels of the book pages, with keys, boxes and sha256s. "
          "Never commit, never share the images.\n")


def line_boxes(words):
    """{(page, region, line key): [x0, y0, x1, y1]}: the union of the OCR word boxes on each line."""
    out = {}
    for w in words:
        k = (w["page"], w["region"], tc.line_key(w["key"]))
        b = w["bbox"]
        if k in out:
            o = out[k]
            out[k] = [min(o[0], b[0]), min(o[1], b[1]), max(o[2], b[2]), max(o[3], b[3])]
        else:
            out[k] = list(b)
    return out


def crop_rows(L, bbox, lines_same_region, H, P=PAD):
    """(top, bottom) in page coordinates, bottom exclusive. L = the word's line box; lines_same_region = boxes of
    the other lines on the same page and region. Pure, integers only."""
    above = below = None
    cy = L[1] + L[3]  # twice the centre
    for ln in lines_same_region:
        if not (ln[0] < bbox[2] and ln[2] > bbox[0]):
            continue
        c = ln[1] + ln[3]
        if c < cy and (above is None or ln[3] > above[3]):
            above = ln
        elif c > cy and (below is None or ln[1] < below[1]):
            below = ln
    top = L[1] - P
    if above is not None:
        top = max(top, -((-(above[3] + L[1])) // 2))  # ceil((above.y1 + L.y0) / 2)
    top = max(min(top, L[1]), 0)
    bottom = L[3] + P
    if below is not None:
        bottom = min(bottom, (L[3] + below[1]) // 2)
    bottom = min(max(bottom, L[3]), H)
    return top, bottom


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
    lines = line_boxes(words)
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
    crops, dropped, drop_rows = [], [], []
    for n, r in enumerate(tc.order(rows), 1):
        pg = page_img(r["page"])
        H, W = pg.shape
        bb = r["bbox"]
        w = by_key[r["key"]]
        if bb != w["bbox"]:
            raise Fail(f"{r['key']}: candidate bbox differs from ocr.json")
        if bb[0] < 0 or bb[1] < 0 or bb[2] > W or bb[3] > H or bb[2] <= bb[0] or bb[3] <= bb[1]:
            raise Fail(f"{r['key']}: bbox outside the page")
        i = f"w{n:03d}"
        lk = (w["page"], w["region"], tc.line_key(r["key"]))
        L = lines[lk]
        others = [b for k, b in lines.items() if k[:2] == lk[:2] and k != lk]
        top, bottom = crop_rows(L, bb, others, H)
        wc = pg[top:bottom, bb[0]:bb[2]]
        word_box = [0, bb[1] - top, bb[2] - bb[0], bb[3] - top]
        edges = build.word_edge_ink(wc, word_box)
        if edges["top"] or edges["bottom"]:
            dropped.append({"id": i, "key": r["key"], "edges": edges})
            side = "both" if edges["top"] and edges["bottom"] else "top" if edges["top"] else "bottom"
            drop_rows.append({"id": i, "key": r["key"], "stratum": r["stratum"], "side": side})
            continue
        lb = tc.line_bbox(words, r["key"], (W, H))
        crops.append({"id": i, "key": r["key"], "page": r["page"], "region": r["region"],
                      "word_png": f"{i}_word.png", "word_sha256": tc.save_png(wc, out / f"{i}_word.png"),
                      "word_size": [int(wc.shape[1]), int(wc.shape[0])], "word_box": word_box,
                      "word_rows": [top, bottom], "line_png": f"{i}_line.png",
                      "line_sha256": tc.save_png(tc.line_crop(pg, lb), out / f"{i}_line.png"),
                      "box": tc.box_in_line(bb, lb)})
    counts = {"n_candidates": len(rows), "kept": len(crops), "dropped": len(dropped)}
    doc = {"rows": crops, "dropped": dropped, "counts": counts, "candidates_digest": truthset_v2.digest(rows),
           "input": dict(sorted(inputs.items())),
           "params": {"pad": PAD, "clip": "midpoint to neighbouring line", "edge": "word-connected ink only",
                      "line_pad": LINE_PAD}}
    (out / "crops.json").write_text(json.dumps(doc, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    drops = {"by_stratum": {}, "by_side": {"top": 0, "bottom": 0, "both": 0}, "rows": drop_rows}
    for d in drop_rows:
        drops["by_stratum"][d["stratum"]] = drops["by_stratum"].get(d["stratum"], 0) + 1
        drops["by_side"][d["side"]] += 1
    (out / "drops.json").write_text(json.dumps(drops, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    git_end = git_state(REPO)
    header = {"run": "truthset-crops-v4",
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
