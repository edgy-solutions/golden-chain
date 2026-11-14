"""Truth-set candidates v2: page- and slant-stratified (ruling on report 13, item 17)

Usage: python tools/truthset_v2.py <slant-run-dir> <ocr-run-dir> <out-dir>

Population: the eligible column words of a slant run (tools/gy_word_slant.py), each in one stratum:
slanted, upright (measured) or edge (abstained). Per page: STRATA words per stratum, ordered by
sha256(SALT + key), the first n taken (fewer if the stratum has fewer). Rows carry no OCR text: the
signer reads the word from pixels. The run-1 candidates (legacy-flag strata) stay on record, unsigned;
their overlap with this set is reported, not used.
Prediction: ~/.golden-chain/r13-item17-truthset-v2-predictions-locked.txt (locked before this file existed).
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

STRATA = {"slanted": 4, "upright": 4, "edge": 2}
SALT = "truthset-v2/"
PREDICTION = "~/.golden-chain/r13-item17-truthset-v2-predictions-locked.txt"


def stratum(row):
    if row["abstain"] == "edge":
        return "edge"
    if row["abstain"] is not None:
        return None
    if row["slanted"] is None:
        raise Fail(f"{row['key']}: measured but no slanted call (unimodal run?)")
    return "slanted" if row["slanted"] else "upright"


def order_key(key):
    return hashlib.sha256((SALT + key).encode("utf-8")).hexdigest()


def draw(slant_rows, bboxes):
    """Pure. slant_rows: gy_word_slant rows; bboxes: key -> bbox. Rows sorted by page, stratum, order key."""
    pools = {}
    for r in slant_rows:
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


def digest(rows):
    blob = json.dumps(rows, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def main(slant_dir, ocr_dir, out):
    git_start = git_state(REPO)
    slant_path, ocr_path = Path(slant_dir) / "slant.json", Path(ocr_dir) / "ocr.json"
    old_path = Path(ocr_dir) / "candidates.json"
    for p in (slant_path, ocr_path, old_path):
        if not p.is_file():
            raise Fail(f"missing: {p}")
    sl = json.loads(slant_path.read_text(encoding="utf-8"))
    ocr = json.loads(ocr_path.read_text(encoding="utf-8"))
    if sl["input"]["ocr_json_sha256"] != hashlib.sha256(ocr_path.read_bytes()).hexdigest():
        raise Fail("the slant run was not made on this ocr.json")
    rows = draw(sl["rows"], {w["key"]: w["bbox"] for w in ocr["words"]})
    old = {r["key"] for r in json.loads(old_path.read_text(encoding="utf-8"))["rows"]}
    summary = {"n": len(rows), "by_stratum": {s: sum(r["stratum"] == s for r in rows) for s in STRATA},
               "pages_without": {s: sorted({r["page"] for r in sl["rows"]} - {r["page"] for r in rows
                                                                              if r["stratum"] == s})
                                 for s in STRATA},
               "p912_left": sum(r["page"] == 912 and r["region"] == "left" for r in rows),
               "overlap_run1_candidates": len(old & {r["key"] for r in rows}), "digest": digest(rows)}
    git_end = git_state(REPO)
    header = {"run": "truthset-v2", "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "input": {"slant_json_sha256": hashlib.sha256(slant_path.read_bytes()).hexdigest(),
                        "ocr_json_sha256": sl["input"]["ocr_json_sha256"]},
              "params": {"strata": STRATA, "salt": SALT}, "prediction": PREDICTION,
              "golden_chain_git_start": git_start, "golden_chain_git_end": git_end,
              "clean_run": clean_run(git_start, git_end)}
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "candidates.json").write_text(json.dumps({"summary": summary, "rows": rows}, indent=1, sort_keys=True,
                                                    ensure_ascii=False), encoding="utf-8")
    (out / "run_header.json").write_text(json.dumps(header, indent=1, sort_keys=True), encoding="utf-8")
    (out / "README.txt").write_text("LOCAL ONLY. Truth-set v2 candidates (keys and boxes of the book's words). Never "
                                    "commit. Every signed_italic is null until Chris signs from pixels.\n",
                                    encoding="utf-8")
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(usage=__doc__)
    ap.add_argument("slant_dir")
    ap.add_argument("ocr_dir")
    ap.add_argument("out")
    a = ap.parse_args()
    try:
        sys.exit(main(a.slant_dir, a.ocr_dir, a.out))
    except Fail as ex:
        print(f"FAIL: {ex}", file=sys.stderr)
        sys.exit(1)
