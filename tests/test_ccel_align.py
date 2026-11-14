"""tools/ccel_align.py on invented tokens only."""

import hashlib
import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("numpy")
pytest.importorskip("PIL")
pytest.importorskip("pypdfium2")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import ccel_align as C  # noqa: E402
from column_rule import Fail  # noqa: E402


def toks(prefix, n):
    return [f"{prefix}x{i}q" for i in range(n)]


def page(p, words):
    """words: list of tokens; every 10th ends a line; returns (page, [(key, text, line_end)])."""
    return (p, [(f"{p}/left/1.1.{i // 10}.{i}", t, (i % 10 == 9)) for i, t in enumerate(words)])


def test_cmp_norm():
    assert C.cmp_norm("Well-known,") == "wellknown"
    assert C.cmp_norm("--") == ""


def test_hyphen_join():
    assert C.hyphen_join(["bap-", "tism", "is"], [True, False, False]) == (["baptism", "is"], [0, 0, 1])
    j, o = C.hyphen_join(["co-", "operate"], [False, False])
    assert j == ["co-", "operate"] and o == [0, 1]
    assert C.hyphen_join(["-", "a"], [True, True])[0] == ["-", "a"]
    assert C.hyphen_join(["1-", "a"], [True, True])[0] == ["1-", "a"]
    assert C.hyphen_join(["a", "end-"], [False, True])[0] == ["a", "end-"]
    # no chaining: the second half's own hyphen is ignored
    j, o = C.hyphen_join(["ab-", "cd-", "ef"], [True, True, False])
    assert j == ["abcd-", "ef"] and o == [0, 0, 1]


def test_align_in_order():
    assert C.align_in_order(["one", "two", "x", "four"], ["one", "two", "three", "four"]) == \
        [("agree", 0), ("agree", 1), ("differ", None), ("agree", 3)]
    assert C.align_in_order(["a", "b", "c"], ["a", "c"]) == \
        [("agree", 0), ("unaligned", None), ("agree", 1)]


def test_block_move():
    A, B, Cc = toks("a", 15), toks("b", 15), toks("c", 15)
    b = A + B + Cc
    a = A + Cc + B
    fl = [f for f, _j in C.align_in_order(a, b)]
    blocks = C.moved_blocks(a, fl, b)
    assert blocks and all(x["a_len"] >= C.MOVE_BLOCK for x in blocks)
    assert "moved" in fl and "unaligned" not in fl
    assert all(f in ("agree", "moved") for f in fl)


def test_page_windows():
    b = toks("m", 1000)
    p1, p2 = b[100:140], b[800:840]
    w = C.page_windows([(1, p1), (2, p2)], b)
    assert w[2][0] > w[1][1] - 2 * C.PAD
    assert w[1] == (0, 339)
    # sparse middle page takes neighbours' bounds
    mid = ["zz1", "zz2"]
    w = C.page_windows([(1, p1), (2, mid), (3, p2)], b)
    assert w[2] == (w[1][1] - C.PAD, w[3][0] + C.PAD)


def test_hyphen_across_columns():
    ccel = ["alpha sacrament beta gamma"]
    pg = (1, [("1/left/1.1.1.0", "alpha", False), ("1/left/1.1.1.1", "sacra-", True),
              ("1/right/1.1.1.0", "ment", False), ("1/right/1.1.1.1", "beta", False),
              ("1/right/1.1.1.2", "gamma", True)])
    flags, rep = C.align([pg], ccel)
    assert flags == ["agree"] * 5
    assert rep["hyphen_pairs"] == 1 and rep["hyphen_pairs_agree_or_moved"] == 1


def test_align_end_to_end():
    A, B, Cc = toks("a", 15), toks("b", 15), toks("c", 15)
    ccel_toks = A + B + Cc + toks("d", 10)
    ccel_toks[3] = "sacrament"
    ccel = [" ".join(ccel_toks)]
    p1 = A[:3] + ["sacra-", "ment"] + A[4:]
    pg1 = (1, [(f"1/left/1.1.{i}.0", t, t.endswith("-")) for i, t in enumerate(p1)])
    p2 = B + Cc
    pg2 = (2, [(f"2/left/1.1.{i}.0", t, False) for i, t in enumerate(p2)])
    p3 = toks("d", 10)
    pg3 = (3, [(f"3/left/1.1.{i}.0", t, False) for i, t in enumerate(p3)])
    flags, rep = C.align([pg1, pg2, pg3], ccel)
    assert rep["totals"]["column_words"] == 56
    assert rep["hyphen_pairs"] == 1 and rep["hyphen_pairs_agree_or_moved"] == 1
    assert rep["pages"]["1"]["agree"] == 16 and rep["pages"]["1"]["column_words"] == 16
    assert rep["pages"]["3"]["agree"] == 10
    assert rep["totals"]["differ"] == 0 and rep["totals"]["unaligned"] == 0
    assert flags[3] == flags[4] == "agree"


def test_align_end_to_end_moved():
    A, B, Cc = toks("a", 15), toks("b", 15), toks("c", 15)
    ccel = [" ".join(A + B + Cc)]
    pg = page(1, A + Cc + B)
    flags, rep = C.align([pg], ccel)
    t = rep["totals"]
    assert t["differ"] == 0 and t["unaligned"] == 0 and t["none"] == 0
    assert t["agree"] + t["moved"] == 45 and t["moved"] >= 15
    assert rep["moved_blocks"] and rep["moved_blocks"][0]["page"] == 1
    assert all("text" not in k for k in rep["moved_blocks"])


def fabricate(tmp_path):
    A, B, Cc = toks("a", 30), toks("b", 30), toks("c", 30)
    lines = ["pre1 pre2"] + [" ".join(A + B + Cc)] + ["post1"]
    ccel = tmp_path / "ccel.txt"
    ccel.write_text("\n".join(lines) + "\n", encoding="utf-8")
    words = []
    for i, t in enumerate(A + Cc + B):
        words.append({"key": f"1/{'left' if i < 45 else 'right'}/1.1.{i // 10}.{i}", "page": 1,
                      "region": "left" if i < 45 else "right", "block": 1, "par": 1, "line": i // 10,
                      "word": i, "text": t, "ccel": "agree" if i < 30 else "differ"})
    words.append({"key": "1/head/1.1.1.0", "page": 1, "region": "head", "block": 1, "par": 1,
                  "line": 1, "word": 0, "text": "headx", "ccel": None})
    run = tmp_path / "run"
    run.mkdir()
    (run / "ocr.json").write_text(json.dumps({"header": {}, "summary": {}, "words": words}), encoding="utf-8")
    return run, ccel


def test_runner(tmp_path):
    run, ccel = fabricate(tmp_path)
    sha = hashlib.sha256(ccel.read_bytes()).hexdigest()
    outs = []
    for n in (1, 2):
        out = tmp_path / f"out{n}"
        assert C.main(run, ccel, out, ccel_sha=sha, ccel_lines_range=(2, 2)) == 0
        outs.append(out)
    b1, b2 = ((o / "align.json").read_bytes() for o in outs)
    assert b1 == b2
    d = json.loads(b1)
    assert '"text"' not in b1.decode()
    assert "1/head/1.1.1.0" not in d["flags"]
    assert d["report"]["totals"]["column_words"] == 90
    assert d["report"]["totals"]["agree"] + d["report"]["totals"]["moved"] == 90
    assert d["input"]["ccel_lines"] == [2, 2]
    assert (outs[0] / "run_header.json").is_file() and (outs[0] / "README.txt").is_file()
    with pytest.raises(Fail):
        C.main(run, ccel, tmp_path / "o3", ccel_sha="0" * 64, ccel_lines_range=(2, 2))
    with pytest.raises(Fail):
        C.main(tmp_path / "nope", ccel, tmp_path / "o4", ccel_sha=sha)
