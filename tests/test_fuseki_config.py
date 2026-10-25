from pathlib import Path

from rdflib import Graph, Namespace

F = Namespace("http://jena.apache.org/fuseki#")
CFG = Path(__file__).resolve().parent.parent / "fuseki" / "config.ttl"


def load():
    g = Graph()
    g.parse(CFG, format="turtle")
    return g


def test_parses():
    assert len(load()) > 0


def test_has_query_endpoint():
    assert list(load().subjects(F.operation, F.query))


def test_no_write_endpoints():
    g = load()
    for op in (F.update, F["gsp-rw"], F.upload, F.patch):
        assert (None, F.operation, op) not in g
    for p in (F.serviceUpdate, F.serviceReadWriteGraphStore, F.serviceUpload):
        assert (None, p, None) not in g
