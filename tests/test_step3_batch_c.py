"""Step 3 Batch C: locus baptism-instrumentality (33e), on the quotation unit
(LOCK_batchC_unit_2026-11-26, ruling on report 28 item 7)."""

from pathlib import Path

import pytest
from rdflib import Graph, Literal
from rdflib.namespace import RDF, RDFS, SKOS

from goldenchain import ingest
from gcfix import GC, U

DATA = Path(__file__).resolve().parent.parent / "data"
G = Graph()
for f in sorted(DATA.glob("*.ttl")):
    G.parse(f, format="turtle", publicID=ingest.B)

LOCUS = U("locus/baptism-instrumentality")
A = U("position/baptism-instrumentality/instrumental")
B = U("position/baptism-instrumentality/representational")


def _args(pos):
    return set(G.subjects(GC.supports, pos))


def _cites(a):
    return {str(c).split("passage/kjv/")[1] for c in G.objects(a, GC.cites)}


def test_locus_33e():
    assert (LOCUS, RDF.type, GC.Locus) in G
    assert G.value(LOCUS, RDFS.label) == Literal("Instrumentality of baptism", lang="en")
    assert G.value(LOCUS, SKOS.notation) == Literal("33e")
    assert G.value(LOCUS, GC.question) == Literal("How does baptism benefit the one baptized?", lang="en")
    assert (LOCUS, GC.underHeading, U("heading/worship")) in G


def test_positions_and_exclusion():
    assert G.value(A, RDFS.label) == Literal("The Holy Ghost confirms faith by the use of the sacraments.", lang="en")
    assert any(l.language == "en" for l in G.objects(B, RDFS.label))
    for p in (A, B):
        assert (p, GC.answers, LOCUS) in G
    assert (A, GC.excludes, B) in G


def test_argument_counts_per_position():
    a, b = _args(A), _args(B)
    assert len(a) == 31
    assert len([x for x in a if str(x).startswith(str(U("argument/heidelberg-harbaugh/")))]) == 23
    assert len([x for x in a if str(x).startswith(str(U("argument/belgic-confession/")))]) == 8
    assert len(b) == 4
    assert all(str(x).startswith(str(U("argument/gill-body/practical/3/1/"))) for x in b)


def test_harbaugh_per_question():
    got = {}
    for x in _args(A):
        s = str(x)
        if "/heidelberg-harbaugh/" in s:
            q = s.split("/heidelberg-harbaugh/")[1].split("/")[0]
            got[q] = got.get(q, 0) + 1
    assert got == {"65": 4, "69": 3, "70": 2, "71": 4, "72": 5, "73": 5}


@pytest.mark.parametrize("iri,cites", [
    ("heidelberg-harbaugh/69/001", {"Matt.28.19", "Mark.16.15-Mark.16.16"}),
    ("heidelberg-harbaugh/70/002", {"Eph.4.22-Eph.4.24", "Rom.6.4"}),
    ("gill-body/practical/3/1/022", {"Rom.6.4-Rom.6.5", "Col.2.12"}),
    ("gill-body/practical/3/1/023", {"Mark.1.4", "Acts.2.38"}),
])
def test_multi_reference_units(iri, cites):
    assert _cites(U("argument/" + iri)) == cites


def test_one_misprint():
    batch = _args(A) | _args(B)
    hits = [x for x in batch if Literal("Apoc. i. 6") in set(G.objects(x, GC.asPrinted))]
    assert len(hits) == 1
    assert "Rev.1.5" in _cites(hits[0])
    assert G.value(hits[0], GC.resolutionNote) is not None


def test_cited_passages_declared():
    declared = set(G.subjects(RDF.type, GC.Passage))
    for x in _args(A) | _args(B):
        for c in G.objects(x, GC.cites):
            assert c in declared, c
