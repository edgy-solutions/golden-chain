"""measure_band (tools/gy_narrow_glyph.py) on synthetic ink: the line-final run, its width, window and shift."""

import sys
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("pypdfium2")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import gy_narrow_glyph as N  # noqa: E402


def page(*spans, h=40, w=400):
    ink = np.zeros((h, w), dtype=bool)
    for a, b in spans:
        ink[10:30, a:b] = True
    return ink


def test_runs():
    assert N.runs(np.array([0, 1, 1, 0, 1, 0, 0, 1], dtype=bool)) == [(1, 3), (4, 5), (7, 8)]


def test_left_thin_final_erased():
    # a word ending at 290, a 6 px glyph at 300-306; rule centre 330 -> both in the window
    ink = page((100, 290), (300, 306))
    band = {"x0": 50, "x1": 320, "y0": 0, "y1": 40, "right_ink_x": 290, "left_ink_x": 100}
    m = N.measure_band(ink, band, "left", 330)
    assert (m["width"], m["gap"], m["thin"], m["shift"]) == (6, 10, True, 16)


def test_left_wide_final_not_thin():
    ink = page((100, 290), (300, 309))
    band = {"x0": 50, "x1": 320, "y0": 0, "y1": 40, "right_ink_x": 309, "left_ink_x": 100}
    m = N.measure_band(ink, band, "left", 330)
    assert (m["width"], m["thin"], m["shift"]) == (9, False, 0)


def test_left_thin_outside_window():
    ink = page((100, 150), (160, 165))
    band = {"x0": 50, "x1": 320, "y0": 0, "y1": 40, "right_ink_x": 165, "left_ink_x": 100}
    m = N.measure_band(ink, band, "left", 330)
    assert (m["in_window"], m["thin"]) == (False, False)


def test_right_mirror():
    ink = page((340, 345), (360, 390))
    band = {"x0": 335, "x1": 400, "y0": 0, "y1": 40, "right_ink_x": 390, "left_ink_x": 360}
    m = N.measure_band(ink, band, "right", 330)
    assert (m["width"], m["gap"], m["thin"], m["shift"]) == (5, 15, True, 20)


def test_empty_band():
    assert N.measure_band(page(), {"x0": 0, "x1": 50, "y0": 0, "y1": 40, "right_ink_x": 0, "left_ink_x": 0},
                          "left", 30) is None
