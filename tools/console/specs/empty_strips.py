"""Spec builder, instance (i): the empty-strips sign-off (Chris).

Usage: python tools/console/specs/empty_strips.py <strips-dir> <out-spec.json>

<strips-dir> holds strips.json (written by tools/signing_strips.py) and the PNGs it lists. The
questions follow docs/handoff/SIGNOFF_empty_strips.md; the architect's quoted wording is read from it.
Sections: h1 (p.896 chapter opening), foot (each foot page, then the two joint rows), abst (897, 898).
Image ids are the PNG file stems. Fails loud on a missing file, a sha256 that differs from strips.json,
a missing run strip, or a missing form.
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import build  # noqa: E402
from build import Fail  # noqa: E402

FORM = build.REPO / "docs" / "handoff" / "SIGNOFF_empty_strips.md"
YN = ["yes", "no"]
INKS = ["rule", "justified-text edge", "footnote text", "catchword", "signature mark", "other page furniture"]
HYPOTHESIS = ["refuted: the rule itself ends above the foot", "confirmed: text edge or footnote ink", "other"]
STOPS = ["yes, on every page", "no: it runs to the bottom and is faint near it"]
ABST_PAGES = (897, 898)


def field(fid, kind, label, options=None, required=True, **extra):
    f = {"id": fid, "kind": kind, "label": label, "required": required, "proposed": None, **extra}
    if options:
        f["options"] = options
    return f


def quoted_block(text):
    """The first '>' block of the form, joined."""
    lines = [l[1:].strip() for l in text.splitlines() if l.startswith(">")]
    if not lines:
        raise Fail(f"{FORM}: no quoted block (the architect's wording)")
    return " ".join(lines)


def image_entries(strips_dir, data):
    out = []
    for s in data["strips"]:
        p = Path(strips_dir) / s["file"]
        if not p.is_file():
            raise Fail(f"strip file missing: {p}")
        if build.sha256_file(p) != s["sha256"]:
            raise Fail(f"{p}: sha256 differs from strips.json")
        stem = p.stem
        tag = "native crop" if s.get("native") else "run frame"
        out.append({"id": stem, "path": str(p.resolve()), "sha256": s["sha256"],
                    "caption": f"p.{s['page']} {s['kind']}, {tag}",
                    "frame": {"rows": s["rows"], "cols": s["cols"], "frame_wh": s["frame_wh"], "k": s["k"]},
                    "overlay": s.get("overlay", [])})
    if len({i["id"] for i in out}) != len(out):
        raise Fail("strips.json: repeated file name")
    return out


def pair(data, page, kind):
    """(run id, [run id, native id if present])."""
    run = [s for s in data["strips"] if s["page"] == page and s["kind"] == kind and not s.get("native")]
    if len(run) != 1:
        raise Fail(f"p.{page} {kind}: expected one run strip, found {len(run)}")
    nat = [s for s in data["strips"] if s["page"] == page and s["kind"] == kind and s.get("native")]
    stem = lambda s: Path(s["file"]).stem  # noqa: E731
    return stem(run[0]), [stem(run[0])] + [stem(n) for n in nat[:1]]


def h1_section(data, form_text):
    run, ids = pair(data, 896, "gutter-full")
    rows = [
        {"id": "h1.head", "label": "Chapter head", "context": [], "image_ids": [], "fields": [
            field("v", "radio", "Is there a chapter head spanning both columns at the top of the body?", YN)]},
        {"id": "h1.rule_start", "label": "Where the rule starts", "context": [], "image_ids": [], "fields": [
            field("row", "pick-row", "Row where the column rule starts", image_id=run)]},
        {"id": "h1.unruled", "label": "Two-column text with no rule", "context": [], "image_ids": [], "fields": [
            field("v", "radio", "Between the head and the rule's start, is there two-column text with no rule?", YN),
            field("from", "pick-row", "Rows from", required=False, image_id=run),
            field("to", "pick-row", "to", required=False, image_id=run)]},
        {"id": "h1.verdict", "label": "H1", "context": [], "image_ids": [], "fields": [
            field("v", "radio", "H1 (geometry reading: no rule above the chapter opening)",
                  ["confirmed", "refuted"]),
            field("what", "text", "If refuted, what occupies the rows above the rule's start?", required=False)]},
    ]
    return {"id": "h1", "title": "H1: p. 896 is a chapter opening", "text": quoted_block(form_text),
            "image_ids": ids, "rows": rows}


def foot_section(data):
    pages = sorted({s["page"] for s in data["strips"] if s["kind"] == "foot"})
    if not pages:
        raise Fail("strips.json: no foot strips")
    rows = []
    for p in pages:
        run, ids = pair(data, p, "foot")
        y0, y1 = data["pages"][str(p)]["last_strip"]
        rows.append({"id": f"foot.{p}", "label": f"p. {p}", "context": [], "image_ids": ids, "fields": [
            field("rule_end", "pick-row", "Row where the rule ends", image_id=run),
            field("to_foot", "radio", "Does it run to the text foot?", YN),
            field("faint", "radio", "Faint near the foot?", YN),
            field("inks", "checkbox", f"What inks the gutter in the last strip (rows {y0}–{y1})?", INKS),
            field("other", "text", "Other (say what)", required=False)]})
    rows.append({"id": "foot.hypothesis", "label": "The locked hypothesis", "context": [], "image_ids": [], "fields": [
        field("v", "radio", "The locked hypothesis", HYPOTHESIS),
        field("other", "text", "If other, what", required=False)]})
    rows.append({"id": "foot.stops", "label": "Does the rule stop above the foot on every page?", "context": [],
                 "image_ids": [], "fields": [field("v", "radio", "Does the rule stop above the foot on every page?", STOPS)]})
    text = ("Two readings are on file. Your reading decides.\n\n"
            "The architect's locked hypothesis: the peaks are \"the inked edge of justified text (left edge of the "
            "right column's stems) or footnote text inside the ±300 px window after the rule ends, not a faint rule\".")
    return {"id": "foot", "title": "The last strip: what inks the gutter?", "text": text, "image_ids": [], "rows": rows}


def abst_section(data):
    rows = []
    for p in ABST_PAGES:
        _, ids = pair(data, p, "gutter-full")
        rows.append({"id": f"abst.{p}", "label": f"p. {p}", "context": [], "image_ids": ids, "fields": [
            field("present", "radio", "Rule present?", YN), field("single", "radio", "Single?", YN),
            field("note", "text", "Note", required=False)]})
    return {"id": "abst", "title": "Run-2 abstentions", "text": "", "image_ids": [], "rows": rows}


def instruction(data):
    s0 = data["strips"][0]
    hs = [s["line_h"] for s in data["strips"] if s.get("line_h") is not None]  # native crops: not measured
    lh = f"{min(hs)}–{max(hs)}" if hs else "not recorded"
    return ("Sign from the pixels. The overlay is the run's result, drawn over raw page pixels; hide it to see "
            "the page alone. No threshold is applied to anything shown here.\n\n"
            f"Frame: {s0['frame_wh'][0]} x {s0['frame_wh'][1]} px. Line height by strip: {lh} px.")


def make_spec(strips_dir):
    sj = Path(strips_dir) / "strips.json"
    if not sj.is_file() or not FORM.is_file():
        raise Fail(f"missing {sj if not sj.is_file() else FORM}")
    data = json.loads(sj.read_text(encoding="utf-8"))
    images = image_entries(strips_dir, data)
    sources = [{"path": str(sj.resolve()), "sha256": build.sha256_file(sj)}, {"path": str(FORM), "sha256": build.sha256_file(FORM)}]
    sources += [{"path": i["path"], "sha256": i["sha256"]} for i in images]
    return {"format": build.SPEC_FORMAT, "kind": "empty-strips",
            "title": "Sign-off: empty strips and the run-2 abstentions", "signer": "Chris",
            "instruction": instruction(data), "sources": sources,
            "run_header": data["header"].get("run_header"), "images": images,
            "sections": [h1_section(data, FORM.read_text(encoding="utf-8")), foot_section(data), abst_section(data)],
            "withheld": [], "signature": {"fields": ["name", "date"]}}


def main(argv):
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        build.write_spec(argv[1], make_spec(argv[0]))
    except (Fail, KeyError) as ex:
        print(f"FAIL: {ex!r}" if isinstance(ex, KeyError) else f"FAIL: {ex}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
