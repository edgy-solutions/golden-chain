import re
from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, SKOS

B = "https://w3id.org/golden-chain/"
VOCAB = Path(__file__).resolve().parent.parent / "ontology" / "vocab.ttl"
COUNTS = {"modality": 4, "user-modality": 3, "tier": 3, "clarity": 3, "scope": 3}


def load():
    g = Graph()
    g.parse(VOCAB, format="turtle")
    return g


def test_parses():
    assert len(load()) > 0


def test_schemes_and_counts():
    g = load()
    schemes = set(g.subjects(RDF.type, SKOS.ConceptScheme))
    assert len(schemes) == 5
    for name, n in COUNTS.items():
        s = URIRef(B + "vocab/" + name)
        assert s in schemes
        assert len(set(g.subjects(SKOS.inScheme, s))) == n
    assert len(set(g.subjects(RDF.type, SKOS.Concept))) == 16


def test_concept_iris():
    g = load()
    pat = re.compile(r"^https://w3id\.org/golden-chain/vocab/[a-z-]+/[a-z0-9-]+$")
    for c in g.subjects(RDF.type, SKOS.Concept):
        assert pat.match(str(c))
        schemes = list(g.objects(c, SKOS.inScheme))
        assert len(schemes) == 1
        assert str(c).startswith(str(schemes[0]) + "/")


def test_labels_and_definitions():
    g = load()
    for c in g.subjects(RDF.type, SKOS.Concept):
        for p in (SKOS.prefLabel, SKOS.definition):
            vals = [o for o in g.objects(c, p) if isinstance(o, Literal) and o.language == "en"]
            assert len(vals) == 1


def test_forbidden_distinct():
    a = URIRef(B + "vocab/modality/forbidden")
    b = URIRef(B + "vocab/user-modality/forbidden")
    g = load()
    assert a != b
    assert (a, RDF.type, SKOS.Concept) in g and (b, RDF.type, SKOS.Concept) in g
