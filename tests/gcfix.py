"""Shared in-test fixtures: a minimal valid dataset and helpers. Never touches the repo's data/."""

from rdflib import Dataset, Graph, URIRef
from rdflib.namespace import RDF

from goldenchain import ingest

B = ingest.B
GC = ingest.GC

PREFIXES = f"""
@base <{B}> .
@prefix gc: <{B}ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
"""

PROPOSED = "gc:status <vocab/status/proposed> ; gc:proposedBy <agent/build>"

MINIMAL = PREFIXES + f"""
<heading/worship> a gc:Heading ; rdfs:label "Worship" .
<agent/build> a gc:Agent .
<agent/architect> a gc:Agent .
<source/gill> a gc:SourceWork ; rdfs:label "Gill" .
<source/gill/ch1> a gc:SourceDivision ; dcterms:isPartOf <source/gill> .
<locus/baptism> a gc:Locus ; rdfs:label "Baptism" ; skos:notation "1" ;
    gc:question "What is baptism?"@en ; gc:underHeading <heading/worship> .
<locus/other> a gc:Locus ; rdfs:label "Other" ; skos:notation "2" ;
    gc:question "Other?"@en ; gc:underHeading <heading/worship> .
<position/baptism/immersion> a gc:Position ; rdfs:label "Immersion" ;
    gc:answers <locus/baptism> ; {PROPOSED} .
<passage/kjv/Matt.28.19> a gc:Passage ; gc:versification "kjv" ; gc:book "Matt" ;
    gc:osisRef "Matt.28.19" ; gc:startOrdinal {{MATT_28_19}} ; gc:endOrdinal {{MATT_28_19}} .
<argument/gill/ch1/001> a gc:Argument ; gc:source <source/gill/ch1> ;
    gc:supports <position/baptism/immersion> ; gc:cites <passage/kjv/Matt.28.19> ; {PROPOSED} .
<body/gill> a gc:Body ; rdfs:label "Gill" ; gc:holds <holding/gill/baptism/immersion> .
<holding/gill/baptism/immersion> a gc:Holding ; gc:position <position/baptism/immersion> ;
    gc:modality <vocab/modality/taught> ; dcterms:source <source/gill/ch1> ; {PROPOSED} .
"""


def _ordinal() -> int:
    from goldenchain import passage

    return passage.parse("Matt.28.19").start_ordinal


def U(s: str) -> URIRef:
    return URIRef(B + s)


def minimal() -> Graph:
    g = Graph()
    g.parse(data=MINIMAL.replace("{MATT_28_19}", str(_ordinal())), format="turtle")
    return g


def add(g: Graph, ttl: str) -> Graph:
    g.parse(data=PREFIXES + ttl, format="turtle")
    return g


def dataset_with(fixture: Graph, name: str = "fixture") -> Dataset:
    """core + vocab + the fixture as graph/{name}."""
    ds = Dataset()
    for f in ingest.input_files(data_dir="/nonexistent-data-dir"):
        ds.graph(ingest.graph_name(f)).parse(f, format="turtle")
    ng = ds.graph(URIRef(B + "graph/" + name))
    for t in fixture:
        ng.add(t)
    return ds


def report(fixture: Graph, name: str = "fixture"):
    return ingest.shacl_report(ingest.union(dataset_with(fixture, name)))


def focus_nodes(rows) -> set[str]:
    return {str(r[0]) for r in rows}


def types_of(g: Graph, node: str):
    return set(g.objects(U(node), RDF.type))


# ---- world builder for reasoner tests (no SHACL needed) -----------------------------

MOD = {m: f"vocab/modality/{m}" for m in ("required", "taught", "tolerated", "forbidden")}


class World:
    """Build bodies, positions and holdings programmatically in one graph."""

    def __init__(self):
        self.g = Graph()

    def position(self, locus: str, name: str):
        iri = U(f"position/{locus}/{name}")
        self.g.add((iri, RDF.type, GC.Position))
        self.g.add((iri, GC.answers, U(f"locus/{locus}")))
        self.g.add((U(f"locus/{locus}"), RDF.type, GC.Locus))
        return iri

    def body(self, name: str, parent: str | None = None):
        iri = U(f"body/{name}")
        self.g.add((iri, RDF.type, GC.Body))
        if parent:
            self.g.add((iri, GC.childOf, U(f"body/{parent}")))
        return iri

    def hold(self, body: str, locus: str, pos: str, modality: str = "taught", scope: str | None = None):
        iri = U(f"holding/{body}/{locus}/{pos}" + (f"/{scope}" if scope else ""))
        self.g.add((iri, RDF.type, GC.Holding))
        self.g.add((U(f"body/{body}"), GC.holds, iri))
        self.g.add((iri, GC.position, U(f"position/{locus}/{pos}")))
        self.g.add((iri, GC.modality, U(MOD[modality])))
        if scope:
            self.g.add((iri, GC.scope, U(f"vocab/scope/{scope}")))
        return iri

    def dataset(self) -> Dataset:
        ds = Dataset()
        ng = ds.graph(U("graph/fixture"))
        for t in self.g:
            ng.add(t)
        return ds


def eff(derived: Dataset) -> set[tuple[str, str]]:
    """(body-name, 'locus/pos') for every effectivelyHolds triple."""
    out = set()
    for b, h in derived.graph(U("graph/derived/inheritance")).subject_objects(GC.effectivelyHolds):
        pos = next(derived.objects(h, GC.position))
        out.add((str(b).split("/body/")[1], str(pos).split("/position/")[1]))
    return out


def inconsistencies(derived: Dataset) -> list:
    return list(derived.graph(U("graph/derived/consistency")).subjects(RDF.type, GC.Inconsistency))


# ---- tiny on-disk data dir for the engine tests ---------------------------------------

def write_tiny_data(directory) -> None:
    """A small valid data dir: one source file, a plumb-line, inheritance and one Inconsistency."""
    from pathlib import Path

    g = minimal()
    add(
        g,
        f"""
<position/baptism/sprinkling> a gc:Position ; rdfs:label "Sprinkling" ;
    gc:answers <locus/baptism> ; gc:excludes <position/baptism/immersion> ; {PROPOSED} .
<argument/gill/ch1/002> a gc:Argument ; gc:source <source/gill/ch1> ;
    gc:supports <position/baptism/sprinkling> ; gc:cites <passage/kjv/Matt.28.19> ; {PROPOSED} .
<body/child> a gc:Body ; rdfs:label "Child" ; gc:childOf <body/gill> ;
    gc:holds <holding/child/baptism/sprinkling> .
<holding/child/baptism/sprinkling> a gc:Holding ; gc:position <position/baptism/sprinkling> ;
    gc:modality <vocab/modality/taught> ; dcterms:source <source/gill/ch1> ; {PROPOSED} .
<body/silent> a gc:Body ; rdfs:label "Silent" .
<body/both> a gc:Body ; rdfs:label "Both" ;
    gc:holds <holding/both/baptism/immersion>, <holding/both/baptism/sprinkling> .
<holding/both/baptism/immersion> a gc:Holding ; gc:position <position/baptism/immersion> ;
    gc:modality <vocab/modality/required> ; dcterms:source <source/gill/ch1> ; {PROPOSED} .
<holding/both/baptism/sprinkling> a gc:Holding ; gc:position <position/baptism/sprinkling> ;
    gc:modality <vocab/modality/taught> ; dcterms:source <source/gill/ch1> ; {PROPOSED} .
""",
    )
    d = Path(directory)
    d.mkdir(parents=True, exist_ok=True)
    g.serialize(d / "tiny.ttl", format="turtle")
    pl = Graph()
    add(pl, '<locus/baptism> gc:tier <vocab/tier/first> ; gc:clarity <vocab/clarity/contested> .')
    pl.serialize(d / "plumb-line.ttl", format="turtle")
