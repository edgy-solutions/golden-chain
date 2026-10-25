import itertools

import pytest
from rdflib.namespace import RDF

from goldenchain import ingest
from gcfix import GC, MOD, U, World, eff, inconsistencies

MODS = list(MOD)
FIRES = {"required", "taught"}


def two_positions(rel: str):
    w = World()
    w.position("l", "p")
    w.position("l", "q")
    w.g.add((U("position/l/p"), GC[rel], U("position/l/q")))
    w.body("b")
    return w


@pytest.mark.parametrize("m1,m2", list(itertools.product(MODS, MODS)))
def test_excludes_fires_iff_both_affirmed(m1, m2):
    w = two_positions("excludes")
    w.hold("b", "l", "p", m1)
    w.hold("b", "l", "q", m2)
    found = inconsistencies(ingest.derive_rdflib(w.dataset()))
    assert len(found) == (1 if m1 in FIRES and m2 in FIRES else 0)


@pytest.mark.parametrize("m1,m2", list(itertools.product(MODS, MODS)))
def test_excludes_symmetric_when_edge_stated_other_way(m1, m2):
    w = two_positions("excludes")
    w.g.remove((U("position/l/p"), GC.excludes, U("position/l/q")))
    w.g.add((U("position/l/q"), GC.excludes, U("position/l/p")))
    w.hold("b", "l", "p", m1)
    w.hold("b", "l", "q", m2)
    found = inconsistencies(ingest.derive_rdflib(w.dataset()))
    assert len(found) == (1 if m1 in FIRES and m2 in FIRES else 0)


@pytest.mark.parametrize("m1,m2", list(itertools.product(MODS, MODS)))
def test_entails_fires_iff_affirmed_and_object_forbidden(m1, m2):
    w = two_positions("entails")
    w.hold("b", "l", "p", m1)
    w.hold("b", "l", "q", m2)
    found = inconsistencies(ingest.derive_rdflib(w.dataset()))
    assert len(found) == (1 if m1 in FIRES and m2 == "forbidden" else 0)


def test_silent_body_gets_nothing_and_holdings_unchanged():
    w = World()
    w.position("l", "p")
    w.body("root")
    w.body("silent")
    w.hold("root", "l", "p")
    ds = w.dataset()
    before = set(ds.graph(U("graph/fixture")).subjects(RDF.type, GC.Holding))
    out = ingest.derive_rdflib(ds)
    assert ("silent", "l/p") not in eff(out)
    assert not any(b == "silent" for b, _ in eff(out))
    u = ingest.union(out)
    assert set(u.subjects(RDF.type, GC.Holding)) == before
    assert len(list(u.subjects(GC.position, None))) == len(before)


def test_inheritance_override_per_locus():
    w = World()
    for loc, name in (("l", "p1"), ("l", "p2"), ("m", "p3")):
        w.position(loc, name)
    w.body("root")
    w.body("child", "root")
    w.body("grand", "child")
    w.hold("root", "l", "p1")
    w.hold("root", "m", "p3")
    w.hold("child", "l", "p2", scope="officers")
    got = eff(ingest.derive_rdflib(w.dataset()))
    assert {x for x in got if x[0] == "root"} == {("root", "l/p1"), ("root", "m/p3")}
    for b in ("child", "grand"):
        assert {x for x in got if x[0] == b} == {(b, "l/p2"), (b, "m/p3")}


def test_intermediate_holding_blocks_root_for_everything_below():
    w = World()
    for loc, name in (("l", "p1"), ("l", "p2"), ("m", "p3")):
        w.position(loc, name)
    w.body("root")
    w.body("mid", "root")
    w.body("leaf", "mid")
    w.body("leaf2", "leaf")
    w.hold("root", "l", "p1")
    w.hold("mid", "l", "p2")
    got = eff(ingest.derive_rdflib(w.dataset()))
    for b in ("mid", "leaf", "leaf2"):
        assert (b, "l/p1") not in got
        assert (b, "l/p2") in got
    assert ("root", "l/p1") in got


def test_intermediate_holding_on_other_locus_does_not_block():
    w = World()
    for loc, name in (("l", "p1"), ("m", "p3")):
        w.position(loc, name)
    w.body("root")
    w.body("mid", "root")
    w.body("leaf", "mid")
    w.hold("root", "l", "p1")
    w.hold("mid", "m", "p3")
    got = eff(ingest.derive_rdflib(w.dataset()))
    assert ("leaf", "l/p1") in got and ("leaf", "m/p3") in got


def test_inheritance_makes_inconsistency_across_edge():
    # Holding by an ancestor and a descendant on different loci can still clash via excludes.
    w = World()
    w.position("l", "p")
    w.position("m", "q")
    w.g.add((U("position/l/p"), GC.excludes, U("position/m/q")))
    w.body("root")
    w.body("child", "root")
    w.hold("root", "l", "p", "required")
    w.hold("child", "m", "q", "taught")
    found = inconsistencies(ingest.derive_rdflib(w.dataset()))
    assert [str(i) for i in found] == [str(U("inconsistency/child/excludes/l/p/m/q"))]


def test_rerun_is_idempotent_and_clears_derived():
    w = two_positions("excludes")
    w.hold("b", "l", "p", "required")
    w.hold("b", "l", "q", "taught")
    out = ingest.derive_rdflib(w.dataset())

    def snapshot():
        return {
            g.identifier: set(g)
            for g in out.graphs()
            if str(g.identifier).startswith(ingest.B + "graph/derived/")
        }

    first = snapshot()
    assert first
    for f in ingest.rule_files():
        out.update(f.read_text(encoding="utf-8"))
    assert snapshot() == first
    # remove the cause, rerun: nothing stale survives 00-clear
    out.graph(U("graph/fixture")).remove((None, GC.modality, U(MOD["taught"])))
    for f in ingest.rule_files():
        out.update(f.read_text(encoding="utf-8"))
    assert inconsistencies(out) == []
    assert not [t for g in snapshot().values() for t in g if t[1] == GC.inconsistent]
