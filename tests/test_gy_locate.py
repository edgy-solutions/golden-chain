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
