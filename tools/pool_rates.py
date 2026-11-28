"""Pool crop-check failure rates per stratum, page and group (lock item 4). Counts only.

Usage: python tools/pool_rates.py <slant-v4-run-dir> <ocr-run-dir> <out-dir> [--group NAME=a-b[,c-d]]...

For every row of a measure-v4 slant run that has a stratum (slanted / upright / edge), runs truthset_v5's crop
check (tools/truthset_crops_v5.crop_check) and counts failures. No draw, no order key, no salt, no exclusions.
Output holds counts only: never keys, text or boxes.
Lock: docs/handoff/LOCK_item4_gill_book2_2026-11-27.md
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
import truthset_crops as tc  # noqa: E402
import truthset_crops_v4 as c4  # noqa: E402
import truthset_crops_v5 as c5  # noqa: E402
from column_rule import REPO, Fail, clean_run, git_state  # noqa: E402
from truthset_v2 import STRATA, stratum  # noqa: E402
from truthset_v5 import _load, sha256_file  # noqa: E402

LOCK = "docs/handoff/LOCK_item4_gill_book2_2026-11-27.md"
SIDES = ("top", "bottom", "both")


def parse_group(s):
    """"NAME=a-b,c-d" -> (name, set of pages)."""
    name, sep, rng = s.partition("=")
    if not sep or not name.strip() or not rng.strip():
        raise Fail(f"malformed --group: {s!r}")
    pages = set()
    for part in rng.split(","):
        a, _, b = part.strip().partition("-")
        try:
            lo, hi = int(a), int(b or a)
        except ValueError:
            raise Fail(f"malformed --group range: {part!r}")
        if lo > hi:
            raise Fail(f"--group range {part!r} has first > last")
        pages.update(range(lo, hi + 1))
    return name.strip(), pages


def _tally(rows_checked):
    """rows_checked: [(stratum, side)] -> {stratum: {pool, fail, share, by_side}}"""
    out = {}
    for s in STRATA:
        mine = [side for st, side in rows_checked if st == s]
        fail = sum(side is not None for side in mine)
        out[s] = {"pool": len(mine), "fail": fail, "share": round(fail / len(mine), 4) if mine else 0.0,
                  "by_side": {k: sum(side == k for side in mine) for k in SIDES}}
    return out


def rates(rows, check, groups=None):
    """Pure apart from check(row) -> None | "top" | "bottom" | "both". rows: slant rows (need stratum() fields,
    key, page). groups: {name: set of pages}. Returns counts only."""
    checked = []  # (page, stratum, side)
    other = 0
    for r in rows:
        s = stratum(r)
        if s is None:
            other += 1
            continue
        row = dict(r, stratum=s)
        checked.append((r["page"], s, check(row)))
    per_page = {}
    for p in sorted({c[0] for c in checked}):
        pg = {}
        for s in STRATA:
            mine = [side for q, st, side in checked if q == p and st == s]
            pg[s] = {"pool": len(mine), "fail": sum(side is not None for side in mine)}
        per_page[str(p)] = pg
    summary = {"rows_total": len(rows), "rows_abstained_other": other,
               "by_stratum": _tally([(s, side) for _p, s, side in checked]), "by_page": per_page}
    if groups:
        summary["groups"] = {name: _tally([(s, side) for p, s, side in checked if p in pages])
                             for name, pages in groups.items()}
    return summary


def main(slant_dir, ocr_dir, out, groups=()):
    git_start = git_state(REPO)
    slant_path, ocr_path = Path(slant_dir) / "slant.json", Path(ocr_dir) / "ocr.json"
    for p in (slant_path, ocr_path):
        if not p.is_file():
            raise Fail(f"missing: {p}")
    gdict = dict(parse_group(g) for g in groups)
    sl, ocr = _load(slant_path), _load(ocr_path)
    if sl.get("params", {}).get("measure") != "v4":
        raise Fail("the slant run is not measure v4")
    if sl["input"]["ocr_json_sha256"] != sha256_file(ocr_path):
        raise Fail("the slant run was not made on this ocr.json")
    bboxes = {w["key"]: w["bbox"] for w in ocr["words"]}
    words_by_key = {w["key"]: w for w in ocr["words"]}
    lines = c4.line_boxes(ocr["words"])
    imgs, memo = {}, {}

    def check(row):
        k = row["key"]
        if k not in memo:
            if k not in bboxes:
                raise Fail(f"{k}: no bbox in the OCR run")
            p = row["page"]
            if p not in imgs:
                pp = Path(ocr_dir) / "pages" / f"p{p}.png"
                if not pp.is_file():
                    raise Fail(f"missing {pp}")
                imgs[p] = tc.grey(pp)
            full = {"key": k, "page": p, "region": row["region"], "bbox": bboxes[k],
                    "stratum": row["stratum"], "slant": row["slant"], "signed_italic": None}
            memo[k] = c5.crop_check(imgs[p], words_by_key, lines, full)
        return memo[k]

    summary = rates(sl["rows"], check, gdict or None)
    git_end = git_state(REPO)
    header = {"run": "pool-rates",
              "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
              "script_sha256": sha256_file(__file__),
              "input": {"slant_json_sha256": sha256_file(slant_path), "ocr_json_sha256": sha256_file(ocr_path)},
              "lock": LOCK, "golden_chain_git_start": git_start, "golden_chain_git_end": git_end,
              "clean_run": clean_run(git_start, git_end)}
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "pool.json").write_text(json.dumps({"header": header, "summary": summary}, indent=1, sort_keys=True,
                                              ensure_ascii=False), encoding="utf-8", newline="\n")
    (out / "README.txt").write_text("LOCAL ONLY. Counts only: pool and crop-check failure rates per stratum, page "
                                    "and group. No keys, text or boxes. Never commit.\n",
                      encoding="utf-8", newline="\n")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(usage=__doc__)
    ap.add_argument("slant_dir")
    ap.add_argument("ocr_dir")
    ap.add_argument("out")
    ap.add_argument("--group", action="append", default=[])
    a = ap.parse_args()
    try:
        sys.exit(main(a.slant_dir, a.ocr_dir, a.out, a.group))
    except Fail as ex:
        print(f"FAIL: {ex}", file=sys.stderr)
        sys.exit(1)
