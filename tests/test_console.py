import copy
import hashlib
import json
import re
import shutil
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
