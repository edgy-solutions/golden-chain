"""Truth-set v5 (draw with replacement, crops, console kind) and the tall-box band measure: synthetic numpy only."""

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
import ingest  # noqa: E402
import tallbox_bands as TB  # noqa: E402
import test_console_specs as tcs  # noqa: E402
import truthset_crops_v5 as C5  # noqa: E402
import truthset_v2  # noqa: E402
import truthset_v4 as T4  # noqa: E402
import truthset_v5 as V5  # noqa: E402
from column_rule import Fail  # noqa: E402
from test_italic_v4 import full, mk, v4_dir  # noqa: E402

CLEAN = {"commit": "abc123", "dirty": False, "porcelain": 0}
PAGES = list(range(1, 11))


def clean_git(monkeypatch):
    for m in (V5, C5, TB):
        monkeypatch.setattr(m, "git_state", lambda repo: dict(CLEAN))


# ---- first_choices -------------------------------------------------------------------------------------

def test_first_choices_equal_v4_under_the_v4_order_key():
    c = full((1, 2, 3, 4))
    c[(2, "slanted")] = 1
    c[(3, "upright")] = 0
    c[(4, "edge")] = 1
    rows, boxes = mk(None, c)
    ex = {rows[0]["key"], rows[7]["key"], rows[90]["key"]}
    out, realloc, pools = V5.first_choices(rows, boxes, ex, okey=T4.order_key)
    assert (out, realloc) == T4.draw_with_realloc(rows, boxes, ex)
    assert all(k not in ex for ws in pools.values() for k in (w["key"] for w in ws))


def test_first_choices_default_key_is_v5_and_differs():
    rows, boxes = mk(None, full((1, 2, 3)))
    a, _, pools = V5.first_choices(rows, boxes)
    b, _, _ = V5.first_choices(rows, boxes, okey=T4.order_key)
    assert V5.SALT == "truthset-v5/" and a != b and len(a) == len(b) == 30
    for (p, s), ws in pools.items():
        assert [w["key"] for w in ws] == sorted((w["key"] for w in ws), key=V5.order_key)
        assert all(w["page"] == p and w["stratum"] == s for w in ws)


def test_first_choices_apply_v2_v3_v4_exclusions():
    rows, boxes = mk(None, full((1, 2)))
    first, _, _ = V5.first_choices(rows, boxes)
    ex2, ex3, ex4 = ({r["key"] for r in first[a:b]} for a, b in ((0, 4), (4, 9), (9, 14)))
    again, _, pools = V5.first_choices(rows, boxes, ex2 | ex3 | ex4)
    keys = {r["key"] for r in again}
    assert not keys & (ex2 | ex3 | ex4) and len(again) == len(first)
    assert not {w["key"] for ws in pools.values() for w in ws} & (ex2 | ex3 | ex4)


# ---- replace -------------------------------------------------------------------------------------------

def world(counts=None):
    rows, boxes = mk(None, counts or full(PAGES, 8))
    return V5.first_choices(rows, boxes)


def fake(fails, calls=None):
    def f(r):
        if calls is not None:
            calls.append(r["key"])
        return fails.get(r["key"])
    return f


def kept_keys(res, s=None):
    return [r["key"] for r in res["rows"] if s is None or r["stratum"] == s]


def test_replace_without_failures_keeps_the_first_choices():
    first, _, pools = world()
    res = V5.replace(first, pools, fake({}), PAGES)
    assert res["rows"] == first and res["drops"] == []
    assert res["ceiling"]["tripped"] is False
    assert res["ceiling"]["by_stratum"]["slanted"] == {"first": 40, "replaced": 0, "limit_exceeded": False}
    assert all(v == {"same_page": 0, "round_robin": 0, "unmet": 0} for v in res["replacements"].values())


def test_replace_takes_the_next_word_of_the_same_page_and_stratum():
    first, _, pools = world()
    pool = pools[(3, "slanted")]
    res = V5.replace(first, pools, fake({pool[1]["key"]: "top"}), PAGES)
    ks = kept_keys(res, "slanted")
    assert len(ks) == 40 and pool[1]["key"] not in ks and pool[4]["key"] in ks
    assert res["replacements"]["slanted"] == {"same_page": 1, "round_robin": 0, "unmet": 0}
    assert res["drops"] == [{"key": pool[1]["key"], "page": 3, "stratum": "slanted", "slant": pool[1]["slant"],
                             "side": "top", "first_choice": True}]


def test_replace_a_failing_replacement_is_listed_and_replaced_again():
    first, _, pools = world()
    pool = pools[(3, "upright")]
    fails = {pool[0]["key"]: "bottom", pool[4]["key"]: "both"}
    res = V5.replace(first, pools, fake(fails), PAGES)
    ks = kept_keys(res, "upright")
    assert len(ks) == 40 and pool[5]["key"] in ks and pool[4]["key"] not in ks
    assert sorted((d["key"], d["side"], d["first_choice"]) for d in res["drops"]) == sorted(
        [(pool[0]["key"], "bottom", True), (pool[4]["key"], "both", False)])
    assert res["replacements"]["upright"]["same_page"] == 1


def test_replace_exhausted_page_goes_round_robin_from_the_lowest_page():
    c = full(PAGES, 8)
    c[(7, "slanted")] = 4  # page 7: first choices are the whole pool
    first, _, pools = world(c)
    p7 = pools[(7, "slanted")]
    fails = {p7[0]["key"]: "top", p7[1]["key"]: "top"}
    res = V5.replace(first, pools, fake(fails), PAGES)
    assert len(kept_keys(res, "slanted")) == 40
    assert res["replacements"]["slanted"] == {"same_page": 0, "round_robin": 2, "unmet": 0}
    assert res["by_page"]["slanted"] == {"took": {"1": 1, "2": 1}}
    assert pools[(1, "slanted")][4]["key"] in kept_keys(res) and pools[(2, "slanted")][4]["key"] in kept_keys(res)


def test_replace_round_robin_wraps_over_pages_and_skips_failures():
    c = full(PAGES, 8)
    c[(7, "slanted")] = 4
    first, _, pools = world(c)
    p7 = pools[(7, "slanted")]
    fails = {p7[0]["key"]: "top", p7[1]["key"]: "top", p7[2]["key"]: "top", pools[(1, "slanted")][4]["key"]: "bottom"}
    res = V5.replace(first, pools, fake(fails), PAGES)
    # page 1's next word fails (listed), the round goes on to page 2 and 3; the third unmet takes page 4
    assert len(kept_keys(res, "slanted")) == 40
    assert res["by_page"]["slanted"] == {"took": {"2": 1, "3": 1, "4": 1}}
    assert any(d["key"] == pools[(1, "slanted")][4]["key"] and d["first_choice"] is False for d in res["drops"])


def test_replace_short_only_when_every_pool_is_exhausted():
    c = full(PAGES, 8)
    for p in PAGES:
        c[(p, "slanted")] = 4  # every pool is just the first choices
    first, _, pools = world(c)
    ks = [r["key"] for r in first if r["stratum"] == "slanted"]
    res = V5.replace(first, pools, fake({ks[3]: "top", ks[20]: "top"}), PAGES)
    assert len(kept_keys(res, "slanted")) == 38
    assert res["replacements"]["slanted"] == {"same_page": 0, "round_robin": 0, "unmet": 2}
    assert res["ceiling"]["tripped"] is False and len(kept_keys(res, "upright")) == 40


def test_replace_never_tries_a_word_twice():
    c = full(PAGES, 8)
    c[(7, "slanted")] = 5
    first, _, pools = world(c)
    fails = {w["key"]: "top" for p in (3, 7) for w in pools[(p, "slanted")][:2]}  # 4 failures, 7 exhausts
    calls = []
    res = V5.replace(first, pools, fake(fails, calls), PAGES)
    assert len(calls) == len(set(calls))
    assert len(kept_keys(res, "slanted")) == 40


@pytest.mark.parametrize("s,n_first,k,tripped", [("slanted", 80, 8, False), ("slanted", 80, 9, True),
                                                 ("edge", 40, 4, False), ("edge", 40, 5, True)])
def test_replace_ceiling_boundary(s, n_first, k, tripped):
    pages = list(range(1, 21))
    first, _, pools = world(full(pages, 30))
    ks = [r["key"] for r in first if r["stratum"] == s]
    assert len(ks) == n_first
    res = V5.replace(first, pools, fake({x: "top" for x in ks[:k]}), pages)
    assert res["ceiling"]["tripped"] is tripped
    assert res["ceiling"]["by_stratum"][s] == {"first": n_first, "replaced": k, "limit_exceeded": tripped}


def test_replace_a_trip_does_no_replacement():
    pages = list(range(1, 21))
    first, _, pools = world(full(pages, 30))
    ks = [r["key"] for r in first if r["stratum"] == "slanted"][:9]
    calls = []
    res = V5.replace(first, pools, fake({x: "bottom" for x in ks}, calls), pages)
    assert res["ceiling"]["tripped"] is True and res["rows"] == first
    assert len(calls) == len(first)  # only the first choices were checked
    assert sorted(d["key"] for d in res["drops"]) == sorted(ks) and all(d["first_choice"] for d in res["drops"])
    assert all(v == {"same_page": 0, "round_robin": 0, "unmet": 0} for v in res["replacements"].values())


def test_replace_drops_rows_shape_and_order():
    first, _, pools = world()
    fails = {}
    for s in ("edge", "upright", "slanted"):
        fails[pools[(5, s)][0]["key"]] = "top"
        fails[pools[(2, s)][1]["key"]] = "both"
    res = V5.replace(first, pools, fake(fails), PAGES)
    if res["ceiling"]["tripped"]:  # edge has 20 first choices: 2 failing is 10 %, not over
        pytest.fail("unexpected trip")
    for d in res["drops"]:
        assert set(d) == {"key", "page", "stratum", "slant", "side", "first_choice"}
    order = list(truthset_v2.STRATA)
    keyf = [(order.index(d["stratum"]), d["page"], V5.order_key(d["key"])) for d in res["drops"]]
    assert keyf == sorted(keyf)


# ---- main of the draw ----------------------------------------------------------------------------------

COUNTS = {(p, s): n for p in range(900, 910) for s, n in (("slanted", 6), ("upright", 6), ("edge", 3))}


def synth(tmp_path, measure="v4"):
    """Ten pages, each with 15 words, one word per line, stacked 40 px apart; returns the OCR and slant dirs."""
    od = tmp_path / "ocr"
    (od / "pages").mkdir(parents=True)
    rows, words, geom = [], [], {}
    for p in range(900, 910):
        n = 0
        for s in truthset_v2.STRATA:
            for i in range(COUNTS[(p, s)]):
                k = f"{p}/left/1.{n}.0"
                y0 = 20 + 40 * n
                words.append({"key": k, "page": p, "region": "left", "bbox": [10, y0, 50, y0 + 16]})
                r = ({"abstain": "edge", "slanted": None, "slant": None} if s == "edge" else
                     {"abstain": None, "slanted": s == "slanted", "slant": 0.25 if s == "slanted" else 0.0})
                rows.append({"key": k, "page": p, "region": "left", **r})
                geom[k] = (p, y0)
                n += 1
    (od / "ocr.json").write_text(json.dumps({"header": {}, "words": words}), encoding="utf-8")
    sd = tmp_path / "slant"
    sd.mkdir()
    (sd / "slant.json").write_text(json.dumps({"rows": rows, "params": {"measure": measure},
                                               "input": {"ocr_json_sha256": V5.sha256_file(od / "ocr.json")}}),
                                   encoding="utf-8")
    return od, sd, rows, {w["key"]: w["bbox"] for w in words}, geom


def paint(od, geom, fails):
    """Write the page images: ink in every word box; a failing word gets an own stroke reaching the crop edge."""
    pages = {p: np.full((20 + 40 * 15 + 60, 80), 255, dtype=np.uint8) for p in range(900, 910)}
    for k, (p, y0) in geom.items():
        pages[p][y0 + 4:y0 + 12, 14:46] = 0
        side = fails.get(k)
        if side in ("top", "both"):
            pages[p][y0 - 12:y0 + 4, 20:22] = 0
        if side in ("bottom", "both"):
            pages[p][y0 + 12:y0 + 28, 30:32] = 0
    for p, a in pages.items():
        Image.fromarray(a, "L").save(od / "pages" / f"p{p}.png")


def earlier(tmp_path, rows):
    ks = [r["key"] for r in rows if r["abstain"] is None and r["slanted"]]
    out = []
    for name, sl in (("v2", ks[0:2]), ("v3", ks[2:3]), ("v4", ks[3:4])):
        p = tmp_path / f"{name}.json"
        p.write_text(json.dumps({"rows": [{"key": k} for k in sl]}), encoding="utf-8")
        out.append(p)
    return out


def firsts(rows, boxes, ex):
    return V5.first_choices(rows, boxes, ex)[0]


def run_draw(tmp_path, monkeypatch, fail_fn=lambda first, pool_rows: {}, out="o"):
    clean_git(monkeypatch)
    od, sd, rows, boxes, geom = synth(tmp_path)
    v2, v3, v4 = earlier(tmp_path, rows)
    ex = set()
    for p in (v2, v3, v4):
        ex |= {r["key"] for r in json.loads(p.read_text())["rows"]}
    first = firsts(rows, boxes, ex)
    paint(od, geom, fail_fn(first, rows))
    rc = V5.main(sd, od, v2, v3, v4, tmp_path / out)
    return rc, od, sd, (v2, v3, v4), rows, first, geom


def slanted_firsts(first, n):
    return [r["key"] for r in first if r["stratum"] == "slanted"][:n]


def test_main_happy_path(tmp_path, monkeypatch):
    rc, od, sd, ex, rows, first, _ = run_draw(tmp_path, monkeypatch,
                                              lambda f, r: {k: "top" for k in slanted_firsts(f, 2)})
    assert rc == 0
    d = json.loads((tmp_path / "o" / "candidates.json").read_text(encoding="utf-8"))
    s = d["summary"]
    assert s["n"] == 100 and s["by_stratum"] == {"slanted": 40, "upright": 40, "edge": 20}
    assert s["ceiling"]["tripped"] is False and s["ceiling"]["by_stratum"]["slanted"]["replaced"] == 2
    assert s["replacements"]["slanted"]["same_page"] + s["replacements"]["slanted"]["round_robin"] == 2
    assert s["excluded_v2"] == 2 and s["excluded_v3"] == 1 and s["excluded_v4"] == 1
    assert (s["shared_with_v2"], s["shared_with_v3"], s["shared_with_v4"]) == (0, 0, 0)
    assert s["digest"] == truthset_v2.digest(d["rows"])
    assert not {r["key"] for r in d["rows"]} & set(slanted_firsts(first, 2))
    assert all(r["signed_italic"] is None and set(r) == {"key", "page", "region", "bbox", "stratum", "slant",
                                                         "signed_italic"} for r in d["rows"])
    dr = json.loads((tmp_path / "o" / "drops.json").read_text(encoding="utf-8"))
    assert dr["by_stratum"] == {"slanted": 2, "upright": 0, "edge": 0} and dr["by_side"]["top"] == 2
    assert all(x["first_choice"] for x in dr["rows"])
    h = json.loads((tmp_path / "o" / "run_header.json").read_text(encoding="utf-8"))
    assert h["clean_run"] is True and h["input"]["v4_candidates_sha256"] == V5.sha256_file(ex[2])
    assert h["input"]["slant_json_sha256"] and h["input"]["v2_candidates_sha256"] == V5.sha256_file(ex[0])
    assert (tmp_path / "o" / "README.txt").read_text().startswith("LOCAL ONLY")


def test_main_forced_trip_exits_3_and_writes_the_first_choices(tmp_path, monkeypatch):
    rc, od, sd, ex, rows, first, _ = run_draw(tmp_path, monkeypatch,
                                              lambda f, r: {k: "bottom" for k in slanted_firsts(f, 5)})
    assert rc == 3
    d = json.loads((tmp_path / "o" / "candidates.json").read_text(encoding="utf-8"))
    assert d["summary"]["ceiling"]["tripped"] is True
    assert d["summary"]["ceiling"]["by_stratum"]["slanted"] == {"first": 40, "replaced": 5, "limit_exceeded": True}
    assert d["rows"] == first
    dr = json.loads((tmp_path / "o" / "drops.json").read_text(encoding="utf-8"))
    assert len(dr["rows"]) == 5 and dr["by_side"]["bottom"] == 5


def test_main_fails_on_measure_v3(tmp_path, monkeypatch):
    clean_git(monkeypatch)
    od, sd, rows, boxes, geom = synth(tmp_path, measure="v3")
    paint(od, geom, {})
    v2, v3, v4 = earlier(tmp_path, rows)
    with pytest.raises(Fail, match="measure v4"):
        V5.main(sd, od, v2, v3, v4, tmp_path / "o")


def test_main_fails_on_another_ocr(tmp_path, monkeypatch):
    clean_git(monkeypatch)
    od, sd, rows, boxes, geom = synth(tmp_path)
    j = json.loads((sd / "slant.json").read_text())
    j["input"]["ocr_json_sha256"] = "0" * 64
    (sd / "slant.json").write_text(json.dumps(j))
    v2, v3, v4 = earlier(tmp_path, rows)
    with pytest.raises(Fail, match="ocr.json"):
        V5.main(sd, od, v2, v3, v4, tmp_path / "o")


def test_main_fails_on_a_shared_key(tmp_path, monkeypatch):
    clean_git(monkeypatch)
    od, sd, rows, boxes, geom = synth(tmp_path)
    paint(od, geom, {})
    v2, v3, v4 = earlier(tmp_path, rows)
    shared = json.loads(v3.read_text())["rows"][0]["key"]
    monkeypatch.setattr(V5, "replace", lambda first, pools, check, pages: {
        "rows": [{"key": shared, "stratum": "slanted"}], "drops": [], "by_page": {},
        "ceiling": {"tripped": False, "by_stratum": {}}, "replacements": {}})
    with pytest.raises(Fail, match="earlier candidates"):
        V5.main(sd, od, v2, v3, v4, tmp_path / "o")


def test_main_rerun_is_byte_identical(tmp_path, monkeypatch):
    fn = lambda f, r: {k: "top" for k in slanted_firsts(f, 2)}  # noqa: E731
    _, od, sd, ex, _, _, _ = run_draw(tmp_path, monkeypatch, fn, out="a")
    V5.main(sd, od, *ex, tmp_path / "b")
    for f in ("candidates.json", "drops.json"):
        assert (tmp_path / "a" / f).read_bytes() == (tmp_path / "b" / f).read_bytes()
        assert b"\r" not in (tmp_path / "a" / f).read_bytes()


def test_main_pool_share_and_first_choice_share(tmp_path, monkeypatch):
    def fn(first, rows):
        fk = slanted_firsts(first, 2)
        firstkeys = {r["key"] for r in first}
        other = [r["key"] for r in rows if r["abstain"] is None and not r["slanted"] and r["key"] not in firstkeys][:5]
        edge = [r["key"] for r in first if r["stratum"] == "edge"][:1]
        return {**{k: "top" for k in fk}, **{k: "bottom" for k in other}, edge[0]: "both"}
    run_draw(tmp_path, monkeypatch, fn)
    s = json.loads((tmp_path / "o" / "candidates.json").read_text())["summary"]
    # excluded slanted: 4 of 60; slanted pool 56 with 2 failing; upright pool 60 with up to 5 failing non-first words
    assert s["first_choice_share"]["slanted"] == {"first": 40, "fail": 2, "share": 0.05}
    assert s["first_choice_share"]["edge"] == {"first": 20, "fail": 1, "share": 0.05}
    assert s["first_choice_share"]["upright"]["fail"] == 0
    assert s["pool_share"]["slanted"] == {"pool": 56, "fail": 2, "share": round(2 / 56, 4)}
    up = s["pool_share"]["upright"]
    assert up["pool"] == 60 and up["fail"] == 5 and up["share"] == round(5 / 60, 4)
    assert s["pool_share"]["edge"] == {"pool": 30, "fail": 1, "share": round(1 / 30, 4)}


# ---- crops v5 ------------------------------------------------------------------------------------------

def test_crop_check_sides():
    words = {"k": {"key": "k", "page": 900, "region": "left", "bbox": [10, 20, 50, 36]}}
    for side in (None, "top", "bottom", "both"):
        pg = np.full((100, 80), 255, dtype=np.uint8)
        pg[24:32, 14:46] = 0
        if side in ("top", "both"):
            pg[8:24, 20:22] = 0
        if side in ("bottom", "both"):
            pg[32:48, 30:32] = 0
        lines = {(900, "left", "k"): [10, 20, 50, 36]}
        row = {"key": "k", "bbox": [10, 20, 50, 36]}
        assert C5.crop_check(pg, words, lines, row) == side


def test_crops_refuse_a_tripped_candidates_file(tmp_path, monkeypatch):
    rc, od, *_ = run_draw(tmp_path, monkeypatch, lambda f, r: {k: "top" for k in slanted_firsts(f, 5)})
    assert rc == 3
    with pytest.raises(Fail, match="ceiling tripped"):
        C5.main(tmp_path / "o", od, tmp_path / "c")
    assert not (tmp_path / "c" / "crops.json").exists()


def test_crops_fail_if_a_candidate_fails_the_check(tmp_path, monkeypatch):
    rc, od, sd, ex, rows, first, geom = run_draw(tmp_path, monkeypatch)
    assert rc == 0
    paint(od, geom, {first[0]["key"]: "top"})  # changed inputs: a kept word now fails
    with pytest.raises(Fail, match="fails the crop check"):
        C5.main(tmp_path / "o", od, tmp_path / "c")


def test_crops_happy_path_dropped_empty_no_stratum_rerun_identical(tmp_path, monkeypatch):
    rc, od, *_ = run_draw(tmp_path, monkeypatch, lambda f, r: {k: "top" for k in slanted_firsts(f, 2)})
    assert rc == 0
    C5.main(tmp_path / "o", od, tmp_path / "a")
    C5.main(tmp_path / "o", od, tmp_path / "b")
    d = json.loads((tmp_path / "a" / "crops.json").read_text(encoding="utf-8"))
    assert d["dropped"] == [] and d["counts"] == {"n_candidates": 100, "kept": 100, "dropped": 0}
    assert d["params"] == {"pad": 12, "clip": "midpoint to neighbouring line", "edge": "word-connected ink only",
                           "line_pad": 12}
    assert all(r["word_box"] and r["word_rows"] for r in d["rows"])
    t = (tmp_path / "a" / "crops.json").read_text(encoding="utf-8")
    assert "stratum" not in t and "slant" not in t
    assert (tmp_path / "a" / "crops.json").read_bytes() == (tmp_path / "b" / "crops.json").read_bytes()
    assert not (tmp_path / "a" / "drops.json").exists()
    h = json.loads((tmp_path / "a" / "run_header.json").read_text())
    assert h["clean_run"] is True and (tmp_path / "a" / "README.txt").read_text().startswith("LOCAL ONLY")


# ---- the console ---------------------------------------------------------------------------------------

def v5_module():
    s = importlib.util.spec_from_file_location("ts_italic_v5_spec",
                                               ROOT / "tools" / "console" / "specs" / "truthset_italic_v5.py")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def test_builder_spec_kind_v5_and_word_box(tmp_path):
    spec = v5_module().make_spec(v4_dir(tmp_path))
    build.check_spec(spec)
    assert spec["kind"] == "truthset-italic-v5" and "v4" not in json.dumps(spec) and "v3" not in json.dumps(spec)
    words = [i for i in spec["images"] if i["id"].endswith("_word")]
    assert len(words) == 3 and all(i["clear_edges"] == ["top", "bottom"] and i["word_box"] == [8, 12, 22, 28]
                                   for i in words)
    assert spec["prediction"] == "~/.golden-chain/italic-v5-predictions-locked.txt"
    assert "truthset-italic-v5" in build.KINDS and "truthset-italic-v5" in ingest.KINDS
    build.hash_images(spec)
    blob = json.dumps(spec).lower()
    for bad in ("stratum", "slanted"):
        assert bad not in blob


def test_ingest_renders_v5_with_markdown_truthset(tmp_path, monkeypatch):
    spec_in = v5_module().make_spec(v4_dir(tmp_path))
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
    assert "| id | key | answer | note |" in t and "SIGNED_truthset_italic_v5_" in res[1].name
    assert "| w001 | 913/left/1.1.1.0 | italic | a note |" in t and man["build_hash"] in t


# ---- two_bands -----------------------------------------------------------------------------------------

def prof(*parts):
    return np.concatenate([np.full(n, v, dtype=int) for v, n in parts])


def test_two_bands_two_blocks_with_a_gap():
    r = TB.two_bands(prof((10, 20), (0, 5), (10, 20)))
    assert r == {"run": [20, 25], "share_above": 0.5, "share_below": 0.5, "band_above_px": 20, "band_below_px": 20}


def test_two_bands_gap_of_two_rows_is_none():
    assert TB.two_bands(prof((10, 20), (0, 2), (10, 20))) is None


def test_two_bands_gap_touching_first_or_last_row_is_none():
    assert TB.two_bands(prof((0, 5), (10, 30))) is None
    assert TB.two_bands(prof((10, 30), (0, 5))) is None
    assert TB.two_bands(prof((0, 5), (10, 20), (0, 5), (10, 20), (0, 5))) is not None  # the inner gap still counts


def test_two_bands_lopsided_split_is_none():
    assert TB.two_bands(prof((5, 17), (0, 4), (1, 15))) is None  # 85 / 15


def test_two_bands_a_band_under_15_px_is_none():
    assert TB.two_bands(prof((10, 10), (0, 4), (10, 20))) is None
    assert TB.two_bands(prof((10, 20), (0, 4), (10, 14))) is None
    assert TB.two_bands(prof((10, 15), (0, 4), (10, 15))) is not None


def test_two_bands_single_block_with_faint_ascender_rows_is_none():
    assert TB.two_bands(prof((1, 4), (20, 40), (1, 2))) is None
    assert TB.two_bands(prof((20, 40), (1, 3), (0, 3))) is None


def test_two_bands_the_more_balanced_run_wins():
    r = TB.two_bands(prof((10, 16), (0, 3), (10, 20), (0, 4), (10, 30)))
    assert r["run"] == [39, 43] and r["share_above"] == round(360 / 660, 4)


def test_two_bands_tie_goes_to_the_earliest_run():
    r = TB.two_bands(prof((10, 16), (0, 3), (10, 16), (0, 4), (10, 16)))
    r1 = TB.two_bands(prof((10, 16), (0, 3), (10, 32), (0, 4), (10, 16)))
    assert r1["run"] == [16, 19]  # shares .2 / .8 and .8 / .2: equal imbalance, the earliest wins


def test_two_bands_all_zeros_is_none():
    assert TB.two_bands(np.zeros(50, dtype=int)) is None
    assert TB.two_bands(np.array([], dtype=int)) is None


# ---- tallbox main --------------------------------------------------------------------------------------

def tall_setup(tmp_path):
    od, ts, cd = tmp_path / "ocr", tmp_path / "ts", tmp_path / "cd"
    (od / "pages").mkdir(parents=True)
    ts.mkdir()
    cd.mkdir()
    W = lambda k, b: {"key": k, "page": 913, "region": "left", "bbox": b}  # noqa: E731
    words = [W("913/left/1.0.0", [20, 10, 100, 50]),     # B: overlaps A, so A's top pad is 0
             W("913/left/1.1.0", [20, 40, 60, 120]),     # A: a merged two-line box, dropped on top
             W("913/left/1.2.0", [20, 300, 60, 320]),    # C: full pad, dropped on top
             W("913/left/1.3.0", [20, 200, 60, 220]),    # D: two words on one line, one band
             W("913/left/1.3.1", [70, 200, 110, 220]),
             W("913/left/1.4.0", [20, 340, 60, 400])]    # E: a kept merged box
    pg = np.full((500, 140), 255, dtype=np.uint8)
    pg[45:70, 25:55] = 0
    pg[90:115, 25:55] = 0       # A's two blocks, 20 gap rows
    pg[205:215, 25:55] = 0      # D one block
    pg[205:215, 75:105] = 0
    pg[305:315, 25:55] = 0      # C one block
    pg[345:366, 25:55] = 0
    pg[375:396, 25:55] = 0      # E's two blocks
    Image.fromarray(pg, "L").save(od / "pages" / "p913.png")
    (od / "ocr.json").write_text(json.dumps({"header": {}, "words": words}), encoding="utf-8")
    rows = [{"key": w["key"], "page": 913, "region": "left", "bbox": w["bbox"]} for w in words]
    (ts / "candidates.json").write_text(json.dumps({"summary": {}, "rows": rows}), encoding="utf-8")
    kept = [rows[3], rows[4], rows[5]]
    (cd / "crops.json").write_text(json.dumps({"rows": [{"key": r["key"]} for r in kept], "dropped": []}),
                                   encoding="utf-8")
    (cd / "drops.json").write_text(json.dumps({"rows": [
        {"id": "w001", "key": "913/left/1.1.0", "stratum": "upright", "side": "top"},
        {"id": "w002", "key": "913/left/1.2.0", "stratum": "slanted", "side": "top"}]}), encoding="utf-8")
    return od, ts, cd


def test_tallbox_main_selects_the_zero_pad_drop_and_shows_two_bands(tmp_path, monkeypatch, capsys):
    clean_git(monkeypatch)
    od, ts, cd = tall_setup(tmp_path)
    assert TB.main(od, ts, cd, tmp_path / "a") == 0
    d = json.loads((tmp_path / "a" / "bands.json").read_text(encoding="utf-8"))
    assert [s["id"] for s in d["selected"]] == ["w001"]  # w002 was granted the full 12 px
    s = d["selected"][0]
    assert s["key"] == "913/left/1.1.0" and s["side"] == "top" and s["box_height"] == 80
    assert s["pad_top"] == 0 and s["pad_bottom"] == 12
    assert s["two_bands"]["run"] == [30, 50] and s["two_bands"]["band_above_px"] == 25
    assert d["params"] == {"gap_frac": 0.05, "min_run": 3, "min_share": 0.2, "min_band_px": 15}
    summary = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert summary == {"n_selected": 1, "n_two_bands": 1, "control_n": 2, "control_two_bands": 1}


def test_tallbox_control_counts_distinct_lines_once(tmp_path, monkeypatch):
    clean_git(monkeypatch)
    od, ts, cd = tall_setup(tmp_path)
    TB.main(od, ts, cd, tmp_path / "a")
    c = json.loads((tmp_path / "a" / "bands.json").read_text(encoding="utf-8"))["control"]
    assert c["n"] == 2 and c["two_bands"] == 1  # D's two words are one line
    assert c["lines"][0]["key"] == "913/left/1.4.0" and c["lines"][0]["box_height"] == 60


def test_tallbox_a_full_pad_drop_is_not_selected_and_rerun_is_identical(tmp_path, monkeypatch):
    clean_git(monkeypatch)
    od, ts, cd = tall_setup(tmp_path)
    TB.main(od, ts, cd, tmp_path / "a")
    TB.main(od, ts, cd, tmp_path / "b")
    assert (tmp_path / "a" / "bands.json").read_bytes() == (tmp_path / "b" / "bands.json").read_bytes()
    assert "913/left/1.2.0" not in (tmp_path / "a" / "bands.json").read_text()
    h = json.loads((tmp_path / "a" / "run_header.json").read_text())
    assert h["clean_run"] is True and (tmp_path / "a" / "README.txt").read_text().startswith("LOCAL ONLY")
