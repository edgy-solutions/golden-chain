import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import footnote_zone as fz  # noqa: E402
from column_rule import Fail  # noqa: E402

CLEAN = {"commit": "abc", "dirty": False, "porcelain": 0}


def W(page, region, line, y0, h, x0=0, block=1, par=1, key=None):
    return {"key": key or f"{page}/{region}/{block}.{par}.{line}.{x0}", "page": page, "region": region,
            "block": block, "par": par, "line": line, "word": x0, "bbox": [x0, y0, x0 + 10, y0 + h]}


def L(i, top, h):
    return {"key": f"k{i}", "top": top, "bottom": top + h, "type_h": h, "n_words": 1}


def col(hs, step=30):
    return [L(i, i * step, h) for i, h in enumerate(hs)]


def test_lines_grouping_and_median():
    ws = [W(1, "left", 2, 100, 10, 0), W(1, "left", 2, 98, 20, 20), W(1, "left", 2, 101, 30, 40),
          W(1, "left", 1, 10, 12, 0), W(1, "head", 1, 0, 5), W(1, "right", 1, 10, 8)]
    d = fz.lines(ws)
    assert set(d) == {(1, "left"), (1, "right")}
    a, b = d[(1, "left")]
    assert a["key"] == "1/left/1.1.1" and b["key"] == "1/left/1.1.2"
    assert (b["top"], b["bottom"], b["type_h"], b["n_words"]) == (98, 131, 20, 3)


def test_body_h():
    d = {(1, "left"): col([10, 20, 30]), (1, "right"): col([40, 20])}
    assert fz.body_h(d) == 20
    with pytest.raises(Fail):
        fz.body_h({})


def test_zone_none_when_no_small():
    assert fz.zone(col([20] * 5), 20) is None


def test_zone_all_small():
    z = fz.zone(col([10] * 4), 20)
    assert (z["first_index"], z["last_index"], z["n_lines"], z["gap"]) == (0, 3, 4, None)
    assert z["ratio_to_body"] == 0.5


def test_zone_isolated_nonsmall_kept():
    z = fz.zone(col([20, 20, 10, 20, 10, 10]), 20)
    assert z["first_index"] == 2 and z["last_index"] == 5 and z["n_lines"] == 4
    z = fz.zone(col([10, 10, 20, 10, 10]), 20)
    assert z["first_index"] == 0 and z["n_lines"] == 5


def test_zone_two_nonsmall_stop():
    z = fz.zone(col([10, 10, 20, 20, 10, 10]), 20)
    assert z["first_index"] == 4 and z["n_lines"] == 2


def test_zone_nonsmall_top_trimmed():
    z = fz.zone(col([20, 10, 10, 10]), 20)
    assert z["first_index"] == 1 and z["n_lines"] == 3
    z = fz.zone(col([10, 10, 20, 10, 10]), 20)
    assert z["first_index"] == 0


def test_zone_fewer_than_two():
    assert fz.zone(col([20, 20, 20, 10]), 20) is None
    assert fz.zone(col([10]), 20) is None
    assert fz.zone(col([20, 10, 20, 20]), 20) is None


def test_zone_gap_and_median_gap():
    c = [L(0, 0, 20), L(1, 30, 20), L(2, 100, 10), L(3, 115, 10)]
    z = fz.zone(c, 20)
    assert z["boundary_y"] == 100 and z["bottom"] == 125
    assert z["gap"] == 50 and z["col_median_gap"] == 10  # gaps 10, 50, 5


def _t1_setup():
    ws = [W(914, "left", i, i * 30, h, key=f"w{i}") for i, h in enumerate([20, 20, 10, 10])]
    cl = fz.lines(ws)[(914, "left")]
    return ws, cl, fz.zone(cl, 20)


def mv(a, b):
    return [{"page": 914, "first_key": a, "last_key": b}]


def test_t1_offset_zero():
    ws, cl, z = _t1_setup()
    r = fz.t1(cl, z, ws, mv("w3", "w3"))  # moved word on line 3, expected first line 2, zone first 2
    assert (r["word_line_index"], r["expected_first_index"], r["offset"], r["agree"]) == (3, 2, 0, True)
    assert r["boundary_y"] == 90 and r["zone_first_key"] == "914/left/1.1.2"


def test_t1_offset_nonzero():
    ws, cl, z = _t1_setup()
    r = fz.t1(cl, z, ws, mv("w2", "w3"))  # first moved word on line 2, expected 1, zone first 2
    assert (r["boundary_y"], r["offset"], r["agree"]) == (60, 1, False)


def test_t1_no_zone():
    ws, cl, _ = _t1_setup()
    r = fz.t1(cl, None, ws, mv("w3", "w3"))
    assert (r["offset"], r["agree"]) == (None, False)


def test_t2_conversion_and_agree():
    top, bot = 3760 * 850 / 72 / 6.947, 3995 * 850 / 72 / 6.947
    assert round(top) == 6390 and round(bot) == 6789
    z = {(913, "left"): {"boundary_y": top + 28, "bottom": bot},
         (913, "right"): {"boundary_y": top - 500, "bottom": bot + 100}}
    r = fz.t2(z)
    assert r["agree"] and r["columns"]["left"]["agree"]
    z[(913, "right")] = {"boundary_y": top + 28.1, "bottom": bot}
    r = fz.t2(z)
    assert not r["agree"] and not r["columns"]["right"]["agree"] and r["columns"]["left"]["agree"]
    z[(913, "right")] = {"boundary_y": top, "bottom": bot - 1}
    assert not fz.t2(z)["columns"]["right"]["agree"]
    assert not fz.t2({(913, "left"): None, (913, "right"): None})["agree"]


def test_main_without_text_fields(tmp_path, monkeypatch):
    monkeypatch.setattr(fz, "git_state", lambda repo: CLEAN)
    words = []
    for p in (913, 914):
        for r in ("left", "right"):
            for i in range(10):
                h = 20 if i < 6 else 12
                y0 = 6000 + i * 100 if p == 913 else 100 + i * 30
                words.append(W(p, r, i, y0, h, key=f"{p}/{r}/{i}"))
    assert all("text" not in w for w in words)
    ocr = {"header": {"pages_printed": [913, 914]}, "words": words}
    o, a, out = tmp_path / "o", tmp_path / "a", tmp_path / "out"
    o.mkdir()
    a.mkdir()
    (o / "ocr.json").write_text(json.dumps(ocr))
    moved = [{"page": 914, "first_key": "914/left/6", "last_key": "914/left/9"}]
    (a / "align.json").write_text(json.dumps({"report": {"moved_blocks": moved}}))
    assert fz.main(str(o), str(a), str(out)) == 0
    res = json.loads((out / "zones.json").read_text(encoding="utf-8"))
    assert sorted(p.name for p in out.iterdir()) == ["README.txt", "zones.json"]
    assert res["scores"]["N3_columns_with_zone"] == 4
    assert res["t1"]["offset"] == 1 and res["t1"]["agree"] is False  # moved starts line 6, zone starts line 6
    assert res["header"]["clean_run"] and res["header"]["ocr_sha256"] == res["header"]["ocr_sha256_end"]
    assert res["scores"]["N5_moved_columns"] == 1 and res["scores"]["N5_with_zone"] == 1


def test_main_fails_on_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(fz, "git_state", lambda repo: CLEAN)
    with pytest.raises(Fail):
        fz.main(str(tmp_path), str(tmp_path), str(tmp_path / "x"))
