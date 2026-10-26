"""Signing console builder: spec.json -> one self-contained HTML page + manifest (ADR-0006).

Usage: python tools/console/build.py <spec.json> [--out-dir DIR]
       out-dir defaults to ~/.golden-chain/console/<kind>/

Writes console_<kind>_<build16>.html, manifest_<kind>_<build16>.json and a copy of the spec,
spec_<kind>_<build16>.json (canonical bytes), so that ingest.py finds it next to the manifest.

Digests (ADR-0006 item 6, truth-set form 8): every JSON is canon(obj) = json.dumps(obj,
ensure_ascii=False, sort_keys=True, indent=1) in UTF-8, no trailing newline, LF only.
  spec_sha256 = sha256(canon(spec))
  code_sha256 = sha256(bytes(build.py) + bytes(template.html))
  build_hash  = sha256(canon({"spec_sha256", "code_sha256", "images": {id: sha256(png bytes)}}))
  build16     = build_hash[:16]
Files get content-addressed names: staged as <name>.tmp, re-read and verified, then renamed. A write to
an existing name with different bytes is refused; the same bytes are a no-op.

The page is rendered here (images inline as data URIs, controls, sha256 beside each image); the
template supplies the style and the script that wires the controls, export and draft.
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
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from column_rule import REPO, Fail, clean_run, git_state  # noqa: E402

SPEC_FORMAT = "golden-chain-console-spec/1"
MANIFEST_FORMAT = "golden-chain-console-manifest/1"
KINDS = ("empty-strips", "plumb-line", "wcf1647")
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


def check_field(row_id, f, image_ids, seen):
    fid = need(f, "id", f"row {row_id} field")
    unique(seen, fid, f"field in row {row_id}")
    kind = need(f, "kind", f"field {row_id}/{fid}")
    if kind not in FIELD_KINDS:
        raise Fail(f"field {row_id}/{fid}: unknown kind {kind!r}")
    if kind in OPTION_KINDS and not f.get("options"):
        raise Fail(f"field {row_id}/{fid}: {kind} has no options")
    if kind == "pick-row" and f.get("image_id") not in image_ids:
        raise Fail(f"field {row_id}/{fid}: pick-row names unknown image {f.get('image_id')!r}")


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
    for f_img in (f for s in spec["sections"] for r in s["rows"] for f in r["fields"]
                  if f["kind"] == "pick-row"):
        if not next(i for i in spec["images"] if i["id"] == f_img["image_id"]).get("frame"):
            raise Fail(f"pick-row {f_img['id']}: image {f_img['image_id']} has no frame")


def hash_images(spec):
    """Checks every image and source file against the spec; returns ({id: sha256}, {id: bytes})."""
    blobs = check_files(spec["images"], "image")
    check_files(spec.get("sources", []), "source")
    ids = [im["id"] for im in spec["images"]]
    for im, b in zip(spec["images"], blobs):
        if b[:8] != PNG_MAGIC:
            raise Fail(f"image {im['id']}: not a PNG")
    return ({i: sha256_bytes(b) for i, b in zip(ids, blobs)}, dict(zip(ids, blobs)))


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
            f'<label>zoom <select class="zoom"><option value="0.25">25%</option><option value="0.5">50%</option>'
            f'<option value="1" selected>100%</option><option value="2">200%</option></select></label></div>'
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
    if kind == "pick-row":
        attrs += f' data-image="{e(f["image_id"])}"'
    head = f'<span class="fl">{e(f.get("label", f["id"]))}{"" if req == "1" else " (optional)"}</span> '
    if kind == "text":
        body = f'<input type="text" name="{name}" class="txt">'
    elif kind == "select":
        opts = "".join(f'<option value="{e(o)}">{e(o)}</option>' for o in f["options"])
        body = f'<select name="{name}"><option value="">-</option>{opts}</select>'
    elif kind in ("radio", "checkbox"):
        t = "radio" if kind == "radio" else "checkbox"
        body = "".join(f'<label class="opt"><input type="{t}" name="{name}" value="{e(o)}"> {e(o)}</label>'
                       for o in f["options"])
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


def header_html(spec, build_hash, provisional):
    banner = ('<div class="prov">PROVISIONAL: built from an uncommitted tree. Its verdicts cannot be cited '
              'unless the architect rules it.</div>' if provisional else "")
    rh = spec.get("run_header")
    run = ""
    if rh:
        git = (rh.get("golden_chain_git_start") or {}).get("commit", "not recorded")
        run = f'<div>run header: golden-chain commit {e(str(git))}, clean_run {e(str(rh.get("clean_run", "not recorded")))}</div>'
    return (f'{banner}<h1>{e(spec["title"])}</h1><div class="meta"><div>signer: {e(spec["signer"])}</div>'
            f'<div>kind: {e(spec["kind"])}</div><div class="sha">build_hash {build_hash}</div>{run}</div>'
            f'<div class="instruction">{paragraphs(spec["instruction"])}</div>')


def data_json(obj):
    s = json.dumps(obj, ensure_ascii=False, sort_keys=True)
    return s.replace("</", "<\\/").replace("<!--", "\\u003c!--")


def render(spec, blobs, shas, build_hash, spec_sha, code_sha, provisional, template):
    page = Page(spec, blobs, shas)
    body = sections_html(spec, page)
    unseen = [im["id"] for im in spec["images"] if im["id"] not in page.done]
    extra = f'<section class="sec"><h2>Images</h2>{page.figs(unseen)}</section>' if unseen else ""
    parts = {
        "__TITLE__": e(spec["title"]),
        "__HEADER__": header_html(spec, build_hash, provisional),
        "__BODY__": extra + body + withheld_html(spec) + signature_html(spec),
        "__DATA__": data_json({"build_hash": build_hash, "build16": build_hash[:16], "kind": spec["kind"],
                               "spec_sha256": spec_sha, "code_sha256": code_sha, "images": shas,
                               "provisional": provisional, "spec": spec}),
    }
    return re.sub("|".join(parts), lambda m: parts[m.group(0)], template)


def build(spec_path, out_dir=None, now=None):
    start = git_state(REPO)
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    check_spec(spec)
    shas, blobs = hash_images(spec)
    spec_bytes = canon(spec)
    spec_sha, code_sha = sha256_bytes(spec_bytes), sha256_bytes(code_bytes())
    bh = build_hash_of(spec_sha, code_sha, shas)
    b16, kind = bh[:16], spec["kind"]
    end = git_state(REPO)
    provisional = not clean_run(start, end)
    template = (HERE / "template.html").read_text(encoding="utf-8")
    page = render(spec, blobs, shas, bh, spec_sha, code_sha, provisional, template).encode("utf-8")
    manifest = {"format": MANIFEST_FORMAT, "kind": kind, "build_hash": bh, "build16": b16,
                "spec_path": str(Path(spec_path).resolve()), "spec_sha256": spec_sha,
                "code_sha256": code_sha, "html_sha256": sha256_bytes(page), "images": shas,
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
