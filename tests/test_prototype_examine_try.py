"""tools/prototype/examine_try.py (ADR-0008): synthetic data via the rdflib store, plus real-data counts."""

import importlib.util
import json
import re
import subprocess
from pathlib import Path

import pytest

from goldenchain import ingest
from gcfix import PREFIXES

TOOL = Path(__file__).resolve().parent.parent / "tools" / "prototype" / "examine_try.py"
spec = importlib.util.spec_from_file_location("examine_try", TOOL)
et = importlib.util.module_from_spec(spec)
spec.loader.exec_module(et)

SENT = ["SENTINEL-COMMENT", "SENTINEL-RESNOTE", "SENTINEL-QUOTE", "SENTINEL-DERIVED"]

SYNTH = PREFIXES + """@prefix owl: <http://www.w3.org/2002/07/owl#> .
<heading/h> a gc:Heading ; rdfs:label "H" .
<agent/build> a gc:Agent ; rdfs:label "Build agent" .
<agent/arch> a gc:Agent ; rdfs:label "Architect" .
<source/s> a gc:SourceWork ; rdfs:label "Source S" .
<source/s/1> a gc:SourceDivision ; dcterms:isPartOf <source/s> .
<locus/one> a gc:Locus ; rdfs:label "Locus One" ; skos:notation "1" ;
    gc:question "Is one one?"@en ; gc:underHeading <heading/h> ;
    rdfs:comment "SENTINEL-COMMENT locus" .
<locus/two> a gc:Locus ; rdfs:label "Locus Two" ; gc:question "Two?"@en ; gc:underHeading <heading/h> .
<position/one/a> a gc:Position ; rdfs:label "Pos A" ; gc:answers <locus/one> ;
    gc:unchurches true ; rdfs:comment "SENTINEL-COMMENT pos" ;
    gc:status <vocab/status/proposed> ; gc:proposedBy <agent/build> .
<position/one/b> a gc:Position ; rdfs:label "Pos B" ; gc:answers <locus/one> ;
    gc:status <vocab/status/proposed> ; gc:proposedBy <agent/build> .
<position/two/a> a gc:Position ; rdfs:label "Pos C" ; gc:answers <locus/two> ;
    gc:status <vocab/status/proposed> ; gc:proposedBy <agent/build> .
<passage/kjv/Gen.1.1> a gc:Passage ; gc:osisRef "Gen.1.1" ; rdfs:label "Genesis 1:1" .
<passage/kjv/Ex.2.2> a gc:Passage ; gc:osisRef "Ex.2.2" .
<passage/kjv/Ps.3.3> a gc:Passage ; gc:osisRef "Ps.3.3" .
<argument/s/1/001> a gc:Argument ; gc:source <source/s/1> ; gc:supports <position/one/a> ;
    gc:cites <passage/kjv/Gen.1.1> , <passage/kjv/Ex.2.2> ; gc:citesCandidate <passage/kjv/Ps.3.3> ;
    gc:locator "1.1" ; gc:secondaryLocator "p. 9" ; gc:asPrinted "(a) Gen. 1.1" ;
    gc:quotation "SENTINEL-QUOTE" ; gc:resolutionNote "SENTINEL-RESNOTE" ;
    rdfs:comment "SENTINEL-COMMENT arg" ;
    gc:status <vocab/status/ratified> ; gc:proposedBy <agent/build> ; gc:ratifiedBy <agent/arch> .
<argument/s/1/002> a gc:Argument ; gc:source <source/s/1> ; gc:supports <position/one/b> ;
    gc:cites <passage/kjv/Gen.1.1> ; gc:locator "1.2" ; gc:asPrinted "(b) Gen. 1.1" ;
    gc:status <vocab/status/proposed> ; gc:proposedBy <agent/build> .
<axiom/asPrinted/s/1/002> a owl:Axiom ; owl:annotatedSource <argument/s/1/002> ;
    owl:annotatedProperty gc:asPrinted ; owl:annotatedTarget "(b) Gen. 1.1" ;
    dcterms:contributor <agent/arch> ; gc:status <vocab/status/proposed> ;
    rdfs:comment "SENTINEL-COMMENT axiom" .
<axiom/asPrinted/s/1/001> a owl:Axiom ; owl:annotatedSource <argument/s/1/001> ;
    owl:annotatedProperty gc:asPrinted ; owl:annotatedTarget "(a) Gen. 1.1" ;
    dcterms:contributor <agent/arch> ; gc:status <vocab/status/ratified> ;
    rdfs:comment "SENTINEL-COMMENT axiom2" .
<argument/s/1/003> a gc:Argument ; gc:source <source/s/1> ; gc:supports <position/two/a> ;
    gc:citesCandidate <passage/kjv/Ps.3.3> ; gc:locator "1.3" ;
    gc:status <vocab/status/proposed> ; gc:proposedBy <agent/build> .
<body/b1> a gc:Body ; rdfs:label "Body One" ; gc:holds <holding/b1/a> , <holding/b1/b> .
<body/b2> a gc:Body ; rdfs:label "Body Two" ; gc:holds <holding/b2/a> .
<holding/b1/a> a gc:Holding ; gc:position <position/one/a> ; gc:modality <vocab/modality/taught> ;
    dcterms:source <source/s/1> ; gc:derivedBy "SENTINEL-DERIVED" ;
    gc:status <vocab/status/proposed> ; gc:proposedBy <agent/build> .
<holding/b1/b> a gc:Holding ; gc:position <position/one/b> ; gc:modality <vocab/modality/tolerated> ;
    gc:scope <vocab/scope/officers> ; dcterms:source <source/s/1> ;
    gc:status <vocab/status/proposed> ; gc:proposedBy <agent/build> .
<holding/b2/a> a gc:Holding ; gc:position <position/one/a> ; gc:modality <vocab/modality/required> ;
    dcterms:source <source/s/1> ; gc:status <vocab/status/proposed> ; gc:proposedBy <agent/build> .
"""


@pytest.fixture(scope="module")
def synth(tmp_path_factory):
    d = tmp_path_factory.mktemp("synth-data")
    (d / "synth.ttl").write_text(SYNTH, encoding="utf-8", newline="\n")
    out1, out2 = tmp_path_factory.mktemp("out1"), tmp_path_factory.mktemp("out2")
    s1 = et.build(out1, "rdflib", d)
    s2 = et.build(out2, "rdflib", d)
    return {"out": out1, "out2": out2, "summary": s1, "summary2": s2}


def pages(out):
    return sorted(p for p in Path(out).rglob("*.html"))


def test_summary_and_page_set(synth):
    s = synth["summary"]
    assert s["pages"] == {"index": 1, "examine": 2, "try": 2}
    assert (s["positions"], s["arguments"], s["cites_rows"]) == (3, 3, 3)
    assert s["candidate_only_passages"] == 1
    assert {p.name for p in (synth["out"] / "try").glob("*.html")} == {"kjv_Gen.1.1.html", "kjv_Ex.2.2.html"}
    assert {p.name for p in (synth["out"] / "examine").glob("*.html")} == {"one.html", "two.html"}


def test_banner_on_every_page(synth):
    head = json.loads((synth["out"] / "run_header.json").read_text())["git_head"][:12]
    banner = et.esc(et.BANNER.format(head=head))
    ps = pages(synth["out"])
    assert len(ps) == 5
    for p in ps:
        assert banner in p.read_text(encoding="utf-8"), p


def test_no_free_text_on_any_page(synth):
    for p in pages(synth["out"]):
        t = p.read_text(encoding="utf-8")
        for s in SENT:
            assert s not in t, (p, s)
        assert "<script" not in t and "http" not in t.replace("http://www.w3.org", "")


def test_each_argument_once_on_locus_page(synth):
    t1 = (synth["out"] / "examine" / "one.html").read_text(encoding="utf-8")
    t2 = (synth["out"] / "examine" / "two.html").read_text(encoding="utf-8")
    assert t1.count('id="arg-s_1_001"') == 1 and t1.count('id="arg-s_1_002"') == 1
    assert 'arg-s_1_003' not in t1
    assert t2.count('id="arg-s_1_003"') == 1
    assert "(a) Gen. 1.1" in t1 and "p. 9" in t1 and "Architect" in t1


def test_each_cites_pair_once_across_try_pages(synth):
    allt = "".join(p.read_text(encoding="utf-8") for p in (synth["out"] / "try").glob("*.html"))
    pairs = re.findall(r'data-pair="([^"]+)"', allt)
    assert sorted(pairs) == sorted(set(pairs))
    assert sorted(pairs) == ["s_1_001|kjv_Ex.2.2", "s_1_001|kjv_Gen.1.1", "s_1_002|kjv_Gen.1.1"]
    g = (synth["out"] / "try" / "kjv_Gen.1.1.html").read_text(encoding="utf-8")
    assert "Locus One" in g and "../examine/one.html" in g and "Genesis 1:1" in g


def test_candidate_only_passage_has_no_page_and_is_unlinked(synth):
    assert not (synth["out"] / "try" / "kjv_Ps.3.3.html").exists()
    t = (synth["out"] / "examine" / "one.html").read_text(encoding="utf-8")
    assert "Ps.3.3 (candidate)" in t and "try/kjv_Ps.3.3" not in t
    assert 'href="../try/kjv_Gen.1.1.html"' in t
    idx = (synth["out"] / "index.html").read_text(encoding="utf-8")
    assert "Ps.3.3" not in idx and "1 Locus One" in idx


def test_holdings_table_cells(synth):
    t = (synth["out"] / "examine" / "one.html").read_text(encoding="utf-8")
    assert "<th>Pos A</th><th>Pos B</th>" in t
    assert "<th>Body One</th><td>taught</td><td>tolerated (officers)</td>" in t
    assert "<th>Body Two</th><td>required</td><td></td>" in t
    assert synth["summary"]["holdings"] == 3
    assert "[unchurches]" in t


def test_byte_identical_two_runs(synth):
    a, b = synth["out"], synth["out2"]
    names = sorted(p.relative_to(a).as_posix() for p in a.rglob("*") if p.is_file())
    assert names == sorted(p.relative_to(b).as_posix() for p in b.rglob("*") if p.is_file())
    for n in names:
        assert (a / n).read_bytes() == (b / n).read_bytes(), n
    assert synth["summary"] == synth["summary2"]


def test_select_shared_by_both_stores(monkeypatch):
    # one SPARQL text, one data-access function; the stores differ only inside select
    seen = []
    monkeypatch.setattr(et, "_tdb2_select", lambda q: seen.append(("tdb2", q)) or [])
    et._ACTIVE.update(kind="tdb2", graph=None)
    et.select(et.QUERY)
    class FakeG:
        def query(self, q):
            seen.append(("rdflib", q))
            return []
    et._ACTIVE.update(kind="rdflib", graph=FakeG())
    et.select(et.QUERY)
    assert [k for k, _ in seen] == ["tdb2", "rdflib"] and seen[0][1] == seen[1][1] == et.QUERY
    for banned in ("comment", "resolutionNote", "quotation", "derivedBy"):
        assert banned not in et.QUERY


def test_tdb2_command_and_parse(monkeypatch, tmp_path):
    calls = []

    class R:
        returncode = 0
        stderr = b""
        stdout = json.dumps({"results": {"bindings": [
            {"s": {"type": "uri", "value": "x"}, "p": {"type": "uri", "value": "y"},
             "o": {"type": "literal", "value": "z"}}]}}).encode()

    monkeypatch.setattr(subprocess, "run", lambda cmd, **kw: calls.append(cmd) or R())
    monkeypatch.setattr(et.jena, "jena_home", lambda: tmp_path)
    assert et._tdb2_select("SELECT * {}") == [{"s": "x", "p": "y", "o": "z"}]
    cmd = calls[0]
    assert "tdb2.tdbquery" in cmd and "tdb:unionDefaultGraph=true" in cmd and "--results=json" in cmd
    assert str(ingest.DB) in cmd


def test_real_data_counts_consistent(tmp_path):
    s = et.build(tmp_path, "rdflib")
    ds = ingest.load_dataset()
    g = ingest.union(ds)
    GC = ingest.GC
    from rdflib.namespace import RDF
    loci = set(g.subjects(RDF.type, GC.Locus))
    cited = {o for _, o in g.subject_objects(GC.cites)}
    assert s["pages"]["examine"] == len(loci) == len(list((tmp_path / "examine").glob("*.html")))
    assert s["pages"]["try"] == len(cited) == len(list((tmp_path / "try").glob("*.html")))
    assert s["cites_rows"] == len(set(g.subject_objects(GC.cites)))
    assert pages(tmp_path) and len(pages(tmp_path)) == 1 + s["pages"]["examine"] + s["pages"]["try"]


def test_unconfirmed_asprinted_marked_from_axiom(synth):
    """ADR-0002 R3: a proposed asPrinted axiom puts the marker beside that string, and only there."""
    loc = (synth["out"] / "examine").glob("*.html")
    body = {p.name: p.read_text(encoding="utf-8") for p in loc}
    one = next(v for k, v in body.items() if "Locus One" in v)
    assert one.count(et.UNCONFIRMED) == 1
    assert f"(b) Gen. 1.1 ({et.UNCONFIRMED})" in one
    assert f"(a) Gen. 1.1 ({et.UNCONFIRMED})" not in one and "(a) Gen. 1.1" in one  # ratified: no marker
    tries = [p.read_text(encoding="utf-8") for p in (synth["out"] / "try").glob("*.html")]
    assert sum(t.count(et.UNCONFIRMED) for t in tries) == 1  # 002 cites one passage
    for t in tries + list(body.values()):
        assert "SENTINEL-COMMENT axiom" not in t

