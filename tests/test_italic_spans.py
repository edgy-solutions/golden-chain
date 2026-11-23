"""tools/italic_spans.py on synthetic words only; plus the real hand-minted counts."""

import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import italic_spans as S  # noqa: E402
from column_rule import Fail  # noqa: E402


def mk(tmp_path, regions, name="run"):
    """regions: {(page, region): [(text, state)]}; state S slanted U upright A abstain N unmeasured."""
    words, rows = [], []
    for (page, region), ws in regions.items():
        for i, (text, st) in enumerate(ws):
            key = f"p{page}.{region}.{i}"
            words.append({"key": key, "page": page, "region": region, "block": 1, "par": 1,
                          "line": i // 5, "word": i % 5, "text": text})
            if st == "N":
                continue
            rows.append({"key": key, "page": page, "region": region, "slant": 0.0,
                         "slanted": {"S": True, "U": False, "A": None}[st],
                         "abstain": "x" if st == "A" else None, "box": [0, 0, 1, 1]})
    d = tmp_path / name
    (d / "ocr").mkdir(parents=True)
    (d / "slant").mkdir()
    (d / "ocr" / "ocr.json").write_text(json.dumps({"header": {}, "summary": {}, "words": words}))
    sha = hashlib.sha256((d / "ocr" / "ocr.json").read_bytes()).hexdigest()
    (d / "slant" / "slant.json").write_text(json.dumps({"rows": rows, "input": {"ocr_json_sha256": sha}}))
    return d / "ocr", d / "slant"


def run(tmp_path, regions, name="run"):
    o, s = mk(tmp_path, regions, name)
    ocr, slant, _, _ = S.load(o, s)
    return S.build(ocr, slant)


def seq(spec):
    return [("w", c) for c in spec.split()]


def test_bridging_unmeasured(tmp_path):
    spans, *_ = run(tmp_path, {(1, "left"): seq("U S N N S U")})
    assert len(spans) == 1 and spans[0]["n_words"] == 4 and spans[0]["n_bridged"] == 2


def test_trims_leading_trailing_unmeasured(tmp_path):
    spans, *_ = run(tmp_path, {(1, "left"): seq("U N S N")})
    assert spans[0]["n_words"] == 1 and spans[0]["first_key"] == "p1.left.2" == spans[0]["last_key"]


def test_upright_ends_span(tmp_path):
    spans, *_ = run(tmp_path, {(1, "left"): seq("S S U S")})
    assert [s["n_words"] for s in spans] == [2, 1]


def test_abstain_ends_span(tmp_path):
    spans, *_ = run(tmp_path, {(1, "left"): seq("S A S")})
    assert len(spans) == 2


def test_no_span_crosses_region_or_page(tmp_path):
    spans, *_ = run(tmp_path, {(1, "left"): seq("S S"), (1, "right"): seq("S S"),
                               (2, "left"): seq("S")})
    assert len(spans) == 3


def test_edge_flag(tmp_path):
    spans, _r, by_page, _t = run(tmp_path, {(1, "left"): seq("S U U S U U S")})
    assert [s["edge"] for s in spans] == [True, False, True]
    assert by_page["1"]["edge_spans"] == 2


def test_book_reference():
    assert S.find_refs(["Rom.", "vi.", "4,"]) == [(0, 2, "book")]
    assert S.find_refs(["x", "1", "Cor.", "xi.", "26"]) == [(1, 4, "book")]


def test_continuation_within_6():
    t = ["Rom.", "vi.", "4,", "a", "b", "c", "d", "e", "xi.", "26"]
    assert [r[2] for r in S.find_refs(t)] == ["book", "continuation"]
    t = ["Rom.", "vi.", "4,", "a", "b", "c", "d", "e", "f", "xi.", "26"]
    assert [r[2] for r in S.find_refs(t)] == ["book"]


def test_continuation_needs_previous_ref():
    assert S.find_refs(["xi.", "26"]) == []


def test_ver_counted_not_ref(tmp_path):
    ws = [("ver.", "U"), ("4", "U"), ("Ver", "U"), ("ver", "U")]
    _s, refs, by_page, _t = run(tmp_path, {(1, "left"): ws})
    assert refs == [] and by_page["1"]["ver_forms"] == 2


def ref_words(gap):
    return [("w", "S")] + [("w", "U")] * gap + [("Rom.", "U"), ("vi.", "U"), ("4", "U")]


def test_pairing_within_8(tmp_path):
    spans, _r, by_page, _t = run(tmp_path, {(1, "left"): ref_words(8)})
    assert spans[0]["paired_ref_key"] == "p1.left.9" and by_page["1"]["paired"] == 1


def test_no_pairing_beyond_8(tmp_path):
    spans, _r, by_page, _t = run(tmp_path, {(1, "left"): ref_words(9)})
    assert spans[0]["paired_ref_key"] is None and by_page["1"]["unpaired"] == 1


def test_no_pairing_past_next_span(tmp_path):
    ws = [("w", "S"), ("w", "U"), ("w", "S"), ("Rom.", "U"), ("vi.", "U"), ("4", "U")]
    spans, *_ = run(tmp_path, {(1, "left"): ws})
    assert spans[0]["paired_ref_key"] is None and spans[1]["paired_ref_key"] == "p1.left.3"


def test_one_span_per_reference():
    assert S.pair([(0, 0), (2, 2)], [(3, 5, "book")]) == [None, 0]
    assert S.pair([(0, 0), (1, 1)], [(3, 5, "book")]) == [None, 0]


def test_sha_mismatch_fails(tmp_path):
    o, s = mk(tmp_path, {(1, "left"): seq("S")})
    (o / "ocr.json").write_text((o / "ocr.json").read_text() + " ")
    with pytest.raises(Fail):
        S.main(o, s, tmp_path / "out")


def test_nonempty_outdir_fails(tmp_path):
    o, s = mk(tmp_path, {(1, "left"): seq("S")})
    out = tmp_path / "out"
    out.mkdir()
    (out / "f").write_text("x")
    with pytest.raises(Fail):
        S.main(o, s, out)


def test_byte_identical_reruns(tmp_path):
    o, s = mk(tmp_path, {(1, "left"): ref_words(2), (1, "right"): seq("S U S")})
    S.main(o, s, tmp_path / "a")
    S.main(o, s, tmp_path / "b")
    for f in ("spans.json", "summary.json"):
        assert (tmp_path / "a" / f).read_bytes() == (tmp_path / "b" / f).read_bytes()
    assert (tmp_path / "a" / "run_header.json").is_file()


def test_hand_minted_real_counts():
    hm = S.hand_minted()
    assert hm == {"897": 5, "898": 20, "899": 4, "900": 7, "910": 5, "911": 6, "914": 9}
    assert sum(hm.values()) == 56
