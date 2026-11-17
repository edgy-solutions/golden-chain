"""ADR-0002 Revision 3 (ruling on report 19, A-1): "read by" as an annotated axiom on a gc:asPrinted triple."""

from pathlib import Path

import pytest
from rdflib import Graph, Literal
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS

from goldenchain import ingest
from gcfix import GC, U, dataset_with, minimal

G = Graph()
for f in sorted((Path(__file__).resolve().parent.parent / "data").glob("*.ttl")):
    G.parse(f, format="turtle", publicID=ingest.B)

MODEL_READ = ["28/1/001", "28/2/001", "29/1/001", "29/1/002", "29/1/003", "29/2/001", "29/2/002",
              "29/3/001", "29/3/002", "29/4/001", "29/4/002"]


def _asprinted_axioms():
    return sorted(ax for ax in G.subjects(OWL.annotatedProperty, GC.asPrinted))


def test_eleven_axioms_one_per_model_read_argument():
    axs = _asprinted_axioms()
    assert [str(a).split("axiom/asPrinted/lbc-1689/")[1] for a in axs] == MODEL_READ
    for ax in axs:
        arg = G.value(ax, OWL.annotatedSource)
        assert arg == U("argument/lbc-1689/" + str(ax).split("axiom/asPrinted/lbc-1689/")[1])
        assert G.value(ax, OWL.annotatedTarget) == G.value(arg, GC.asPrinted)
        assert list(G.objects(ax, DCTERMS.contributor)) == [U("agent/architect")]
        assert list(G.objects(ax, GC.status)) == [U("vocab/status/proposed")]
        assert G.value(ax, RDFS.comment) is not None
        assert any("model-proposed" in str(c) for c in G.objects(arg, RDFS.comment))  # stays until confirmed


def test_ch7_transcription_strings_get_no_axiom():
    sources = {G.value(ax, OWL.annotatedSource) for ax in _asprinted_axioms()}
    ch7 = [a for a in G.subjects(GC.asPrinted, None) if "/lbc-1689/7/" in str(a)]
    assert len(ch7) == 3 and not (set(ch7) & sources)


def _fix(extra, target="(a) Gen. 1.1"):
    g = minimal()
    g.add((U("argument/x/1/001"), GC.asPrinted, Literal("(a) Gen. 1.1")))
    g.parse(data=f"""@base <{ingest.B}> .
@prefix gc: <{ingest.B}ontology#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
<axiom/asPrinted/x/1/001> a owl:Axiom ;
    owl:annotatedSource <argument/x/1/001> ; owl:annotatedProperty gc:asPrinted ;
    owl:annotatedTarget "{target}" ; rdfs:comment "read by"@en {extra} .
""", format="turtle")
    return g


def _check(g):
    ingest.code_checks(dataset_with(g))


OK = "; dcterms:contributor <agent/architect> ; gc:status <vocab/status/proposed>"


def test_proposed_axiom_with_reader_passes():
    _check(_fix(OK))


def test_ratified_by_chris_passes():
    g = _fix("; dcterms:contributor <agent/architect> ; gc:status <vocab/status/ratified>")
    _check(g)


def test_no_contributor_is_violation():
    with pytest.raises(ingest.IngestError, match="contributor"):
        _check(_fix("; gc:status <vocab/status/proposed>"))


def test_contributor_not_an_agent_is_violation():
    with pytest.raises(ingest.IngestError, match="contributor"):
        _check(_fix("; dcterms:contributor <agent/nobody> ; gc:status <vocab/status/proposed>"))


def test_no_status_is_violation():
    with pytest.raises(ingest.IngestError, match="status proposed or ratified"):
        _check(_fix("; dcterms:contributor <agent/architect>"))


def test_target_not_the_asserted_string_is_violation():
    with pytest.raises(ingest.IngestError, match="not asserted"):
        _check(_fix(OK, target="(a) Gen. 1.2"))
