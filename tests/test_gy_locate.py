"""The pin guard of tools/gy_locate_column_rule.py: goat-yard is used only clean, at substrate-v0."""

import importlib
import sys
from pathlib import Path

import pytest

pytest.importorskip("numpy")
pytest.importorskip("pypdfium2")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import gy_locate_column_rule as G  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
WORKTREE = REPO.parent / "goatyard-substrate-v0"


def test_wrong_commit_fails_loud(monkeypatch):
    monkeypatch.setenv("GOLDEN_CHAIN_GOATYARD", str(REPO))
    with pytest.raises(G.Fail, match="not substrate-v0"):
        G.goatyard()


@pytest.mark.skipif(not WORKTREE.exists(), reason="no goat-yard worktree at substrate-v0")
def test_pinned_worktree_loads_unchanged(monkeypatch):
    monkeypatch.setenv("GOLDEN_CHAIN_GOATYARD", str(WORKTREE))
    _, _, VR = G.goatyard()
    assert VR.RULE_COL_FRAC == 0.59 and VR.RULE_MAX_RESID_PX == 15


@pytest.mark.skipif(not WORKTREE.exists(), reason="no goat-yard worktree at substrate-v0")
@pytest.mark.parametrize("name", sorted(G.SUBSTRATE_MODULES))
def test_every_substrate_module_imports_without_skipped_deps(monkeypatch, name):
    """Installed --no-deps: a module that needs dagster etc. fails here, not in a run."""
    monkeypatch.setenv("GOLDEN_CHAIN_GOATYARD", str(WORKTREE))
    root, _, _ = G.goatyard()
    module = importlib.import_module(name)
    assert Path(module.__file__).resolve().is_relative_to(root)


@pytest.mark.skipif(not WORKTREE.exists(), reason="no goat-yard worktree at substrate-v0")
def test_unlisted_substrate_module_fails_loud(monkeypatch):
    monkeypatch.setenv("GOLDEN_CHAIN_GOATYARD", str(WORKTREE))
    monkeypatch.setattr(G, "SUBSTRATE_MODULES", G.SUBSTRATE_MODULES - {"box_sanity"})
    with pytest.raises(G.Fail, match="box_sanity"):
        G.goatyard()


def bands(*ys, h=50):
    return [{"y0": y, "y1": y + h} for y in ys]


S1 = {"line_h": {"left": {"basis": "own", "page_line_h": 54}, "right": {"basis": "page", "page_line_h": 54}},
      "left": bands(300, 100, 200), "right": bands(110, 230, h=60)}


def test_line_height_exact_medians():
    r = G.line_height(S1)
    assert r == {"page_line_h": 54, "basis": {"left": "own", "right": "page"},
                 "band_h_med": 50, "pitch_med": 100, "n_bands": 5}  # pitches 100,100,120


def test_line_height_right_fallback_and_empty():
    s1 = {"line_h": {"right": {"basis": "own", "page_line_h": 7}}, "left": [], "right": []}
    assert G.line_height(s1) == {"page_line_h": 7, "basis": {"right": "own"},
                                 "band_h_med": None, "pitch_med": None, "n_bands": 0}


def test_line_height_summary():
    per = [{"page_line_h": 50, "pitch_med": 100}, {"page_line_h": 56, "pitch_med": 110},
           {"page_line_h": 60, "pitch_med": None}]
    assert G.line_height_summary(per) == {"page_line_h_median": 56, "page_line_h_range": [50, 60],
                                          "pitch_median": 105, "ratio_to_55": 1.018,
                                          "goat_yard_band": [49, 61]}


def test_gy_uses_shared_git_state():
    import column_rule as C
    assert G.git_state is C.git_state and G.clean_run is C.clean_run and G.REPO == C.REPO
