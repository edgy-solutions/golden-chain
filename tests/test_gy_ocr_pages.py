"""tools/gy_ocr_pages.py on synthetic data only: range parsing, split-failure handling, word records."""

import sys
from pathlib import Path

import pytest

pytest.importorskip("numpy")
pytest.importorskip("PIL")
pytest.importorskip("pypdfium2")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import gy_ocr_pages as P  # noqa: E402
from column_rule import Fail  # noqa: E402


def test_parse_ranges_valid_and_merged():
    assert P.parse_ranges("201-203") == [201, 202, 203]
    assert P.parse_ranges("5") == [5]
    assert P.parse_ranges("10-12,11-14,3,3") == [3, 10, 11, 12, 13, 14]
    assert P.parse_ranges("895") == [895]
    assert P.parse_ranges(" 1 - 2".replace(" ", "")) == [1, 2]


@pytest.mark.parametrize("s", ["896", "900", "890-896", "897-912", "1-1000"])
def test_parse_ranges_refuses_above_895(s):
    with pytest.raises(Fail, match="895"):
        P.parse_ranges(s)


@pytest.mark.parametrize("s", ["", "  ", "a", "1-", "-3", "1--3", "1,,2", "1-2-3", "0", "0-5", "9-3"])
def test_parse_ranges_malformed(s):
    with pytest.raises(Fail):
        P.parse_ranges(s)


def _region(name):
    return {"name": name, "x_off": 100, "y_off": 10, "image": None}


def _split(status="ok", reason=None):
    if status != "ok":
        return {"status": status, "reason": reason}
    return {"status": "ok", "rec": {"status": "ok", "ytop": 1, "ybot": 2},
            "regions": [_region("left"), _region("right")]}


def _ocr(p, r):
    lstm = [{"block": 1, "par": 2, "line": 3, "word": 4, "conf": 90.0, "text": f"w{p}",
             "bbox": [0, 0, 10, 10]}]
    legacy = [{"text": f"w{p}", "bbox": [0, 0, 10, 10], "italic": True}]
    return lstm, legacy


def test_failed_pages_skipped_and_recorded():
    fakes = {1: _split(), 2: _split("rule_not_found", "no rule"), 3: None, 4: _split()}
    splits, failed, words = P.run_pages([1, 2, 3, 4], fakes.get, _ocr, workers=2)
    assert sorted(splits) == ["1", "4"]
    assert failed == {"2": {"status": "rule_not_found", "reason": "no rule"},
                      "3": {"status": "no_record", "reason": None}}
    assert {w["page"] for w in words} == {1, 4}
    assert len(words) == 4
    s = P.summarize([1, 2, 3, 4], splits, failed, words)
    assert s["pages"] == 4 and s["split_ok"] == 2 and s["split_failed"] == 2
    assert s["words_total"] == 4 and s["words_per_page"] == 2.0 and s["column_words"] == 4
    assert s["legacy_matched"] == 4 and s["match_frac"] == 1.0 and s["italic_rate"] == 1.0


def test_all_failed_raises():
    with pytest.raises(Fail):
        P.run_pages([1, 2], {1: None, 2: _split("x")}.get, _ocr)


def test_words_have_ccel_none_and_baptism_fields(tmp_path):
    _s, _f, words = P.run_pages([7], {7: _split()}.get, _ocr)
    assert all(w["ccel"] is None for w in words)
    w = words[0]
    assert w["key"] == "7/left/1.2.3.4" and w["bbox"] == [100, 10, 110, 20]
    assert set(w) == {"key", "page", "region", "block", "par", "line", "word", "text", "conf", "bbox",
                      "italic", "legacy_iou", "legacy_text", "ccel"}
    assert not (tmp_path / "candidates.json").exists()


def test_no_candidates_code_path():
    src = Path(P.__file__).read_text(encoding="utf-8")
    assert "candidates(" not in src and "candidates.json" not in src.replace("no candidates", "")
