import json
import re
import sys
from pathlib import Path

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools" / "console"))
sys.path.insert(0, str(ROOT / "tools" / "console" / "specs"))
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import empty_strips  # noqa: E402
import ingest  # noqa: E402
import plumb_line  # noqa: E402
import test_console as tc  # noqa: E402
import wcf1647  # noqa: E402
from column_rule import Fail  # noqa: E402
from rdflib import DCTERMS, RDF, Graph, Namespace, URIRef  # noqa: E402

GC = Namespace("https://w3id.org/golden-chain/ontology#")
BASE = "https://w3id.org/golden-chain/"


def built(tmp_path, monkeypatch, spec_path):
    monkeypatch.setattr(build, "git_state", lambda r: dict(tc.CLEAN))
    made = build.build(spec_path, tmp_path / "out")
    return made, json.loads(made["manifest"].read_text(encoding="utf-8"))


def sign(tmp_path, made, man, spec, mutate=None, **kw):
    ex = tc.make_export(spec, man)
    if mutate:
        mutate(ex)
    p = tmp_path / "verdicts.json"
    p.write_text(json.dumps(ex), encoding="utf-8")
    return ingest.ingest(p, made["manifest"], out_dir=tmp_path / "signed", **kw)


# ---- (i) empty strips -----------------------------------------------------------------------------

def strips_dir(tmp_path):
    d = tmp_path / "strips"
    d.mkdir()
    entries = []

    def add(name, page, kind, native):
        tc.png(d / name, 16, 8, shade=90 + len(entries))
        entries.append({"file": name, "sha256": build.sha256_file(d / name), "page": page, "kind": kind,
                        "native": native, "rows": [700, 708], "cols": [0, 16], "frame_wh": [3585, 5377],
                        "k": 1.4227 if native else 1.0, "line_h": 60 + page % 10,
                        "overlay": [{"x": 0, "y": 0, "w": 16, "h": 2, "colour": "#00a000", "what": "tick 700"}]})
    add("p896-gutter-full.png", 896, "gutter-full", False)
    add("p896-gutter-full-native.png", 896, "gutter-full", True)
    add("p896-foot.png", 896, "foot", False)
    add("p896-foot-native.png", 896, "foot", True)
    add("p902-foot.png", 902, "foot", False)
    add("p897-gutter-full.png", 897, "gutter-full", False)
    add("p898-gutter-full.png", 898, "gutter-full", False)
    data = {"header": {"run_header": {"golden_chain_git_start": {"commit": "feedbeef"}, "clean_run": True},
                       "clean_run": True},
            "strips": entries,
            "pages": {str(p): {"ticks": [700], "y_end": 5077, "last_strip": [4900, 5077], "empty_strips": [],
                               "line_h": 64} for p in (896, 902)}}
    (d / "strips.json").write_text(json.dumps(data), encoding="utf-8")
    return d


def row_ids(spec):
    return {s["id"]: [r["id"] for r in s["rows"]] for s in spec["sections"]}


def test_empty_strips_spec_ids_and_build(tmp_path, monkeypatch):
    d = strips_dir(tmp_path)
    out = tmp_path / "spec.json"
    empty_strips.build.write_spec(out, empty_strips.make_spec(d))
    spec = json.loads(out.read_text(encoding="utf-8"))
    assert row_ids(spec) == {
        "h1": ["h1.head", "h1.rule_start", "h1.unruled", "h1.verdict"],
        "foot": ["foot.896", "foot.902", "foot.hypothesis", "foot.stops"],
        "abst": ["abst.897", "abst.898"]}
    rows = {r["id"]: r for s in spec["sections"] for r in s["rows"]}
    assert [f["id"] for f in rows["h1.unruled"]["fields"]] == ["v", "from", "to"]
    assert [f["kind"] for f in rows["h1.unruled"]["fields"]] == ["radio", "pick-row", "pick-row"]
    assert [f["id"] for f in rows["foot.896"]["fields"]] == ["rule_end", "to_foot", "faint", "inks", "other"]
    assert "4900–5077" in rows["foot.896"]["fields"][3]["label"]
    assert rows["foot.896"]["fields"][3]["options"][-1] == "other page furniture"
    assert rows["foot.896"]["image_ids"] == ["p896-foot", "p896-foot-native"]
    assert rows["foot.902"]["image_ids"] == ["p902-foot"]
    assert rows["foot.hypothesis"]["fields"][0]["options"][0].startswith("refuted")
    assert rows["h1.rule_start"]["fields"][0]["image_id"] == "p896-gutter-full"
    assert spec["sections"][0]["text"].startswith("if the pixels refute the geometry reading of H1")
    assert spec["run_header"]["clean_run"] is True and spec["signer"] == "Chris"
    assert "Sign from the pixels." in spec["instruction"] and "3585 x 5377" in spec["instruction"]
    assert {i["id"] for i in spec["images"]} == {Path(f).stem for f in
            (e["file"] for e in json.loads((d / "strips.json").read_text())["strips"])}
    made, man = built(tmp_path, monkeypatch, out)
    assert man["kind"] == "empty-strips"
    t = made["html"].read_text(encoding="utf-8")
    assert t.count("data:image/png;base64,") == 7


def test_empty_strips_sha_mismatch_and_missing_run(tmp_path):
    d = strips_dir(tmp_path)
    (d / "p897-gutter-full.png").write_bytes((d / "p897-gutter-full.png").read_bytes() + b"\0")
    with pytest.raises(Fail, match="sha256 differs"):
        empty_strips.make_spec(d)
    (tmp_path / "again").mkdir()
    d2 = strips_dir(tmp_path / "again")
    sj = json.loads((d2 / "strips.json").read_text())
    sj["strips"] = [s for s in sj["strips"] if s["page"] != 898]
    (d2 / "strips.json").write_text(json.dumps(sj), encoding="utf-8")
    with pytest.raises(Fail, match="p.898"):
        empty_strips.make_spec(d2)


def test_empty_strips_markdown_writer(tmp_path, monkeypatch):
    out = tmp_path / "spec.json"
    build.write_spec(out, empty_strips.make_spec(strips_dir(tmp_path)))
    made, man = built(tmp_path, monkeypatch, out)
    spec = json.loads(made["spec"].read_text(encoding="utf-8"))
    ho = tmp_path / "handoff"
    ho.mkdir()
    monkeypatch.setattr(ingest, "HANDOFF", ho)
    res = sign(tmp_path, made, man, spec, write=True)
    md = ho / f"SIGNED_empty_strips_{man['build16']}.md"
    assert res[1] == md
    t = md.read_text(encoding="utf-8")
    assert "| Row | Question | Answer | State | Note |" in t
    assert "page row 103 (frame 3585x5377)" in t and "feedbeef" in t and "p897-gutter-full: " in t
    assert man["build_hash"] in t and "\r" not in t


# ---- (ii) plumb-line ------------------------------------------------------------------------------

LOCI = ROOT / "data" / "loci.ttl"
FORM = ROOT / "docs" / "loci" / "plumb-line-form-phase1.md"


def form_position_rows():
    return len(re.findall(r"^\| `[^`]+` \|", FORM.read_text(encoding="utf-8"), re.M))


def test_plumb_line_spec_matches_form():
    spec = plumb_line.make_spec(LOCI)
    secs = spec["sections"]
    assert [s["id"] for s in secs] == ["covenant-administrations", "baptism-perpetuity", "johns-baptism",
                                       "baptism-subjects", "baptism-mode", "baptism-formula",
                                       "baptism-significance", "baptism-efficacy", "baptism-repetition"]
    assert [s["title"].split(" ")[0] for s in secs] == ["23", "28", "29", "30", "31", "32", "33a", "33b", "33c"]
    pos_rows = [r for s in secs for r in s["rows"] if not r["id"].endswith(".locus")]
    assert len(pos_rows) == form_position_rows() == 15
    locus_rows = [r for s in secs for r in s["rows"] if r["id"].endswith(".locus")]
    assert len(locus_rows) == 9
    assert [f["id"] for f in locus_rows[0]["fields"]] == ["tier", "clarity"]
    assert pos_rows[0]["fields"][0]["options"] == ["required", "taught", "tolerated", "forbidden", "silent"]
    assert spec["signer"] == "the architect" and spec["images"] == [] and spec["run_header"] is None
    assert "Modality" in spec["instruction"] and "Clarity" in spec["instruction"]


def test_plumb_line_refuses_a_form_that_differs(tmp_path, monkeypatch):
    f = tmp_path / "form.md"
    f.write_text(FORM.read_text(encoding="utf-8").replace("`once-only`", "`twice-only`"), encoding="utf-8")
    monkeypatch.setattr(plumb_line, "FORM", f)
    with pytest.raises(Fail, match="positions differ"):
        plumb_line.make_spec(LOCI)


@pytest.fixture
def plumb(tmp_path, monkeypatch):
    sp = tmp_path / "spec.json"
    build.write_spec(sp, plumb_line.make_spec(LOCI))
    made, man = built(tmp_path, monkeypatch, sp)
    return tmp_path, made, man, json.loads(made["spec"].read_text(encoding="utf-8"))


def modalities(ex):
    ex["rows"]["baptism-subjects.infants"]["values"]["modality"] = "silent"
    ex["rows"]["baptism-mode.immersion-only"]["values"]["modality"] = "forbidden"
    ex["rows"]["baptism-efficacy.sign-only"] = {"state": "abstain", "note": "unsure",
                                                "values": {"modality": None}}
    ex["rows"]["baptism-efficacy.locus"] = {"state": "fault", "note": "", "values": {"tier": None, "clarity": None}}
    ex["rows"]["johns-baptism.locus"]["values"].update(tier="third", clarity="contested")


def test_plumb_line_ttl_writer(plumb):
    tmp, made, man, spec = plumb
    ttl = tmp / "pl.ttl"
    res = sign(tmp, made, man, spec, modalities, write=True, ttl_out=ttl)
    assert res[1] == ttl
    g = Graph()
    g.parse(ttl, format="turtle")
    b = lambda s: URIRef(BASE + s)  # noqa: E731
    holdings = set(g.subjects(RDF.type, GC.Holding))
    assert len(holdings) == 15 - 1 - 1  # one silent, one abstained
    assert b("holding/plumb-line/baptism-subjects/infants") not in holdings
    assert b("holding/plumb-line/baptism-efficacy/sign-only") not in holdings
    assert len(list(g.objects(b("body/plumb-line"), GC.holds))) == 13
    assert (b("locus/johns-baptism"), GC.tier, b("vocab/tier/third")) in g
    assert (b("locus/johns-baptism"), GC.clarity, b("vocab/clarity/contested")) in g
    assert (b("locus/baptism-perpetuity"), GC.tier, b("vocab/tier/first")) in g
    assert len(list(g.subject_objects(GC.tier))) == 8  # baptism-efficacy locus row was a fault
    h = b("holding/plumb-line/baptism-mode/immersion-only")
    assert (h, GC.modality, b("vocab/modality/forbidden")) in g
    assert (h, GC.position, b("position/baptism-mode/immersion-only")) in g
    src = b(f"source/plumb-line/sitting-{man['build16']}")
    assert (h, DCTERMS.source, src) in g and (src, RDF.type, GC.SourceDivision) in g
    rec = json.loads(res[0].read_text(encoding="utf-8"))
    assert str(g.value(src, DCTERMS.identifier)) == rec["export_sha256"]
    text = ttl.read_text(encoding="utf-8")
    assert text.startswith("@base <https://w3id.org/golden-chain/> .") and "baptism-efficacy.sign-only" in text


def test_plumb_line_refuses_data_while_adr_proposed(plumb, monkeypatch):
    tmp, made, man, spec = plumb
    adr = tmp / "adr.md"
    adr.write_text("# ADR\n\n- Status: Proposed\n", encoding="utf-8")
    target = tmp / "data" / "plumb-line.ttl"
    monkeypatch.setattr(ingest, "ADR", adr)
    monkeypatch.setattr(ingest, "PLUMB_TTL", target)
    with pytest.raises(Fail, match="ADR-0006 not ratified: plumb-line TTL not written"):
        sign(tmp, made, man, spec, write=True)
    assert not target.exists() and not (tmp / "signed").exists()
    adr.write_text("# ADR\n\n- Status: Ratified\n", encoding="utf-8")
    sign(tmp, made, man, spec, write=True)
    assert target.is_file()


def test_real_adr_is_not_ratified_yet_or_the_tests_above_need_a_look():
    assert ingest.adr_ratified() == any(
        l.startswith("- Status: Ratified") for l in ingest.ADR.read_text(encoding="utf-8").splitlines())


def test_plumb_line_ttl_refuses_unknown_modality(plumb):
    tmp, made, man, spec = plumb
    with pytest.raises(Fail, match="modality"):
        sign(tmp, made, man, spec, lambda ex: ex["rows"]["johns-baptism.same-ordinance"]["values"].update(
            modality="<x> gc:evil"), write=True, ttl_out=tmp / "x.ttl")
    assert not (tmp / "signed").exists()


# ---- (iii) wcf1647 --------------------------------------------------------------------------------

def proposals(tmp_path):
    for n in ("leaf56-note-b", "leaf24-note-r"):
        tc.png(tmp_path / f"{n}.png", 20, 10)
    p = {"witness": "Edinburgh, Evan Tyler, 1647", "instruction_extra": "Extra line.",
         "images": [{"id": "leaf56-note-b", "path": str(tmp_path / "leaf56-note-b.png"), "caption": "leaf 56",
                     "frame": {"rows": [0, 10], "cols": [0, 20], "frame_wh": [20, 10], "k": 1.0}},
                    {"id": "leaf24-note-r", "path": str(tmp_path / "leaf24-note-r.png"), "caption": "leaf 24"}],
         "chapters": [
             {"id": "ch28", "title": "Ch. 28 (IA leaves 56–57)", "rows": [
                 {"id": "28/1/001", "clause": "a sign and seal", "schaff": "Rom. iv. 11",
                  "image_ids": ["leaf56-note-b"],
                  "proposed": {"letters": "a", "as_printed": "Rom. 4. 11.", "page": "(48)"}}]},
             {"id": "ch7", "title": "Ch. 7", "rows": [
                 {"id": "7/5/001", "clause": "differently administered", "schaff": "2 Cor. iii. 6",
                  "image_ids": ["leaf24-note-r"], "proposed": {"letters": "r", "as_printed": "2 Cor. 3. 6."}}]}],
         "lettering": ["Do the letters run per chapter, starting at a?", "Are j and v skipped?"]}
    out = tmp_path / "proposals.json"
    out.write_text(json.dumps(p), encoding="utf-8")
    return out


def test_wcf1647_spec_shape(tmp_path):
    spec = wcf1647.make_spec(proposals(tmp_path))
    assert row_ids(spec) == {"ch28": ["ch28.leaves", "28/1/001"], "ch7": ["ch7.leaves", "7/5/001"],
                             "lettering": ["lettering.1", "lettering.2"]}
    rows = {r["id"]: r for s in spec["sections"] for r in s["rows"]}
    fields = rows["28/1/001"]["fields"]
    assert [f["id"] for f in fields] == ["letters", "as_printed", "page"]
    assert all(f["options"] == ["confirm", "correct"] and f["kind"] == "radio" for f in fields)
    assert [f["proposed"] for f in fields] == ["a", "Rom. 4. 11.", "(48)"]
    assert [f["id"] for f in rows["7/5/001"]["fields"]] == ["letters", "as_printed"]
    assert rows["ch28.leaves"]["fields"][0]["options"] == ["confirmed", "differs"]
    assert rows["lettering.1"]["fields"][0]["options"] == ["yes", "no"]
    assert "Write long s as s." in spec["instruction"] and "Extra line." in spec["instruction"]
    assert "recorded as a signed reading" in spec["instruction"]
    assert all(len(i["sha256"]) == 64 for i in spec["images"]) and spec["signer"] == "Chris"


def test_wcf1647_page_heads_and_doubts(tmp_path):
    p = proposals(tmp_path)
    d = json.loads(p.read_text(encoding="utf-8"))
    d["chapters"][0]["image_ids"] = ["leaf56-note-b"]
    d["chapters"][0]["rows"][0]["doubts"] = ["comma or period after 13"]
    p.write_text(json.dumps(d), encoding="utf-8")
    rows = {r["id"]: r for s in wcf1647.make_spec(p)["sections"] for r in s["rows"]}
    assert rows["ch28.leaves"]["image_ids"] == ["leaf56-note-b"] and rows["ch7.leaves"]["image_ids"] == []
    assert rows["28/1/001"]["context"] == ["Schaff (A): Rom. iv. 11", "Doubt: comma or period after 13"]


def test_wcf1647_missing_image_and_missing_letters(tmp_path):
    p = proposals(tmp_path)
    d = json.loads(p.read_text())
    d["chapters"][1]["rows"][0]["proposed"].pop("letters")
    p.write_text(json.dumps(d), encoding="utf-8")
    with pytest.raises(Fail, match="no letters"):
        wcf1647.make_spec(p)
    (tmp_path / "leaf24-note-r.png").unlink()
    with pytest.raises(Fail, match="image missing"):
        wcf1647.make_spec(p)


def test_wcf1647_markdown_renders_a_corrected_field_as_signed_reading(tmp_path, monkeypatch):
    sp = tmp_path / "spec.json"
    build.write_spec(sp, wcf1647.make_spec(proposals(tmp_path)))
    made, man = built(tmp_path, monkeypatch, sp)
    spec = json.loads(made["spec"].read_text(encoding="utf-8"))
    ho = tmp_path / "handoff"
    ho.mkdir()
    monkeypatch.setattr(ingest, "HANDOFF", ho)

    def correct(ex):
        ex["rows"]["28/1/001"]["values"]["as_printed"] = {"action": "correct", "text": "Rom. 4. 11, 12.",
                                                          "proposed": "Rom. 4. 11."}
    res = sign(tmp_path, made, man, spec, correct, write=True)
    t = res[1].read_text(encoding="utf-8")
    assert res[1].name == f"SIGNED_wcf1647_{man['build16']}.md"
    assert 'corrected: "Rom. 4. 11, 12." (proposed "Rom. 4. 11."); signed reading' in t
    assert 'confirmed: "a"' in t and "Reading form: WCF 1647 proof notes as printed" in t
    assert t.count("signed reading") == 1
