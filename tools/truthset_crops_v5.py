"""Truth-set v5 signing crops: each candidate word at its line's height, clipped between neighbouring lines.

Usage: python tools/truthset_crops_v5.py <truthset-v5-dir> <ocr-run-dir> <out-dir>

<truthset-v5-dir> holds candidates.json (tools/truthset_v5.py). The crop rule is v4's, unchanged
(tools/truthset_crops_v4.py: line_boxes, crop_rows with P = 12, build.word_edge_ink), shared with the draw through
crop_check. The draw already checked every kept word, so here a word that fails the check is a bug or changed
inputs: the tool fails. It also fails if candidates.json says the ceiling tripped ("ceiling tripped: no crops, no
console"). crops.json is in v4's format (dropped is always empty; no stratum, no slant, no word text) and is
byte-identical across reruns; time and git state go to run_header.json. The drops list lives with the draw.
Prediction: ~/.golden-chain/italic-v5-predictions-locked.txt (name only)
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
import truthset_crops_v4 as c4  # noqa: E402
import truthset_v2  # noqa: E402
from column_rule import REPO, Fail, clean_run, git_state  # noqa: E402

PAD = c4.PAD
LINE_PAD = tc.LINE_PAD
PREDICTION = "~/.golden-chain/italic-v5-predictions-locked.txt"
README = ("LOCAL ONLY. Truth-set v5 signing crops: pixels of the book pages, with keys, boxes and sha256s. "
          "Never commit, never share the images.\n")


def crop_cut(page_img, words_by_key, lines, row):
    """v4's cut for one candidate row -> (top, bottom, word crop, word_box, edges)."""
    H = page_img.shape[0]
    bb = row["bbox"]
    w = words_by_key[row["key"]]
    lk = (w["page"], w["region"], tc.line_key(row["key"]))
    L = lines[lk]
    others = [b for k, b in lines.items() if k[:2] == lk[:2] and k != lk]
    top, bottom = c4.crop_rows(L, bb, others, H, c4.PAD)
    wc = page_img[top:bottom, bb[0]:bb[2]]
    word_box = [0, bb[1] - top, bb[2] - bb[0], bb[3] - top]
    return top, bottom, wc, word_box, build.word_edge_ink(wc, word_box)


def crop_check(page_img, words_by_key, lines, row):
    """The crop rule C: None, or "top" / "bottom" / "both" where word ink touches the crop's edge."""
    edges = crop_cut(page_img, words_by_key, lines, row)[4]
    if edges["top"] and edges["bottom"]:
        return "both"
    return "top" if edges["top"] else "bottom" if edges["bottom"] else None


def main(truthset_dir, ocr_dir, out):
    git_start = git_state(REPO)
    ts, od, out = Path(truthset_dir), Path(ocr_dir), Path(out)
    cand_p, ocr_p = ts / "candidates.json", od / "ocr.json"
    for p in (cand_p, ocr_p):
        if not p.is_file():
            raise Fail(f"missing: {p}")
    cand = json.loads(cand_p.read_text(encoding="utf-8"))
    if cand.get("summary", {}).get("ceiling", {}).get("tripped"):
        raise Fail("ceiling tripped: no crops, no console")
    rows = cand["rows"]
    ocr = json.loads(ocr_p.read_text(encoding="utf-8"))
    words = ocr["words"]
    by_key = {w["key"]: w for w in words}
    lines = c4.line_boxes(words)
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
    crops = []
    for n, r in enumerate(tc.order(rows), 1):
        pg = page_img(r["page"])
        H, W = pg.shape
        bb = r["bbox"]
        if bb != by_key[r["key"]]["bbox"]:
            raise Fail(f"{r['key']}: candidate bbox differs from ocr.json")
        if bb[0] < 0 or bb[1] < 0 or bb[2] > W or bb[3] > H or bb[2] <= bb[0] or bb[3] <= bb[1]:
            raise Fail(f"{r['key']}: bbox outside the page")
        i = f"w{n:03d}"
        top, bottom, wc, word_box, edges = crop_cut(pg, by_key, lines, r)
        if edges["top"] or edges["bottom"]:
            raise Fail(f"{r['key']}: fails the crop check ({edges}); the draw checked every candidate, "
                       "so this is a bug or changed inputs")
        lb = tc.line_bbox(words, r["key"], (W, H))
        crops.append({"id": i, "key": r["key"], "page": r["page"], "region": r["region"],
                      "word_png": f"{i}_word.png", "word_sha256": tc.save_png(wc, out / f"{i}_word.png"),
                      "word_size": [int(wc.shape[1]), int(wc.shape[0])], "word_box": word_box,
                      "word_rows": [top, bottom], "line_png": f"{i}_line.png",
                      "line_sha256": tc.save_png(tc.line_crop(pg, lb), out / f"{i}_line.png"),
                      "box": tc.box_in_line(bb, lb)})
    counts = {"n_candidates": len(rows), "kept": len(crops), "dropped": 0}
    doc = {"rows": crops, "dropped": [], "counts": counts, "candidates_digest": truthset_v2.digest(rows),
           "input": dict(sorted(inputs.items())),
           "params": {"pad": PAD, "clip": "midpoint to neighbouring line", "edge": "word-connected ink only",
                      "line_pad": LINE_PAD}}
    (out / "crops.json").write_text(json.dumps(doc, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    git_end = git_state(REPO)
    header = {"run": "truthset-crops-v5",
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
