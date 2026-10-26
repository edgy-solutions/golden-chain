# ADR-0003 §6 as ratified 2026-10-25.
#   excludes (symmetric): fires when a Body effectively holds P and Q, both in {required, taught}.
#   entails  (directed):  fires when a Body holds P in {required, taught} and Q forbidden.
# Both fire only when the two Holdings' scopes intersect: an absent scope is all and
# intersects everything; two explicit scopes intersect only if equal (ADR-0003 rev. 1).
#   parents-differ: a Body with two parents that both speak on a Locus, whose effective
#   Holdings there differ, and that asserts nothing of its own there (ADR-0003 rev. 1).
# No rule ever derives a Holding, and none picks a parent.
# Reads graph/derived/inheritance through the union; writes graph/derived/consistency.
PREFIX gc: <https://w3id.org/golden-chain/ontology#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

INSERT { GRAPH <https://w3id.org/golden-chain/graph/derived/consistency> {
    ?i a gc:Inconsistency ; gc:body ?b ; gc:rule "excludes" ; gc:involves ?p , ?q .
    ?b gc:inconsistent "true"^^xsd:boolean } }
WHERE {
  ?b gc:effectivelyHolds ?h1 , ?h2 .
  ?h1 gc:position ?p ; gc:modality ?m1 .
  ?h2 gc:position ?q ; gc:modality ?m2 .
  ?p gc:excludes|^gc:excludes ?q .
  FILTER (STR(?p) < STR(?q))
  FILTER (?m1 IN (<https://w3id.org/golden-chain/vocab/modality/required>, <https://w3id.org/golden-chain/vocab/modality/taught>))
  FILTER (?m2 IN (<https://w3id.org/golden-chain/vocab/modality/required>, <https://w3id.org/golden-chain/vocab/modality/taught>))
  FILTER NOT EXISTS { ?h1 gc:scope ?s1 . ?h2 gc:scope ?s2 . FILTER (?s1 != ?s2) }
  BIND (IRI(CONCAT("https://w3id.org/golden-chain/inconsistency/", STRAFTER(STR(?b), "/body/"),
                   "/excludes/", STRAFTER(STR(?p), "/position/"), "/", STRAFTER(STR(?q), "/position/"))) AS ?i)
} ;

INSERT { GRAPH <https://w3id.org/golden-chain/graph/derived/consistency> {
    ?i a gc:Inconsistency ; gc:body ?b ; gc:rule "entails" ; gc:involves ?p , ?q .
    ?b gc:inconsistent "true"^^xsd:boolean } }
WHERE {
  ?b gc:effectivelyHolds ?h1 , ?h2 .
  ?h1 gc:position ?p ; gc:modality ?m1 .
  ?h2 gc:position ?q ; gc:modality <https://w3id.org/golden-chain/vocab/modality/forbidden> .
  ?p gc:entails ?q .
  FILTER (?m1 IN (<https://w3id.org/golden-chain/vocab/modality/required>, <https://w3id.org/golden-chain/vocab/modality/taught>))
  FILTER NOT EXISTS { ?h1 gc:scope ?s1 . ?h2 gc:scope ?s2 . FILTER (?s1 != ?s2) }
  BIND (IRI(CONCAT("https://w3id.org/golden-chain/inconsistency/", STRAFTER(STR(?b), "/body/"),
                   "/entails/", STRAFTER(STR(?p), "/position/"), "/", STRAFTER(STR(?q), "/position/"))) AS ?i)
} ;

INSERT { GRAPH <https://w3id.org/golden-chain/graph/derived/consistency> {
    ?i a gc:Inconsistency ; gc:body ?b ; gc:rule "parents-differ" ; gc:involves ?pos .
    ?b gc:inconsistent "true"^^xsd:boolean } }
WHERE {
  ?b gc:childOf ?p1 , ?p2 .
  FILTER (?p1 != ?p2)
  ?p1 gc:effectivelyHolds ?h1 .
  ?h1 gc:position ?pos ; gc:modality ?m .
  ?pos gc:answers ?l .
  ?p2 gc:effectivelyHolds/gc:position/gc:answers ?l .
  FILTER NOT EXISTS { ?b gc:holds/gc:position/gc:answers ?l }
  # ?h1 differs unless ?p2 effectively holds the same Position, modality and scope (absent = all).
  FILTER NOT EXISTS {
    ?p2 gc:effectivelyHolds ?h2 .
    ?h2 gc:position ?pos ; gc:modality ?m .
    FILTER NOT EXISTS { ?h1 gc:scope ?s1 . FILTER NOT EXISTS { ?h2 gc:scope ?s1 } }
    FILTER NOT EXISTS { ?h2 gc:scope ?s2 . FILTER NOT EXISTS { ?h1 gc:scope ?s2 } }
  }
  BIND (IRI(CONCAT("https://w3id.org/golden-chain/inconsistency/", STRAFTER(STR(?b), "/body/"),
                   "/parents-differ/", STRAFTER(STR(?l), "/locus/"))) AS ?i)
}
