"""Truth-set candidates v3: a new draw on the v3 slant measure, the v2 words excluded

Usage: python tools/truthset_v3.py <slant-v3-run-dir> <ocr-run-dir> <v2-candidates.json> <out-dir>

As tools/truthset_v2.py (strata slanted / upright / edge, STRATA words per page and stratum, ordered by
sha256(SALT + key)) with SALT "truthset-v3/", on the eligible words of a tools/gy_word_slant_v3.py run, and with
every key of the v2 candidates removed from the pools before drawing, so the two sets share no word. Fails if
the slant run is not measure v3, was not made on this ocr.json, or the draw shares a key with v2. Rows carry no
OCR text; signed_italic stays null until Chris signs from pixels.
Prediction: ~/.golden-chain/italic-v3-predictions-locked.txt (name only)
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

SALT = "truthset-v3/"
PREDICTION = "~/.golden-chain/italic-v3-predictions-locked.txt"


def order_key(key):
    return hashlib.sha256((SALT + key).encode("utf-8")).hexdigest()


def draw(slant_rows, bboxes, excluded=()):
    """Pure. Rows sorted by page, stratum, order key; keys in `excluded` never enter a pool."""
    excluded = set(excluded)
    pools = {}
    for r in slant_rows:
        if r["key"] in excluded:
            continue
        s = stratum(r)
        if s is not None:
            pools.setdefault((r["page"], s), []).append(r)
    out = []
    for page in sorted({r["page"] for r in slant_rows}):
        for s in STRATA:
            pool = sorted(pools.get((page, s), []), key=lambda r: order_key(r["key"]))
            for r in pool[:STRATA[s]]:
                if r["key"] not in bboxes:
                    raise Fail(f"{r['key']}: no bbox in the OCR run")
                out.append({"key": r["key"], "page": page, "region": r["region"], "bbox": bboxes[r["key"]],
                            "stratum": s, "slant": r["slant"], "signed_italic": None})
    return out


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main(slant_dir, ocr_dir, v2_path, out):
    git_start = git_state(REPO)
    slant_path, ocr_path, v2_path = Path(slant_dir) / "slant.json", Path(ocr_dir) / "ocr.json", Path(v2_path)
    for p in (slant_path, ocr_path, v2_path):
        if not p.is_file():
            raise Fail(f"missing: {p}")
    sl = json.loads(slant_path.read_text(encoding="utf-8"))
    ocr = json.loads(ocr_path.read_text(encoding="utf-8"))
    if sl.get("params", {}).get("measure") != "v3":
        raise Fail("the slant run is not measure v3")
    if sl["input"]["ocr_json_sha256"] != sha256_file(ocr_path):
        raise Fail("the slant run was not made on this ocr.json")
    v2_keys = {r["key"] for r in json.loads(v2_path.read_text(encoding="utf-8"))["rows"]}
    rows = draw(sl["rows"], {w["key"]: w["bbox"] for w in ocr["words"]}, v2_keys)
    shared = len(v2_keys & {r["key"] for r in rows})
    if shared:
        raise Fail(f"{shared} drawn keys are also in the v2 candidates")
    all_pages = {r["page"] for r in sl["rows"]}
    summary = {"n": len(rows), "by_stratum": {s: sum(r["stratum"] == s for r in rows) for s in STRATA},
               "pages_without": {s: sorted(all_pages - {r["page"] for r in rows if r["stratum"] == s})
                                 for s in STRATA},
               "excluded_v2": len(v2_keys), "shared_with_v2": shared, "digest": digest(rows)}
    git_end = git_state(REPO)
    header = {"run": "truthset-v3", "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
              "script_sha256": sha256_file(__file__),
              "input": {"slant_json_sha256": sha256_file(slant_path), "ocr_json_sha256": sl["input"]["ocr_json_sha256"],
                        "v2_candidates_sha256": sha256_file(v2_path)},
              "params": {"strata": STRATA, "salt": SALT}, "prediction": PREDICTION,
              "golden_chain_git_start": git_start, "golden_chain_git_end": git_end,
              "clean_run": clean_run(git_start, git_end)}
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "candidates.json").write_text(json.dumps({"summary": summary, "rows": rows}, indent=1, sort_keys=True,
                                                    ensure_ascii=False), encoding="utf-8", newline="\n")
    (out / "run_header.json").write_text(json.dumps(header, indent=1, sort_keys=True), encoding="utf-8",
                                         newline="\n")
    (out / "README.txt").write_text("LOCAL ONLY. Truth-set v3 candidates (keys and boxes of the book's words). Never "
                                    "commit. Every signed_italic is null until Chris signs from pixels.\n",
                                    encoding="utf-8", newline="\n")
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(usage=__doc__)
    for a in ("slant_dir", "ocr_dir", "v2_candidates", "out"):
        ap.add_argument(a)
    a = ap.parse_args()
    try:
        sys.exit(main(a.slant_dir, a.ocr_dir, a.v2_candidates, a.out))
    except Fail as ex:
        print(f"FAIL: {ex}", file=sys.stderr)
        sys.exit(1)
