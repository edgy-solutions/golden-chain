"""gc:unchurches derivation (ADR-0003 R2.3 / R2.7): which Bodies are not churches by the plumb-line's standard.

Pure functions over an rdflib graph or dataset (union view) that already carries the derived
inheritance graph (gc:effectivelyHolds, from ingest.derive_rdflib; reasoner/10-inheritance.ru:
a Body's own Holdings on a Locus override its parent's). This module reads only
gc:effectivelyHolds, so a section-6 derived stance can never trigger exclusion.
"""

from rdflib import URIRef
from rdflib.namespace import DCTERMS, RDF

from goldenchain.ingest import B, GC

PLUMB_BODY = URIRef(B + "body/plumb-line")
TRIGGER = {URIRef(B + f"vocab/modality/{m}") for m in ("required", "taught", "tolerated")}

_CONF = "churches subscribing to this standard are not churches by this plumb-line's standard."
_SYS = "teaches what, where practised, makes a body no church by this plumb-line's standard."
WORDING = {
    "Congregation": "not a church by this plumb-line's standard.",
    "Denomination": "not a church by this plumb-line's standard.",
    "Confession": _CONF,
    "Catechism": _CONF,
    "Collection": _CONF,
    "Systematic": _SYS,
    "Teacher": _SYS,
}
HEADING = "Not a church by this plumb-line's standard"
MEMBERS = "Its members' standing as Christians is not asserted either way."


def flagged(g) -> set[URIRef]:
    return set(g.subjects(GC.unchurches, None))


def excluded(g) -> dict[URIRef, list[dict]]:
    flags = flagged(g)
    out: dict[URIRef, list[dict]] = {}
    for b in set(g.subjects(GC.effectivelyHolds, None)) - {PLUMB_BODY}:
        rows = []
        for h in g.objects(b, GC.effectivelyHolds):
            pos = g.value(h, GC.position)
            mod = g.value(h, GC.modality)
            if pos in flags and mod in TRIGGER:
                rows.append({
                    "holding": h,
                    "position": pos,
                    "modality": mod,
                    "source": g.value(h, DCTERMS.source),
                    "own": (b, GC.holds, h) in g,
                })
        if rows:
            out[b] = sorted(rows, key=lambda r: str(r["holding"]))
    return out


def wording(g, body) -> str:
    ns = str(GC)
    classes = sorted(str(c)[len(ns):] for c in g.objects(body, RDF.type) if str(c).startswith(ns))
    for name in classes:
        if name in WORDING:
            return WORDING[name]
    raise ValueError(f"{body} has no wording: its gc classes are {classes}")


def flag_source(g, position):
    for h in g.objects(PLUMB_BODY, GC.holds):
        if (h, GC.position, position) in g:
            return g.value(h, DCTERMS.source)
    return None
