"""Spec builder, instance (ii): the plumb-line grid, loci x positions (the architect).

Usage: python tools/console/specs/plumb_line.py <loci.ttl> <out-spec.json>

One section per gc:Locus that has at least one gc:Position (gc:answers), ordered by skos:notation
(23, 28, ... 33a, 33b, 33c). Rows: <locus-slug>.locus (tier, clarity selects) and
<locus-slug>.<position-slug> (modality select, silent included). The slug is the last IRI segment.
The loci and positions must match docs/loci/plumb-line-form-phase1.md (the "(not minted)" row aside),
else Fail. The instruction copies that form's "How the entries are used" bullets.
"""

import re
import sys
from pathlib import Path

from rdflib import RDF, RDFS, Graph, Namespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import build  # noqa: E402
from build import Fail  # noqa: E402

FORM = build.REPO / "docs" / "loci" / "plumb-line-form-phase1.md"
GC = Namespace("https://w3id.org/golden-chain/ontology#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
TIERS = ["first", "second", "third"]
CLARITIES = ["settled", "contested", "open"]
MODALITIES = ["required", "taught", "tolerated", "forbidden", "silent"]


def tail(iri):
    return str(iri).rsplit("/", 1)[1]


def notation_key(n):
    m = re.fullmatch(r"(\d+)([a-z]*)", n)
    if not m:
        raise Fail(f"locus notation {n!r} is not <number><letters>")
    return int(m.group(1)), m.group(2)


def read_loci(ttl):
    g = Graph()
    g.parse(ttl, format="turtle")
    loci = []
    for loc in g.subjects(RDF.type, GC.Locus):
        poss = sorted(g.subjects(GC.answers, loc))
        if not poss:
            continue
        loci.append({"slug": tail(loc), "notation": str(g.value(loc, SKOS.notation)),
                     "question": str(g.value(loc, GC.question)), "label": str(g.value(loc, RDFS.label)),
                     "positions": [{"slug": tail(p), "label": str(g.value(p, RDFS.label))} for p in poss]})
    return sorted(loci, key=lambda l: notation_key(l["notation"]))


def read_form(form_text):
    """([(notation, slug)], {slug: [position slugs]}, usage bullets) from the blank form."""
    order, pos, cur = [], {}, None
    for line in form_text.splitlines():
        m = re.match(r"## (\S+) `([^`]+)`:", line)
        if m:
            cur = m.group(2)
            order.append((m.group(1), cur))
            pos[cur] = []
        elif cur and (m := re.match(r"\| `([^`]+)` \|", line)):
            pos[cur].append(m.group(1))
    use = re.search(r"- How the entries are used:\n((?:  .*\n)+)", form_text)
    if not use:
        raise Fail(f"{FORM}: no 'How the entries are used' block")
    bullets = [re.sub(r"^\s*- ", "", l) for l in use.group(1).splitlines()]
    return order, pos, bullets


def check_against_form(loci, order, pos):
    got = [(l["notation"], l["slug"]) for l in loci]
    if got != order:
        raise Fail(f"loci differ from the form: ttl {got}, form {order}")
    for l in loci:
        if sorted(p["slug"] for p in l["positions"]) != sorted(pos[l["slug"]]):
            raise Fail(f"{l['slug']}: positions differ from the form")


def sel(fid, label, options):
    return {"id": fid, "kind": "select", "label": label, "options": options, "required": True, "proposed": None}


def section(l):
    rows = [{"id": f"{l['slug']}.locus", "label": f"{l['notation']} {l['label']}", "context": [], "image_ids": [],
             "fields": [sel("tier", "Tier", TIERS), sel("clarity", "Clarity", CLARITIES)]}]
    for p in l["positions"]:
        rows.append({"id": f"{l['slug']}.{p['slug']}", "label": p["label"], "context": [], "image_ids": [],
                     "fields": [sel("modality", "Modality", MODALITIES)]})
    return {"id": l["slug"], "title": f"{l['notation']} {l['slug']}: {l['question']}", "text": "",
            "image_ids": [], "rows": rows}


def make_spec(ttl):
    ttl, form = Path(ttl), FORM.read_text(encoding="utf-8")
    loci = read_loci(ttl)
    order, pos, bullets = read_form(form)
    check_against_form(loci, order, pos)
    instruction = ("The plumb-line: your stance on each Position, and the tier and clarity of each locus "
                   "(ADR-0003 sections 3 to 5a). How the entries are used:\n\n" + "\n\n".join(bullets))
    return {"format": build.SPEC_FORMAT, "kind": "plumb-line", "title": "Plumb-line form: phase 1",
            "signer": "the architect", "instruction": instruction,
            "sources": [{"path": str(p.resolve()), "sha256": build.sha256_file(p)} for p in (ttl, FORM)],
            "run_header": None, "images": [], "sections": [section(l) for l in loci], "withheld": [],
            "signature": {"fields": ["name", "date"]}}


def main(argv):
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        build.write_spec(argv[1], make_spec(argv[0]))
    except Fail as ex:
        print(f"FAIL: {ex}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
