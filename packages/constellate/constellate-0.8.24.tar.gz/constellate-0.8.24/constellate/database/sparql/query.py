from rdflib import Graph
from rdflib.query import Result
from rdflib.store import Store


def query(
    raw_query: str,
    graph: Graph = None,
    store: Store = None,
    init_namespaces: dict = None,
    init_bindings: dict = None,
) -> Result:
    """
    Query a store, with provided query builder and bindings applied

    Usage: See unit tests
    """
    init_namespaces = init_namespaces if init_namespaces is not None else {}
    init_bindings = init_bindings if init_bindings is not None else {}

    graph = Graph(store=store) if graph is None and store is None else graph
    return graph.query(raw_query, initNs=init_namespaces, initBindings=init_bindings)
