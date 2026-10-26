import math
import sys
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import signing_strips as ss  # noqa: E402

def run_json(n_strips=12, consts=None):
    sf = [{"y0": 700 + 300 * i, "y1": 1000 + 300 * i, "frac": [0.0]} for i in range(n_strips)]
    return {"header": {"constants": consts} if consts is not None else {}, "pages": {"1": {"strip_fracs": sf}}}


def test_strip_bounds_from_run():
    last, foot = ss.strip_bounds(run_json()["pages"]["1"])
    assert last == (4000, 4300) and foot == 3400


def test_strip_bounds_short_runs():
    assert ss.strip_bounds(run_json(2)["pages"]["1"]) == ((1000, 1300), 700)
    with pytest.raises(ss.Fail):
        ss.strip_bounds({"strip_fracs": []})


def test_parse_full_foot():
    argv, full, foot, nat = ss.parse(["x", "run", "--full", "1,2", "out", "--foot", "3"])
    assert argv == ["x", "run", "out"] and full == (1, 2) and foot == (3,)
    _, full, foot, nat = ss.parse(["x", "run"])
    assert full == ss.FULL_PAGES and foot == ss.FOOT_PAGES and nat is None
    assert ss.parse(["x", "run", "--native", "d"])[3] == "d"
    with pytest.raises(ss.Fail):
        ss.parse(["x", "run", "--full", "a"])


def test_readme_lists_ticks_yend_frame_and_line_h(tmp_path):
    d = run_json(3)
    d["pages"]["1"]["split"] = {"y_range": [1234, 1234]}
    made = [{"file": "f.png", "page": 1, "rows": [0, 9], "cols": [0, 9], "frame_wh": [100, 200], "line_h": 55},
            {"file": "g.png", "page": 1, "rows": [0, 9], "cols": [0, 9], "frame_wh": [100, 200], "line_h": None}]
    ss.write_readme(tmp_path, made, d)
    t = (tmp_path / "README.txt").read_text()
    assert "100 x 200 px, line height 55 px" in t and "line height n/a" in t
    assert "700, 1000, 1300" in t and "p1 1234" in t and "7300" not in t


def native_fixture(tmp_path, kn=2.0, kxn=None, write=True):
    """Run frame 100 (W) x 400 (H), y_end 300; native kn x. Returns (data, run_dir, native_dir)."""
    from PIL import Image
    kxn = kxn or kn
    run, nat = tmp_path / "run", tmp_path / "nat"
    (run / "pages").mkdir(parents=True)
    nat.mkdir()
    Image.fromarray(np.full((400, 100), 255, np.uint8)).save(run / "pages" / "p1.png")
    if write:
        Image.fromarray(np.full((round(400 * kn), round(100 * kxn)), 255, np.uint8)).save(nat / "p1.png")
    page = {"geometry": {"xdiv": 50}, "strip_fracs": [{"y0": 100, "y1": 200, "frac": [0.0]}],
            "split": {"strips": [], "half_w": 5, "pad": 2, "slope": 0.0, "c0": 50.0, "y_range": [0, 300]}}
    return {"pages": {"1": page}}, run, nat


def test_native_crop_shape_and_mag_tick(tmp_path):
    from PIL import Image
    for kn in (2.0, 1.4):
        d = tmp_path / str(kn)
        data, run, nat = native_fixture(d, kn)
        out = d / "out"
        out.mkdir()
        made = ss.strip(run, data, 1, 100, "p1-foot.png", out, nat, "foot")
        assert [m["file"] for m in made] == ["p1-foot.png", "p1-foot-native.png"]
        im = np.asarray(Image.open(out / "p1-foot-native.png"))
        hn, wn = round(400 * kn), round(100 * kn)
        r0, r1 = math.floor(100 * kn), min(hn - 1, math.ceil(400 * kn) - 1)
        assert im.shape == (r1 - r0 + 1, wn)  # grey; xdiv 50 +-300 covers all columns
        assert (im == 255).all()  # no overlay in the pixels
        assert made[1]["rows"] == [r0, r1] and made[1]["cols"] == [0, wn - 1]
        ye = round(300 * kn) - r0  # magenta y_end tick, centre row
        mag = [o for o in made[1]["overlay"] if o["colour"] == ss.MAGENTA]
        assert [(o["x"], o["y"], o["w"], o["h"]) for o in mag] == [(0, ye - 1, 20, 3), (wn - 20, ye - 1, 20, 3)]
        assert made[1]["sha256"] == ss.sha256(out / "p1-foot-native.png")


def test_strip_is_raw_page_pixels(tmp_path):
    """Ruling on report 6: no threshold in what the signer sees; every grey level survives."""
    from PIL import Image
    data, run, nat = native_fixture(tmp_path)
    page = (np.arange(400 * 100) % 256).astype(np.uint8).reshape(400, 100)
    Image.fromarray(page).save(run / "pages" / "p1.png")
    out = tmp_path / "out"
    out.mkdir()
    made = ss.strip(run, data, 1, 100, "p1-foot.png", out)
    im = np.asarray(Image.open(out / "p1-foot.png"))
    assert np.array_equal(im, page[100:, 0:100]) and len(np.unique(im)) == 256
    assert made[0]["overlay"] and all(set(o) == {"x", "y", "w", "h", "colour", "what"} for o in made[0]["overlay"])


def test_page_record_from_run():
    d = run_json(3)
    d["pages"]["1"]["split"] = {"y_range": [0, 1234], "strips": [{"y_mid": 850.0}]}
    r = ss.page_record(d["pages"]["1"])
    assert r["ticks"] == [700, 1000, 1300] and r["y_end"] == 1234 and r["foot_y0"] == 700
    assert r["last_strip"] == [1300, 1600] and [e["y0"] for e in r["empty_strips"]] == [1000, 1300]


def test_native_readme_line(tmp_path):
    data, run, nat = native_fixture(tmp_path)
    out = tmp_path / "out"
    out.mkdir()
    made = ss.strip(run, data, 1, 100, "p1-foot.png", out, nat)
    ss.write_readme(out, made, data)
    t = (out / "README.txt").read_text()
    assert "(native), maps run rows 100..399 x k=2.0000, native line height not measured here" in t
    assert "line height n/a" in t


def test_native_aspect_mismatch_fails(tmp_path):
    data, run, nat = native_fixture(tmp_path, 2.0, 2.02)
    with pytest.raises(ss.Fail):
        ss.strip(run, data, 1, 100, "p1-foot.png", tmp_path, nat)


def test_native_missing_page_fails(tmp_path):
    data, run, nat = native_fixture(tmp_path, write=False)
    with pytest.raises(ss.Fail):
        ss.strip(run, data, 1, 100, "p1-foot.png", tmp_path, nat)


def test_no_native_no_native_file(tmp_path):
    data, run, nat = native_fixture(tmp_path)
    out = tmp_path / "out"
    out.mkdir()
    made = ss.strip(run, data, 1, 100, "p1-foot.png", out)
    assert len(made) == 1 and [p.name for p in out.iterdir()] == ["p1-foot.png"]


def test_signing_uses_shared_git_state():
    import column_rule as C
    assert ss.git_state is C.git_state and ss.clean_run is C.clean_run and ss.REPO == C.REPO
