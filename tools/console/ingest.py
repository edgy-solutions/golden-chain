"""Signing console ingest: a verdicts export + its manifest -> the signed record (ADR-0006).

Usage: python tools/console/ingest.py <verdicts.json> <manifest.json> [--provisional]
                                      [--out-dir DIR] [--write] [--ttl-out PATH] [--records-dir DIR]
       out-dir defaults to the manifest's directory.

Checks, each a Fail with nothing written (ADR-0006 item 8):
  1. formats; kinds agree
  2. recomputation from the files: the spec copy next to the manifest (spec_<kind>_<build16>.json),
     the CURRENT build.py + template.html, and every image file, against the manifest and the export
  3. export.complete is true and the spec's required fields are answered (rechecked here); on the
     plumb-line a modality left empty is silence, a complete verdict (dispatch 2026-11-08 §1); from console
     v3 any select field with empty_means "silent" is the same (silent_rows)
  4. no abstain/fault row holds a value
  5. signature name and date
  6. manifest.provisional is false, unless --provisional
  7. the export's rows are the spec's rows
Writes signed_<kind>_<build16>.json. With --write also the instance record: a Markdown file under
docs/handoff/ (empty-strips, wcf1647, q11-crops, truthset-italic; plumb-line-followup also). For the plumb-line kinds
(plumb-line, plumb-line-followup) the merge (plumb_merge.merge, ADR-0006 R1) writes the numbered record
docs/sittings/plumb-line/NNNN_signed_<kind>_<build16>.json and replaces data/plumb-line.ttl with the replay of
all records, only once ADR-0006 says "- Status: Ratified" (else Fail before anything is written; --ttl-out PATH
writes the TTL there instead, with its records in --records-dir, default PATH's directory/sittings). The merge
refuses if the committed TTL is not the replay of its records.

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
KINDS = ("empty-strips", "plumb-line", "plumb-line-followup", "wcf1647", "q11-crops", "truthset-italic")
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


def is_other(v):
    return isinstance(v, dict) and "other" in v


def other_ok(v):
    return bool(str(v["other"] or "").strip())


def answered(f, v):
    if v is None:
        return False
    if is_other(v):
        return other_ok(v)
    if isinstance(v, list):
        if any(is_other(x) and not other_ok(x) for x in v):
            return False
        n = f.get("min_ticks")
        if n and len(v) < n:
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


def empty_fields(spec, ex, means=("silent", "unanswered")):
    """{row id: [field ids]}: verdict rows' fields left empty that are allowed to be (complete). A field is
    allowed when its spec field has empty_means in `means` ("silent", legacy v3; "unanswered", v4), or (legacy
    v2 plumb-line specs) it is the modality field, read as "silent". Dispatch 2026-11-08 §1 and ADR-0006 R1 §6:
    an empty field does not make an export incomplete."""
    out = {}
    for _, r in spec_rows(spec):
        row = ex["rows"][r["id"]]
        if row["state"] != "verdict":
            continue
        vals = row.get("values") or {}
        ids = [f["id"] for f in r["fields"]
               if (f.get("empty_means") in means
                   or ("silent" in means and spec["kind"] == "plumb-line" and f["id"] == "modality" and "empty_means" not in f))
               and vals.get(f["id"]) is None]
        if ids:
            out[r["id"]] = ids
    return out


def silent_fields(spec, ex):
    """Legacy alias: the empty fields read as silence (v3 / v2 specs)."""
    return empty_fields(spec, ex, ("silent",))


def silent_rows(spec, ex):
    return list(empty_fields(spec, ex))


def check_complete(spec, ex):
    silent = empty_fields(spec, ex)
    if ex.get("complete") is not True and not silent:
        raise Fail("export is not complete")
    for _, r in spec_rows(spec):
        row = ex["rows"][r["id"]]
        if row["state"] != "verdict":
            continue
        for f in r["fields"]:
            if f["id"] in silent.get(r["id"], []):
                continue
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
        return "not answered"
    if is_other(v):
        return f'other, as written: "{v["other"]}"'
    if isinstance(v, list):
        return ", ".join(render_answer(x) for x in v) if v else "(none ticked)"
    if isinstance(v, dict) and "page_row" in v:
        return f"page row {v['page_row']} (frame {v['frame_wh'][0]}x{v['frame_wh'][1]})"
    if isinstance(v, dict) and v.get("action") == "correct":
        return f'corrected: "{v["text"]}" (proposed "{v["proposed"]}"); signed reading'
    if isinstance(v, dict) and v.get("action") == "confirm":
        return f'confirmed: "{v["proposed"]}"'
    return str(v)


def answer_text(v):
    """italic / roman / other: note; for the truthset-italic record."""
    if v is None:
        return "not answered"
    if is_other(v):
        return f"other: {v['other']}"
    return str(v)


def markdown_truthset(signed, spec):
    """Keys and answers only (no word text, no image): the truth-set v2 record."""
    keys = {r["id"]: r.get("key", "") for s in spec["sections"] for r in s["rows"]}
    sig = signed["signature"]
    ans = {r["row_id"]: {f["id"]: f["value"] for f in r["fields"]} for r in signed["rows"]}
    state = {r["row_id"]: r["state"] for r in signed["rows"]}
    out = [f"# {spec['title']}", "", "## Provenance", "",
           f"- Signer: {signed['signer']} ({sig.get('name', '')}), {sig.get('date', '')}",
           f"- build_hash: {signed['build_hash']}", f"- export sha256: {signed['export_sha256']}",
           f"- manifest sha256: {signed['manifest_sha256']}",
           f"- provisional: {str(signed['provisional']).lower()}", "", "## Words", "",
           "| id | key | answer |", "|---|---|---|"]

    def one(rid, fid):
        return answer_text(ans[rid].get(fid)) if state[rid] == "verdict" else state[rid]
    for r in next(s for s in spec["sections"] if s["id"] == "words")["rows"]:
        out.append("| " + " | ".join(cell(x) for x in (r["id"], keys[r["id"]], one(r["id"], "v"))) + " |")
    out += ["", "## Page rows", "", f"- p912.left face: {cell(one('p912.left', 'face'))}",
            f"- p912.left what: {cell(one('p912.left', 'what'))}",
            f"- ccel.p914-foot footnotes: {cell(one('ccel.p914-foot', 'v'))}"]
    return ("\n".join(out) + "\n").encode("utf-8")


def _export_of(signed):
    """The export-shaped view of a signed record, for empty_fields."""
    return {"rows": {r["row_id"]: {"state": r["state"], "values": {f["id"]: f["value"] for f in r["fields"]}}
                     for r in signed["rows"]}}


def markdown(signed, spec):
    ex = _export_of(signed)
    silent = {(rid, fid) for rid, fids in empty_fields(spec, ex, ("silent",)).items() for fid in fids}
    unans = {(rid, fid) for rid, fids in empty_fields(spec, ex, ("unanswered",)).items() for fid in fids}
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
                    r["row_id"], q, ("left empty, read as silent" if (r["row_id"], f["id"]) in silent
                                  else "left empty: unanswered, the earlier answer stands" if (r["row_id"], f["id"]) in unans
                                  else render_answer(f["value"])),
                    r["state"], r["note"] if n == 0 else "")) + " |")
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
    """The plumb-line TTL of one signed record alone: the replay of [signed] (ADR-0006 R1)."""
    import plumb_merge
    return plumb_merge.replay([signed])


def adr_ratified():
    try:
        return any(l.startswith("- Status: Ratified") for l in Path(ADR).read_text(encoding="utf-8").splitlines())
    except OSError:
        return False


def instance_output(signed, spec, ttl_out, records_dir=None):
    """[(path, bytes)] of the instance record(s); Fails before anything is written if it may not be.
    Plumb-line kinds merge: the numbered record file, then the replayed TTL (which replaces the old one)."""
    if signed["kind"] in ("plumb-line", "plumb-line-followup"):
        import plumb_merge
        if ttl_out is None and not adr_ratified():
            raise Fail("ADR-0006 not ratified: plumb-line TTL not written")
        ttl_path = Path(ttl_out) if ttl_out else Path(PLUMB_TTL)
        if records_dir is None:
            records_dir = plumb_merge.RECORDS if ttl_out is None else ttl_path.parent / "sittings"
        rec, rec_bytes, ttl_bytes = plumb_merge.merge(signed, ttl_path, records_dir)
        out = [(rec, rec_bytes), (ttl_path, ttl_bytes)]
        if signed["kind"] == "plumb-line-followup":
            name = f"SIGNED_{signed['kind'].replace('-', '_')}_{signed['build_hash'][:16]}.md"
            out.append((Path(HANDOFF) / name, markdown(signed, spec)))
        return out
    name = f"SIGNED_{signed['kind'].replace('-', '_')}_{signed['build_hash'][:16]}.md"
    md = markdown_truthset if signed["kind"] == "truthset-italic" else markdown
    return [(Path(HANDOFF) / name, md(signed, spec))]


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


def write_replace(path, data):
    """Atomic overwrite (tmp + os.replace, digest re-checked): the plumb-line merge's TTL only."""
    path = Path(path)
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


def ingest(verdicts, manifest, provisional=False, out_dir=None, write=False, ttl_out=None, now=None,
           records_dir=None):
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
        plan += instance_output(signed, spec, ttl_out, records_dir)
    merged_ttl = None
    if write and signed["kind"] in ("plumb-line", "plumb-line-followup"):
        merged_ttl = plan[2][0]  # the TTL: the one file the merge may overwrite
    for p, data in plan:  # refuse every collision before writing anything
        if p != merged_ttl and p.exists() and p.read_bytes() != data:
            raise Fail(f"{p} exists with different bytes; content-addressed names are never overwritten")
    made = []
    for p, data in plan:
        p.parent.mkdir(parents=True, exist_ok=True)
        made.append(write_replace(p, data) if p == merged_ttl else write_addressed(p, data))
    return made


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("verdicts")
    ap.add_argument("manifest")
    ap.add_argument("--provisional", action="store_true")
    ap.add_argument("--out-dir")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--ttl-out")
    ap.add_argument("--records-dir")
    a = ap.parse_args(argv)
    try:
        made = ingest(a.verdicts, a.manifest, a.provisional, a.out_dir, a.write, a.ttl_out, records_dir=a.records_dir)
    except Fail as ex:
        print(f"FAIL: {ex}", file=sys.stderr)
        return 1
    for p in made:
        print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
