import pytest

from goldenchain.versification import (
    BOOKS, CHAPTERS, V11N, last_verse, verse_ordinal,
)


def test_totals():
    """Born check (architect ruling 8): 66 books, 1,189 chapters, 31,102 verses."""
    assert V11N == "kjv"
    assert len(BOOKS) == 66
    assert sum(len(c) for c in CHAPTERS.values()) == 1189
    assert sum(sum(c) for c in CHAPTERS.values()) == 31102


def test_known_counts():
    assert len(CHAPTERS["Ps"]) == 150
    assert last_verse("Ps", 119) == 176
    assert last_verse("3John", 1) == 14
    assert len(CHAPTERS["Mal"]) == 4
    assert last_verse("Rom", 16) == 27
    assert last_verse("Gen", 1) == 31


def test_ordinals():
    assert verse_ordinal("Gen", 2, 1) == 32
    for book, counts in CHAPTERS.items():
        assert verse_ordinal(book, len(counts), counts[-1]) == sum(counts)


@pytest.mark.parametrize("args", [("Mat", 1, 1), ("Rom", 17, 1), ("Rom", 0, 1),
                                  ("Rom", 6, 24), ("Rom", 6, 0)])
def test_errors(args):
    with pytest.raises(ValueError):
        verse_ordinal(*args)
