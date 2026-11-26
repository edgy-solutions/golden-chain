"""ADR-0003 Revision 3, built: the born tests (LOCK_adr3_r3_2026-11-22, rows R1-R8 and the placeholder guard).

The weigh fixture is test_weigh's, migrated to the one gc:unchurches form (<body/plumb-line> gc:unchurches <position>).
"""
from pathlib import Path

import pytest
from rdflib import Graph, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF

from goldenchain import ingest, unchurches, weigh
from gcfix import GC, U, add, dataset_with, focus_nodes, minimal, report
from test_unchurches import TIER2, build as ck_build, refused

ROOT = Path(__file__).resolve().parents[1]
OWL_AX = "<http://www.w3.org/2002/07/owl#"
SITTING = U("source/plumb-line/sitting-eb961ddb1e582ed6")
FLAGGED = ["baptism-subjects/believers-and-their-infants", "baptism-subjects/infants",
           "circumcision-covenant/administration-of-grace"]

# ---- the weigh fixture, in the new form ---------------------------------------------------------------

LOCI = ["worship", "baptism-subjects", "baptism-validity", "baptism-repetition"]
SRC = "<source/plumb-line/sitting-fixture>"
PL = [("worship", "a-cappella-psalmody", "taught"), ("worship", "hymns-and-instruments", "forbidden"),
      ("baptism-subjects", "professing-believers-only", "taught"),
      ("baptism-subjects", "believers-and-their-infants", "forbidden"),
      ("baptism-subjects", "infants", "forbidden"),
      ("baptism-validity", "subject-mode-formula", "tolerated"),
      ("baptism-validity", "church-of-gospel-order", "taught"),
      ("baptism-validity", "church-of-our-order", "forbidden"),
      ("baptism-repetition", "once-only", "taught")]
BODIES = {
    "case-a": [("worship", "hymns-and-instruments", "taught"),
               ("baptism-subjects", "professing-believers-only", "taught"),
               ("baptism-validity", "church-of-gospel-order", "taught"),
               ("baptism-repetition", "once-only", "taught")],
    "case-b": [("baptism-subjects", "believers-and-their-infants", "required"),
               ("worship", "a-cappella-psalmody", "taught"),
               ("baptism-repetition", "once-only", "taught")],
    "case-c": [("baptism-subjects", "professing-believers-only", "taught"),
               ("baptism-validity", "church-of-our-order", "required"),
               ("baptism-repetition", "once-only", "taught"),
               ("worship", "a-cappella-psalmody", "taught")],
}


def holding(body, locus, pos, mod, src=None):
    s = src or f"<source/{body}/x>"
    return (f"<body/{body}> gc:holds <holding/{body}/{pos}> .\n"
            f"<holding/{body}/{pos}> a gc:Holding ; gc:position <position/{locus}/{pos}> ; "
            f"gc:modality <vocab/modality/{mod}> ; dcterms:source {s} .\n")


def stated_ttl(body, locus, pos, src="source/case-a/p3", loc="p. 3", source=True, locator=True):
    """A Body's stated judgment, with its axiom (ADR-0003 R3.4)."""
    t = f"<body/{body}> gc:unchurches <position/{locus}/{pos}> .\n"
    t += (f"<axiom/unchurches/{body}/{locus}/{pos}> a {OWL_AX}Axiom> ; {OWL_AX}annotatedSource> <body/{body}> ; "
          f"{OWL_AX}annotatedProperty> gc:unchurches ; {OWL_AX}annotatedTarget> <position/{locus}/{pos}> ; "
          + (f"dcterms:source <{src}> ; " if source else "") + (f'gc:locator "{loc}" ; ' if locator else "")
          + 'rdfs:comment "Stated by the Body, in its own words."@en .\n')
    return t


def build(extra="", extra_pl=""):
    ttl_pl = "<body/plumb-line> a gc:Editorial .\n"
    ttl_fx = ""
    for l in LOCI:
        ttl_pl += f"<locus/{l}> a gc:Locus ; gc:tier <vocab/tier/second> ; gc:clarity <vocab/clarity/settled> .\n"
    for l, p, m in PL:
        ttl_fx += f"<position/{l}/{p}> a gc:Position ; gc:answers <locus/{l}> .\n"
        ttl_pl += holding("plumb-line", l, p, m, SRC)
    for p in ("believers-and-their-infants", "infants"):
        ttl_pl += f"<body/plumb-line> gc:unchurches <position/baptism-subjects/{p}> .\n"
        ttl_pl += (f"<axiom/unchurches/plumb-line/baptism-subjects/{p}> a {OWL_AX}Axiom> ; "
                   f"{OWL_AX}annotatedSource> <body/plumb-line> ; {OWL_AX}annotatedProperty> gc:unchurches ; "
                   f"{OWL_AX}annotatedTarget> <position/baptism-subjects/{p}> ; dcterms:source {SRC} .\n")
    for name, hs in BODIES.items():
        ttl_fx += f"<body/{name}> a gc:Confession .\n"
        for l, p, m in hs:
            src = "<source/case-b/28>" if name == "case-b" and p == "believers-and-their-infants" else None
            ttl_fx += holding(name, l, p, m, src)
    ds = dataset_with(add(Graph(), ttl_fx + extra))
    pl = ds.graph(ingest.PLUMB_LINE)
    for t in add(Graph(), ttl_pl + extra_pl):
        pl.add(t)
    return ingest.union(ingest.derive_rdflib(ds))


def real():
    return ingest.union(ingest.derive_rdflib(ingest.load_dataset()))


# ---- R1 -------------------------------------------------------------------------------------------------

def test_r1_data_has_the_one_form():
    """R1: no boolean gc:unchurches; three plumb-line statements, each with its axiom from sitting eb961ddb."""
    g = Graph()
    g.parse(ROOT / "data" / "plumb-line.ttl", format="turtle")
    assert [t for t in g.triples((None, GC.unchurches, None)) if not isinstance(t[2], URIRef)] == []
    assert set(g.subject_objects(GC.unchurches)) == {(U("body/plumb-line"), U("position/" + f)) for f in FLAGGED}
    for f in FLAGGED:
        ax = U(f"axiom/unchurches/plumb-line/{f}")
        assert (ax, RDF.type, OWL.Axiom) in g
        assert (ax, OWL.annotatedSource, U("body/plumb-line")) in g
        assert (ax, OWL.annotatedProperty, GC.unchurches) in g
        assert (ax, OWL.annotatedTarget, U("position/" + f)) in g
        assert set(g.objects(ax, DCTERMS.source)) == {SITTING}


# ---- R3 -------------------------------------------------------------------------------------------------

def test_r3_no_plumb_line_standard_wording():
    """R3: no *.py or *.ttl under goldenchain/, tools/ or ontology/ says "plumb-line's standard"."""
    hits = [str(p) for d in ("goldenchain", "tools", "ontology") for ext in ("*.py", "*.ttl")
            for p in (ROOT / d).rglob(ext) if "plumb-line's standard" in p.read_text(encoding="utf-8")]
    assert hits == []


# ---- R4 -------------------------------------------------------------------------------------------------

def test_r4_placeholder_in_the_site_view():
    """R4: UNSIGNED is line 2, and directly above every line that begins with HEADING, at its indentation."""
    lines = weigh.render(build()).split("\n")
    assert lines[1] == unchurches.UNSIGNED
    n = 0
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith(unchurches.HEADING):
            n += 1
            indent = ln[:len(ln) - len(ln.lstrip())]
            assert lines[i - 1] == indent + unchurches.UNSIGNED
    assert n == 2  # the section heading and case-b's own line


def test_r4_no_statement_in_the_data():
    """R4: the placeholder text and standard-statement are in no data/*.ttl."""
    for p in (ROOT / "data").glob("*.ttl"):
        t = p.read_text(encoding="utf-8")
        assert unchurches.UNSIGNED not in t and "standard-statement" not in t, p.name


def test_placeholder_guard_no_standard_statement_source():
    """Guard (R4): no source/plumb-line/standard-statement in the real data. The display has to be built before it is."""
    assert (U("source/plumb-line/standard-statement"), None, None) not in real()
    assert list(real().triples((None, None, U("source/plumb-line/standard-statement")))) == []


# ---- R5 -------------------------------------------------------------------------------------------------

def test_r5_comparison_view_fixture():
    """R5: from body/case-a, labelled, case-b ranked not excluded, no site wording, walls name case-a; its stated judgment listed."""
    # case-c also forbids what case-a teaches (hymns), so that a wall appears
    g = build(extra=stated_ttl("case-a", "baptism-subjects", "infants")
              + holding("case-c", "worship", "hymns-and-instruments", "forbidden"))
    out = weigh.render(g, frm=U("body/case-a"))
    lines = out.split("\n")
    assert lines[0] == ("Comparison view: weighed from the Holdings of body/case-a, not by this site's standard")
    assert lines[1] == "(scope members)"
    assert lines[2] == "stated by body/case-a:"
    assert lines[3] == ("  - body/case-a states that holders of position/baptism-subjects/infants are not a church "
                        "(source/case-a/p3, p. 3)")
    assert lines[3] == "  - " + unchurches.stated_line(g, U("body/case-a"), unchurches.stated(g, U("body/case-a"))[0])
    res = weigh.weigh(g, frm=U("body/case-a"))
    assert res["excluded"] == {}
    assert {b for b, _ in res["ranked"]} == {U("body/case-b"), U("body/case-c")}
    assert "body/case-b [Confession] ranked" in out
    assert unchurches.HEADING not in out and unchurches.UNSIGNED not in out
    assert "not ranked" not in out
    assert "against body/case-a " in out
    assert "against plumb-line" not in out


def test_r5_default_view_is_the_plumb_line():
    """R5: render(g, frm=PLUMB) is render(g)."""
    g = build()
    assert weigh.render(g, frm=weigh.PLUMB) == weigh.render(g)
    assert weigh.render(g, "officers", frm=weigh.PLUMB) == weigh.render(g, "officers")


def test_r5_comparison_view_real_data():
    """R5: from body/lbc-1689 on the real data: no site exclusion, the three Bodies ranked, lbc-1689 itself not."""
    g = real()
    lbc = U("body/lbc-1689")
    out = weigh.render(g, frm=lbc)
    assert unchurches.HEADING not in out and unchurches.UNSIGNED not in out
    res = weigh.weigh(g, frm=lbc)
    ranked = {b for b, _ in res["ranked"]}
    assert {U("body/wcf"), U("body/augsburg"), U("body/apology-1531")} <= ranked
    assert lbc not in ranked
    assert res["excluded"] == {}


# ---- R6 -------------------------------------------------------------------------------------------------

def _stated_graph(**kw):
    g = minimal()
    return add(g, stated_ttl("gill", "baptism", "immersion", **kw))


def _violates(g, node="body/gill"):
    violations, _ = report(g)
    return str(U(node)) in focus_nodes(violations)


def test_r6_stated_without_source_is_a_violation():
    """R6: a stated gc:unchurches whose axiom has no dcterms:source."""
    assert _violates(_stated_graph(source=False))


def test_r6_stated_without_locator_is_a_violation():
    """R6: a stated gc:unchurches whose axiom has no gc:locator."""
    assert _violates(_stated_graph(locator=False))


def test_r6_stated_with_both_conforms():
    """R6: with source and locator it conforms."""
    violations, _ = report(_stated_graph())
    assert violations == []


def test_r6_literal_object_is_a_violation():
    """R6: a literal object of gc:unchurches."""
    g = minimal()
    add(g, '<body/gill> gc:unchurches "true"^^xsd:boolean .')
    assert _violates(g)


# ---- R7 -------------------------------------------------------------------------------------------------

PL_STMT = "<body/plumb-line> gc:unchurches <position/baptism/immersion> ."
GILL_STMT = "<body/gill> gc:unchurches <position/baptism/immersion> ."


def test_r7_one_form_accepted():
    """R7: the plumb-line's statement in its graph, and another Body's in its own graph, pass."""
    ingest.code_checks(ck_build(plumb_extra=PL_STMT))
    ingest.code_checks(ck_build(plumb_extra=PL_STMT, fixture_extra=GILL_STMT))


def test_r7_boolean_form_refused():
    """R7: the old form (a Position true) is an error."""
    refused(ck_build(plumb_extra='<position/baptism/immersion> gc:unchurches "true"^^xsd:boolean .'),
            "not a gc:Body", "must be a gc:Position")


def test_r7_plumb_line_statement_outside_its_graph_refused():
    """R7: body/plumb-line's statement outside the plumb-line graph."""
    refused(ck_build(fixture_extra=PL_STMT), "not plumb-line")


def test_r7_other_body_in_plumb_line_graph_refused():
    """R7: another Body's statement inside the plumb-line graph."""
    refused(ck_build(plumb_extra=GILL_STMT), "only body/plumb-line's statements belong there")


def test_r7_non_position_object_refused():
    """R7: an object that is not a gc:Position."""
    refused(ck_build(plumb_extra="<body/plumb-line> gc:unchurches <locus/baptism> ."), "must be a gc:Position")


def test_r7_non_body_subject_refused():
    """R7: a subject that is not a gc:Body."""
    refused(ck_build(fixture_extra="<position/baptism/immersion> gc:unchurches <position/baptism/immersion> ."),
            "not a gc:Body")


def test_r7_shapes_one_and_two_still_apply():
    """R7: shape 1 (plumb-line does not hold it forbidden), no tier, tier third."""
    refused(ck_build(plumb_extra=PL_STMT, forbid=False), "shape 1")
    refused(ck_build(plumb_extra=PL_STMT, tier=""), "shape 2")
    refused(ck_build(plumb_extra=PL_STMT, tier="<locus/baptism> gc:tier <vocab/tier/third> ."), "tier third")


def test_r7_real_data_passes():
    """R7/R9: the committed data passes every code check."""
    ingest.code_checks(ingest.load_dataset())


# ---- R8 -------------------------------------------------------------------------------------------------

def test_r8_stated_judgment_excludes_nothing():
    """R8: case-a states a judgment on a Position case-c holds taught; weigh's ranked and excluded are unchanged."""
    base = weigh.weigh(build())
    withs = weigh.weigh(build(extra=stated_ttl("case-a", "baptism-subjects", "professing-believers-only")))
    assert withs["ranked"] == base["ranked"]
    assert withs["excluded"] == base["excluded"]
    assert set(base["excluded"]) == {U("body/case-b")}
    assert unchurches.flagged(build(extra=stated_ttl("case-a", "baptism-subjects", "infants"))) == \
        unchurches.flagged(build())
