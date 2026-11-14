"""Plumb-line merge by replay (ADR-0006 Revision 1).

data/plumb-line.ttl is the deterministic product of replaying the committed signed records
(docs/sittings/plumb-line/NNNN_signed_<kind>_<build16>.json) in order. Pure functions; the only I/O is
reading the records directory and the TTL in `merge`.
"""

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
from column_rule import REPO, Fail  # noqa: E402
import ingest  # noqa: E402

RECORDS = REPO / "docs" / "sittings" / "plumb-line"
KINDS = ("plumb-line", "plumb-line-followup")
NAME = re.compile(r"^(\d{4})_signed_(plumb-line|plumb-line-followup)_([0-9a-f]{16})\.json$")
NOTE_KEYS = ("abstain_fault", "other", "unanswered", "silent_removed", "silent_nothing", "flags_not_written",
             "not_data")
NOTE_TEXT = (("abstain_fault", "abstain/fault, untouched"),
             ("other", "other, as written, untouched (the architect rules)"),
             ("unanswered", "modality left empty, unanswered, untouched"),
             ("silent_removed", "verdict silent, Holding removed"),
             ("silent_nothing", "verdict silent, nothing held"),
             ("flags_not_written", "unchurches confirmed on a Position the plumb-line does not hold, not written"),
             ("not_data", "not data, in the SIGNED record only"))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def record_paths(d):
    d = Path(d)
    if not d.exists():
        return []
    files = sorted(d.iterdir())
    for p in files:
        if not p.is_file() or not NAME.match(p.name):
            raise Fail(f"{d}: {p.name} is not a sitting record (NNNN_signed_<kind>_<build16>.json)")
    nums = [int(NAME.match(p.name).group(1)) for p in files]
    if nums != list(range(1, len(files) + 1)):
        raise Fail(f"{d}: record numbers are {nums}, not 1..{len(files)} with no gaps")
    return files


def new_state():
    return {"tier": {}, "clarity": {}, "holdings": {}, "flags": {}, "sittings": []}


def apply(state, signed):
    """Mutates state by one signed record (ADR-0006 R1 section 3)."""
    kind = signed.get("kind")
    if kind not in KINDS:
        raise Fail(f"plumb-line merge: record kind {kind!r} is not one of {list(KINDS)}")
    b16 = str(signed["build_hash"])[:16]
    src = f"source/plumb-line/sitting-{b16}"
    day = str(signed["signature"].get("date") or "")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
        raise Fail(f"plumb-line: signature date {day!r} is not YYYY-MM-DD")
    notes = {k: [] for k in NOTE_KEYS}
    replaced = sha(render(state)) if state["sittings"] else sha(b"")
    flag_rows, pos_flag_keys = [], set()
    for r in signed["rows"]:
        rid = r["row_id"]
        vals = {f["id"]: f["value"] for f in r["fields"]}
        fids = [f["id"] for f in r["fields"]]
        if fids == ["v"]:
            notes["not_data"].append(rid)
            continue
        if r["state"] != "verdict":
            notes["abstain_fault"].append(rid)
            continue
        if rid.endswith(".locus"):
            locus = rid[:-len(".locus")]
            ingest.slug_ok(locus)
            for fid, allowed, store in (("tier", ingest.TIERS, state["tier"]),
                                        ("clarity", ingest.CLARITIES, state["clarity"])):
                v = vals.get(fid)
                if ingest.is_other(v):
                    notes["other"].append(f"{rid}.{fid}")
                    continue
                if v is None:
                    continue
                ingest.choice(v, allowed, fid)
                if locus in store and store[locus][0] == v:
                    continue
                store[locus] = (v, src)
            continue
        if rid.startswith("unchurches."):
            locus, _, pos = rid[len("unchurches."):].partition(".")
            ingest.slug_ok(locus, pos)
            flag_rows.append((rid, locus, pos, vals.get("unchurches")))
            continue
        locus, _, pos = rid.partition(".")
        ingest.slug_ok(locus, pos)
        key = (locus, pos)
        m = vals.get("modality")
        has_flag = "unchurches" in fids
        raw = vals.get("unchurches") or []
        ticked = False
        if has_flag:
            pos_flag_keys.add(key)
            items = raw if isinstance(raw, list) else [raw]
            if any(ingest.is_other(x) for x in items):
                notes["other"].append(f"{rid}.unchurches")
            ticked = "unchurches" in [x for x in items if not ingest.is_other(x)]
        if ingest.is_other(m):
            notes["other"].append(f"{rid}.modality")
            continue
        if m is None:
            notes["unanswered"].append(rid)
            if ticked:
                raise Fail(f"plumb-line: {rid} unchurches ticked but modality is unanswered; "
                           "only forbidden may be flagged (ADR-0003 R2.3)")
            continue
        if m == "silent":
            if state["holdings"].pop(key, None):
                notes["silent_removed"].append(rid)
            else:
                notes["silent_nothing"].append(rid)
            state["flags"].pop(key, None)
            continue
        ingest.choice(m, ingest.MODALITIES, "modality")
        held = state["holdings"].get(key)
        if not (held and held[0] == m):
            state["holdings"][key] = (m, src, day)
        if has_flag:
            if ticked:
                if m != "forbidden":
                    raise Fail(f"plumb-line: {rid} unchurches ticked but modality is {m!r}; "
                               "only forbidden may be flagged (ADR-0003 R2.3)")
                state["flags"].setdefault(key, src)
            else:
                state["flags"].pop(key, None)
    for rid, locus, pos, v in flag_rows:
        key = (locus, pos)
        if key in pos_flag_keys:
            raise Fail(f"plumb-line: {rid} and the Position row both carry the unchurches flag in one record")
        if ingest.is_other(v):
            notes["other"].append(rid)
        elif v == "confirm":
            if key in state["holdings"]:
                state["flags"].setdefault(key, src)
            else:
                notes["flags_not_written"].append(rid)
        elif v == "withdraw":
            state["flags"].pop(key, None)
        elif v is not None:
            raise Fail(f"plumb-line: {rid}: unchurches {v!r} is not confirm or withdraw")
    for (locus, pos) in state["flags"]:
        if state["holdings"].get((locus, pos), (None,))[0] != "forbidden":
            raise Fail(f"plumb-line: unchurches on {locus}/{pos}, whose holding is not forbidden (ADR-0003 R2.3)")
        if state["tier"].get(locus, (None,))[0] == "third":
            raise Fail(f"plumb-line: unchurches on {locus}/{pos}, a tier-third locus (ADR-0003 R2.3)")
    state["sittings"].append({"build16": b16, "kind": kind, "day": day, "export_sha256": signed["export_sha256"],
                              "replaced_sha256": replaced, "notes": notes})


def _status(day):
    return ("gc:status <vocab/status/ratified> ; gc:proposedBy <agent/build-agent> ;\n"
            f'    gc:ratifiedBy <agent/chris> ; dcterms:dateAccepted "{day}"^^xsd:date .')


def render(state):
    head = ingest.LOCI_HEADER + "@prefix owl: <http://www.w3.org/2002/07/owl#> ."
    com = ["# data/plumb-line.ttl is the product of replaying the signed sittings below, in order (ADR-0006 R1). "
           "Never edit by hand."]
    for n, s in enumerate(state["sittings"], 1):
        com.append(f"# {n:04d} sitting {s['build16']} ({s['kind']}), signed {s['day']}, export sha256 "
                   f"{s['export_sha256']}, replaced sha256 {s['replaced_sha256']}")
        for k, text in NOTE_TEXT:
            if s["notes"][k]:
                com.append(f"#   {text}: " + ", ".join(s["notes"][k]))
    loci = []
    for locus in sorted(set(state["tier"]) | set(state["clarity"])):
        bits = ([f"gc:tier <vocab/tier/{state['tier'][locus][0]}>"] if locus in state["tier"] else []) + \
               ([f"gc:clarity <vocab/clarity/{state['clarity'][locus][0]}>"] if locus in state["clarity"] else [])
        loci.append(f"<locus/{locus}> " + " ; ".join(bits) + " .")
    keys = sorted(state["holdings"], key=lambda k: f"holding/plumb-line/{k[0]}/{k[1]}")
    holds = [f"<body/plumb-line> gc:holds <holding/plumb-line/{l}/{p}> ." for l, p in keys]
    holdings = []
    for l, p in keys:
        m, src, day = state["holdings"][(l, p)]
        holdings.append(f"<holding/plumb-line/{l}/{p}> a gc:Holding ; gc:position <position/{l}/{p}> ;\n"
                        f"    gc:modality <vocab/modality/{m}> ; dcterms:source <{src}> ;\n    " + _status(day))
    flags = [f"<position/{l}/{p}> gc:unchurches true ." for l, p in sorted(state["flags"])]
    axioms = {}

    def ax(iri, source, prop, target, src):
        b16 = src.rsplit("sitting-", 1)[1]
        axioms[iri] = (f"<{iri}> a owl:Axiom ; owl:annotatedSource <{source}> ; owl:annotatedProperty {prop} ; "
                       f"owl:annotatedTarget {target} ;\n    dcterms:source <{src}> ; "
                       f'rdfs:comment "Set by plumb-line sitting {b16} (ADR-0006 R1)."@en .')
    for locus, (t, src) in state["tier"].items():
        ax(f"axiom/tier/{locus}/to/{t}", f"locus/{locus}", "gc:tier", f"<vocab/tier/{t}>", src)
    for locus, (c, src) in state["clarity"].items():
        ax(f"axiom/clarity/{locus}/to/{c}", f"locus/{locus}", "gc:clarity", f"<vocab/clarity/{c}>", src)
    for (l, p), src in state["flags"].items():
        ax(f"axiom/unchurches/{l}/{p}/to/true", f"position/{l}/{p}", "gc:unchurches", "true", src)
    divs = [f'<source/plumb-line/sitting-{s["build16"]}> a gc:SourceDivision ; dcterms:isPartOf <source/plumb-line> ;\n'
            f'    dcterms:identifier "{s["export_sha256"]}" ;\n    ' + _status(s["day"]) for s in state["sittings"]]
    blocks = [head, "\n".join(com), "\n".join(loci), "\n".join(holds), "\n".join(holdings),
              ("\n".join(["# unchurches (ADR-0003 R2.3)"] + flags) if flags else ""),
              "\n".join(axioms[k] for k in sorted(axioms)), "\n".join(divs)]
    return ("\n\n".join(b for b in blocks if b) + "\n").encode("utf-8")


def replay(records):
    state = new_state()
    for s in records:
        apply(state, s)
    return render(state)


def merge(signed, ttl_path, records_dir):
    """(record_path, record_bytes, ttl_bytes); Fails before anything is written."""
    ttl_path, records_dir = Path(ttl_path), Path(records_dir)
    paths = record_paths(records_dir)
    records = [json.loads(p.read_bytes().decode("utf-8")) for p in paths]
    if ttl_path.exists():
        if replay(records) != ttl_path.read_bytes():
            raise Fail("data/plumb-line.ttl differs from the replay of its records: hand edit or a missing "
                       "record; nothing merged")
    elif records:
        raise Fail(f"{ttl_path} is missing but {len(records)} records exist; nothing merged")
    b16 = str(signed["build_hash"])[:16]
    if any(NAME.match(p.name).group(3) == b16 for p in paths):
        raise Fail(f"sitting {b16} is already a record in {records_dir}; nothing merged")
    kind = signed.get("kind")
    ttl_bytes = replay(records + [signed])
    rec = records_dir / f"{len(paths) + 1:04d}_signed_{kind}_{b16}.json"
    rec_bytes = json.dumps(signed, ensure_ascii=False, sort_keys=True, indent=1).encode("utf-8")
    return rec, rec_bytes, ttl_bytes
