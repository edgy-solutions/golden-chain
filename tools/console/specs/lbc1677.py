"""Spec builder: Chris confirms or corrects the LBC 1677 margin notes (ruling on report 18, item 2).

Usage: python tools/console/specs/lbc1677.py <photos-dir> <out-spec.json>

Photos are named lbc1677_<group>_<n>.<jpg|jpeg|png>, group in title, ch07, ch26, ch27, ch28, ch29, n = 1, 2, ...
contiguous. A JPEG is converted to PNG deterministically (PIL, no resize, no metadata) next to the spec; the image
entry records the source and converted sha256. The 15 rows are in lbc1677_rows.json; each proposed string must be
in data/lbc-1689.ttl's gc:asPrinted of every Argument the row lists.
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import build  # noqa: E402
from build import Fail  # noqa: E402

ROWS = HERE / "lbc1677_rows.json"
DATA = HERE.parents[2] / "data" / "lbc-1689.ttl"
GROUPS = ("title", "ch07", "ch26", "ch27", "ch28", "ch29")
NAME = re.compile(r"^lbc1677_(title|ch07|ch26|ch27|ch28|ch29)_(\d+)\.(jpg|jpeg|png)$")
PLAIN_WITNESS = ('The photograph should show the title page of the book the notes were photographed from. Choose "yes" if it is '
                 'the 1677 first printing in the facsimile edition (2000), "no" if it is another edition; if you are not sure, '
                 'choose "other, as written" and type what the title page says.')
PLAIN_WITNESS_NOTE = ("Optional: anything on the title page that identifies the edition, such as a year or the facsimile "
                      "publisher. Leave it empty if there is nothing to add.")
PLAIN_PROPOSAL = ('The text on a grey background is a proposed reading of this margin note, made by a model from photographs, '
                  'so check it letter by letter, stops and spacing included. Choose "confirm" if the page prints exactly that, '
                  'or "correct" and type exactly what is printed.')
PLAIN_UNLISTED = ('Look in the margins of this chapter for any note letter or citation that has no row above. Choose "yes" if you '
                  'find one and type it in the note, "no" if every note is listed; if you cannot tell, choose "other, as written" '
                  'and say why.')
PLAIN_UNLISTED_NOTE = "Optional: type any unlisted note exactly as printed, with its letter. Leave it empty if there is none."
HELP = [{"q": "Why am I asked to read these?",
         "a": "These notes were read by the architect, a hosted model, from your photographs. A model reading is not a signed one "
              "(ruling on report 18). This sitting makes each note yours, confirmed or corrected. Rule 11: if a question is "
              "unclear, ask, and you will be answered from this page's text only."}]


def find_photos(photos_dir):
    d = Path(photos_dir)
    if not d.is_dir():
        raise Fail(f"photos dir missing: {d}")
    found = {g: {} for g in GROUPS}
    for p in sorted(d.iterdir()):
        if not p.is_file():
            continue
        m = NAME.match(p.name)
        if not m:
            raise Fail(f"photo name {p.name!r} does not match lbc1677_<group>_<n>.<jpg|jpeg|png>")
        n = int(m.group(2))
        if n in found[m.group(1)]:
            raise Fail(f"photo {p.name!r}: group {m.group(1)} n={n} appears twice")
        found[m.group(1)][n] = p
    out = {}
    for g in GROUPS:
        if not found[g]:
            raise Fail(f"group {g} has no photo")
        ns = sorted(found[g])
        if ns != list(range(1, len(ns) + 1)):
            raise Fail(f"group {g}: n is not contiguous from 1 ({ns})")
        out[g] = [found[g][n] for n in ns]
    return out


def to_png(src, out_dir):
    """Deterministic JPEG -> PNG: pixels as decoded, no resize, no metadata, fixed compression."""
    from PIL import Image
    dst = Path(out_dir) / (src.stem + ".png")
    with Image.open(src) as im:
        im.load()
        clean = Image.frombytes(im.mode, im.size, im.tobytes())
        clean.save(dst, format="PNG", compress_level=6, optimize=False)
    return dst


def image_entry(gid, n, p, out_dir):
    src_sha = build.sha256_file(p)
    e = {"id": f"{gid}-{n}", "caption": p.name, "overlay": []}
    if p.suffix.lower() == ".png":
        e.update(path=str(p.resolve()), sha256=src_sha)
    else:
        q = to_png(p, out_dir)
        e.update(path=str(q.resolve()), sha256=build.sha256_file(q), source_sha256=src_sha, source_name=p.name)
    return e


def check_against_data(rows, data_path):
    from rdflib import Graph, Namespace, URIRef
    g = Graph()
    g.parse(data=Path(data_path).read_text(encoding="utf-8"), format="turtle")
    base = "https://w3id.org/golden-chain/"
    asp = Namespace(base + "ontology#").asPrinted
    for r in rows:
        for a in r["arguments"]:
            vals = [str(o) for o in g.objects(URIRef(f"{base}argument/{a}"), asp)]
            if not any(r["proposed"] in v for v in vals):
                raise Fail(f"row {r['id']}: proposed {r['proposed']!r} not in asPrinted of argument/{a} ({vals})")


def field(fid, kind, label, plain, options=None, proposed=None, required=True):
    f = {"id": fid, "kind": kind, "label": label, "required": required, "proposed": proposed, "plain": plain}
    if options:
        f["options"] = options
    return f


def note_row(r):
    used = "Used by: " + (", ".join(r["arguments"]) if r["arguments"] else "Stored for phase 2, not in the data")
    return {"id": r["id"], "label": f"{r['locator']}, note {r['note']}", "context": [used, "Read by: " + r["read_by"]],
            "image_ids": [], "fields": [field("v", "radio", "As printed", PLAIN_PROPOSAL, ["confirm", "correct"], r["proposed"])]}


def unlisted_row(g):
    return {"id": f"{g}.unlisted", "label": "Any margin note on these pages with no row above?", "context": [],
            "image_ids": [], "fields": [
                field("v", "radio", "Any unlisted note?", PLAIN_UNLISTED, ["yes", "no"]),
                field("note", "text", "The unlisted note, as printed (optional)", PLAIN_UNLISTED_NOTE, required=False)]}


def make_spec(photos_dir, out_dir, rows_path=ROWS, data_path=DATA):
    meta = json.loads(Path(rows_path).read_text(encoding="utf-8"))
    rows = meta["rows"]
    check_against_data(rows, data_path)
    photos = find_photos(photos_dir)
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    images = {g: [image_entry(g, n, p, out_dir) for n, p in enumerate(ps, 1)] for g, ps in photos.items()}
    sections = [{"id": "witness", "title": "Which book", "text": "", "image_ids": [], "rows": [
        {"id": "witness", "label": "The title page", "context": [], "image_ids": [i["id"] for i in images["title"]], "fields": [
            field("v", "radio", "Is this the title page of the 1677 first printing, in the facsimile edition (2000)?",
                  PLAIN_WITNESS, ["yes", "no"]),
            field("note", "text", "What the title page says (optional)", PLAIN_WITNESS_NOTE, required=False)]}]}]
    for g in GROUPS[1:]:
        if g not in meta["chapters"]:
            raise Fail(f"rows.json has no chapter {g}")
        ids = [i["id"] for i in images[g]]
        sections.append({"id": g, "title": meta["chapters"][g], "text": "", "image_ids": ids,
                         "rows": [note_row(r) for r in rows if r["chapter"] == g] + [unlisted_row(g)]})
    allimg = [i for g in GROUPS for i in images[g]]
    return {"format": build.SPEC_FORMAT, "kind": "lbc1677",
            "title": "Reading form: LBC 1677 margin notes as printed", "signer": "Chris",
            "instruction": "Each grey string is a model's reading of a margin note in your photographs. Confirm it, or correct it "
                           "to exactly what is printed; a corrected row is recorded as a signed reading.",
            "sources": [{"path": str(Path(rows_path).resolve()), "sha256": build.sha256_file(rows_path)},
                        {"path": str(Path(data_path).resolve()), "sha256": build.sha256_file(data_path)}]
            + [{"path": i["path"], "sha256": i["sha256"]} for i in allimg],
            "run_header": None, "images": allimg, "sections": sections, "withheld": [],
            "help": HELP, "signature": {"fields": ["name", "date"]}}


def main(argv):
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        build.write_spec(argv[1], make_spec(argv[0], Path(argv[1]).resolve().parent))
    except Fail as ex:
        print(f"FAIL: {ex}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
