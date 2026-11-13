"""Step 3 Batch B (PLAN_step3_minting, RULING_report_12: B-Q1 to B-Q5)."""

from pathlib import Path

import pytest
from rdflib import Graph, Literal
from rdflib.namespace import DCTERMS, RDF, RDFS, SKOS

from goldenchain import ingest
from gcfix import GC, U

DATA = Path(__file__).resolve().parent.parent / "data"
G = Graph()
for f in sorted(DATA.glob("*.ttl")):
    G.parse(f, format="turtle", publicID=ingest.B)

LOCUS = U("locus/baptism-validity")
P = {k: U("position/" + v) for k, v in {
    "smf": "baptism-validity/subject-mode-formula",
    "gospel": "baptism-validity/church-of-gospel-order",
    "ours": "baptism-validity/church-of-our-order",
    "rep": "baptism-repetition/infant-sprinkling-not-baptism",
}.items()}


def test_locus_33d_has_no_tier():
    assert (LOCUS, RDF.type, GC.Locus) in G
    assert G.value(LOCUS, SKOS.notation) == Literal("33d")
    assert G.value(LOCUS, RDFS.label) == Literal("Validity of baptism", lang="en")
    assert (LOCUS, GC.underHeading, U("heading/worship")) in G
    assert G.value(LOCUS, GC.tier) is None


@pytest.mark.parametrize("key,label", [
    ("smf", "Subject, mode and formula: a professing believer, immersed, in the triune name."),
    ("gospel", "Subject, mode and formula, and the administrator a church of gospel order, "
               "defined by doctrine, not by identity or succession."),
    ("ours", "Subject, mode and formula, and the administrator a church of our own order, "
             "by identity or succession."),
    ("rep", "Baptism is administered once. The sprinkling of an infant is not baptism, so the baptism of a "
            "professing believer who was sprinkled in infancy is his first baptism, not a repetition."),
])
def test_position_labels(key, label):
    assert G.value(P[key], RDFS.label) == Literal(label, lang="en")
    want = U("locus/baptism-repetition") if key == "rep" else LOCUS
    assert (P[key], GC.answers, want) in G


# (argument, supports, cites, asPrinted, comment is required)
ARGS = [
    ("lbc-1689/29/2/002", "smf", "Mark.16.16 Acts.8.36-Acts.8.37", "(f) Mar. 16.16; Act. 8.36,37"),
    ("lbc-1689/29/3/002", "smf", "Matt.28.19-Matt.28.20 Acts.8.38", "(g) Mat. 28. 19, 20. with Act. 8. 38."),
    ("lbc-1689/29/4/002", "smf", "Matt.3.16 John.3.23", "(h) Mat. 3. 16. Joh. 3. 23."),
    ("lbc-1689/28/2/001", "gospel", "Matt.28.19 1Cor.4.1", "(b) Mat. 28. 19. 1 Cor. 4. 1."),
    ("graves-old-landmarkism/10/001", "ours", "Matt.16.18 Heb.12.28 Dan.2.44",
     "(Matt. 16: 18) … (Heb. 12: 28) … Daniel (2: 44)"),
    ("belgic-confession/34/001", "rep", "Mark.16.16 Matt.28.19 Eph.4.5 Heb.6.2",
     "1 Marc xvi. 16; Matt. xxviii. 19; Eph. iv. 5; Héb. vi. 2."),
]


@pytest.mark.parametrize("iri,pos,cites,ap", ARGS)
def test_argument(iri, pos, cites, ap):
    a = U("argument/" + iri)
    assert (a, RDF.type, GC.Argument) in G
    assert (a, GC.supports, P[pos]) in G
    assert set(G.objects(a, GC.supports)) == {P[pos]}
    assert set(G.objects(a, GC.cites)) == {U("passage/kjv/" + c) for c in cites.split()}
    assert G.value(a, GC.asPrinted) == Literal(ap)
    assert G.value(a, RDFS.comment) is not None


def test_lbc_comments_and_booth():
    for n in ("29/2/002", "29/3/002", "29/4/002", "28/2/001"):
        c = str(G.value(U("argument/lbc-1689/" + n), RDFS.comment))
        assert "without an LBC Holding" in c
    assert "Booth" in str(G.value(U("argument/lbc-1689/29/4/002"), RDFS.comment))


def test_lbc_28_2_division():
    d = U("source/lbc-1689/28/2")
    assert (d, DCTERMS.isPartOf, U("source/lbc-1689")) in G


def test_graves_locators():
    a = U("argument/graves-old-landmarkism/10/001")
    assert G.value(a, GC.locator) == Literal("Ch. X")
    assert G.value(a, GC.pages) == Literal("124")
    assert {str(o) for o in G.objects(a, GC.secondaryLocator)} == {
        "IA oldlandmarkismw00gravgoog leaf 130", "Ch. VI, p. 64 (IA leaf 70)"}


def test_belgic_locators():
    a = U("argument/belgic-confession/34/001")
    assert G.value(a, GC.locator) == Literal("Art. XXXIV")
    assert G.value(a, GC.pages) == Literal("427")


def test_gill_holding():
    h = U("holding/gill/baptism-repetition/infant-sprinkling-not-baptism")
    assert (U("body/gill"), GC.holds, h) in G
    assert (h, GC.position, P["rep"]) in G
    assert (h, GC.modality, U("vocab/modality/taught")) in G
    assert (h, DCTERMS.source, U("source/gill-divine-right/2")) in G
    assert G.value(h, RDFS.comment) is not None
    assert G.value(h, GC.status) == U("vocab/status/proposed")
    assert G.value(U("source/gill-divine-right/2"), RDFS.label) == Literal("Divine Right, ch. II", lang="en")


def _held_positions():
    return {G.value(h, GC.position) for h in G.subjects(RDF.type, GC.Holding)}


def test_no_lbc_holding_on_validity_positions():
    for h in G.subjects(RDF.type, GC.Holding):
        if str(h).startswith(str(U("holding/lbc-1689/"))):
            assert G.value(h, GC.position) not in (P["smf"], P["gospel"], P["ours"])
    for k in ("smf", "gospel", "ours"):
        assert P[k] not in _held_positions()


@pytest.mark.parametrize("work", ["graves-old-landmarkism", "belgic-confession", "bsb-gill-1984"])
def test_no_holding_for_work(work):
    prefix = str(U("source/" + work))
    for h in G.subjects(RDF.type, GC.Holding):
        src = str(G.value(h, DCTERMS.source))
        assert not src.startswith(prefix)
    assert (U("body/" + work), RDF.type, None) not in G


def test_bsb_not_quoted():
    d = U("source/bsb-gill-1984/foreword/vii-viii")
    assert (d, RDF.type, GC.SourceDivision) in G
    assert (d, DCTERMS.isPartOf, U("source/bsb-gill-1984")) in G
    bsb = str(U("source/bsb-gill-1984"))
    for s, _, o in G.triples((None, GC.quotation, None)):
        assert not str(G.value(s, GC.source) or "").startswith(bsb)
    for s in G.subjects(GC.source, d):
        assert G.value(s, GC.quotation) is None


def test_no_edges_touch_validity_positions():
    vp = {P["smf"], P["gospel"], P["ours"]}
    for pred in (GC.excludes, GC.entails):
        for s, _, o in G.triples((None, pred, None)):
            assert s not in vp and o not in vp
