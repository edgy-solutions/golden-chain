"""Weigh Bodies against the plumb-line as a user (ADR-0003 section 5, 5a, 7, R2.3, R2.4, R2.5, R2.7).

Pure functions over a graph that carries gc:effectivelyHolds (ingest.derive_rdflib output, or its
union). Exclusion (R2.3) is delegated to goldenchain.unchurches, which reads only
gc:effectivelyHolds, so a section-6 derived stance can never trigger it. Exclusion is computed
before walls and cost; an excluded Body is not scored.

Readings applied (each is also a comment where it is used):
 1. The user is body/plumb-line; its Holdings are user stances through USER_OF (section 5a).
    Silent or any other modality writes no stance. Deprecated loci are skipped.
 2. Locus weight is TIER_W[tier] * CLARITY_W[clarity]; a locus lacking either is "untiered":
    listed, and in neither cost nor coverage.
 3. A Body's cell on a Position is the max over its effective Holdings there whose gc:scope
    (or none) is in SCOPES[scope]; WALL is above every number; none means unknown.
 4. A locus is covered when at least one of its stance Positions has a known cell (R2.4).
 5. C(L) is the max over known cells. Open loci (w == 0) are never a wall or break and are in
    neither cost nor coverage.
 6. A wall locus is covered, has w > 0 and C == WALL; it is not in the cost sum.
 7. Cost = sum(w*C) / sum(w*MAX_CELL) over covered, non-wall loci with w > 0; None if none.
 8. Coverage = sum(w over covered loci, w > 0) / sum(w over stance loci, w > 0); None if 0.
 9. A break (R2.3, R2.7 (4)) is a covered locus with w > 0 whose C is WALL or >= 0.25.
10. Ranking key: (wall count, cost is None, cost, str(body)).
"""

import argparse

from rdflib import Literal, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS, XSD

from goldenchain import ingest, unchurches
from goldenchain.ingest import B, GC

WALL = "WALL"
CELL = {
    "obligatory": {"required": 0, "taught": 0, "tolerated": 0.25, "forbidden": WALL},
    "permitted": {"required": 0.1, "taught": 0, "tolerated": 0, "forbidden": 0.05},
    "forbidden": {"required": WALL, "taught": 0.75, "tolerated": 0.5, "forbidden": 0},
}
USER_OF = {"required": "obligatory", "taught": "obligatory", "tolerated": "permitted",
           "forbidden": "forbidden"}
TIER_W = {"first": 9, "second": 3, "third": 1}
CLARITY_W = {"open": 0, "contested": 1, "settled": 1}
MAX_CELL = 0.75
SCOPES = {
    "members": {None, URIRef(B + "vocab/scope/all"), URIRef(B + "vocab/scope/members")},
    "officers": {None, URIRef(B + "vocab/scope/all"), URIRef(B + "vocab/scope/officers")},
}
PLUMB = unchurches.PLUMB_BODY
# Ruled consequence wording, shown under a WALL cell on the Position (ruling on report 13, item 7).
CONSEQUENCE = {
    URIRef(B + "position/baptism-validity/church-of-our-order"):
        "requires the baptism of one already validly baptized (repetition)",
}


# ADR-0007 C6: the fixed wording every Congregation page carries for how the church may correct it.
CORRECTION = ("The church may correct this page by writing to the maintainers of Golden Chain. "
              "A correction is read against the church's own statement, signed, and then replaces the entry; "
              "until then the entry stands as proposed.")
NOT_RECORDED = "not recorded"


def rel(iri) -> str:
    return str(iri)[len(B):] if str(iri).startswith(B) else str(iri)


def tail(iri) -> str:
    return str(iri).rsplit("/", 1)[-1]


def _num(v) -> float:
    return 1e9 if v == WALL else v


def _deprecated(g, locus) -> bool:
    return any(str(o).lower() in ("true", "1") for o in g.objects(locus, OWL.deprecated))


def _stance_mods(g) -> tuple[dict, dict]:
    """The plumb-line as a user (5a): stance[locus][position] = user modality; plumb_mod[position]."""
    stance: dict = {}
    plumb_mod: dict = {}
    for h in g.objects(PLUMB, GC.holds):
        mod = g.value(h, GC.modality)
        pos = g.value(h, GC.position)
        if mod is None or pos is None or tail(mod) not in USER_OF:
            continue
        locus = g.value(pos, GC.answers)
        if locus is None or _deprecated(g, locus):
            continue
        stance.setdefault(locus, {})[pos] = USER_OF[tail(mod)]
        plumb_mod[pos] = tail(mod)
    return stance, plumb_mod


def stances(g) -> dict:
    return _stance_mods(g)[0]


def _weight(g, locus):
    tier, clarity = g.value(locus, GC.tier), g.value(locus, GC.clarity)
    if tier is None or clarity is None or tail(tier) not in TIER_W or tail(clarity) not in CLARITY_W:
        return None, None
    return TIER_W[tail(tier)] * CLARITY_W[tail(clarity)], tail(tier)


def _cell(g, body, pos, user, scope):
    """(value, body_mod_tail) of the max cell for body on pos, or None when unknown."""
    best = None
    for h in g.objects(body, GC.effectivelyHolds):
        if (h, GC.position, pos) not in g:
            continue
        if g.value(h, GC.scope) not in SCOPES[scope]:
            continue
        mod = g.value(h, GC.modality)
        if mod is None or tail(mod) not in CELL[user]:
            continue
        c = (CELL[user][tail(mod)], tail(mod))
        if best is None or _num(c[0]) > _num(best[0]):
            best = c
    return best


def score(g, body, scope="members") -> dict:
    st, plumb_mod = _stance_mods(g)
    walls, breaks, untiered = [], [], []
    num = den = 0.0
    n_cost = 0
    cov_num = cov_den = 0.0
    for locus in sorted(st, key=str):
        w, tier = _weight(g, locus)
        if w is None:
            untiered.append(locus)
            continue
        if w == 0:
            continue  # open: scores 0, no verdict
        cov_den += w
        cells = {p: _cell(g, body, p, u, scope) for p, u in st[locus].items()}
        known = {p: c for p, c in cells.items() if c is not None}
        if not known:
            continue
        cov_num += w
        top = max((c[0] for c in known.values()), key=_num)
        if top == WALL:
            walls.append({"locus": locus, "tier": tier, "cells": sorted(
                [(p, c[1], plumb_mod[p]) for p, c in known.items() if c[0] == WALL],
                key=lambda t: str(t[0]))})
        else:
            num += w * top
            den += w * MAX_CELL
            n_cost += 1
        if top == WALL or top >= 0.25:
            breaks.append((locus, tier, top))
    return {"walls": walls, "cost": (num / den if n_cost else None), "n_cost": n_cost,
            "coverage": (cov_num / cov_den if cov_den else None), "breaks": breaks,
            "untiered": untiered}


def bodies(g) -> list:
    classes = {GC.Body} | set(g.transitive_subjects(RDFS.subClassOf, GC.Body))
    out = {s for c in classes for s in g.subjects(RDF.type, c)}
    return sorted(out - {PLUMB}, key=str)


def body_class(g, body) -> str:
    ns = str(GC)
    names = sorted(str(c)[len(ns):] for c in g.objects(body, RDF.type) if str(c).startswith(ns))
    for n in names:
        if n in unchurches.WORDING:
            return n
    for n in names:
        if n != "Body":
            return n
    return "Body"


def weigh(g, scope="members", only=None) -> dict:
    allowed = set(bodies(g))
    if only is not None:
        allowed &= set(only)
    exc = {b: r for b, r in unchurches.excluded(g).items() if b in allowed}
    scored = [(b, score(g, b, scope)) for b in sorted(allowed - set(exc), key=str)]
    scored.sort(key=lambda t: (len(t[1]["walls"]), t[1]["cost"] is None, t[1]["cost"] or 0.0, str(t[0])))
    return {"ranked": scored, "excluded": exc}


def _fmt(v) -> str:
    return "n/a" if v is None else f"{v:.4f}"


# ---- Congregations (ADR-0007 C6, C8): pure on the graph --------------------------------------------

def is_congregation(g, body) -> bool:
    return (body, RDF.type, GC.Congregation) in g


def _label(g, iri) -> str:
    v = g.value(iri, RDFS.label)
    return str(v) if v is not None else rel(iri)


def _exception_axioms(g, body, locus=None):
    for ax in g.subjects(OWL.annotatedSource, body):
        if ((ax, OWL.annotatedProperty, GC.exceptsLocus) in g
                and (locus is None or (ax, OWL.annotatedTarget, locus) in g)):
            yield ax


def _holder(g, holding):
    return next(iter(sorted(g.subjects(GC.holds, holding), key=str)), None)


def _own_cell(g, holding) -> str:
    src = g.value(holding, DCTERMS.source)
    if src is not None and (src, RDF.type, GC.PersonalKnowledge) in g:
        return "own (personal knowledge)"
    loc = g.value(holding, GC.locator)
    return f"own (statement, {loc})" if loc is not None else "own (statement)"


def cells(g, body) -> list:
    """[(locus, text)] for a Congregation: one entry per Locus where it has an effective Holding or an
    exception, in Locus IRI order; within a Locus inherited (by parent IRI), then own, then excepted.
    A Locus with Holdings from several parents gives one entry per parent."""
    found: dict = {}
    for h in g.objects(body, GC.effectivelyHolds):
        pos = g.value(h, GC.position)
        locus = g.value(pos, GC.answers) if pos is not None else None
        if locus is None:
            continue
        holder = _holder(g, h)
        if holder == body:
            found.setdefault(locus, set()).add((1, "", _own_cell(g, h)))
        else:
            who = rel(holder) if holder is not None else NOT_RECORDED
            found.setdefault(locus, set()).add((0, who, f"inherited from {who}"))
    for locus in g.objects(body, GC.exceptsLocus):
        found.setdefault(locus, set()).add((2, "", "excepted, unknown"))
    return [(locus, t[2]) for locus in sorted(found, key=str) for t in sorted(found[locus])]


def _source_text(g, src) -> str:
    if (src, RDF.type, GC.PersonalKnowledge) in g:
        who = g.value(src, DCTERMS.creator)
        return f"personal knowledge ({_label(g, who) if who is not None else NOT_RECORDED})"
    if (src, RDF.type, GC.SourceWork) in g:
        see = g.value(src, RDFS.seeAlso)
        read = g.value(src, GC.readOn)
        arch = g.value(src, GC.archivedCopy)
        return (f"{_label(g, src)} ({see if see is not None else NOT_RECORDED}, "
                f"read {read if read is not None else NOT_RECORDED}, "
                f"archived {arch if arch is not None else NOT_RECORDED})")
    return _label(g, src)


def congregation_header(g, body) -> list:
    """The lines after the first line of a Congregation page (ADR-0007 C6, C8)."""
    parents = sorted(g.objects(body, GC.childOf), key=str)
    lines = ["  subscribes to: " + "; ".join(f"{_label(g, p)} ({rel(p)})" for p in parents)]
    excepted = sorted(g.objects(body, GC.exceptsLocus), key=str)
    lines.append(f"  exceptions: {len(excepted)}")
    for locus in excepted:
        note = g.value(locus, SKOS.notation)
        lines.append("    - " + (f"{note} " if note is not None else "") + f"{_label(g, locus)} ({rel(locus)})")
    srcs = set(g.objects(body, DCTERMS.source))
    for h in g.objects(body, GC.holds):
        srcs |= set(g.objects(h, DCTERMS.source))
    for ax in _exception_axioms(g, body):
        srcs |= set(g.objects(ax, DCTERMS.source))
    by = g.value(body, GC.proposedBy)
    on = g.value(body, DCTERMS.created)
    lines.append(f"  entered by: {_label(g, by) if by is not None else NOT_RECORDED}, "
                 f"on {on if on is not None else NOT_RECORDED}, from: "
                 + ("; ".join(_source_text(g, x) for x in sorted(srcs, key=str)) or NOT_RECORDED))
    conf = g.value(body, GC.ratifiedBy)
    lines.append("  confirmed by: " + (_label(g, conf) if conf is not None
                                       else "not yet confirmed (every row here is proposed)"))
    lines.append("  correction: " + CORRECTION)
    return lines


def congregation_cells(g, body) -> list:
    return ["  cells:"] + [f"    - {rel(locus)}: {text}" for locus, text in cells(g, body)]


def render_body(g, body, scope="members") -> str:
    cls = body_class(g, body)
    exc = unchurches.excluded(g)
    cong = is_congregation(g, body)
    if body in exc:
        lines = [f"{rel(body)} [{cls}] not ranked"]
        if cong:
            lines += congregation_header(g, body)
        lines.append("  " + unchurches.HEADING + ": " + unchurches.wording(g, body))
        for r in exc[body]:
            fs = unchurches.flag_source(g, r["position"])
            line = (f"    - {rel(r['position'])} {tail(r['modality'])} "
                    f"({rel(r['source']) if r['source'] else 'no source'}); flagged by the "
                    f"plumb-line at {rel(fs) if fs else 'no source'}")
            if cong and not r["own"]:
                holder = _holder(g, r["holding"])
                line += " inherited from " + (rel(holder) if holder is not None else NOT_RECORDED)
            lines.append(line)
        lines.append("  " + unchurches.MEMBERS)
        if cong:
            lines += congregation_cells(g, body)
        return "\n".join(lines)
    s = score(g, body, scope)
    lines = [f"{rel(body)} [{cls}] ranked"]
    if cong:
        lines += congregation_header(g, body)
    lines.append(f"  walls: {len(s['walls'])}")
    for wl in s["walls"]:
        for pos, bm, pm in wl["cells"]:
            lines.append(f"    - {rel(wl['locus'])} (tier {wl['tier']}): {rel(pos)} {bm} "
                         f"against plumb-line {pm}")
            if pos in CONSEQUENCE:
                lines.append(f"      consequence: {CONSEQUENCE[pos]}")
    lines.append(f"  cost: {_fmt(s['cost'])} over {s['n_cost']} loci; coverage: {_fmt(s['coverage'])}")
    lines.append(f"  breaks: {len(s['breaks'])}")
    for locus, tier, v in s["breaks"]:
        lines.append(f"    - {rel(locus)} (tier {tier}): {v if v == WALL else format(v, 'g')}")
    if s["untiered"]:
        lines.append("  untiered: " + ", ".join(rel(l) for l in s["untiered"]))
    if cong:
        lines += congregation_cells(g, body)
    return "\n".join(lines)


def render(g, scope="members", only=None) -> str:
    res = weigh(g, scope, only)
    parts = [f"Weigh against body/plumb-line (scope {scope})", ""]
    blocks = [render_body(g, b, scope) for b, _ in res["ranked"]]
    parts.append("\n\n".join(blocks))
    if res["excluded"]:
        parts += ["", unchurches.HEADING, ""]
        parts.append("\n\n".join(render_body(g, b, scope) for b in sorted(res["excluded"], key=str)))
    return "\n".join(parts).rstrip("\n")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(prog="goldenchain.weigh")
    ap.add_argument("--scope", choices=sorted(SCOPES), default="members")
    ap.add_argument("--flag", action="append", default=[], metavar="locus/pos")
    a = ap.parse_args(argv)
    ds = ingest.load_dataset()
    pl = ds.graph(ingest.PLUMB_LINE)
    for f in a.flag:  # in memory only
        pl.add((URIRef(B + "position/" + f), GC.unchurches, Literal(True, datatype=XSD.boolean)))
    g = ingest.union(ingest.derive_rdflib(ds))
    if a.flag:
        print("PROJECTION (flags overlaid in memory, not in data): " + ", ".join(a.flag))
        print()
    print(render(g, a.scope))


if __name__ == "__main__":
    main()
