"""The A2 single-rule fixture (tools/gy_single_rule_fixture.py) against goat-yard's
locate_column_rule and analyze_page_s1 at substrate-v1, plus a self-check of its
measured shape. Predictions: ~/.golden-chain/a2-single-rule-fixture-predictions-locked.txt (F4, F7 missed;
see docs/sources/goat-yard.md) and a2-single-rule-fixture-v2-predictions-locked.txt."""

import sys
from pathlib import Path

import pytest

pytest.importorskip("numpy")
pytest.importorskip("pypdfium2")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import gy_locate_column_rule as G  # noqa: E402
import gy_single_rule_fixture as F  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
WORKTREE = REPO.parent / "goatyard-substrate-v1"
needs_gy = pytest.mark.skipif(not WORKTREE.exists(), reason="no goat-yard worktree at substrate-v1")
KEYS = ("status", "reason", "n_strips", "n_rule", "half_w", "c0", "slope", "max_resid")


def vr(monkeypatch):
    monkeypatch.setenv("GOLDEN_CHAIN_GOATYARD", str(WORKTREE))
    _, _, VR = G.goatyard()
    return VR


@needs_gy
@pytest.mark.parametrize("rule_w, half_w", [(3, 1.5), (5, 2.5), (7, 3.5)])
def test_single_rule_located(monkeypatch, rule_w, half_w):
    VR = vr(monkeypatch)
    ink, geom, _ = F.single_rule_page(rule_w=rule_w)
    sp = VR.locate_column_rule(ink, geom)
    print("LOCATE", rule_w, {k: sp.get(k) for k in KEYS})
    assert sp["status"] == "ok"
    assert sp["n_strips"] == 12 and sp["n_rule"] == 12
    assert sp["half_w"] == half_w
    assert abs(sp["c0"] - 1500.8) <= 1.0
    assert abs(sp["slope"] + 0.0012) <= 1e-4
    assert sp["max_resid"] <= 1.0


@needs_gy
def test_single_rule_bands_split(monkeypatch):
    VR = vr(monkeypatch)
    rule_w = 5
    ink, geom, texts = F.single_rule_page(rule_w=rule_w)
    s1 = VR.analyze_page_s1(ink, geom)
    assert s1["col_split"]["status"] == "ok"
    assert s1["full"] == []
    assert s1["left"] and s1["right"]
    lines = sorted({y for (_, y) in texts})
    for b in s1["left"]:
        mid = (b["y0"] + b["y1"]) // 2
        hit = [y for y in lines if y <= mid < y + F.LINE_H]
        assert len(hit) == 1
        # right_ink_x is EXCLUSIVE in goat-yard (cx0 + right_local + 1), so it
        # equals l_end, the exclusive end of the drawn left type.
        assert b["right_ink_x"] == texts[("left", hit[0])][1]
    for b in s1["right"]:
        mid = (b["y0"] + b["y1"]) // 2
        edge = int(round(F.centre(1500.8, -0.0012, mid) - rule_w / 2)) + rule_w
        assert b["left_ink_x"] >= edge


@needs_gy
@pytest.mark.parametrize("missing, status, n_rule",
                         [((1, 3, 5, 7, 9), "ok", 7), ((0, 1, 2, 3, 4, 5, 6), "abstained", 5)])
def test_broken_rule_strip_share(monkeypatch, missing, status, n_rule):
    VR = vr(monkeypatch)
    ink, geom, _ = F.single_rule_page(missing_strips=missing)
    sp = VR.locate_column_rule(ink, geom)
    print("LOCATE", missing, {k: sp.get(k) for k in KEYS})
    assert sp["status"] == status
    assert sp["n_rule"] == n_rule
    if status == "abstained":
        assert sp["reason"] == "no_rule"


@needs_gy
@pytest.mark.parametrize("duty, status, n_rule", [(0.4, "abstained", 0), (0.7, "ok", 12)])
def test_dashed_rule_column_fraction(monkeypatch, duty, status, n_rule):
    VR = vr(monkeypatch)
    ink, geom, _ = F.single_rule_page(duty=duty)
    sp = VR.locate_column_rule(ink, geom)
    print("LOCATE", duty, {k: sp.get(k) for k in KEYS})
    assert sp["status"] == status
    assert sp["n_rule"] == n_rule
    if status == "abstained":
        assert sp["reason"] == "no_rule"
    else:
        assert sp["half_w"] == 2.5


def test_fixture_matches_measured_gill():
    xdiv, rule_w = 1471, 5
    ink, _, _ = F.single_rule_page(xdiv=xdiv, rule_w=rule_w)
    allfr = []
    for k in range(12):
        y0, y1 = 700 + 300 * k, min(1000 + 300 * k, F.Y_END)
        mid = (y0 + y1) // 2
        cen = F.centre(1500.8, -0.0012, mid)
        a = int(round(cen - rule_w / 2))
        lo, hi = xdiv - 300, xdiv + 300
        fr = F.column_fractions(ink, y0, y1, lo, hi)
        rule = [fr[c - lo] for c in range(lo, hi) if a <= c < a + rule_w]
        typ = [fr[c - lo] for c in range(lo, hi) if abs(c + 0.5 - cen) > 12]
        # The sloped rule steps 1 px inside some strips (2, 5, 8), so an edge column can be
        # fractional; the measured Gill value is the peak (lock v2, R5).
        assert len(rule) == rule_w and max(rule) == 1.0 and sum(f == 1.0 for f in rule) >= rule_w - 1
        assert max(typ) < 0.59
        allfr += typ
    mean = sum(allfr) / len(allfr)
    print("SELFCHECK type max", max(allfr), "mean", mean)
    assert 0.15 <= mean <= 0.25
