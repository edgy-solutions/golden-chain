"""The single ingest path (ADR-0001): TTL -> parse -> SHACL -> code checks -> TDB2; derive by SPARQL."""

import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pyshacl
import rdflib
from rdflib import Dataset, Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, SH

from goldenchain import jena, passage

B = "https://w3id.org/golden-chain/"
GC = Namespace(B + "ontology#")
ROOT = Path(__file__).resolve().parent.parent
ONTOLOGY = ROOT / "ontology"
REASONER = ROOT / "reasoner"
FUSEKI = ROOT / "fuseki"
DB = FUSEKI / "databases" / "gc"
RUN = FUSEKI / "run"
PLUMB_LINE = URIRef(B + "graph/plumb-line")
DERIVED = [URIRef(B + "graph/derived/inheritance"), URIRef(B + "graph/derived/consistency")]


class IngestError(RuntimeError):
    pass


def data_root(data_dir=None) -> Path:
    """Repo data/ by default; override by argument or GOLDEN_CHAIN_DATA."""
    return Path(data_dir or os.environ.get("GOLDEN_CHAIN_DATA") or ROOT / "data")


def input_files(data_dir=None) -> list[Path]:
    d = data_root(data_dir)
    return [ONTOLOGY / "core.ttl", ONTOLOGY / "vocab.ttl", *sorted(d.glob("*.ttl"))]


def graph_name(path: Path) -> URIRef:
    return URIRef(B + "graph/" + path.stem)


def load_dataset(data_dir=None) -> Dataset:
    ds = Dataset()
    for f in input_files(data_dir):
        ds.graph(graph_name(f)).parse(f, format="turtle")  # parse errors raise
    return ds


def union(ds: Dataset) -> Graph:
    g = Graph()
    for ng in ds.graphs():
        for t in ng:
            g.add(t)
    return g


def shacl_report(data: Graph):
    """SHACL over one data graph. Returns (violations, warnings) as lists of (focus, path, message)."""
    shapes = Graph().parse(ONTOLOGY / "shapes.ttl", format="turtle")
    _, rg, _ = pyshacl.validate(
        data, shacl_graph=shapes, advanced=True, allow_warnings=True, inference="none"
    )
    violations, warnings = [], []
    for r in rg.subjects(RDF.type, SH.ValidationResult):
        row = (
            rg.value(r, SH.focusNode),
            rg.value(r, SH.resultPath),
            str(rg.value(r, SH.resultMessage) or ""),
        )
        (warnings if rg.value(r, SH.resultSeverity) == SH.Warning else violations).append(row)
    return violations, warnings


def validate(ds: Dataset):
    """SHACL over the union of all graphs. Returns (violations, warnings); raises on any violation."""
    violations, warnings = shacl_report(union(ds))
    if violations:
        raise IngestError(
            f"{len(violations)} SHACL violation(s):\n"
            + "\n".join(f"  {f} {p} {m}" for f, p, m in violations[:50])
        )
    return violations, warnings


def code_checks(ds: Dataset) -> None:
    """Checks that SHACL cannot express; raise listing every offender."""
    u = union(ds)
    errs: list[str] = []
    props = {
        GC.versification: lambda p: p.v11n,
        GC.book: lambda p: p.book,
        GC.osisRef: lambda p: p.osis,
        GC.startOrdinal: lambda p: p.start_ordinal,
        GC.endOrdinal: lambda p: p.end_ordinal,
    }
    passages = set(u.subjects(RDF.type, GC.Passage))
    for iri in sorted(passages):
        try:
            p = passage.parse(str(iri))
        except ValueError as e:
            errs.append(f"a. {iri}: {e}")
            continue
        for pred, getter in props.items():
            vals = {o.toPython() if isinstance(o, Literal) else o for o in u.objects(iri, pred)}
            if vals != {getter(p)}:
                errs.append(
                    f"a. {iri}: {pred.split('#')[1]} is {sorted(map(str, vals))}, expected {getter(p)!r}"
                )
    for pred in (GC.cites, GC.citesCandidate):
        for s, o in u.subject_objects(pred):
            if o not in passages:
                errs.append(f"b. {s} {pred.split('#')[1]} {o}: object is not typed gc:Passage")
    for pred in (GC.tier, GC.clarity):
        for ng in ds.graphs():
            if ng.identifier == PLUMB_LINE:
                continue
            for s, o in ng.subject_objects(pred):
                errs.append(f"c. {s} {pred.split('#')[1]} {o} asserted in {ng.identifier}, not plumb-line")
    if errs:
        raise IngestError(f"{len(errs)} code-check failure(s):\n" + "\n".join(errs))


def rule_files() -> list[Path]:
    return sorted(REASONER.glob("*.ru"))


def derive_rdflib(ds: Dataset) -> Dataset:
    """Run reasoner/*.ru in filename order over a union-default copy of ds."""
    out = Dataset(default_union=True)
    for ng in ds.graphs():
        if ng.identifier in DERIVED:
            continue
        g = out.graph(ng.identifier)
        for t in ng:
            g.add(t)
    for f in rule_files():
        out.update(f.read_text(encoding="utf-8"))
    return out


def build_tdb2(data_dir=None, ds: Dataset | None = None) -> None:
    ds = ds if ds is not None else load_dataset(data_dir)
    RUN.mkdir(parents=True, exist_ok=True)
    log = RUN / "tdb2.log"
    log.write_bytes(b"")
    trig = RUN / "gc.trig"
    trig.write_bytes(ds.serialize(format="trig", encoding="utf-8"))
    if DB.exists():
        shutil.rmtree(DB)
    DB.parent.mkdir(parents=True, exist_ok=True)
    jena.run_tool("tdb2.tdbloader", ["--loc", str(DB), str(trig)], ROOT, log)
    for f in rule_files():
        jena.run_tool(
            "tdb2.tdbupdate",
            ["--loc", str(DB), "--set", "tdb:unionDefaultGraph=true", "--update", str(f)],
            ROOT,
            log,
        )


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _git(*args: str) -> str:
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else "unknown"


def header(data_dir, n_violations: int, n_warnings: int) -> dict:
    files = [*input_files(data_dir), ONTOLOGY / "shapes.ttl", *rule_files(), FUSEKI / "config.ttl"]
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_head": _git("rev-parse", "HEAD"),
        "git_dirty": bool(_git("status", "--porcelain")),
        "python": platform.python_version(),
        "rdflib": rdflib.__version__,
        "pyshacl": pyshacl.__version__,
        "jena": jena.jena_version(),
        "inputs_sha256": {
            str(f.relative_to(ROOT) if ROOT in f.parents else f): _sha(f) for f in files
        },
        "violations": n_violations,
        "warnings": n_warnings,
    }


def ingest(data_dir=None) -> dict:
    ds = load_dataset(data_dir)
    violations, warnings = validate(ds)
    code_checks(ds)
    build_tdb2(data_dir, ds)
    h = header(data_dir, len(violations), len(warnings))
    RUN.mkdir(parents=True, exist_ok=True)
    (RUN / "ingest-header.json").write_text(json.dumps(h, indent=2), encoding="utf-8")
    print(json.dumps(h, indent=2))
    return h


def main() -> int:
    try:
        ingest()
    except Exception as e:  # noqa: BLE001 - report any failure, exit non-zero
        print(f"INGEST FAILED: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
