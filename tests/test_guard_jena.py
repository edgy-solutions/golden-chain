"""ADR-0001 guard, Jena half: Fuseki (built by tdbloader + tdbupdate) vs rdflib, per named graph."""

import urllib.error
import urllib.request

import pytest
from rdflib import Literal, URIRef
from rdflib.namespace import RDF, XSD

from goldenchain import fuseki, ingest
from gcfix import GC, write_tiny_data

CLASSES = ["Locus", "Position", "Argument", "Passage", "Body", "Holding"]
PREDICATES = ["holds", "answers", "supports", "childOf", "effectivelyHolds"]


def term(b: dict):
    if b["type"] == "uri":
        return URIRef(b["value"])
    dt = b.get("datatype")
    if dt == str(XSD.string):
        dt = None
    return Literal(b["value"], lang=b.get("xml:lang"), datatype=dt)


@pytest.fixture(scope="module")
def engines(tmp_path_factory):
    data = tmp_path_factory.mktemp("tiny-data")
    write_tiny_data(data)
    ds = ingest.load_dataset(data)
    ingest.validate(ds)
    ingest.code_checks(ds)
    ref = ingest.derive_rdflib(ds)
    ingest.build_tdb2(data, ds)
    with fuseki.serve() as srv:
        yield srv, ref


def per_graph(rows):
    out = {}
    for r in rows:
        out[r["g"]["value"]] = int(r["n"]["value"])
    return out


def ref_graphs(ref):
    return {g.identifier: g for g in ref.graphs() if len(g)}


def test_graph_set_and_triple_counts(engines):
    srv, ref = engines
    got = per_graph(srv.select("SELECT ?g (COUNT(*) AS ?n) WHERE { GRAPH ?g { ?s ?p ?o } } GROUP BY ?g"))
    want = {str(i): len(g) for i, g in ref_graphs(ref).items()}
    assert got == want
    assert any(k.endswith("graph/derived/inheritance") for k in got)
    assert any(k.endswith("graph/derived/consistency") for k in got)


@pytest.mark.parametrize("cls", CLASSES)
def test_distinct_subjects_per_class(engines, cls):
    srv, ref = engines
    got = per_graph(srv.select(
        f"SELECT ?g (COUNT(DISTINCT ?s) AS ?n) WHERE {{ GRAPH ?g {{ ?s a <{GC[cls]}> }} }} GROUP BY ?g"))
    want = {}
    for i, g in ref_graphs(ref).items():
        n = len(set(g.subjects(RDF.type, GC[cls])))
        if n:
            want[str(i)] = n
    assert got == want


@pytest.mark.parametrize("pred", PREDICATES)
def test_predicate_counts(engines, pred):
    srv, ref = engines
    got = per_graph(srv.select(
        f"SELECT ?g (COUNT(*) AS ?n) WHERE {{ GRAPH ?g {{ ?s <{GC[pred]}> ?o }} }} GROUP BY ?g"))
    want = {}
    for i, g in ref_graphs(ref).items():
        n = len(list(g.triples((None, GC[pred], None))))
        if n:
            want[str(i)] = n
    assert got == want
    if pred == "effectivelyHolds":
        assert want, "fixture should derive effectivelyHolds"


@pytest.mark.parametrize("name", ["inheritance", "consistency"])
def test_derived_graphs_equal_triple_for_triple(engines, name):
    srv, ref = engines
    iri = ingest.B + "graph/derived/" + name
    rows = srv.select(f"SELECT ?s ?p ?o WHERE {{ GRAPH <{iri}> {{ ?s ?p ?o }} }}")
    got = {(term(r["s"]), term(r["p"]), term(r["o"])) for r in rows}
    want = set(ref.graph(URIRef(iri)))
    assert got == want
    assert want


def test_service_has_no_update_endpoint(engines):
    srv, _ = engines
    for path in ("/gc/update", "/gc"):
        req = urllib.request.Request(
            srv.base + path,
            b"INSERT DATA { <urn:x> <urn:y> <urn:z> }",
            {"Content-Type": "application/sparql-update"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                status = r.status
        except urllib.error.HTTPError as e:
            status = e.code
        assert not 200 <= status < 300, f"POST update to {path} returned {status}"
    assert srv.select("SELECT * WHERE { <urn:x> <urn:y> <urn:z> }") == []
