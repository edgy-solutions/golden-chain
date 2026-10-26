"""Cross-check goldenchain.versification against a USFM KJV (counts only).

Data tests need GOLDEN_CHAIN_BIBLES, a directory containing eng-kjv2006_usfm/.
"""

import os
from pathlib import Path

import pytest

from goldenchain import usfm
from goldenchain.versification import BOOKS, CHAPTERS


def _gen(extra=""):
    return (
        "\\id GEN Genesis\n\\h Genesis\n\\c 1  \n\\p\n\\v 1 a\n\\v 2 b \r\n"
        "\\c 2\n\\p\n\\v 1 c \\v 2-3 d\n\\v 4 e\n" + extra
    )


def test_parse_book_bridge_and_midline(tmp_path):
    book, ch, bridges = usfm.parse_book(_gen())
    assert (book, ch, bridges) == ("Gen", (2, 4), [(2, "2-3")])


def test_read_counts_and_bridges(tmp_path):
    (tmp_path / "a.usfm").write_text(_gen(), encoding="utf-8")
    (tmp_path / "b.usfm").write_text(
        "\\id EXO\n\\c 1\n\\v 1 x\n\\v 2 y\n", encoding="utf-8"
    )
    (tmp_path / "copr.htm").write_text("ignored", encoding="utf-8")
    counts, bridges = usfm.read_all(tmp_path)
    assert counts == {"Gen": (2, 4), "Exod": (2,)}
    assert bridges == [("Gen", 2, "2-3")]
    assert list(usfm.read_counts(tmp_path)) == ["Gen", "Exod"]


@pytest.mark.parametrize(
    "text",
    [
        "\\id GEN\n\\c 1\n\\v 1 a\n\\v 3 b\n",  # verse gap
        "\\id GEN\n\\c 1\n\\v 1 a\n\\c 3\n\\v 1 b\n",  # chapter gap
        "\\id GEN\n\\c 1\n\\v 2 a\n",  # does not start at 1
        "\\id GEN\n\\c 1\n\\v 1 a\n\\v 1 b\n",  # repeat
        "\\id XXX\n\\c 1\n\\v 1 a\n",  # unknown id
        "\\id GEN\n\\c 1\n",  # empty chapter
    ],
)
def test_parse_fails_loud(text):
    with pytest.raises(usfm.UsfmError):
        usfm.parse_book(text)


def test_duplicate_book_fails(tmp_path):
    for n in "ab":
        (tmp_path / f"{n}.usfm").write_text(_gen(), encoding="utf-8")
    with pytest.raises(usfm.UsfmError):
        usfm.read_all(tmp_path)


def test_diff_counts_exact():
    a = {"Gen": (1, 2, 3), "Exod": (5, 6), "Lev": (1,), "Num": (4,)}
    b = {"Gen": (1, 9, 3), "Exod": (5,), "Lev": (1,), "Deut": (7,)}
    assert usfm.diff_counts(a, b) == [
        ("verses", "Gen", 2, 2, 9),
        ("chapters", "Exod", 2, 1),
        ("missing", "Num", "b"),
        ("missing", "Deut", "a"),
    ]
    assert usfm.diff_counts(a, a) == []


def test_mapping_aligns_with_books():
    assert tuple(usfm.USFM_TO_OSIS.values()) == BOOKS


def test_table_totals():
    assert len(BOOKS) == 66
    assert sum(len(v) for v in CHAPTERS.values()) == 1189
    assert sum(sum(v) for v in CHAPTERS.values()) == 31102


@pytest.fixture(scope="module")
def kjv_dir():
    root = os.environ.get("GOLDEN_CHAIN_BIBLES")
    if not root:
        pytest.skip("GOLDEN_CHAIN_BIBLES not set")
    d = Path(root) / "eng-kjv2006_usfm"
    if not d.is_dir():
        pytest.skip("eng-kjv2006_usfm/ not found under GOLDEN_CHAIN_BIBLES")
    return d


def test_usfm_matches_table(kjv_dir):
    counts, _ = usfm.read_all(kjv_dir)
    assert set(counts) == set(BOOKS) and len(counts) == 66
    assert sum(len(v) for v in counts.values()) == 1189
    assert sum(sum(v) for v in counts.values()) == 31102
    diffs = usfm.diff_counts(counts, CHAPTERS)
    assert diffs == [], "usfm vs canon.h differences:\n" + "\n".join(map(str, diffs))
