"""The plumb-line replay holds answers on Positions not yet in the data (LOCK_replay_held H1-H5)."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools" / "console"))
sys.path.insert(0, str(ROOT))

import plumb_merge as pm  # noqa: E402
from column_rule import Fail  # noqa: E402

TTL = ROOT / "data" / "plumb-line.ttl"
BFILE = ROOT / "docs" / "sittings" / "plumb-line-bindings.json"


def rec(n, rows, kind="plumb-line", day="2026-11-12", states=None):
    states = states or {}
    return {"kind": kind, "build_hash": f"{n:016x}".ljust(64, "0"), "export_sha256": f"{n:x}".rjust(64, "e"),
            "signature": {"name": "Chris", "date": day},
            "rows": [{"row_id": rid, "section": rid.split(".")[0], "label": "", "state": states.get(rid, "verdict"),
                      "note": "", "fields": [{"id": k, "label": k, "kind": "x", "value": v} for k, v in vals.items()]}
                     for rid, vals in rows.items()]}


def b16(n):
    return f"{n:016x}"


def bind_pos(n, target="position/x/a", modality="x.a-stance", unch="x.a-unchurches"):
    rows = {"modality": modality}
    if unch:
        rows["unchurches"] = unch
    return {"sitting": b16(n), "target": target, "rows": rows}


S1_HELD = {"x.a-stance": {"v": "forbidden"}, "x.a-unchurches": {"v": "unchurches"}}
BOTH = frozenset({"position/x/a"})
NONE = frozenset()


def lines(bs):
    return bs.decode("utf-8").splitlines()


def non_comment(bs):
    return [l for l in lines(bs) if not l.startswith("#")]


def test_real_records_with_no_bindings_equal_the_committed_file():
    paths = pm.record_paths(ROOT / "docs" / "sittings" / "plumb-line")
    records = [json.loads(p.read_bytes().decode("utf-8")) for p in paths]
    assert pm.replay(records, bindings=[]) == TTL.read_bytes()
    assert pm.replay(records) == TTL.read_bytes()  # the defaults: committed file, data/loci.ttl


def test_committed_bindings_file_loads_empty():
    assert pm.load_bindings(BFILE) == []
    assert pm.load_bindings(ROOT / "no-such-file.json") == []


def test_targets_in_reads_loci_ttl():
    t = pm.targets_in([ROOT / "data" / "loci.ttl"])
    assert any(x.startswith("position/") for x in t) and any(x.startswith("locus/") for x in t)


def test_held_then_applied_when_minted_equals_direct_position_row():
    records = [rec(1, S1_HELD)]
    bs = [bind_pos(1)]
    before = pm.replay(records, bs, NONE).decode()
    assert "holding/plumb-line/x/a" not in before
    assert "held for position/x/a" in before
    assert "not data" not in before
    after = pm.replay(records, bs, BOTH)
    direct = pm.replay([rec(1, {"x.a": {"modality": "forbidden", "unchurches": ["unchurches"]}})], [], NONE)
    assert non_comment(after) == non_comment(direct)
    assert "gc:unchurches <position/x/a>" in after.decode()
    assert "held for" not in after.decode()


def test_before_and_after_minting_equals_single_replay_after():
    records = [rec(1, S1_HELD)]
    bs = [bind_pos(1)]
    pm.replay(records, bs, NONE)
    second = pm.replay(records, bs, BOTH)
    assert second == pm.replay(records, bs, BOTH)
    assert second != pm.replay(records, bs, NONE)


def test_later_normal_row_overrides_applied_held_answer():
    records = [rec(1, S1_HELD), rec(2, {"x.a": {"modality": "taught", "unchurches": []}}, day="2026-11-13")]
    out = pm.replay(records, [bind_pos(1)], BOTH).decode()
    assert "gc:modality <vocab/modality/taught>" in out
    assert "gc:modality <vocab/modality/forbidden>" not in out
    assert f"sitting-{b16(2)}" in out.split("gc:modality")[1]


def test_unchurches_not_ticked_when_does_not_unchurch():
    records = [rec(1, {"x.a-stance": {"v": "forbidden"}, "x.a-unchurches": {"v": "does not unchurch"}})]
    out = pm.replay(records, [bind_pos(1)], BOTH).decode()
    assert "gc:unchurches" not in out and "holding/plumb-line/x/a" in out


def test_locus_binding_applies_tier_and_clarity_with_sitting_src():
    records = [rec(1, {"x.tier": {"v": "second"}, "x.clarity": {"v": "settled"}})]
    bs = [{"sitting": b16(1), "target": "locus/x", "rows": {"tier": "x.tier", "clarity": "x.clarity"}}]
    held = pm.replay(records, bs, NONE).decode()
    assert "held for locus/x" in held and "gc:tier" not in held
    out = pm.replay(records, bs, frozenset({"locus/x"})).decode()
    assert "<locus/x> gc:tier <vocab/tier/second> ; gc:clarity <vocab/clarity/settled> ." in out
    assert f"Set by plumb-line sitting {b16(1)}" in out


def test_held_unchurches_on_taught_fails_once_target_exists_not_while_held():
    records = [rec(1, {"x.a-stance": {"v": "taught"}, "x.a-unchurches": {"v": "unchurches"}})]
    bs = [bind_pos(1)]
    pm.replay(records, bs, NONE)
    with pytest.raises(Fail) as e:
        pm.replay(records, bs, BOTH)
    assert "x.a" in str(e.value) and "x.a-stance" in str(e.value) and "x.a-unchurches" in str(e.value)


def test_unbound_single_field_row_is_still_not_data():
    out = pm.replay([rec(1, {"y.q": {"v": "z"}})], [], NONE).decode()
    assert "not data, in the SIGNED record only: y.q" in out


# ---- H5, each loud failure on its own ------------------------------------------------------------

def test_h5_no_record_for_the_sitting():
    with pytest.raises(Fail, match="matches no record"):
        pm.replay([rec(1, S1_HELD)], [bind_pos(2)], NONE)


def test_h5_row_not_in_record():
    with pytest.raises(Fail, match="is not in sitting"):
        pm.replay([rec(1, S1_HELD)], [bind_pos(1, unch="x.a-nope")], NONE)


def _write(tmp_path, doc):
    p = tmp_path / "b.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    return p


def test_h5_row_bound_twice(tmp_path):
    doc = {"format": pm.BIND_FORMAT, "bindings": [bind_pos(1), bind_pos(1, target="position/x/b")]}
    with pytest.raises(Fail, match="bound twice"):
        pm.load_bindings(_write(tmp_path, doc))


def test_h5_target_bound_twice_for_one_sitting(tmp_path):
    doc = {"format": pm.BIND_FORMAT, "bindings": [bind_pos(1), bind_pos(1, modality="x.b-stance", unch=None)]}
    with pytest.raises(Fail, match="target position/x/a bound twice"):
        pm.load_bindings(_write(tmp_path, doc))


def test_h5_multi_field_row_bound():
    records = [rec(1, {"x.a": {"modality": "forbidden", "unchurches": []}, "x.a-unchurches": {"v": "unchurches"}})]
    with pytest.raises(Fail, match="not a single-field row"):
        pm.replay(records, [bind_pos(1, modality="x.a")], NONE)


def test_h5_bad_format_and_extra_keys(tmp_path):
    with pytest.raises(Fail):
        pm.load_bindings(_write(tmp_path, {"format": "nope/1", "bindings": []}))
    with pytest.raises(Fail):
        pm.load_bindings(_write(tmp_path, {"format": pm.BIND_FORMAT, "bindings": [], "extra": 1}))
    extra = dict(bind_pos(1), note="x")
    with pytest.raises(Fail):
        pm.load_bindings(_write(tmp_path, {"format": pm.BIND_FORMAT, "bindings": [extra]}))
    bad_rows = {"sitting": b16(1), "target": "position/x/a", "rows": {"unchurches": "x.a-unchurches"}}
    with pytest.raises(Fail):
        pm.load_bindings(_write(tmp_path, {"format": pm.BIND_FORMAT, "bindings": [bad_rows]}))
