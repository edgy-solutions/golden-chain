"""Spec builder: Chris confirms or corrects the LBC 1677 margin notes (ruling on report 18, item 2).

Usage: python tools/console/specs/lbc1677.py <photos-dir> <out-spec.json>

Photos are named lbc1677_<group>_<n>.<jpg|jpeg|png>, group in title, ch01, ch07, ch26, ch27, ch28, ch29, n = 1, 2, ...
contiguous. The photos dir also holds one public-domain scan, wcf1647_leaf14.<jpg|jpeg|png> (IA humbleadviceofas00west,
leaf 14), shown in a last section as one page number to confirm or correct. A JPEG is converted to PNG deterministically (PIL, no resize, no metadata) next to the spec; the image
entry records the source and converted sha256. The 15 note rows are in lbc1677_rows.json; each proposed string must be
in data/lbc-1689.ttl's gc:asPrinted of every Argument the row lists.
Chapter 7 also carries two "reading" rows (7.2.text, 7.3.text; the "readings" key of the rows file): the build agent's reading of LBC 7.2 and 7.3
from Chris's photographs, each a words field and a page field to confirm or correct (ruling on report 23). Each proposed string must occur
verbatim in docs/handoff/REPORT_phase1_23.md; none is in the data.
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
REPORT23 = HERE.parents[2] / "docs" / "handoff" / "REPORT_phase1_23.md"
GROUPS = ("title", "ch01", "ch07", "ch26", "ch27", "ch28", "ch29")
NAME = re.compile(r"^lbc1677_(title|ch01|ch07|ch26|ch27|ch28|ch29)_(\d+)\.(jpg|jpeg|png)$")
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
PLAIN_FOLIO = ('The text on a grey background is a proposed reading of the page number at the top of this page, made by a model '
               'from the scan. Choose "confirm" if it matches the page exactly, brackets included, or "correct" if it does '
               'not, and type exactly what is printed.')
PLAIN_LOC_PAGE = ('Type the page number printed on the page where paragraph 6 of chapter 1 begins, exactly as printed. If the '
                  'paragraph runs onto the next page, type both, for example "12-13"; if no number is printed, type the '
                  'signature (the letters and number at the foot), or "none".')
PLAIN_LOC_NOTES = ('Type each margin note that belongs to paragraph 6, with its letter, exactly as printed, one after another. '
                   'If there are none, type "none".')
PLAIN_READ = ('The text on a grey background is the build agent\'s reading of these words from your photograph, with the long s written as "s". '
              'Choose "confirm" if the page prints exactly these words in this order, or "correct" and type exactly what is printed.')
PLAIN_READ_PAGE = ('The text on a grey background is the page number the build agent read or inferred for these words. '
                   'Choose "confirm" if it is the number printed on the page where they stand, or "correct" and type what is printed.')
WCF_NAME = re.compile(r"^wcf1647_leaf14\.(jpg|jpeg|png)$")
WCF_ID = "wcf1647-leaf14-1"
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
        if WCF_NAME.match(p.name):
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


def find_wcf_leaf(photos_dir):
    hits = [p for p in sorted(Path(photos_dir).iterdir()) if p.is_file() and WCF_NAME.match(p.name)]
    if not hits:
        raise Fail("wcf1647_leaf14 image missing: put the IA humbleadviceofas00west leaf 14 page image in the photos dir "
                   "as wcf1647_leaf14.<jpg|jpeg|png>")
    if len(hits) > 1:
        raise Fail(f"wcf1647_leaf14 appears more than once: {[p.name for p in hits]}")
    return hits[0]


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


def check_readings(readings, rows, report_path=REPORT23):
    text = Path(report_path).read_text(encoding="utf-8")
    seen = {r["id"] for r in rows}
    for r in readings:
        if r["chapter"] not in GROUPS:
            raise Fail(f"reading {r['id']}: chapter {r['chapter']!r} is not in {GROUPS}")
        if r["id"] in seen:
            raise Fail(f"reading {r['id']}: id is not unique or clashes with a note row")
        seen.add(r["id"])
        if r["proposed"] not in text:
            raise Fail(f"reading {r['id']}: proposed {r['proposed']!r} not found verbatim in {Path(report_path).name}")


def field(fid, kind, label, plain, options=None, proposed=None, required=True):
    f = {"id": fid, "kind": kind, "label": label, "required": required, "proposed": proposed, "plain": plain}
    if options:
        f["options"] = options
    return f


def note_row(r):
    used = "Used by: " + (", ".join(r["arguments"]) if r["arguments"] else "Stored for phase 2, not in the data")
    return {"id": r["id"], "label": f"{r['locator']}, note {r['note']}", "context": [used, "Read by: " + r["read_by"]],
            "image_ids": [], "fields": [field("v", "radio", "As printed", PLAIN_PROPOSAL, ["confirm", "correct"], r["proposed"])]}


def reading_row(r):
    ctx = ["Read by: build agent, from your photograph, 2026-11-22 (a proposal, not signed)",
           "Used by: report 23, dispatch 23a question Q-c; not in the data"]
    if r["page_note"]:
        ctx.append("Page: " + r["page_note"])
    return {"id": r["id"], "label": f"{r['id'][:3]} as printed, page {r['page']}: the words quoted in report 23", "context": ctx,
            "image_ids": [], "fields": [
                field("text", "radio", "The words, as printed", PLAIN_READ, ["confirm", "correct"], r["proposed"]),
                field("page", "radio", "The page number", PLAIN_READ_PAGE, ["confirm", "correct"], r["page"])]}


def unlisted_row(g):
    return {"id": f"{g}.unlisted", "label": "Any margin note on these pages with no row above?", "context": [],
            "image_ids": [], "fields": [
                field("v", "radio", "Any unlisted note?", PLAIN_UNLISTED, ["yes", "no"]),
                field("note", "text", "The unlisted note, as printed (optional)", PLAIN_UNLISTED_NOTE, required=False)]}


def locate_row():
    return {"id": "1.6.locate", "label": "1.6: where it is printed, and its margin notes",
            "context": ["Used by: the phase-2 warrant locus (row 10b), not yet in the data",
                        "Read by: nobody yet; the build agent did not view this page (ruling on report 22: a reading for Chris)"],
            "image_ids": [], "fields": [
                field("page", "text", "Page number(s) as printed", PLAIN_LOC_PAGE),
                field("notes", "text", "Margin notes beside paragraph 6, as printed", PLAIN_LOC_NOTES)]}


def folio_row():
    return {"id": "wcf1647.leaf14.folio", "label": "The page number printed at the top of this page",
            "context": ["Source: IA humbleadviceofas00west, leaf 14, a public-domain scan",
                        'Read by: build agent, from the scan, as "[6]"; "[4]" would be expected from the leaf before it'],
            "image_ids": [], "fields": [field("v", "radio", "As printed", PLAIN_FOLIO, ["confirm", "correct"], "[6]")]}


def make_spec(photos_dir, out_dir, rows_path=ROWS, data_path=DATA):
    meta = json.loads(Path(rows_path).read_text(encoding="utf-8"))
    rows = meta["rows"]
    check_against_data(rows, data_path)
    readings = meta.get("readings", [])
    check_readings(readings, rows)
    photos = find_photos(photos_dir)
    wcf = find_wcf_leaf(photos_dir)
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
        grows = [locate_row()] if g == "ch01" else [note_row(r) for r in rows if r["chapter"] == g] + [reading_row(r) for r in readings if r["chapter"] == g] + [unlisted_row(g)]
        sections.append({"id": g, "title": meta["chapters"][g], "text": "", "image_ids": ids, "rows": grows})
    wimg = image_entry("wcf1647-leaf14", 1, wcf, out_dir)
    assert wimg["id"] == WCF_ID
    sections.append({"id": "wcf1647", "title": "WCF 1647 (Edinburgh: Evan Tyler), leaf 14: the page number", "text": "",
                     "image_ids": [WCF_ID], "rows": [folio_row()]})
    allimg = [i for g in GROUPS for i in images[g]] + [wimg]
    return {"format": build.SPEC_FORMAT, "kind": "lbc1677",
            "title": "Reading form: LBC 1677 margin notes as printed", "signer": "Chris",
            "instruction": "Each grey string is a model's reading of a margin note in your photographs. Confirm it, or correct it "
                           "to exactly what is printed; a corrected row is recorded as a signed reading. "
                           "The last section is one page number in a scan of the 1647 Westminster Confession.",
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
