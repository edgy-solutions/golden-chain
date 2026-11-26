"""Italic-span signing crops: 40 spans drawn (20 paired, 20 unpaired), each cut as a band of its lines.

Usage: python tools/italic_span_crops.py <spans-dir> <ocr-run-dir> <out-dir>

<spans-dir> holds spans.json (tools/italic_spans.py); <ocr-run-dir> holds ocr.json and pages/p<N>.png.
The draw (LOCK_italic_console_2026-11-26): spans sorted by page, region (left before right) and reading order of
first_key (tools/italic_spans.region_lists gives the order); each group (paired = paired_ref_key not null,
unpaired) separately, round-robin over the pages in ascending order, round k taking each page's k-th span, until
20 are taken; a group with fewer than 20 fails. The band for a span is its printed lines with two lines either
side in the same page and region, at the full column width, cut with truthset_crops_v4.crop_rows. Boxes: one per
printed line the span touches. Rows get ids s01..s40 in tc.order over first_key (a fixed shuffled order).
crops.json (rows: id, key, last_key, page, region, png, sha256, boxes, n_lines, short) never says paired, and
holds no word text; it is byte-identical across reruns; time and git state go to run_header.json.
draw.json holds the paired/unpaired split for the later counts tool: draw.json must never feed the console.
Fails on a missing file, on spans.json's recorded ocr sha differing from ocr.json's, and on an out-dir that exists
and is not empty. Outputs are local only, never commit.
"""

import datetime
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TOOLS / "console"))
import italic_spans as isp  # noqa: E402
import truthset_crops as tc  # noqa: E402
import truthset_crops_v4 as c4  # noqa: E402
from column_rule import REPO, Fail, clean_run, git_state  # noqa: E402

PAD = c4.PAD
N_PER_GROUP = 20
CONTEXT = 2
README = ("LOCAL ONLY. Italic-span signing crops: pixels of the book pages, with keys, boxes and sha256s. "
          "Never commit, never share the images.\n")


def sort_spans(spans, region_words):
    """Spans by (page, region order, reading index of first_key). region_words = {(page, region): [keys]}."""
    def k(s):
        keys = region_words.get((s["page"], s["region"]))
        if keys is None or s["first_key"] not in keys or s["last_key"] not in keys:
            raise Fail(f"{s['first_key']}: span not in the OCR words of its page and region")
        return (s["page"], isp.REGIONS[s["region"]], keys.index(s["first_key"]))
    return sorted(spans, key=k)


def round_robin(spans, n=N_PER_GROUP):
    """The first n spans taken round by round over the pages in ascending order (spans already sorted)."""
    by_page = {}
    for s in spans:
        by_page.setdefault(s["page"], []).append(s)
    pages = sorted(by_page)
    out, k = [], 0
    while len(out) < n and any(len(by_page[p]) > k for p in pages):
        for p in pages:
            if len(by_page[p]) > k and len(out) < n:
                out.append(by_page[p][k])
        k += 1
    if len(out) < n:
        raise Fail(f"a group has {len(out)} spans, fewer than {n}")
    return out


def draw(spans, region_words, n=N_PER_GROUP):
    """(paired, unpaired): n spans each, in draw order. Pure."""
    s = sort_spans(spans, region_words)
    return (round_robin([x for x in s if x.get("paired_ref_key") is not None], n),
            round_robin([x for x in s if x.get("paired_ref_key") is None], n))


def band(span, words_ordered, lines, page_wh):
    """One span's cut: (x0, top, x1, bottom, boxes in page coordinates, n_lines, short). Pure."""
    W, H = page_wh
    page, region = span["page"], span["region"]
    lk = {k: b for k, b in lines.items() if k[:2] == (page, region)}
    ordered = sorted(lk, key=lambda k: (lk[k][1] + lk[k][3], k))
    idx = {k: i for i, k in enumerate(ordered)}
    keys = [w["key"] for w in words_ordered]
    a, b = keys.index(span["first_key"]), keys.index(span["last_key"])
    seg = words_ordered[a:b + 1]
    i0 = idx[(page, region, tc.line_key(span["first_key"]))]
    i1 = idx[(page, region, tc.line_key(span["last_key"]))]
    n = len(ordered)
    lo, hi = max(0, i0 - CONTEXT), min(n - 1, i1 + CONTEXT)
    short = (i0 < CONTEXT) or (i1 > n - 1 - CONTEXT)
    x0 = max(0, min(lk[k][0] for k in ordered))
    x1 = min(W, max(lk[k][2] for k in ordered))
    first, last = lk[ordered[lo]], lk[ordered[hi]]
    top = c4.crop_rows(first, [x0, first[1], x1, first[3]],
                       [lk[k] for k in ordered if k != ordered[lo]], H, PAD)[0]
    bottom = c4.crop_rows(last, [x0, last[1], x1, last[3]],
                          [lk[k] for k in ordered if k != ordered[hi]], H, PAD)[1]
    per = {}
    for w in seg:
        k = (page, region, tc.line_key(w["key"]))
        bb = w["bbox"]
        o = per.get(k)
        per[k] = list(bb) if o is None else [min(o[0], bb[0]), min(o[1], bb[1]), max(o[2], bb[2]), max(o[3], bb[3])]
    boxes = []
    for k in sorted(per, key=lambda k: idx[k]):
        bx0, by0, bx1, by1 = per[k]
        boxes.append([max(bx0, x0), max(by0, top), min(bx1, x1), min(by1, bottom)])
    return x0, top, x1, bottom, boxes, hi - lo + 1, short


def main(spans_dir, ocr_dir, out):
    git_start = git_state(REPO)
    sd, od, out = Path(spans_dir), Path(ocr_dir), Path(out)
    spans_p, ocr_p = sd / "spans.json", od / "ocr.json"
    for p in (spans_p, ocr_p):
        if not p.is_file():
            raise Fail(f"missing: {p}")
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise Fail(f"out-dir exists and is not empty: {out}")
    sj = json.loads(spans_p.read_text(encoding="utf-8"))
    ocr_sha = tc.sha256_file(ocr_p)
    if sj.get("input", {}).get("ocr_json_sha256") != ocr_sha:
        raise Fail("spans.json input.ocr_json_sha256 does not match sha256 of ocr.json")
    ocr = json.loads(ocr_p.read_text(encoding="utf-8"))
    words = ocr["words"]
    ordered = {(p, r): ws for p, r, ws, _s in isp.region_lists(ocr, {"rows": []})}
    region_keys = {k: [w["key"] for w in ws] for k, ws in ordered.items()}
    lines = c4.line_boxes(words)
    paired, unpaired = draw(sj["spans"], region_keys)
    group = {id(s): "paired" for s in paired}
    group.update({id(s): "unpaired" for s in unpaired})
    drawn = [{"key": s["first_key"], "span": s} for s in paired + unpaired]
    if len({d["key"] for d in drawn}) != len(drawn):
        raise Fail("two drawn spans share a first_key")
    inputs = {"spans.json": tc.sha256_file(spans_p), "ocr.json": ocr_sha}
    pages = {}

    def page_img(p):
        if p not in pages:
            pp = od / "pages" / f"p{p}.png"
            if not pp.is_file():
                raise Fail(f"missing {pp}")
            inputs[f"pages/p{p}.png"] = tc.sha256_file(pp)
            pages[p] = tc.grey(pp)
        return pages[p]

    out.mkdir(parents=True, exist_ok=True)
    rows, draw_rows = [], []
    for n, d in enumerate(tc.order(drawn), 1):
        s = d["span"]
        pg = page_img(s["page"])
        H, W = pg.shape
        x0, top, x1, bottom, boxes, n_lines, short = band(s, ordered[(s["page"], s["region"])], lines, (W, H))
        i = f"s{n:02d}"
        sha = tc.save_png(pg[top:bottom, x0:x1], out / f"{i}.png")
        rows.append({"id": i, "key": s["first_key"], "last_key": s["last_key"], "page": s["page"],
                     "region": s["region"], "png": f"{i}.png", "sha256": sha,
                     "boxes": [{"x": b[0] - x0, "y": b[1] - top, "w": b[2] - b[0], "h": b[3] - b[1]}
                               for b in boxes],
                     "n_lines": n_lines, "short": short})
        draw_rows.append({"id": i, "key": s["first_key"], "group": group[id(s)]})
    doc = {"rows": rows, "input": dict(sorted(inputs.items())),
           "params": {"draw": "round-robin by page, 20 paired + 20 unpaired", "context_lines": CONTEXT}}
    (out / "crops.json").write_text(json.dumps(doc, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    dj = {"note": "the paired/unpaired split for the counts tool; this file must never feed the console",
          "rows": draw_rows}
    (out / "draw.json").write_text(json.dumps(dj, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    git_end = git_state(REPO)
    header = {"run": "italic-span-crops",
              "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
              "script_sha256": tc.sha256_file(__file__),
              "golden_chain_git_start": git_start, "golden_chain_git_end": git_end,
              "clean_run": clean_run(git_start, git_end)}
    (out / "run_header.json").write_text(json.dumps(header, indent=1, sort_keys=True), encoding="utf-8",
                                         newline="\n")
    (out / "README.txt").write_text(README, encoding="utf-8", newline="\n")
    print(json.dumps({"rows": len(rows), "short": sum(r["short"] for r in rows),
                      "clean_run": header["clean_run"]}))
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    try:
        sys.exit(main(*sys.argv[1:]))
    except Fail as ex:
        print(f"FAIL: {ex}", file=sys.stderr)
        sys.exit(1)
