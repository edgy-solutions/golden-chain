"""Read-only local prototype of `examine` (locus pages) and `try` (passage pages) (ADR-0008).

Static HTML from the Jena store (or the rdflib mirror). Every page string is a label, a question,
a locator, an asPrinted, an osisRef, a vocabulary label or an IRI tail, plus a banner and fixed
headings. No rdfs:comment, gc:resolutionNote, gc:quotation, gc:derivedBy or other free text is
ever queried: the allow-list of predicates is the VALUES clause in QUERY.

Usage: examine_try.py [--out DIR] [--store tdb2|rdflib]
"""

import argparse
import hashlib
import html
import json
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT, ROOT / "tools"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from goldenchain import ingest, jena  # noqa: E402

B = ingest.B
G = str(ingest.GC)

BANNER = ("PROTOTYPE — local only, not deployed. Generated from the data at {head}; "
          "every line below is a label, a locator or a signed record.")
DASH = " — "
# ADR-0002 R3 / ruling on report 19 A-1: shown beside an asPrinted whose annotated axiom is still proposed.
UNCONFIRMED = "proposed reading, unconfirmed"
OWL = "http://www.w3.org/2002/07/owl#"

# The only predicates the tool ever reads. Free-text predicates are absent by construction.
QUERY = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX gc: <https://w3id.org/golden-chain/ontology#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT ?s ?p ?o (LANG(?o) AS ?lang) WHERE {
  VALUES ?p { rdf:type rdfs:label skos:prefLabel skos:notation gc:question gc:tier gc:clarity
              gc:unchurches gc:answers gc:source gc:supports gc:cites gc:citesCandidate
              gc:locator gc:secondaryLocator gc:asPrinted gc:osisRef gc:status gc:proposedBy
              gc:ratifiedBy gc:position gc:modality gc:scope gc:effectivelyHolds
              owl:annotatedSource owl:annotatedProperty owl:annotatedTarget }
  ?s ?p ?o .
}
ORDER BY ?s ?p ?o
"""

_ACTIVE = {"kind": None, "graph": None}


def use_store(kind: str, data_dir=None) -> None:
    """Select the store `select` queries: 'tdb2' (ingest.DB) or 'rdflib' (derived mirror)."""
    if kind == "tdb2":
        if not ingest.DB.exists():
            raise SystemExit(f"TDB2 store absent at {ingest.DB}: run python -m goldenchain.ingest first")
        _ACTIVE.update(kind="tdb2", graph=None)
    elif kind == "rdflib":
        _ACTIVE.update(kind="rdflib", graph=ingest.derive_rdflib(ingest.load_dataset(data_dir)))
    else:
        raise SystemExit(f"unknown store {kind!r}")


def _tdb2_select(sparql: str) -> list[dict[str, str]]:
    with tempfile.TemporaryDirectory() as td:
        qf = Path(td) / "q.rq"
        qf.write_text(sparql, encoding="utf-8")
        cmd = ["java", "-cp", str(jena.jena_home() / "lib") + "/*", "tdb2.tdbquery",
               "--loc", str(ingest.DB), "--set", "tdb:unionDefaultGraph=true",
               "--results=json", "--query", str(qf)]
        r = subprocess.run(cmd, capture_output=True, cwd=ROOT)
    if r.returncode:
        raise RuntimeError(f"tdb2.tdbquery failed ({r.returncode}): "
                           f"{r.stderr.decode('utf-8', 'replace')[-1500:]}")
    data = json.loads(r.stdout.decode("utf-8"))
    return [{k: v["value"] for k, v in b.items()} for b in data["results"]["bindings"]]


def select(sparql: str) -> list[dict[str, str]]:
    """The one data-access function: both stores run the same SPARQL text."""
    if _ACTIVE["kind"] == "tdb2":
        return _tdb2_select(sparql)
    if _ACTIVE["kind"] == "rdflib":
        rows = []
        for r in _ACTIVE["graph"].query(sparql):
            rows.append({str(v): str(r[v]) for v in r.labels if r[v] is not None})
        return rows
    raise RuntimeError("no store selected: call use_store first")


# ------------------------------------------------------------------ model

RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
RDFS_LABEL = "http://www.w3.org/2000/01/rdf-schema#label"
SKOS_PREF = "http://www.w3.org/2004/02/skos/core#prefLabel"
SKOS_NOTATION = "http://www.w3.org/2004/02/skos/core#notation"


def tail(iri: str) -> str:
    return iri.removeprefix(B)


def slug(iri: str) -> str:
    """IRI tail minus its class segment, filesystem-safe."""
    parts = tail(iri).split("/")
    s = "_".join(parts[1:] if len(parts) > 1 else parts)
    return re.sub(r"[^A-Za-z0-9._-]", "_", s)


class Model:
    def __init__(self, rows):
        self.v = defaultdict(lambda: defaultdict(list))  # s -> p -> [(o, lang)]
        for r in rows:
            self.v[r["s"]][r["p"]].append((r["o"], r.get("lang", "")))
        self.types = defaultdict(set)
        for s, ps in self.v.items():
            for o, _ in ps.get(RDF_TYPE, []):
                self.types[o].add(s)
        # (Argument, asPrinted string) pairs whose "read by" axiom is still proposed (ADR-0002 R3).
        self.unconfirmed = set()
        for ax in self.types.get(OWL + "Axiom", ()):
            if (self.one(ax, OWL + "annotatedProperty") == G + "asPrinted"
                    and self.one(ax, "status") == B + "vocab/status/proposed"):
                self.unconfirmed.add((self.one(ax, OWL + "annotatedSource"),
                                      self.one(ax, OWL + "annotatedTarget")))

    def vals(self, s, p):
        return sorted({o for o, _ in self.v[s].get(p if "://" in p else G + p, [])})

    def one(self, s, p):
        x = self.vals(s, p)
        return x[0] if x else None

    def label(self, iri):
        if iri is None:
            return None
        cands = []
        for rank, p in ((0, SKOS_PREF), (1, RDFS_LABEL)):
            for o, lang in self.v[iri].get(p, []):
                cands.append((rank, lang not in ("", "en"), o))
        return sorted(cands)[0][2] if cands else tail(iri)

    def of_type(self, name):
        return sorted(self.types.get(G + name, set()))


def collect(model: Model) -> dict:
    loci = model.of_type("Locus")
    positions = defaultdict(list)
    for p in model.of_type("Position"):
        for l in model.vals(p, "answers"):
            positions[l].append(p)
    args = defaultdict(list)
    cites = set()
    candidates = set()
    for a in model.of_type("Argument"):
        for pos in model.vals(a, "supports"):
            args[pos].append(a)
        for ps in model.vals(a, "cites"):
            cites.add((a, ps))
        for ps in model.vals(a, "citesCandidate"):
            candidates.add((a, ps))
    pos_locus = {p: l for l, ps in positions.items() for p in ps}
    held = defaultdict(lambda: defaultdict(set))  # position -> body -> holdings
    for body in sorted(s for s in model.v if G + "effectivelyHolds" in model.v[s]):
        for h in model.vals(body, "effectivelyHolds"):
            p = model.one(h, "position")
            if p in pos_locus:
                held[p][body].add(h)
    return {"loci": loci, "positions": positions, "args": args, "cites": sorted(cites),
            "candidates": sorted(candidates), "pos_locus": pos_locus, "held": held}


# ------------------------------------------------------------------ html

CSS = ("body{font:16px/1.5 system-ui,sans-serif;max-width:60rem;margin:1rem auto;padding:0 1rem}"
       ".banner{background:#fff3cd;border:1px solid #c9a227;padding:.5rem .75rem;margin-bottom:1rem}"
       "table{border-collapse:collapse}td,th{border:1px solid #888;padding:.25rem .5rem;text-align:left}"
       "li{margin:.4rem 0}footer{margin-top:2rem;font-size:.8rem;color:#555}")


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def page(title, body, head12, store_sha):
    return ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<title>{esc(title)}</title><style>{CSS}</style></head><body>\n"
            f"<div class=\"banner\">{esc(BANNER.format(head=head12))}</div>\n"
            f"{body}\n<footer>git HEAD {esc(head12)}; store sha256 {esc(store_sha)}</footer>\n"
            "</body></html>\n")


def locus_title(m, l):
    n = m.one(l, SKOS_NOTATION)
    return (f"{n} " if n else "") + m.label(l)


def as_printed(m, a):
    x = m.one(a, "asPrinted")
    if x is not None and (a, x) in m.unconfirmed:
        return f"{x} ({UNCONFIRMED})"
    return x


def arg_fields(m, a):
    def lab(p):
        x = m.one(a, p)
        return m.label(x) if x else None
    items = [("Source", lab("source")),
             ("Locator", m.one(a, "locator")),
             ("Secondary locator", m.one(a, "secondaryLocator")),
             ("As printed", as_printed(m, a)),
             ("Status", lab("status")),
             ("Proposed by", lab("proposedBy")),
             ("Ratified by", lab("ratifiedBy"))]
    return "; ".join(f"{k}: {esc(v)}" for k, v in items if v)


def passage_name(m, ps):
    return m.one(ps, "osisRef") or tail(ps)


def locus_page(m, c, l, with_page):
    out = [f"<h1>{esc(locus_title(m, l))}</h1>"]
    q = m.one(l, "question")
    if q:
        out.append(f"<p>{esc(q)}</p>")
    meta = [m.label(x) for x in (m.one(l, "tier"), m.one(l, "clarity")) if x]
    if meta:
        out.append(f"<p>{esc(' / '.join(meta))}</p>")
    out.append("<h2>Positions</h2>")
    poss = sorted(c["positions"].get(l, []))
    for p in poss:
        flag = " [unchurches]" if p in m.vals(B + "body/plumb-line", "unchurches") else ""
        out.append(f"<h3>{esc(m.label(p) + flag)}</h3>\n<h4>Arguments</h4>\n<ul>")
        for a in sorted(c["args"].get(p, [])):
            li = f"<li id=\"arg-{esc(slug(a))}\">{arg_fields(m, a)}"
            refs = [f"<a href=\"../try/{esc(slug(x))}.html\">{esc(passage_name(m, x))}</a>"
                    for x in m.vals(a, "cites") if x in with_page]
            refs += [f"{esc(passage_name(m, x))} (candidate)" for x in m.vals(a, "citesCandidate")]
            if refs:
                li += "; cites: " + ", ".join(refs)
            out.append(li + "</li>")
        out.append("</ul>")
    out.append("<h2>Holdings</h2>")
    bodies = sorted({b for p in poss for b in c["held"].get(p, {})})
    if bodies:
        out.append("<table><tr><th>Body</th>"
                   + "".join(f"<th>{esc(m.label(p))}</th>" for p in poss) + "</tr>")
        for b in bodies:
            cells = []
            for p in poss:
                parts = []
                for h in sorted(c["held"].get(p, {}).get(b, ())):
                    mod = m.one(h, "modality")
                    s = m.label(mod) if mod else tail(h)
                    sc = m.one(h, "scope")
                    if sc and sc != B + "vocab/scope/all":
                        s += f" ({m.label(sc)})"
                    parts.append(esc(s))
                cells.append("<td>" + "; ".join(parts) + "</td>")
            out.append(f"<tr><th>{esc(m.label(b))}</th>{''.join(cells)}</tr>")
        out.append("</table>")
    return "\n".join(out)


def try_page(m, c, ps, by_passage):
    out = [f"<h1>{esc(passage_name(m, ps))}</h1>"]
    lab = m.label(ps)
    if lab not in (tail(ps), passage_name(m, ps)):
        out.append(f"<p>{esc(lab)}</p>")
    out.append("<h2>Cited by</h2>")
    groups = defaultdict(list)
    for a in by_passage[ps]:
        for pos in m.vals(a, "supports"):
            groups[pos].append(a)
    for pos in sorted(groups):
        l = c["pos_locus"].get(pos)
        link = ""
        if l:
            link = DASH + f"<a href=\"../examine/{esc(slug(l))}.html\">{esc(locus_title(m, l))}</a>"
        out.append(f"<h3>{esc(m.label(pos))}{link}</h3>\n<ul>")
        for a in sorted(groups[pos]):
            out.append(f"<li data-pair=\"{esc(slug(a))}|{esc(slug(ps))}\">{arg_fields(m, a)}</li>")
        out.append("</ul>")
    return "\n".join(out)


# ------------------------------------------------------------------ build

def store_sha(kind, data_dir=None) -> str:
    if kind == "tdb2" or data_dir is None:
        p = ingest.RUN / "gc.trig"
        return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else "absent"
    h = hashlib.sha256()
    for f in ingest.input_files(data_dir):
        h.update(f.read_bytes())
    return h.hexdigest()


def build(out: Path, store: str = "tdb2", data_dir=None) -> dict:
    from column_rule import clean_run, git_state  # lazy: heavy imports
    out = Path(out)
    start = git_state(ingest.ROOT)
    use_store(store, data_dir)
    m = Model(select(QUERY))
    c = collect(m)
    head = start["commit"][:12]
    sha = store_sha(store, data_dir)

    by_passage = defaultdict(list)
    for a, ps in c["cites"]:
        by_passage[ps].append(a)
    with_page = sorted(by_passage)
    cand_only = sorted({ps for _, ps in c["candidates"]} - set(by_passage))

    names = {}
    for kind, iris in (("examine", c["loci"]), ("try", with_page)):
        for i in iris:
            k = (kind, slug(i))
            if k in names:
                raise RuntimeError(f"slug collision {k}: {names[k]} and {i}")
            names[k] = i

    files = {}
    idx = ["<h1>Index</h1>", "<h2>Loci</h2>", "<ul>"]
    for l in c["loci"]:
        idx.append(f"<li><a href=\"examine/{esc(slug(l))}.html\">{esc(locus_title(m, l))}</a></li>")
    idx += ["</ul>", "<h2>Passages</h2>", "<ul>"]
    for ps in with_page:
        idx.append(f"<li><a href=\"try/{esc(slug(ps))}.html\">{esc(passage_name(m, ps))}</a></li>")
    idx.append("</ul>")
    files["index.html"] = page("Index", "\n".join(idx), head, sha)
    wp = set(with_page)
    for l in c["loci"]:
        files[f"examine/{slug(l)}.html"] = page(locus_title(m, l), locus_page(m, c, l, wp), head, sha)
    for ps in with_page:
        files[f"try/{slug(ps)}.html"] = page(passage_name(m, ps), try_page(m, c, ps, by_passage),
                                             head, sha)
    for rel in sorted(files):
        p = out / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(files[rel].encode("utf-8"))

    end = git_state(ingest.ROOT)
    summary = {
        "pages": {"index": 1, "examine": len(c["loci"]), "try": len(with_page)},
        "positions": sum(len(v) for v in c["positions"].values()),
        "arguments": len({a for p in c["pos_locus"] for a in c["args"].get(p, [])}),
        "holdings": sum(len(hs) for p in c["held"].values() for hs in p.values()),
        "cites_rows": len(c["cites"]),
        "candidate_only_passages": len(cand_only),
    }
    header = {"git_head": start["commit"], "store": store, "store_sha256": sha,
              "clean_run": clean_run(start, end), "summary": summary}
    (out / "run_header.json").write_text(json.dumps(header, indent=2, sort_keys=True) + "\n",
                                         encoding="utf-8", newline="\n")
    return summary


def default_out() -> Path:
    return Path.home() / ".golden-chain" / "prototype" / ingest._git("rev-parse", "HEAD")[:12]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--store", choices=["tdb2", "rdflib"], default="tdb2")
    a = ap.parse_args(argv)
    summary = build(a.out or default_out(), a.store)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
