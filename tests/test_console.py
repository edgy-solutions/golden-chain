import copy
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools" / "console"))
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import ingest  # noqa: E402
from column_rule import Fail  # noqa: E402

CLEAN = {"commit": "abc123", "dirty": False, "porcelain": 0}


def png(path, w=24, h=12, shade=200):
    Image.new("L", (w, h), shade).save(path)
    return build.sha256_file(path)


def field(fid, kind, options=None, required=True, **kw):
    f = {"id": fid, "kind": kind, "label": fid, "required": required, "proposed": None, **kw}
    if options:
        f["options"] = options
    return f


def make_spec(tmp_path):
    a, b = tmp_path / "a.png", tmp_path / "b.png"
    sha_a, sha_b = png(a, shade=100), png(b, 30, 15, shade=50)
    frame = {"rows": [100, 112], "cols": [0, 24], "frame_wh": [3585, 5377], "k": 1.0}
    return {
        "format": build.SPEC_FORMAT, "kind": "empty-strips", "title": "Fixture sitting", "signer": "Chris",
        "instruction": "Sign from the pixels.\n\nSecond paragraph.",
        "sources": [{"path": str(a), "sha256": sha_a}],
        "run_header": {"golden_chain_git_start": {"commit": "deadbeef"}, "clean_run": True},
        "images": [
            {"id": "pa", "path": str(a), "sha256": sha_a, "caption": "page a", "frame": frame,
             "overlay": [{"x": 0, "y": 0, "w": 20, "h": 3, "colour": "#00a000", "what": "strip boundary 700"}]},
            {"id": "pb", "path": str(b), "sha256": sha_b, "caption": "page b", "overlay": []}],
        "sections": [{"id": "s1", "title": "Section one", "text": "Some text", "image_ids": ["pa"], "rows": [
            {"id": "s1.r1", "label": "Row one", "context": ["ctx"], "image_ids": ["pb"], "fields": [
                field("rad", "radio", ["yes", "no"]), field("sel", "select", ["x", "y"]),
                field("chk", "checkbox", ["p", "q"]), field("txt", "text", required=False),
                field("pick", "pick-row", image_id="pa")]},
            {"id": "s1.r2", "label": "Row two", "context": [], "image_ids": [], "fields": [
                field("prop", "radio", ["confirm", "correct"], proposed="Rom. 4. 11.")]}]}],
        "withheld": [{"what": "row z", "reason": "not ready"}],
        "signature": {"fields": ["name", "date"]},
    }


def write_spec(tmp_path, spec, name="spec.json"):
    p = tmp_path / name
    p.write_bytes(build.canon(spec))
    return p


def do_build(tmp_path, spec, monkeypatch, out="out"):
    monkeypatch.setattr(build, "git_state", lambda repo: dict(CLEAN))
    return build.build(write_spec(tmp_path, spec), tmp_path / out)


def sample_value(f):
    k = f["kind"]
    if f.get("proposed") is not None:
        return {"action": "confirm", "text": None, "proposed": f["proposed"]}
    if k in ("radio", "select"):
        return f["options"][0]
    if k == "checkbox":
        return [f["options"][0]]
    if k == "text":
        return "x"
    return {"image_id": f["image_id"], "y_image": 3, "page_row": 103, "frame_wh": [3585, 5377]}


def make_export(spec, manifest):
    rows = {r["id"]: {"state": "verdict", "values": {f["id"]: sample_value(f) for f in r["fields"]}, "note": ""}
            for s in spec["sections"] for r in s["rows"]}
    return {"format": "golden-chain-console-verdicts/1", "kind": spec["kind"], "build_hash": manifest["build_hash"],
            "spec_sha256": manifest["spec_sha256"], "code_sha256": manifest["code_sha256"],
            "run_header": spec["run_header"], "images": dict(manifest["images"]), "rows": rows,
            "signature": {"name": "Chris", "date": "2026-10-26"}, "complete": True,
            "exported_utc": "2026-10-26T10:00:00Z"}


@pytest.fixture
def sitting(tmp_path, monkeypatch):
    spec = make_spec(tmp_path)
    made = do_build(tmp_path, spec, monkeypatch)
    man = json.loads(made["manifest"].read_text(encoding="utf-8"))
    return {"spec": spec, "made": made, "man": man, "dir": tmp_path}


def run_ingest(s, ex, tmp_path, **kw):
    p = tmp_path / "verdicts.json"
    p.write_text(json.dumps(ex), encoding="utf-8")
    return ingest.ingest(p, s["made"]["manifest"], out_dir=tmp_path / "signed", **kw)


# ---- the page -----------------------------------------------------------------------------------

def page_text(s):
    return s["made"]["html"].read_text(encoding="utf-8")


def test_page_has_csp_and_no_network(sitting):
    t = page_text(sitting)
    assert ("<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; img-src data:; "
            "style-src 'unsafe-inline'; script-src 'unsafe-inline'\">") in t
    assert not re.search(r"""(?:src|href)\s*=\s*["']?\s*(?:https?:)?//""", t, re.I)
    assert not re.search(r"url\(\s*['\"]?\s*(?:https?:)?//", t, re.I)
    assert not re.search(r"<script[^>]*\bsrc=", t) and "<link" not in t


def test_embedded_images_hash_to_printed_sha_and_manifest(sitting):
    import base64
    t = page_text(sitting)
    found = re.findall(r'<figure class="fig" data-image="(\w+)".*?<img src="data:image/png;base64,([^"]+)".*?'
                       r'<div class="sha">sha256 ([0-9a-f]{64})</div>', t, re.S)
    assert sorted(i for i, _, _ in found) == ["pa", "pb"]
    for iid, b64, printed in found:
        assert hashlib.sha256(base64.b64decode(b64)).hexdigest() == printed == sitting["man"]["images"][iid]
    assert t.count("data:image/png;base64,") == 2  # each image once, at its first reference


def test_page_header_and_controls(sitting):
    t = page_text(sitting)
    assert sitting["man"]["build_hash"] in t and "Chris" in t and "deadbeef" in t
    assert "PROVISIONAL" not in t.split("</header>")[0]
    for needle in ('data-kind="pick-row"', 'data-kind="proposal"', 'value="abstain"', 'value="fault"',
                   'type="date"', "The download is the record.", "beforeunload", "gc-console-"):
        assert needle in t
    assert re.search(r'<script type="application/json" id="data">', t) and "</" not in t.split(
        'id="data">')[1].split("</script>")[0]


def test_provisional_banner(tmp_path, monkeypatch):
    spec = make_spec(tmp_path)
    monkeypatch.setattr(build, "git_state", lambda r: {"commit": "a", "dirty": True, "porcelain": 2})
    made = build.build(write_spec(tmp_path, spec), tmp_path / "o")
    assert "PROVISIONAL" in made["html"].read_text(encoding="utf-8")
    assert json.loads(made["manifest"].read_text(encoding="utf-8"))["provisional"] is True


def test_build_hash_is_the_stated_rule(sitting):
    spec, man = sitting["spec"], sitting["man"]
    spec_sha = hashlib.sha256(json.dumps(spec, ensure_ascii=False, sort_keys=True, indent=1).encode("utf-8")).hexdigest()
    code_sha = hashlib.sha256((ROOT / "tools/console/build.py").read_bytes()
                              + (ROOT / "tools/console/template.html").read_bytes()).hexdigest()
    imgs = {i["id"]: hashlib.sha256(Path(i["path"]).read_bytes()).hexdigest() for i in spec["images"]}
    want = hashlib.sha256(json.dumps({"spec_sha256": spec_sha, "code_sha256": code_sha, "images": imgs},
                                     ensure_ascii=False, sort_keys=True, indent=1).encode("utf-8")).hexdigest()
    assert man["build_hash"] == want and man["build16"] == want[:16]
    assert man["spec_sha256"] == spec_sha and man["code_sha256"] == code_sha
    assert man["html_sha256"] == hashlib.sha256(sitting["made"]["html"].read_bytes()).hexdigest()
    assert sitting["made"]["spec"].read_bytes() == build.canon(spec)
    assert not build.canon(spec).endswith(b"\n") and b"\r" not in build.canon(spec)


def test_same_spec_same_hash_other_dir(sitting, monkeypatch):
    made2 = do_build(sitting["dir"], sitting["spec"], monkeypatch, out="out2")
    assert json.loads(made2["manifest"].read_text(encoding="utf-8"))["build_hash"] == sitting["man"]["build_hash"]


@pytest.mark.parametrize("mutate,msg", [
    (lambda s: Path(s["images"][0]["path"]).unlink(), "missing file"),
    (lambda s: s["images"][0].update(sha256="0" * 64), "sha256 differs"),
    (lambda s: s["images"].append(dict(s["images"][0])), "duplicate image"),
    (lambda s: s["sections"][0]["rows"].append(copy.deepcopy(s["sections"][0]["rows"][0])), "duplicate row"),
    (lambda s: s.update(kind="nope"), "unknown kind"),
    (lambda s: s["sections"][0]["rows"][0]["fields"][4].update(image_id="zz"), "unknown image"),
    (lambda s: s["sections"][0]["rows"][0]["fields"][0].update(kind="slider"), "unknown kind"),
    (lambda s: s["sections"][0]["rows"][0]["fields"][0].update(options=[]), "no options"),
    (lambda s: s["sections"][0]["rows"][0]["fields"].append(dict(s["sections"][0]["rows"][0]["fields"][0])),
     "duplicate field"),
])
def test_build_fails_loud(tmp_path, monkeypatch, mutate, msg):
    spec = make_spec(tmp_path)
    mutate(spec)
    monkeypatch.setattr(build, "git_state", lambda r: dict(CLEAN))
    with pytest.raises(Fail, match=msg):
        build.build(write_spec(tmp_path, spec), tmp_path / "o")
    assert not (tmp_path / "o").exists() or not list((tmp_path / "o").iterdir())


def test_build_twice_with_other_manifest_bytes_is_refused(sitting, monkeypatch):
    monkeypatch.setattr(build, "git_state", lambda r: {"commit": "other", "dirty": False, "porcelain": 0})
    with pytest.raises(Fail, match="different bytes"):
        build.build(sitting["dir"] / "spec.json", sitting["dir"] / "out")


# ---- ingest -------------------------------------------------------------------------------------

def test_ingest_happy_path(sitting):
    ex = make_export(sitting["spec"], sitting["man"])
    out = run_ingest(sitting, ex, sitting["dir"])
    rec = json.loads(out[0].read_text(encoding="utf-8"))
    assert out[0].name == f"signed_empty-strips_{sitting['man']['build16']}.json"
    assert rec["format"] == "golden-chain-console-signed/1" and rec["provisional"] is False
    assert rec["build_hash"] == sitting["man"]["build_hash"] and rec["signer"] == "Chris"
    assert rec["export_sha256"] == hashlib.sha256((sitting["dir"] / "verdicts.json").read_bytes()).hexdigest()
    assert rec["manifest_sha256"] == hashlib.sha256(sitting["made"]["manifest"].read_bytes()).hexdigest()
    assert [r["row_id"] for r in rec["rows"]] == ["s1.r1", "s1.r2"] and rec["signature"]["name"] == "Chris"


def refuses(sitting, ex, msg, **kw):
    with pytest.raises(Fail, match=msg):
        run_ingest(sitting, ex, sitting["dir"], **kw)
    assert not (sitting["dir"] / "signed").exists()


def test_refuses_changed_build_hash(sitting):
    ex = make_export(sitting["spec"], sitting["man"])
    ex["build_hash"] = "0" * 64
    refuses(sitting, ex, "build_hash")


def test_refuses_changed_image_byte(sitting):
    ex = make_export(sitting["spec"], sitting["man"])
    p = Path(sitting["spec"]["images"][0]["path"])
    p.write_bytes(p.read_bytes() + b"\x00")
    refuses(sitting, ex, "image pa: file sha256 differs")


def test_refuses_incomplete(sitting):
    ex = make_export(sitting["spec"], sitting["man"])
    ex["complete"] = False
    refuses(sitting, ex, "not complete")


def test_refuses_required_field_null_even_if_complete_true(sitting):
    ex = make_export(sitting["spec"], sitting["man"])
    ex["rows"]["s1.r1"]["values"]["rad"] = None
    refuses(sitting, ex, "required field rad is unanswered")


def test_refuses_corrected_proposal_without_text(sitting):
    ex = make_export(sitting["spec"], sitting["man"])
    ex["rows"]["s1.r2"]["values"]["prop"] = {"action": "correct", "text": " ", "proposed": "Rom. 4. 11."}
    refuses(sitting, ex, "unanswered")


def test_refuses_abstain_with_value(sitting):
    ex = make_export(sitting["spec"], sitting["man"])
    ex["rows"]["s1.r1"]["state"] = "abstain"
    refuses(sitting, ex, "abstain but fields hold values")


def test_abstain_with_null_values_is_accepted(sitting):
    ex = make_export(sitting["spec"], sitting["man"])
    ex["rows"]["s1.r1"] = {"state": "fault", "values": {k: None for k in ex["rows"]["s1.r1"]["values"]}, "note": "blurred"}
    rec = json.loads(run_ingest(sitting, ex, sitting["dir"])[0].read_text(encoding="utf-8"))
    assert rec["rows"][0]["state"] == "fault" and rec["rows"][0]["note"] == "blurred"


@pytest.mark.parametrize("sig", [{"name": "", "date": "2026-10-26"}, {"name": "Chris", "date": " "}, {}])
def test_refuses_empty_signature(sitting, sig):
    ex = make_export(sitting["spec"], sitting["man"])
    ex["signature"] = sig
    refuses(sitting, ex, "signature")


def test_provisional_manifest_needs_the_flag(sitting):
    man = dict(sitting["man"], provisional=True)
    sitting["made"]["manifest"].write_bytes(build.canon(man))
    ex = make_export(sitting["spec"], man)
    refuses(sitting, ex, "provisional")
    rec = json.loads(run_ingest(sitting, ex, sitting["dir"], provisional=True)[0].read_text(encoding="utf-8"))
    assert rec["provisional"] is True


def test_refuses_missing_and_extra_row(sitting):
    ex = make_export(sitting["spec"], sitting["man"])
    del ex["rows"]["s1.r2"]
    refuses(sitting, ex, "missing .*s1.r2")
    ex = make_export(sitting["spec"], sitting["man"])
    ex["rows"]["zz"] = {"state": "verdict", "values": {}, "note": ""}
    refuses(sitting, ex, "unexpected .*zz")


def test_refuses_kind_and_format_mismatch(sitting):
    ex = make_export(sitting["spec"], sitting["man"])
    ex["kind"] = "wcf1647"
    refuses(sitting, ex, "kinds disagree")
    ex = make_export(sitting["spec"], sitting["man"])
    ex["format"] = "x"
    refuses(sitting, ex, "export format")


def test_refuses_when_console_code_changed_since_build(sitting, monkeypatch):
    # simulation: ingest reads the console code from a copy whose template differs by one byte
    code = sitting["dir"] / "code"
    code.mkdir()
    shutil.copy(ROOT / "tools/console/build.py", code / "build.py")
    (code / "template.html").write_bytes((ROOT / "tools/console/template.html").read_bytes() + b" ")
    monkeypatch.setattr(ingest, "CODE_DIR", code)
    refuses(sitting, make_export(sitting["spec"], sitting["man"]), "console code changed since build")


def test_refuses_changed_spec_copy(sitting):
    p = sitting["made"]["spec"]
    spec = json.loads(p.read_text(encoding="utf-8"))
    spec["title"] = "Other"
    p.write_bytes(build.canon(spec))
    refuses(sitting, make_export(sitting["spec"], sitting["man"]), "spec_sha256")


def test_signed_name_collision_with_other_bytes_is_refused(sitting):
    ex = make_export(sitting["spec"], sitting["man"])
    out = run_ingest(sitting, ex, sitting["dir"])
    out[0].write_bytes(b"{}")
    with pytest.raises(Fail, match="different bytes"):
        run_ingest(sitting, ex, sitting["dir"])


# ---- content-addressed writes ---------------------------------------------------------------------

def test_write_addressed_same_bytes_ok_different_fails_no_tmp(tmp_path):
    for mod in (build, ingest):
        p = tmp_path / f"f_{mod.__name__}.json"
        mod.write_addressed(p, b"abc")
        mod.write_addressed(p, b"abc")
        with pytest.raises(Fail, match="different bytes"):
            mod.write_addressed(p, b"abd")
        assert p.read_bytes() == b"abc"
    assert not list(tmp_path.glob("*.tmp"))


def test_write_addressed_failure_removes_tmp(tmp_path, monkeypatch):
    def boom(a, b):
        raise OSError("no rename")
    monkeypatch.setattr(build.os, "replace", boom)
    with pytest.raises(OSError):
        build.write_addressed(tmp_path / "x.json", b"abc")
    assert not list(tmp_path.iterdir())


def test_write_addressed_digest_check_removes_tmp(tmp_path, monkeypatch):
    real = build.sha256_bytes
    calls = []

    def lying(b):
        calls.append(1)
        return real(b) if len(calls) % 2 else "0" * 64
    monkeypatch.setattr(build, "sha256_bytes", lying)
    with pytest.raises(Fail, match="digest"):
        build.write_addressed(tmp_path / "x.json", b"abc")
    assert not list(tmp_path.iterdir())


def test_render_answer_never_says_unknown_for_a_blank():
    """Finding (b), WCF sitting 318910c8, accepted on report 8: a blank optional field is not "unknown"."""
    assert ingest.render_answer(None) == "not answered"


# ---- console template v2 ---------------------------------------------------------------------------

def test_fit_is_the_default_zoom(sitting):
    t = page_text(sitting)
    opts = re.findall(r'<select class="zoom">(.*?)</select>', t)
    assert opts and all(o.startswith('<option value="fit" selected>') for o in opts)
    assert opts[0].count("selected") == 1
    assert 'addEventListener("resize"' in (build.HERE / "template.html").read_text(encoding="utf-8")


def test_template_version_in_header_and_manifest(sitting):
    assert "console template v5" in page_text(sitting)
    assert sitting["man"]["template_version"] == 5 == build.TEMPLATE_VERSION


def test_help_panel_has_common_then_spec_entries(tmp_path, monkeypatch):
    spec = make_spec(tmp_path)
    spec["help"] = [{"q": "Spec question one?", "a": "Spec answer one."}, {"q": "Spec question two?", "a": "b"}]
    made = do_build(tmp_path, spec, monkeypatch)
    t = made["html"].read_text(encoding="utf-8")
    qs = [build.e(x["q"]) for x in build.COMMON_HELP] + ["Spec question one?", "Spec question two?"]
    assert len(build.COMMON_HELP) == 5
    pos = [t.index(f"<summary>{q}</summary>") for q in qs]
    assert pos == sorted(pos)
    assert '<aside id="help" hidden>' in t and 'id="helpbtn">Help</button>' in t


def test_check_spec_rejects_malformed_help(tmp_path):
    spec = make_spec(tmp_path)
    spec["help"] = [{"q": "only a question"}]
    with pytest.raises(Fail, match="help"):
        build.check_spec(spec)


def test_every_choice_offers_other_as_written(sitting):
    t = page_text(sitting)
    sp = sitting["spec"]
    fields = {f["id"]: f for r in sp["sections"][0]["rows"] for f in r["fields"]}
    rad = build.field_html("s1.r1", fields["rad"])
    sel = build.field_html("s1.r1", fields["sel"])
    chk = build.field_html("s1.r1", fields["chk"])
    prop = build.field_html("s1.r2", fields["prop"])
    for h in (rad, sel, chk):
        assert build.OTHER in h and 'class="txt othertxt" disabled' in h
    assert f'type="radio" name="s1.r1::rad" value="{build.OTHER}"' in rad
    assert f'<option value="{build.OTHER}">' in sel
    assert build.OTHER not in prop and "othertxt" not in prop
    assert t.count("othertxt\" disabled") == 3


def test_check_spec_rejects_reserved_other_option(tmp_path):
    spec = make_spec(tmp_path)
    spec["sections"][0]["rows"][0]["fields"][0]["options"].append(build.OTHER)
    with pytest.raises(Fail, match="reserved"):
        build.check_spec(spec)


def test_ingest_other_as_written_needs_text():
    f = {"id": "c", "kind": "checkbox"}
    assert ingest.answered(f, {"other": "  "}) is False
    assert ingest.answered(f, {"other": "x"}) is True
    assert ingest.answered(f, ["p", {"other": "  "}]) is False
    assert ingest.answered(f, ["p", {"other": "x"}]) is True


def test_render_answer_other_as_written():
    assert ingest.render_answer({"other": "t"}) == 'other, as written: "t"'
    assert ingest.render_answer(["p", {"other": "t"}]) == 'p, other, as written: "t"'


def test_min_ticks_checkbox_needs_n_entries(tmp_path):
    f1 = {"id": "c", "kind": "checkbox", "min_ticks": 1}
    assert ingest.answered(f1, []) is False
    assert ingest.answered(f1, ["rule"]) is True
    assert ingest.answered(f1, [{"other": "x"}]) is True
    assert ingest.answered({"id": "c", "kind": "checkbox"}, []) is True
    spec = make_spec(tmp_path)
    flds = spec["sections"][0]["rows"][0]["fields"]
    flds[2]["min_ticks"] = 0
    with pytest.raises(Fail, match="min_ticks"):
        build.check_spec(spec)
    flds[2]["min_ticks"] = 1
    flds[0]["min_ticks"] = 1  # on a radio
    with pytest.raises(Fail, match="min_ticks"):
        build.check_spec(spec)


# ---- console v3: silence is complete (empty_means), the follow-up kind ----------------------------------

def silent_spec(tmp_path, kind="plumb-line-followup", means="silent"):
    sil = field("modality", "select", ["required", "taught", "forbidden", "silent"], empty_means=means)
    return {
        "format": build.SPEC_FORMAT, "kind": kind, "title": "Follow-up fixture", "signer": "Chris",
        "instruction": "Sign.", "sources": [], "run_header": None, "images": [], "withheld": [],
        "signature": {"fields": ["name", "date"]},
        "sections": [{"id": "loc", "title": "Locus", "text": "", "image_ids": [], "rows": [
            {"id": "loc.locus", "label": "locus", "context": [], "image_ids": [], "fields": [
                field("tier", "select", ["first", "second", "third"]),
                field("clarity", "select", ["settled", "contested", "open"])]},
            {"id": "loc.pa", "label": "Pa", "context": [], "image_ids": [], "fields": [
                dict(sil), field("unchurches", "checkbox", ["unchurches"], required=False)]},
            {"id": "loc.pb", "label": "Pb", "context": [], "image_ids": [], "fields": [
                dict(sil), field("unchurches", "checkbox", ["unchurches"], required=False)]}]}],
    }


def test_check_spec_refuses_empty_means_on_a_radio_or_with_another_value(tmp_path):
    spec = make_spec(tmp_path)
    flds = spec["sections"][0]["rows"][0]["fields"]
    flds[0]["empty_means"] = "silent"  # a radio
    with pytest.raises(Fail, match=r"field s1\.r1/rad: empty_means"):
        build.check_spec(spec)
    del flds[0]["empty_means"]
    flds[1]["empty_means"] = "loud"  # a select, wrong value
    with pytest.raises(Fail, match=r"field s1\.r1/sel: empty_means"):
        build.check_spec(spec)
    flds[1]["empty_means"] = "silent"
    build.check_spec(spec)


def test_select_with_empty_means_renders_data_empty(tmp_path, monkeypatch):
    made = do_build(tmp_path, silent_spec(tmp_path), monkeypatch)
    t = made["html"].read_text(encoding="utf-8")
    assert t.count('data-empty="silent"') == 2
    assert 'data-field="tier" data-kind="select" data-required="1">' in t


def test_followup_export_with_empty_modalities_is_accepted_and_read_as_silent(tmp_path, monkeypatch):
    spec = silent_spec(tmp_path)
    made = do_build(tmp_path, spec, monkeypatch)
    man = json.loads(made["manifest"].read_text(encoding="utf-8"))
    for complete in (True, False):
        ho = tmp_path / f"handoff_{complete}"  # the record names the build, and the export differs per loop
        ho.mkdir()
        monkeypatch.setattr(ingest, "HANDOFF", ho)
        ex = make_export(spec, man)
        ex["complete"] = complete
        for rid in ("loc.pa", "loc.pb"):
            ex["rows"][rid]["values"] = {"modality": None, "unchurches": []}
        p = tmp_path / f"verdicts_{complete}.json"
        p.write_text(json.dumps(ex), encoding="utf-8")
        out = ingest.ingest(p, made["manifest"], out_dir=tmp_path / f"signed_{complete}", write=True,
                            ttl_out=tmp_path / f"pl_{complete}" / "plumb-line.ttl")
        md = ho / f"SIGNED_plumb_line_followup_{man['build16']}.md"
        assert out[3] == md  # signed json, sitting record, ttl, then the SIGNED Markdown
        t = md.read_text(encoding="utf-8")
        assert t.count("left empty, read as silent") == 2 and "not answered" not in t
    # an empty required non-silent field still refuses
    ex = make_export(spec, man)
    ex["rows"]["loc.locus"]["values"]["tier"] = None
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(ex), encoding="utf-8")
    with pytest.raises(Fail, match="required field tier is unanswered"):
        ingest.ingest(p, made["manifest"], out_dir=tmp_path / "signed_bad")


def signed_plumb(rows):
    """A minimal signed record for plumb_ttl: rows = {row_id: {field: value}}."""
    return {"kind": "plumb-line", "build_hash": "a" * 64, "export_sha256": "b" * 64, "signature": {"name": "Chris", "date": "2026-11-12"},
            "rows": [{"row_id": rid, "section": rid.split(".")[0], "label": "", "state": "verdict", "note": "",
                      "fields": [{"id": k, "label": k, "kind": "x", "value": v} for k, v in vals.items()]}
                     for rid, vals in rows.items()]}


def ttl_graph(signed):
    from rdflib import Graph
    g = Graph()
    g.parse(data=ingest.plumb_ttl(signed).decode("utf-8"), format="turtle")
    return g


def unchurches_triples(g):
    from rdflib import URIRef
    return list(g.triples((None, URIRef("https://w3id.org/golden-chain/ontology#unchurches"), None)))


def test_plumb_ttl_unchurches_ticked_on_forbidden_writes_one_triple():
    g = ttl_graph(signed_plumb({"loc.locus": {"tier": "second", "clarity": "settled"},
                                "loc.pa": {"modality": "forbidden", "unchurches": ["unchurches"]},
                                "loc.pb": {"modality": "forbidden", "unchurches": []}}))
    tr = unchurches_triples(g)
    assert len(tr) == 1 and str(tr[0][0]).endswith("position/loc/pa") and tr[0][2].toPython() is True


def test_plumb_ttl_unchurches_refusals_and_silences():
    loc = {"loc.locus": {"tier": "second", "clarity": "settled"}}
    with pytest.raises(Fail, match=r"modality is 'taught'; only forbidden may be flagged \(ADR-0003 R2.3\)"):
        ingest.plumb_ttl(signed_plumb({**loc, "loc.pa": {"modality": "taught", "unchurches": ["unchurches"]}}))
    with pytest.raises(Fail, match="tier-third locus"):
        ingest.plumb_ttl(signed_plumb({"loc.locus": {"tier": "third", "clarity": "settled"},
                                       "loc.pa": {"modality": "forbidden", "unchurches": ["unchurches"]}}))
    other = signed_plumb({**loc, "loc.pa": {"modality": "forbidden", "unchurches": [{"other": "maybe"}]}})
    t = ingest.plumb_ttl(other).decode("utf-8")
    assert "loc.pa.unchurches" in [l for l in t.splitlines() if l.startswith("#   other, as written")][0]
    assert not unchurches_triples(ttl_graph(other))
    for v in (None, []):
        assert not unchurches_triples(ttl_graph(signed_plumb(
            {**loc, "loc.pa": {"modality": "forbidden", "unchurches": v}})))


NODE_DRIVER = r"""
const puppeteer = require('puppeteer');
(async () => {
  const b = await puppeteer.launch({headless: true, args: ['--no-sandbox']});
  const pg = await b.newPage();
  await pg.goto(process.argv[2]);
  const out = await pg.evaluate(() => {
    const set = (sel, v) => { const e = document.querySelector(sel); e.value = v; e.dispatchEvent(new Event('input', {bubbles: true})); };
    set('.row[data-row="loc.locus"] [data-field="tier"] select', 'second');
    set('.row[data-row="loc.locus"] [data-field="clarity"] select', 'settled');
    document.getElementById('sig-name').value = 'Chris';
    document.getElementById('sig-date').value = '2026-11-12';
    document.getElementById('sig-name').dispatchEvent(new Event('input', {bubbles: true}));
    const first = document.getElementById('status').textContent;
    set('.row[data-row="loc.pa"] [data-field="modality"] select', 'forbidden');
    return [first, document.getElementById('status').textContent];
  });
  console.log(JSON.stringify(out));
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
"""


def headless_status(tmp_path, monkeypatch, means):
    import os

    node = shutil.which("node")
    if not node:
        pytest.skip("node is not on PATH")
    root = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True, timeout=60,
                          shell=True).stdout.strip()
    env = dict(os.environ, NODE_PATH=os.pathsep.join(x for x in (os.environ.get("NODE_PATH"), root) if x))
    chk = subprocess.run([node, "-e", "require('puppeteer')"], capture_output=True, text=True, env=env, timeout=60)
    if chk.returncode != 0:
        pytest.skip("the puppeteer module is not available to node (npm root -g: %s)" % root)
    spec = silent_spec(tmp_path, kind="plumb-line", means=means)
    made = do_build(tmp_path, spec, monkeypatch)
    drv = tmp_path / "drive.js"
    drv.write_text(NODE_DRIVER, encoding="utf-8", newline="\n")
    r = subprocess.run([node, str(drv), made["html"].resolve().as_uri()], capture_output=True, text=True,
                       env=env, timeout=120)
    assert r.returncode == 0, r.stderr[-500:]
    return json.loads(r.stdout.strip().splitlines()[-1])


def test_headless_status_counts_rows_left_empty_as_silent(tmp_path, monkeypatch):
    """Legacy v3 wording, empty_means "silent"."""
    first, second = headless_status(tmp_path, monkeypatch, "silent")
    assert first.startswith("complete; 2 left empty, read as silent")
    assert second.startswith("complete; 1 left empty")


def test_headless_status_counts_rows_left_empty_as_unanswered(tmp_path, monkeypatch):
    first, second = headless_status(tmp_path, monkeypatch, "unanswered")
    assert first.startswith("complete; 2 left empty, unanswered (earlier answers stand)")
    assert "read as silent" not in first
    assert second.startswith("complete; 1 left empty, unanswered (earlier answers stand)")


# ---- console v4: empty is unanswered (ADR-0006 R1 section 6) ---------------------------------------------

def test_v4_unanswered_field_renders_and_check_spec_accepts_both_values(tmp_path, monkeypatch):
    made = do_build(tmp_path, silent_spec(tmp_path, means="unanswered"), monkeypatch)
    t = made["html"].read_text(encoding="utf-8")
    assert t.count('data-empty="unanswered"') == 2 and 'data-empty="silent"' not in t
    spec = make_spec(tmp_path)
    flds = spec["sections"][0]["rows"][0]["fields"]
    for v in ("unanswered", "silent"):
        flds[1]["empty_means"] = v  # a select
        build.check_spec(spec)
    flds[1]["empty_means"] = "loud"
    with pytest.raises(Fail, match=r"field s1\.r1/sel: empty_means"):
        build.check_spec(spec)
    flds[1]["empty_means"] = "unanswered"
    flds[0]["empty_means"] = "unanswered"  # a radio
    with pytest.raises(Fail, match=r"field s1\.r1/rad: empty_means"):
        build.check_spec(spec)


def test_v4_export_with_unanswered_modalities_is_complete_and_says_unanswered(tmp_path, monkeypatch):
    spec = silent_spec(tmp_path, means="unanswered")
    made = do_build(tmp_path, spec, monkeypatch)
    man = json.loads(made["manifest"].read_text(encoding="utf-8"))
    ho = tmp_path / "handoff"
    ho.mkdir()
    monkeypatch.setattr(ingest, "HANDOFF", ho)
    ex = make_export(spec, man)
    for rid in ("loc.pa", "loc.pb"):
        ex["rows"][rid]["values"] = {"modality": None, "unchurches": []}
    p = tmp_path / "v.json"
    p.write_text(json.dumps(ex), encoding="utf-8")
    ingest.ingest(p, made["manifest"], out_dir=tmp_path / "signed", write=True,
                  ttl_out=tmp_path / "pl" / "plumb-line.ttl")
    t = (ho / f"SIGNED_plumb_line_followup_{man['build16']}.md").read_text(encoding="utf-8")
    assert t.count("left empty: unanswered, the earlier answer stands") == 2
    assert "read as silent" not in t and "not answered" not in t


def test_v3_legacy_silent_spec_still_checks_and_renders_the_old_wording(tmp_path, monkeypatch):
    spec = silent_spec(tmp_path, means="silent")
    build.check_spec(spec)
    made = do_build(tmp_path, spec, monkeypatch)
    man = json.loads(made["manifest"].read_text(encoding="utf-8"))
    ho = tmp_path / "handoff"
    ho.mkdir()
    monkeypatch.setattr(ingest, "HANDOFF", ho)
    ex = make_export(spec, man)
    ex["rows"]["loc.pa"]["values"] = {"modality": None, "unchurches": []}
    ex["rows"]["loc.pb"]["values"] = {"modality": "taught", "unchurches": []}
    p = tmp_path / "v.json"
    p.write_text(json.dumps(ex), encoding="utf-8")
    ingest.ingest(p, made["manifest"], out_dir=tmp_path / "signed", write=True,
                  ttl_out=tmp_path / "pl" / "plumb-line.ttl")
    t = (ho / f"SIGNED_plumb_line_followup_{man['build16']}.md").read_text(encoding="utf-8")
    assert t.count("left empty, read as silent") == 1 and "unanswered, the earlier answer" not in t


def test_v4_followup_shaped_export_empty_stands_and_silent_removes(tmp_path, monkeypatch):
    """End to end: ingest + plumb_merge into a tmp ttl. pa is left empty (unanswered), pb is chosen silent."""
    import plumb_merge as pm
    import test_plumb_merge as tpm

    spec = silent_spec(tmp_path, means="unanswered")
    made = do_build(tmp_path, spec, monkeypatch)
    man = json.loads(made["manifest"].read_text(encoding="utf-8"))
    ho = tmp_path / "handoff"
    ho.mkdir()
    monkeypatch.setattr(ingest, "HANDOFF", ho)
    d, ttl = tmp_path / "pl" / "sittings", tmp_path / "pl" / "plumb-line.ttl"
    r1 = tpm.rec(1, {**tpm.LOC, "loc.pa": {"modality": "taught"}, "loc.pb": {"modality": "taught"}})
    tpm.write_records(d, [r1])
    ttl.write_bytes(pm.replay([r1]))
    ex = make_export(spec, man)
    ex["rows"]["loc.pa"]["values"] = {"modality": None, "unchurches": []}
    ex["rows"]["loc.pb"]["values"] = {"modality": "silent", "unchurches": []}
    p = tmp_path / "v.json"
    p.write_text(json.dumps(ex), encoding="utf-8")
    ingest.ingest(p, made["manifest"], out_dir=tmp_path / "signed", write=True, ttl_out=ttl)
    t = ttl.read_text(encoding="utf-8")
    assert "holding/plumb-line/loc/pa" in t and "holding/plumb-line/loc/pb" not in t


# ---- console v5: keyboard signing --------------------------------------------------------------------

def kb_spec(tmp_path, keys=None, **over):
    keys = keys or {"i": "italic", "r": "roman", "o": build.OTHER}

    def row(rid, opts):
        return {"id": rid, "label": rid, "context": [], "image_ids": [], "fields": [field("v", "radio", opts)]}
    spec = {
        "format": build.SPEC_FORMAT, "kind": "truthset-italic", "title": "Keyboard fixture", "signer": "Chris",
        "instruction": "Sign.", "sources": [], "images": [], "withheld": [], "signature": {"fields": ["name", "date"]},
        "keyboard": {"field": "v", "keys": keys},
        "sections": [{"id": "words", "title": "Words", "image_ids": [], "rows": [
            row("w1", ["italic", "roman"]), row("w2", ["italic", "roman"]), row("w3", ["italic", "roman"]),
            row("w4", ["italic", "roman"])]},
            {"id": "ccel", "title": "Foot", "image_ids": [], "rows": [row("c1", ["yes", "no"])]}]}
    spec.update(over)
    return spec


@pytest.mark.parametrize("kb,msg", [
    ({"field": "nope", "keys": {"i": "italic"}}, "not a radio"),
    ({"field": "v", "keys": {"I": "italic"}}, "single lowercase"),
    ({"field": "v", "keys": {"ii": "italic"}}, "single lowercase"),
    ({"field": "v", "keys": {"i": "kursiv"}}, "not an option"),
    ({"field": "v", "keys": {}}, "non-empty"),
    ({"field": "v"}, "keys"),
])
def test_check_spec_keyboard_validation(tmp_path, kb, msg):
    spec = kb_spec(tmp_path)
    spec["keyboard"] = kb
    with pytest.raises(Fail, match=msg):
        build.check_spec(spec)


def test_check_spec_keyboard_field_must_be_a_radio(tmp_path):
    spec = kb_spec(tmp_path)
    for s in spec["sections"]:
        for r in s["rows"]:
            r["fields"] = [field("v", "select", r["fields"][0]["options"])]
    with pytest.raises(Fail, match="not a radio"):
        build.check_spec(spec)


def test_check_spec_keyboard_accepts_the_block_and_its_absence(tmp_path):
    spec = kb_spec(tmp_path)
    build.check_spec(spec)
    del spec["keyboard"]
    build.check_spec(spec)


KB_DRIVER = r"""
const puppeteer = require('puppeteer');
(async () => {
  const b = await puppeteer.launch({headless: true, args: ['--no-sandbox']});
  const pg = await b.newPage();
  await pg.goto(process.argv[2]);
  const snap = () => pg.evaluate(() => {
    const cur = Array.from(document.querySelectorAll('.row.cur')).map(r => r.dataset.row);
    const vals = {};
    document.querySelectorAll('.row').forEach(r => {
      const c = r.querySelector('.field input[type=radio]:checked');
      vals[r.dataset.row] = [c ? c.value : null, r.querySelector('.othertxt').value];
    });
    return {cur, vals, focus: document.activeElement.className, status: document.getElementById('status').textContent};
  });
  const out = [await snap()];
  for (const k of ['i', 'r']) { await pg.keyboard.press(k); out.push(await snap()); }
  await pg.keyboard.press('o'); out.push(await snap());
  await pg.keyboard.type('small caps'); out.push(await snap());
  await pg.keyboard.press('Enter'); out.push(await snap());
  await pg.keyboard.press('Backspace'); out.push(await snap());
  await pg.keyboard.press('ArrowRight'); out.push(await snap());
  await pg.keyboard.press('ArrowRight'); out.push(await snap());
  await pg.keyboard.press('ArrowRight'); out.push(await snap());
  await pg.keyboard.press('i'); out.push(await snap());
  await pg.keyboard.press('ArrowLeft'); out.push(await snap());
  console.log(JSON.stringify(out));
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
"""


def node_env():
    import os

    node = shutil.which("node")
    if not node:
        pytest.skip("node is not on PATH")
    root = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True, timeout=60,
                          shell=True).stdout.strip()
    env = dict(os.environ, NODE_PATH=os.pathsep.join(x for x in (os.environ.get("NODE_PATH"), root) if x))
    chk = subprocess.run([node, "-e", "require('puppeteer')"], capture_output=True, text=True, env=env, timeout=60)
    if chk.returncode != 0:
        pytest.skip("the puppeteer module is not available to node (npm root -g: %s)" % root)
    return node, env


def test_headless_keyboard_signing(tmp_path, monkeypatch):
    node, env = node_env()
    made = do_build(tmp_path, kb_spec(tmp_path), monkeypatch)
    drv = tmp_path / "kb.js"
    drv.write_text(KB_DRIVER, encoding="utf-8", newline="\n")
    r = subprocess.run([node, str(drv), made["html"].resolve().as_uri()], capture_output=True, text=True,
                       env=env, timeout=120)
    assert r.returncode == 0, r.stderr[-500:]
    s = json.loads(r.stdout.strip().splitlines()[-1])
    cur = [x["cur"] for x in s]
    assert cur[0] == ["w1"]                                   # starts at the first unanswered row
    assert s[1]["vals"]["w1"][0] == "italic" and cur[1] == ["w2"]   # i signs and advances
    assert s[2]["vals"]["w2"][0] == "roman" and cur[2] == ["w3"]    # r signs and advances
    assert s[3]["vals"]["w3"][0] == build.OTHER and cur[3] == ["w3"]  # o stays and focuses the note
    assert "othertxt" in s[3]["focus"]
    assert s[4]["vals"]["w3"][1] == "small caps" and s[4]["vals"]["w1"][0] == "italic"  # typing is not a key
    assert cur[5] == ["w4"]                                   # Enter advances
    assert cur[6] == ["w3"]                                   # Backspace goes back
    assert cur[7] == ["w4"] and cur[8] == ["c1"] and cur[9] == ["c1"]  # ArrowRight; end of the list holds
    assert s[10]["vals"]["c1"][0] is None and cur[10] == ["c1"]  # i on a row without that option is ignored
    assert cur[11] == ["w4"]                                  # ArrowLeft


# ---- ingest --code-at -----------------------------------------------------------------------------

def _git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                          check=True, capture_output=True, text=True).stdout.strip()


@pytest.fixture
def code_at_sitting(tmp_path, monkeypatch):
    """A console built from a tmp git repo's code; the repo's template then changes in a second commit."""
    repo = tmp_path / "repo"
    code = repo / "tools" / "console"
    code.mkdir(parents=True)
    for n in ("build.py", "template.html"):
        shutil.copy(ROOT / "tools/console" / n, code / n)
    _git(repo, "init", "-q")
    _git(repo, "add", "tools")
    _git(repo, "commit", "-q", "-m", "one")
    first = _git(repo, "rev-parse", "HEAD")
    spec = make_spec(tmp_path)
    monkeypatch.setattr(build, "git_state", lambda r: {"commit": first, "dirty": False, "porcelain": 0})
    made = build.build(write_spec(tmp_path, spec), tmp_path / "out")
    man = json.loads(made["manifest"].read_text(encoding="utf-8"))
    (code / "template.html").write_bytes((code / "template.html").read_bytes() + b"\n<!-- later -->\n")
    _git(repo, "commit", "-q", "-am", "two")
    second = _git(repo, "rev-parse", "HEAD")
    monkeypatch.setattr(ingest, "REPO", repo)
    monkeypatch.setattr(ingest, "CODE_DIR", code)
    monkeypatch.setattr(ingest, "HANDOFF", tmp_path / "handoff")
    return {"spec": spec, "made": made, "man": man, "dir": tmp_path, "first": first, "second": second}


def test_code_at_without_flag_refuses_changed_code(code_at_sitting):
    refuses(code_at_sitting, make_export(code_at_sitting["spec"], code_at_sitting["man"]),
            "console code changed since build")


@pytest.mark.parametrize("abbrev", [False, True])
def test_code_at_first_commit_ingests_and_is_recorded(code_at_sitting, abbrev):
    s = code_at_sitting
    ref = s["first"][:8] if abbrev else s["first"]
    out = run_ingest(s, make_export(s["spec"], s["man"]), s["dir"], code_at=ref, write=True)
    rec = json.loads(out[0].read_text(encoding="utf-8"))
    assert rec["code_at"] == s["first"]
    md = next(p for p in out if p.suffix == ".md").read_text(encoding="utf-8")
    assert f"- console code read from commit {s['first']} (--code-at)" in md


def test_code_at_truthset_markdown_has_the_line():
    signed = {"signer": "C", "signature": {}, "build_hash": "b", "export_sha256": "e", "manifest_sha256": "m",
              "provisional": False, "code_at": "f" * 40,
              "rows": [{"row_id": r, "state": "abstain", "fields": []} for r in ("p912.left", "ccel.p914-foot")]}
    spec = {"title": "T", "sections": [{"id": "words", "rows": []}]}
    assert f"- console code read from commit {'f' * 40} (--code-at)" in ingest.markdown_truthset(signed, spec).decode()
    del signed["code_at"]
    assert "--code-at" not in ingest.markdown_truthset(signed, spec).decode()


def test_code_at_second_commit_unknown_commit_and_dirty_start_refuse(code_at_sitting):
    s = code_at_sitting
    ex = make_export(s["spec"], s["man"])
    with pytest.raises(Fail, match="not the manifest's build commit"):
        run_ingest(s, ex, s["dir"], code_at=s["second"])
    with pytest.raises(Fail, match="rev-parse"):
        run_ingest(s, ex, s["dir"], code_at="0" * 40)
    man = json.loads(s["made"]["manifest"].read_text(encoding="utf-8"))
    man["golden_chain_git_start"]["dirty"] = True
    mp = s["dir"] / "manifest_dirty.json"
    mp.write_text(json.dumps(man), encoding="utf-8")
    (s["dir"] / "verdicts.json").write_text(json.dumps(ex), encoding="utf-8")
    with pytest.raises(Fail, match="dirty"):
        ingest.ingest(s["dir"] / "verdicts.json", mp, out_dir=s["dir"] / "signed", code_at=s["first"])


def test_signed_record_has_no_code_at_without_the_flag(sitting):
    out = run_ingest(sitting, make_export(sitting["spec"], sitting["man"]), sitting["dir"])
    assert "code_at" not in json.loads(out[0].read_text(encoding="utf-8"))
