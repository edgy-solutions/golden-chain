"""weigh: cost from the user into the Body, against body/plumb-line (ADR-0003 section 5, 5a, R2.3-R2.7)."""

from rdflib import Graph, Literal
from rdflib.namespace import XSD

from goldenchain import ingest, unchurches, weigh
from gcfix import GC, U, add, dataset_with

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


def holding(body, locus, pos, mod, src=None, scope=None):
    s = src or f"<source/{body}/x>"
    sc = f" ; gc:scope <vocab/scope/{scope}>" if scope else ""
    return (f"<body/{body}> gc:holds <holding/{body}/{pos}> .\n"
            f"<holding/{body}/{pos}> a gc:Holding ; gc:position <position/{locus}/{pos}> ; "
            f"gc:modality <vocab/modality/{mod}> ; dcterms:source {s}{sc} .\n")


def build(bodies=None, tier=None, clarity=None, extra=""):
    """tier/clarity: dict locus -> value or None (to omit). Returns the derived union graph."""
    tier = {l: "second" for l in LOCI} | (tier or {})
    clarity = {l: "settled" for l in LOCI} | (clarity or {})
    ttl_pl = "<body/plumb-line> a gc:Editorial .\n"
    ttl_fx = ""
    for l in LOCI:
        ttl_pl += f"<locus/{l}> a gc:Locus"
        if tier[l]:
            ttl_pl += f" ; gc:tier <vocab/tier/{tier[l]}>"
        if clarity[l]:
            ttl_pl += f" ; gc:clarity <vocab/clarity/{clarity[l]}>"
        ttl_pl += " .\n"
    for l, p, _ in PL:
        ttl_fx += f"<position/{l}/{p}> a gc:Position ; gc:answers <locus/{l}> .\n"
        ttl_pl += holding("plumb-line", l, p, _, SRC)
    for p in ("believers-and-their-infants", "infants"):
        ttl_pl += f'<position/baptism-subjects/{p}> gc:unchurches "true"^^xsd:boolean .\n'
    for name, hs in (BODIES if bodies is None else bodies).items():
        ttl_fx += f"<body/{name}> a gc:Confession .\n"
        for l, p, m in hs:
            src = "<source/case-b/28>" if name == "case-b" and p == "believers-and-their-infants" else None
            ttl_fx += holding(name, l, p, m, src)
    ds = dataset_with(add(Graph(), ttl_fx + extra))
    pl = ds.graph(ingest.PLUMB_LINE)
    for t in add(Graph(), ttl_pl):
        pl.add(t)
    return ingest.union(ingest.derive_rdflib(ds))


W1 = """body/case-a [Confession] ranked
  walls: 0
  cost: 0.2500 over 4 loci; coverage: 1.0000
  breaks: 1
    - locus/worship (tier second): 0.75"""

W2 = """body/case-b [Confession] not ranked
  Not a church by this plumb-line's standard: churches subscribing to this standard are not churches by this plumb-line's standard.
    - position/baptism-subjects/believers-and-their-infants required (source/case-b/28); flagged by the plumb-line at source/plumb-line/sitting-fixture
  Its members' standing as Christians is not asserted either way."""

W3 = """body/case-c [Confession] ranked
  walls: 1
    - locus/baptism-validity (tier second): position/baptism-validity/church-of-our-order required against plumb-line forbidden
  cost: 0.0000 over 3 loci; coverage: 1.0000
  breaks: 1
    - locus/baptism-validity (tier second): WALL"""


def test_w1_w2_w3():
    g = build()
    assert weigh.render_body(g, U("body/case-a")) == W1
    assert weigh.render_body(g, U("body/case-b")) == W2
    assert weigh.render_body(g, U("body/case-c")) == W3


def test_w4_distinct_and_order():
    g = build()
    r = {b: weigh.render_body(g, U(f"body/{b}")) for b in BODIES}
    assert len(set(r.values())) == 3
    res = weigh.weigh(g)
    assert [b for b, _ in res["ranked"]] == [U("body/case-a"), U("body/case-c")]
    assert set(res["excluded"]) == {U("body/case-b")}
    txt = weigh.render(g)
    assert txt.startswith("Weigh against body/plumb-line (scope members)\n\n")
    assert txt.index("case-a") < txt.index("case-c") < txt.index(unchurches.HEADING)


def check_w5(g):
    for b, rows in unchurches.excluded(g).items():
        by = {l: t for l, t, v in weigh.score(g, b)["breaks"]}
        for r in rows:
            locus = g.value(r["position"], GC.answers)
            assert locus in by
            assert by[locus] != "third"


def test_w5():
    g = build()
    s = weigh.score(g, U("body/case-b"))
    assert (U("locus/baptism-subjects"), "second", "WALL") in s["breaks"]
    check_w5(g)


def test_constants():
    assert weigh.CELL == {
        "obligatory": {"required": 0, "taught": 0, "tolerated": 0.25, "forbidden": "WALL"},
        "permitted": {"required": 0.1, "taught": 0, "tolerated": 0, "forbidden": 0.05},
        "forbidden": {"required": "WALL", "taught": 0.75, "tolerated": 0.5, "forbidden": 0}}
    assert weigh.USER_OF == {"required": "obligatory", "taught": "obligatory",
                             "tolerated": "permitted", "forbidden": "forbidden"}
    assert weigh.TIER_W == {"first": 9, "second": 3, "third": 1}
    assert weigh.CLARITY_W == {"open": 0, "contested": 1, "settled": 1}
    assert weigh.MAX_CELL == 0.75


def test_inheritance():
    extra = ("<body/child-b> a gc:Confession ; gc:childOf <body/case-b> .\n"
             "<body/child-own> a gc:Confession ; gc:childOf <body/case-b> .\n"
             + holding("child-own", "baptism-subjects", "professing-believers-only", "taught"))
    res = weigh.weigh(build(extra=extra))
    assert U("body/child-b") in res["excluded"]
    assert res["excluded"][U("body/child-b")][0]["own"] is False
    assert U("body/child-own") not in res["excluded"]
    assert U("body/child-own") in [b for b, _ in res["ranked"]]


def test_scope():
    g = build(bodies={"off": []}, extra="<body/off> a gc:Confession .\n" + holding(
        "off", "baptism-validity", "church-of-our-order", "required", scope="officers"))
    sm = weigh.score(g, U("body/off"))
    so = weigh.score(g, U("body/off"), "officers")
    assert sm["walls"] == [] and sm["coverage"] == 0.0
    assert len(so["walls"]) == 1


def test_unknown():
    g = build(bodies={"mute": []})
    assert weigh.render_body(g, U("body/mute")).splitlines()[2] == \
        "  cost: n/a over 0 loci; coverage: 0.0000"


def test_open_locus():
    g = build(clarity={"baptism-validity": "open"})
    s = weigh.score(g, U("body/case-c"))
    assert s["walls"] == [] and s["breaks"] == []
    assert s["n_cost"] == 3 and s["coverage"] == 1.0


def test_untiered():
    g = build(tier={"worship": None})
    s = weigh.score(g, U("body/case-a"))
    assert s["untiered"] == [U("locus/worship")]
    assert s["cost"] == 0 and s["n_cost"] == 3
    assert "  untiered: locus/worship" in weigh.render_body(g, U("body/case-a"))


def test_real_data_smoke():
    ds = ingest.load_dataset()
    g = ingest.union(ingest.derive_rdflib(ds))
    assert weigh.weigh(g)["excluded"] == {}
    pl = ds.graph(ingest.PLUMB_LINE)
    for p in ("believers-and-their-infants", "infants"):
        pl.add((U(f"position/baptism-subjects/{p}"), GC.unchurches, Literal(True, datatype=XSD.boolean)))
    g = ingest.union(ingest.derive_rdflib(ds))
    assert weigh.render(g)
    check_w5(g)
