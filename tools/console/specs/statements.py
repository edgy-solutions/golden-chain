"""Spec builder, instance (v): the statements console (kind statements).

Usage: python tools/console/specs/statements.py <content.json> <data-dir> <image-dir> <out-spec.json>

The content file (format golden-chain-statements-content/1, e.g. docs/consoles/statements-1.json) holds
"title", "instruction", "images" [{id, file, caption}], "statements" (two own-words statements: id, title,
row, label, plain, context) and "inclusion" (id, title, plain, reason_plain, options, sources). Source IRIs are
relative to https://w3id.org/golden-chain/; existing sources are checked against the SourceWork in data-dir/*.ttl.
Sections 1 and 2 are one text row each; by ruling no wording is suggested. Section 3 is one row per source.
Fails loud on: a wrong content format; a statement carrying "proposed", "value" or "default"; a non-new IRI that
is not a SourceWork in the data; a new IRI that already has triples in the data; source/plumb-line listed; a
duplicate IRI; a proposed value not among the options; a missing image file.
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import build  # noqa: E402
from build import Fail  # noqa: E402

CONTENT_FORMAT = "golden-chain-statements-content/1"
BASE = "https://w3id.org/golden-chain/"
SOURCE_WORK = "https://w3id.org/golden-chain/ontology#SourceWork"
BARRED = ("source/plumb-line",)
HELP = [{"q": "Why is no wording suggested?",
         "a": "By ruling, no model drafts these two statements (ADR-0003 R3.2; ADR-0009 Decision 5). "
              "Write them in your own words."}]


def load_data(data_dir):
    from rdflib import RDF, RDFS, Graph, URIRef
    g = Graph()
    files = sorted(Path(data_dir).glob("*.ttl"))
    if not files:
        raise Fail(f"no .ttl files in {data_dir}")
    for f in files:
        g.parse(f, format="turtle")
    works = {str(s): str(g.value(s, RDFS.label) or "") for s in g.subjects(RDF.type, URIRef(SOURCE_WORK))}
    return g, works


def full(iri):
    return iri if iri.startswith("http") else BASE + iri


def statement_section(s):
    for bad in ("proposed", "value", "default"):
        if bad in s:
            raise Fail(f"statement {s.get('id')}: a suggested wording ({bad!r}) is refused by ruling")
    return {"id": s["id"], "title": s["title"], "text": "", "image_ids": [],
            "rows": [{"id": s["row"], "label": s["label"], "context": list(s.get("context", [])),
                      "image_ids": [],
                      "fields": [{"id": "v", "kind": "text", "label": "Your statement", "plain": s["plain"],
                                  "required": True}]}]}


def inclusion_section(inc, g, works):
    from rdflib import URIRef
    options = inc["options"]
    rows, seen = [], set()
    for s in inc["sources"]:
        rel = s["source"]
        iri = full(rel)
        if rel in BARRED:
            raise Fail(f"{rel}: may not be listed in this batch")
        if iri in seen:
            raise Fail(f"{rel}: listed twice")
        seen.add(iri)
        new = bool(s.get("new"))
        if new:
            if (URIRef(iri), None, None) in g:
                raise Fail(f"{rel}: marked new but already in the data")
            label = "New: " + s["label"]
        else:
            if iri not in works:
                raise Fail(f"{rel}: not a SourceWork in the data")
            label = works[iri]
        if s["proposed"] not in options:
            raise Fail(f"{rel}: proposed {s['proposed']!r} is not one of {options}")
        ctx = [f"Witness: {s['witness']}", f"Status: {s['status']}", f"Role: {s['role']}",
               f"IRI: {iri}" + (" (not yet in the data)" if new else "")]
        fields = [{"id": "include", "kind": "radio", "label": "Include?", "options": list(options),
                   "plain": inc["plain"], "proposed": s["proposed"], "required": True},
                  {"id": "reason", "kind": "text", "label": "Reason (if left out)", "plain": inc["reason_plain"],
                   "required": False}]
        ex = s.get("extra")
        if ex:
            fields.append({"id": ex["id"], "kind": "radio", "label": ex["label"], "options": list(ex["options"]),
                           "plain": ex["plain"], "required": True})
        rows.append({"id": rel.rsplit("/", 1)[-1], "label": label, "context": ctx,
                     "image_ids": list(s.get("image_ids", [])), "fields": fields})
    return {"id": inc["id"], "title": inc["title"], "text": "", "image_ids": [], "rows": rows}


def make_spec(content_path, data_dir, image_dir):
    content_path, image_dir = Path(content_path), Path(image_dir)
    content = json.loads(content_path.read_text(encoding="utf-8"))
    if content.get("format") != CONTENT_FORMAT:
        raise Fail(f"content format {content.get('format')!r}, expected {CONTENT_FORMAT}")
    g, works = load_data(data_dir)
    sections = [statement_section(s) for s in content["statements"]]
    sections.append(inclusion_section(content["inclusion"], g, works))
    images = []
    for im in content["images"]:
        p = (image_dir / im["file"]).resolve()
        if not p.is_file():
            raise Fail(f"image {im['id']}: missing file {p}")
        images.append({"id": im["id"], "path": str(p), "sha256": build.sha256_file(p),
                       "caption": im.get("caption", "")})
    spec = {"format": build.SPEC_FORMAT, "kind": "statements", "title": content["title"], "signer": "Chris",
            "instruction": content["instruction"],
            "sources": [{"path": str(content_path.resolve()), "sha256": build.sha256_file(content_path)}],
            "run_header": None, "images": images, "sections": sections, "withheld": [],
            "help": list(HELP), "signature": {"fields": ["name", "date"]}}
    build.check_spec(spec)
    return spec


def main(argv):
    if len(argv) != 4:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        build.write_spec(argv[3], make_spec(*argv[:3]))
    except Fail as ex:
        print(f"FAIL: {ex}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
