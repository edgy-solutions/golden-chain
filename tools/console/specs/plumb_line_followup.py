"""Spec builder, instance (iv): the plumb-line follow-up sitting (kind plumb-line-followup).

Usage: python tools/console/specs/plumb_line_followup.py <content.json> <loci.ttl> <image-dir> <out-spec.json>

The content file (format golden-chain-followup-content/1, e.g. docs/loci/plumb-line-followup-1.json) names
the sections and rows; the loci and Position labels come from loci.ttl, the images from image-dir.
Row types: locus (tier, clarity), position (modality, unchurches), radio, proposal, text, flag.
A section with "locus" takes its title from the ttl, and every Position answering that Locus must have a
position row. Fails loud on an unknown row type, a Position that does not answer its Locus, a missing
Position row, a wrong content format.
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import build  # noqa: E402
import plumb_line  # noqa: E402
from build import Fail  # noqa: E402
from plumb_line import CLARITIES, TIERS, adr_help, position_fields, sel  # noqa: E402

CONTENT_FORMAT = "golden-chain-followup-content/1"


def pos_label(loci, ref):
    """The rdfs:label of the Position '<locus>/<pos>'; Fail if it is not one."""
    loc, _, pos = ref.partition("/")
    for l in loci:
        if l["slug"] == loc:
            for p in l["positions"]:
                if p["slug"] == pos:
                    return p["label"]
    raise Fail(f"{ref!r} is not a Position in the loci file")


def common(row):
    return {"context": list(row.get("context", [])), "image_ids": list(row.get("image_ids", []))}


def make_row(sec, locus, row, loci):
    t = row.get("type")
    if t == "locus":
        if locus is None:
            raise Fail(f"section {sec['id']}: a locus row needs the section's 'locus'")
        return {"id": f"{locus['slug']}.locus", "label": f"{locus['notation']} {locus['label']}", **common(row),
                "fields": [sel("tier", "Tier", TIERS), sel("clarity", "Clarity", CLARITIES)]}
    if t == "position":
        if locus is None:
            raise Fail(f"section {sec['id']}: a position row needs the section's 'locus'")
        by = {p["slug"]: p for p in locus["positions"]}
        if row["position"] not in by:
            raise Fail(f"{locus['slug']}/{row['position']}: that Position does not answer the Locus")
        return {"id": f"{locus['slug']}.{row['position']}", "label": by[row["position"]]["label"], **common(row),
                "fields": position_fields()}
    rid = f"{sec['id']}.{row.get('id')}"
    if t == "radio":
        return {"id": rid, "label": row["label"], **common(row),
                "fields": [{"id": "v", "kind": "radio", "label": row["label"], "options": row["options"],
                            "required": row.get("required", True), "proposed": None}]}
    if t == "proposal":
        return {"id": rid, "label": row["label"], **common(row),
                "fields": [{"id": "v", "kind": "radio", "label": "As proposed", "options": ["confirm", "correct"],
                            "required": True, "proposed": row["proposed"]}]}
    if t == "text":
        return {"id": rid, "label": row["label"], **common(row),
                "fields": [{"id": "v", "kind": "text", "label": row["label"],
                            "required": row.get("required", True)}]}
    if t == "flag":
        label = pos_label(loci, row["position"]) if row.get("position") else row["label"]
        return {"id": f"unchurches.{row['id']}", "label": label, **common(row),
                "fields": [{"id": "unchurches", "kind": "radio", "label": "Unchurches",
                            "options": ["confirm", "withdraw"], "required": True, "proposed": None}]}
    raise Fail(f"section {sec['id']}: unknown row type {t!r}")


def make_spec(content_path, ttl, image_dir):
    content_path, ttl, image_dir = Path(content_path), Path(ttl), Path(image_dir)
    content = json.loads(content_path.read_text(encoding="utf-8"))
    if content.get("format") != CONTENT_FORMAT:
        raise Fail(f"content format {content.get('format')!r}, expected {CONTENT_FORMAT}")
    loci = plumb_line.read_loci(ttl)
    by_slug = {l["slug"]: l for l in loci}
    sections = []
    for sec in content["sections"]:
        locus = None
        if sec.get("locus"):
            locus = by_slug.get(sec["locus"])
            if locus is None:
                raise Fail(f"section {sec['id']}: {sec['locus']!r} is not a non-deprecated Locus with Positions")
            title = f"{locus['notation']} {locus['slug']}: {locus['question']}"
        else:
            title = sec["title"]
        rows = [make_row(sec, locus, r, loci) for r in sec["rows"]]
        if locus is not None and any(r["type"] == "locus" for r in sec["rows"]):
            have = {r["position"] for r in sec["rows"] if r["type"] == "position"}
            missing = [p["slug"] for p in locus["positions"] if p["slug"] not in have]
            if missing:
                raise Fail(f"{locus['slug']}: positions without a row: {missing}")
        sections.append({"id": sec["id"], "title": title, "text": sec.get("text", ""),
                         "image_ids": list(sec.get("image_ids", [])), "rows": rows})
    images = []
    for im in content["images"]:
        p = (image_dir / im["file"]).resolve()
        if not p.is_file():
            raise Fail(f"image {im['id']}: missing file {p}")
        images.append({"id": im["id"], "path": str(p), "sha256": build.sha256_file(p),
                       "caption": im.get("caption", "")})
    return {"format": build.SPEC_FORMAT, "kind": "plumb-line-followup", "title": content["title"],
            "signer": "Chris", "instruction": content["instruction"],
            "sources": [{"path": str(p.resolve()), "sha256": build.sha256_file(p)}
                        for p in (content_path, ttl, plumb_line.ADR3)],
            "run_header": None, "images": images, "sections": sections, "withheld": [],
            "help": plumb_line.HELP + adr_help(), "signature": {"fields": ["name", "date"]}}


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
