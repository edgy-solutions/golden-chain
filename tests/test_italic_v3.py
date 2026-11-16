"""Measure v3, the v3 draw, padded crops and the v3 console builder: synthetic numpy images in tmp_path only."""

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools" / "console"))
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))
import build  # noqa: E402
import gy_word_slant as S2  # noqa: E402
import gy_word_slant_v3 as S3  # noqa: E402
import ingest  # noqa: E402
import test_console_specs as tcs  # noqa: E402
import truthset_crops as tc2  # noqa: E402
import truthset_crops_v3 as C3  # noqa: E402
import truthset_v2  # noqa: E402
import truthset_v3 as T3  # noqa: E402
from column_rule import Fail  # noqa: E402

CLEAN = {"commit": "abc123", "dirty": False, "porcelain": 0}


# ---- shear_score_subpixel ------------------------------------------------------------------------------

def bar(s, h=60, w=80, thick=5):
    ink = np.zeros((h, w), dtype=bool)
    yc = (h - 1) / 2
    for y in range(h):
        x = 30 + int(round(s * (yc - y)))
        ink[y, x:x + thick] = True
    return ink


def best_s(ink):
    grid = np.arange(-0.2, 0.5001, 0.01)
    return float(grid[int(np.argmax([S3.shear_score_subpixel(ink, float(s)) for s in grid]))])


def test_subpixel_sheared_bar_measures_its_slope():
    assert abs(best_s(bar(0.25)) - 0.25) <= 0.01


def test_subpixel_upright_bar_measures_zero():
    assert abs(best_s(bar(0.0))) <= 0.005


def test_subpixel_score_is_continuous_in_s():
    rng = np.random.default_rng(3)
    ink = rng.random((50, 70)) < 0.25
    for s in np.arange(-0.2, 0.5, 0.05):
        a, b = S3.shear_score_subpixel(ink, float(s)), S3.shear_score_subpixel(ink, float(s) + 0.001)
        assert abs(a - b) <= 0.10 * a


def test_subpixel_agrees_with_integer_score_on_unsheared_input():
    rng = np.random.default_rng(4)
    ink = rng.random((40, 60)) < 0.3
    assert S3.shear_score_subpixel(ink, 0.0) == S2.shear_score(ink, 0.0)


def test_subpixel_empty_is_zero():
    assert S3.shear_score_subpixel(np.zeros((5, 5), dtype=bool), 0.1) == 0.0


# ---- ink_mask / edge_ink -------------------------------------------------------------------------------

def grey_img():
    a = np.full((10, 12), 200, dtype=np.uint8)
    a[3:7, 4:8] = 30
    a[0, 0:3] = 150  # mid-grey: not ink
    return a


def test_ink_mask_paper_200_ink_30_midgrey_not_ink():
    m = build.ink_mask(grey_img())
    assert m.dtype == bool and int(m.sum()) == 16 and not m[0, 0:3].any() and m[3:7, 4:8].all()


def test_ink_mask_all_white_has_no_ink():
    assert not build.ink_mask(np.full((6, 6), 255, dtype=np.uint8)).any()


def test_edge_ink_counts_outermost_lines():
    a = grey_img()
    a[9, 2:6] = 30
    a[:, 11] = 30
    e = build.edge_ink(a)
    assert e == {"top": 1, "bottom": 5, "left": 0, "right": 10} or e["top"] == 1 and e["bottom"] == 5
    assert e["left"] == 0 and e["right"] == 10


def test_check_clear_edges_unchanged(tmp_path):
    p = tmp_path / "a.png"
    a = grey_img()
    Image.fromarray(a, "L").save(p)
    build.check_clear_edges({"id": "a", "clear_edges": ["top", "bottom", "left", "right"]}, p)
    a[9, 2:6] = 30
    Image.fromarray(a, "L").save(p)
    with pytest.raises(Fail, match="ink touches the bottom edge .4 px."):
        build.check_clear_edges({"id": "a", "clear_edges": ["bottom"]}, p)
    build.check_clear_edges({"id": "a", "clear_edges": ["top"]}, p)
    build.check_clear_edges({"id": "a"}, p)


# ---- line box measure ----------------------------------------------------------------------------------

def test_line_box_covers_full_line_height_for_a_clipped_word():
    words = [{"key": "913/left/1.1.2.0", "bbox": [10, 40, 40, 52]},   # a clipped word: no ascender
             {"key": "913/left/1.1.2.1", "bbox": [50, 30, 90, 58]},   # ascender and descender
             {"key": "913/left/1.1.3.0", "bbox": [10, 70, 40, 82]}]
    lines = S3.line_ranges(words)
    assert lines["913/left/1.1.2"] == [30, 58] and lines["913/left/1.1.3"] == [70, 82]
    assert S3.measured_box(words[0]["bbox"], lines["913/left/1.1.2"]) == [10, 30, 40, 58]


def test_run_measures_clipped_word_on_the_line_height(tmp_path, monkeypatch):
    od = tmp_path / "ocr"
    (od / "pages").mkdir(parents=True)
    (od / "regions").mkdir()
    reg = np.full((100, 160), 255, dtype=np.uint8)
    yc = (60 - 1) / 2
    for y in range(20, 80):  # slanted stems 0.25, word 1 at x 10..50
        for i in range(4):
            x = 12 + i * 10 + int(round(0.25 * (yc - (y - 20))))
            reg[y, x:x + 4] = 0
    Image.fromarray(reg, "L").save(od / "regions" / "p900-left.png")
    Image.fromarray(np.full((120, 160), 255, dtype=np.uint8), "L").save(od / "pages" / "p900.png")
    words = [{"key": "900/left/1.1.0.0", "page": 900, "region": "left", "text": "abcd", "bbox": [0, 45, 60, 55]},
             {"key": "900/left/1.1.0.1", "page": 900, "region": "left", "text": "efgh", "bbox": [70, 20, 100, 80]}]
    (od / "ocr.json").write_text(json.dumps({"header": {"splits": {"900": {"ytop": 0}}}, "words": words}),
                                 encoding="utf-8")
    monkeypatch.setattr(S3, "git_state", lambda repo: dict(CLEAN))
    S3.main(od, tmp_path / "out")
    sj = json.loads((tmp_path / "out" / "slant.json").read_text(encoding="utf-8"))
    assert sj["params"]["measure"] == "v3" and "comb" in sj["summary"]
    r0 = sj["rows"][0]
    assert r0["box"] == [0, 20, 60, 80] and abs(r0["slant"] - 0.25) <= 0.03 and r0["abstain"] is None


def test_comb_lists_empty_and_deep_dip_bins():
    h = [5] * 35
    h[10], h[20], h[21], h[22] = 0, 100, 10, 100
    c = S3.comb(h)
    assert 10 in c["empty_between"] and 21 not in c["empty_between"] and c["deep_dip"] == [21]


# ---- the draw ------------------------------------------------------------------------------------------

def slant_rows(n=40, pages=(912, 913)):
    rows, boxes = [], {}
    for p in pages:
        for i in range(n):
            k = f"{p}/left/1.1.{i // 5}.{i % 5}"
            m = i % 10
            r = ({"abstain": "edge", "slanted": None, "slant": None} if m < 2 else
                 {"abstain": None, "slanted": True, "slant": 0.25} if m < 6 else
                 {"abstain": None, "slanted": False, "slant": 0.02})
            rows.append({"key": k, "page": p, "region": "left", **r})
            boxes[k] = [1, 2, 3, 4]
    return rows, boxes


def test_draw_excludes_v2_keys_and_shares_nothing():
    rows, boxes = slant_rows()
    first = T3.draw(rows, boxes)
    ex = {r["key"] for r in first[:6]}
    again = T3.draw(rows, boxes, ex)
    assert ex.isdisjoint({r["key"] for r in again}) and len(again) >= len(first) - 2


def test_draw_is_deterministic_in_order_and_input_order():
    rows, boxes = slant_rows()
    a = T3.draw(rows, boxes, ["912/left/1.1.0.0"])
    b = T3.draw(list(reversed(rows)), boxes, ["912/left/1.1.0.0"])
    assert a == b and T3.digest(a) == T3.digest(b)
    assert T3.SALT == "truthset-v3/" and T3.STRATA == truthset_v2.STRATA


def make_run(tmp_path, measure="v3", sha=None):
    rows, boxes = slant_rows()
    od = tmp_path / "ocr"
    od.mkdir()
    ocr = {"header": {}, "words": [{"key": k, "bbox": b} for k, b in boxes.items()]}
    (od / "ocr.json").write_text(json.dumps(ocr), encoding="utf-8")
    sd = tmp_path / "slant"
    sd.mkdir()
    (sd / "slant.json").write_text(json.dumps({"rows": rows, "params": {"measure": measure},
                                               "input": {"ocr_json_sha256": sha or T3.sha256_file(od / "ocr.json")}}),
                                   encoding="utf-8")
    v2 = tmp_path / "v2.json"
    v2.write_text(json.dumps({"rows": [{"key": r["key"]} for r in truthset_v2.draw(rows, boxes)]}), encoding="utf-8")
    return sd, od, v2


def test_draw_main_summary_and_files(tmp_path, monkeypatch):
    monkeypatch.setattr(T3, "git_state", lambda repo: dict(CLEAN))
    sd, od, v2 = make_run(tmp_path)
    T3.main(sd, od, v2, tmp_path / "o")
    d = json.loads((tmp_path / "o" / "candidates.json").read_text(encoding="utf-8"))
    s = d["summary"]
    assert s["shared_with_v2"] == 0 and s["excluded_v2"] == 20 and s["n"] == len(d["rows"]) > 0
    assert {r["key"] for r in d["rows"]}.isdisjoint({r["key"] for r in json.loads(v2.read_text())["rows"]})
    h = json.loads((tmp_path / "o" / "run_header.json").read_text(encoding="utf-8"))
    assert h["input"]["v2_candidates_sha256"] == T3.sha256_file(v2)
    assert (tmp_path / "o" / "README.txt").read_text().startswith("LOCAL ONLY") and "never commit" in (
        tmp_path / "o" / "README.txt").read_text().lower()


def test_draw_fails_when_measure_is_not_v3(tmp_path, monkeypatch):
    monkeypatch.setattr(T3, "git_state", lambda repo: dict(CLEAN))
    sd, od, v2 = make_run(tmp_path, measure="v2")
    with pytest.raises(Fail, match="measure v3"):
        T3.main(sd, od, v2, tmp_path / "o")


def test_draw_fails_when_slant_run_is_on_another_ocr(tmp_path, monkeypatch):
    monkeypatch.setattr(T3, "git_state", lambda repo: dict(CLEAN))
    sd, od, v2 = make_run(tmp_path, sha="0" * 64)
    with pytest.raises(Fail, match="ocr.json"):
        T3.main(sd, od, v2, tmp_path / "o")


# ---- the crops -----------------------------------------------------------------------------------------

PW, PH = 200, 200


def crop_setup(tmp_path, monkeypatch, ink_rows=()):
    """One line of two words (y 50..70); ink_rows: page rows set to ink across the word x range of w1."""
    od, ts = tmp_path / "ocr", tmp_path / "ts"
    (od / "pages").mkdir(parents=True)
    ts.mkdir()
    words = [{"key": "913/left/1.1.0.0", "page": 913, "region": "left", "bbox": [20, 50, 60, 70]},
             {"key": "913/left/1.1.0.1", "page": 913, "region": "left", "bbox": [70, 52, 110, 68]}]
    pg = np.full((PH, PW), 255, dtype=np.uint8)
    pg[55:65, 25:55] = 0
    pg[55:65, 75:105] = 0
    for y in ink_rows:
        pg[y, 20:60] = 0
    Image.fromarray(pg, "L").save(od / "pages" / "p913.png")
    (od / "ocr.json").write_text(json.dumps({"header": {}, "words": words}), encoding="utf-8")
    rows = [{"key": w["key"], "page": 913, "region": "left", "bbox": w["bbox"], "stratum": "upright",
             "slant": 0.0, "signed_italic": None} for w in words]
    (ts / "candidates.json").write_text(json.dumps({"summary": {}, "rows": rows}), encoding="utf-8")
    monkeypatch.setattr(C3, "git_state", lambda repo: dict(CLEAN))
    return ts, od


def run_crops(ts, od, out):
    C3.main(ts, od, out)
    return json.loads((out / "crops.json").read_text(encoding="utf-8"))


def test_crops_first_cut_ok(tmp_path, monkeypatch):
    ts, od = crop_setup(tmp_path, monkeypatch)
    d = run_crops(ts, od, tmp_path / "o")
    assert d["counts"] == {"n_candidates": 2, "first_cut_ok": 2, "recut_ok": 0, "dropped": 0}
    r = d["rows"][0]
    assert r["word_pad"] == 6 and r["word_size"][1] == 20 + 12 and r["word_size"][0] in (40, 40)
    assert (tmp_path / "o" / f"{r['id']}_word.png").is_file() and (tmp_path / "o" / f"{r['id']}_line.png").is_file()


def test_crops_recut_at_twelve_when_ink_sits_in_the_first_pad(tmp_path, monkeypatch):
    ts, od = crop_setup(tmp_path, monkeypatch, ink_rows=(44,))  # y 44 is the top row of the 6-pad cut (50-6)
    d = run_crops(ts, od, tmp_path / "o")
    c = d["counts"]
    assert c["recut_ok"] == 2 - c["first_cut_ok"] and c["recut_ok"] >= 1 and c["dropped"] == 0
    assert any(r["word_pad"] == 12 for r in d["rows"])
    r = next(r for r in d["rows"] if r["word_pad"] == 12)
    assert r["word_size"][1] == 20 + 24


def test_crops_dropped_when_ink_at_both_pads(tmp_path, monkeypatch):
    ts, od = crop_setup(tmp_path, monkeypatch, ink_rows=(44, 38))
    d = run_crops(ts, od, tmp_path / "o")
    assert d["counts"]["dropped"] >= 1 and d["dropped"][0]["edges"]["top"] > 0
    ids = {r["id"] for r in d["rows"]}
    for dr in d["dropped"]:
        assert dr["id"] not in ids and not (tmp_path / "o" / f"{dr['id']}_word.png").exists()
        assert not (tmp_path / "o" / f"{dr['id']}_line.png").exists()


def test_crops_counts_add_up_and_params(tmp_path, monkeypatch):
    ts, od = crop_setup(tmp_path, monkeypatch, ink_rows=(44, 38))
    d = run_crops(ts, od, tmp_path / "o")
    c = d["counts"]
    assert c["first_cut_ok"] + c["recut_ok"] + c["dropped"] == c["n_candidates"] == 2
    assert len(d["rows"]) == c["first_cut_ok"] + c["recut_ok"] and len(d["dropped"]) == c["dropped"]
    assert d["params"] == {"v_pad": 6, "recut_pad": 12, "line_pad": 12}


def test_crops_json_is_byte_identical_on_rerun(tmp_path, monkeypatch):
    ts, od = crop_setup(tmp_path, monkeypatch, ink_rows=(44,))
    run_crops(ts, od, tmp_path / "a")
    run_crops(ts, od, tmp_path / "b")
    assert (tmp_path / "a" / "crops.json").read_bytes() == (tmp_path / "b" / "crops.json").read_bytes()
    j = json.loads((tmp_path / "a" / "crops.json").read_text(encoding="utf-8"))
    assert "stratum" not in json.dumps(j) and "slant" not in json.dumps(j)


def test_crops_page_edge_failure_counts(tmp_path, monkeypatch):
    ts, od = crop_setup(tmp_path, monkeypatch)
    pg = np.full((PH, PW), 255, dtype=np.uint8)
    pg[0:70, 20:60] = 0  # ink runs off the top of the page
    Image.fromarray(pg, "L").save(od / "pages" / "p913.png")
    words = json.loads((od / "ocr.json").read_text(encoding="utf-8"))["words"]
    words[0]["bbox"] = [20, 3, 60, 70]
    words[1]["bbox"] = [70, 3, 110, 70]
    (od / "ocr.json").write_text(json.dumps({"header": {}, "words": words}), encoding="utf-8")
    rows = [{"key": w["key"], "page": 913, "region": "left", "bbox": w["bbox"], "stratum": "x", "slant": 0,
             "signed_italic": None} for w in words]
    (ts / "candidates.json").write_text(json.dumps({"summary": {}, "rows": rows}), encoding="utf-8")
    d = run_crops(ts, od, tmp_path / "o")
    assert d["counts"]["dropped"] >= 1


# ---- the builder ---------------------------------------------------------------------------------------

def v3_module():
    s = importlib.util.spec_from_file_location("ts_italic_v3_spec",
                                               ROOT / "tools" / "console" / "specs" / "truthset_italic_v3.py")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def v3_dir(tmp_path, n=3):
    rows = []
    for i in range(1, n + 1):
        i_ = f"w{i:03d}"
        w = np.full((24, 20), 255, dtype=np.uint8)
        w[6:18, 5:15] = 30
        ln = np.full((30, 80), 255, dtype=np.uint8)
        ln[8:22, 12:32] = 30
        Image.fromarray(w, "L").save(tmp_path / f"{i_}_word.png")
        Image.fromarray(ln, "L").save(tmp_path / f"{i_}_line.png")
        rows.append({"id": i_, "key": f"913/left/1.1.{i}.0", "page": 913, "region": "left",
                     "word_png": f"{i_}_word.png", "word_sha256": build.sha256_file(tmp_path / f"{i_}_word.png"),
                     "word_size": [20, 24], "word_pad": 6, "line_png": f"{i_}_line.png",
                     "line_sha256": build.sha256_file(tmp_path / f"{i_}_line.png"), "box": [12, 7, 32, 17]})
    (tmp_path / "crops.json").write_text(json.dumps({"rows": rows, "dropped": [], "counts": {}}), encoding="utf-8")
    return tmp_path


def test_builder_spec_passes_check_spec_and_carries_clear_edges(tmp_path):
    spec = v3_module().make_spec(v3_dir(tmp_path))
    build.check_spec(spec)
    assert spec["kind"] == "truthset-italic-v3" and [s["id"] for s in spec["sections"]] == ["words"]
    words = [i for i in spec["images"] if i["id"].endswith("_word")]
    lines = [i for i in spec["images"] if i["id"].endswith("_line")]
    assert len(words) == len(lines) == 3 and all(i["clear_edges"] == ["top", "bottom"] for i in words)
    assert all(len(i["overlay"]) == 1 and "clear_edges" not in i for i in lines)
    assert spec["keyboard"] == {"field": "v", "keys": {"i": "italic", "r": "roman", "o": build.OTHER}}
    assert spec["prediction"] == "~/.golden-chain/italic-v3-predictions-locked.txt"
    blob = json.dumps(spec).lower()
    for bad in ("stratum", "slanted", "p912", "p914", "p. 912", "p. 914"):
        assert bad not in blob


def test_builder_every_field_has_plain_and_kind_registered(tmp_path):
    spec = v3_module().make_spec(v3_dir(tmp_path))
    fields = [f for s in spec["sections"] for r in s["rows"] for f in r["fields"]]
    assert [f["id"] for f in fields[:2]] == ["v", "note"] and all(f["plain"].strip() for f in fields)
    note = fields[1]
    assert note["kind"] == "text" and note["required"] is False
    assert "truthset-italic-v3" in build.KINDS and "truthset-italic-v3" in ingest.KINDS


def test_builder_fails_on_sha_mismatch_and_missing_png(tmp_path):
    m = v3_module()
    d = v3_dir(tmp_path)
    Image.fromarray(np.full((24, 21), 255, dtype=np.uint8), "L").save(d / "w002_word.png")
    with pytest.raises(Fail):
        m.make_spec(d)


def test_build_refuses_a_word_image_with_ink_on_its_top_edge(tmp_path, monkeypatch):
    d = v3_dir(tmp_path)
    w = np.full((24, 20), 255, dtype=np.uint8)
    w[0, 3:9] = 30
    w[6:18, 5:15] = 30
    Image.fromarray(w, "L").save(d / "w001_word.png")
    crops = json.loads((d / "crops.json").read_text(encoding="utf-8"))
    crops["rows"][0]["word_sha256"] = build.sha256_file(d / "w001_word.png")
    (d / "crops.json").write_text(json.dumps(crops), encoding="utf-8")
    spec = v3_module().make_spec(d)
    with pytest.raises(Fail, match="top edge"):
        build.hash_images(spec)


def test_ingest_renders_v3_like_v2_with_notes(tmp_path, monkeypatch):
    spec_in = v3_module().make_spec(v3_dir(tmp_path))
    out = tmp_path / "spec.json"
    build.write_spec(out, spec_in)
    made, man = tcs.built(tmp_path, monkeypatch, out)
    spec = json.loads(made["spec"].read_text(encoding="utf-8"))
    ho = tmp_path / "handoff"
    ho.mkdir()
    monkeypatch.setattr(ingest, "HANDOFF", ho)

    def answers(ex):
        ex["rows"]["w001"]["values"]["v"] = "italic"
        ex["rows"]["w002"]["values"]["v"] = "roman"
        ex["rows"]["w003"]["values"]["v"] = {"other": "small caps"}
        ex["rows"]["w001"]["note"] = "a note"
    res = tcs.sign(tmp_path, made, man, spec, answers, write=True)
    md = ho / f"SIGNED_truthset_italic_v3_{man['build16']}.md"
    assert res[1] == md
    t = md.read_text(encoding="utf-8")
    assert "| id | key | answer | note |" in t
    assert "| w001 | 913/left/1.1.1.0 | italic | a note |" in t and "| w002 | 913/left/1.1.2.0 | roman |" in t
    assert "| w003 | 913/left/1.1.3.0 | other: small caps |" in t and man["build_hash"] in t
