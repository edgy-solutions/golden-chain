"""ADR-0007 as locked 2026-11-22: congregations. AV1 to AV7 (AV8 is the full suite and the real-data checks).

Synthetic only: the parents P1 and P2, the Loci L1..L6 and the Example Church are built here. No church content.
"""

import datetime
import json
import sys
from pathlib import Path

import pytest
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, RDF

ROOT = Path(__file__).resolve().parent.parent
for sub in ("tools/console/specs", "tools/console", "tools"):
    sys.path.insert(0, str(ROOT / sub))
import build  # noqa: E402
import congregation as cform  # noqa: E402
import ingest as console_ingest  # noqa: E402
from column_rule import Fail  # noqa: E402

from goldenchain import ingest as gc_ingest  # noqa: E402
from goldenchain import weigh  # noqa: E402
from gcfix import GC, PROPOSED, U, add, dataset_with, eff, inconsistencies, report  # noqa: E402

from gcfix import _ordinal  # noqa: E402

ORD = _ordinal()
SLUG = "example-church-sometown"
CB = f"body/congregation/{SLUG}"
STMT = f"source/congregation/{SLUG}/statement"
PK = f"source/congregation/{SLUG}/personal-knowledge"
CHRIS = "gc:status <vocab/status/proposed> ; gc:proposedBy <agent/chris>"
NOW = datetime.datetime(2026, 11, 22, 12, 0, tzinfo=datetime.timezone.utc)
CLEAN = {"commit": "abc123", "dirty": False, "porcelain": 0}

WORLD = """@prefix owl: <http://www.w3.org/2002/07/owl#> .
<heading/h> a gc:Heading ; rdfs:label "Heading" .
<agent/build> a gc:Agent .
<agent/architect> a gc:Agent .
<agent/chris> a gc:Agent ; rdfs:label "Chris" .
"""


def parents_ttl(loci=range(1, 7), one_parent=False):
    t = WORLD + (f'<passage/kjv/Matt.28.19> a gc:Passage ; gc:versification "kjv" ; gc:book "Matt" ; '
                 f'gc:osisRef "Matt.28.19" ; gc:startOrdinal {ORD} ; gc:endOrdinal {ORD} .\n')
    for i in loci:
        t += (f'<locus/l{i}> a gc:Locus ; rdfs:label "Question {i}" ; skos:notation "{i}" ; '
              f'gc:question "Question {i}?"@en ; gc:underHeading <heading/h> .\n')
        for p in "ab":
            t += (f'<position/l{i}/{p}> a gc:Position ; rdfs:label "Answer {p.upper()} {i}" ; '
                  f"gc:answers <locus/l{i}> ; {PROPOSED} .\n")
            t += (f"<argument/p1/x/{i}{'ab'.index(p)}1> a gc:Argument ; gc:source <source/p1/x> ; "
                  f"gc:supports <position/l{i}/{p}> ; gc:cites <passage/kjv/Matt.28.19> ; {PROPOSED} .\n")
    for p in ("p1",) if one_parent else ("p1", "p2"):
        t += (f'<source/{p}> a gc:SourceWork ; rdfs:label "Source {p}" .\n'
              f"<source/{p}/x> a gc:SourceDivision ; dcterms:isPartOf <source/{p}> .\n"
              f'<body/{p}> a gc:Confession ; rdfs:label "Parent {p[1]}" .\n')
    return t


def hold(body, locus, pos, src, extra="", status=PROPOSED, mod="taught"):
    h = f"holding/{body}/l{locus}/{pos}"
    return (f"<body/{body}> gc:holds <{h}> .\n" if not body.startswith("congregation") else f"<{CB}> gc:holds <{h}> .\n") + \
        f"<{h}> a gc:Holding ; gc:position <position/l{locus}/{pos}> ; gc:modality <vocab/modality/{mod}> ; " \
        f"dcterms:source <{src}> ; {extra} {status} .\n"


def parent_holdings(loci=(1, 2, 3, 4, 6), one_parent=False):
    """Agree on L1..L3; differ on L4 and L6; L5 silent."""
    t = ""
    for i in loci:
        t += hold("p1", i, "a", "source/p1/x")
        if not one_parent:
            t += hold("p2", i, "b" if i in (4, 6) else "a", "source/p2/x")
    return t


def church_ttl(except_l4=False, own_l3=False, ratified=False):
    t = ("@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
         f'<{CB}> a gc:Congregation ; rdfs:label "Example Church, Sometown" ; gc:childOf <body/p1>, <body/p2> ; '
         f'dcterms:source <{STMT}> ; dcterms:created "2026-11-22"^^xsd:date ; {CHRIS}'
         + (" ; gc:ratifiedBy <agent/chris>" if ratified else "") + " .\n"
         f'<{STMT}> a gc:SourceWork ; rdfs:label "Example Statement of Faith" ; '
         f"rdfs:seeAlso <https://example.org/statement> ; gc:readOn \"2026-11-20\"^^xsd:date ; "
         f"gc:archivedCopy <https://example.org/archive/statement> .\n"
         f'<{PK}> a gc:PersonalKnowledge ; rdfs:label "Personal knowledge" ; dcterms:creator <agent/chris> ; '
         f'dcterms:created "2026-11-22"^^xsd:date .\n')
    t += hold(f"congregation/{SLUG}", 2, "b", STMT, 'gc:locator "Art. 2" ;', CHRIS)
    if not except_l4:
        t += hold(f"congregation/{SLUG}", 4, "b", STMT, 'gc:locator "Art. 4" ;', CHRIS)
    t += hold(f"congregation/{SLUG}", 5, "a", PK, "", CHRIS)
    for locus in ([3] if not own_l3 else []) + ([4] if except_l4 else []):
        t += (f"<{CB}> gc:exceptsLocus <locus/l{locus}> .\n"
              f"<axiom/exceptsLocus/{SLUG}/l{locus}> a owl:Axiom ; owl:annotatedSource <{CB}> ; "
              f"owl:annotatedProperty gc:exceptsLocus ; owl:annotatedTarget <locus/l{locus}> ; "
              f'rdfs:comment "Excepted." ; dcterms:source <{STMT}> ; gc:locator "Art. {locus}" ; {CHRIS} .\n')
    return t


def graph(*parts):
    g = Graph()
    for p in parts:
        add(g, p)
    return g


def derived(g, plumb=""):
    ds = dataset_with(g)
    if plumb:
        pl = ds.graph(gc_ingest.PLUMB_LINE)
        for t in add(Graph(), plumb):
            pl.add(t)
    return gc_ingest.derive_rdflib(ds)


def holdings_of(d, body):
    return {str(h) for h in d.graph(U("graph/derived/inheritance")).objects(U(body), GC.effectivelyHolds)}


def fixture(**kw):
    return graph(parents_ttl(), parent_holdings(), church_ttl(**kw))


# ---- AV1 --------------------------------------------------------------------------------------------

def test_av1_effective_holdings():
    got = holdings_of(derived(fixture()), CB)
    want = {f"{gc_ingest.B}{x}" for x in (
        "holding/p1/l1/a", "holding/p2/l1/a", "holding/p1/l6/a", "holding/p2/l6/b",
        f"holding/congregation/{SLUG}/l2/b", f"holding/congregation/{SLUG}/l4/b", f"holding/congregation/{SLUG}/l5/a")}
    assert got == want
    assert not any("/l3/" in h for h in got)  # L3: none, the cell is unknown


# ---- AV2 --------------------------------------------------------------------------------------------

def differs(d):
    return {str(s).rsplit("/", 1)[1] for s in inconsistencies(d)
            if "/inconsistency/" + CB.split("body/")[1] + "/parents-differ/" in str(s)}


def test_av2_parents_differ_fires_on_l6_only():
    assert differs(derived(fixture())) == {"l6"}


def test_av2_parents_differ_still_fires_on_an_excepted_locus():
    g = graph(parents_ttl(), parent_holdings(), church_ttl(except_l4=True))
    assert differs(derived(g)) == {"l4", "l6"}


# ---- AV3 --------------------------------------------------------------------------------------------

def plumb_for(loci_tiers):
    t = "<body/plumb-line> a gc:Editorial .\n"
    for i, tier in loci_tiers.items():
        t += f"<locus/l{i}> a gc:Locus ; gc:tier <vocab/tier/{tier}> ; gc:clarity <vocab/clarity/settled> .\n"
        t += (f"<body/plumb-line> gc:holds <holding/plumb-line/l{i}/a> .\n<holding/plumb-line/l{i}/a> a gc:Holding ; "
              f"gc:position <position/l{i}/a> ; gc:modality <vocab/modality/taught> ; "
              f"dcterms:source <source/plumb-line/x> .\n")
    return t


ONE_PARENT_CHURCH = (f'<{CB}> a gc:Congregation ; rdfs:label "Example Church, Sometown" ; gc:childOf <body/p1> ; '
                     f'dcterms:created "2026-11-22"^^xsd:date ; {CHRIS} .\n')
EXCEPT_L3 = (f"<{CB}> gc:exceptsLocus <locus/l3> .\n")


def one_parent(with_exception):
    g = graph(parents_ttl(range(1, 4), one_parent=True), parent_holdings((1, 3), one_parent=True),
              ONE_PARENT_CHURCH + (EXCEPT_L3 if with_exception else ""))
    return gc_ingest.union(derived(g, plumb_for({1: "first", 3: "second"})))


def test_av3_coverage_counts_the_excepted_locus_in_the_denominator_only():
    plain, excepted = one_parent(False), one_parent(True)
    c = U(CB)
    w1, w3 = weigh._weight(plain, U("locus/l1"))[0], weigh._weight(plain, U("locus/l3"))[0]
    sp, se = weigh.score(plain, c), weigh.score(excepted, c)
    assert sp["coverage"] == pytest.approx(1.0)
    assert se["coverage"] == pytest.approx(w1 / (w1 + w3))
    assert sp["coverage"] - se["coverage"] == pytest.approx(w3 / (w1 + w3))
    assert se["n_cost"] == 1 and se["walls"] == []
    assert all(b[0] != U("locus/l3") for b in se["breaks"])
    assert not [h for h in excepted.objects(c, GC.effectivelyHolds)
                if (h, GC.position, U("position/l3/a")) in excepted]  # never shown as tolerated


# ---- AV4 --------------------------------------------------------------------------------------------

def test_av4_weigh_renders_the_congregation():
    g = gc_ingest.union(derived(fixture(), plumb_for({i: "second" for i in range(1, 7)})))
    text = weigh.render_body(g, U(CB))
    lines = text.split("\n")
    assert lines[0] == f"{CB} [Congregation] ranked"
    assert lines[1] == "  subscribes to: Parent 1 (body/p1); Parent 2 (body/p2)"
    assert "  exceptions: 1" in lines and "    - 3 Question 3 (locus/l3)" in lines
    assert any(l.startswith("  entered by: Chris, on 2026-11-22, from: ") for l in lines)
    entered = next(l for l in lines if l.startswith("  entered by"))
    assert "Example Statement of Faith (https://example.org/statement, read 2026-11-20, archived " \
           "https://example.org/archive/statement)" in entered
    assert "personal knowledge (Chris)" in entered
    assert "  confirmed by: not yet confirmed (every row here is proposed)" in lines
    assert "  correction: " + weigh.CORRECTION in lines
    cells = lines[lines.index("  cells:") + 1:]
    assert cells == [
        "    - locus/l1: inherited from body/p1", "    - locus/l1: inherited from body/p2",
        "    - locus/l2: own (statement, Art. 2)", "    - locus/l3: excepted, unknown",
        "    - locus/l4: own (statement, Art. 4)", "    - locus/l5: own (personal knowledge)",
        "    - locus/l6: inherited from body/p1", "    - locus/l6: inherited from body/p2"]
    g2 = gc_ingest.union(derived(fixture(ratified=True), plumb_for({i: "second" for i in range(1, 7)})))
    assert "  confirmed by: Chris" in weigh.render_body(g2, U(CB)).split("\n")


def test_av4_other_bodies_render_unchanged_by_the_congregation_lines():
    g = gc_ingest.union(derived(fixture(), plumb_for({i: "second" for i in range(1, 7)})))
    text = weigh.render_body(g, U("body/p1"))
    assert "subscribes to" not in text and "cells:" not in text and "correction:" not in text


# ---- AV5 --------------------------------------------------------------------------------------------

def test_av5_excluded_by_an_inherited_holding_says_so():
    plumb = (plumb_for({1: "second"}) + '<position/l1/a> gc:unchurches "true"^^xsd:boolean .\n')
    g = graph(parents_ttl(range(1, 2), one_parent=True), hold("p1", 1, "a", "source/p1/x"), ONE_PARENT_CHURCH)
    text = weigh.render_body(gc_ingest.union(derived(g, plumb)), U(CB))
    assert text.split("\n")[0] == f"{CB} [Congregation] not ranked"
    reason = next(l for l in text.split("\n") if l.startswith("    - position/l1/a"))
    assert "(source/p1/x)" in reason and reason.endswith(" inherited from body/p1")
    assert "  cells:" in text and "    - locus/l1: inherited from body/p1" in text
    own = graph(parents_ttl(range(1, 2), one_parent=True), hold("p1", 1, "a", "source/p1/x"),
                ONE_PARENT_CHURCH + hold(f"congregation/{SLUG}", 1, "a", STMT, 'gc:locator "Art. 1" ;', CHRIS)
                + f'<{STMT}> a gc:SourceWork ; rdfs:label "S" .\n')
    t2 = weigh.render_body(gc_ingest.union(derived(own, plumb)), U(CB))
    assert not any("inherited from" in l for l in t2.split("\n") if l.startswith("    - position/"))


# ---- AV6 --------------------------------------------------------------------------------------------

def msgs(g):
    v, _ = report(g)
    return [m for _, _, m in v]


def test_av6_the_av1_fixture_conforms():
    assert report(fixture())[0] == []


def has(g, tag):
    return any(tag in m for m in msgs(g))


def test_av6a_exception_and_own_holding_on_one_locus():
    g = fixture()
    add(g, hold(f"congregation/{SLUG}", 3, "b", STMT, 'gc:locator "Art. 3" ;', CHRIS))
    assert has(g, "AV6 (a)")


def test_av6b_excepts_locus_on_a_non_congregation():
    g = fixture()
    add(g, "<body/p1> gc:exceptsLocus <locus/l1> .\n")
    assert has(g, "AV6 (b)")


def test_av6c_congregation_holding_without_source():
    g = fixture()
    g.remove((U(f"holding/congregation/{SLUG}/l2/b"), DCTERMS.source, None))
    assert has(g, "AV6 (c)")


@pytest.mark.parametrize("pred", [DCTERMS.source, GC.status, GC.proposedBy])
def test_av6d_exception_without_its_axiom_provenance(pred):
    g = fixture()
    g.remove((U(f"axiom/exceptsLocus/{SLUG}/l3"), pred, None))
    assert has(g, "AV6 (d)")


def test_av6d_exception_without_an_axiom():
    g = fixture()
    g.remove((U(f"axiom/exceptsLocus/{SLUG}/l3"), None, None))
    assert has(g, "AV6 (d)")


def test_av6e_statement_based_holding_or_exception_without_locator():
    g = fixture()
    g.remove((U(f"holding/congregation/{SLUG}/l2/b"), GC.locator, None))
    assert has(g, "AV6 (e)")
    g = fixture()
    g.remove((U(f"axiom/exceptsLocus/{SLUG}/l3"), GC.locator, None))
    assert has(g, "AV6 (e)")


def test_av6_a_personal_knowledge_holding_needs_no_locator():
    assert report(fixture())[0] == []  # l5 cites personal knowledge, no locator


def test_av6_congregation_and_personal_knowledge_needs():
    for pred in (RDF.type, GC.childOf, DCTERMS.created, GC.proposedBy):
        g = fixture()
        if pred == RDF.type:
            g.remove((U(CB), pred, GC.Congregation))
            g.add((U(CB), pred, GC.Body))
        else:
            g.remove((U(CB), pred, None))
        assert report(g)[0], pred
    g = fixture()
    g.remove((U(PK), DCTERMS.creator, None))
    assert report(g)[0]


# ---- AV7: the form, the console, the ingest -------------------------------------------------------------

def parents_graph():
    return graph(parents_ttl(), parent_holdings())


def spec_of(g=None, parents=("body/p1", "body/p2")):
    d = gc_ingest.union(derived(g or parents_graph()))
    return cform.form_spec(d, [U(p) for p in parents])


def rows_of(spec):
    return {r["id"]: r for s in spec["sections"] for r in s["rows"]}


def test_av7_spec_passes_every_build_check_and_is_built_from_the_data():
    spec = spec_of()
    build.check_spec(spec)
    rows = rows_of(spec)
    assert [s["id"] for s in spec["sections"]] == ["church", "parents-speak", "parents-silent"]
    assert [r for r in rows if r.startswith("locus.")] == [f"locus.l{i}" for i in (1, 2, 3, 4, 6, 5)]
    agree, differ = rows["locus.l1"]["fields"][0], rows["locus.l4"]["fields"][0]
    assert agree["options"] == ["as the parents", "excepts: holds another", "excepts: no alternative stated"]
    assert differ["options"] == ["holds this one", "excepts: no alternative stated"]
    assert "differ here" in differ["plain"]
    assert any("Answer A 1 (" in c and "Parent 1 holds" in c for c in rows["locus.l1"]["context"])
    assert rows["locus.l5"]["fields"][0]["id"] == "own"
    assert rows["locus.l5"]["fields"][0]["empty_means"] == "unanswered"
    assert rows["locus.l5"]["fields"][0]["options"] == ["Answer A 5", "Answer B 5"]
    assert rows["locus.l1"]["locus"] == f"{gc_ingest.B}locus/l1"
    assert spec["congregation"]["parents"] == [{"iri": f"{gc_ingest.B}body/p1", "label": "Parent 1"},
                                               {"iri": f"{gc_ingest.B}body/p2", "label": "Parent 2"}]
    for r in rows.values():
        for f in r["fields"]:
            if f["id"] in ("instead", "modality", "scope", "own"):
                assert set(f["iris"]) == set(f["options"])


def test_av7_one_parent_says_the_parent():
    g = graph(parents_ttl(one_parent=True), parent_holdings(one_parent=True))
    spec = spec_of(g, ("body/p1",))
    build.check_spec(spec)
    f = rows_of(spec)["locus.l1"]["fields"][0]
    assert f["options"][0] == "as the parent" and "the parent" in f["plain"]
    assert "the parents" not in f["plain"]


def test_av7_the_builder_refuses_a_non_body_and_no_parent():
    d = gc_ingest.union(derived(parents_graph()))
    with pytest.raises(Fail):
        cform.form_spec(d, [U("locus/l1")])
    with pytest.raises(Fail):
        cform.form_spec(d, [])


def pick(spec, rid, fid, word):
    f = next(f for f in rows_of(spec)[rid]["fields"] if f["id"] == fid)
    return next(o for o in f["options"] if word in o)


def full_answers(spec):
    stm, pk = "the church's statement", "personal knowledge"
    mod, scope = (lambda r: pick(spec, r, "modality", "taught")), (lambda r: pick(spec, r, "scope", "all"))
    return {
        "church.name": {"name": "Example Church, Sometown"},
        "church.basis": {"basis": "its published statement"},
        "church.statement": {"title": "Example Statement of Faith", "url": "https://example.org/statement",
                             "read": "2026-11-20", "archived": "https://example.org/archive/statement"},
        "church.parents": {"where": "Art. 1"},
        "locus.l1": {"answer": "as the parents"},
        "locus.l2": {"answer": "excepts: holds another", "instead": "Answer B 2", "modality": mod("locus.l2"),
                     "scope": scope("locus.l2"), "basis": stm, "where": "Art. 2"},
        "locus.l3": {"answer": "excepts: no alternative stated", "basis": stm, "where": "Art. 3"},
        "locus.l4": {"answer": "holds this one", "instead": "Answer B 4", "modality": mod("locus.l4"),
                     "scope": scope("locus.l4"), "basis": stm, "where": "Art. 4"},
        "locus.l5": {"own": "Answer A 5", "modality": mod("locus.l5"), "scope": scope("locus.l5"), "basis": pk},
    }


def make_export(spec, man, answers, states=None):
    rows = {}
    for r in (r for s in spec["sections"] for r in s["rows"]):
        st = (states or {}).get(r["id"], "verdict")
        vals = {f["id"]: None for f in r["fields"]}
        if st == "verdict":
            vals.update(answers.get(r["id"], {}))
        rows[r["id"]] = {"state": st, "values": vals, "note": ""}
    return {"format": "golden-chain-console-verdicts/1", "kind": spec["kind"], "build_hash": man["build_hash"],
            "spec_sha256": man["spec_sha256"], "code_sha256": man["code_sha256"],
            "run_header": man["local"]["run_header"] if "local" in man else spec["run_header"],
            "images": dict(man["images"]), "rows": rows, "signature": {"name": "Chris", "date": "2026-11-22"},
            "complete": True, "exported_utc": "2026-11-22T10:00:00Z"}


@pytest.fixture
def sit(tmp_path, monkeypatch):
    monkeypatch.setattr(build, "git_state", lambda repo: dict(CLEAN))
    monkeypatch.setattr(console_ingest, "HANDOFF", tmp_path / "handoff")
    monkeypatch.setattr(console_ingest, "DATA_DIR", tmp_path / "data")
    spec = spec_of()
    p = tmp_path / "spec.json"
    p.write_bytes(build.canon(spec))
    made = build.build(p, tmp_path / "out")
    man = json.loads(made["manifest"].read_text(encoding="utf-8"))
    return {"spec": spec, "made": made, "man": man, "dir": tmp_path}


def sign(s, answers=None, states=None, ttl_out="default", name="v.json", **kw):
    ans = full_answers(s["spec"]) if answers is None else answers
    p = s["dir"] / name
    p.write_text(json.dumps(make_export(s["spec"], s["man"], ans, {"locus.l6": "abstain"} if states is None else states)),
                 encoding="utf-8")
    if ttl_out == "default":
        ttl_out = s["dir"] / "church.ttl"
    return console_ingest.ingest(p, s["made"]["manifest"], out_dir=s["dir"] / "signed", ttl_out=ttl_out,
                                 now=NOW, **kw)


def test_av7_ingest_reproduces_av1(sit):
    made = sign(sit)
    ttl = sit["dir"] / "church.ttl"
    assert ttl in made and any(p.name.startswith("SIGNED_congregation_") for p in made)
    g = graph(parents_ttl(), parent_holdings())
    g.parse(ttl, format="turtle")
    assert report(g)[0] == []
    got = holdings_of(derived(g), CB)
    want = holdings_of(derived(fixture()), CB)
    assert got == want
    t = ttl.read_text(encoding="utf-8")
    assert "gc:ratifiedBy" not in t.replace("no gc:ratifiedBy", "")
    assert t.count("gc:proposedBy <agent/chris>") == 1 + 4  # congregation, 3 holdings, 1 axiom
    assert f"SIGNED_congregation_{sit['man']['build16']}.md" in t.split("\n")[0]
    assert sit["man"]["build_hash"] in t.split("\n")[1]


def test_av7_output_is_deterministic(sit):
    sign(sit)
    first = (sit["dir"] / "church.ttl").read_bytes()
    sign(sit, ttl_out=sit["dir"] / "second.ttl")
    assert (sit["dir"] / "second.ttl").read_bytes() == first
    assert b"\r" not in first


def test_av7_record_lists_what_is_minted(sit):
    sign(sit)
    md = next((sit["dir"] / "handoff").glob("SIGNED_congregation_*.md")).read_text(encoding="utf-8")
    assert "## What this record mints" in md and "## Questions for the architect" in md
    assert "locus.l6: abstain, nothing minted" in md


def test_av7_other_as_written_mints_nothing_for_that_row(sit):
    ans = full_answers(sit["spec"])
    ans["locus.l2"] = {"answer": {"other": "It holds a third thing"}}
    sign(sit, ans)
    t = (sit["dir"] / "church.ttl").read_text(encoding="utf-8")
    assert "/l2/" not in t and "/l4/b" in t
    md = next((sit["dir"] / "handoff").glob("SIGNED_congregation_*.md")).read_text(encoding="utf-8")
    assert "It holds a third thing" in md.split("## Questions for the architect")[1]


def test_av7_other_in_the_church_section_mints_nothing_at_all(sit):
    ans = full_answers(sit["spec"])
    ans["church.basis"] = {"basis": {"other": "It has a covenant only"}}
    sign(sit, ans)
    assert not (sit["dir"] / "church.ttl").exists()
    md = next((sit["dir"] / "handoff").glob("SIGNED_congregation_*.md")).read_text(encoding="utf-8")
    assert "nothing at all is minted" in md and "It has a covenant only" in md


def mut(rid, **kw):
    def f(a):
        a[rid] = {**a[rid], **kw}
    return f


def drop(rid, *keys):
    def f(a):
        a[rid] = {k: v for k, v in a[rid].items() if k not in keys}
    return f


def both(*fs):
    def f(a):
        for x in fs:
            x(a)
    return f


REFUSALS = {
    "statement without url": mut("church.statement", url=None),
    "statement without archived": mut("church.statement", archived=None),
    "statement without title": mut("church.statement", title=None),
    "date read not a date": mut("church.statement", read="20 Nov 2026"),
    "date read impossible": mut("church.statement", read="2026-13-40"),
    "url not a url": mut("church.statement", url="not a url"),
    "personal basis with statement fields": mut("church.basis", basis="personal knowledge only"),
    "personal basis, row cites the statement": both(
        mut("church.basis", basis="personal knowledge only"),
        mut("church.statement", title=None, url=None, read=None, archived=None),
        mut("church.parents", where=None)),
    "holds another without modality": mut("locus.l2", modality=None),
    "holds another without instead": mut("locus.l2", instead=None),
    "holds another without scope": mut("locus.l2", scope=None),
    "holds another without basis": mut("locus.l2", basis=None),
    "holds this one without modality": mut("locus.l4", modality=None),
    "statement basis without where": mut("locus.l2", where=None),
    "no alternative without basis": mut("locus.l3", basis=None),
    "no alternative, statement, without where": mut("locus.l3", where=None),
    "no alternative with a position": mut("locus.l3", instead="Answer B 3"),
    "as the parents with a field": mut("locus.l1", modality="x"),
    "personal basis with where": mut("locus.l5", where="Art. 9"),
    "silent row filled but no position": mut("locus.l5", own=None),
    "name gives no slug": mut("church.name", name="!!!"),
}


@pytest.mark.parametrize("case", sorted(REFUSALS))
def test_av7_a_broken_condition_is_refused_and_nothing_is_written(sit, case):
    ans = full_answers(sit["spec"])
    REFUSALS[case](ans)
    with pytest.raises(Fail):
        sign(sit, ans)
    assert not (sit["dir"] / "church.ttl").exists()
    assert not (sit["dir"] / "signed").exists()
    assert not (sit["dir"] / "handoff").exists()


def test_av7_write_without_ttl_out_goes_to_data_and_never_overwrites(sit):
    sign(sit, ttl_out=None, write=True)
    out = sit["dir"] / "data" / f"congregation-{SLUG}.ttl"
    assert out.exists()
    with pytest.raises(Fail):
        sign(sit, ttl_out=None, write=True)


def test_av7_without_ttl_out_or_write_nothing_goes_to_data_or_handoff(sit):
    made = sign(sit, ttl_out=None)
    assert [p.parent for p in made] == [sit["dir"] / "signed"]
    assert not (sit["dir"] / "data").exists() and not (sit["dir"] / "handoff").exists()


def test_av7_the_slug_is_folded_and_checked():
    assert console_ingest.congregation_slug("Église  Évangélique, Saint-Lô!") == "eglise-evangelique-saint-lo"
    for bad in ("", "!!!", "   "):
        with pytest.raises(Fail):
            console_ingest.congregation_slug(bad)


# ---- the two engines agree on exceptsLocus -----------------------------------------------------------

def test_jena_and_rdflib_agree_on_exceptsLocus(tmp_path):
    from gcfix import write_tiny_data
    from goldenchain import fuseki

    data = tmp_path / "data"
    write_tiny_data(data)
    cong = f"""@prefix owl: <http://www.w3.org/2002/07/owl#> .
<source/congregation/c-one/statement> a gc:SourceWork ; rdfs:label "Statement" .
<body/congregation/c-one> a gc:Congregation ; rdfs:label "C one" ; gc:childOf <body/gill> ;
    dcterms:source <source/congregation/c-one/statement> ; dcterms:created "2026-11-22"^^xsd:date ; {PROPOSED} ;
    gc:exceptsLocus <locus/baptism> .
<axiom/exceptsLocus/c-one/baptism> a owl:Axiom ; owl:annotatedSource <body/congregation/c-one> ;
    owl:annotatedProperty gc:exceptsLocus ; owl:annotatedTarget <locus/baptism> ; rdfs:comment "Excepted." ;
    dcterms:source <source/congregation/c-one/statement> ; gc:locator "Art. 1" ; {PROPOSED} .
<body/congregation/c-two> a gc:Congregation ; rdfs:label "C two" ; gc:childOf <body/gill> ;
    dcterms:source <source/congregation/c-one/statement> ; dcterms:created "2026-11-22"^^xsd:date ; {PROPOSED} .
"""
    g = add(Graph(), cong)
    (data / "cong.ttl").write_text(g.serialize(format="turtle"), encoding="utf-8")
    ds = gc_ingest.load_dataset(data)
    gc_ingest.validate(ds)
    ref = gc_ingest.derive_rdflib(ds)
    want = {(str(b), str(h)) for b, h in ref.graph(U("graph/derived/inheritance")).subject_objects(GC.effectivelyHolds)}
    assert any("c-two" in b for b, _ in want) and not any("c-one" in b for b, _ in want)
    gc_ingest.build_tdb2(data, ds)
    with fuseki.serve() as srv:
        rows = srv.select("SELECT ?b ?h WHERE { GRAPH ?g { ?b <" + str(GC.effectivelyHolds) + "> ?h } }")
    assert {(r["b"]["value"], r["h"]["value"]) for r in rows} == want
