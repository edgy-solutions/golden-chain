import sys
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("pypdfium2")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import column_rule as C  # noqa: E402


def test_slab_rows():
    assert C.slab_rows(None) == 400
    assert C.slab_rows(C.SCALE_NATIVE) == 400
    assert C.slab_rows(7.2) == 244


def page(lw, rule_w, rw, h=3000, w=1000):
    """Text ink 0.4 of rows in two blocks, a full-height rule between: white lw, rule, white rw."""
    ink = np.zeros((h, w), dtype=bool)
    text = ((np.arange(h) % 10 < 4) & (np.arange(h) >= 60) & (np.arange(h) < h - 60))[:, None]
    x = 400 + lw
    ink[:, 100:400] = text
    ink[60:h - 60, x:x + rule_w] = True
    ink[:, x + rule_w + rw:900] = text
    return ink, x


@pytest.mark.parametrize("r", [400, 244])
def test_measure_rule_and_gutter_at_slab_height(r):
    ink, x = page(60, 4, 80)
    m = C.measure(ink, r=r)
    assert m["rule_present"] and m["coverage"] == 1.0
    assert set(m["rule_w_px"]) == {4}
    assert set(m["gutter_px"]) == {60 + 4 + 80}
    assert m["slabs"][1]["rule_x"] == x and m["slabs"][1]["y"] == r


def test_measure_default_is_r():
    ink, _ = page(60, 4, 80)
    assert C.measure(ink)["slabs"][1]["y"] == C.R


def test_grey_checked_guards():
    g = np.full((300, 300), 255, dtype=np.uint8)
    g[100:200, 100:200] = 0
    assert C.grey_checked(g[:, :, None], 1).shape == (300, 300)
    with pytest.raises(C.Fail, match="2-D uint8"):
        C.grey_checked(np.stack([g] * 3, -1), 1)
    with pytest.raises(C.Fail, match="2-D uint8"):
        C.grey_checked(g.astype(np.float32), 1)
    with pytest.raises(C.Fail, match="polarity"):
        C.grey_checked(255 - g, 1)


def test_parse_scale_anywhere():
    assert C.parse(["a.pdf", "1", "2", "o", "--scale", "7.2"]) == ("a.pdf", 1, 2, "o", 7.2)
    assert C.parse(["--scale", "7.2", "a.pdf", "1", "2", "o"]) == ("a.pdf", 1, 2, "o", 7.2)
    assert C.parse(["a.pdf", "1", "2", "o"])[-1] is None


def _git(repo, *args):
    import subprocess
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=repo, check=True,
                   capture_output=True)


def test_git_state_clean_then_dirty(tmp_path):
    _git(tmp_path, "init")
    (tmp_path / "a.txt").write_text("a")
    _git(tmp_path, "add", "a.txt")
    _git(tmp_path, "commit", "-m", "x")
    s = C.git_state(tmp_path)
    assert s["dirty"] is False and s["porcelain"] == 0 and len(s["commit"]) == 40
    (tmp_path / "b.txt").write_text("b")
    s2 = C.git_state(tmp_path)
    assert s2["dirty"] is True and s2["porcelain"] == 1 and s2["commit"] == s["commit"]


def test_clean_run_truth_table():
    c1 = {"commit": "a", "dirty": False, "porcelain": 0}
    c2 = {"commit": "b", "dirty": False, "porcelain": 0}
    d1 = {"commit": "a", "dirty": True, "porcelain": 2}
    assert C.clean_run(c1, dict(c1)) is True
    assert C.clean_run(d1, c1) is False
    assert C.clean_run(c1, d1) is False
    assert C.clean_run(c1, c2) is False


def test_git_state_non_repo_fails_loud(tmp_path):
    with pytest.raises(C.Fail):
        C.git_state(tmp_path)


def test_repo_is_golden_chain_root():
    assert (C.REPO / "tools" / "column_rule.py").exists()
