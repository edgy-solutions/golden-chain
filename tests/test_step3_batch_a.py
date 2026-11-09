"""Step 3 Batch A (PLAN_step3_minting, ruling on report 11): loci 23a/23b, the retired 23, E1 moved, 16 Arguments."""

from pathlib import Path

import pytest
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF

from goldenchain import ingest
from gcfix import GC, U

G = Graph()
for f in sorted((Path(__file__).resolve().parent.parent / "data").glob("*.ttl")):
    G.parse(f, format="turtle", publicID=ingest.B)

COG = "covenant-of-grace/"
CC = "circumcision-covenant/"
CIRC_YES = CC + "administration-of-grace"
CIRC_NO = CC + "not-an-administration-of-grace"
CG_I = COG + "eternal-with-christ"
CG_II = COG + "established-in-new-covenant"
CG_III = COG + "made-in-time-after-fall"

ARGS = {
    "gill-body/doctrinal/2/15/001": (CG_I, ["Eph.1.3-Eph.1.4", "2Tim.1.9"]),
    "gill-body/doctrinal/2/15/002": (CG_I, ["Titus.1.2", "2Tim.1.1"]),
    "gill-body/doctrinal/2/15/003": (CG_I, ["Ps.89.2-Ps.89.3", "Ps.89.28", "Ps.103.17", "John.17.23-John.17.24",
                                            "Eph.1.4", "Prov.8.23", "Mic.5.2"]),
    "coxe-covenants/2/10/001": (CG_II, ["2Tim.1.9-2Tim.1.10", "Titus.1.1-Titus.1.2"]),
    "coxe-covenants/2/10/002": (CG_II, ["Prov.8.22-Prov.8.31"]),
    "coxe-covenants/2/11/001": (CG_II, ["Gen.3.15"]),
    "wcf/7/3/001": (CG_III, ["Gal.3.21", "Rom.8.3", "Rom.3.20-Rom.3.21", "Gen.3.15", "Isa.42.6"]),
    "wcf/7/5/002": (CG_III, ["2Cor.3.6-2Cor.3.9"]),
    "wcf/7/5/003": (CIRC_YES, ["Rom.4.11", "Col.2.11-Col.2.12", "1Cor.5.7"]),
    "wcf/28/4/003": (CIRC_YES, ["Gen.17.7", "Gen.17.9", "Gal.3.9", "Gal.3.14", "Col.2.11-Col.2.12",
                                "Acts.2.38-Acts.2.39", "Rom.4.11-Rom.4.12", "1Cor.7.14", "Matt.28.19",
                                "Mark.10.13-Mark.10.16", "Luke.18.15"]),
    "coxe-covenants/5/8/001": (CIRC_NO, ["Gen.17.4-Gen.17.5", "Rom.4.17", "Rom.4.11"]),
    "gill-divine-right/4/001": (CIRC_NO, ["Acts.7.8", "Gal.5.2-Gal.5.4"]),
    "gill-divine-right/4/002": (CIRC_NO, ["Gen.17.9-Gen.17.14"]),
    "gill-divine-right/4/003": (CIRC_NO, ["Gen.17.14", "Ps.89.34"]),
    "gill-divine-right/4/004": (CIRC_NO, ["Gen.17.6", "Gen.17.8", "Gen.17.5"]),
    "gill-divine-right/4/005": (CIRC_NO, ["Gal.3.16"]),
}
NOTES = ["wcf/7/5/003", "wcf/28/4/003", "coxe-covenants/2/11/001", "coxe-covenants/5/8/001",
         "gill-divine-right/4/004"]


def test_the_16_arguments_are_all_present():
    assert len(ARGS) == 16


def test_retired_locus_is_deprecated_and_replaced():
    old = U("locus/covenant-administrations")
    assert (old, OWL.deprecated, Literal(True)) in G
    assert set(G.objects(old, DCTERMS.isReplacedBy)) == {U("locus/covenant-of-grace"),
                                                         U("locus/circumcision-covenant")}


def test_old_e1_absent_new_present():
    infants = U("position/baptism-subjects/believers-and-their-infants")
    assert (infants, GC.entails, U("position/covenant-administrations/one-covenant-two-administrations")) not in G
    assert (U("position/" + CIRC_YES), GC.entails, infants) in G


@pytest.mark.parametrize("aid", sorted(ARGS))
def test_argument_cites_and_supports(aid):
    a = U("argument/" + aid)
    sup, cites = ARGS[aid]
    assert (a, RDF.type, GC.Argument) in G
    assert set(G.objects(a, GC.supports)) == {U("position/" + sup)}
    assert set(G.objects(a, GC.cites)) == {U("passage/kjv/" + c) for c in cites}


@pytest.mark.parametrize("aid", NOTES)
def test_resolution_note_present(aid):
    assert G.value(U("argument/" + aid), GC.resolutionNote) is not None


def test_no_holding_on_circumcision_no():
    pos = U("position/" + CIRC_NO)
    assert list(G.subjects(GC.position, pos)) == []


@pytest.mark.parametrize("slug", ["covenant-of-grace", "circumcision-covenant"])
def test_new_loci_have_no_tier(slug):
    loc = U("locus/" + slug)
    assert (loc, RDF.type, GC.Locus) in G
    assert G.value(loc, GC.tier) is None
