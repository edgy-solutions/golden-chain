"""The italic-spans console (LOCK_italic_console_2026-11-26): draw, bands, crops, spec builder, kind. Synthetic only."""

import hashlib
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
import build  # noqa: E402
import ingest  # noqa: E402
import italic_span_crops as IC  # noqa: E402
from column_rule import Fail  # noqa: E402

SENT = "ZQXSENTINEL"
CLEAN = {"commit": "abc123", "dirty": False, "porcelain": 0}
W, H = 400, 600
LINE_H, GAP, TOP0 = 14, 12, 20  # lines every 26 px
N_LINES = 20


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def line_y(i):
    return TOP0 + i * (LINE_H + GAP)


def mk_words(pages, regions=("left",), n_lines=N_LINES, words_per_line=4):
    """Synthetic OCR words: key p<page>.<region>.<line>.<word>, region-wide lines, sentinel text on every word."""
    out = []
    for p in pages:
        for ri, r in enumerate(regions):
            for ln in range(n_lines):
                for wd in range(words_per_line):
                    x0 = 20 + ri * 190 + wd * 40
                    out.append({"key": f"{p}.{r}.1.1.{ln}.{wd}", "page": p, "region": r, "block": 1, "par": 1,
                                "line": ln, "word": wd, "text": SENT,
                                "bbox": [x0, line_y(ln), x0 + 34, line_y(ln) + LINE_H]})
    return out


def key(p, r, ln, wd):
    return f"{p}.{r}.1.1.{ln}.{wd}"


def span(p, ln, wd0=0, wd1=1, ln1=None, region="left", paired=False):
    ln1 = ln if ln1 is None else ln1
    return {"page": p, "region": region, "first_key": key(p, region, ln, wd0), "last_key": key(p, region, ln1, wd1),
            "n_words": 2, "n_slanted": 2, "n_bridged": 0, "edge": False,
            "paired_ref_key": key(p, region, ln1, 3) if paired else None}


def write_world(root, spans, pages, words=None, sha_override=None):
    root = Path(root)
    od, sd = root / "ocr", root / "spans"
    (od / "pages").mkdir(parents=True)
    sd.mkdir(parents=True)
    words = mk_words(pages) if words is None else words
    (od / "ocr.json").write_text(json.dumps({"words": words}), encoding="utf-8")
    rng = np.random.default_rng(3)
    for p in pages:
        arr = (rng.random((H, W)) * 255).astype(np.uint8)
        Image.fromarray(arr).save(od / "pages" / f"p{p}.png")
    s = {"input": {"ocr_json_sha256": sha_override or sha(od / "ocr.json"), "slant_json_sha256": "0" * 64},
         "params": {}, "refs": [], "spans": spans}
    (sd / "spans.json").write_text(json.dumps(s), encoding="utf-8")
    return sd, od


def standard_spans(pages=(1, 2, 3, 4, 5)):
    """Per page: 5 paired and 5 unpaired spans, on distinct lines (lines 3, 5, 7, ... for unpaired, 4, 6, ... paired)."""
    out = []
    for p in pages:
        for j in range(5):
            out.append(span(p, 3 + 2 * j, paired=False))
            out.append(span(p, 4 + 2 * j, paired=True))
    return out


@pytest.fixture(autouse=True)
def clean_git(monkeypatch):
    monkeypatch.setattr(IC, "git_state", lambda repo: dict(CLEAN))


def run(tmp_path, name="a", spans=None, pages=(1, 2, 3, 4, 5), **kw):
    sd, od = write_world(tmp_path / f"w_{name}", standard_spans() if spans is None else spans, pages, **kw)
    out = tmp_path / f"out_{name}"
    IC.main(sd, od, out)
    return out, sd, od


def region_keys_of(words):
    import italic_spans as isp
    return {(p, r): [w["key"] for w in ws] for p, r, ws, _s in isp.region_lists({"words": words}, {"rows": []})}


# ---- the draw ------------------------------------------------------------------------------------------

def test_draw_round_robin_order_and_counts():
    pages = (1, 2, 3, 4, 5)
    sp = standard_spans(pages)
    paired, unpaired = IC.draw(sp, region_keys_of(mk_words(pages)))
    assert len(paired) == len(unpaired) == 20
    assert all(s["paired_ref_key"] is not None for s in paired)
    assert all(s["paired_ref_key"] is None for s in unpaired)
    # round 0 takes each page's first span in page order, round 1 each page's second, and so on
    assert [s["page"] for s in unpaired[:10]] == [1, 2, 3, 4, 5, 1, 2, 3, 4, 5]
    assert [s["first_key"] for s in unpaired[:5]] == [key(p, "left", 3, 0) for p in pages]
    assert [s["first_key"] for s in unpaired[5:10]] == [key(p, "left", 5, 0) for p in pages]
    assert {s["page"] for s in paired} == set(pages)


def test_draw_takes_left_column_before_right_and_reading_order():
    words = mk_words((1,), regions=("left", "right"))
    sp = [span(1, 9, region="right"), span(1, 8), span(1, 2), span(1, 12, region="right")]
    sp = [dict(s, paired_ref_key=None) for s in sp]
    got = IC.sort_spans(sp, region_keys_of(words))
    assert [(s["region"], s["first_key"].split(".")[4]) for s in got] == [("left", "2"), ("left", "8"),
                                                                         ("right", "9"), ("right", "12")]


def test_draw_uneven_pages_continue_round_robin():
    sp = [span(1, 3 + j) for j in range(8)] + [span(2, 3 + j) for j in range(2)] + [span(3, 3)]
    keys = region_keys_of(mk_words((1, 2, 3)))
    got = IC.round_robin(IC.sort_spans(sp, keys), 8)
    assert [s["page"] for s in got] == [1, 2, 3, 1, 2, 1, 1, 1]


def test_draw_fails_when_a_group_is_short():
    pages = (1, 2, 3, 4)
    sp = standard_spans(pages)
    keys = region_keys_of(mk_words(pages))
    paired_short = [s for s in sp if s["paired_ref_key"] is None] + \
                   [s for s in sp if s["paired_ref_key"] is not None][:19]
    with pytest.raises(Fail):
        IC.draw(paired_short, keys)
    unpaired_short = [s for s in sp if s["paired_ref_key"] is not None] + \
                     [s for s in sp if s["paired_ref_key"] is None][:19]
    with pytest.raises(Fail):
        IC.draw(unpaired_short, keys)


# ---- bands ---------------------------------------------------------------------------------------------

def band_of(sp, pages=(1,)):
    words = mk_words(pages)
    from truthset_crops_v4 import line_boxes
    ordered = {(p, r): ws for p, r, ws, _s in __import__("italic_spans").region_lists({"words": words},
                                                                                        {"rows": []})}
    return IC.band(sp, ordered[(sp["page"], sp["region"])], line_boxes(words), (W, H))


def test_band_two_lines_either_side():
    x0, top, x1, bottom, boxes, n, short = band_of(span(1, 8))
    assert (n, short) == (5, False) and len(boxes) == 1
    assert top <= line_y(6) and bottom >= line_y(10) + LINE_H
    assert top > line_y(5) + LINE_H - 1 and bottom <= line_y(11)  # clipped between the neighbouring lines


def test_band_short_at_top_and_bottom_of_column():
    *_, n, short = band_of(span(1, 0))
    assert (n, short) == (3, True)
    *_, n, short = band_of(span(1, 1))
    assert (n, short) == (4, True)
    *_, n, short = band_of(span(1, N_LINES - 1))
    assert (n, short) == (3, True)
    *_, n, short = band_of(span(1, N_LINES - 2))
    assert (n, short) == (4, True)
    *_, n, short = band_of(span(1, 2))
    assert (n, short) == (5, False)
    *_, n, short = band_of(span(1, N_LINES - 3))
    assert (n, short) == (5, False)


def test_band_span_over_two_lines_is_six_lines_and_two_boxes():
    x0, top, x1, bottom, boxes, n, short = band_of(span(1, 8, wd0=2, wd1=1, ln1=9))
    assert (n, short) == (6, False) and len(boxes) == 2
    assert boxes[0][1] < boxes[1][1]
    x0, top, x1, bottom, boxes, n, short = band_of(span(1, 0, wd0=2, wd1=1, ln1=1))
    assert (n, short) == (4, True) and len(boxes) == 2


def test_band_is_full_column_width():
    x0, top, x1, bottom, boxes, *_ = band_of(span(1, 8))
    assert (x0, x1) == (20, 20 + 3 * 40 + 34)


def test_boxes_lie_inside_the_crop(tmp_path):
    out, *_ = run(tmp_path)
    rows = json.loads((out / "crops.json").read_text())["rows"]
    assert len(rows) == 40
    for r in rows:
        w, h = Image.open(out / r["png"]).size
        assert r["boxes"]
        for b in r["boxes"]:
            assert b["w"] > 0 and b["h"] > 0
            assert 0 <= b["x"] and 0 <= b["y"] and b["x"] + b["w"] <= w and b["y"] + b["h"] <= h


# ---- outputs -------------------------------------------------------------------------------------------

def test_outputs_ids_shape_and_no_pairing(tmp_path):
    out, *_ = run(tmp_path)
    doc = json.loads((out / "crops.json").read_text())
    assert [r["id"] for r in doc["rows"]] == [f"s{i:02d}" for i in range(1, 41)]
    assert doc["params"] == {"draw": "round-robin by page, 20 paired + 20 unpaired", "context_lines": 2}
    assert set(doc["input"]) == {"spans.json", "ocr.json"} | {f"pages/p{p}.png" for p in range(1, 6)}
    for r in doc["rows"]:
        assert set(r) == {"id", "key", "last_key", "page", "region", "png", "sha256", "boxes", "n_lines", "short"}
        assert r["sha256"] == sha(out / r["png"])
    dj = json.loads((out / "draw.json").read_text())
    assert sorted(r["group"] for r in dj["rows"]).count("paired") == 20
    assert {r["id"] for r in dj["rows"]} == {r["id"] for r in doc["rows"]}
    assert (out / "run_header.json").is_file() and (out / "README.txt").read_text().startswith("LOCAL ONLY")


def test_sentinel_absent_from_every_output(tmp_path):
    out, *_ = run(tmp_path)
    spec_mod = load_spec_module()
    spec = spec_mod.make_spec(out)
    spec_p = tmp_path / "spec.json"
    build.write_spec(spec_p, spec)
    site = tmp_path / "site"
    build.build(spec_p, site)
    texts = [(out / n).read_text() for n in ("crops.json", "draw.json", "run_header.json", "README.txt")]
    texts.append(spec_p.read_text())
    for f in site.rglob("*"):
        if f.is_file() and f.suffix in (".html", ".json", ".txt", ".md"):
            texts.append(f.read_text(encoding="utf-8", errors="replace"))
    assert len(texts) > 5 and not any(SENT in t for t in texts)


def test_reruns_are_byte_identical(tmp_path):
    a, *_ = run(tmp_path, "a")
    b, *_ = run(tmp_path, "b")
    for n in ("crops.json", "draw.json"):
        assert (a / n).read_bytes() == (b / n).read_bytes()
    pa = sorted(p.name for p in a.glob("s*.png"))
    assert pa == sorted(p.name for p in b.glob("s*.png")) and len(pa) == 40
    assert [sha(a / n) for n in pa] == [sha(b / n) for n in pa]


def test_sha_mismatch_fails(tmp_path):
    sd, od = write_world(tmp_path / "w", standard_spans(), (1, 2, 3, 4, 5), sha_override="0" * 64)
    with pytest.raises(Fail):
        IC.main(sd, od, tmp_path / "out")


def test_nonempty_out_dir_fails_and_empty_is_fine(tmp_path):
    sd, od = write_world(tmp_path / "w", standard_spans(), (1, 2, 3, 4, 5))
    full = tmp_path / "full"
    full.mkdir()
    (full / "x").write_text("x")
    with pytest.raises(Fail):
        IC.main(sd, od, full)
    empty = tmp_path / "empty"
    empty.mkdir()
    IC.main(sd, od, empty)
    assert (empty / "crops.json").is_file()


def test_missing_files_fail(tmp_path):
    sd, od = write_world(tmp_path / "w", standard_spans(), (1, 2, 3, 4, 5))
    (od / "pages" / "p3.png").unlink()
    with pytest.raises(Fail):
        IC.main(sd, od, tmp_path / "o1")
    (sd / "spans.json").unlink()
    with pytest.raises(Fail):
        IC.main(sd, od, tmp_path / "o2")


# ---- the spec builder and the kind ---------------------------------------------------------------------

def load_spec_module():
    s = importlib.util.spec_from_file_location("italic_spans_spec", ROOT / "tools" / "console" / "specs" /
                                               "italic_spans.py")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def test_spec_shape_and_builds(tmp_path):
    out, *_ = run(tmp_path)
    m = load_spec_module()
    spec = m.make_spec(out)
    build.check_spec(spec)
    assert spec["kind"] == "italic-spans" and spec["signer"] == "Chris"
    rows = spec["sections"][0]["rows"]
    assert len(rows) == 40 and rows[0]["label"].startswith("s01 · p. ")
    v = rows[0]["fields"][0]
    assert v["id"] == "v" and v["options"] == m.OPTIONS and len(v["options"]) == 7
    assert v["options"][0] == "a Scripture quotation, with its reference after it"
    assert set(spec["keyboard"]["keys"]) == set("abcdefgo") and spec["keyboard"]["keys"]["o"] == build.OTHER
    build.check_keyboard(spec)
    assert "paired" not in json.dumps(spec)


@pytest.mark.parametrize("bad", ["paired", "paired_ref_key", "ref"])
def test_spec_builder_fails_on_a_pairing_key(tmp_path, bad):
    out, *_ = run(tmp_path)
    doc = json.loads((out / "crops.json").read_text())
    doc["rows"][0][bad] = "x"
    (out / "crops.json").write_text(json.dumps(doc))
    with pytest.raises(Fail):
        load_spec_module().make_spec(out)


def test_spec_builder_fails_on_a_changed_png(tmp_path):
    out, *_ = run(tmp_path)
    (out / "s01.png").write_bytes((out / "s02.png").read_bytes())
    with pytest.raises(Fail):
        load_spec_module().make_spec(out)


def test_kind_accepted_and_in_ingest():
    assert "italic-spans" in ingest.KINDS and "italic-spans" in build.KINDS
