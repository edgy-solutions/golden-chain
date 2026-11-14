"""tools/gy_word_slant.py on synthetic data only."""

import json
import sys
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")
Image = pytest.importorskip("PIL.Image")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import gy_word_slant as S  # noqa: E402


def word(s, k=5, h=100, w=160):
    img = np.full((h, w), 255, dtype=np.uint8)
    yc = (h - 1) / 2
    for y in range(20, 80):
        shift = int(round(s * (yc - y)))
        for i in range(k):
            x = 20 + i * 20 + shift
            img[y, x:x + 6] = 0
    return img


@pytest.mark.parametrize("s", [0.0, 0.1, 0.2, 0.3])
def test_slant_recovers(s):
    got, why = S.slant(word(s))
    assert why is None and abs(got - s) <= 0.02


def test_slant_small_and_edge():
    crop = np.full((100, 160), 255, dtype=np.uint8)
    crop[10:20, 10:20] = 0
    assert S.slant(crop) == (None, "small")
    assert S.slant(word(0.7)) == (None, "edge")


def test_shear_score_upright():
    ink = word(0.0) < 128
    assert S.shear_score(ink, 0.0) > S.shear_score(ink, 0.2)


def test_ties_smallest_abs(monkeypatch):
    monkeypatch.setattr(S, "shear_score", lambda ink, s: 1.0)
    assert S.slant(word(0.0)) == (0.0, None)
    monkeypatch.setattr(S, "shear_score", lambda ink, s: 5.0 if abs(abs(s) - 0.05) < 1e-9 else 1.0)
    assert S.slant(word(0.0)) == (-0.05, None)


def test_mode_midpoint_bimodal():
    rng = np.random.default_rng(1)
    v = np.concatenate([rng.normal(0, 0.02, 900), rng.normal(0.25, 0.03, 100)])
    T, info = S.mode_midpoint(v)
    assert 0.10 <= T <= 0.15 and 0.2 <= info["hi_centre"] <= 0.3


def test_mode_midpoint_none_cases():
    rng = np.random.default_rng(2)
    assert S.mode_midpoint(rng.normal(0, 0.03, 1000))[0] is None
    close = np.concatenate([rng.normal(0, 0.01, 500), rng.normal(0.06, 0.01, 400)])
    assert S.mode_midpoint(close)[0] is None
    # shallow second peak: valley is not below half of the second peak
    cs = -0.19 + 0.02 * np.arange(35)
    shallow = np.concatenate([np.repeat(cs[10], 100), np.repeat(cs[11:16], 60), np.repeat(cs[16], 99)])
    assert S.mode_midpoint(shallow)[0] is None


def test_eligible():
    r = "left"
    assert S.eligible({"region": r, "text": "the"})
    assert not S.eligible({"region": r, "text": "of"})
    assert not S.eligible({"region": r, "text": "1.2"})
    assert not S.eligible({"region": r, "text": "(a)"})
    assert S.eligible({"region": r, "text": "Acts"})
    assert not S.eligible({"region": "head", "text": "Acts"})


def test_end_to_end(tmp_path, monkeypatch):
    monkeypatch.setattr(S, "git_state", lambda repo: {"commit": "x", "dirty": False, "porcelain": 0})
    run = tmp_path / "run"
    (run / "regions").mkdir(parents=True)
    (run / "pages").mkdir()
    Image.fromarray(np.full((300, 400), 255, np.uint8), "L").save(run / "pages" / "p1.png")
    Image.fromarray(word(0.0), "L").save(run / "regions" / "p1-left.png")
    Image.fromarray(word(0.2), "L").save(run / "regions" / "p1-right.png")
    # right region is 160 wide on a 400 wide page: x offset 240; ytop 10
    words = [{"key": "1/left/a", "page": 1, "region": "left", "bbox": [0, 10, 160, 110],
              "text": "aaaa", "italic": True},
             {"key": "1/right/b", "page": 1, "region": "right", "bbox": [240, 10, 400, 110],
              "text": "bbbb", "italic": False},
             {"key": "1/left/c", "page": 1, "region": "left", "bbox": [0, 10, 20, 30],
              "text": "cccc", "italic": False}]
    (run / "ocr.json").write_text(json.dumps({"header": {"splits": {"1": {"ytop": 10}}, "script_sha256": "z"},
                                              "summary": {}, "words": words}), encoding="utf-8")
    a, b = tmp_path / "a", tmp_path / "b"
    assert S.main(run, a) == 0 and S.main(run, b) == 0
    assert (a / "slant.json").read_bytes() == (b / "slant.json").read_bytes()
    assert (a / "README.txt").is_file()
    d = json.loads((a / "slant.json").read_text(encoding="utf-8"))
    assert len(d["rows"]) == 3 and all("text" not in r for r in d["rows"])
    assert d["summary"]["legacy"]["flagged"] == 1
