import json
import random
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import truthset_crops as tc  # noqa: E402
import truthset_v2  # noqa: E402
from column_rule import Fail  # noqa: E402

CLEAN = {"commit": "abc123", "dirty": False, "porcelain": 0}
PW, PH = 200, 300


def make_words(pages=(912, 914)):
    words = []
    for p in pages:
        for line in range(6):
            for w in range(5):
                x0, y0 = 10 + w * 30, 20 + line * 20
                words.append({"key": f"{p}/left/1.1.{line}.{w}", "page": p, "region": "left",
                              "bbox": [x0, y0, x0 + 25, y0 + 12], "text": "SECRETWORD"})
    return words


def fabricated(tmp_path, monkeypatch):
    words = make_words()
    slant_rows = []
    for i, w in enumerate(words):
        m = i % 10
        if m < 3:
            r = {"abstain": "edge", "slanted": None, "slant": None}
        elif m < 6:
            r = {"abstain": None, "slanted": True, "slant": 0.25}
        else:
            r = {"abstain": None, "slanted": False, "slant": 0.02}
        slant_rows.append({"key": w["key"], "page": w["page"], "region": "left", **r})
    rows = truthset_v2.draw(slant_rows, {w["key"]: w["bbox"] for w in words})
    assert rows
    ts, od, ad = tmp_path / "ts", tmp_path / "ocr", tmp_path / "align"
    for d in (ts, od / "pages", od / "regions", ad):
        d.mkdir(parents=True)
    (ts / "candidates.json").write_text(json.dumps({"summary": {}, "rows": rows}), encoding="utf-8")
    rng = np.random.default_rng(7)
    for p in (912, 914):
        Image.fromarray(rng.integers(0, 255, (PH, PW), dtype=np.uint8), "L").save(od / "pages" / f"p{p}.png")
        Image.fromarray(rng.integers(0, 255, (250, PW), dtype=np.uint8), "L").save(od / "regions" / f"p{p}-left.png")
    (od / "ocr.json").write_text(json.dumps({"header": {"splits": {"912": {"ytop": 20}, "914": {"ytop": 20}}},
                                             "words": words}), encoding="utf-8")
    (ad / "align.json").write_text(json.dumps({"report": {"moved_blocks": [
        {"page": 914, "first_key": "914/left/1.1.2.0", "last_key": "914/left/1.1.4.4"}]}}), encoding="utf-8")
    monkeypatch.setattr(tc, "EXPECTED_DIGEST", truthset_v2.digest(rows))
    monkeypatch.setattr(tc, "git_state", lambda repo: dict(CLEAN))
    return ts, od, ad, rows


def test_order_is_input_order_free_and_not_by_page():
    rows = [{"key": f"{p}/left/1.1.{i}.0", "page": p} for p in (912, 913, 914, 915) for i in range(6)]
    a = tc.order(rows)
    shuffled = rows[:]
    random.Random(3).shuffle(shuffled)
    assert tc.order(shuffled) == a
    pages = [r["page"] for r in a]
    assert pages != sorted(pages)


def test_line_key():
    assert tc.line_key("914/left/1.2.3.4") == "914/left/1.2.3"


def test_line_bbox_union_pad_and_clip():
    words = [{"key": "9/left/1.1.1.0", "bbox": [5, 40, 20, 50]}, {"key": "9/left/1.1.1.1", "bbox": [30, 38, 60, 52]},
             {"key": "9/left/1.1.2.0", "bbox": [0, 100, 90, 110]}]
    assert tc.line_bbox(words, "9/left/1.1.1.1", (100, 300)) == [0, 26, 72, 64]  # x0 5-12 clipped to 0
    assert tc.line_bbox(words, "9/left/1.1.2.0", (100, 112)) == [0, 88, 100, 112]  # right and bottom clipped
    with pytest.raises(Fail):
        tc.line_bbox(words, "9/left/9.9.9.9", (100, 300))


def test_word_crop_size_equals_bbox_size_and_is_exact():
    img = np.arange(60 * 80, dtype=np.uint8).reshape(60, 80)
    c = tc.word_crop(img, [10, 20, 35, 33])
    assert c.shape == (13, 25) and np.array_equal(c, img[20:33, 10:35])


def test_box_in_line_and_line_crop():
    lb = [7, 30, 90, 60]
    assert tc.box_in_line([20, 38, 45, 50], lb) == [13, 8, 38, 20]
    img = np.zeros((100, 100), np.uint8)
    assert tc.line_crop(img, lb).shape == (30, 83)


def test_foot_box_region_coordinates():
    words = make_words((914,))
    moved = [{"page": 914, "first_key": "914/left/1.1.2.0", "last_key": "914/left/1.1.4.4"},
             {"page": 913, "first_key": "913/left/x.0.0.0", "last_key": "913/left/x.0.0.1"}]
    assert tc.foot_box(words, moved, ytop=20, region_wh=(200, 250)) == [0, 10, 200, 250]
    assert tc.foot_box(words, moved, ytop=0, region_wh=(200, 250))[1] == 30
    assert tc.foot_box(words, moved, ytop=70, region_wh=(200, 250))[1] == 0  # clipped at 0
    with pytest.raises(Fail):
        tc.foot_box(words, [{"page": 913, "first_key": "a", "last_key": "b"}], ytop=0, region_wh=(1, 1))
    with pytest.raises(Fail):
        tc.foot_box(words, [{"page": 914, "first_key": "nope", "last_key": "914/left/1.1.4.4"}], region_wh=(1, 1))


def test_end_to_end_deterministic_and_blind(tmp_path, monkeypatch):
    ts, od, ad, rows = fabricated(tmp_path, monkeypatch)
    o1, o2 = tmp_path / "o1", tmp_path / "o2"
    assert tc.main(ts, od, ad, o1) == 0
    assert tc.main(ts, od, ad, o2) == 0
    assert (o1 / "crops.json").read_bytes() == (o2 / "crops.json").read_bytes()
    assert (o1 / "README.txt").read_text(encoding="utf-8").startswith("LOCAL ONLY")
    assert (o1 / "run_header.json").is_file()
    raw = (o1 / "crops.json").read_text(encoding="utf-8")
    for bad in ("stratum", "slant", "text", "SECRETWORD", "italic"):
        assert bad not in raw
    doc = json.loads(raw)
    n = len(rows)
    assert len(doc["rows"]) == n and doc["rows"][0]["id"] == "w001" and doc["rows"][-1]["id"] == f"w{n:03d}"
    assert [r["key"] for r in doc["rows"]] == [r["key"] for r in tc.order(rows)]
    assert len(list(o1.glob("*.png"))) == 2 * n + 2
    r0 = doc["rows"][0]
    page = np.asarray(Image.open(od / "pages" / f"p{r0['page']}.png"))
    wb = next(r for r in rows if r["key"] == r0["key"])["bbox"]
    assert np.array_equal(np.asarray(Image.open(o1 / r0["word_png"])), page[wb[1]:wb[3], wb[0]:wb[2]])
    assert r0["word_size"] == [wb[2] - wb[0], wb[3] - wb[1]]
    assert doc["extra"]["p914_left_foot"]["box_region"] == [0, 10, PW, 250]
    foot = np.asarray(Image.open(o1 / "p914_left_foot.png"))
    assert foot.shape == (240, PW)
    assert np.array_equal(np.asarray(Image.open(o1 / "p912_left.png")),
                          np.asarray(Image.open(od / "regions" / "p912-left.png")))


def test_main_fails_loud(tmp_path, monkeypatch):
    ts, od, ad, rows = fabricated(tmp_path, monkeypatch)
    monkeypatch.setattr(tc, "EXPECTED_DIGEST", "0" * 64)
    with pytest.raises(Fail):
        tc.main(ts, od, ad, tmp_path / "o")
    monkeypatch.setattr(tc, "EXPECTED_DIGEST", truthset_v2.digest(rows))
    (ad / "align.json").write_text(json.dumps({"report": {"moved_blocks": []}}), encoding="utf-8")
    with pytest.raises(Fail):
        tc.main(ts, od, ad, tmp_path / "o")
    (od / "ocr.json").unlink()
    with pytest.raises(Fail):
        tc.main(ts, od, ad, tmp_path / "o")
