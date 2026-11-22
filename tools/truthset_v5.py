"""Truth-set candidates v5: the v4 draw under a new salt, with words that fail the crop check replaced

Usage: python tools/truthset_v5.py <slant-v4-run-dir> <ocr-run-dir> <v2-candidates.json> <v3-candidates.json> <v4-candidates.json> <out-dir>

First choices are truthset_v4's draw (strata slanted / upright / edge, pass 1 min(quota, pool) per page, then a
round-robin over pages in ascending order) with SALT "truthset-v5/", on the eligible words of a measure-v4 slant
run, every key of the v2, v3 and v4 candidates removed from the pools. Every first choice is checked by the crop
rule C (tools/truthset_crops_v5.crop_check: v4's rule). Ceiling: per stratum, if the first choices that fail C
exceed 10 % of that stratum's first choices, nothing is replaced: the first choices and their failures are written
with "ceiling": tripped and the tool exits 3. Otherwise each failure is replaced by the next untaken word of the
same page and stratum in order-key order (checked in turn; a failing replacement is listed and replaced the same
way); an exhausted page sends the word to a round-robin over pages in ascending order. Every failing word is
listed in drops.json (key, page, stratum, slant, side, first_choice); crops.json never carries them. Fails if the
slant run is not measure v4, was not made on this ocr.json, or a drawn key is also in v2, v3 or v4. Rows carry no
OCR text; signed_italic stays null until Chris signs from pixels. Pool and first-choice failing shares are
reported for scale only.
Prediction: ~/.golden-chain/italic-v5-predictions-locked.txt (name only)
Outputs are local only, never commit.
"""

import argparse
import datetime
import hashlib
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
from truthset_v2 import STRATA, digest, stratum  # noqa: E402

SALT = "truthset-v5/"
PREDICTION = "~/.golden-chain/italic-v5-predictions-locked.txt"
ORDER = list(STRATA)


def order_key(key):
    return hashlib.sha256((SALT + key).encode("utf-8")).hexdigest()


def _row(r, bboxes):
    if r["key"] not in bboxes:
        raise Fail(f"{r['key']}: no bbox in the OCR run")
    return {"key": r["key"], "page": r["page"], "region": r["region"], "bbox": bboxes[r["key"]],
            "stratum": stratum(r), "slant": r["slant"], "signed_italic": None}


def first_choices(slant_rows, bboxes, excluded=(), okey=order_key):
    """Pure. truthset_v4.draw_with_realloc's algorithm with the order key okey (default v5's).
    -> (rows, realloc, pools): rows sorted by page, stratum order, order key; realloc[stratum] =
    {"short": {page: shortfall in pass 1}, "took": {page: extra words in pass 2}} (string page keys);
    pools[(page, stratum)] = the sorted pool (output-format rows) after the exclusions."""
    excluded = set(excluded)
    pages = sorted({r["page"] for r in slant_rows})
    raw = {}
    for r in slant_rows:
        if r["key"] in excluded:
            continue
        s = stratum(r)
        if s is not None:
            raw.setdefault((r["page"], s), []).append(r)
    pools = {k: [_row(r, bboxes) for r in sorted(v, key=lambda r: okey(r["key"]))] for k, v in raw.items()}
    chosen, realloc = [], {}
    for s, quota in STRATA.items():
        pool = {p: pools.get((p, s), []) for p in pages}
        target = quota * len(pages)
        took_n = {p: min(quota, len(pool[p])) for p in pages}
        short = {p: quota - took_n[p] for p in pages if took_n[p] < quota}
        total = sum(took_n.values())
        extra = {}
        while total < target and any(took_n[p] < len(pool[p]) for p in pages):
            for p in pages:
                if total >= target:
                    break
                if took_n[p] < len(pool[p]):
                    took_n[p] += 1
                    extra[p] = extra.get(p, 0) + 1
                    total += 1
        for p in pages:
            for r in pool[p][:took_n[p]]:
                chosen.append((p, ORDER.index(s), okey(r["key"]), r))
        realloc[s] = {"short": {str(p): v for p, v in short.items()}, "took": {str(p): v for p, v in extra.items()}}
    chosen.sort(key=lambda t: t[:3])
    return [t[3] for t in chosen], realloc, pools


def _sort_rows(rows):
    return sorted(rows, key=lambda r: (r["page"], ORDER.index(r["stratum"]), order_key(r["key"])))


def _drop(r, side, first):
    return {"key": r["key"], "page": r["page"], "stratum": r["stratum"], "slant": r["slant"], "side": side,
            "first_choice": first}


def _sort_drops(drops):
    return sorted(drops, key=lambda d: (ORDER.index(d["stratum"]), d["page"], order_key(d["key"])))


def replace(first, pools, check, pages):
    """Rules R and X. Pure apart from calling check(row) -> None | "top" | "bottom" | "both".
    -> {"rows", "drops", "ceiling", "replacements", "by_page"}; by_page[stratum] = {"took": {page: n}} counts the
    round-robin passes. On a tripped ceiling nothing is replaced: rows = first, drops = the first-choice failures."""
    pages = sorted(pages)
    first_fail = {}
    for r in first:
        side = check(r)
        if side is not None:
            first_fail[r["key"]] = side
    ceiling = {"tripped": False, "by_stratum": {}}
    for s in STRATA:
        n_first = sum(r["stratum"] == s for r in first)
        k = sum(1 for r in first if r["stratum"] == s and r["key"] in first_fail)
        over = 10 * k > n_first
        ceiling["by_stratum"][s] = {"first": n_first, "replaced": k, "limit_exceeded": over}
        ceiling["tripped"] = ceiling["tripped"] or over
    repl = {s: {"same_page": 0, "round_robin": 0, "unmet": 0} for s in STRATA}
    by_page = {s: {"took": {}} for s in STRATA}
    failed_first = [r for r in first if r["key"] in first_fail]
    drops = [_drop(r, first_fail[r["key"]], True) for r in failed_first]
    if ceiling["tripped"]:
        return {"rows": list(first), "drops": _sort_drops(drops), "ceiling": ceiling, "replacements": repl,
                "by_page": by_page}
    kept = [r for r in first if r["key"] not in first_fail]
    taken = {r["key"] for r in first}

    def next_untaken(p, s):
        for w in pools.get((p, s), []):
            if w["key"] not in taken:
                return w
        return None

    for s in STRATA:
        queue = sorted((r for r in failed_first if r["stratum"] == s), key=lambda r: (r["page"], order_key(r["key"])))
        unmet = 0
        for f in queue:
            while True:
                w = next_untaken(f["page"], s)
                if w is None:
                    unmet += 1
                    break
                taken.add(w["key"])
                side = check(w)
                if side is None:
                    kept.append(w)
                    repl[s]["same_page"] += 1
                    break
                drops.append(_drop(w, side, False))
        while unmet > 0 and any(next_untaken(p, s) is not None for p in pages):
            for p in pages:
                if unmet == 0:
                    break
                w = next_untaken(p, s)
                if w is None:
                    continue
                taken.add(w["key"])
                side = check(w)
                if side is None:
                    kept.append(w)
                    unmet -= 1
                    repl[s]["round_robin"] += 1
                    by_page[s]["took"][str(p)] = by_page[s]["took"].get(str(p), 0) + 1
                else:
                    drops.append(_drop(w, side, False))
        repl[s]["unmet"] = unmet
    return {"rows": _sort_rows(kept), "drops": _sort_drops(drops), "ceiling": ceiling, "replacements": repl,
            "by_page": by_page}


def shares(pools, first, check):
    """For scale only: failing share over every pool word and over the first choices, per stratum."""
    pool_share, first_share = {}, {}
    for s in STRATA:
        words = [w for (p, st), ws in pools.items() if st == s for w in ws]
        fw = [r for r in first if r["stratum"] == s]
        pf = sum(check(w) is not None for w in words)
        ff = sum(check(r) is not None for r in fw)
        pool_share[s] = {"pool": len(words), "fail": pf, "share": round(pf / len(words), 4) if words else 0.0}
        first_share[s] = {"first": len(fw), "fail": ff, "share": round(ff / len(fw), 4) if fw else 0.0}
    return pool_share, first_share


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def _write(p, doc):
    p.write_text(json.dumps(doc, indent=1, sort_keys=True, ensure_ascii=False), encoding="utf-8", newline="\n")


def main(slant_dir, ocr_dir, v2_path, v3_path, v4_path, out):
    git_start = git_state(REPO)
    slant_path, ocr_path = Path(slant_dir) / "slant.json", Path(ocr_dir) / "ocr.json"
    ex_paths = [Path(v2_path), Path(v3_path), Path(v4_path)]
    for p in (slant_path, ocr_path, *ex_paths):
        if not p.is_file():
            raise Fail(f"missing: {p}")
    sl, ocr = _load(slant_path), _load(ocr_path)
    if sl.get("params", {}).get("measure") != "v4":
        raise Fail("the slant run is not measure v4")
    if sl["input"]["ocr_json_sha256"] != sha256_file(ocr_path):
        raise Fail("the slant run was not made on this ocr.json")
    ex = [{r["key"] for r in _load(p)["rows"]} for p in ex_paths]
    bboxes = {w["key"]: w["bbox"] for w in ocr["words"]}
    first, realloc, pools = first_choices(sl["rows"], bboxes, ex[0] | ex[1] | ex[2])
    words_by_key = {w["key"]: w for w in ocr["words"]}
    lines = c4.line_boxes(ocr["words"])
    imgs, memo = {}, {}

    def check(row):
        k = row["key"]
        if k not in memo:
            p = row["page"]
            if p not in imgs:
                pp = Path(ocr_dir) / "pages" / f"p{p}.png"
                if not pp.is_file():
                    raise Fail(f"missing {pp}")
                imgs[p] = tc.grey(pp)
            memo[k] = c5.crop_check(imgs[p], words_by_key, lines, row)
        return memo[k]

    pages = sorted({r["page"] for r in sl["rows"]})
    res = replace(first, pools, check, pages)
    pool_share, first_share = shares(pools, first, check)
    rows = res["rows"]
    keys = {r["key"] for r in rows} | {d["key"] for d in res["drops"]}
    sh = [len(e & keys) for e in ex]
    if any(sh):
        raise Fail(f"drawn keys are also in the earlier candidates: {sh[0]} in v2, {sh[1]} in v3, {sh[2]} in v4")
    summary = {"n": len(rows), "by_stratum": {s: sum(r["stratum"] == s for r in rows) for s in STRATA},
               "realloc": realloc, "ceiling": res["ceiling"], "replacements": res["replacements"],
               "replacements_by_page": res["by_page"], "first_choice_share": first_share, "pool_share": pool_share,
               "excluded_v2": len(ex[0]), "excluded_v3": len(ex[1]), "excluded_v4": len(ex[2]),
               "shared_with_v2": sh[0], "shared_with_v3": sh[1], "shared_with_v4": sh[2], "digest": digest(rows)}
    dr = res["drops"]
    drops = {"by_stratum": {s: sum(d["stratum"] == s for d in dr) for s in STRATA},
             "by_side": {k: sum(d["side"] == k for d in dr) for k in ("top", "bottom", "both")}, "rows": dr}
    git_end = git_state(REPO)
    header = {"run": "truthset-v5", "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
              "script_sha256": sha256_file(__file__),
              "input": {"slant_json_sha256": sha256_file(slant_path), "ocr_json_sha256": sl["input"]["ocr_json_sha256"],
                        "v2_candidates_sha256": sha256_file(ex_paths[0]),
                        "v3_candidates_sha256": sha256_file(ex_paths[1]),
                        "v4_candidates_sha256": sha256_file(ex_paths[2])},
              "params": {"strata": STRATA, "salt": SALT}, "prediction": PREDICTION,
              "golden_chain_git_start": git_start, "golden_chain_git_end": git_end,
              "clean_run": clean_run(git_start, git_end)}
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    _write(out / "candidates.json", {"summary": summary, "rows": rows})
    _write(out / "drops.json", drops)
    _write(out / "run_header.json", header)
    (out / "README.txt").write_text("LOCAL ONLY. Truth-set v5 candidates (keys and boxes of the book's words) and the "
                                    "list of words that failed the crop check. Never commit. Every signed_italic is "
                                    "null until Chris signs from pixels.\n", encoding="utf-8", newline="\n")
    print(json.dumps(summary, sort_keys=True))
    return 3 if res["ceiling"]["tripped"] else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(usage=__doc__)
    for a in ("slant_dir", "ocr_dir", "v2_candidates", "v3_candidates", "v4_candidates", "out"):
        ap.add_argument(a)
    a = ap.parse_args()
    try:
        sys.exit(main(a.slant_dir, a.ocr_dir, a.v2_candidates, a.v3_candidates, a.v4_candidates, a.out))
    except Fail as ex:
        print(f"FAIL: {ex}", file=sys.stderr)
        sys.exit(1)
