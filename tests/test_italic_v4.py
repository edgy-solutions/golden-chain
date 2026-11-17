"""Measure v4, the v4 draw, crop_rows, word_edge_ink, v4 crops and the v4 console builder: synthetic numpy only."""

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
import gy_word_slant_v4 as S4  # noqa: E402
import ingest  # noqa: E402
import test_console_specs as tcs  # noqa: E402
import truthset_crops_v4 as C4  # noqa: E402
import truthset_v2  # noqa: E402
import truthset_v4 as T4  # noqa: E402
from column_rule import Fail  # noqa: E402

CLEAN = {"commit": "abc123", "dirty": False, "porcelain": 0}


# ---- the measure ---------------------------------------------------------------------------------------

def bar(s, h=60, w=80, thick=5):
    ink = np.zeros((h, w), dtype=bool)
    yc = (h - 1) / 2
    for y in range(h):
        x = 30 + int(round(s * (yc - y)))
        ink[y, x:x + thick] = True
    return ink


def best_s(ink):
    grid = S4.GRID
    return float(grid[int(np.argmax([S4.shear_score_v4(ink, float(s)) for s in grid]))])


@pytest.mark.parametrize("which", ["random", "bar"])
def test_score_is_phase_invariant(which):
    if which == "random":
        xp = np.random.default_rng(7).random(500) * 60
    else:
        xp = np.tile(np.arange(10.0, 15.0), 40)
    base = S4.score_positions(xp)
    for d in np.arange(0.1, 0.95, 0.1):
        assert abs(S4.score_positions(xp + d) / base - 1) <= 0.005


def test_kernel_is_normalised_and_truncated():
    assert abs(S4.KERNEL.sum() - 1) < 1e-12 and len(S4.KERNEL) == 33 and S4.OVERSAMPLE == 4


def test_score_positions_empty_is_zero():
    assert S4.score_positions([]) == 0.0


def test_upright_bar_gives_zero():
    assert best_s(bar(0.0)) == 0.0


@pytest.mark.parametrize("s", [0.25, -0.10, 0.03])
def test_sheared_bar_is_recovered(s):
    assert abs(best_s(bar(s)) - s) <= 0.01


def test_slant_small_and_edge():
    assert S4.slant(np.full((30, 30), 255, dtype=np.uint8)) == (None, "small")
    ink = bar(0.6, h=80, w=120, thick=4)
    a = np.where(ink, 0, 255).astype(np.uint8)
    assert S4.slant(a) == (None, "edge")
    s, why = S4.slant(np.where(bar(0.2), 0, 255).astype(np.uint8))
    assert why is None and abs(s - 0.2) <= 0.01


def make_ocr(tmp_path):
    od = tmp_path / "ocr"
    (od / "pages").mkdir(parents=True)
    (od / "regions").mkdir()
    reg = np.full((100, 160), 255, dtype=np.uint8)
    yc = (60 - 1) / 2
    for y in range(20, 80):
        for i in range(4):
            x = 12 + i * 10 + int(round(0.25 * (yc - (y - 20))))
            reg[y, x:x + 4] = 0
    Image.fromarray(reg, "L").save(od / "regions" / "p900-left.png")
    Image.fromarray(np.full((120, 160), 255, dtype=np.uint8), "L").save(od / "pages" / "p900.png")
    words = [{"key": "900/left/1.1.0.0", "page": 900, "region": "left", "text": "abcd", "bbox": [0, 45, 60, 55]},
             {"key": "900/left/1.1.0.1", "page": 900, "region": "left", "text": "efgh", "bbox": [70, 20, 100, 80]}]
    (od / "ocr.json").write_text(json.dumps({"header": {"splits": {"900": {"ytop": 0}}}, "words": words}),
                                 encoding="utf-8")
    return od


def test_main_gives_v4_and_is_byte_identical(tmp_path, monkeypatch):
    monkeypatch.setattr(S4, "git_state", lambda repo: dict(CLEAN))
    od = make_ocr(tmp_path)
    S4.main(od, tmp_path / "a")
    S4.main(od, tmp_path / "b")
    sj = json.loads((tmp_path / "a" / "slant.json").read_text(encoding="utf-8"))
    assert sj["params"]["measure"] == "v4" and "comb" in sj["summary"] and sj["params"]["sigma_px"] == 1.0
    assert abs(sj["rows"][0]["slant"] - 0.25) <= 0.03 and sj["rows"][0]["box"] == [0, 20, 60, 80]
    assert (tmp_path / "a" / "slant.json").read_bytes() == (tmp_path / "b" / "slant.json").read_bytes()
    h = json.loads((tmp_path / "a" / "run_header.json").read_text(encoding="utf-8"))
    assert h["run"] == "gy-word-slant-v4" and h["clean_run"] is True
    assert (tmp_path / "a" / "README.txt").read_text().startswith("LOCAL ONLY")


# ---- the draw ------------------------------------------------------------------------------------------

def mk(pages, counts):
    """counts[(page, stratum)] = n -> rows and bboxes."""
    rows, boxes = [], {}
    for (p, s), n in counts.items():
        for i in range(n):
            k = f"{p}/left/1.1.{s}.{i}"
            r = ({"abstain": "edge", "slanted": None, "slant": None} if s == "edge" else
                 {"abstain": None, "slanted": s == "slanted", "slant": 0.25 if s == "slanted" else 0.0})
            rows.append({"key": k, "page": p, "region": "left", **r})
            boxes[k] = [1, 2, 3, 4]
    return rows, boxes


def full(pages, n=30):
    return {(p, s): n for p in pages for s in truthset_v2.STRATA}


def count(rows, p, s):
    return sum(1 for r in rows if r["page"] == p and r["stratum"] == s)


def test_draw_no_shortfall_equals_plain_quotas():
    rows, boxes = mk(None, full((1, 2, 3)))
    out, realloc = T4.draw_with_realloc(rows, boxes)
    assert len(out) == 3 * 10
    for p in (1, 2, 3):
        for s, q in truthset_v2.STRATA.items():
            assert count(out, p, s) == q
    assert all(v == {"short": {}, "took": {}} for v in realloc.values())
    assert T4.draw(rows, boxes) == out and T4.SALT == "truthset-v4/"


def test_draw_shortfall_goes_round_robin_in_ascending_page_order():
    c = full((1, 2, 3, 4))
    c[(2, "slanted")] = 1  # page 2 short by 3
    rows, boxes = mk(None, c)
    out, realloc = T4.draw_with_realloc(rows, boxes)
    assert count(out, 2, "slanted") == 1 and len(out) == 4 * 10
    # target 16, pass 1 takes 4+1+4+4 = 13, three extras: pages 1, 3, 4 in ascending order, one each
    assert [count(out, p, "slanted") for p in (1, 2, 3, 4)] == [5, 1, 5, 5]
    assert sum(count(out, p, "slanted") for p in (1, 2, 3, 4)) == 16
    assert realloc["slanted"] == {"short": {"2": 3}, "took": {"1": 1, "3": 1, "4": 1}}
    assert realloc["upright"] == {"short": {}, "took": {}}


def test_draw_round_robin_wraps_and_stops_at_pool_size():
    c = full((1, 2, 3))
    c[(3, "upright")] = 0
    c[(2, "upright")] = 5  # page 1 pool 30
    rows, boxes = mk(None, c)
    out, realloc = T4.draw_with_realloc(rows, boxes)
    # target 12; pass 1 takes 4 + 4 + 0 = 8; four extras round-robin over pages 1 and 2 (page 3 is empty)
    assert sum(count(out, p, "upright") for p in (1, 2, 3)) == 12
    assert count(out, 3, "upright") == 0 and count(out, 2, "upright") == 5
    assert realloc["upright"]["short"] == {"3": 4} and realloc["upright"]["took"] == {"1": 3, "2": 1}


def test_draw_short_only_when_every_pool_is_empty():
    c = full((1, 2))
    c[(1, "edge")] = 1
    c[(2, "edge")] = 2
    rows, boxes = mk(None, c)
    out, realloc = T4.draw_with_realloc(rows, boxes)
    assert count(out, 1, "edge") == 1 and count(out, 2, "edge") == 2  # target 4, the pools hold 3
    assert realloc["edge"] == {"short": {"1": 1}, "took": {}} and len(out) == 8 + 8 + 3


def test_draw_applies_v2_and_v3_exclusions():
    rows, boxes = mk(None, full((1, 2)))
    first, _ = T4.draw_with_realloc(rows, boxes)
    ex2 = {r["key"] for r in first[:5]}
    ex3 = {r["key"] for r in first[5:12]}
    again = T4.draw(rows, boxes, ex2 | ex3)
    keys = {r["key"] for r in again}
    assert not keys & ex2 and not keys & ex3 and len(again) == len(first)


def test_draw_rows_sorted_and_shaped():
    rows, boxes = mk(None, full((2, 1)))
    out = T4.draw(rows, boxes)
    order = list(truthset_v2.STRATA)
    keyf = [(r["page"], order.index(r["stratum"]), T4.order_key(r["key"])) for r in out]
    assert keyf == sorted(keyf) and all(r["signed_italic"] is None and set(r) >= {"key", "bbox", "slant"}
                                        for r in out)
    assert T4.draw(list(reversed(rows)), boxes) == out


def make_run(tmp_path, measure="v4", clash=None):
    rows, boxes = mk(None, full((912, 913)))
    od = tmp_path / "ocr"
    od.mkdir()
    (od / "ocr.json").write_text(json.dumps({"header": {}, "words": [{"key": k, "bbox": b}
                                                                      for k, b in boxes.items()]}), encoding="utf-8")
    sd = tmp_path / "slant"
    sd.mkdir()
    (sd / "slant.json").write_text(json.dumps({"rows": rows, "params": {"measure": measure},
                                               "input": {"ocr_json_sha256": T4.sha256_file(od / "ocr.json")}}),
                                   encoding="utf-8")
    v2 = tmp_path / "v2.json"
    v3 = tmp_path / "v3.json"
    v2.write_text(json.dumps({"rows": [{"key": r["key"]} for r in rows[:6]]}), encoding="utf-8")
    v3.write_text(json.dumps({"rows": [{"key": r["key"]} for r in rows[40:46]]}), encoding="utf-8")
    return sd, od, v2, v3


def test_draw_main_summary_and_files(tmp_path, monkeypatch):
    monkeypatch.setattr(T4, "git_state", lambda repo: dict(CLEAN))
    sd, od, v2, v3 = make_run(tmp_path)
    T4.main(sd, od, v2, v3, tmp_path / "o")
    d = json.loads((tmp_path / "o" / "candidates.json").read_text(encoding="utf-8"))
    s = d["summary"]
    assert s["n"] == 20 and s["by_stratum"] == {"slanted": 8, "upright": 8, "edge": 4}
    assert s["shared_with_v2"] == 0 and s["shared_with_v3"] == 0 and s["excluded_v2"] == 6 and s["excluded_v3"] == 6
    assert set(s["realloc"]) == set(truthset_v2.STRATA) and s["digest"] == truthset_v2.digest(d["rows"])
    h = json.loads((tmp_path / "o" / "run_header.json").read_text(encoding="utf-8"))
    assert h["input"]["v2_candidates_sha256"] == T4.sha256_file(v2)
    assert h["input"]["v3_candidates_sha256"] == T4.sha256_file(v3) and h["input"]["slant_json_sha256"]
    assert (tmp_path / "o" / "README.txt").read_text().startswith("LOCAL ONLY")


def test_draw_main_summary_realloc_is_correct(tmp_path, monkeypatch):
    monkeypatch.setattr(T4, "git_state", lambda repo: dict(CLEAN))
    sd, od, v2, v3 = make_run(tmp_path)
    rows = json.loads((sd / "slant.json").read_text())["rows"]
    # v2/v3 take page 912's first slanted words: leave page 912 with 2 slanted
    slanted912 = [r["key"] for r in rows if r["page"] == 912 and r["slanted"]]
    v2.write_text(json.dumps({"rows": [{"key": k} for k in slanted912[:28]]}), encoding="utf-8")
    T4.main(sd, od, v2, v3, tmp_path / "o")
    s = json.loads((tmp_path / "o" / "candidates.json").read_text())["summary"]
    assert s["realloc"]["slanted"] == {"short": {"912": 2}, "took": {"913": 2}}
    assert s["by_stratum"]["slanted"] == 8


def test_draw_fails_on_measure_v3(tmp_path, monkeypatch):
    monkeypatch.setattr(T4, "git_state", lambda repo: dict(CLEAN))
    sd, od, v2, v3 = make_run(tmp_path, measure="v3")
    with pytest.raises(Fail, match="measure v4"):
        T4.main(sd, od, v2, v3, tmp_path / "o")


def test_draw_fails_on_another_ocr(tmp_path, monkeypatch):
    monkeypatch.setattr(T4, "git_state", lambda repo: dict(CLEAN))
    sd, od, v2, v3 = make_run(tmp_path)
    j = json.loads((sd / "slant.json").read_text())
    j["input"]["ocr_json_sha256"] = "0" * 64
    (sd / "slant.json").write_text(json.dumps(j))
    with pytest.raises(Fail, match="ocr.json"):
        T4.main(sd, od, v2, v3, tmp_path / "o")


def test_draw_fails_on_a_shared_key(tmp_path, monkeypatch):
    monkeypatch.setattr(T4, "git_state", lambda repo: dict(CLEAN))
    sd, od, v2, v3 = make_run(tmp_path)
    monkeypatch.setattr(T4, "draw_with_realloc", lambda *a, **k: (
        [{"key": "912/left/1.1.slanted.0"}], {}))
    with pytest.raises(Fail, match="earlier candidates"):
        T4.main(sd, od, v2, v3, tmp_path / "o")


# ---- crop_rows -----------------------------------------------------------------------------------------

def test_crop_rows_midpoint_clip_with_gap():
    L = [10, 100, 200, 120]
    above, below = [10, 60, 200, 80], [10, 140, 200, 160]
    assert C4.crop_rows(L, [20, 100, 50, 120], [above, below], 1000) == (90, 130)
    # above.y1 + L.y0 = 180 -> 90; L.y1 + below.y0 = 260 -> 130; both clip the 12 px pad (88, 132)


def test_crop_rows_midpoint_is_ceil_and_floor():
    L = [0, 100, 100, 120]
    assert C4.crop_rows(L, [0, 100, 10, 120], [[0, 70, 100, 91]], 1000)[0] == 96   # ceil(191/2)
    assert C4.crop_rows(L, [0, 100, 10, 120], [[0, 125, 100, 150]], 1000)[1] == 122  # floor(245/2)


def test_crop_rows_overlapping_neighbour_never_cuts_inside_own_box():
    L = [0, 100, 100, 120]
    above = [0, 90, 100, 110]  # overlaps L; its centre is above
    below = [0, 112, 100, 140]
    top, bottom = C4.crop_rows(L, [0, 100, 10, 120], [above, below], 1000)
    assert top == 100 and bottom == 120


def test_crop_rows_no_neighbour_gives_full_pad():
    assert C4.crop_rows([0, 100, 100, 120], [0, 100, 10, 120], [], 1000) == (88, 132)


def test_crop_rows_neighbour_without_x_overlap_is_ignored():
    L = [0, 100, 100, 120]
    far = [[200, 85, 300, 98], [200, 122, 300, 140], [50, 85, 100, 90]]
    assert C4.crop_rows(L, [0, 100, 40, 120], far[:2], 1000) == (88, 132)
    assert C4.crop_rows(L, [0, 100, 40, 120], [far[2]], 1000) == (88, 132)  # x 50..100 vs word 0..40
    assert C4.crop_rows(L, [60, 100, 90, 120], [far[2]], 1000)[0] == 95  # overlaps: ceil((90+100)/2)


def test_crop_rows_clips_to_the_page():
    assert C4.crop_rows([0, 5, 100, 20], [0, 5, 10, 20], [], 30) == (0, 30)
    assert C4.crop_rows([0, 5, 100, 20], [0, 5, 10, 20], [], 1000) == (0, 32)


def test_crop_rows_picks_the_nearest_neighbours():
    L = [0, 100, 100, 120]
    ls = [[0, 20, 100, 40], [0, 60, 100, 80], [0, 150, 100, 170], [0, 200, 100, 220]]
    assert C4.crop_rows(L, [0, 100, 10, 120], ls, 1000) == (90, 132)


# ---- word_edge_ink -------------------------------------------------------------------------------------

def page(h=30, w=30):
    return np.full((h, w), 255, dtype=np.uint8)


def test_edge_foreign_ink_not_connected_gives_zero():
    a = page()
    a[10:20, 10:20] = 0
    a[29, 0:8] = 0  # foreign, on the bottom edge, not touching the word
    a[0, 25:29] = 0
    e = build.word_edge_ink(a, [10, 10, 20, 20])
    assert e == {"top": 0, "bottom": 0, "left": 0, "right": 0}
    assert build.edge_ink(a)["bottom"] == 8


def test_edge_words_own_stroke_touching_the_bottom_counts():
    a = page()
    a[10:30, 12:15] = 0  # a descender running off the bottom
    a[10:14, 10:20] = 0
    e = build.word_edge_ink(a, [10, 10, 20, 20])
    assert e["bottom"] == 3 and e["top"] == 0


def test_edge_foreign_ink_connected_to_the_word_counts():
    a = page()
    a[10:20, 10:20] = 0
    a[20:30, 25] = 0
    a[19, 20:26] = 0  # a bridge from the word to the foreign stroke
    e = build.word_edge_ink(a, [10, 10, 20, 20])
    assert e["bottom"] == 1


def test_edge_diagonal_linking_counts():
    a = page()
    a[10:20, 10:20] = 0
    for i in range(10):
        a[20 + i, 20 + i] = 0  # touches the word's corner diagonally
    a[29, 29] = 0
    e = build.word_edge_ink(a, [10, 10, 20, 20])
    assert e["bottom"] == 1 and e["right"] == 1
    b = page()
    b[10:20, 10:20] = 0
    b[24:30, 24] = 0  # gap of one pixel diagonal-free
    assert build.word_edge_ink(b, [10, 10, 20, 20])["bottom"] == 0


def test_edge_no_ink_in_box_or_none_at_all():
    assert build.word_edge_ink(page(), [5, 5, 10, 10]) == {"top": 0, "bottom": 0, "left": 0, "right": 0}
    a = page()
    a[0:3, 0:3] = 0
    assert build.word_edge_ink(a, [10, 10, 20, 20])["top"] == 0


# ---- crops main ----------------------------------------------------------------------------------------

PW, PH = 200, 200


def crop_setup(tmp_path, monkeypatch, foreign=False, own_touch=False):
    """Line A (y 80..100) with two words; line B above (y 40..60) in the same region."""
    od, ts = tmp_path / "ocr", tmp_path / "ts"
    (od / "pages").mkdir(parents=True)
    ts.mkdir()
    words = [{"key": "913/left/1.1.1.0", "page": 913, "region": "left", "bbox": [20, 80, 60, 100]},
             {"key": "913/left/1.1.1.1", "page": 913, "region": "left", "bbox": [70, 80, 110, 100]},
             {"key": "913/left/1.1.0.0", "page": 913, "region": "left", "bbox": [20, 40, 110, 60]}]
    pg = np.full((PH, PW), 255, dtype=np.uint8)
    pg[85:95, 25:55] = 0
    pg[85:95, 75:105] = 0
    if foreign:
        pg[68:74, 25:55] = 0  # a neighbour's descender, clipped to the crop's top rows, not touching the word
    if own_touch:
        pg[70:90, 80:83] = 0  # the second word's own stroke reaching up out of the crop
    Image.fromarray(pg, "L").save(od / "pages" / "p913.png")
    (od / "ocr.json").write_text(json.dumps({"header": {}, "words": words}), encoding="utf-8")
    rows = [{"key": w["key"], "page": 913, "region": "left", "bbox": w["bbox"], "stratum": "upright",
             "slant": 0.0, "signed_italic": None} for w in words[:2]]
    (ts / "candidates.json").write_text(json.dumps({"summary": {}, "rows": rows}), encoding="utf-8")
    monkeypatch.setattr(C4, "git_state", lambda repo: dict(CLEAN))
    return ts, od


def run_crops(ts, od, out):
    C4.main(ts, od, out)
    return (json.loads((out / "crops.json").read_text(encoding="utf-8")),
            json.loads((out / "drops.json").read_text(encoding="utf-8")))


def test_crops_keep_a_row_with_only_a_neighbours_ink_at_the_edge(tmp_path, monkeypatch):
    ts, od = crop_setup(tmp_path, monkeypatch, foreign=True)
    d, dr = run_crops(ts, od, tmp_path / "o")
    # top = max(80-12, ceil((60+80)/2)) = 70; the foreign ink (rows 68..73) lies on the crop's top rows
    assert d["counts"] == {"n_candidates": 2, "kept": 2, "dropped": 0} and dr["rows"] == []
    r = d["rows"][0]
    assert r["word_rows"] == [70, 112] and r["word_box"] == [0, 10, 40, 30] and r["word_size"] == [40, 42]
    assert (tmp_path / "o" / f"{r['id']}_word.png").is_file()
    assert "word_pad" not in r and d["params"]["edge"] == "word-connected ink only" and d["params"]["pad"] == 12


def test_crops_drop_a_row_whose_word_ink_touches_the_edge(tmp_path, monkeypatch):
    ts, od = crop_setup(tmp_path, monkeypatch, own_touch=True)
    d, dr = run_crops(ts, od, tmp_path / "o")
    assert d["counts"] == {"n_candidates": 2, "kept": 1, "dropped": 1}
    assert dr["by_stratum"] == {"upright": 1} and dr["by_side"] == {"top": 1, "bottom": 0, "both": 0}
    row = dr["rows"][0]
    assert row["key"] == "913/left/1.1.1.1" and row["side"] == "top" and row["stratum"] == "upright"
    assert not (tmp_path / "o" / f"{row['id']}_word.png").exists()
    assert d["dropped"][0]["edges"]["top"] > 0


def test_crops_json_has_no_stratum_or_slant_and_reruns_identically(tmp_path, monkeypatch):
    ts, od = crop_setup(tmp_path, monkeypatch, own_touch=True)
    run_crops(ts, od, tmp_path / "a")
    run_crops(ts, od, tmp_path / "b")
    for f in ("crops.json", "drops.json"):
        assert (tmp_path / "a" / f).read_bytes() == (tmp_path / "b" / f).read_bytes()
    t = (tmp_path / "a" / "crops.json").read_text(encoding="utf-8")
    assert "stratum" not in t and "slant" not in t
    h = json.loads((tmp_path / "a" / "run_header.json").read_text())
    assert h["clean_run"] is True and (tmp_path / "a" / "README.txt").read_text().startswith("LOCAL ONLY")


# ---- the console ---------------------------------------------------------------------------------------

def word_png(tmp_path, name, foreign=False, own=False):
    a = np.full((40, 30), 255, dtype=np.uint8)
    a[12:28, 8:22] = 30
    if foreign:
        a[0:4, 2:6] = 30
    if own:
        a[0:14, 10:12] = 30
    p = tmp_path / name
    Image.fromarray(a, "L").save(p)
    return p


def test_build_word_box_passes_for_foreign_ink_and_fails_for_own(tmp_path):
    ent = {"id": "a", "clear_edges": ["top", "bottom"], "word_box": [8, 12, 22, 28]}
    build.check_clear_edges(ent, word_png(tmp_path, "f.png", foreign=True))
    with pytest.raises(Fail, match="top edge"):
        build.check_clear_edges(ent, word_png(tmp_path, "o.png", own=True))
    with pytest.raises(Fail, match="top edge"):
        build.check_clear_edges({"id": "a", "clear_edges": ["top"]}, word_png(tmp_path, "g.png", foreign=True))


def test_build_word_box_without_clear_edges_fails(tmp_path):
    with pytest.raises(Fail, match="without clear_edges"):
        build.check_clear_edges({"id": "a", "word_box": [8, 12, 22, 28]}, word_png(tmp_path, "f.png"))


@pytest.mark.parametrize("box", [[0, 0, 31, 40], [0, 0, 30, 41], [-1, 0, 10, 10], [10, 0, 10, 10], [12, 0, 8, 10],
                                 [0, 10, 10, 10], [0, 0, 10.5, 10], [0, 0, "10", 10], [0, 0, 10], "0,0,10,10",
                                 [True, 0, 10, 10]])
def test_build_malformed_word_box_fails(tmp_path, box):
    with pytest.raises(Fail, match="word_box"):
        build.check_clear_edges({"id": "a", "clear_edges": ["top"], "word_box": box}, word_png(tmp_path, "f.png"))


def v4_module():
    s = importlib.util.spec_from_file_location("ts_italic_v4_spec",
                                               ROOT / "tools" / "console" / "specs" / "truthset_italic_v4.py")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def v4_dir(tmp_path, n=3):
    rows = []
    for i in range(1, n + 1):
        i_ = f"w{i:03d}"
        w = np.full((40, 30), 255, dtype=np.uint8)
        w[12:28, 8:22] = 30
        w[0:4, 2:6] = 30  # a neighbour's ink on the top edge
        ln = np.full((30, 80), 255, dtype=np.uint8)
        ln[8:22, 12:32] = 30
        Image.fromarray(w, "L").save(tmp_path / f"{i_}_word.png")
        Image.fromarray(ln, "L").save(tmp_path / f"{i_}_line.png")
        rows.append({"id": i_, "key": f"913/left/1.1.{i}.0", "page": 913, "region": "left",
                     "word_png": f"{i_}_word.png", "word_sha256": build.sha256_file(tmp_path / f"{i_}_word.png"),
                     "word_size": [30, 40], "word_box": [8, 12, 22, 28], "word_rows": [0, 40],
                     "line_png": f"{i_}_line.png",
                     "line_sha256": build.sha256_file(tmp_path / f"{i_}_line.png"), "box": [12, 7, 32, 17]})
    (tmp_path / "crops.json").write_text(json.dumps({"rows": rows, "dropped": [], "counts": {},
                                                     "params": {"edge": "word-connected ink only"}}),
                                         encoding="utf-8")
    return tmp_path


def test_builder_spec_kind_v4_and_word_box(tmp_path):
    spec = v4_module().make_spec(v4_dir(tmp_path))
    build.check_spec(spec)
    assert spec["kind"] == "truthset-italic-v4" and "v3" not in json.dumps(spec)
    words = [i for i in spec["images"] if i["id"].endswith("_word")]
    assert len(words) == 3 and all(i["clear_edges"] == ["top", "bottom"] and i["word_box"] == [8, 12, 22, 28]
                                   for i in words)
    assert spec["prediction"] == "~/.golden-chain/italic-v4-predictions-locked.txt"
    assert "truthset-italic-v4" in build.KINDS and "truthset-italic-v4" in ingest.KINDS
    build.hash_images(spec)  # foreign ink on the top edge passes
    blob = json.dumps(spec).lower()
    for bad in ("stratum", "slanted", "p912", "p914"):
        assert bad not in blob


def test_builder_fails_without_word_box_or_with_other_edge(tmp_path):
    d = v4_dir(tmp_path)
    c = json.loads((d / "crops.json").read_text())
    c["params"]["edge"] = "any ink"
    (d / "crops.json").write_text(json.dumps(c))
    with pytest.raises(Fail, match="edge"):
        v4_module().make_spec(d)
    c["params"]["edge"] = "word-connected ink only"
    del c["rows"][1]["word_box"]
    (d / "crops.json").write_text(json.dumps(c))
    with pytest.raises(Fail, match="word_box"):
        v4_module().make_spec(d)


def test_ingest_renders_v4_like_v3_with_notes(tmp_path, monkeypatch):
    spec_in = v4_module().make_spec(v4_dir(tmp_path))
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
    t = res[1].read_text(encoding="utf-8")
    assert "| id | key | answer | note |" in t
    assert "| w001 | 913/left/1.1.1.0 | italic | a note |" in t and "| w002 | 913/left/1.1.2.0 | roman |" in t
    assert "| w003 | 913/left/1.1.3.0 | other: small caps |" in t and man["build_hash"] in t
