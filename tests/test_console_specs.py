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
import plumb_merge  # noqa: E402
import test_console as tc  # noqa: E402
import lbc1677  # noqa: E402
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
    for r in ex["rows"].values():  # the fixture ticks every checkbox; unchurches is ticked only where a test says
        if "unchurches" in r["values"] and spec["kind"] == "plumb-line":
            r["values"]["unchurches"] = []
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
                        "k": 1.4227 if native else 1.0, "line_h": None if native else 60 + page % 10,
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
    assert [f["id"] for f in rows["foot.896"]["fields"]] == ["rule_end", "to_foot", "faint", "inks"]
    assert "4900–5077" in rows["foot.896"]["fields"][3]["label"]
    assert rows["foot.896"]["fields"][3]["options"][-1] == "nothing"
    assert rows["foot.896"]["image_ids"] == ["p896-foot", "p896-foot-native"]
    assert rows["foot.902"]["image_ids"] == ["p902-foot"]
    assert rows["foot.hypothesis"]["fields"][0]["options"][0].startswith("refuted")
    assert rows["h1.rule_start"]["fields"][0]["image_id"] == "p896-gutter-full"
    assert spec["sections"][0]["text"].startswith("if the pixels refute the geometry reading of H1")
    assert spec["run_header"]["clean_run"] is True and spec["signer"] == "Chris"
    assert "Sign from the pixels." in spec["instruction"] and "3585 x 5377" in spec["instruction"]
    assert "Line height by strip: 62–68 px." in spec["instruction"]  # native strips carry line_h None
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
    # 23 is retired (owl:deprecated) and replaced by 23a and 23b (ruling on report 11)
    assert [s["id"] for s in secs] == ["covenant-of-grace", "circumcision-covenant", "baptism-perpetuity",
                                       "johns-baptism", "baptism-subjects", "baptism-mode", "baptism-formula",
                                       "baptism-significance", "baptism-efficacy", "baptism-repetition",
                                       "baptism-validity"]  # 33d, Batch B
    assert [s["title"].split(" ")[0] for s in secs] == ["23a", "23b", "28", "29", "30", "31", "32", "33a",
                                                        "33b", "33c", "33d"]
    pos_rows = [r for s in secs for r in s["rows"] if not r["id"].endswith(".locus")]
    assert len(pos_rows) == 23 and form_position_rows() == 15  # Batch B: +1 repetition, +3 validity
    locus_rows = [r for s in secs for r in s["rows"] if r["id"].endswith(".locus")]
    assert len(locus_rows) == 11
    order, form_pos, _ = plumb_line.read_form(FORM.read_text(encoding="utf-8"))
    for s in secs:  # every locus the form knows (all but 23a, 23b) carries its rows; Batch B adds one after it
        if s["id"] in form_pos:
            got = sorted(r["id"].split(".", 1)[1] for r in s["rows"][1:])
            extra = ["infant-sprinkling-not-baptism"] if s["id"] == "baptism-repetition" else []
            assert got == sorted(form_pos[s["id"]] + extra)
    by_id = {s["id"]: [r["id"].split(".", 1)[1] for r in s["rows"][1:]] for s in secs}
    assert "covenant-administrations" not in by_id
    assert sorted(by_id["covenant-of-grace"]) == sorted(["eternal-with-christ", "established-in-new-covenant",
                                                         "made-in-time-after-fall"])
    assert sorted(by_id["circumcision-covenant"]) == ["administration-of-grace", "not-an-administration-of-grace"]
    assert pos_rows[0]["fields"][0]["options"] == ["required", "taught", "tolerated", "forbidden", "silent"]
    assert spec["signer"] == "Chris" and spec["images"] == []  # ruling, report 7 Q2a and spec["run_header"] is None
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
    assert res[2] == ttl  # signed json, sitting record, ttl
    g = Graph()
    g.parse(ttl, format="turtle")
    b = lambda s: URIRef(BASE + s)  # noqa: E731
    holdings = set(g.subjects(RDF.type, GC.Holding))
    assert len(holdings) == 23 - 1 - 1  # one silent, one abstained
    assert b("holding/plumb-line/baptism-subjects/infants") not in holdings
    assert b("holding/plumb-line/baptism-efficacy/sign-only") not in holdings
    assert len(list(g.objects(b("body/plumb-line"), GC.holds))) == 21
    assert (b("locus/johns-baptism"), GC.tier, b("vocab/tier/third")) in g
    assert (b("locus/johns-baptism"), GC.clarity, b("vocab/clarity/contested")) in g
    assert (b("locus/baptism-perpetuity"), GC.tier, b("vocab/tier/first")) in g
    assert len(list(g.subject_objects(GC.tier))) == 10  # baptism-efficacy locus row was a fault
    h = b("holding/plumb-line/baptism-mode/immersion-only")
    assert (h, GC.modality, b("vocab/modality/forbidden")) in g
    assert (h, GC.position, b("position/baptism-mode/immersion-only")) in g
    src = b(f"source/plumb-line/sitting-{man['build16']}")
    assert (h, DCTERMS.source, src) in g and (src, RDF.type, GC.SourceDivision) in g
    rec = json.loads(res[0].read_text(encoding="utf-8"))
    assert str(g.value(src, DCTERMS.identifier)) == rec["export_sha256"]
    text = ttl.read_text(encoding="utf-8")
    assert text.startswith("@base <https://w3id.org/golden-chain/> .") and "baptism-efficacy.sign-only" in text
    for s in (h, src):  # ruling, report 8 Q1
        assert (s, GC.proposedBy, b("agent/build-agent")) in g and (s, GC.ratifiedBy, b("agent/chris")) in g
    assert str(g.value(h, DCTERMS.dateAccepted)) == "2026-10-26"  # the signature date
    assert (src, DCTERMS.isPartOf, b("source/plumb-line")) in g


def silence(ex):  # the 2026-11-08 sitting: one modality left empty, so console v2 exports complete false
    ex["rows"]["johns-baptism.same-ordinance"]["values"]["modality"] = None
    ex["complete"] = False


def test_plumb_line_null_modality_is_silence(plumb):
    """Ruling, dispatch 2026-11-08 §1: a modality left empty is deliberate silence, a complete verdict."""
    tmp, made, man, spec = plumb
    ttl = tmp / "pl.ttl"
    sign(tmp, made, man, spec, silence, write=True, ttl_out=ttl)
    g = Graph()
    g.parse(ttl, format="turtle")
    assert len(set(g.subjects(RDF.type, GC.Holding))) == 23 - 1
    assert URIRef(BASE + "holding/plumb-line/johns-baptism/same-ordinance") not in set(g.subjects())
    assert "modality left empty, unanswered, untouched: johns-baptism.same-ordinance\n" \
        in ttl.read_text(encoding="utf-8")


def test_plumb_line_silence_does_not_excuse_another_gap(plumb):
    tmp, made, man, spec = plumb
    with pytest.raises(Fail, match="row johns-baptism.locus: required field tier is unanswered"):
        sign(tmp, made, man, spec, lambda ex: (silence(ex), ex["rows"]["johns-baptism.locus"]["values"]
                                               .update(tier=None)), write=True, ttl_out=tmp / "x.ttl")
    with pytest.raises(Fail, match="export is not complete"):
        sign(tmp, made, man, spec, lambda ex: ex.update(complete=False), write=True, ttl_out=tmp / "x.ttl")
    assert not (tmp / "signed").exists() and not (tmp / "x.ttl").exists()


def test_null_modality_is_silence_on_the_plumb_line_only(plumb):
    tmp, made, man, spec = plumb
    ex = tc.make_export(spec, man)
    silence(ex)
    legacy = json.loads(json.dumps(spec))  # a v2 spec: no empty_means; only the plumb-line kind reads modality as silent
    for s_ in legacy["sections"]:
        for r_ in s_["rows"]:
            for f_ in r_["fields"]:
                f_.pop("empty_means", None)
    with pytest.raises(Fail, match="export is not complete"):
        ingest.check_complete(dict(legacy, kind="wcf1647"), ex)
    ingest.check_complete(legacy, ex)
    ingest.check_complete(spec, ex)


def test_plumb_line_ttl_conforms_with_the_real_data(plumb):
    """The writer's output, loaded beside data/*.ttl as graph/plumb-line, has no SHACL violation."""
    from goldenchain import ingest as gi

    tmp, made, man, spec = plumb
    d = tmp / "data"
    d.mkdir()
    for f in (ROOT / "data").glob("*.ttl"):
        if f.name != "plumb-line.ttl":  # the signed sitting; this test's own sitting stands in for it
            (d / f.name).write_bytes(f.read_bytes())
    sign(tmp, made, man, spec, modalities, write=True, ttl_out=d / "plumb-line.ttl")
    violations, _ = gi.shacl_report(gi.union(gi.load_dataset(d)))
    assert violations == []


def test_plumb_line_ttl_refuses_a_signature_date_that_is_not_iso(plumb):
    tmp, made, man, spec = plumb
    with pytest.raises(Fail, match="signature date"):
        sign(tmp, made, man, spec, lambda ex: ex["signature"].update(date="1 Nov 2026"),
             write=True, ttl_out=tmp / "x.ttl")


def test_plumb_line_refuses_data_while_adr_proposed(plumb, monkeypatch):
    tmp, made, man, spec = plumb
    adr = tmp / "adr.md"
    adr.write_text("# ADR\n\n- Status: Proposed\n", encoding="utf-8")
    target = tmp / "data" / "plumb-line.ttl"
    monkeypatch.setattr(ingest, "ADR", adr)
    monkeypatch.setattr(ingest, "PLUMB_TTL", target)
    monkeypatch.setattr(plumb_merge, "RECORDS", tmp / "sittings")  # never the real records
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


def test_plumb_ttl_writes_nothing_for_other_as_written(plumb):
    tmp, made, man, spec = plumb

    def mutate(ex):
        modalities(ex)
        ex["rows"]["baptism-mode.immersion-only"]["values"]["modality"] = {"other": "x"}
        ex["rows"]["johns-baptism.locus"]["values"]["tier"] = {"other": "y"}

    d = tmp / "data"
    d.mkdir()
    for f in (ROOT / "data").glob("*.ttl"):
        if f.name != "plumb-line.ttl":  # the signed sitting; this test's own sitting stands in for it
            (d / f.name).write_bytes(f.read_bytes())
    ttl = d / "plumb-line.ttl"
    sign(tmp, made, man, spec, mutate, write=True, ttl_out=ttl)
    g = Graph()
    g.parse(ttl, format="turtle")
    b = lambda s: URIRef(BASE + s)  # noqa: E731
    assert b("holding/plumb-line/baptism-mode/immersion-only") not in set(g.subjects(RDF.type, GC.Holding))
    assert (b("locus/johns-baptism"), GC.tier, None) not in g
    assert (b("locus/johns-baptism"), GC.clarity, b("vocab/clarity/contested")) in g
    text = ttl.read_text(encoding="utf-8")
    line = [l for l in text.splitlines() if l.startswith("#   other, as written, untouched")][0]
    assert "baptism-mode.immersion-only.modality" in line and "johns-baptism.locus.tier" in line
    from goldenchain import ingest as gi

    violations, _ = gi.shacl_report(gi.union(gi.load_dataset(d)))
    assert violations == []


def test_empty_strips_spec_v2_options(tmp_path):
    spec = empty_strips.make_spec(strips_dir(tmp_path))
    rows = {r["id"]: r for s in spec["sections"] for r in s["rows"]}
    assert empty_strips.STOPS == ["yes", "no: it runs to the foot and is faint near it",
                                  "no: it runs to the foot, solid"]
    assert empty_strips.HYPOTHESIS == [
        "refuted: the rule itself ends above the foot",
        "confirmed: the rule reaches the foot; the extra ink is text edge or footnote ink",
        "runs to the foot, solid: the extra ink is the rule itself"]
    assert rows["foot.hypothesis"]["fields"][0]["options"] == empty_strips.HYPOTHESIS
    assert rows["foot.stops"]["fields"][0]["options"] == empty_strips.STOPS
    inks = rows["foot.896"]["fields"][3]
    assert inks["id"] == "inks" and inks["min_ticks"] == 1 and inks["options"][-1] == "nothing"
    abst = spec["sections"][2]
    assert abst["title"].startswith("Run-1") and abst["text"].strip()
    assert spec["help"]


# ---- console v3: the plumb-line's new fields and help; the follow-up builder ---------------------------

ADR3 = ROOT / "docs" / "adr" / "0003-controlled-vocabularies-and-scoring.md"
CONTENT = ROOT / "docs" / "loci" / "plumb-line-followup-1.json"


def adr_blockquote(heading):
    """Read independently of plumb_line.adr_quote: the quote lines between the heading and the next heading."""
    text = ADR3.read_text(encoding="utf-8")
    body = re.search(r"^### " + re.escape(heading) + r" .*?\n(.*?)(?=^#)", text, re.M | re.S).group(1)
    quote = [l for l in body.splitlines() if l.startswith(">")]
    return "\n".join(re.sub(r"^> ?", "", l) for l in quote).strip()


def test_plumb_line_position_rows_have_modality_and_unchurches_and_help():
    spec = plumb_line.make_spec(LOCI)
    pos_rows = [r for s in spec["sections"] for r in s["rows"] if not r["id"].endswith(".locus")]
    assert pos_rows
    for r in pos_rows:
        mod, unc = r["fields"]
        assert [f["id"] for f in r["fields"]] == ["modality", "unchurches"]
        assert mod["empty_means"] == "unanswered" and mod["kind"] == "select"
        assert unc["kind"] == "checkbox" and unc["options"] == ["unchurches"] and unc["required"] is False
    assert len(spec["help"]) == 6
    assert spec["help"][3]["a"] == adr_blockquote("R2.1") and spec["help"][4]["a"] == adr_blockquote("R2.2")
    assert "R2.1" in spec["help"][3]["q"] and "R2.2" in spec["help"][4]["q"]
    assert any(s["path"] == str(ADR3.resolve()) for s in spec["sources"])
    build.check_spec(spec)


@pytest.fixture
def followup_images(tmp_path):
    d = tmp_path / "imgs"
    d.mkdir()
    for n, im in enumerate(json.loads(CONTENT.read_text(encoding="utf-8"))["images"]):
        tc.png(d / im["file"], 8, 4, shade=50 + n)
    return d


def test_followup_spec_on_the_real_content(followup_images):
    import plumb_line_followup as pf

    spec = pf.make_spec(CONTENT, LOCI, followup_images)
    secs = spec["sections"]
    assert spec["kind"] == "plumb-line-followup" and spec["signer"] == "Chris"
    assert len(secs) == 7
    assert sum(len(s["rows"]) for s in secs) == 25
    # C1 locked 39 fields: MISSED. The content gives 3 locus x 2 + 9 position x 2 + 5 radio + 4 proposal
    # + 1 text + 3 flag = 37; the lock miscounted (~/.golden-chain/item2-console-v3-predictions-locked.txt).
    assert sum(len(r["fields"]) for s in secs for r in s["rows"]) == 37
    assert len(spec["images"]) == 4
    assert [len(s["rows"]) for s in secs] == [6, 3, 1, 7, 2, 3, 3]
    build.check_spec(spec)


def content_with(tmp_path, mutate):
    c = json.loads(CONTENT.read_text(encoding="utf-8"))
    mutate(c)
    p = tmp_path / "content.json"
    p.write_text(json.dumps(c), encoding="utf-8")
    return p


def test_followup_refusals(tmp_path, followup_images):
    import plumb_line_followup as pf

    def mk(mutate):
        return pf.make_spec(content_with(tmp_path, mutate), LOCI, followup_images)

    with pytest.raises(Fail, match="unknown row type 'blob'"):
        mk(lambda c: c["sections"][4]["rows"][0].update(type="blob"))
    with pytest.raises(Fail, match="does not answer the Locus"):
        mk(lambda c: c["sections"][1]["rows"][1].update(position="eternal-with-christ"))
    with pytest.raises(Fail, match="positions without a row"):
        mk(lambda c: c["sections"][0]["rows"].pop(3))
    with pytest.raises(Fail, match="content format"):
        mk(lambda c: c.update(format="other/1"))


# ---- (v) q11-crops --------------------------------------------------------------------------------

def _q11_spec_module():
    import importlib.util
    s = importlib.util.spec_from_file_location("q11_crops_spec", ROOT / "tools" / "console" / "specs" / "q11_crops.py")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def q11_dir(tmp_path):
    crops = []
    for p, n in ((913, 16), (915, 5)):
        name = f"q11-p{p}-slab{n}.png"
        tc.png(tmp_path / name, 20, 10)
        crops.append({"file": name, "sha256": build.sha256_file(tmp_path / name), "page": p, "slab": n,
                      "rows": [0, 10], "cols": [0, 20], "frame_wh": [20, 30], "slab_rows_in_frame": [3, 6],
                      "measured": {"gutter": 277, "left_white": 237, "right_white": 29},
                      "overlay": [{"x": 0, "y": 1, "w": 20, "h": 2, "colour": "#ff00ff", "what": "top"}]})
    (tmp_path / "q11_crops.json").write_text(json.dumps({"header": {"run": "q11-crops"}, "crops": crops}),
                                             encoding="utf-8")
    return tmp_path


def test_q11_spec_shape(tmp_path):
    spec = _q11_spec_module().make_spec(q11_dir(tmp_path))
    build.check_spec(spec)
    assert spec["kind"] == "q11-crops" and len(spec["images"]) == 2
    assert len(spec["sections"]) == 1 and len(spec["sections"][0]["rows"]) == 2
    assert sum(len(r["fields"]) for r in spec["sections"][0]["rows"]) == 6


def test_q11_spec_fails(tmp_path):
    m = _q11_spec_module()
    d = q11_dir(tmp_path)
    tc.png(d / "q11-p913-slab16.png", 21, 10)  # sha differs from q11_crops.json
    with pytest.raises(Fail):
        m.make_spec(d)
    (d / "q11-p915-slab5.png").unlink()
    with pytest.raises(Fail):
        m.make_spec(d)


def test_q11_kind_registered():
    assert "q11-crops" in build.KINDS and "q11-crops" in ingest.KINDS


def test_v4_plumb_line_and_followup_builders_mark_modalities_unanswered_with_help(followup_images):
    import plumb_line_followup as pf

    specs = [plumb_line.make_spec(LOCI), pf.make_spec(CONTENT, LOCI, followup_images)]
    for spec in specs:
        mods = [f for s in spec["sections"] for r in s["rows"] for f in r["fields"] if f["id"] == "modality"]
        assert mods
        for f in mods:
            assert f["empty_means"] == "unanswered" and "silent" in f["options"]
        h = [x for x in spec["help"] if x["q"] == "What if I leave a modality empty, or choose silent?"]
        assert len(h) == 1 and "earlier answer" in h[0]["a"] and "silent" in h[0]["a"]
        build.check_spec(spec)


# ---- (vi) truthset-italic -------------------------------------------------------------------------

def _ts_spec_module():
    import importlib.util
    s = importlib.util.spec_from_file_location("ts_italic_spec", ROOT / "tools" / "console" / "specs" / "truthset_italic.py")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def ts_dir(tmp_path, n=3):
    rows = []
    for i in range(1, n + 1):
        i_ = f"w{i:03d}"
        tc.png(tmp_path / f"{i_}_word.png", 20, 10, shade=60 + i)
        tc.png(tmp_path / f"{i_}_line.png", 80, 24, shade=120 + i)
        rows.append({"id": i_, "key": f"913/left/1.1.{i}.0", "page": 913, "region": "left",
                     "word_png": f"{i_}_word.png", "word_sha256": build.sha256_file(tmp_path / f"{i_}_word.png"),
                     "word_size": [20, 10], "line_png": f"{i_}_line.png",
                     "line_sha256": build.sha256_file(tmp_path / f"{i_}_line.png"), "box": [12, 7, 32, 17]})
    extra = {}
    for k, name in (("p912_left", "p912_left.png"), ("p914_left_foot", "p914_left_foot.png")):
        tc.png(tmp_path / name, 90, 40, shade=30)
        extra[k] = {"png": name, "sha256": build.sha256_file(tmp_path / name)}
    (tmp_path / "crops.json").write_text(json.dumps({"rows": rows, "extra": extra}), encoding="utf-8")
    return tmp_path


def test_truthset_spec_shape_and_blind(tmp_path):
    d = ts_dir(tmp_path)
    spec = _ts_spec_module().make_spec(d)
    build.check_spec(spec)
    assert spec["kind"] == "truthset-italic" and [s["id"] for s in spec["sections"]] == ["words", "p912", "ccel"]
    rows = [r for s in spec["sections"] for r in s["rows"]]
    assert len(rows) == 3 + 2 and [r["id"] for r in rows[:3]] == ["w001", "w002", "w003"]
    assert len(spec["images"]) == 2 * 3 + 2
    lines = [i for i in spec["images"] if i["id"].endswith("_line")]
    assert len(lines) == 3 and all(len(i["overlay"]) == 1 for i in lines)
    assert lines[0]["overlay"][0]["x"] == 12 and lines[0]["overlay"][0]["w"] == 20
    assert spec["keyboard"] == {"field": "v", "keys": {"i": "italic", "r": "roman", "o": build.OTHER}}
    assert any("keys" in h["q"] or "key" in h["q"] for h in spec["help"])
    blob = json.dumps(spec).lower()
    for bad in ("stratum", "slant", "slanted", "upright", "edge"):
        assert bad not in blob
    assert rows[0]["label"] == "w001 · p. 913, left column · 913/left/1.1.1.0"


def test_truthset_spec_fails(tmp_path):
    m = _ts_spec_module()
    d = ts_dir(tmp_path)
    tc.png(d / "w002_line.png", 81, 24)  # sha differs from crops.json
    with pytest.raises(Fail):
        m.make_spec(d)
    d2 = ts_dir(tmp_path / "x" if (tmp_path / "x").mkdir() is None else tmp_path)
    (d2 / "p912_left.png").unlink()
    with pytest.raises(Fail):
        m.make_spec(d2)


def test_truthset_kind_registered():
    assert "truthset-italic" in build.KINDS and "truthset-italic" in ingest.KINDS


def test_truthset_ingest_write_records_keys_and_answers(tmp_path, monkeypatch):
    spec_in = _ts_spec_module().make_spec(ts_dir(tmp_path))
    out = tmp_path / "spec.json"
    build.write_spec(out, spec_in)
    made, man = built(tmp_path, monkeypatch, out)
    spec = json.loads(made["spec"].read_text(encoding="utf-8"))
    ho = tmp_path / "handoff"
    ho.mkdir()
    monkeypatch.setattr(ingest, "HANDOFF", ho)

    def answers(ex):
        ex["rows"]["w001"]["values"]["v"] = "italic"
        ex["rows"]["w002"]["values"]["v"] = "roman"
        ex["rows"]["w003"]["values"]["v"] = {"other": "small caps"}
        ex["rows"]["p912.left"]["values"] = {"face": "mixed", "what": "a creed"}
        ex["rows"]["ccel.p914-foot"]["values"]["v"] = "yes"
        ex["rows"]["w001"]["note"] = "a note"
        ex["rows"]["ccel.p914-foot"]["note"] = "crop fault | here"
    res = sign(tmp_path, made, man, spec, answers, write=True)
    md = ho / f"SIGNED_truthset_italic_{man['build16']}.md"
    assert res[1] == md
    t = md.read_text(encoding="utf-8")
    assert "| id | key | answer | note |" in t
    assert "| w001 | 913/left/1.1.1.0 | italic | a note |" in t and "| w002 | 913/left/1.1.2.0 | roman |  |" in t
    assert "| w003 | 913/left/1.1.3.0 | other: small caps |  |" in t
    assert "p912.left face: mixed" in t and "p912.left what: a creed" in t and "footnotes: yes" in t
    assert "ccel.p914-foot note: crop fault \| here" in t
    assert man["build_hash"] in t and "\r" not in t


# ---- (vii) region-reask and the region-question check ------------------------------------------------

def _rr_module():
    import importlib.util
    s = importlib.util.spec_from_file_location("region_reask_spec", ROOT / "tools" / "console" / "specs" / "region_reask.py")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def rr_dirs(tmp_path, w=40, h=120, box_y0=70):
    crops, ocr = tmp_path / "crops", tmp_path / "ocr"
    (ocr / "regions").mkdir(parents=True)
    crops.mkdir()
    sha = tc.png(ocr / "regions" / "p914-left.png", w, h)
    (crops / "crops.json").write_text(json.dumps({
        "extra": {"p914_left_foot": {"box_region": [0, box_y0, w, h]}}, "input": {"regions/p914-left.png": sha}}),
        encoding="utf-8")
    return crops, ocr


def rq_spec(**rq):
    spec = tc.make_spec(Path(rq.pop("tmp")))
    row = spec["sections"][0]["rows"][0]
    row["region_question"] = {"image_id": "pb", "roi": [0, 6127, 2480, 6600], "source_wh": [2480, 6600],
                              "crop_box": [0, 6097, 2480, 6600], **rq}
    return spec


def test_region_question_whole_source_passes(tmp_path):
    build.check_spec(rq_spec(tmp=tmp_path, crop_box=[0, 0, 2480, 6600]))


def test_region_question_old_foot_geometry_fails(tmp_path):
    with pytest.raises(Fail, match=r"s1\.r1.*above.*30 px shown"):
        build.check_spec(rq_spec(tmp=tmp_path))


def test_region_question_bad_refs_and_geometry_fail(tmp_path):
    full = dict(crop_box=[0, 0, 2480, 6600])
    with pytest.raises(Fail, match="not one of the row's images"):
        build.check_spec(rq_spec(tmp=tmp_path, image_id="pa", **full))
    with pytest.raises(Fail, match="roi"):
        build.check_spec(rq_spec(tmp=tmp_path, roi=[0, 6127, 2480, 6700], **full))
    with pytest.raises(Fail, match="not inside the source"):
        build.check_spec(rq_spec(tmp=tmp_path, crop_box=[0, 0, 2480, 6700], roi=[0, 6127, 2480, 6600]))


def test_region_question_enough_context_passes(tmp_path):
    # roi 500 tall in the middle: needs 500 above and 500 below
    ok = dict(roi=[0, 2000, 2480, 2500], crop_box=[0, 1500, 2480, 3000])
    build.check_spec(rq_spec(tmp=tmp_path, **ok))
    with pytest.raises(Fail, match="below.*499 px shown|below"):
        build.check_spec(rq_spec(tmp=tmp_path, roi=[0, 2000, 2480, 2500], crop_box=[0, 1500, 2480, 2999]))


def test_region_question_sideways_context(tmp_path):
    with pytest.raises(Fail, match="left"):
        build.check_spec(rq_spec(tmp=tmp_path, roi=[1000, 0, 1400, 6600], crop_box=[900, 0, 2480, 6600]))


def test_region_reask_spec_shape_and_build(tmp_path, monkeypatch):
    crops, ocr = rr_dirs(tmp_path)
    m = _rr_module()
    spec = m.make_spec(crops, ocr)
    build.check_spec(spec)
    assert spec["kind"] == "region-reask" and len(spec["images"]) == 1
    rows = [r for s in spec["sections"] for r in s["rows"]]
    assert [r["id"] for r in rows] == ["p914.left-foot"]
    ov = spec["images"][0]["overlay"]
    assert len(ov) == 1 and ov[0]["y"] == 70 + m.FOOT_PAD and ov[0]["h"] == 120 - 100 and ov[0]["w"] == 40
    assert rows[0]["region_question"]["crop_box"] == [0, 0, 40, 120]
    out = tmp_path / "spec.json"
    build.write_spec(out, spec)
    h1 = built(tmp_path, monkeypatch, out)[1]["build_hash"]
    h2 = built(tmp_path / "two" if (tmp_path / "two").mkdir() is None else tmp_path, monkeypatch, out)[1]["build_hash"]
    assert h1 == h2


def test_region_reask_sha_mismatch_fails(tmp_path):
    crops, ocr = rr_dirs(tmp_path)
    tc.png(ocr / "regions" / "p914-left.png", 41, 120)
    with pytest.raises(Fail):
        _rr_module().make_spec(crops, ocr)


def test_region_reask_kind_registered():
    assert "region-reask" in build.KINDS and "region-reask" in ingest.KINDS


# ---- (viii) clear_edges ------------------------------------------------------------------------------

def _ce(tmp_path, block=None, paper=255, ink=0, edges=("top", "bottom"), speck=None):
    import numpy as np
    a = np.full((30, 40), paper, dtype=np.uint8)
    if block == "inside":
        a[3:27, 3:37] = ink
    elif block == "top":
        a[0:10, 10:20] = ink
    elif block == "bottom":
        a[20:30, 10:20] = ink
    elif block == "left":
        a[10:20, 0:10] = ink
    if speck is not None:
        a[0, 5] = speck
        a[10:20, 10:20] = ink
    p = tmp_path / "ce.png"
    Image.fromarray(a, "L").save(p)
    return {"id": "w001-word", "path": str(p), "clear_edges": list(edges)}


def test_clear_edges_inside_margin_passes(tmp_path):
    e = _ce(tmp_path, "inside")
    build.check_clear_edges(e, e["path"])


@pytest.mark.parametrize("block,edge", [("top", "top"), ("bottom", "bottom")])
def test_clear_edges_flush_fails_naming_edge(tmp_path, block, edge):
    e = _ce(tmp_path, block)
    with pytest.raises(Fail, match=f"w001-word: ink touches the {edge} edge"):
        build.check_clear_edges(e, e["path"])


def test_clear_edges_unlisted_edge_passes_and_listed_fails(tmp_path):
    e = _ce(tmp_path, "left")
    build.check_clear_edges(e, e["path"])
    e = _ce(tmp_path, "left", edges=("left",))
    with pytest.raises(Fail, match="left edge"):
        build.check_clear_edges(e, e["path"])


def test_clear_edges_all_white_passes(tmp_path):
    e = _ce(tmp_path)
    build.check_clear_edges(e, e["path"])


def test_clear_edges_grey_paper_and_midgrey_speck(tmp_path):
    e = _ce(tmp_path, "inside", paper=200, ink=30)
    build.check_clear_edges(e, e["path"])
    e = _ce(tmp_path, paper=200, ink=30, speck=150)
    build.check_clear_edges(e, e["path"])


@pytest.mark.parametrize("bad", ["middle", [], ["top", "top"], ["middle"]])
def test_clear_edges_bad_values_fail(tmp_path, bad):
    e = _ce(tmp_path, "inside")
    e["clear_edges"] = bad
    with pytest.raises(Fail, match="clear_edges"):
        build.check_clear_edges(e, e["path"])


def test_clear_edges_in_hash_images_and_absent_key_unchanged(tmp_path):
    spec = tc.make_spec(tmp_path)
    build.hash_images(spec)
    # the fixture image is ink to the edge: requiring a clear top edge must fail the build
    spec["images"][0]["clear_edges"] = ["top"]
    with pytest.raises(Fail, match="flush against ink"):
        build.hash_images(spec)


# ---- plain words on every field (ruling on report 18; ADR-0006 Revision 4; template v6) ----

def _plain_fail(tmp_path, mutate, msg):
    spec = tc.make_spec(tmp_path)
    f = spec["sections"][0]["rows"][0]["fields"]
    mutate(f)
    with pytest.raises(Fail, match=msg):
        build.check_spec(spec)


def _plain_ok(tmp_path, mutate):
    spec = tc.make_spec(tmp_path)
    mutate(spec["sections"][0]["rows"][0]["fields"])
    build.check_spec(spec)


def test_plain_missing_fails(tmp_path):
    _plain_fail(tmp_path, lambda f: f[0].pop("plain"), "s1.r1/rad.*plain")


def test_plain_blank_or_not_a_string_fails(tmp_path):
    _plain_fail(tmp_path, lambda f: f[0].update(plain="   "), "plain")
    _plain_fail(tmp_path, lambda f: f[0].update(plain=["x"]), "plain")


def test_plain_three_sentences_fails_two_pass(tmp_path):
    three = 'Choose "yes" or "no". This is the second. And a third. Choose "other, as written" if none fits.'
    _plain_fail(tmp_path, lambda f: f[0].update(plain=three), "3 or more sentences")
    two = 'Choose "yes" or "no". If none fits, choose "other, as written" and say what you see.'
    _plain_ok(tmp_path, lambda f: f[0].update(plain=two))


def test_plain_abbreviations_without_a_capital_are_not_breaks(tmp_path):
    p = ('p. 914 shows Rom. 6. 3 here: choose "yes" or "no". If none fits, choose "other, as written" and say what you see.')
    assert len(build.SENTENCE_BREAK.findall(p)) == 1
    _plain_ok(tmp_path, lambda f: f[0].update(plain=p))


def test_plain_radio_must_name_every_option_and_other(tmp_path):
    # "no" is a substring of "none", so the omitted-option case uses distinctive option strings
    def two_opts(f, plain):
        f[0].update(options=["alpha", "beta"], plain=plain)
    _plain_fail(tmp_path, lambda f: two_opts(f, 'Choose "alpha". If none fits, choose "other, as written".'),
                "does not name option 'beta'")
    _plain_fail(tmp_path, lambda f: two_opts(f, 'Choose "alpha" or "beta" and say what you see.'), "none fits")


def test_plain_option_is_matched_as_a_whole_word(tmp_path):
    # build agent review: a stray "none" must not count as naming the option "no"
    def yn(f, plain):
        f[0].update(options=["yes", "no"], plain=plain)
    _plain_fail(tmp_path, lambda f: yn(f, 'Choose "yes". If none fits, choose "other, as written".'),
                "does not name option 'no'")

def test_plain_proposal_radio_needs_no_other(tmp_path):
    spec = tc.make_spec(tmp_path)
    prop = spec["sections"][0]["rows"][1]["fields"][0]
    assert prop["proposed"] is not None and "other, as written" not in prop["plain"]
    build.check_spec(spec)


def test_plain_text_field_with_plain_passes(tmp_path):
    spec = tc.make_spec(tmp_path)
    txt = spec["sections"][0]["rows"][0]["fields"][3]
    assert txt["kind"] == "text"
    build.check_spec(spec)
    txt.pop("plain")
    with pytest.raises(Fail, match="plain"):
        build.check_spec(spec)


def test_plain_is_rendered_escaped(tmp_path, monkeypatch):
    spec = tc.make_spec(tmp_path)
    spec["sections"][0]["rows"][0]["fields"][3]["plain"] = "Write <b>a few</b> words & stop."
    made = tc.do_build(tmp_path, spec, monkeypatch)
    page = made["html"].read_text(encoding="utf-8")
    assert 'class="plain"' in page
    assert "Write &lt;b&gt;a few&lt;/b&gt; words &amp; stop." in page


def test_template_version_is_6():
    assert build.TEMPLATE_VERSION == 6


# ---- lbc1677 --------------------------------------------------------------------------------------

def lbc_photos(tmp_path, ext="png", extra=None):
    d = tmp_path / "photos"
    d.mkdir(exist_ok=True)
    for g in lbc1677.GROUPS:
        for n in range(1, (extra or {}).get(g, 1) + 1):
            im = Image.new("RGB", (30, 20), (10 * n, 90, 160))
            im.save(d / f"lbc1677_{g}_{n}.{ext}", "JPEG" if ext in ("jpg", "jpeg") else "PNG")
    return d


def lbc_spec(tmp_path, **kw):
    return lbc1677.make_spec(lbc_photos(tmp_path, **kw), tmp_path / "spec_out")


def test_lbc1677_builds_checks_and_renders(tmp_path, monkeypatch):
    sp = tmp_path / "spec.json"
    build.write_spec(sp, lbc_spec(tmp_path, extra={"ch29": 2}))
    build.check_spec(json.loads(sp.read_text(encoding="utf-8")))
    made, man = built(tmp_path, monkeypatch, sp)
    assert man["kind"] == "lbc1677" and made["html"].exists()


def test_lbc1677_row_counts_and_plain_on_every_field(tmp_path):
    spec = lbc_spec(tmp_path)
    rows = [r for s in spec["sections"] for r in s["rows"]]
    assert len(rows) == 21
    assert len([r for r in rows if r["id"].endswith(".unlisted")]) == 5
    assert len([r for r in rows if r["id"] == "witness"]) == 1
    assert all(f["plain"].strip() for r in rows for f in r["fields"])
    assert [i["id"] for i in spec["images"]][:2] == ["title-1", "ch07-1"]


def test_lbc1677_missing_group_fails(tmp_path):
    d = lbc_photos(tmp_path)
    (d / "lbc1677_ch29_1.png").unlink()
    with pytest.raises(Fail, match="ch29 has no photo"):
        lbc1677.make_spec(d, tmp_path / "o")


def test_lbc1677_bad_file_name_fails(tmp_path):
    d = lbc_photos(tmp_path)
    (d / "stray.png").write_bytes(b"x")
    with pytest.raises(Fail, match="does not match"):
        lbc1677.make_spec(d, tmp_path / "o")


def test_lbc1677_non_contiguous_n_fails(tmp_path):
    d = lbc_photos(tmp_path)
    (d / "lbc1677_ch07_3.png").write_bytes((d / "lbc1677_ch07_1.png").read_bytes())
    with pytest.raises(Fail, match="not contiguous"):
        lbc1677.make_spec(d, tmp_path / "o")


def test_lbc1677_proposed_differing_from_data_fails(tmp_path):
    rows = json.loads(lbc1677.ROWS.read_text(encoding="utf-8"))
    rows["rows"][0]["proposed"] = "e Gen. 3.16."
    rp = tmp_path / "rows.json"
    rp.write_text(json.dumps(rows), encoding="utf-8")
    with pytest.raises(Fail, match="not in asPrinted"):
        lbc1677.make_spec(lbc_photos(tmp_path), tmp_path / "o", rows_path=rp)


def test_lbc1677_jpeg_converts_deterministically(tmp_path):
    d = lbc_photos(tmp_path, ext="jpg")
    a = lbc1677.make_spec(d, tmp_path / "o1")["images"]
    b = lbc1677.make_spec(d, tmp_path / "o2")["images"]
    assert [i["sha256"] for i in a] == [i["sha256"] for i in b]
    assert a[0]["path"].endswith(".png") and a[0]["source_sha256"] != a[0]["sha256"]
    assert Path(a[0]["path"]).read_bytes()[:8] == build.PNG_MAGIC


def test_lbc1677_ingest_renders_confirm_and_correct(tmp_path, monkeypatch):
    sp = tmp_path / "spec.json"
    build.write_spec(sp, lbc_spec(tmp_path))
    made, man = built(tmp_path, monkeypatch, sp)
    spec = json.loads(made["spec"].read_text(encoding="utf-8"))
    ho = tmp_path / "handoff"
    ho.mkdir()
    monkeypatch.setattr(ingest, "HANDOFF", ho)

    def correct(ex):
        ex["rows"]["7.3-e"]["values"]["v"] = {"action": "correct", "text": "e Gen. 3. 15.", "proposed": "e Gen. 3.15."}
    res = sign(tmp_path, made, man, spec, correct, write=True)
    t = res[1].read_text(encoding="utf-8")
    assert res[1].name == f"SIGNED_lbc1677_{man['build16']}.md"
    assert 'corrected: "e Gen. 3. 15." (proposed "e Gen. 3.15."); signed reading' in t
    assert "confirmed:" in t
