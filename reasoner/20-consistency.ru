# ADR-0003 §6 as ratified 2026-10-25.
#   excludes (symmetric): fires when a Body effectively holds P and Q, both in {required, taught}.
#   entails  (directed):  fires when a Body holds P in {required, taught} and Q forbidden.
# Neither rule ever derives a Holding. Scope is ignored when firing.
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
  BIND (IRI(CONCAT("https://w3id.org/golden-chain/inconsistency/", STRAFTER(STR(?b), "/body/"),
                   "/entails/", STRAFTER(STR(?p), "/position/"), "/", STRAFTER(STR(?q), "/position/"))) AS ?i)
}
