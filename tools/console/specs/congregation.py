"""Spec builder, instance (vi): the congregation form (ADR-0007, as locked 2026-11-22: C7).

Usage: python tools/console/specs/congregation.py --parent body/<slug> [--parent body/<slug> ...] <out-spec.json>

One form per church. The parents (one or more Bodies already in the data) are given when the form is built. The
rows are generated from the data, read as weigh reads it (goldenchain.ingest.load_dataset, derive_rdflib, union):
every Locus and Position, every parent and every modality and scope by rdfs:label (skos:prefLabel for the
vocabularies). No row text is written by a model: the question and plain-words wording is fixed and is the same
for every church (ADR-0006 Revision 4).

Church section: name; basis (its published statement / personal knowledge only); statement title, URL, read date,
archived URL; and the parents row (where the statement names them).
Per Locus where any parent has an effective Holding: one row showing each parent's Position(s). If the speaking
parents agree it offers "as the parents", "excepts: holds another" and "excepts: no alternative stated"; if they
differ, "holds this one", "excepts: no alternative stated" and "says nothing: keeps both" (mints nothing). Per Locus where every parent is silent: one row,
"own" (empty means unanswered). The optional fields (instead, modality, scope, basis, where) are required: false;
tools/console/ingest.py checks the conditions for this kind.
The spec records the parents' IRIs, each row's Locus IRI and each option's IRI, so ingest mints from IRIs.
It reads the real data only when run by hand, and writes only the spec file named.
"""

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import build  # noqa: E402
from build import Fail  # noqa: E402

sys.path.insert(0, str(build.REPO))
from rdflib import RDF, RDFS, URIRef  # noqa: E402
from rdflib.namespace import OWL, SKOS  # noqa: E402

from goldenchain import ingest as gc_ingest  # noqa: E402
from goldenchain import weigh  # noqa: E402
from goldenchain.ingest import B, GC  # noqa: E402

OTHER = build.OTHER
SCOPE_ALL = URIRef(B + "vocab/scope/all")
B_STATEMENT, B_PERSONAL = "its published statement", "personal knowledge only"
ROW_STATEMENT, ROW_PERSONAL = "the church's statement", "personal knowledge"
A_AS, A_ANOTHER, A_NONE, A_THIS = "as the parents", "excepts: holds another", "excepts: no alternative stated", "holds this one"
A_KEEP = "says nothing: keeps both"
A_AS_ONE = "as the parent"
# Option -> code, recorded on the answer field so ingest never reads wording.
CODES = {A_AS: "as-parents", A_AS_ONE: "as-parents", A_ANOTHER: "holds-another", A_THIS: "holds-this",
         A_NONE: "no-alternative", A_KEEP: "keeps-both"}
MOD_ORDER = ["required", "taught", "tolerated", "forbidden"]
SCOPE_ORDER = ["all", "officers", "members"]
NONE_FIT = 'If none fits, choose "other, as written" and say what you mean.'
LEAVE_EMPTY_P = "Leave it empty if you chose personal knowledge only."

INSTRUCTION = ("One form per church. Say who the church is and where its own words are, then, for each question, "
               "whether the church holds what the Body or Bodies it subscribes to hold, holds something else, or "
               "states nothing in their place. Only what the church publishes is used, unless you choose personal "
               "knowledge, which is shown as that. No person is named. Nothing is written to the data until you "
               "sign; everything written is marked proposed until a named person confirms it.")
SECTION_TEXT = {
    "church": "The church and where its statement is. Every answer here is about the church as a whole.",
    "parents-speak": ("The questions on which the Body or Bodies the church subscribes to have a position. "
                      "Each shows what they hold."),
    "parents-silent": ("The questions on which none of those Bodies has a position. Answer only where the church's "
                       "statement or your own knowledge takes one; leave the rest empty."),
}
HELP = [
    {"q": "What does excepts mean?",
     "a": "The church holds what its parents hold on every question except the ones you mark. A question marked "
          "\"excepts: no alternative stated\" is shown as unknown, not as tolerated: the church is not recorded as "
          "holding the parents' position, and nothing is recorded in its place."},
    {"q": "What if I leave a question as the parents?",
     "a": "Choose \"as the parents\" and leave the fields below it empty. Nothing is written for that question; the "
          "church inherits."},
    {"q": "What is personal knowledge?",
     "a": "What you know of the church that its published statement does not say. It is written and shown as personal "
          "knowledge, with you named as its source, and is proposed until a named person confirms it."},
]


def tail(iri):
    return str(iri).rsplit("/", 1)[1]


def label(g, iri, pred=RDFS.label):
    v = g.value(iri, pred)
    if v is None and pred == RDFS.label:
        v = g.value(iri, SKOS.prefLabel)
    if v is None:
        raise Fail(f"{iri} has no label in the data")
    return str(v)


def notation_key(n):
    m = re.fullmatch(r"(\d+)([a-z]*)", n or "")
    return (0, int(m.group(1)), m.group(2)) if m else (1, 0, n or "")


def vocab(g, scheme, order):
    """[(label, iri)] of the concepts of a skos scheme, in `order` by IRI tail, then any others by IRI."""
    items = sorted(g.subjects(SKOS.inScheme, URIRef(B + scheme)), key=str)
    items.sort(key=lambda i: (order.index(tail(i)) if tail(i) in order else len(order), str(i)))
    return [(label(g, i, SKOS.prefLabel), i) for i in items]


def definitions(g, scheme, order):
    out = []
    for lab, i in vocab(g, scheme, order):
        d = g.value(i, SKOS.definition)
        if d is not None:
            out.append(f"{lab}: {d}")
    return " ".join(out)


def check_unique(labels, what):
    if len(set(labels)) != len(labels):
        raise Fail(f"{what}: two options share a label: {sorted(labels)}")


def names(opts):
    return ", ".join(f'"{o}"' for o in opts)


def parent_cells(g, parent):
    """{locus: {(position, modality, scope)}} of a parent's effective Holdings."""
    out = {}
    for h in g.objects(parent, GC.effectivelyHolds):
        pos, mod = g.value(h, GC.position), g.value(h, GC.modality)
        locus = g.value(pos, GC.answers) if pos is not None else None
        if locus is None or mod is None:
            continue
        out.setdefault(locus, set()).add((pos, mod, g.value(h, GC.scope) or SCOPE_ALL))
    return out


def text_field(fid, lab, plain, required=False):
    return {"id": fid, "kind": "text", "label": lab, "required": required, "proposed": None, "plain": plain}


def choice(fid, kind, lab, options, iris, plain, required=False, **kw):
    check_unique(options, f"field {fid}")
    f = {"id": fid, "kind": kind, "label": lab, "options": list(options), "required": required, "proposed": None,
         "plain": plain, **kw}
    if iris:
        f["iris"] = {o: str(iris[o]) for o in options}
    return f


def church_section(parents, plabels):
    one = len(parents) == 1
    name = [text_field("name", "Public name and place", "Write the church's public name and place, as it appears on "
                       "its own published page. Do not name any person.", True)]
    basis = [choice("basis", "radio", "Where the church's words come from", [B_STATEMENT, B_PERSONAL], None,
                    f'Choose "{B_STATEMENT}" if the church has a public statement of faith you can cite, or '
                    f'"{B_PERSONAL}" if you know what it holds but it has no public statement. {NONE_FIT}', True)]
    stmt = [text_field("title", "Statement title",
                       f"Write the title of the church's own statement of faith, constitution or covenant, as "
                       f"printed. {LEAVE_EMPTY_P}"),
            text_field("url", "Statement URL", f"Write the web address where the statement is published. "
                                               f"{LEAVE_EMPTY_P}"),
            text_field("read", "Date read (YYYY-MM-DD)", f"Write the date you read the statement, as "
                       f"year-month-day, for example 2026-11-22. {LEAVE_EMPTY_P}"),
            text_field("archived", "Archived copy URL", f"Write the web address of an archived copy of the "
                       f"statement. {LEAVE_EMPTY_P}")]
    where = [text_field("where", "Where the statement names the parent" + ("" if one else "s"),
                        f"Write the article or section where the statement says it subscribes to "
                        f"{'it' if one else 'them'}. Leave it empty if there is none or you chose personal "
                        f"knowledge only.")]
    plabel = "; ".join(plabels)
    rows = [{"id": "church.name", "label": "The church", "context": [], "image_ids": [], "fields": name},
            {"id": "church.basis", "label": "Basis", "context": [], "image_ids": [], "fields": basis},
            {"id": "church.statement", "label": "Its statement", "context": [], "image_ids": [], "fields": stmt},
            {"id": "church.parents", "label": f"Subscribes to: {plabel}",
             "context": [f"subscribes to: {x}" for x in plabels], "image_ids": [], "parents": [str(p) for p in parents],
             "fields": where}]
    return {"id": "church", "title": "The church", "text": SECTION_TEXT["church"], "image_ids": [], "rows": rows}


def extra_fields(positions, mods, scopes, instead):
    """instead (optional), modality, scope, basis, where: all required false."""
    f = []
    if instead:
        f.append(choice("instead", "select", "Instead", [lab for lab, _ in positions], dict(positions),
                        f"If the church holds a position here, choose it from this list: "
                        f"{names([lab for lab, _ in positions])}. {NONE_FIT}"))
    f.append(choice("modality", "select", "Modality", [lab for lab, _ in mods], dict(mods),
                    f"Choose how the church holds it: {names([lab for lab, _ in mods])}, as the help defines "
                    f"them. {NONE_FIT}"))
    f.append(choice("scope", "select", "Scope", [lab for lab, _ in scopes], dict(scopes),
                    f"Choose who it applies to: {names([lab for lab, _ in scopes])}. {NONE_FIT}"))
    f.append(choice("basis", "radio", "Basis", [ROW_STATEMENT, ROW_PERSONAL], None,
                    f'Choose "{ROW_STATEMENT}" if you took this from its published statement, or "{ROW_PERSONAL}" '
                    f"if it is what you know of the church. {NONE_FIT}"))
    f.append(text_field("where", "Where",
                        "Write the article or section of the church's statement where this is stated. "
                        "Leave it empty if you chose personal knowledge."))
    return f


def form_spec(g, parents):
    """The spec dict for a church subscribing to `parents` (URIRefs of Bodies in g). Pure on the graph g, which
    carries gc:effectivelyHolds (ingest.derive_rdflib, unioned)."""
    parents = sorted(set(parents), key=str)
    if not parents:
        raise Fail("no parent given")
    known = set(weigh.bodies(g))
    for p in parents:
        if p not in known:
            raise Fail(f"{p} is not a Body in the data")
    plabels = [label(g, p) for p in parents]
    check_unique(plabels, "parents")
    one = len(parents) == 1
    cells = {p: parent_cells(g, p) for p in parents}
    mods, scopes = vocab(g, "vocab/modality", MOD_ORDER), vocab(g, "vocab/scope", SCOPE_ORDER)
    if not mods or not scopes:
        raise Fail("the data has no modality or scope vocabulary")
    lab_of = {iri: lab for lab, iri in mods + scopes}
    loci = []
    for loc in g.subjects(RDF.type, GC.Locus):
        dep = g.value(loc, OWL.deprecated)
        if dep is not None and dep.toPython() is True:
            continue
        poss = sorted(g.subjects(GC.answers, loc), key=str)
        if poss:
            loci.append((notation_key(str(g.value(loc, SKOS.notation) or "")), str(loc), loc, poss))
    loci.sort(key=lambda t: t[:2])
    speak, silent = [], []
    the_parent = "the parent" if one else "the parents"
    for _, _, loc, poss in loci:
        positions = [(label(g, p), p) for p in poss]
        check_unique([lab for lab, _ in positions], f"locus {tail(loc)}")
        note = g.value(loc, SKOS.notation)
        head = (f"{note} " if note is not None else "") + label(g, loc)
        question = g.value(loc, GC.question)
        ctx = [str(question)] if question is not None else []
        speaking = [p for p in parents if loc in cells[p]]
        base = {"id": f"locus.{tail(loc)}", "label": head, "image_ids": [], "locus": str(loc)}
        if not speaking:
            fields = [{**choice("own", "select", "Own", [lab for lab, _ in positions], dict(positions),
                                f"If the church's statement or your own knowledge takes a position here, choose it "
                                f"from this list: {names([lab for lab, _ in positions])}. {NONE_FIT}", True),
                       "empty_means": "unanswered"}]
            fields += extra_fields(positions, mods, scopes, instead=False)
            silent.append({**base, "context": ctx + [f"{p_}: silent" for p_ in plabels], "fields": fields})
            continue
        sets = [cells[p][loc] for p in speaking]
        agree = all(s == sets[0] for s in sets)
        for p, lab in zip(parents, plabels):
            if loc not in cells[p]:
                ctx.append(f"{lab}: silent")
            else:
                ctx.append(f"{lab} holds: " + "; ".join(
                    f"{label(g, pos)} ({lab_of.get(m, tail(m))}, {lab_of.get(s, tail(s))})"
                    for pos, m, s in sorted(cells[p][loc], key=lambda t: (label(g, t[0]), str(t[1]), str(t[2])))))
        if agree:
            a_as = A_AS_ONE if one else A_AS
            opts = [a_as, A_ANOTHER, A_NONE]
            plain = (f'Choose "{a_as}" if the church holds this as {the_parent} {"does" if one else "do"}, '
                     f'"{A_ANOTHER}" if it holds a different position (fill in the fields below), or "{A_NONE}" if '
                     f"it drops that position and gives none. {NONE_FIT}")
        else:
            ctx.append(f"{the_parent.capitalize()} differ here.")
            opts = [A_THIS, A_NONE, A_KEEP]
            plain = (f'{the_parent.capitalize()} differ here: choose "{A_THIS}" and pick the position below, '
                     f'"{A_NONE}", or "{A_KEEP}" if its statement does not say which. {NONE_FIT}')
        ans = choice("answer", "radio", "Answer", opts, None, plain, True, codes={o: CODES[o] for o in opts})
        speak.append({**base, "context": ctx, "fields": [ans] + extra_fields(positions, mods, scopes, instead=True)})
    sections = [church_section(parents, plabels)]
    for sid, title, rows in (("parents-speak", "Where the parents speak", speak),
                             ("parents-silent", "Where the parents are silent", silent)):
        if rows:
            sections.append({"id": sid, "title": title, "text": SECTION_TEXT[sid], "image_ids": [], "rows": rows})
    help_ = list(HELP)
    for q, scheme, order in (("What do the modalities mean?", "vocab/modality", MOD_ORDER),
                             ("What do the scopes mean?", "vocab/scope", SCOPE_ORDER)):
        d = definitions(g, scheme, order)
        if d:
            help_.append({"q": q, "a": d})
    return {"format": build.SPEC_FORMAT, "kind": "congregation", "title": "Congregation form",
            "signer": "Chris", "instruction": INSTRUCTION, "sources": [], "run_header": None, "images": [],
            "congregation": {"parents": [{"iri": str(p), "label": lab} for p, lab in zip(parents, plabels)]},
            "sections": sections, "withheld": [], "help": help_, "signature": {"fields": ["name", "date"]}}


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--parent", action="append", required=True, metavar="body/<slug>")
    ap.add_argument("out")
    a = ap.parse_args(argv)
    try:
        ds = gc_ingest.load_dataset()
        g = gc_ingest.union(gc_ingest.derive_rdflib(ds))
        spec = form_spec(g, [URIRef(B + p) for p in a.parent])
        build.check_spec(spec)
        build.write_spec(a.out, spec)
    except Fail as ex:
        print(f"FAIL: {ex}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
