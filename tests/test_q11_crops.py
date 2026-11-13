import importlib.util
import sys
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("PIL")

TOOLS = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS))
# The console spec builder is also named q11_crops, so load the tool under its own name.
_spec = importlib.util.spec_from_file_location("q11_crops_tool", TOOLS / "q11_crops.py")
q = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(q)
from column_rule import Fail  # noqa: E402

ENTRY = {"y": 400, "rule_x": 140, "left_white": 20, "rule_w": 5, "right_white": 10, "gutter": 35}


def grey():
    return np.random.default_rng(0).integers(0, 256, (1000, 300), dtype=np.uint8)


def test_crop_and_overlay():
    g = grey()
    crop, rows, ov = q.crop_and_overlay(g, ENTRY, 100)
    assert crop.shape == (300, 300) and crop.dtype == g.dtype
    assert np.array_equal(crop, g[300:600]) and rows == [300, 600]
    assert len(ov) == 4
    blue = [o for o in ov if o["colour"] == "#00b0ff"]
    assert [(o["x"], o["w"]) for o in blue] == [(120, 35), (120, 35)]
    assert sorted(o["y"] for o in ov if o["colour"] == "#ff00ff") == [98, 200]


@pytest.mark.parametrize("y", [50, 900])
def test_clipping_fails(y):
    with pytest.raises(Fail):
        q.crop_and_overlay(grey(), dict(ENTRY, y=y), 100)


def test_check_remeasure():
    assert q.check_remeasure(dict(ENTRY, rule=1), dict(ENTRY, rule=1, extra=3))
    with pytest.raises(Fail):
        q.check_remeasure(dict(ENTRY, rule=1), dict(ENTRY, rule=1, gutter=36))
    with pytest.raises(Fail):
        q.check_remeasure(ENTRY, None)
