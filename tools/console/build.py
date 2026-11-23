"""Signing console builder: spec.json -> one self-contained HTML page + manifest (ADR-0006).

Usage: python tools/console/build.py <spec.json> [--out-dir DIR]
       out-dir defaults to ~/.golden-chain/console/<kind>/

Writes console_<kind>_<build16>.html, manifest_<kind>_<build16>.json and a copy of the spec,
spec_<kind>_<build16>.json (canonical bytes), so that ingest.py finds it next to the manifest.

Digests (ADR-0006 item 6, truth-set form 8): every JSON is canon(obj) = json.dumps(obj,
ensure_ascii=False, sort_keys=True, indent=1) in UTF-8, no trailing newline, LF only.
  spec_sha256 = sha256(canon(hashed spec))   (R5: the spec with every path replaced by name, run_header removed)
  code_sha256 = sha256(bytes(build.py) + bytes(template.html))
  build_hash  = sha256(canon({"spec_sha256", "code_sha256", "images": {id: sha256(png bytes)}}))
  build16     = build_hash[:16]
Files get content-addressed names: staged as <name>.tmp, re-read and verified, then renamed. A write to
an existing name with different bytes is refused; the same bytes are a no-op.

The page is rendered here (images inline as data URIs, controls, sha256 beside each image); the
template supplies the style and the script that wires the controls, export and draft.
Console template v3 (TEMPLATE_VERSION): fit-to-window zoom, a help panel, "other, as written" on every choice;
v3 adds silence is complete (a select field with "empty_means": "silent" may be left empty and still counts as
answered; the status line says how many rows were left empty) and the plumb-line-followup kind.
v4: an empty select with empty_means "unanswered" is complete and is unanswered: it changes nothing in the
merge; only the option `silent`, chosen, is silence (ADR-0006 R1 §6). "silent" stays for legacy v3 specs.
v5: an optional spec "keyboard" block for one-key signing.
v6 (ruling on report 18, 2026-11-15): every field carries "plain", one or two sentences in plain words saying what is asked, what each option means and what to choose when none fits; build fails without it. Consoles built before v6 are not rebuilt; they ingest with --code-at at their build commit.
v7 (ADR-0006 R5, ruling on report 19, A-7): the hash names images by id, name and sha256; paths and the run header go in the manifest's local block (manifest format /2), never in the hashed spec, the spec copy or the page.
Region questions (2026-11-15): a row asking what a region is must show context (a "region_question" block):
the crop must carry max(region size, CONTEXT_MIN_PX) of surroundings on each side, unless it reaches the source edge.
Clear edges (ruling on report 17, Q-1, 2026-11-15): an image may require that no ink touch
given edges (mode-midpoint threshold)
Fails loud (Fail) on a missing path, a sha256 mismatch, a repeated id, an unknown field kind,
options missing, or a pick-row naming an unknown image.
"""

import argparse
import base64
import datetime
import hashlib
import html
import json
import os
import re
import struct
import sys
from pathlib import Path, PurePath

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from column_rule import REPO, Fail, clean_run, git_state  # noqa: E402

SPEC_FORMAT = "golden-chain-console-spec/1"
TEMPLATE_VERSION = 7
OTHER = "other, as written"
CONTEXT_MIN_PX = 300
COMMON_HELP = [
    {"q": "What do verdict, abstain and fault mean?",
     "a": "verdict: you are answering the row. abstain: you cannot tell from the image. fault: the image or "
          "the question is wrong (wrong page, cut off, a question that does not fit). An abstain or fault "
          "row records no answers, only your note."},
    {"q": "How do I answer when none of the options fits?",
     "a": "Choose \"other, as written\" and write what you see in the box beside it. That is a recorded "
          "answer, not a wrong one. Every choice on this form has it."},
    {"q": "How do I pick a row on an image?",
     "a": "Press pick, then click the image at that height. The row is recorded and drawn as a magenta line. "
          "clear undoes it."},
    {"q": "The image is cut off or too small.",
     "a": "Use zoom: fit (the default) fits the image to the window; 100% and 200% show more detail, and the "
          "box scrolls. show overlay hides the drawn marks to show the bare page."},
    {"q": "Can I ask someone mid-sitting?",
     "a": "Everything the form needs is on this page. If something is still unclear, ask in words; do not "
          "paste images from this console anywhere. If a question cannot be answered as asked, mark the row "
          "fault and say why in the note."},
]
MANIFEST_FORMAT = "golden-chain-console-manifest/2"
KINDS = ("empty-strips", "plumb-line", "plumb-line-followup", "wcf1647", "lbc1677", "q11-crops", "truthset-italic", "truthset-italic-v3", "truthset-italic-v4", "truthset-italic-v5", "region-reask", "congregation", "statements")
FIELD_KINDS = ("radio", "checkbox", "select", "text", "pick-row")
OPTION_KINDS = ("radio", "checkbox", "select")
SIGNATURE_FIELDS = ("name", "date")
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def canon(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=1).encode("utf-8")


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(path):
    return sha256_bytes(Path(path).read_bytes())


def check_target(path, data):
    """Fail if path exists with other bytes; True if it exists with the same bytes (no-op)."""
    path = Path(path)
    if not path.exists():
        return False
    if path.read_bytes() != data:
        raise Fail(f"{path} exists with different bytes; content-addressed names are never overwritten")
    return True


def write_addressed(path, data):
    """Stage <path>.tmp, re-read and verify the digest, rename. Same bytes: no-op."""
    path = Path(path)
    if check_target(path, data):
        return path
    tmp = path.with_name(path.name + ".tmp")
    try:
        tmp.write_bytes(data)
        if sha256_bytes(tmp.read_bytes()) != sha256_bytes(data):
            raise Fail(f"{tmp}: staged bytes do not match their digest")
        os.replace(tmp, path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise
    return path


def write_spec(path, spec):
    """Spec builders' output: canon bytes at a caller-named path (overwritten, staged)."""
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    try:
        tmp.write_bytes(canon(spec))
        os.replace(tmp, path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise
    return path


def need(d, key, where):
    if not isinstance(d, dict) or key not in d:
        raise Fail(f"{where}: missing '{key}'")
    return d[key]


def unique(seen, key, what):
    if key in seen:
        raise Fail(f"duplicate {what} id {key!r}")
    seen.add(key)


SENTENCE_BREAK = re.compile(r"[.!?]\s+[A-Z]")


def check_plain(row_id, f, kind):
    where = f"field {row_id}/{f['id']}"
    plain = f.get("plain")
    if not isinstance(plain, str) or not plain.strip():
        raise Fail(f"{where}: missing 'plain' (one or two sentences in plain words)")
    if len(SENTENCE_BREAK.findall(plain)) > 1:
        raise Fail(f"{where}: 'plain' has 3 or more sentences (one or two allowed)")
    if kind in OPTION_KINDS:
        for o in f["options"]:
            if not re.search(r"(?<!\w)" + re.escape(o) + r"(?!\w)", plain):
                raise Fail(f"{where}: 'plain' does not name option {o!r}")
        if not (kind == "radio" and f.get("proposed") is not None) and OTHER not in plain:
            raise Fail(f"{where}: 'plain' does not say what to choose when none fits ({OTHER!r})")


def check_field(row_id, f, image_ids, seen):
    fid = need(f, "id", f"row {row_id} field")
    unique(seen, fid, f"field in row {row_id}")
    kind = need(f, "kind", f"field {row_id}/{fid}")
    if kind not in FIELD_KINDS:
        raise Fail(f"field {row_id}/{fid}: unknown kind {kind!r}")
    if kind in OPTION_KINDS and not f.get("options"):
        raise Fail(f"field {row_id}/{fid}: {kind} has no options")
    if OTHER in (f.get("options") or []):
        raise Fail(f"field {row_id}/{fid}: option {OTHER!r} is reserved (the console adds it)")
    if "min_ticks" in f:
        mt = f["min_ticks"]
        if kind != "checkbox":
            raise Fail(f"field {row_id}/{fid}: min_ticks is only for checkbox fields")
        if not isinstance(mt, int) or isinstance(mt, bool) or mt < 1:
            raise Fail(f"field {row_id}/{fid}: min_ticks {mt!r} is not an int >= 1")
    if "empty_means" in f and (kind != "select" or f["empty_means"] not in ("silent", "unanswered")):
        raise Fail(f"field {row_id}/{fid}: empty_means {f['empty_means']!r} is only allowed as 'unanswered' (or legacy 'silent') on a select")
    if kind == "pick-row" and f.get("image_id") not in image_ids:
        raise Fail(f"field {row_id}/{fid}: pick-row names unknown image {f.get('image_id')!r}")
    check_plain(row_id, f, kind)


def check_image_refs(where, ids, image_ids):
    for i in ids:
        if i not in image_ids:
            raise Fail(f"{where}: unknown image {i!r}")


def check_files(items, what):
    """Every {path, sha256} item must exist and hash to its sha256; returns the file bytes by index."""
    blobs = []
    for it in items:
        p = Path(need(it, "path", what))
        if not p.is_file():
            raise Fail(f"{what}: missing file {p}")
        b = p.read_bytes()
        if sha256_bytes(b) != need(it, "sha256", what):
            raise Fail(f"{what}: {p} sha256 differs from the spec's")
        blobs.append(b)
    return blobs


def check_region_question(row):
    """A row asking what a region is must show enough surroundings (Chris, 2026-11-15)."""
    rid = row["id"]
    rq = row["region_question"]
    if not isinstance(rq, dict) or set(rq) != {"image_id", "roi", "source_wh", "crop_box"}:
        raise Fail(f"row {rid}: region_question must be {{image_id, roi, source_wh, crop_box}}")
    if rq["image_id"] not in row.get("image_ids", []):
        raise Fail(f"row {rid}: region_question image {rq['image_id']!r} is not one of the row's images")
    try:
        (rx0, ry0, rx1, ry1), (cx0, cy0, cx1, cy1), (W, H) = rq["roi"], rq["crop_box"], rq["source_wh"]
    except (TypeError, ValueError):
        raise Fail(f"row {rid}: region_question roi/crop_box need 4 numbers, source_wh 2")
    if not (cx0 <= rx0 < rx1 <= cx1 and cy0 <= ry0 < ry1 <= cy1):
        raise Fail(f"row {rid}: region_question roi {rq['roi']} is not inside crop_box {rq['crop_box']}")
    if not (0 <= cx0 < cx1 <= W and 0 <= cy0 < cy1 <= H):
        raise Fail(f"row {rid}: region_question crop_box {rq['crop_box']} is not inside the source {W}x{H}")
    for side, have, need_, at_edge in (
            ("above", ry0 - cy0, max(ry1 - ry0, CONTEXT_MIN_PX), cy0 == 0),
            ("below", cy1 - ry1, max(ry1 - ry0, CONTEXT_MIN_PX), cy1 == H),
            ("left", rx0 - cx0, max(rx1 - rx0, CONTEXT_MIN_PX), cx0 == 0),
            ("right", cx1 - rx1, max(rx1 - rx0, CONTEXT_MIN_PX), cx1 == W)):
        if have < need_ and not at_edge:
            raise Fail(f"row {rid}: region question lacks context {side}: {have} px shown, {need_} needed "
                       f"({need_ - have} px missing)")


CLEAR_EDGES = ("top", "bottom", "left", "right")


def ink_mask(a):
    """Bool ink mask of a 2-D uint8 grey array. Threshold by mode-midpoint: paper = most common value >= 128,
    ink = most common value < 128, T = (paper + ink) / 2; ink is a pixel < T. No pixel < 128: all False."""
    import numpy as np
    a = np.asarray(a)
    dark = a < 128
    if not dark.any():
        return np.zeros(a.shape, dtype=bool)
    light = a[~dark]
    paper = int(np.bincount(light, minlength=256).argmax()) if light.size else 255
    ink = int(np.bincount(a[dark], minlength=256).argmax())
    return a < (paper + ink) / 2


def edge_ink(a):
    """Ink pixel counts on the outermost rows and columns of a grey array."""
    m = ink_mask(a)
    return {"top": int(m[0, :].sum()), "bottom": int(m[-1, :].sum()),
            "left": int(m[:, 0].sum()), "right": int(m[:, -1].sum())}


def word_edge_ink(a, box):
    """Like edge_ink, but counting only word ink: ink pixels 8-connected (through ink) to an ink pixel inside
    box = [x0, y0, x1, y1] (x1, y1 exclusive). Foreign ink that merely touches an edge does not count."""
    import numpy as np
    m = ink_mask(a)
    x0, y0, x1, y1 = box
    seed = np.zeros(m.shape, dtype=bool)
    seed[y0:y1, x0:x1] = m[y0:y1, x0:x1]
    word = seed
    while True:
        p = np.pad(word, 1)
        h, w = word.shape
        grow = np.zeros_like(word)
        for dy in (0, 1, 2):
            for dx in (0, 1, 2):
                grow |= p[dy:dy + h, dx:dx + w]
        grow &= m
        if (grow == word).all():
            break
        word = grow
    return {"top": int(word[0, :].sum()), "bottom": int(word[-1, :].sum()),
            "left": int(word[:, 0].sum()), "right": int(word[:, -1].sum())}


def check_word_box(iid, box, width, height):
    if (not isinstance(box, list) or len(box) != 4
            or any(isinstance(v, bool) or not isinstance(v, int) for v in box)):
        raise Fail(f"image {iid}: word_box must be a list of four ints [x0, y0, x1, y1]")
    x0, y0, x1, y1 = box
    if not (0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height):
        raise Fail(f"image {iid}: word_box {box} is outside the {width}x{height} image or empty")


def check_clear_edges(image_entry, png_path):
    """An image with "clear_edges" must have no ink on those outermost rows/columns.
    Threshold by mode-midpoint: paper = most common value >= 128, ink = most common value < 128,
    T = (paper + ink) / 2; ink is a pixel < T. No pixel < 128 means no ink: pass."""
    if "word_box" in image_entry and "clear_edges" not in image_entry:
        raise Fail(f"image {image_entry.get('id')}: word_box without clear_edges")
    if "clear_edges" not in image_entry:
        return
    iid, edges = image_entry.get("id"), image_entry["clear_edges"]
    if (not isinstance(edges, list) or not edges or len(set(map(str, edges))) != len(edges)
            or any(e not in CLEAR_EDGES for e in edges)):
        raise Fail(f"image {iid}: clear_edges must be a non-empty list of distinct values from {list(CLEAR_EDGES)}")
    from PIL import Image
    import numpy as np
    with Image.open(png_path) as im:
        a = np.asarray(im.convert("L"))
    if "word_box" in image_entry:
        check_word_box(iid, image_entry["word_box"], a.shape[1], a.shape[0])
        counts = word_edge_ink(a, image_entry["word_box"])
    else:
        counts = edge_ink(a)
    for e in edges:
        n = counts[e]
        if n:
            raise Fail(f"image {iid}: ink touches the {e} edge ({n} px): the crop is flush against ink")


def check_spec(spec):
    """Structure and ids; the files are checked by hash_images."""
    if need(spec, "format", "spec") != SPEC_FORMAT:
        raise Fail(f"spec format {spec['format']!r}, expected {SPEC_FORMAT}")
    if need(spec, "kind", "spec") not in KINDS:
        raise Fail(f"unknown kind {spec['kind']!r}")
    for k in ("title", "signer", "instruction"):
        need(spec, k, "spec")
    ids = set()
    for im in need(spec, "images", "spec"):
        unique(ids, need(im, "id", "image"), "image")
    sig = need(need(spec, "signature", "spec"), "fields", "signature")
    if any(s not in SIGNATURE_FIELDS for s in sig):
        raise Fail(f"signature fields {sig}: only {list(SIGNATURE_FIELDS)} are known")
    if "help" in spec:
        h = spec["help"]
        if not isinstance(h, list) or not all(
                isinstance(x, dict) and set(x) == {"q", "a"}
                and all(isinstance(x[k], str) and x[k].strip() for k in ("q", "a")) for x in h):
            raise Fail("spec help: must be a list of {q, a} dicts with non-empty strings")
    sec_ids, row_ids = set(), set()
    for sec in need(spec, "sections", "spec"):
        unique(sec_ids, need(sec, "id", "section"), "section")
        check_image_refs(f"section {sec['id']}", sec.get("image_ids", []), ids)
        for row in need(sec, "rows", f"section {sec['id']}"):
            unique(row_ids, need(row, "id", "row"), "row")
            check_image_refs(f"row {row['id']}", row.get("image_ids", []), ids)
            seen = set()
            for f in need(row, "fields", f"row {row['id']}"):
                check_field(row["id"], f, ids, seen)
            if "region_question" in row:
                check_region_question(row)
    if "keyboard" in spec:
        check_keyboard(spec)
    for f_img in (f for s in spec["sections"] for r in s["rows"] for f in r["fields"]
                  if f["kind"] == "pick-row"):
        if not next(i for i in spec["images"] if i["id"] == f_img["image_id"]).get("frame"):
            raise Fail(f"pick-row {f_img['id']}: image {f_img['image_id']} has no frame")


def check_keyboard(spec):
    """The optional one-key block: {"field": id, "keys": {char: option or OTHER}}."""
    kb = spec["keyboard"]
    if not isinstance(kb, dict) or set(kb) != {"field", "keys"} or not isinstance(kb["keys"], dict) or not kb["keys"]:
        raise Fail("spec keyboard: must be {field, keys} with a non-empty keys dict")
    fields = [f for s in spec["sections"] for r in s["rows"] for f in r["fields"] if f["id"] == kb["field"]]
    radios = [f for f in fields if f["kind"] == "radio"]
    if not radios:
        raise Fail(f"spec keyboard: field {kb['field']!r} is not a radio on any row")
    for k, v in kb["keys"].items():
        if not (isinstance(k, str) and len(k) == 1 and k.islower()):
            raise Fail(f"spec keyboard: key {k!r} is not a single lowercase character")
        if v != OTHER and not any(v in f["options"] for f in radios):
            raise Fail(f"spec keyboard: key {k!r} maps to {v!r}, not an option of field {kb['field']!r}")


def hash_images(spec):
    """Checks every image and source file against the spec; returns ({id: sha256}, {id: bytes})."""
    blobs = check_files(spec["images"], "image")
    check_files(spec.get("sources", []), "source")
    ids = [im["id"] for im in spec["images"]]
    for im, b in zip(spec["images"], blobs):
        if b[:8] != PNG_MAGIC:
            raise Fail(f"image {im['id']}: not a PNG")
        check_clear_edges(im, im["path"])
    return ({i: sha256_bytes(b) for i, b in zip(ids, blobs)}, dict(zip(ids, blobs)))


def check_name(name, what):
    """A logical name is a relative POSIX path: non-empty, no backslash, no colon, no leading /, no .. part."""
    if not isinstance(name, str) or not name:
        raise Fail(f"{what}: name must be a non-empty string")
    if "\\" in name or ":" in name or name.startswith("/") or ".." in name.split("/"):
        raise Fail(f"{what}: name {name!r} must be a relative POSIX path (no backslash, colon, leading / or ..)")


def split_spec(spec):
    """R5: returns (hashed spec, local block). Run after check_spec and hash_images."""
    hashed = json.loads(json.dumps(spec))
    hashed.pop("run_header", None)
    local = {"images": {}, "sources": [], "run_header": spec.get("run_header")}
    seen_names = set()
    for im in hashed["images"]:
        path = im.pop("path")
        im["name"] = im.get("name") or PurePath(path).name
        check_name(im["name"], f"image {im['id']}")
        if im["name"] in seen_names:
            raise Fail(f"duplicate image name {im['name']!r}")
        seen_names.add(im["name"])
        local["images"][im["id"]] = str(path)
    src_sha = {}
    for it in hashed.get("sources", []):
        path = it.pop("path")
        it["name"] = it.get("name") or PurePath(path).name
        check_name(it["name"], "source")
        if src_sha.setdefault(it["name"], it.get("sha256")) != it.get("sha256"):
            raise Fail(f"source name {it['name']!r} used for two different sha256 values")
        local["sources"].append({"name": it["name"], "path": str(path)})
    return hashed, local


def code_bytes(code_dir=HERE):
    return (Path(code_dir) / "build.py").read_bytes() + (Path(code_dir) / "template.html").read_bytes()


def build_hash_of(spec_sha, code_sha, images):
    return sha256_bytes(canon({"spec_sha256": spec_sha, "code_sha256": code_sha, "images": images}))


# ---- page rendering -------------------------------------------------------------------------------

e = html.escape


def png_wh(b):
    return struct.unpack(">II", b[16:24])


def paragraphs(text):
    return "".join(f"<p>{e(p)}</p>" for p in text.split("\n\n") if p.strip())


def overlay_rects(overlay):
    out = []
    for r in overlay:
        c = r.get("colour", "")
        if not re.fullmatch(r"#[0-9a-fA-F]{3,8}", c):
            raise Fail(f"overlay colour {c!r} is not a #hex colour")
        out.append(f'<rect x="{float(r["x"])}" y="{float(r["y"])}" width="{float(r["w"])}" '
                   f'height="{float(r["h"])}" fill="{c}" fill-opacity="0.55"><title>{e(r.get("what", ""))}'
                   f'</title></rect>')
    return "".join(out)


def figure(im, blob, sha):
    w, h = png_wh(blob)
    fr = im.get("frame")
    fr_line = ""
    if fr:
        fr_line = (f'<div class="frame">rows {fr["rows"][0]}-{fr["rows"][1]}, cols {fr["cols"][0]}-'
                   f'{fr["cols"][1]}, frame {fr["frame_wh"][0]}x{fr["frame_wh"][1]}, k {fr["k"]}</div>')
    uri = "data:image/png;base64," + base64.b64encode(blob).decode("ascii")
    return (f'<figure class="fig" data-image="{e(im["id"])}" data-w="{w}" data-h="{h}">'
            f'<div class="figbar"><b>{e(im["id"])}</b> '
            f'<label><input type="checkbox" class="ovtoggle" checked> show overlay</label> '
            f'<label>zoom <select class="zoom"><option value="fit" selected>fit</option>'
            f'<option value="0.25">25%</option><option value="0.5">50%</option>'
            f'<option value="1">100%</option><option value="2">200%</option></select></label></div>'
            f'<div class="box"><div class="stack" style="width:{w}px;height:{h}px">'
            f'<img src="{uri}" width="{w}" height="{h}" alt="{e(im["id"])}">'
            f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}"><g class="rects">'
            f'{overlay_rects(im.get("overlay", []))}</g><g class="picks"></g></svg></div></div>'
            f'<figcaption>{e(im.get("caption", ""))}<div class="sha">sha256 {sha}</div>{fr_line}'
            f'</figcaption></figure>')


class Page:
    """Renders figures once, at the first reference; later references link back."""

    def __init__(self, spec, blobs, shas):
        self.images = {im["id"]: im for im in spec["images"]}
        self.blobs, self.shas, self.done = blobs, shas, set()

    def figs(self, ids):
        out = []
        for i in ids:
            if i in self.done:
                out.append(f'<div class="seeabove">image <a href="#fig-{e(i)}">{e(i)}</a> is shown above</div>')
            else:
                self.done.add(i)
                out.append(f'<div id="fig-{e(i)}">{figure(self.images[i], self.blobs[i], self.shas[i])}</div>')
        return "".join(out)


def field_html(row_id, f):
    name = e(f"{row_id}::{f['id']}", quote=True)
    req = "1" if f.get("required", True) else "0"
    kind = f["kind"]
    proposal = kind == "radio" and f.get("proposed") is not None
    attrs = f'data-field="{e(f["id"])}" data-kind="{"proposal" if proposal else kind}" data-required="{req}"'
    if f.get("empty_means") in ("silent", "unanswered"):
        attrs += f' data-empty="{f["empty_means"]}"'
    if kind == "pick-row":
        attrs += f' data-image="{e(f["image_id"])}"'
    head = f'<span class="fl">{e(f.get("label", f["id"]))}{"" if req == "1" else " (optional)"}</span> '
    head += f'<div class="plain">{e(f["plain"])}</div>'
    other_txt = '<input type="text" class="txt othertxt" disabled placeholder="as written">'
    if kind == "text":
        body = f'<input type="text" name="{name}" class="txt">'
    elif kind == "select":
        opts = "".join(f'<option value="{e(o)}">{e(o)}</option>' for o in f["options"] + [OTHER])
        body = f'<select name="{name}"><option value="">-</option>{opts}</select> {other_txt}'
    elif kind in ("radio", "checkbox"):
        t = "radio" if kind == "radio" else "checkbox"
        # Proposal radios get no OTHER: "correct" plus the text of what is printed already records an
        # as-written answer.
        opt_list = f["options"] if proposal else f["options"] + [OTHER]
        body = "".join(f'<label class="opt"><input type="{t}" name="{name}" value="{e(o)}"> {e(o)}</label>'
                       for o in opt_list)
        if not proposal:
            body += f" {other_txt}"
        if proposal:
            body = (f'<code class="prop">{e(f["proposed"])}</code> {body} '
                    f'<input type="text" class="txt corr" disabled placeholder="what is printed">')
    else:
        body = ('<button type="button" class="pick">pick</button> <span class="pickval">not picked</span> '
                '<button type="button" class="pickclear">clear</button>')
    return f'<div class="field" {attrs}>{head}{body}</div>'


def row_html(page, row):
    rid = e(row["id"])
    sname = e(f"{row['id']}::__state", quote=True)
    ctx = "".join(f"<li>{e(c)}</li>" for c in row.get("context", []))
    states = "".join(f'<label class="opt"><input type="radio" name="{sname}" value="{s}"{" checked" if s == "verdict" else ""}>'
                     f" {s}</label>" for s in ("verdict", "abstain", "fault"))
    fields = "".join(field_html(row["id"], f) for f in row["fields"])
    return (f'<div class="row" data-row="{rid}"><div class="rl"><code>{rid}</code> {e(row.get("label", ""))}</div>'
            f'{"<ul class=ctx>" + ctx + "</ul>" if ctx else ""}{page.figs(row.get("image_ids", []))}'
            f'<div class="fields">{fields}</div><div class="rstate">{states} '
            f'<input type="text" class="note" placeholder="note"></div></div>')


def sections_html(spec, page):
    out = []
    for sec in spec["sections"]:
        rows = "".join(row_html(page, r) for r in sec["rows"])
        out.append(f'<section class="sec" data-section="{e(sec["id"])}"><h2>{e(sec["title"])}</h2>'
                   f'<div class="text">{paragraphs(sec.get("text", ""))}</div>'
                   f'{page.figs(sec.get("image_ids", []))}{rows}</section>')
    return "".join(out)


def signature_html(spec):
    parts = []
    for s in spec["signature"]["fields"]:
        t = "date" if s == "date" else "text"
        parts.append(f'<label>{s} <input type="{t}" id="sig-{s}" class="sigfield"></label>')
    return f'<section class="sec" id="signature"><h2>Signature</h2>{" ".join(parts)}</section>'


def withheld_html(spec):
    w = spec.get("withheld", [])
    if not w:
        return ""
    items = "".join(f"<li>{e(x['what'])}: {e(x['reason'])}</li>" for x in w)
    return f'<section class="sec"><h2>Withheld</h2><ul>{items}</ul></section>'


def help_html(spec):
    items = "".join(f"<details><summary>{e(x['q'])}</summary><p>{e(x['a'])}</p></details>"
                    for x in COMMON_HELP + spec.get("help", []))
    return (f'<aside id="help" hidden><button type="button" id="helpclose">close</button>'
            f'<h2>Help</h2>{items}</aside>')


def header_html(spec, build_hash, provisional, rh=None):
    banner = ('<div class="prov">PROVISIONAL: built from an uncommitted tree. Its verdicts cannot be cited '
              'unless the architect rules it.</div>' if provisional else "")
    run = ""
    if rh:
        git = (rh.get("golden_chain_git_start") or {}).get("commit", "not recorded")
        run = f'<div>run header: golden-chain commit {e(str(git))}, clean_run {e(str(rh.get("clean_run", "not recorded")))}</div>'
    return (f'{banner}<h1>{e(spec["title"])}</h1><div class="meta"><div>signer: {e(spec["signer"])}</div>'
            f'<div>kind: {e(spec["kind"])}</div><div>console template v{TEMPLATE_VERSION}</div><div class="sha">build_hash {build_hash}</div>{run}</div>'
            f'<div class="instruction">{paragraphs(spec["instruction"])}</div>')


def data_json(obj):
    s = json.dumps(obj, ensure_ascii=False, sort_keys=True)
    return s.replace("</", "<\\/").replace("<!--", "\\u003c!--")


def render(spec, blobs, shas, build_hash, spec_sha, code_sha, provisional, template, run_header=None):
    page = Page(spec, blobs, shas)
    body = sections_html(spec, page)
    unseen = [im["id"] for im in spec["images"] if im["id"] not in page.done]
    extra = f'<section class="sec"><h2>Images</h2>{page.figs(unseen)}</section>' if unseen else ""
    parts = {
        "__TITLE__": e(spec["title"]),
        "__HEADER__": header_html(spec, build_hash, provisional, run_header),
        "__HELP__": help_html(spec),
        "__BODY__": extra + body + withheld_html(spec) + signature_html(spec),
        "__DATA__": data_json({"build_hash": build_hash, "build16": build_hash[:16], "kind": spec["kind"],
                               "spec_sha256": spec_sha, "code_sha256": code_sha, "images": shas,
                               "provisional": provisional, "other": OTHER, "spec": spec,
                               "run_header": run_header}),
    }
    return re.sub("|".join(parts), lambda m: parts[m.group(0)], template)


def build(spec_path, out_dir=None, now=None):
    start = git_state(REPO)
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    check_spec(spec)
    shas, blobs = hash_images(spec)
    hashed, local = split_spec(spec)
    spec_bytes = canon(hashed)
    spec_sha, code_sha = sha256_bytes(spec_bytes), sha256_bytes(code_bytes())
    bh = build_hash_of(spec_sha, code_sha, shas)
    b16, kind = bh[:16], spec["kind"]
    end = git_state(REPO)
    provisional = not clean_run(start, end)
    template = (HERE / "template.html").read_text(encoding="utf-8")
    page = render(hashed, blobs, shas, bh, spec_sha, code_sha, provisional, template, local["run_header"]).encode("utf-8")
    manifest = {"format": MANIFEST_FORMAT, "kind": kind, "build_hash": bh, "build16": b16,
                "spec_path": str(Path(spec_path).resolve()), "spec_sha256": spec_sha,
                "code_sha256": code_sha, "template_version": TEMPLATE_VERSION, "html_sha256": sha256_bytes(page), "images": shas, "local": local,
                "golden_chain_git_start": start, "golden_chain_git_end": end, "provisional": provisional,
                "utc": (now or datetime.datetime.now(datetime.timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")}
    out = Path(out_dir) if out_dir else Path.home() / ".golden-chain" / "console" / kind
    out.mkdir(parents=True, exist_ok=True)
    files = {"html": (out / f"console_{kind}_{b16}.html", page),
             "manifest": (out / f"manifest_{kind}_{b16}.json", canon(manifest)),
             "spec": (out / f"spec_{kind}_{b16}.json", spec_bytes)}
    for p, data in files.values():
        check_target(p, data)  # refuse before writing anything
    return {k: write_addressed(p, data) for k, (p, data) in files.items()}


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("spec")
    ap.add_argument("--out-dir")
    a = ap.parse_args(argv)
    try:
        made = build(a.spec, a.out_dir)
    except Fail as ex:
        print(f"FAIL: {ex}", file=sys.stderr)
        return 1
    for k, p in made.items():
        print(f"{k}: {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
