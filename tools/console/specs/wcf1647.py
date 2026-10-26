"""Spec builder, instance (iii): the WCF 1647 proof-note reading (Chris).

Usage: python tools/console/specs/wcf1647.py <proposals.json> <out-spec.json>

proposals.json (written by the build agent from the page images): witness, instruction_extra, images
[{id, path, caption, frame?}], chapters [{id, title, image_ids?, rows [{id, clause, schaff, image_ids,
doubts?, proposed {letters, as_printed, page?}}]}], lettering [question, ...]. The builder hashes each
image file. A chapter's image_ids (the page heads) go on its leaves row; each doubt is shown as context.

Each proposed string is a radio field with options confirm/correct and `proposed` set: the page shows the
string in monospace and a text box enabled only on correct. Its value is {"action", "text", "proposed"}.
A corrected row is a signed reading, not a pixel signature (ADR-0006 item 5).
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import build  # noqa: E402
from build import Fail  # noqa: E402

LABELS = {"letters": "Letter(s)", "as_printed": "As printed (1647)", "page": "Page"}
RULES = ("Keep the original spelling, punctuation and spacing, including \"with\" and \"&\". Write long s as s.\n\n"
         "If the texts fall under more than one letter, give one row per letter (the Argument then splits). "
         "If the 1647 note prints texts that Schaff does not, or omits some, write what is printed and mark it.")
TAIL = ("The strings beside each crop were proposed by the build agent from the page images. Confirm or "
        "correct each from the pixels; a corrected row is recorded as a signed reading.")


def yn(fid, label, required=True):
    return {"id": fid, "kind": "radio", "label": label, "options": ["yes", "no"], "required": required, "proposed": None}


def leaves_row(ch):
    return {"id": f"{ch['id']}.leaves", "label": f"{ch['title']}: are the leaves right?", "context": [],
            "image_ids": ch.get("image_ids", []), "fields": [
                {"id": "v", "kind": "radio", "label": "Leaves", "options": ["confirmed", "differs"],
                 "required": True, "proposed": None},
                {"id": "note", "kind": "text", "label": "If it differs, say how", "required": False, "proposed": None}]}


def argument_row(r):
    p = r.get("proposed") or {}
    for k in ("letters", "as_printed"):
        if k not in p:
            raise Fail(f"row {r['id']}: proposed has no {k}")
    fields = [{"id": k, "kind": "radio", "label": LABELS[k], "options": ["confirm", "correct"],
               "required": True, "proposed": p[k]} for k in ("letters", "as_printed", "page") if k in p]
    context = ([f"Schaff (A): {r['schaff']}"] if r.get("schaff") else []) + [f"Doubt: {d}" for d in r.get("doubts", [])]
    return {"id": r["id"], "label": r["clause"], "context": context,
            "image_ids": r.get("image_ids", []), "fields": fields}


def image_entry(im):
    p = Path(im["path"])
    if not p.is_file():
        raise Fail(f"image missing: {p}")
    e = {"id": im["id"], "path": str(p.resolve()), "sha256": build.sha256_file(p),
         "caption": im.get("caption", ""), "overlay": im.get("overlay", [])}
    if im.get("frame"):
        e["frame"] = im["frame"]
    return e


def make_spec(proposals):
    prop = json.loads(Path(proposals).read_text(encoding="utf-8"))
    for k in ("witness", "images", "chapters", "lettering"):
        build.need(prop, k, "proposals")
    images = [image_entry(im) for im in prop["images"]]
    sections = [{"id": ch["id"], "title": ch["title"], "text": "", "image_ids": [],
                 "rows": [leaves_row(ch)] + [argument_row(r) for r in ch["rows"]]} for ch in prop["chapters"]]
    lettering = [{"id": f"lettering.{n}", "label": q, "context": [], "image_ids": [], "fields": [
        yn("v", "Answer"), {"id": "note", "kind": "text", "label": "Note", "required": False, "proposed": None}]}
        for n, q in enumerate(prop["lettering"], 1)]
    sections.append({"id": "lettering", "title": "Lettering", "text": "", "image_ids": [], "rows": lettering})
    instruction = "\n\n".join(x for x in (f"Witness: {prop['witness']}", RULES, prop.get("instruction_extra", ""), TAIL) if x)
    return {"format": build.SPEC_FORMAT, "kind": "wcf1647",
            "title": "Reading form: WCF 1647 proof notes as printed", "signer": "Chris",
            "instruction": instruction,
            "sources": [{"path": str(Path(proposals).resolve()), "sha256": build.sha256_file(proposals)}]
            + [{"path": i["path"], "sha256": i["sha256"]} for i in images],
            "run_header": None, "images": images, "sections": sections, "withheld": [],
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
