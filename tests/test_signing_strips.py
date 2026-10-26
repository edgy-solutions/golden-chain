import sys
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import signing_strips as ss  # noqa: E402

H, W, HALF_W, PAD = 400, 200, 10, 5


def rows(ink):
    return ss.ruled_rows(ink, 0.0, 100.0, HALF_W, PAD)


def test_rule_ends_at_known_row():
    ink = np.zeros((H, W), dtype=bool)
    ink[:300, 95:115] = True  # 20 ink px per row = 2*half_w
    r = rows(ink)
    assert r[:300].all() and not r[300:].any()
    assert ss.last_run_end(r) == 299 + (ss.RUN - ss.NEED)  # 45 of 50 rows: L is 5 rows past the end


def test_rule_starts_at_known_row():
    ink = np.zeros((H, W), dtype=bool)
    ink[150:, 95:115] = True
    r = rows(ink)
    assert not r[:150].any()
    assert ss.first_run_start(r, y_min=0) == 150 - (ss.RUN - ss.NEED)  # F is 5 rows before the start
    assert ss.first_run_start(r, y_min=200) == 200


def test_faint_rule_not_ruled():
    ink = np.zeros((H, W), dtype=bool)
    ink[:, 100:119] = True  # 19 ink px < 2*half_w
    r = rows(ink)
    assert not r.any()
    assert ss.first_run_start(r, y_min=0) is None
    assert ss.last_run_end(r) is None
