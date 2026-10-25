# ADR-0003 §7: childOf inheritance with per-Locus override.
# A Body effectively holds a Holding of itself or of an ancestor A on Locus L,
# unless some Body on the path from it to A (itself included) holds anything on L.
# The nearest Holder on L wins and blocks everything above it, whatever the scope.
# Reads the union of the named graphs; writes graph/derived/inheritance.
PREFIX gc: <https://w3id.org/golden-chain/ontology#>

INSERT { GRAPH <https://w3id.org/golden-chain/graph/derived/inheritance> { ?b gc:effectivelyHolds ?h } }
WHERE {
  { ?b gc:holds ?x } UNION { ?b gc:childOf ?x }
  ?b gc:childOf* ?a .
  ?a gc:holds ?h .
  ?h gc:position/gc:answers ?l .
  FILTER NOT EXISTS {
    ?b gc:childOf* ?m .
    ?m gc:childOf+ ?a .
    ?m gc:holds/gc:position/gc:answers ?l .
  }
}
