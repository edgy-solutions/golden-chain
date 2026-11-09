"""Step 3 Batch A' (PLAN_step3_minting, ruling M5, M6, M8, M9, M10, M11, F-A)."""

from pathlib import Path

import pytest
from rdflib import Graph, Literal
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS

from goldenchain import ingest, passage
from gcfix import GC, U, dataset_with, minimal

G = Graph()
for f in sorted((Path(__file__).resolve().parent.parent / "data").glob("*.ttl")):
    G.parse(f, format="turtle", publicID=ingest.B)

AXIOM = U("axiom/entails/baptism-subjects/believers-and-their-infants/to/circumcision-covenant/administration-of-grace")
SRC = U("position/baptism-subjects/believers-and-their-infants")
TGT = U("position/circumcision-covenant/administration-of-grace")


@pytest.mark.parametrize("ref,iri", [
    ("Heb.8-Heb.10", "Heb.8.1-Heb.10.39"),
    ("Rom.4", "Rom.4.1-Rom.4.25"),
    ("Gal.3", "Gal.3.1-Gal.3.29"),
    ("Gen.17", "Gen.17.1-Gen.17.27"),
])
def test_whole_chapters_expand(ref, iri):
    assert passage.canonical(ref) == ingest.B + "passage/kjv/" + iri
    assert U("passage/kjv/" + iri) in set(G.subjects(RDF.type, GC.Passage))


def test_no_chapter_only_passage_iri():
    for p in G.subjects(RDF.type, GC.Passage):
        tail = str(p).split("/passage/kjv/")[1]
        for part in tail.split("-"):
            assert part.count(".") == 2, p


def test_rejected_axiom_in_data():
    assert (AXIOM, RDF.type, OWL.Axiom) in G
    assert (AXIOM, OWL.annotatedSource, SRC) in G
    assert (AXIOM, OWL.annotatedProperty, GC.entails) in G
    assert (AXIOM, OWL.annotatedTarget, TGT) in G
    assert (AXIOM, GC.status, U("vocab/status/rejected")) in G
    assert G.value(AXIOM, RDFS.comment) is not None
    assert (SRC, GC.entails, TGT) not in G


def _check(g):
    ingest.code_checks(dataset_with(g))


def _fix(status, asserted):
    g = minimal()
    g.parse(data=f"""@base <{ingest.B}> .
@prefix gc: <{ingest.B}ontology#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
<position/baptism/a> a gc:Position ; rdfs:label "A" ; gc:answers <locus/baptism> ;
    gc:status <vocab/status/proposed> ; gc:proposedBy <agent/build> .
<position/baptism/b> a gc:Position ; rdfs:label "B" ; gc:answers <locus/baptism> ;
    gc:status <vocab/status/proposed> ; gc:proposedBy <agent/build> .
<axiom/entails/baptism/a/to/baptism/b> a owl:Axiom ;
    owl:annotatedSource <position/baptism/a> ; owl:annotatedProperty gc:entails ;
    owl:annotatedTarget <position/baptism/b> ; rdfs:comment "note"@en {status} .
""", format="turtle")
    if asserted:
        g.add((U("position/baptism/a"), GC.entails, U("position/baptism/b")))
    return g


REJ = "; gc:status <vocab/status/rejected>"


def test_rejected_axiom_with_triple_absent_passes():
    _check(_fix(REJ, False))


def test_rejected_axiom_with_triple_asserted_is_violation():
    with pytest.raises(ingest.IngestError, match="rejected axiom"):
        _check(_fix(REJ, True))


def test_unrejected_axiom_with_triple_absent_is_violation():
    with pytest.raises(ingest.IngestError, match="not asserted"):
        _check(_fix("", False))


def test_unrejected_axiom_with_triple_asserted_passes():
    _check(_fix("", True))


def test_gill_is_a_teacher_in_two_works():
    gill = U("body/gill")
    assert set(G.objects(gill, RDF.type)) == {GC.Teacher}
    assert set(G.objects(gill, GC.expressedIn)) == {U("source/gill-body"), U("source/gill-divine-right")}
    assert G.value(gill, RDFS.label) == Literal("John Gill (1697–1771)", lang="en")


def test_gill_circumcision_holding():
    h = U("holding/gill/circumcision-covenant/not-an-administration-of-grace")
    assert (U("body/gill"), GC.holds, h) in G
    assert (h, GC.modality, U("vocab/modality/taught")) in G
    assert (h, DCTERMS.source, U("source/gill-divine-right/4")) in G


@pytest.mark.parametrize("p,q", [
    ("circumcision-covenant/administration-of-grace", "circumcision-covenant/not-an-administration-of-grace"),
    ("covenant-of-grace/eternal-with-christ", "covenant-of-grace/established-in-new-covenant"),
    ("covenant-of-grace/eternal-with-christ", "covenant-of-grace/made-in-time-after-fall"),
    ("covenant-of-grace/established-in-new-covenant", "covenant-of-grace/made-in-time-after-fall"),
])
def test_new_excludes(p, q):
    assert (U("position/" + p), GC.excludes, U("position/" + q)) in G


def test_23a_ii_label():
    assert G.value(U("position/covenant-of-grace/established-in-new-covenant"), RDFS.label) == Literal(
        "An eternal covenant of redemption between the Father and the Son; in pursuance of it, "
        "grace revealed to fallen man by promise from the fall.", lang="en")


def test_lbc_7_3():
    pos = U("position/covenant-of-grace/established-in-new-covenant")
    h = U("holding/lbc-1689/covenant-of-grace/established-in-new-covenant")
    assert (U("body/lbc-1689"), GC.holds, h) in G
    assert (h, GC.position, pos) in G
    assert (h, DCTERMS.source, U("source/lbc-1689/7/3")) in G
    want = {"001": ("Gen.3.15", "e Gen. 3.15."), "002": ("Heb.1.1", "f Heb. 1.1."),
            "003": ("2Tim.1.9 Titus.1.2", "* 2 Tim. 1.9. Tit. 1.2.")}
    for n, (cites, ap) in want.items():
        a = U("argument/lbc-1689/7/3/" + n)
        assert (a, GC.supports, pos) in G
        assert (a, GC.source, U("source/lbc-1689/7/3")) in G
        assert set(G.objects(a, GC.cites)) == {U("passage/kjv/" + c) for c in cites.split()}
        assert G.value(a, GC.asPrinted) == Literal(ap)
        assert G.value(a, RDFS.comment) is not None


def test_wcf_7_6_002():
    a = U("argument/wcf/7/6/002")
    assert set(G.objects(a, GC.cites)) == {U("passage/kjv/Col.2.17")}
    assert G.value(a, GC.asPrinted) == Literal("n Gal, 2, 17")
    assert (a, GC.supports, U("position/covenant-of-grace/made-in-time-after-fall")) in G
