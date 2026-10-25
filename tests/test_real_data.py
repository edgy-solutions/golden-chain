"""The real dataset (data/ by default, or GOLDEN_CHAIN_DATA): shapes, code checks, refutation, counts."""

import pytest
from rdflib import URIRef
from rdflib.namespace import RDF

from goldenchain import ingest
from gcfix import GC, U, inconsistencies
from predictions import PREDICTED

DS = ingest.load_dataset()
UNION = ingest.union(DS)
DERIVED = ingest.derive_rdflib(DS)
EDGES = [(rel, p, q) for rel in ("excludes", "entails") for p, q in sorted(UNION.subject_objects(GC[rel]))]


def test_no_shacl_violations():
    violations, _ = ingest.validate(DS)
    assert violations == []


def test_code_checks_pass():
    ingest.code_checks(DS)


def test_consistency_graph_empty():
    assert inconsistencies(DERIVED) == []
    assert len(DERIVED.graph(U("graph/derived/consistency"))) == 0


@pytest.mark.parametrize(
    "rel,p,q",
    EDGES or [("no-edges", None, None)],
    ids=[f"{r}:{str(p).split('/position/')[-1]}->{str(q).split('/position/')[-1]}" for r, p, q in EDGES]
    or ["no-edges"],
)
def test_no_body_inconsistent_under_edge(rel, p, q):
    """Refutation check: no source Body violates this edge."""
    if p is None:
        assert EDGES == []
        return
    cons = DERIVED.graph(U("graph/derived/consistency"))
    hits = [
        i for i in cons.subjects(GC.rule, None)
        if (i, GC.involves, p) in cons and (i, GC.involves, q) in cons
    ]
    assert hits == [], f"edge {rel} {p} -> {q} is violated by: {[str(h) for h in hits]}"


def actual_counts() -> dict:
    out = {c: len(set(UNION.subjects(RDF.type, GC[c]))) for c in
           ("Locus", "Position", "Argument", "Passage", "Holding")}
    # Bodies are typed by their subclass only (ontology/core.ttl); no inference runs here.
    out["Body"] = len({s for c in ("Body", "Confession", "Catechism", "Systematic", "Collection")
                       for s in UNION.subjects(RDF.type, GC[c])})
    for p in ("excludes", "entails", "holds", "answers", "supports", "childOf"):
        out[p] = len(list(UNION.triples((None, GC[p], None))))
    out["effectivelyHolds"] = len(list(ingest.union(DERIVED).triples((None, GC.effectivelyHolds, None))))
    out["warnings"] = len(ingest.validate(DS)[1])
    return out


def test_counts_match_predictions():
    assert PREDICTED is not None, "predictions not filled"
    assert actual_counts() == PREDICTED
