import re

import pytest

from goldenchain.passage import BASE, IRI_PATTERN, canonical, parse

K = BASE + "passage/kjv/"


def test_expansion_and_collapse():
    assert canonical("Ps.23") == K + "Ps.23.1-Ps.23.6"
    assert canonical("Ps.23-Ps.24") == K + "Ps.23.1-Ps.24.10"
    assert canonical("Rom.6.4-Rom.6.4") == K + "Rom.6.4"
    assert canonical("Rom.6.4") == K + "Rom.6.4"
    assert canonical("Rom.6.3-Rom.6.4") == K + "Rom.6.3-Rom.6.4"
    assert canonical("Gen.17.1-Gen.18.2") == K + "Gen.17.1-Gen.18.2"


@pytest.mark.parametrize("ref", [
    "Rom.6.4-Rom.6.3", "Matt.28.20-Mark.1.1", "Mat.1.1", "rom.6.4",
    "Rom.17.1", "Rom.6.24", "Rom.6.0", "Rom.0", "Rom", "Rom.6.4!a",
    "Rom.6.4@", "Rom.6.4.", " Rom.6.4", "Rom.6.4 ", "Rom. 6.4", "",
    "Rom.6.4-Rom", "Rom.6.4-",
])
def test_rejected(ref):
    with pytest.raises(ValueError):
        canonical(ref)


def test_unsupported_v11n():
    with pytest.raises(ValueError):
        canonical("Rom.6.4", "nrsv")
    with pytest.raises(ValueError):
        canonical("Rom.6.4", "KJV")


@pytest.mark.parametrize("ref", ["Rom.6.4", "Ps.23", "Gen.17.1-Gen.18.2",
                                 "Rom.6.4-Rom.6.4", "Ps.23-Ps.25"])
def test_round_trip(ref):
    assert canonical(parse(ref).osis) == canonical(ref)
    assert parse(canonical(ref)).osis == parse(ref).osis


def test_ordinals():
    r, s = parse("Matt.28.19-Matt.28.20"), parse("Matt.28.19")
    assert r.start_ordinal == s.start_ordinal == s.end_ordinal
    assert r.end_ordinal == s.end_ordinal + 1
    assert r.book == "Matt" and r.v11n == "kjv"


def test_parse_rejects_noncanonical_iri():
    with pytest.raises(ValueError):
        parse(K + "Rom.6.4-Rom.6.4")
    with pytest.raises(ValueError):
        parse(K + "Ps.23")
    with pytest.raises(ValueError):
        parse(BASE + "passage/nrsv/Rom.6.4")


def test_iri_pattern():
    for ref in ["Rom.6.4", "Ps.23", "1John.1.1-1John.2.2"]:
        assert re.match(IRI_PATTERN, canonical(ref))
    assert not re.match(IRI_PATTERN, BASE + "passage/Rom.6.4")
    assert not re.match(IRI_PATTERN, K + "Rom.6")
    assert not re.match(IRI_PATTERN, K + "Mat.6.4")
