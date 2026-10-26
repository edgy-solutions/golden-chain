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


# ---- scope (ADR-0003 rev. 1): excludes and entails fire only when scopes intersect ----------

SCOPES = [None, "officers", "members"]


def intersect(s1, s2) -> bool:
    return s1 is None or s2 is None or s1 == s2


def test_officers_required_vs_members_tolerated_does_not_fire():
    """The architect's born test (report 2, Q11). Tolerated never fires, so scope is not what
    keeps this one quiet; the parametrised tests below are the ones that exercise scope."""
    w = two_positions("excludes")
    w.hold("b", "l", "p", "required", scope="officers")
    w.hold("b", "l", "q", "tolerated", scope="members")
    assert inconsistencies(ingest.derive_rdflib(w.dataset())) == []


@pytest.mark.parametrize("s1,s2", list(itertools.product(SCOPES, SCOPES)))
def test_excludes_fires_iff_scopes_intersect(s1, s2):
    w = two_positions("excludes")
    w.hold("b", "l", "p", "required", scope=s1)
    w.hold("b", "l", "q", "required", scope=s2)
    found = inconsistencies(ingest.derive_rdflib(w.dataset()))
    assert len(found) == (1 if intersect(s1, s2) else 0)


@pytest.mark.parametrize("s1,s2", list(itertools.product(SCOPES, SCOPES)))
def test_entails_fires_iff_scopes_intersect(s1, s2):
    w = two_positions("entails")
    w.hold("b", "l", "p", "required", scope=s1)
    w.hold("b", "l", "q", "forbidden", scope=s2)
    found = inconsistencies(ingest.derive_rdflib(w.dataset()))
    assert len(found) == (1 if intersect(s1, s2) else 0)


# ---- two parents (ADR-0003 rev. 1): differing parents make the child inconsistent ---------

def diamond(hold_p1, hold_p2):
    """Child c of parents p1 and p2 on locus l; hold_pN is a list of (pos, modality, scope)."""
    w = World()
    for pos in ("x", "y"):
        w.position("l", pos)
    w.position("k", "z")
    for name, holds in (("p1", hold_p1), ("p2", hold_p2)):
        w.body(name)
        for pos, mod, scope in holds:
            w.hold(name, "l", pos, mod, scope)
    w.body("c")
    w.g.add((U("body/c"), GC.childOf, U("body/p1")))
    w.g.add((U("body/c"), GC.childOf, U("body/p2")))
    return w


def rules(derived):
    cons = derived.graph(U("graph/derived/consistency"))
    return sorted((str(next(cons.objects(i, GC.body))).split("/body/")[1], str(next(cons.objects(i, GC.rule))))
                  for i in inconsistencies(derived))


@pytest.mark.parametrize("p1,p2,fires", [
    ([("x", "taught", None)], [("y", "taught", None)], True),          # different Positions
    ([("x", "taught", None)], [("x", "required", None)], True),        # same Position, other modality
    ([("x", "taught", None)], [("x", "taught", "officers")], True),    # same, other scope
    ([("x", "taught", None)], [("x", "taught", None)], False),         # agree
    ([("x", "taught", None), ("y", "forbidden", None)],
     [("y", "forbidden", None), ("x", "taught", None)], False),        # agree as sets
    ([("x", "taught", None)], [], False),                              # p2 silent on l: not a difference
])
def test_parents_differ(p1, p2, fires):
    d = ingest.derive_rdflib(diamond(p1, p2).dataset())
    assert rules(d) == ([("c", "parents-differ")] if fires else [])


def test_parents_differ_silenced_by_own_holding():
    w = diamond([("x", "taught", None)], [("y", "taught", None)])
    w.hold("c", "l", "x", "taught")
    d = ingest.derive_rdflib(w.dataset())
    assert rules(d) == []
    assert ("c", "l/x") in eff(d) and ("c", "l/y") not in eff(d)


def test_parents_differ_picks_no_parent():
    """The child still inherits from both parents; no parent is chosen."""
    d = ingest.derive_rdflib(diamond([("x", "taught", None)], [("y", "taught", None)]).dataset())
    assert {("c", "l/x"), ("c", "l/y")} <= eff(d)
    assert len(inconsistencies(d)) == 1
