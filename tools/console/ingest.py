"""Signing console ingest: a verdicts export + its manifest -> the signed record (ADR-0006).

Usage: python tools/console/ingest.py <verdicts.json> <manifest.json> [--provisional]
                                      [--out-dir DIR] [--write] [--ttl-out PATH]
       out-dir defaults to the manifest's directory.

Checks, each a Fail with nothing written (ADR-0006 item 8):
  1. formats; kinds agree
  2. recomputation from the files: the spec copy next to the manifest (spec_<kind>_<build16>.json),
     the CURRENT build.py + template.html, and every image file, against the manifest and the export
  3. export.complete is true and the spec's required fields are answered (rechecked here)
  4. no abstain/fault row holds a value
  5. signature name and date
  6. manifest.provisional is false, unless --provisional
  7. the export's rows are the spec's rows
Writes signed_<kind>_<build16>.json. With --write also the instance record: a Markdown file under
docs/handoff/ (empty-strips, wcf1647) or TTL for the plumb-line, written to data/plumb-line.ttl only
once ADR-0006 says "- Status: Ratified" (else Fail before anything is written; --ttl-out PATH writes
the TTL there instead).

The build hash is recomputed here by its own code, not imported from build.py (truth-set form 8.5):
the rule is spelled out at the check site.
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from column_rule import REPO, Fail  # noqa: E402

CODE_DIR = HERE  # where build.py and template.html are read from (tests point it elsewhere)
HANDOFF = REPO / "docs" / "handoff"
ADR = REPO / "docs" / "adr" / "0006-signing-console.md"
PLUMB_TTL = REPO / "data" / "plumb-line.ttl"
KINDS = ("empty-strips", "plumb-line", "wcf1647")
STATES = ("verdict", "abstain", "fault")
LOCI_HEADER = """@base <https://w3id.org/golden-chain/> .
@prefix gc: <https://w3id.org/golden-chain/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
"""
TIERS = ("first", "second", "third")
CLARITIES = ("settled", "contested", "open")
MODALITIES = ("required", "taught", "tolerated", "forbidden")
SLUG = re.compile(r"[a-z0-9][a-z0-9-]*")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def load(path, what):
    try:
        raw = Path(path).read_bytes()
        return raw, json.loads(raw.decode("utf-8"))
    except (OSError, ValueError) as ex:
        raise Fail(f"{what} {path}: unreadable: {ex}")


def same(what, *vals):
    if len({json.dumps(v, sort_keys=True) for v in vals}) != 1:
        raise Fail(f"{what} disagree: " + " / ".join(str(v) for v in vals))


# ---- check 2: recomputation -------------------------------------------------------------------------

def check_formats(ex, man):
    if ex.get("format") != "golden-chain-console-verdicts/1":
        raise Fail(f"export format {ex.get('format')!r}")
    if man.get("format") != "golden-chain-console-manifest/1":
        raise Fail(f"manifest format {man.get('format')!r}")
    if ex.get("kind") != man.get("kind") or man.get("kind") not in KINDS:
        raise Fail(f"kinds disagree or unknown: export {ex.get('kind')!r}, manifest {man.get('kind')!r}")
    b16 = str(man.get("build16"))
    if not re.fullmatch(r"[0-9a-f]{16}", b16) or b16 != str(man.get("build_hash"))[:16]:
        raise Fail("manifest build16 is not the first 16 digits of its build_hash")


def recompute(ex, man, manifest_dir):
    """Returns the spec. Every digest is recomputed from the files on disk."""
    kind, b16 = man["kind"], man["build16"]
    spec_path = Path(manifest_dir) / f"spec_{kind}_{b16}.json"
    spec_raw, spec = load(spec_path, "spec copy")
    spec_sha = sha(spec_raw)
    same("spec_sha256 (spec copy / manifest / export)", spec_sha, man.get("spec_sha256"), ex.get("spec_sha256"))
    code_sha = sha((Path(CODE_DIR) / "build.py").read_bytes() + (Path(CODE_DIR) / "template.html").read_bytes())
    if code_sha != man.get("code_sha256"):
        raise Fail(f"console code changed since build (code_sha256 now {code_sha[:16]}, "
                   f"manifest {str(man.get('code_sha256'))[:16]})")
    if code_sha != ex.get("code_sha256"):
        raise Fail("export code_sha256 differs from the console code")
    images = {}
    for im in spec.get("images", []):
        p = Path(im["path"])
        if not p.is_file():
            raise Fail(f"image {im['id']}: file missing: {p}")
        images[im["id"]] = sha(p.read_bytes())
        if images[im["id"]] != im["sha256"]:
            raise Fail(f"image {im['id']}: file sha256 differs from the spec's ({p})")
    same("image ids (spec / manifest / export)", sorted(images), sorted(man.get("images", {})),
         sorted(ex.get("images", {})))
    for i, h in images.items():
        same(f"image {i} sha256 (file / manifest / export)", h, man["images"][i], ex["images"][i])
    # build_hash = sha256 of the UTF-8 bytes of json.dumps({"spec_sha256", "code_sha256", "images"},
    # ensure_ascii=False, sort_keys=True, indent=1) (ADR-0006 item 6)
    bh = sha(json.dumps({"spec_sha256": spec_sha, "code_sha256": code_sha, "images": images},
                        ensure_ascii=False, sort_keys=True, indent=1).encode("utf-8"))
    same("build_hash (recomputed / manifest / export)", bh, man.get("build_hash"), ex.get("build_hash"))
    return spec


# ---- checks 3-7 -------------------------------------------------------------------------------------

def spec_rows(spec):
    return [(s, r) for s in spec["sections"] for r in s["rows"]]


def answered(f, v):
    if v is None:
        return False
    if isinstance(v, dict) and v.get("action") == "correct":
        return bool(str(v.get("text") or "").strip())
    return True


def check_rows(spec, ex):
    want = [r["id"] for _, r in spec_rows(spec)]
    got = ex.get("rows", {})
    missing, extra = sorted(set(want) - set(got)), sorted(set(got) - set(want))
    if missing or extra:
        raise Fail(f"rows differ from the spec: missing {missing}, unexpected {extra}")
    for _, r in spec_rows(spec):
        if got[r["id"]].get("state") not in STATES:
            raise Fail(f"row {r['id']}: unknown state {got[r['id']].get('state')!r}")


def check_complete(spec, ex):
    if ex.get("complete") is not True:
        raise Fail("export is not complete")
    for _, r in spec_rows(spec):
        row = ex["rows"][r["id"]]
        if row["state"] != "verdict":
            continue
        for f in r["fields"]:
            if f.get("required", True) and not answered(f, (row.get("values") or {}).get(f["id"])):
                raise Fail(f"row {r['id']}: required field {f['id']} is unanswered")


def check_nonverdicts(spec, ex):
    for _, r in spec_rows(spec):
        row = ex["rows"][r["id"]]
        vals = [k for k, v in (row.get("values") or {}).items() if v is not None]
        if row["state"] != "verdict" and vals:
            raise Fail(f"row {r['id']}: state {row['state']} but fields hold values: {vals}")


def check_signature(spec, ex):
    sig = ex.get("signature") or {}
    for k in spec["signature"]["fields"]:
        if not str(sig.get(k) or "").strip():
            raise Fail(f"signature {k} is empty")


def signed_record(spec, ex, man, ex_raw, man_raw, now):
    rows = []
    for s, r in spec_rows(spec):
        row = ex["rows"][r["id"]]
        vals = row.get("values") or {}
        rows.append({"row_id": r["id"], "section": s["id"], "label": r.get("label", ""),
                     "state": row["state"], "note": row.get("note", ""),
                     "fields": [{"id": f["id"], "label": f.get("label", f["id"]), "kind": f["kind"],
                                 "value": vals.get(f["id"])} for f in r["fields"]]})
    return {"format": "golden-chain-console-signed/1", "kind": man["kind"], "build_hash": man["build_hash"],
            "export_sha256": sha(ex_raw), "manifest_sha256": sha(man_raw),
            "provisional": bool(man.get("provisional")), "signer": spec["signer"],
            "signed_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "rows": rows, "signature": ex["signature"]}


# ---- instance writers -------------------------------------------------------------------------------

def cell(s):
    return str(s).replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def render_answer(v):
    if v is None:
        return "unknown"
    if isinstance(v, list):
        return ", ".join(v) if v else "(none ticked)"
    if isinstance(v, dict) and "page_row" in v:
        return f"page row {v['page_row']} (frame {v['frame_wh'][0]}x{v['frame_wh'][1]})"
    if isinstance(v, dict) and v.get("action") == "correct":
        return f'corrected: "{v["text"]}" (proposed "{v["proposed"]}"); signed reading'
    if isinstance(v, dict) and v.get("action") == "confirm":
        return f'confirmed: "{v["proposed"]}"'
    return str(v)


def markdown(signed, spec):
    sig = signed["signature"]
    out = [f"# {spec['title']}", "", "## Provenance", "",
           f"- Signer: {signed['signer']} ({sig.get('name', '')}), {sig.get('date', '')}",
           f"- build_hash: {signed['build_hash']}", f"- export sha256: {signed['export_sha256']}",
           f"- manifest sha256: {signed['manifest_sha256']}",
           f"- spec sha256: {sha(json.dumps(spec, ensure_ascii=False, sort_keys=True, indent=1).encode('utf-8'))}",
           f"- provisional: {str(signed['provisional']).lower()}"]
    rh = spec.get("run_header")
    if rh:
        out.append(f"- run header: golden-chain commit {(rh.get('golden_chain_git_start') or {}).get('commit', 'not recorded')},"
                   f" clean_run {rh.get('clean_run', 'not recorded')}")
    out += [f"- image {im['id']}: {im['sha256']}" for im in spec["images"]]
    by_sec = {}
    for r in signed["rows"]:
        by_sec.setdefault(r["section"], []).append(r)
    for s in spec["sections"]:
        out += ["", f"## {s['title']}", "", "| Row | Question | Answer | State | Note |", "|---|---|---|---|---|"]
        for r in by_sec.get(s["id"], []):
            for n, f in enumerate(r["fields"]):
                q = f["label"] if not r["label"] else f"{r['label']}: {f['label']}"
                out.append("| " + " | ".join(cell(x) for x in (
                    r["row_id"], q, render_answer(f["value"]), r["state"], r["note"] if n == 0 else "")) + " |")
    return ("\n".join(out)).encode("utf-8")


def slug_ok(*parts):
    for p in parts:
        if not SLUG.fullmatch(p):
            raise Fail(f"plumb-line: {p!r} is not a slug")


def choice(v, allowed, what):
    if v is not None and v not in allowed:
        raise Fail(f"plumb-line: {what} {v!r} is not one of {list(allowed)}")
    return v


def plumb_ttl(signed):
    """Proposed mapping, ADR-0006 open point 1."""
    lines, loci, holds, holdings, skipped = [], [], [], [], []
    src = f"source/plumb-line/sitting-{signed['build_hash'][:16]}"
    for r in signed["rows"]:
        vals = {f["id"]: f["value"] for f in r["fields"]}
        if r["state"] != "verdict":
            skipped.append(r["row_id"])
            continue
        locus, _, pos = r["row_id"].partition(".")
        if pos == "locus":
            slug_ok(locus)
            t, c = choice(vals.get("tier"), TIERS, "tier"), choice(vals.get("clarity"), CLARITIES, "clarity")
            bits = ([f"gc:tier <vocab/tier/{t}>"] if t else []) + ([f"gc:clarity <vocab/clarity/{c}>"] if c else [])
            if bits:
                loci.append(f"<locus/{locus}> " + " ; ".join(bits) + " .")
            continue
        slug_ok(locus, pos)
        m = vals.get("modality")
        if m is None or m == "silent":
            continue
        choice(m, MODALITIES, "modality")
        h = f"holding/plumb-line/{locus}/{pos}"
        holds.append(f"<body/plumb-line> gc:holds <{h}> .")
        holdings.append(f"<{h}> a gc:Holding ; gc:position <position/{locus}/{pos}> ;\n"
                        f"    gc:modality <vocab/modality/{m}> ; dcterms:source <{src}> ;\n"
                        f"    gc:status <vocab/status/ratified> ; gc:proposedBy <agent/architect> ; "
                        f"gc:ratifiedBy <agent/architect> .")
    lines += [LOCI_HEADER, "# Plumb-line sitting " + signed["build_hash"][:16] + " (proposed mapping, ADR-0006 open point 1)."]
    lines.append("# abstain/fault rows, nothing written: " + (", ".join(skipped) if skipped else "none"))
    lines += [""] + loci + [""] + holds + [""] + holdings + [""]
    lines.append(f'<{src}> a gc:SourceDivision ; dcterms:identifier "{signed["export_sha256"]}" ;\n'
                 f"    gc:status <vocab/status/ratified> ; gc:proposedBy <agent/architect> ; gc:ratifiedBy <agent/architect> .")
    return ("\n".join(lines) + "\n").encode("utf-8")


def adr_ratified():
    try:
        return any(l.startswith("- Status: Ratified") for l in Path(ADR).read_text(encoding="utf-8").splitlines())
    except OSError:
        return False


def instance_output(signed, spec, ttl_out):
    """(path, bytes) of the instance record; Fails before anything is written if it may not be."""
    if signed["kind"] == "plumb-line":
        if ttl_out is None and not adr_ratified():
            raise Fail("ADR-0006 not ratified: plumb-line TTL not written")
        return Path(ttl_out) if ttl_out else Path(PLUMB_TTL), plumb_ttl(signed)
    name = f"SIGNED_{signed['kind'].replace('-', '_')}_{signed['build_hash'][:16]}.md"
    return Path(HANDOFF) / name, markdown(signed, spec)


def write_addressed(path, data):
    path = Path(path)
    if path.exists():
        if path.read_bytes() != data:
            raise Fail(f"{path} exists with different bytes; content-addressed names are never overwritten")
        return path
    tmp = path.with_name(path.name + ".tmp")
    try:
        tmp.write_bytes(data)
        if sha(tmp.read_bytes()) != sha(data):
            raise Fail(f"{tmp}: staged bytes do not match their digest")
        os.replace(tmp, path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise
    return path


def ingest(verdicts, manifest, provisional=False, out_dir=None, write=False, ttl_out=None, now=None):
    ex_raw, ex = load(verdicts, "export")
    man_raw, man = load(manifest, "manifest")
    check_formats(ex, man)
    spec = recompute(ex, man, Path(manifest).resolve().parent)
    check_rows(spec, ex)
    check_complete(spec, ex)
    check_nonverdicts(spec, ex)
    check_signature(spec, ex)
    if man.get("provisional") and not provisional:
        raise Fail("manifest is provisional (built from an uncommitted tree); pass --provisional to sign anyway")
    now = now or datetime.datetime.now(datetime.timezone.utc)
    signed = signed_record(spec, ex, man, ex_raw, man_raw, now)
    out = Path(out_dir) if out_dir else Path(manifest).resolve().parent
    signed_path = out / f"signed_{man['kind']}_{man['build16']}.json"
    signed_bytes = json.dumps(signed, ensure_ascii=False, sort_keys=True, indent=1).encode("utf-8")
    plan = [(signed_path, signed_bytes)]
    if write:
        plan.append(instance_output(signed, spec, ttl_out))
    for p, data in plan:  # refuse every collision before writing anything
        if p.exists() and p.read_bytes() != data:
            raise Fail(f"{p} exists with different bytes; content-addressed names are never overwritten")
    made = []
    for p, data in plan:
        p.parent.mkdir(parents=True, exist_ok=True)
        made.append(write_addressed(p, data))
    return made


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("verdicts")
    ap.add_argument("manifest")
    ap.add_argument("--provisional", action="store_true")
    ap.add_argument("--out-dir")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--ttl-out")
    a = ap.parse_args(argv)
    try:
        made = ingest(a.verdicts, a.manifest, a.provisional, a.out_dir, a.write, a.ttl_out)
    except Fail as ex:
        print(f"FAIL: {ex}", file=sys.stderr)
        return 1
    for p in made:
        print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
