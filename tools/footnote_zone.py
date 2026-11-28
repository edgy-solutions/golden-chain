"""Item 5: a geometry-only rule that finds the column footnote zone (lock: docs/handoff/LOCK_item5_footnote_rule_2026-11-27.md).

Usage: python tools/footnote_zone.py <ocr-dir> <align-dir> <out-dir>

Reads <ocr-dir>/ocr.json and <align-dir>/align.json. Writes <out-dir>/zones.json and README.txt only.
Geometry only: word text fields are never read and no text is written. ocr.json is hashed at start and end.
"""

import argparse
import datetime
import hashlib
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from column_rule import REPO, Fail, git_state  # noqa: E402

LOCK = "docs/handoff/LOCK_item5_footnote_rule_2026-11-27.md (895affc)"
RATIO = 0.85
MIN_LINES = 2
T2_TOL = 28
REGIONS = ("left", "right")
SLAB_ROWS, SLAB_SCALE = (3760, 3995), 6.947
README = ("LOCAL ONLY. Footnote-zone rule measurements (item 5): geometry only, no word text. "
          "zones.json holds per-column zones, T1, T2 and the scores N3-N5.\n")


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def lines(words):
    """{(page, region): [line dicts sorted by top]} for left/right regions only."""
    groups = {}
    for w in words:
        if w["region"] not in REGIONS:
            continue
        k = (w["page"], w["region"], w["block"], w["par"], w["line"])
        groups.setdefault(k, []).append(w)
    out = {}
    for (page, region, b, p, ln), ws in groups.items():
        out.setdefault((page, region), []).append({
            "key": f"{page}/{region}/{b}.{p}.{ln}",
            "top": min(w["bbox"][1] for w in ws), "bottom": max(w["bbox"][3] for w in ws),
            "type_h": statistics.median(w["bbox"][3] - w["bbox"][1] for w in ws), "n_words": len(ws)})
    for v in out.values():
        v.sort(key=lambda d: (d["top"], d["bottom"]))
    return out


def body_h(lines_by_col):
    hs = [ln["type_h"] for v in lines_by_col.values() for ln in v]
    if not hs:
        raise Fail("no column lines")
    return statistics.median(hs)


def zone(col_lines, bh, ratio=RATIO, min_lines=MIN_LINES):
    n = len(col_lines)
    small = [ln["type_h"] <= ratio * bh for ln in col_lines]
    taken, run = [], 0
    for i in range(n - 1, -1, -1):
        if small[i]:
            run = 0
            taken.append(i)
        else:
            run += 1
            if run == 2:
                taken.pop()  # the first of the two non-small lines does not join
                break
            taken.append(i)
    taken.reverse()
    while taken and not small[taken[0]]:
        taken.pop(0)
    if len(taken) < min_lines:
        return None
    f, last = taken[0], taken[-1]
    zl = [col_lines[i] for i in taken]
    zh = statistics.median(ln["type_h"] for ln in zl)
    gaps = [col_lines[i + 1]["top"] - col_lines[i]["bottom"] for i in range(n - 1)]
    return {"first_index": f, "last_index": last, "first_key": col_lines[f]["key"],
            "last_key": col_lines[last]["key"], "n_lines": len(taken),
            "boundary_y": col_lines[f]["top"], "bottom": col_lines[last]["bottom"],
            "zone_type_h": zh, "ratio_to_body": zh / bh,
            "gap": col_lines[f]["top"] - col_lines[f - 1]["bottom"] if f > 0 else None,
            "col_median_gap": statistics.median(gaps) if gaps else None}


def moved_words(words, moved_blocks, page=None, region=None):
    pos = {w["key"]: i for i, w in enumerate(words)}
    out = []
    for b in moved_blocks:
        for k in ("first_key", "last_key"):
            if b[k] not in pos:
                raise Fail(f"moved block key {b[k]} is not in ocr.json")
        for w in words[pos[b["first_key"]]:pos[b["last_key"]] + 1]:
            if w["page"] != b["page"]:
                continue
            if page is not None and w["page"] != page:
                continue
            if region is not None and w["region"] != region:
                continue
            out.append(w)
    return out


def t1(col_lines, z, words, moved_blocks, page=914, region="left"):
    ws = moved_words(words, moved_blocks, page=page, region=region)
    if not ws:
        raise Fail(f"no moved block words on p. {page} {region}")
    w = min(ws, key=lambda x: x["bbox"][1])
    lk = f"{page}/{region}/{w['block']}.{w['par']}.{w['line']}"
    keys = [ln["key"] for ln in col_lines]
    if lk not in keys:
        raise Fail(f"{lk}: not a line of the column")
    li = keys.index(lk)
    exp = li - 1
    off = None if z is None else z["first_index"] - exp
    return {"boundary_y": w["bbox"][1], "word_line_index": li, "word_line_key": lk,
            "expected_first_index": exp, "expected_first_key": keys[exp] if exp >= 0 else None,
            "zone_first_key": None if z is None else z["first_key"],
            "offset": off, "agree": off == 0}


def to850(y):
    return y * (850 / 72) / SLAB_SCALE


def t2(zones, page=913):
    top, bot = (to850(r) for r in SLAB_ROWS)
    res = {"slab_top": top, "slab_bottom": bot, "tol": T2_TOL, "columns": {}}
    for r in REGIONS:
        z = zones.get((page, r))
        ag = z is not None and z["boundary_y"] <= top + T2_TOL and z["bottom"] >= bot
        res["columns"][r] = {"agree": bool(ag), "boundary_y": None if z is None else z["boundary_y"],
                             "zone_bottom": None if z is None else z["bottom"]}
    res["agree"] = all(c["agree"] for c in res["columns"].values())
    return res


def main(ocr_dir, align_dir, out):
    git_start = git_state(REPO)
    ocr_p, align_p = Path(ocr_dir) / "ocr.json", Path(align_dir) / "align.json"
    for p in (ocr_p, align_p):
        if not p.is_file():
            raise Fail(f"missing: {p}")
    ocr_sha = sha256_file(ocr_p)
    align_sha = sha256_file(align_p)
    ocr = json.loads(ocr_p.read_text(encoding="utf-8"))
    moved = json.loads(align_p.read_text(encoding="utf-8"))["report"]["moved_blocks"]
    words = ocr["words"]
    first, last = ocr["header"]["pages_printed"]  # [first, last], as gy_ocr_baptism writes it
    pages = list(range(first, last + 1))
    lbc = lines(words)
    bh = body_h(lbc)
    zones, table = {}, {}
    for p in pages:
        for r in REGIONS:
            cl = lbc.get((p, r), [])
            z = zone(cl, bh) if cl else None
            zones[(p, r)] = z
            table[f"{p}/{r}"] = {"n_lines": len(cl), "zone": z}
    mw = {(w["page"], w["region"]) for w in moved_words(words, moved) if w["region"] in REGIONS}
    mcols = sorted(f"{p}/{r}" for (p, r) in mw if (p, r) in zones)
    n5 = sum(1 for c in mcols if table[c]["zone"] is not None)
    ratios = [z["ratio_to_body"] for z in zones.values() if z]
    res = {"body_type_h": bh, "columns": table,
           "t1": t1(lbc.get((914, "left"), []), zones.get((914, "left")), words, moved),
           "t2": t2(zones),
           "scores": {"N3_columns_with_zone": sum(1 for z in zones.values() if z), "N3_columns": len(zones),
                      "N4_median_ratio": statistics.median(ratios) if ratios else None,
                      "N5_moved_columns": len(mcols), "N5_with_zone": n5,
                      "N5_share": n5 / len(mcols) if mcols else None}}
    ocr_sha_end = sha256_file(ocr_p)
    if ocr_sha_end != ocr_sha:
        raise Fail("ocr.json changed during the run")
    git_end = git_state(REPO)
    clean = (not git_start["dirty"] and not git_end["dirty"] and git_start["commit"] == git_end["commit"])
    res["header"] = {"run": "footnote-zone",
                     "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                     "script_sha256": sha256_file(__file__), "ocr_sha256": ocr_sha, "ocr_sha256_end": ocr_sha_end,
                     "align_sha256": align_sha, "lock": LOCK,
                     "params": {"ratio": RATIO, "min_lines": MIN_LINES, "t2_tol": T2_TOL},
                     "golden_chain_git_start": git_start, "golden_chain_git_end": git_end, "clean_run": clean}
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "zones.json").write_text(json.dumps(res, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    (out / "README.txt").write_text(README, encoding="utf-8", newline="\n")
    print(json.dumps({"scores": res["scores"], "t1_agree": res["t1"]["agree"], "t2_agree": res["t2"]["agree"],
                      "clean_run": clean}))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(usage=__doc__)
    for a in ("ocr_dir", "align_dir", "out"):
        ap.add_argument(a)
    args = ap.parse_args()
    try:
        sys.exit(main(args.ocr_dir, args.align_dir, args.out))
    except Fail as ex:
        print(f"FAIL: {ex}", file=sys.stderr)
        sys.exit(1)
