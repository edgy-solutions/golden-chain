"""Plumb-line merge by replay (ADR-0006 Revision 1)."""

import json
import random
import subprocess
import sys
from pathlib import Path

import pytest
from rdflib import OWL, RDF, Graph, URIRef
from rdflib.compare import isomorphic

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools" / "console"))
sys.path.insert(0, str(ROOT))

import plumb_merge as pm  # noqa: E402
from column_rule import Fail  # noqa: E402

TTL = ROOT / "data" / "plumb-line.ttl"


def rec(n, rows, kind="plumb-line", day="2026-11-12", states=None):
    """A minimal signed record. rows = {row_id: {field: value}}; states = {row_id: state}."""
    states = states or {}
    return {"kind": kind, "build_hash": f"{n:016x}".ljust(64, "0"), "export_sha256": f"{n:x}".rjust(64, "e"),
            "signature": {"name": "Chris", "date": day},
            "rows": [{"row_id": rid, "section": rid.split(".")[0], "label": "", "state": states.get(rid, "verdict"),
                      "note": "", "fields": [{"id": k, "label": k, "kind": "x", "value": v} for k, v in vals.items()]}
                     for rid, vals in rows.items()]}


def flag_row(loc, pos, v):
    return {f"unchurches.{loc}.{pos}": {"unchurches": v}}


LOC = {"loc.locus": {"tier": "second", "clarity": "settled"}}


def text(records):
    return pm.replay(records).decode("utf-8")


def graph(records):
    g = Graph()
    g.parse(data=pm.replay(records).decode("utf-8"), format="turtle")
    return g


def b(s):
    return URIRef("https://w3id.org/golden-chain/" + s)


def holding_src(g, h):
    return str(g.value(b(h), URIRef("http://purl.org/dc/terms/source")))


# ---- the ruled replay test and the equivalence with the old writer's graph ------------------------

def test_replay_of_committed_records_is_the_committed_file():
    paths = pm.record_paths(ROOT / "docs" / "sittings" / "plumb-line")  # conftest points pm.RECORDS away
    assert paths
    records = [json.loads(p.read_bytes().decode("utf-8")) for p in paths]
    assert pm.replay(records) == TTL.read_bytes()


def test_regenerated_graph_is_the_old_graph_plus_axioms():
    try:
        old = subprocess.run(["git", "show", "8912293:data/plumb-line.ttl"], cwd=ROOT, capture_output=True,
                             check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("git or the commit is not available")
    g_old = Graph()
    g_old.parse(data=old.decode("utf-8"), format="turtle")
    # The regeneration of sitting 1: the replay of record 0001 alone (later sittings add to the file;
    # LOCK_ingest_eb961ddb_2026-11-22.md, E10).
    first = pm.record_paths(ROOT / "docs" / "sittings" / "plumb-line")[0]
    g_new = Graph()
    g_new.parse(data=pm.replay([json.loads(first.read_bytes().decode("utf-8"))]).decode("utf-8"), format="turtle")
    axioms = set(g_new.subjects(RDF.type, OWL.Axiom))
    assert len(axioms) == 17
    for s in axioms:
        for t in list(g_new.triples((s, None, None))):
            g_new.remove(t)
    assert isomorphic(g_new, g_old)


def test_check_d_accepts_the_regenerated_axioms():
    from goldenchain import ingest as gi

    ds = gi.load_dataset(ROOT / "data")
    gi.code_checks(ds)  # raises, listing every offender, including d. (axioms) and e. (unchurches)
    violations, _ = gi.validate(ds)
    assert violations == []
    assert len(list(gi.union(ds).subjects(RDF.type, OWL.Axiom))) >= 17


# ---- fixtures: the merge rows ---------------------------------------------------------------------

def test_new_holding_and_axioms():
    g = graph([rec(1, {**LOC, "loc.pa": {"modality": "taught"}})])
    h = "holding/plumb-line/loc/pa"
    assert (b("body/plumb-line"), URIRef("https://w3id.org/golden-chain/ontology#holds"), b(h)) in g
    assert holding_src(g, h).endswith("sitting-" + "0" * 15 + "1")
    t = text([rec(1, {**LOC})])
    assert "<axiom/tier/loc/to/second> a owl:Axiom" in t and "<axiom/clarity/loc/to/settled> a owl:Axiom" in t


def test_changed_modality_takes_new_src_and_day_unchanged_keeps_old():
    r1 = rec(1, {"loc.pa": {"modality": "taught"}, "loc.pb": {"modality": "required"}}, day="2026-11-12")
    r2 = rec(2, {"loc.pa": {"modality": "forbidden"}, "loc.pb": {"modality": "required"}}, day="2026-11-20")
    t = text([r1, r2])
    g = graph([r1, r2])
    assert holding_src(g, "holding/plumb-line/loc/pa").endswith("0002")
    assert holding_src(g, "holding/plumb-line/loc/pb").endswith("0001")
    pa = t[t.index("<holding/plumb-line/loc/pa> a"):].split("\n    gc:status")[0]
    assert "forbidden" in pa
    assert '"2026-11-12"^^xsd:date' in t[t.index("<holding/plumb-line/loc/pb> a"):].split("\n\n")[0]
    assert '"2026-11-20"^^xsd:date' in t[t.index("<holding/plumb-line/loc/pa> a"):].split("\n\n")[0]


def test_silent_removes_holding_flag_and_its_axiom():
    r1 = rec(1, {**LOC, "loc.pa": {"modality": "forbidden", "unchurches": ["unchurches"]}})
    assert "<axiom/unchurches/loc/pa/to/true>" in text([r1])
    r2 = rec(2, {"loc.pa": {"modality": "silent", "unchurches": []}, "loc.pz": {"modality": "silent"}})
    t = text([r1, r2])
    assert "holding/plumb-line/loc/pa" not in t and "axiom/unchurches" not in t and "gc:unchurches" not in t
    assert "#   verdict silent, Holding removed: loc.pa" in t
    assert "#   verdict silent, nothing held: loc.pz" in t


def test_none_other_and_abstain_leave_it():
    r1 = rec(1, {"loc.pa": {"modality": "taught"}, "loc.pb": {"modality": "taught"}, "loc.pc": {"modality": "taught"}})
    r2 = rec(2, {"loc.pa": {"modality": None}, "loc.pb": {"modality": {"other": "x"}},
                 "loc.pc": {"modality": "forbidden"}}, states={"loc.pc": "abstain"})
    t = text([r1, r2])
    g = graph([r1, r2])
    for p in "abc":
        assert holding_src(g, f"holding/plumb-line/loc/p{p}").endswith("0001")
    assert "modality left empty, unanswered, untouched: loc.pa" in t
    assert "other, as written, untouched (the architect rules): loc.pb.modality" in t
    assert "abstain/fault, untouched: loc.pc" in t
    assert t.count("vocab/modality/taught") == 3


def test_tier_change_replaces_axiom_and_unchanged_keeps_source():
    r1 = rec(1, {"loc.locus": {"tier": "second", "clarity": "settled"}})
    r2 = rec(2, {"loc.locus": {"tier": "first", "clarity": "settled"}})
    t = text([r1, r2])
    assert "axiom/tier/loc/to/second" not in t and "axiom/tier/loc/to/first" in t
    g = graph([r1, r2])
    dc = URIRef("http://purl.org/dc/terms/source")
    assert str(g.value(b("axiom/tier/loc/to/first"), dc)).endswith("0002")
    assert str(g.value(b("axiom/clarity/loc/to/settled"), dc)).endswith("0001")


def test_flag_rows_confirm_and_withdraw():
    r1 = rec(1, {**LOC, "loc.pa": {"modality": "forbidden"}})
    r2 = rec(2, {**flag_row("loc", "pa", "confirm")}, kind="plumb-line-followup")
    t = text([r1, r2])
    assert "<position/loc/pa> gc:unchurches true ." in t and "# unchurches (ADR-0003 R2.3)" in t
    assert "<axiom/unchurches/loc/pa/to/true> a owl:Axiom" in t
    r3 = rec(3, {**flag_row("loc", "pa", "withdraw")}, kind="plumb-line-followup")
    t3 = text([r1, r2, r3])
    assert "gc:unchurches" not in t3 and "axiom/unchurches" not in t3
    r4 = rec(4, {**flag_row("loc", "pa", "confirm")}, kind="plumb-line-followup")
    g = graph([r1, r2, r4])  # confirmed again later keeps the standing source
    assert str(g.value(b("axiom/unchurches/loc/pa/to/true"), URIRef("http://purl.org/dc/terms/source"))
               ).endswith("0002")


def test_flag_row_on_unheld_position_not_written_and_noted():
    t = text([rec(1, {**LOC, **flag_row("loc", "pz", "confirm")}, kind="plumb-line-followup")])
    assert "gc:unchurches" not in t
    assert "does not hold, not written: unchurches.loc.pz" in t


def test_radio_rows_are_not_data():
    t = text([rec(1, {**LOC, "q.r1": {"v": "yes"}}, kind="plumb-line-followup")])
    assert "not data, in the SIGNED record only: q.r1" in t and "q/r1" not in t


def test_ticked_with_unanswered_modality_fails():
    with pytest.raises(Fail, match="unchurches ticked"):
        pm.replay([rec(1, {**LOC, "loc.pa": {"modality": None, "unchurches": ["unchurches"]}})])


def test_flag_on_a_position_later_changed_to_taught_fails():
    r1 = rec(1, {**LOC, "loc.pa": {"modality": "forbidden", "unchurches": ["unchurches"]}})
    with pytest.raises(Fail, match="not forbidden"):
        pm.replay([r1, rec(2, {"loc.pa": {"modality": "taught"}})])
    with pytest.raises(Fail, match="unchurches ticked but modality is 'taught'"):  # the same sitting
        pm.replay([r1, rec(2, {"loc.pa": {"modality": "taught", "unchurches": ["unchurches"]}})])
    with pytest.raises(Fail, match="not forbidden"):  # a flag row cannot rescue it either
        pm.replay([r1, rec(2, {"loc.pa": {"modality": "taught"}, **flag_row("loc", "pa", "confirm")},
                           kind="plumb-line-followup")])
    pm.replay([r1, rec(2, {"loc.pa": {"modality": "taught", "unchurches": []}})])


def test_tier_third_with_a_standing_flag_fails():
    r1 = rec(1, {**LOC, "loc.pa": {"modality": "forbidden", "unchurches": ["unchurches"]}})
    with pytest.raises(Fail, match="tier-third"):
        pm.replay([r1, rec(2, {"loc.locus": {"tier": "third", "clarity": "settled"}})])


def test_checkbox_and_flag_row_in_one_record_fails():
    r1 = rec(1, {**LOC, "loc.pa": {"modality": "forbidden"}})
    r2 = rec(2, {"loc.pa": {"modality": "forbidden", "unchurches": []}, **flag_row("loc", "pa", "confirm")},
             kind="plumb-line-followup")
    with pytest.raises(Fail, match="both carry"):
        pm.replay([r1, r2])


def test_unknown_kind_fails():
    with pytest.raises(Fail, match="kind"):
        pm.replay([rec(1, {**LOC}, kind="wcf1647")])


def test_header_lists_each_sitting_with_replaced_sha():
    r1, r2 = rec(1, {**LOC}), rec(2, {"loc.pa": {"modality": "taught"}})
    t = text([r1, r2])
    lines = [l for l in t.splitlines() if l.startswith("# 000")]
    assert len(lines) == 2
    assert f"replaced sha256 {pm.sha(b'')}" in lines[0]
    assert f"replaced sha256 {pm.sha(pm.replay([r1]))}" in lines[1]
    assert "export sha256 " + "e" * 63 + "1" in lines[0] and "(plumb-line), signed 2026-11-12" in lines[0]
    assert t.count("a gc:SourceDivision") == 2


def test_determinism_and_row_order():
    rows = {**LOC, "loc.pa": {"modality": "taught"}, "loc.pb": {"modality": "forbidden", "unchurches": ["unchurches"]},
            "loc2.locus": {"tier": "first", "clarity": "open"}, "loc2.pc": {"modality": "required"}}
    r = rec(1, rows)
    assert pm.replay([r]) == pm.replay([r])
    items = list(rows.items())
    random.Random(3).shuffle(items)
    assert pm.replay([rec(1, dict(items))]) == pm.replay([r])


# ---- record_paths and merge -----------------------------------------------------------------------

def write_records(d, records):
    d.mkdir(parents=True, exist_ok=True)
    out = []
    for n, r in enumerate(records, 1):
        p = d / f"{n:04d}_signed_{r['kind']}_{r['build_hash'][:16]}.json"
        p.write_bytes(json.dumps(r, ensure_ascii=False, sort_keys=True, indent=1).encode("utf-8"))
        out.append(p)
    return out


def test_merge_writes_next_numbered_record_and_replay(tmp_path):
    r1, r2 = rec(1, {**LOC, "loc.pa": {"modality": "taught"}}), rec(2, {"loc.pa": {"modality": "required"}})
    d, ttl = tmp_path / "sittings", tmp_path / "plumb-line.ttl"
    path, rb, tb = pm.merge(r1, ttl, d)
    assert path.name.startswith("0001_signed_plumb-line_") and tb == pm.replay([r1])
    write_records(d, [r1])
    ttl.write_bytes(tb)
    path, rb, tb = pm.merge(r2, ttl, d)
    assert path.name == f"0002_signed_plumb-line_{r2['build_hash'][:16]}.json" and tb == pm.replay([r1, r2])
    assert json.loads(rb.decode("utf-8")) == r2


def test_merge_guard_refuses_a_hand_edit(tmp_path):
    r1 = rec(1, {**LOC})
    d, ttl = tmp_path / "sittings", tmp_path / "plumb-line.ttl"
    write_records(d, [r1])
    ttl.write_bytes(pm.replay([r1]) + b"#")
    before = sorted(p.name for p in tmp_path.rglob("*"))
    with pytest.raises(Fail, match="differs from the replay"):
        pm.merge(rec(2, {**LOC}), ttl, d)
    assert sorted(p.name for p in tmp_path.rglob("*")) == before and ttl.read_bytes().endswith(b"#")


def test_merge_ttl_present_without_records_fails_and_missing_ttl_with_records_fails(tmp_path):
    ttl = tmp_path / "plumb-line.ttl"
    ttl.write_bytes(pm.replay([rec(1, {**LOC})]))
    with pytest.raises(Fail, match="differs from the replay"):
        pm.merge(rec(2, {**LOC}), ttl, tmp_path / "sittings")
    d = tmp_path / "s2"
    write_records(d, [rec(1, {**LOC})])
    with pytest.raises(Fail, match="missing"):
        pm.merge(rec(2, {**LOC}), tmp_path / "none.ttl", d)


def test_merge_duplicate_build_refused(tmp_path):
    r1 = rec(1, {**LOC})
    d, ttl = tmp_path / "sittings", tmp_path / "plumb-line.ttl"
    write_records(d, [r1])
    ttl.write_bytes(pm.replay([r1]))
    with pytest.raises(Fail, match="already a record"):
        pm.merge(r1, ttl, d)


def test_record_paths_gap_and_strangers(tmp_path):
    d = tmp_path / "s"
    ps = write_records(d, [rec(1, {**LOC}), rec(2, {**LOC}), rec(3, {**LOC})])
    assert pm.record_paths(d) == ps
    ps[1].unlink()
    with pytest.raises(Fail, match="no gaps"):
        pm.record_paths(d)
    (d / "notes.txt").write_text("x")
    with pytest.raises(Fail, match="not a sitting record"):
        pm.record_paths(d)
