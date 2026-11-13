"""tools/gy_ocr_baptism.py on synthetic data only: regions, parsers, matching, CCEL flags, candidates."""

import sys
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("PIL")
pytest.importorskip("pypdfium2")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import gy_ocr_baptism as O  # noqa: E402
from column_rule import Fail  # noqa: E402


def test_regions():
    grey = np.zeros((300, 400), dtype=np.uint8)  # all ink
    split = {"strips": [{"y_mid": 100}, {"y_mid": 200}]}
    rs = {r["name"]: r for r in O.regions(grey, split, 40, lambda s, y: 140, lambda s, y: 160)}
    assert list(rs) == ["head", "left", "right", "foot"]
    assert rs["head"]["image"].shape == (80, 400) and rs["head"]["y_off"] == 0
    assert rs["foot"]["image"].shape == (80, 400) and rs["foot"]["y_off"] == 220
    left = rs["left"]
    assert left["y_off"] == 80 and left["image"].shape == (140, 141)
    assert (left["image"][:, :140] == 0).all() and (left["image"][:, 140] == 255).all()
    right = rs["right"]
    assert right["x_off"] == 160 and right["image"].shape == (140, 240)
    assert (right["image"][:, 0] == 255).all() and (right["image"][:, 1:] == 0).all()


def test_regions_skips_blank():
    grey = np.full((300, 400), 255, dtype=np.uint8)
    split = {"strips": [{"y_mid": 100}, {"y_mid": 200}]}
    assert O.regions(grey, split, 40, lambda s, y: 140, lambda s, y: 160) == []


def test_parse_tsv():
    t = ("level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext\n"
         "4\t1\t1\t1\t1\t0\t0\t0\t9\t9\t-1\t\n"
         "5\t1\t1\t2\t3\t4\t10\t20\t30\t40\t91.5\talpha\n"
         "5\t1\t1\t2\t3\t5\t50\t20\t30\t40\t80\t  \n")
    w = O.parse_tsv(t)
    assert len(w) == 1
    assert (w[0]["block"], w[0]["par"], w[0]["line"], w[0]["word"]) == (1, 2, 3, 4)
    assert w[0]["conf"] == 91.5 and w[0]["bbox"] == [10, 20, 40, 60] and w[0]["text"] == "alpha"


def test_parse_hocr():
    h = ("<span class='ocrx_word' id='w1' title='bbox 1 2 30 40; x_wconf 90'><em>beta</em></span>"
         "<span class='ocrx_word' id='w2' title='bbox 50 2 80 40; x_font Foo-Italic; x_fsize 9'>gam&amp;ma</span>"
         "<span class='ocrx_word' id='w3' title='bbox 90 2 99 40; x_font Foo; x_fsize 9'>delta</span>")
    w = O.parse_hocr(h)
    assert [x["text"] for x in w] == ["beta", "gam&ma", "delta"]
    assert [x["italic"] for x in w] == [True, True, False]
    assert w[0]["bbox"] == [1, 2, 30, 40]


def test_match_threshold():
    lstm = [{"text": "a", "bbox": [0, 0, 10, 10]}]
    hit = [{"text": "b", "bbox": [0, 0, 10, 20], "italic": True}]  # IoU exactly 0.5
    miss = [{"text": "b", "bbox": [0, 0, 10, 21], "italic": True}]
    assert O.match(lstm, hit)[0]["italic"] is True
    assert O.match(lstm, hit)[0]["legacy_text"] == "b"
    m = O.match(lstm, miss)[0]
    assert m["italic"] is None and m["legacy_text"] is None
    assert O.match(lstm, [])[0]["italic"] is None


def test_ccel_flags():
    assert O.ccel_flags(["One,", "two", "x", "four"], ["one", "two", "three", "four"]) == \
        ["agree", "agree", "differ", "agree"]
    assert O.ccel_flags(["a", "b", "c"], ["a", "c"]) == ["agree", "unaligned", "agree"]
    assert O.ccel_flags(["a", "--", "b"], ["a", "b"]) == ["agree", None, "agree"]


def words(n_true, n_false):
    out = []
    for i in range(n_true + n_false):
        out.append({"key": f"1/left/1.1.1.{i}", "page": 1, "region": "left", "bbox": [0, 0, 1, 1],
                    "text": f"w{i}", "italic": i < n_true, "ccel": "agree"})
    return out


def test_candidates():
    ws = words(5, 6)
    a = O.candidates(ws, 3)
    assert a == O.candidates(list(reversed(ws)), 3)
    assert [r["stratum"] for r in a] == ["flagged"] * 3 + ["unflagged"] * 3
    assert all(r["signed_italic"] is None for r in a)
    with pytest.raises(Fail):
        O.candidates(ws, 6)


@pytest.mark.skipif(not Path(O.TESSERACT).is_file(), reason="tesseract missing")
def test_lstm_runner(tmp_path):
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype("C:/Windows/Fonts/times.ttf", 60)
    img = Image.new("L", (600, 140), 255)
    ImageDraw.Draw(img).text((20, 30), "water baptism", font=font, fill=0)
    png = tmp_path / "t.png"
    img.save(png)
    tsv = O.run_lstm(png, tmp_path / "t.lstm")
    assert len(O.parse_tsv(tsv.read_text(encoding="utf-8"))) >= 1
