from pyexpect import expect
from pytest_httpserver import HTTPServer
from rdflib import Graph
from rdflib.namespace import FOAF
from rdflib.plugins.stores.sparqlstore import SPARQLStore
from rdflib.term import URIRef, Literal

from constellate.database.sparql.query import query
from constellate.database.sparql.sparqlburger.triple import to_triple

from SPARQLBurger.SPARQLQueryBuilder import SPARQLSelectQuery, SPARQLGraphPattern


def test_query(httpserver: HTTPServer) -> None:
    # Fake SPARQL server endpoint result
    data = {
        "head": {
            "vars": ["name"],
        },
        "results": {"bindings": [{"name": {"type": "literal", "value": "Beckett"}}]},
    }
    httpserver.expect_request("/sample", method="POST").respond_with_json(
        response_json=data, content_type="application/sparql-results+json"
    )

    # Request to query the following sparql endpoint
    store: SPARQLStore = SPARQLStore(sparql11=True, returnFormat="json", **{"method": "POST"})
    graph: Graph = Graph(store=store)
    graph.open(httpserver.url_for("/sample"), create=True)

    # Generate query:
    # SELECT ?age WHERE { ?person foaf:name ?name .}
    select_builder = SPARQLSelectQuery()
    select_builder.add_variables(variables=["?name"])
    where_pattern = SPARQLGraphPattern()
    # ?person will be replaced with http://example/person/1
    where_pattern.add_triples(
        triples=[
            to_triple(
                subject=Literal("?person"), predicate=URIRef("foaf:name"), object=Literal("?name")
            ),
        ]
    )
    select_builder.set_where_pattern(graph_pattern=where_pattern)

    # Replace ?name with John Smith in query
    result = query(
        raw_query=select_builder.get_text(),
        graph=graph,
        init_namespaces={"foaf": FOAF},
        init_bindings={"person": URIRef("http://person.com/beckett")},
    )
    name: Literal = next(iter([row.name for row in result]), None)
    expect(name.value).to_equal("Beckett")
