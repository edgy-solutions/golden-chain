import pytest
from rdflib import Literal, URIRef
from rdflib.namespace import DCTERMS, RDF, RDFS, XSD

from goldenchain import ingest
from gcfix import GC, U, add, dataset_with, focus_nodes, minimal, report

POS = U("position/baptism/immersion")
ARG = U("argument/gill/ch1/001")
HOLD = U("holding/gill/baptism/immersion")
PASSAGE = U("passage/kjv/Matt.28.19")


def fails_on(g, node: URIRef) -> bool:
    violations, _ = report(g)
    return str(node) in focus_nodes(violations)


def test_minimal_conforms():
    violations, warnings = report(minimal())
    assert violations == []
    # Only the "no tier yet" warnings, one per Locus.
    assert len(warnings) == 2


@pytest.mark.parametrize("node", [POS, ARG, HOLD])
@pytest.mark.parametrize("prop", ["status", "proposedBy"])
def test_missing_status_or_proposer_fails(node, prop):
    g = minimal()
    g.remove((node, GC[prop], None))
    assert fails_on(g, node)


@pytest.mark.parametrize("node", [POS, ARG, HOLD])
def test_ratified_complete_passes(node):
    g = minimal()
    g.set((node, GC.status, U("vocab/status/ratified")))
    g.set((node, GC.ratifiedBy, U("agent/architect")))
    g.set((node, DCTERMS.dateAccepted, Literal("2026-10-25", datatype=XSD.date)))
    assert not fails_on(g, node)


@pytest.mark.parametrize("missing", ["ratifiedBy", "dateAccepted"])
def test_ratified_missing_part_fails(missing):
    g = minimal()
    g.set((POS, GC.status, U("vocab/status/ratified")))
    if missing != "ratifiedBy":
        g.set((POS, GC.ratifiedBy, U("agent/architect")))
    if missing != "dateAccepted":
        g.set((POS, DCTERMS.dateAccepted, Literal("2026-10-25", datatype=XSD.date)))
    assert fails_on(g, POS)


def test_proposed_with_ratified_by_fails():
    g = minimal()
    g.set((POS, GC.ratifiedBy, U("agent/architect")))
    assert fails_on(g, POS)


def test_ratified_by_other_than_architect_fails():
    g = minimal()
    g.set((POS, GC.status, U("vocab/status/ratified")))
    g.set((POS, GC.ratifiedBy, U("agent/build")))
    g.set((POS, DCTERMS.dateAccepted, Literal("2026-10-25", datatype=XSD.date)))
    assert fails_on(g, POS)


def quoted(text, checked=True, pages=True):
    g = minimal()
    g.add((ARG, GC.quotation, Literal(text)))
    if checked:
        g.add((ARG, GC.quotationCheckedAgainst, Literal("Gill 1769")))
    if pages:
        g.add((ARG, GC.pages, Literal("12-13")))
    return g


def test_quotation_complete_passes():
    assert not fails_on(quoted("One sentence."), ARG)


def test_quotation_without_checked_against_fails():
    assert fails_on(quoted("One.", checked=False), ARG)


def test_quotation_without_pages_fails():
    assert fails_on(quoted("One.", pages=False), ARG)


def test_two_quotations_fail():
    g = quoted("One.")
    g.add((ARG, GC.quotation, Literal("Two.")))
    assert fails_on(g, ARG)


@pytest.mark.parametrize(
    "text,ok",
    [
        ("One. Two. Three.", True),
        ("One. Two. Three. Four.", False),
        ("See Rom. vi. 4, and Acts ii. 38. Done.", True),
    ],
)
def test_quotation_sentence_cap(text, ok):
    assert fails_on(quoted(text), ARG) is (not ok)


def test_argument_with_comment_fails_closed():
    g = minimal()
    g.add((ARG, RDFS.comment, Literal("editorial prose")))
    assert fails_on(g, ARG)


def test_resolution_note_without_as_printed_fails():
    g = minimal()
    g.add((ARG, GC.resolutionNote, Literal("why")))
    assert fails_on(g, ARG)
    g.add((ARG, GC.asPrinted, Literal("Matt. xxviii. 19")))
    assert not fails_on(g, ARG)


def test_position_without_argument_fails():
    g = minimal()
    for t in list(g.triples((ARG, None, None))):
        g.remove(t)
    assert fails_on(g, POS)


def test_position_locus_segment_must_match_answers():
    g = minimal()
    g.set((POS, GC.answers, U("locus/other")))
    assert fails_on(g, POS)


def test_holding_iri_must_match_body_position_scope():
    g = minimal()
    bad = U("holding/gill/baptism/wrong")
    g.add((bad, RDF.type, GC.Holding))
    for t in list(g.triples((HOLD, None, None))):
        g.add((bad, t[1], t[2]))
    g.remove((U("body/gill"), GC.holds, HOLD))
    g.add((U("body/gill"), GC.holds, bad))
    for t in list(g.triples((HOLD, None, None))):
        g.remove(t)
    assert fails_on(g, bad)


@pytest.mark.parametrize("scope", ["officers", "members"])
def test_holding_with_scope_matching_iri_passes(scope):
    g = minimal()
    ok = U(f"holding/gill/baptism/immersion/{scope}")
    g.add((ok, RDF.type, GC.Holding))
    for p, o in list(g.predicate_objects(HOLD)):
        g.add((ok, p, o))
    g.add((ok, GC.scope, U(f"vocab/scope/{scope}")))
    g.remove((U("body/gill"), GC.holds, HOLD))
    g.add((U("body/gill"), GC.holds, ok))
    for t in list(g.triples((HOLD, None, None))):
        g.remove(t)
    assert not fails_on(g, ok)
    # the same Holding with the scope segment missing from its IRI fails
    g.add((ok, GC.scope, U("vocab/scope/members" if scope == "officers" else "vocab/scope/officers")))
    g.remove((ok, GC.scope, U(f"vocab/scope/{scope}")))
    assert fails_on(g, ok)


def test_explicit_scope_all_fails():
    g = minimal()
    all_ = U("holding/gill/baptism/immersion/all")
    g.add((all_, RDF.type, GC.Holding))
    for p, o in list(g.predicate_objects(HOLD)):
        g.add((all_, p, o))
    g.add((all_, GC.scope, U("vocab/scope/all")))
    g.remove((U("body/gill"), GC.holds, HOLD))
    g.add((U("body/gill"), GC.holds, all_))
    for t in list(g.triples((HOLD, None, None))):
        g.remove(t)
    assert fails_on(g, all_)


def test_anchor_fails():
    g = minimal()
    g.add((U("anchor/x"), RDF.type, GC.Anchor))
    assert fails_on(g, U("anchor/x"))


def test_passage_closed():
    g = minimal()
    g.add((PASSAGE, GC.supports, POS))
    assert fails_on(g, PASSAGE)


# ---- code checks a-c -------------------------------------------------------------------


def checks(g, name="fixture"):
    ingest.code_checks(dataset_with(g, name))


def test_code_checks_pass_on_minimal():
    checks(minimal())


def test_noncanonical_passage_iri_fails():
    g = minimal()
    bad = U("passage/kjv/Matt.28.19-Matt.28.19")
    g.add((bad, RDF.type, GC.Passage))
    with pytest.raises(ingest.IngestError, match="Matt.28.19-Matt.28.19"):
        checks(g)


def test_mismatched_ordinal_fails():
    g = minimal()
    g.set((PASSAGE, GC.endOrdinal, Literal(5)))
    with pytest.raises(ingest.IngestError, match="endOrdinal"):
        checks(g)


def test_mismatched_versification_literal_fails():
    g = minimal()
    g.set((PASSAGE, GC.versification, Literal("KJV")))
    with pytest.raises(ingest.IngestError, match="versification"):
        checks(g)


def test_cites_non_passage_fails():
    g = minimal()
    g.add((ARG, GC.citesCandidate, U("passage/kjv/Matt.28.20")))
    with pytest.raises(ingest.IngestError, match="not typed gc:Passage"):
        checks(g)


def test_all_offenders_listed():
    g = minimal()
    g.set((PASSAGE, GC.endOrdinal, Literal(5)))
    g.add((ARG, GC.cites, U("passage/kjv/Matt.28.20")))
    with pytest.raises(ingest.IngestError) as e:
        checks(g)
    assert "endOrdinal" in str(e.value) and "Matt.28.20" in str(e.value)


def test_tier_outside_plumb_line_fails():
    g = minimal()
    g.add((U("locus/baptism"), GC.tier, U("vocab/tier/first")))
    with pytest.raises(ingest.IngestError, match="plumb-line"):
        checks(g)
    checks(g, name="plumb-line")  # same triple in the plumb-line graph is fine


def test_clarity_outside_plumb_line_fails():
    g = minimal()
    g.add((U("locus/baptism"), GC.clarity, U("vocab/clarity/open")))
    with pytest.raises(ingest.IngestError, match="plumb-line"):
        checks(g)
