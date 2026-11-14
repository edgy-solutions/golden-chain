"""Truth-set v2 signing crops (ruling on report 14, Q7): each candidate word as cut, and its printed line.

Usage: python tools/truthset_crops.py <truthset-dir> <ocr-run-dir> <ccel-align-dir> <out-dir>

<truthset-dir> holds candidates.json (tools/truthset_v2.py); its digest must equal EXPECTED_DIGEST. For each
candidate, in the fixed order sha256(SALT + key), the tool writes w%03d_word.png (the page pixels at the
word's OCR box, as cut: no padding, no scaling) and w%03d_line.png (the union of every OCR word of the same
printed line, padded LINE_PAD, clipped to the page; the word's box in it is listed as "box"). It also writes
p912_left.png (the whole p. 912 left column) and p914_left_foot.png (the p. 914 left column from FOOT_PAD above
the first word of the CCEL-moved blocks to the column's bottom). crops.json lists ids, keys, pages, boxes and
sha256s only: no stratum, no slant, no word text, and it is byte-identical across reruns; the time and git
state go to run_header.json. Needs numpy, pillow.
Prediction: ~/.golden-chain/r14-q7-truthset-console-predictions-locked.txt (locked before this file existed)
Outputs are local only, never commit.
"""

import argparse
import datetime
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import truthset_v2  # noqa: E402
from column_rule import REPO, Fail, clean_run, git_state  # noqa: E402

SALT = "truthset-v2-console/"
LINE_PAD = 12
FOOT_PAD = 30
EXPECTED_DIGEST = "34de37bac8975af603abda91cb0c1ae054b309176b89183ff8ec2439b892de7f"
PREDICTION = "~/.golden-chain/r14-q7-truthset-console-predictions-locked.txt"
FOOT_PAGE, FOOT_REGION = 914, "left"
FULL_PAGE, FULL_REGION = 912, "left"

README = ("LOCAL ONLY. Truth-set v2 signing crops: pixels of the book pages, with keys, boxes and sha256s. "
          "Never commit, never share the images.\n")


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def order(rows):
    """Rows sorted by sha256(SALT + key), independent of the input order, page and stratum."""
    return sorted(rows, key=lambda r: hashlib.sha256((SALT + r["key"]).encode("utf-8")).hexdigest())


def line_key(key):
    return key.rsplit(".", 1)[0]


def line_bbox(words, key, page_wh):
    """Union of the bboxes of all words on the key's line, padded LINE_PAD, clipped to the page (w, h)."""
    lk = line_key(key)
    bs = [w["bbox"] for w in words if line_key(w["key"]) == lk]
    if not bs:
        raise Fail(f"{key}: no OCR word on its line")
    W, H = page_wh
    return [max(0, min(b[0] for b in bs) - LINE_PAD), max(0, min(b[1] for b in bs) - LINE_PAD),
            min(W, max(b[2] for b in bs) + LINE_PAD), min(H, max(b[3] for b in bs) + LINE_PAD)]


def word_crop(page_img, bbox):
    x0, y0, x1, y1 = bbox
    return page_img[y0:y1, x0:x1]


def line_crop(page_img, lb):
    return word_crop(page_img, lb)


def box_in_line(bbox, lb):
    return [bbox[0] - lb[0], bbox[1] - lb[1], bbox[2] - lb[0], bbox[3] - lb[1]]


def foot_box(words, moved_blocks, page=FOOT_PAGE, region=FOOT_REGION, *, ytop=0, region_wh=None):
    """Crop box [x0, y0, x1, y1] in REGION coordinates: full width, from FOOT_PAD above the first word of the
    moved blocks (on page and region) to the region's bottom."""
    if region_wh is None:
        raise Fail("foot_box: region_wh is required")
    idx = {w["key"]: i for i, w in enumerate(words)}
    ys = []
    for blk in moved_blocks:
        if blk["page"] != page:
            continue
        for k in ("first_key", "last_key"):
            if blk[k] not in idx:
                raise Fail(f"moved block {k} {blk[k]} is not in ocr.json")
        i0, i1 = idx[blk["first_key"]], idx[blk["last_key"]]
        ys += [w["bbox"][1] for w in words[i0:i1 + 1] if w["page"] == page and w["region"] == region]
    if not ys:
        raise Fail(f"no moved block words on p. {page} {region}")
    W, H = region_wh
    return [0, max(0, min(ys) - ytop - FOOT_PAD), W, H]


def save_png(arr, path):
    arr = np.ascontiguousarray(arr)
    Image.fromarray(arr, "L").save(path, optimize=False)
    if not np.array_equal(np.asarray(Image.open(path)), arr):
        raise Fail(f"{Path(path).name}: written pixels differ from the crop")
    return sha256_file(path)


def grey(path):
    return np.asarray(Image.open(path).convert("L"))


def main(truthset_dir, ocr_dir, align_dir, out):
    git_start = git_state(REPO)
    ts, od, ad, out = Path(truthset_dir), Path(ocr_dir), Path(align_dir), Path(out)
    cand_p, ocr_p, align_p = ts / "candidates.json", od / "ocr.json", ad / "align.json"
    for p in (cand_p, ocr_p, align_p):
        if not p.is_file():
            raise Fail(f"missing: {p}")
    rows = json.loads(cand_p.read_text(encoding="utf-8"))["rows"]
    dg = truthset_v2.digest(rows)
    if dg != EXPECTED_DIGEST:
        raise Fail(f"candidates digest {dg} differs from the expected {EXPECTED_DIGEST}")
    ocr = json.loads(ocr_p.read_text(encoding="utf-8"))
    words = ocr["words"]
    splits = ocr["header"].get("splits", {})
    by_key = {w["key"]: w for w in words}
    moved = json.loads(align_p.read_text(encoding="utf-8"))["report"]["moved_blocks"]
    inputs = {"candidates.json": sha256_file(cand_p), "ocr.json": sha256_file(ocr_p),
              "align.json": sha256_file(align_p)}
    pages = {}

    def page_img(p):
        if p not in pages:
            pp = od / "pages" / f"p{p}.png"
            if not pp.is_file():
                raise Fail(f"missing {pp}")
            inputs[f"pages/p{p}.png"] = sha256_file(pp)
            pages[p] = grey(pp)
        return pages[p]

    for r in rows:
        if r["key"] not in by_key:
            raise Fail(f"{r['key']}: not in ocr.json")
    out.mkdir(parents=True, exist_ok=True)
    crops = []
    for n, r in enumerate(order(rows), 1):
        pg = page_img(r["page"])
        H, W = pg.shape
        bb = r["bbox"]
        if bb != by_key[r["key"]]["bbox"]:
            raise Fail(f"{r['key']}: candidate bbox differs from ocr.json")
        if bb[0] < 0 or bb[1] < 0 or bb[2] > W or bb[3] > H or bb[2] <= bb[0] or bb[3] <= bb[1]:
            raise Fail(f"{r['key']}: bbox outside the page")
        lb = line_bbox(words, r["key"], (W, H))
        wc = word_crop(pg, bb)
        i = f"w{n:03d}"
        crops.append({"id": i, "key": r["key"], "page": r["page"], "region": r["region"],
                      "word_png": f"{i}_word.png", "word_sha256": save_png(wc, out / f"{i}_word.png"),
                      "word_size": [int(wc.shape[1]), int(wc.shape[0])],
                      "line_png": f"{i}_line.png",
                      "line_sha256": save_png(line_crop(pg, lb), out / f"{i}_line.png"),
                      "box": box_in_line(bb, lb)})
    # the whole p. 912 left column
    rp = od / "regions" / f"p{FULL_PAGE}-{FULL_REGION}.png"
    if not rp.is_file():
        raise Fail(f"missing {rp}")
    inputs[f"regions/p{FULL_PAGE}-{FULL_REGION}.png"] = sha256_file(rp)
    extra = {"p912_left": {"png": "p912_left.png", "sha256": save_png(grey(rp), out / "p912_left.png")}}
    # the p. 914 left foot
    fp = od / "regions" / f"p{FOOT_PAGE}-{FOOT_REGION}.png"
    if not fp.is_file():
        raise Fail(f"missing {fp}")
    inputs[f"regions/p{FOOT_PAGE}-{FOOT_REGION}.png"] = sha256_file(fp)
    reg = grey(fp)
    if str(FOOT_PAGE) not in splits:
        raise Fail(f"p.{FOOT_PAGE}: no split in ocr.json header")
    box = foot_box(words, moved, FOOT_PAGE, FOOT_REGION, ytop=int(splits[str(FOOT_PAGE)]["ytop"]),
                   region_wh=(reg.shape[1], reg.shape[0]))
    extra["p914_left_foot"] = {"png": "p914_left_foot.png", "box_region": box,
                               "sha256": save_png(word_crop(reg, box), out / "p914_left_foot.png")}
    doc = {"rows": crops, "extra": extra, "candidates_digest": dg, "input": dict(sorted(inputs.items())),
           "params": {"salt": SALT, "line_pad": LINE_PAD, "foot_pad": FOOT_PAD}}
    (out / "crops.json").write_text(json.dumps(doc, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    git_end = git_state(REPO)
    header = {"run": "truthset-crops",
              "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
              "script_sha256": sha256_file(__file__), "prediction": PREDICTION,
              "golden_chain_git_start": git_start, "golden_chain_git_end": git_end,
              "clean_run": clean_run(git_start, git_end)}
    (out / "run_header.json").write_text(json.dumps(header, indent=1, sort_keys=True), encoding="utf-8",
                                         newline="\n")
    (out / "README.txt").write_text(README, encoding="utf-8", newline="\n")
    print(json.dumps({"word_rows": len(crops), "files": 2 * len(crops) + 2, "foot_box": box,
                      "clean_run": header["clean_run"]}))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(usage=__doc__)
    for a in ("truthset_dir", "ocr_dir", "align_dir", "out"):
        ap.add_argument(a)
    a = ap.parse_args()
    try:
        sys.exit(main(a.truthset_dir, a.ocr_dir, a.align_dir, a.out))
    except Fail as ex:
        print(f"FAIL: {ex}", file=sys.stderr)
        sys.exit(1)
