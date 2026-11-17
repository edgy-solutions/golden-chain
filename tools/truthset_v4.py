"""Truth-set candidates v4: a redraw on the v4 slant measure, the v2 and v3 words excluded, with reallocation

Usage: python tools/truthset_v4.py <slant-v4-run-dir> <ocr-run-dir> <v2-candidates.json> <v3-candidates.json> <out-dir>

As tools/truthset_v3.py (strata slanted / upright / edge, ordered by sha256(SALT + key), SALT "truthset-v4/"),
on the eligible words of a tools/gy_word_slant_v4.py run, with every key of the v2 and v3 candidates removed
from the pools. Reallocation: per stratum the target is quota x number of pages. Pass 1 takes min(quota, pool)
on each page; then, round-robin over pages in ascending order, each page with words left in its pool takes its
next word, until the target is met or every pool is empty. Fails if the slant run is not measure v4, was not
made on this ocr.json, or the draw shares a key with v2 or v3. Rows carry no OCR text; signed_italic stays
null until Chris signs from pixels.
Prediction: ~/.golden-chain/italic-v4-predictions-locked.txt (name only)
Outputs are local only, never commit.
"""

import argparse
import datetime
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from column_rule import REPO, Fail, clean_run, git_state  # noqa: E402
from truthset_v2 import STRATA, digest, stratum  # noqa: E402

SALT = "truthset-v4/"
PREDICTION = "~/.golden-chain/italic-v4-predictions-locked.txt"


def order_key(key):
    return hashlib.sha256((SALT + key).encode("utf-8")).hexdigest()


def draw_with_realloc(slant_rows, bboxes, excluded=()):
    """Pure. -> (rows, realloc). Rows sorted by page, stratum order, order key. realloc[stratum] =
    {"short": {page: shortfall in pass 1}, "took": {page: extra words taken in pass 2}} (string page keys)."""
    excluded = set(excluded)
    pages = sorted({r["page"] for r in slant_rows})
    pools = {}
    for r in slant_rows:
        if r["key"] in excluded:
            continue
        s = stratum(r)
        if s is not None:
            pools.setdefault((r["page"], s), []).append(r)
    chosen, realloc = [], {}
    for s, quota in STRATA.items():
        pool = {p: sorted(pools.get((p, s), []), key=lambda r: order_key(r["key"])) for p in pages}
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
                chosen.append((p, list(STRATA).index(s), order_key(r["key"]), s, r))
        realloc[s] = {"short": {str(p): v for p, v in short.items()}, "took": {str(p): v for p, v in extra.items()}}
    chosen.sort(key=lambda t: t[:3])
    out = []
    for p, _, _, s, r in chosen:
        if r["key"] not in bboxes:
            raise Fail(f"{r['key']}: no bbox in the OCR run")
        out.append({"key": r["key"], "page": p, "region": r["region"], "bbox": bboxes[r["key"]],
                    "stratum": s, "slant": r["slant"], "signed_italic": None})
    return out, realloc


def draw(slant_rows, bboxes, excluded=()):
    return draw_with_realloc(slant_rows, bboxes, excluded)[0]


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main(slant_dir, ocr_dir, v2_path, v3_path, out):
    git_start = git_state(REPO)
    slant_path, ocr_path = Path(slant_dir) / "slant.json", Path(ocr_dir) / "ocr.json"
    v2_path, v3_path = Path(v2_path), Path(v3_path)
    for p in (slant_path, ocr_path, v2_path, v3_path):
        if not p.is_file():
            raise Fail(f"missing: {p}")
    sl = json.loads(slant_path.read_text(encoding="utf-8"))
    ocr = json.loads(ocr_path.read_text(encoding="utf-8"))
    if sl.get("params", {}).get("measure") != "v4":
        raise Fail("the slant run is not measure v4")
    if sl["input"]["ocr_json_sha256"] != sha256_file(ocr_path):
        raise Fail("the slant run was not made on this ocr.json")
    v2_keys = {r["key"] for r in json.loads(v2_path.read_text(encoding="utf-8"))["rows"]}
    v3_keys = {r["key"] for r in json.loads(v3_path.read_text(encoding="utf-8"))["rows"]}
    rows, realloc = draw_with_realloc(sl["rows"], {w["key"]: w["bbox"] for w in ocr["words"]}, v2_keys | v3_keys)
    keys = {r["key"] for r in rows}
    sh2, sh3 = len(v2_keys & keys), len(v3_keys & keys)
    if sh2 or sh3:
        raise Fail(f"drawn keys are also in the earlier candidates: {sh2} in v2, {sh3} in v3")
    all_pages = {r["page"] for r in sl["rows"]}
    summary = {"n": len(rows), "by_stratum": {s: sum(r["stratum"] == s for r in rows) for s in STRATA},
               "realloc": realloc,
               "pages_without": {s: sorted(all_pages - {r["page"] for r in rows if r["stratum"] == s})
                                 for s in STRATA},
               "excluded_v2": len(v2_keys), "excluded_v3": len(v3_keys),
               "shared_with_v2": sh2, "shared_with_v3": sh3, "digest": digest(rows)}
    git_end = git_state(REPO)
    header = {"run": "truthset-v4", "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
              "script_sha256": sha256_file(__file__),
              "input": {"slant_json_sha256": sha256_file(slant_path), "ocr_json_sha256": sl["input"]["ocr_json_sha256"],
                        "v2_candidates_sha256": sha256_file(v2_path), "v3_candidates_sha256": sha256_file(v3_path)},
              "params": {"strata": STRATA, "salt": SALT}, "prediction": PREDICTION,
              "golden_chain_git_start": git_start, "golden_chain_git_end": git_end,
              "clean_run": clean_run(git_start, git_end)}
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "candidates.json").write_text(json.dumps({"summary": summary, "rows": rows}, indent=1, sort_keys=True,
                                                    ensure_ascii=False), encoding="utf-8", newline="\n")
    (out / "run_header.json").write_text(json.dumps(header, indent=1, sort_keys=True), encoding="utf-8",
                                         newline="\n")
    (out / "README.txt").write_text("LOCAL ONLY. Truth-set v4 candidates (keys and boxes of the book's words). Never "
                                    "commit. Every signed_italic is null until Chris signs from pixels.\n",
                                    encoding="utf-8", newline="\n")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(usage=__doc__)
    for a in ("slant_dir", "ocr_dir", "v2_candidates", "v3_candidates", "out"):
        ap.add_argument(a)
    a = ap.parse_args()
    try:
        sys.exit(main(a.slant_dir, a.ocr_dir, a.v2_candidates, a.v3_candidates, a.out))
    except Fail as ex:
        print(f"FAIL: {ex}", file=sys.stderr)
        sys.exit(1)
