"""tools/pool_rates.py on synthetic data only."""

import hashlib
import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("numpy")
pytest.importorskip("PIL")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import pool_rates as R  # noqa: E402
from column_rule import Fail  # noqa: E402


def row(key, page, abstain=None, slanted=None):
    return {"key": key, "page": page, "region": "left", "abstain": abstain, "slanted": slanted, "slant": 1.0}


ROWS = [row("a", 1, None, True), row("b", 1, None, True), row("c", 1, None, False),
        row("d", 2, "edge"), row("e", 2, "other"), row("f", 2, None, True)]
SIDE = {"a": "top", "b": None, "c": "both", "d": "bottom", "f": "top"}


def check(r):
    return SIDE[r["key"]]


def walk(o):
    if isinstance(o, dict):
        for k, v in o.items():
            yield k
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)


def test_rates_counts():
    s = R.rates(ROWS, check)
    assert s["rows_total"] == 6 and s["rows_abstained_other"] == 1
    sl = s["by_stratum"]["slanted"]
    assert (sl["pool"], sl["fail"], sl["share"]) == (3, 2, 0.6667)
    assert sl["by_side"] == {"top": 2, "bottom": 0, "both": 0}
    up = s["by_stratum"]["upright"]
    assert (up["pool"], up["fail"], up["share"]) == (1, 1, 1.0) and up["by_side"]["both"] == 1
    assert s["by_stratum"]["edge"]["by_side"]["bottom"] == 1
    assert s["by_page"]["1"]["slanted"] == {"pool": 2, "fail": 1}
    assert s["by_page"]["2"]["edge"] == {"pool": 1, "fail": 1}


def test_zero_pool_share():
    s = R.rates([row("a", 1, None, True)], lambda r: None)
    assert s["by_stratum"]["edge"] == {"pool": 0, "fail": 0, "share": 0.0,
                                       "by_side": {"top": 0, "bottom": 0, "both": 0}}


def test_groups_filter_pages():
    g = dict([R.parse_group("one=1"), R.parse_group("two=2-3,9")])
    assert g == {"one": {1}, "two": {2, 3, 9}}
    s = R.rates(ROWS, check, g)
    assert s["groups"]["one"]["slanted"]["pool"] == 2
    assert s["groups"]["two"]["slanted"]["pool"] == 1 and s["groups"]["two"]["edge"]["fail"] == 1
    assert "groups" not in R.rates(ROWS, check)


def test_no_key_text_bbox_anywhere():
    s = R.rates(ROWS, check, {"g": {1}})
    assert not {"key", "text", "bbox"} & set(walk(s))


def test_bad_group():
    for g in ("x", "=1-2", "x=", "x=3-1", "x=a"):
        with pytest.raises(Fail):
            R.parse_group(g)


def _setup(tmp_path, measure="v4", sha=None):
    ocr = tmp_path / "ocr"
    sl = tmp_path / "slant"
    ocr.mkdir()
    sl.mkdir()
    op = ocr / "ocr.json"
    op.write_text(json.dumps({"words": []}), encoding="utf-8")
    good = hashlib.sha256(op.read_bytes()).hexdigest()
    (sl / "slant.json").write_text(json.dumps({"params": {"measure": measure},
                                               "input": {"ocr_json_sha256": sha or good}, "rows": []}),
                                   encoding="utf-8")
    return sl, ocr


def test_main_missing(tmp_path):
    with pytest.raises(Fail, match="missing"):
        R.main(tmp_path / "s", tmp_path / "o", tmp_path / "out")


def test_main_refuses_wrong_measure(tmp_path):
    sl, ocr = _setup(tmp_path, measure="v3")
    with pytest.raises(Fail, match="v4"):
        R.main(sl, ocr, tmp_path / "out")


def test_main_refuses_sha_mismatch(tmp_path):
    sl, ocr = _setup(tmp_path, sha="0" * 64)
    with pytest.raises(Fail, match="ocr.json"):
        R.main(sl, ocr, tmp_path / "out")
