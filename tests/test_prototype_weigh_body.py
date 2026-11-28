"""tools/prototype/examine_try.py, item 7: the weigh page and the Body pages (synthetic data and real-data counts)."""

import importlib.util
import json
import re
from pathlib import Path

import pytest

from goldenchain import ingest, unchurches, weigh
from gcfix import PREFIXES

TOOL = Path(__file__).resolve().parent.parent / "tools" / "prototype" / "examine_try.py"
spec = importlib.util.spec_from_file_location("examine_try_wb", TOOL)
et = importlib.util.module_from_spec(spec)
spec.loader.exec_module(et)

SENT = ["SENTINEL-COMMENT", "SENTINEL-RESNOTE", "SENTINEL-QUOTE", "SENTINEL-DERIVED"]
PROPOSED = "gc:status <vocab/status/proposed> ; gc:proposedBy <agent/build>"

# Plumb-line stances (user modality in brackets): pA forbidden (L1, first), pB taught -> obligatory and
# pB2 tolerated -> permitted (L2, second), pC forbidden (L3, third), pF forbidden (L5, second, flagged),
# pO forbidden (L4, open: weight 0).  Cells: CELL[user][body modality] in goldenchain.weigh.
SYNTH = PREFIXES + f"""@prefix owl: <http://www.w3.org/2002/07/owl#> .
<agent/build> a gc:Agent ; rdfs:label "Build agent" .
<heading/h> a gc:Heading ; rdfs:label "H" .
<source/s> a gc:SourceWork ; rdfs:label "Source S" .
<source/s/1> a gc:SourceDivision ; dcterms:isPartOf <source/s> .
<source/s/2> a gc:SourceDivision ; dcterms:isPartOf <source/s> .
<source/flag> a gc:SourceWork ; rdfs:label "Flag source" .
<locus/l1> a gc:Locus ; rdfs:label "Locus L1" ; gc:question "L1?"@en ; gc:underHeading <heading/h> ;
    gc:tier <vocab/tier/first> ; gc:clarity <vocab/clarity/settled> ; rdfs:comment "SENTINEL-COMMENT locus" .
<locus/l2> a gc:Locus ; rdfs:label "Locus L2" ; gc:question "L2?"@en ; gc:underHeading <heading/h> ;
    gc:tier <vocab/tier/second> ; gc:clarity <vocab/clarity/settled> .
<locus/l3> a gc:Locus ; rdfs:label "Locus L3" ; gc:question "L3?"@en ; gc:underHeading <heading/h> ;
    gc:tier <vocab/tier/third> ; gc:clarity <vocab/clarity/settled> .
<locus/l4> a gc:Locus ; rdfs:label "Locus L4" ; gc:question "L4?"@en ; gc:underHeading <heading/h> ;
    gc:tier <vocab/tier/first> ; gc:clarity <vocab/clarity/open> .
<locus/l5> a gc:Locus ; rdfs:label "Locus L5" ; gc:question "L5?"@en ; gc:underHeading <heading/h> ;
    gc:tier <vocab/tier/second> ; gc:clarity <vocab/clarity/settled> .
<locus/l6> a gc:Locus ; rdfs:label "Locus L6" ; gc:question "L6?"@en ; gc:underHeading <heading/h> ;
    gc:tier <vocab/tier/second> ; gc:clarity <vocab/clarity/settled> .
<position/pa> a gc:Position ; rdfs:label "Pos A" ; gc:answers <locus/l1> ; {PROPOSED} .
<position/pb> a gc:Position ; rdfs:label "Pos B" ; gc:answers <locus/l2> ; {PROPOSED} .
<position/pb2> a gc:Position ; rdfs:label "Pos B2" ; gc:answers <locus/l2> ; {PROPOSED} .
<position/pc> a gc:Position ; rdfs:label "Pos C" ; gc:answers <locus/l3> ; {PROPOSED} .
<position/po> a gc:Position ; rdfs:label "Pos O" ; gc:answers <locus/l4> ; {PROPOSED} .
<position/pf> a gc:Position ; rdfs:label "Pos F" ; gc:answers <locus/l5> ; {PROPOSED} .
<position/pz> a gc:Position ; rdfs:label "Pos Z" ; gc:answers <locus/l6> ; {PROPOSED} .

<body/plumb-line> a gc:Body ; gc:unchurches <position/pf> ;
    gc:holds <holding/pl/a> , <holding/pl/b> , <holding/pl/b2> , <holding/pl/c> , <holding/pl/o> , <holding/pl/f> .
<holding/pl/a> a gc:Holding ; gc:position <position/pa> ; gc:modality <vocab/modality/forbidden> ;
    dcterms:source <source/s/1> ; {PROPOSED} .
<holding/pl/b> a gc:Holding ; gc:position <position/pb> ; gc:modality <vocab/modality/taught> ;
    dcterms:source <source/s/1> ; {PROPOSED} .
<holding/pl/b2> a gc:Holding ; gc:position <position/pb2> ; gc:modality <vocab/modality/tolerated> ;
    dcterms:source <source/s/1> ; {PROPOSED} .
<holding/pl/c> a gc:Holding ; gc:position <position/pc> ; gc:modality <vocab/modality/forbidden> ;
    dcterms:source <source/s/1> ; {PROPOSED} .
<holding/pl/o> a gc:Holding ; gc:position <position/po> ; gc:modality <vocab/modality/forbidden> ;
    dcterms:source <source/s/1> ; {PROPOSED} .
<holding/pl/f> a gc:Holding ; gc:position <position/pf> ; gc:modality <vocab/modality/forbidden> ;
    dcterms:source <source/s/1> ; {PROPOSED} .
<axiom/flag/pf> a owl:Axiom ; owl:annotatedSource <body/plumb-line> ; owl:annotatedProperty gc:unchurches ;
    owl:annotatedTarget <position/pf> ; dcterms:source <source/flag> ; {PROPOSED} .

<body/wallb> a gc:Body ; rdfs:label "Wall Body" ; rdfs:comment "SENTINEL-COMMENT body" ;
    gc:holds <holding/wallb/a> .
<holding/wallb/a> a gc:Holding ; gc:position <position/pa> ; gc:modality <vocab/modality/required> ;
    dcterms:source <source/s/1> , <source/s/2> ; gc:derivedBy "SENTINEL-DERIVED" ;
    gc:resolutionNote "SENTINEL-RESNOTE" ; {PROPOSED} .
<body/smallb> a gc:Body ; rdfs:label "Small Difference Body" ; gc:holds <holding/smallb/b> , <holding/smallb/b2> .
<holding/smallb/b> a gc:Holding ; gc:position <position/pb> ; gc:modality <vocab/modality/taught> ;
    dcterms:source <source/s/1> ; {PROPOSED} .
<holding/smallb/b2> a gc:Holding ; gc:position <position/pb2> ; gc:modality <vocab/modality/required> ;
    dcterms:source <source/s/2> ; rdfs:comment "SENTINEL-COMMENT holding" ; {PROPOSED} .
<body/breakb> a gc:Body ; rdfs:label "Break Body" ; gc:holds <holding/breakb/c> .
<holding/breakb/c> a gc:Holding ; gc:position <position/pc> ; gc:modality <vocab/modality/taught> ;
    dcterms:source <source/s/2> ; gc:quotation "SENTINEL-QUOTE" ; {PROPOSED} .
<body/zerob> a gc:Body ; rdfs:label "Zero Body" ; gc:holds <holding/zerob/b> .
<holding/zerob/b> a gc:Holding ; gc:position <position/pb> ; gc:modality <vocab/modality/taught> ;
    dcterms:source <source/s/1> ; {PROPOSED} .
<body/inhb> a gc:Body ; rdfs:label "Inheriting Body" ; gc:childOf <body/zerob> .
<body/noneb> a gc:Body ; rdfs:label "Nothing Covered Body" ; gc:holds <holding/noneb/z> .
<holding/noneb/z> a gc:Holding ; gc:position <position/pz> ; gc:modality <vocab/modality/taught> ;
    dcterms:source <source/s/1> ; {PROPOSED} .
<body/exb> a gc:Confession ; rdfs:label "Excluded Confession" ; gc:holds <holding/exb/f> .
<holding/exb/f> a gc:Holding ; gc:position <position/pf> ; gc:modality <vocab/modality/taught> ;
    dcterms:source <source/s/1> , <source/s/2> ; {PROPOSED} .
"""

NAMES = ("wallb", "smallb", "breakb", "zerob", "inhb", "noneb", "exb")


@pytest.fixture(scope="module")
def synth(tmp_path_factory):
    d = tmp_path_factory.mktemp("wb-data")
    (d / "synth.ttl").write_text(SYNTH, encoding="utf-8", newline="\n")
    outs = [tmp_path_factory.mktemp(f"wb-out{i}") for i in range(2)]
    off = tmp_path_factory.mktemp("wb-off")
    sums = [et.build(o, "rdflib", d, weigh_pages=True) for o in outs]
    et.build(off, "rdflib", d)
    g = ingest.union(ingest.derive_rdflib(ingest.load_dataset(d)))
    return {"out": outs[0], "out2": outs[1], "off": off, "summary": sums[0], "g": g}


def read(out, rel):
    return (Path(out) / rel).read_text(encoding="utf-8")


def sections(html):
    """{h2 text: body text up to the next h2}."""
    parts = re.split(r"<h2>(.*?)</h2>", html)
    return {parts[i]: parts[i + 1] for i in range(1, len(parts), 2)}


def U(rel):
    return ingest.URIRef(ingest.B + rel)


# ---- pure functions

def test_group_rules():
    assert et.group({"walls": [1], "coverage": 0.5}, [1]) == "could not join"
    assert et.group({"walls": [], "coverage": 0.5}, [1]) == "could join with stated differences"
    assert et.group({"walls": [], "coverage": 0.5}, []) == "could join"
    assert et.group({"walls": [], "coverage": 0.0}, []) == "no locus covered"
    assert et.group({"walls": [], "coverage": None}, []) == "no locus covered"


def test_differences_small_and_break(synth):
    g = synth["g"]
    small = et.differences(g, U("body/smallb"))
    assert [d["locus"] for d in small] == [U("locus/l2")]
    d = small[0]
    assert d["cell"] == 0.1 and d["break"] is False and d["tier"] == "second"
    assert d["positions"] == [(U("position/pb2"), "required", "tolerated", [U("source/s/2")])]
    big = et.differences(g, U("body/breakb"))
    assert [(x["locus"], x["cell"], x["break"]) for x in big] == [(U("locus/l3"), 0.75, True)]
    assert 0 < small[0]["cell"] < 0.25 <= big[0]["cell"]


def test_differences_empty_for_wall_zero_and_uncovered(synth):
    g = synth["g"]
    for n in ("wallb", "zerob", "inhb", "noneb"):
        assert et.differences(g, U(f"body/{n}")) == [], n


def test_differences_agree_with_score(synth):
    g = synth["g"]
    for b in weigh.bodies(g):
        if b in unchurches.excluded(g):
            continue
        s = weigh.score(g, b)
        diffs = et.differences(g, b)
        assert {x["locus"] for x in diffs if x["break"]} == {l for l, _, v in s["breaks"] if v != weigh.WALL}


def test_holding_sources(synth):
    g = synth["g"]
    assert et.holding_sources(g, U("body/wallb"), U("position/pa"), "required") == [U("source/s/1"), U("source/s/2")]
    assert et.holding_sources(g, U("body/wallb"), U("position/pa"), "taught") == []
    assert et.holding_sources(g, U("body/inhb"), U("position/pb"), "taught") == [U("source/s/1")]
    assert et.holding_sources(g, U("body/noneb"), U("position/pa"), "taught") == []


# ---- weigh.html

def test_weigh_groups_and_listing(synth):
    t = read(synth["out"], "weigh.html")
    assert t.count(f"<p>{et.esc(unchurches.UNSIGNED)}</p>") == 2
    secs = sections(t)
    names = [n.replace("&#x27;", "'") for n in secs]
    assert names[:4] == ["Could join", "Could join with stated differences", "Could not join", "No locus covered"]
    assert names[4] == unchurches.HEADING
    want = {"Could join": ["body/zerob.html", "body/inhb.html"],
            "Could join with stated differences": ["body/smallb.html", "body/breakb.html"],
            "Could not join": ["body/wallb.html"], "No locus covered": ["body/noneb.html"]}
    for name, members in want.items():
        sec = next(v for k, v in secs.items() if k == name)
        found = re.findall(r'<a href="(body/[^"]+)"', sec)
        assert sorted(found) == sorted(members), name
    listing = next(v for k, v in secs.items() if k.replace("&#x27;", "'") == unchurches.HEADING)
    assert re.findall(r'<a href="(body/[^"]+)"', listing) == ["body/exb.html"]
    for ranked in ("wallb", "smallb", "breakb", "zerob", "inhb", "noneb"):
        assert t.count(f'href="body/{ranked}.html"') == 1
    assert t.count('href="body/exb.html"') == 1
    assert "<p>none</p>" not in "".join(v for k, v in secs.items() if k in want)


def test_weigh_listing_row_has_sources_and_flag_source(synth):
    t = read(synth["out"], "weigh.html")
    row = "<tr><td>position/pf</td><td>taught</td><td>source/s/1, source/s/2</td><td>source/flag</td></tr>"
    assert t.count(row) == 1
    g = synth["g"]
    assert t.count("<tr><td>") == sum(len(r) for r in unchurches.excluded(g).values())
    assert f"<p>{et.esc(unchurches.MEMBERS)}</p>" in t and et.esc(unchurches.wording(g, U("body/exb"))) in t
    assert "[Confession]" in t


def test_weigh_line_numbers_are_weighs_own(synth):
    g = synth["g"]
    t = read(synth["out"], "weigh.html")
    s = weigh.score(g, U("body/breakb"))
    line = (f"walls 0; differences 1; cost {weigh._fmt(s['cost'])} over {s['n_cost']} loci; "
            f"coverage {weigh._fmt(s['coverage'])}")
    assert line in t


# ---- Body pages

def test_body_pages_one_per_body_none_for_plumb(synth):
    g = synth["g"]
    got = sorted(p.name for p in (synth["out"] / "body").glob("*.html"))
    assert got == sorted(f"{et.slug(str(b))}.html" for b in weigh.bodies(g))
    assert got == sorted(f"{n}.html" for n in NAMES)
    assert "plumb-line.html" not in got
    assert synth["summary"]["body_pages"] == len(got) and synth["summary"]["weigh_pages"] == 1
    assert synth["summary"]["weigh_source"] == "rdflib"
    h = json.loads(read(synth["out"], "run_header.json"))
    assert (h["weigh_pages"], h["body_pages"], h["weigh_source"]) == (1, len(got), "rdflib")


def test_wall_page(synth):
    t = read(synth["out"], "body/wallb.html")
    secs = sections(t)
    assert "group: could not join" in t
    assert "position/pa, required against plumb-line forbidden; sources: source/s/1, source/s/2" in secs["Walls"]
    assert "(tier first)" in secs["Walls"]
    assert "<p>none</p>" in secs["Differences"]


def test_difference_pages_keep_walls_apart(synth):
    small = sections(read(synth["out"], "body/smallb.html"))
    assert "<p>none</p>" in small["Walls"]
    assert "cell 0.1" in small["Differences"] and "break" not in small["Differences"]
    assert "position/pb2, required against plumb-line tolerated; sources: source/s/2" in small["Differences"]
    big = sections(read(synth["out"], "body/breakb.html"))
    assert "cell 0.75 break" in big["Differences"]
    assert "breaks 1" in big["Numbers"]


def test_zero_and_uncovered_pages(synth):
    z = read(synth["out"], "body/zerob.html")
    assert "group: could join" in z and z.count("<p>none</p>") == 2
    n = read(synth["out"], "body/noneb.html")
    assert "group: no locus covered" in n and "cost n/a over 0 loci; coverage 0.0000" in n


def test_excluded_body_page(synth):
    t = read(synth["out"], "body/exb.html")
    assert f"<p>{et.esc(unchurches.UNSIGNED)}</p>" in t
    assert t.count("source/flag") == 1 and "source/s/1, source/s/2" in t
    assert "Walls" not in t and "group:" not in t
    assert f"<p>{et.esc(unchurches.MEMBERS)}</p>" in t


def test_every_effective_holding_row_present(synth):
    g = synth["g"]
    for b in weigh.bodies(g):
        t = read(synth["out"], f"body/{et.slug(str(b))}.html")
        hs = list(g.objects(b, ingest.GC.effectivelyHolds))
        sec = sections(t)["Holdings"]
        assert sec.count("<tr><td>") == len(hs), b
        for h in hs:
            pos = g.value(h, ingest.GC.position)
            row = f"<td>{weigh.rel(pos)}</td><td>{weigh.tail(g.value(h, ingest.GC.modality))}</td>"
            assert row in sec
            srcs = ", ".join(weigh.rel(x) for x in sorted(g.objects(h, et.DCTERMS.source), key=str))
            assert f"<td>{srcs}</td>" in sec
    inh = sections(read(synth["out"], "body/inhb.html"))["Holdings"]
    assert "<td>body/zerob</td>" in inh and "<td>own</td>" not in inh
    assert "<td>own</td>" in sections(read(synth["out"], "body/zerob.html"))["Holdings"]


def test_locus_links_only_to_existing_examine_pages(synth):
    t = read(synth["out"], "body/wallb.html")
    assert '<a href="../examine/l1.html">locus/l1</a>' in t
    assert (synth["out"] / "examine" / "l1.html").exists()
    assert '<a href="../weigh.html">Weigh</a>' in t


# ---- banner, free text, determinism, index

def test_banner_on_every_page(synth):
    head = json.loads(read(synth["out"], "run_header.json"))["git_head"][:12]
    banner = et.esc(et.BANNER.format(head=head))
    ps = sorted(synth["out"].rglob("*.html"))
    assert len(ps) == 1 + 1 + 6 + len(NAMES) and any(p.name == "weigh.html" for p in ps)
    for p in ps:
        assert banner in p.read_text(encoding="utf-8"), p


def test_no_free_text_anywhere(synth):
    for p in synth["out"].rglob("*.html"):
        t = p.read_text(encoding="utf-8")
        for s in SENT:
            assert s not in t, (p, s)
        assert "<script" not in t


def test_two_builds_byte_identical(synth):
    a, b = synth["out"], synth["out2"]
    names = sorted(p.relative_to(a).as_posix() for p in a.rglob("*") if p.is_file())
    assert names == sorted(p.relative_to(b).as_posix() for p in b.rglob("*") if p.is_file())
    for n in names:
        assert (a / n).read_bytes() == (b / n).read_bytes(), n


def test_index_differs_only_by_one_link_line(synth):
    on = read(synth["out"], "index.html").split("\n")
    off = read(synth["off"], "index.html").split("\n")
    i = on.index("<h1>Index</h1>")
    assert on[i + 1] == '<p><a href="weigh.html">Weigh</a></p>' and on.count(on[i + 1]) == 1
    assert on[:i + 1] + on[i + 2:] == off
    # every existing page is unchanged by the new pages
    for p in (synth["off"]).rglob("*.html"):
        rel = p.relative_to(synth["off"]).as_posix()
        if rel != "index.html":
            assert p.read_bytes() == (synth["out"] / rel).read_bytes(), rel
    assert not (synth["off"] / "weigh.html").exists()


# ---- real data: counts derived

def test_real_data_counts_consistent(tmp_path):
    s = et.build(tmp_path, "rdflib", weigh_pages=True)
    g = ingest.union(ingest.derive_rdflib(ingest.load_dataset()))
    res = weigh.weigh(g, "members")
    bodies = weigh.bodies(g)
    assert s["body_pages"] == len(bodies) == len(list((tmp_path / "body").glob("*.html")))
    assert not (tmp_path / "body" / "plumb-line.html").exists()
    t = (tmp_path / "weigh.html").read_text(encoding="utf-8")
    secs = sections(t)
    for b, sc in res["ranked"]:
        name = et.group(sc, et.differences(g, b)).capitalize()
        assert f'href="body/{et.slug(str(b))}.html"' in secs[name], b
        assert "group: " + et.group(sc, et.differences(g, b)) in (
            tmp_path / "body" / f"{et.slug(str(b))}.html").read_text(encoding="utf-8")
    listing = next(v for k, v in secs.items() if k.replace("&#x27;", "'") == unchurches.HEADING)
    assert len(re.findall(r"<h3>", listing)) == len(unchurches.excluded(g))
    assert listing.count("<tr><td>") == sum(len(r) for r in unchurches.excluded(g).values())
