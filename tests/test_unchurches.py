"""gc:unchurches: ingest check e, the derivation, the wording, and the real data (ADR-0003 R2.3/R2.7)."""

import pytest
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, XSD

from goldenchain import ingest, unchurches
from gcfix import GC, PROPOSED, U, World, add, dataset_with, minimal

TRUE = '"true"^^xsd:boolean'
FLAG = "<position/baptism/immersion> gc:unchurches " + TRUE + " ."
PL_FORBID = f"""
<body/plumb-line> a gc:Body ; gc:holds <holding/plumb-line/baptism/immersion> .
<holding/plumb-line/baptism/immersion> a gc:Holding ; gc:position <position/baptism/immersion> ;
    gc:modality <vocab/modality/forbidden> ; dcterms:source <source/gill/ch1> ; {PROPOSED} .
"""
TIER2 = "<locus/baptism> gc:tier <vocab/tier/second> ."


def build(plumb_extra="", fixture_extra="", forbid=True, tier=TIER2, pl_hold=None):
    """Fixture dataset: the minimal graph, plus a plumb-line graph."""
    fx = minimal()
    if fixture_extra:
        add(fx, fixture_extra)
    ds = dataset_with(fx)
    ttl = (pl_hold if pl_hold is not None else (PL_FORBID if forbid else "")) + tier + " " + plumb_extra
    g = add(Graph(), ttl)
    pl = ds.graph(ingest.PLUMB_LINE)
    for t in g:
        pl.add(t)
    return ds


def refused(ds, *needles):
    with pytest.raises(ingest.IngestError, match=r"e\.") as e:
        ingest.code_checks(ds)
    for n in needles:
        assert n in str(e.value)


def test_accepts_flag_on_forbidden_tier_second():
    ingest.code_checks(build(FLAG))


def test_refuse_non_plumb_line_graph():
    refused(build("", FLAG), "asserted in", "not plumb-line")


def test_refuse_false():
    refused(build('<position/baptism/immersion> gc:unchurches "false"^^xsd:boolean .'),
            "only", "may be written")


def test_refuse_plain_literal():
    refused(build('<position/baptism/immersion> gc:unchurches "yes" .'), "may be written")


def test_refuse_non_position():
    refused(build("<locus/baptism> gc:unchurches " + TRUE + " ."), "not a gc:Position")


def test_refuse_two_literals():
    ds = build(FLAG)
    # rdflib folds "1"^^xsd:boolean to "true" on parse, so build the second term unnormalised.
    ds.graph(ingest.PLUMB_LINE).add(
        (U("position/baptism/immersion"), GC.unchurches, Literal("1", datatype=XSD.boolean, normalize=False))
    )
    refused(ds, "written 2 times")


def test_refuse_plumb_line_taught():
    taught = PL_FORBID.replace("forbidden", "taught")
    refused(build(FLAG, pl_hold=taught), "does not hold it forbidden (shape 1)")


def test_refuse_plumb_line_silent():
    refused(build(FLAG, forbid=False), "does not hold it forbidden (shape 1)")


def test_refuse_tier_third():
    refused(build(FLAG, tier="<locus/baptism> gc:tier <vocab/tier/third> ."), "is tier third (shape 2)")


def test_refuse_no_tier():
    refused(build(FLAG, tier=""), "has no tier (shape 2 cannot be checked)")


# ---- derivation -----------------------------------------------------------------------

def derive(w: World, flag_pos="position/l/p"):
    ds = w.dataset()
    pl = ds.graph(ingest.PLUMB_LINE)
    pl.add((U(flag_pos), GC.unchurches, Literal(True)))
    return ingest.derive_rdflib(ds)


def world():
    w = World()
    w.position("l", "p")
    w.body("parent")
    w.body("child", "parent")
    w.body("other", "parent")
    w.body("plumb-line")
    return w


def test_inheritance_and_override():
    w = world()
    w.hold("parent", "l", "p", "taught")
    w.hold("other", "l", "p", "forbidden")
    out = unchurches.excluded(derive(w))
    assert set(out) == {U("body/parent"), U("body/child")}
    assert out[U("body/child")][0]["own"] is False
    assert out[U("body/parent")][0]["own"] is True
    assert U("body/other") not in out


@pytest.mark.parametrize("mod,hit", [("required", True), ("taught", True), ("tolerated", True),
                                     ("forbidden", False)])
def test_trigger_modalities(mod, hit):
    w = world()
    w.hold("parent", "l", "p", mod)
    w.hold("plumb-line", "l", "p", "forbidden")
    out = unchurches.excluded(derive(w))
    assert (U("body/parent") in out) is hit
    assert U("body/plumb-line") not in out


def test_unflagged_is_empty():
    w = world()
    w.hold("parent", "l", "p", "required")
    assert unchurches.excluded(w.dataset()) == {}


@pytest.mark.parametrize("cls", ["Confession", "Catechism", "Collection", "Systematic", "Teacher"])
def test_wording(cls):
    w = world()
    w.g.add((U("body/parent"), RDF.type, GC[cls]))
    got = unchurches.wording(w.g, U("body/parent"))
    assert got == unchurches.WORDING[cls]
    assert ("subscribing" in got) == (cls in ("Confession", "Catechism", "Collection"))


def test_wording_editorial_raises():
    w = world()
    w.g.add((U("body/parent"), RDF.type, GC.Editorial))
    with pytest.raises(ValueError, match="body/parent"):
        unchurches.wording(w.g, U("body/parent"))


# ---- real data ------------------------------------------------------------------------

def test_real_data_no_flags_empty():
    ds = ingest.load_dataset()
    assert unchurches.excluded(ingest.derive_rdflib(ds)) == {}


def test_real_data_with_flags():
    ds = ingest.load_dataset()
    pl = ds.graph(ingest.PLUMB_LINE)
    pos = [U("position/baptism-subjects/believers-and-their-infants"),
           U("position/baptism-subjects/infants")]
    for p in pos:
        pl.add((p, GC.unchurches, Literal(True, datatype=XSD.boolean)))
    ingest.code_checks(ds)
    d = ingest.derive_rdflib(ds)
    out = unchurches.excluded(d)
    assert set(out) == {U("body/wcf"), U("body/augsburg"), U("body/apology-1531")}
    expect = {
        "body/wcf": ("holding/wcf/baptism-subjects/believers-and-their-infants", "required", None),
        "body/augsburg": ("holding/augsburg/baptism-subjects/infants", "taught", None),
        "body/apology-1531": ("holding/apology-1531/baptism-subjects/infants", "taught", True),
    }
    for b, (h, m, own) in expect.items():
        assert len(out[U(b)]) == 1
        row = out[U(b)][0]
        assert row["holding"] == U(h)
        assert row["modality"] == U("vocab/modality/" + m)
        if own is not None:
            assert row["own"] is own
        assert unchurches.wording(d, U(b)) == unchurches.WORDING["Confession"]
