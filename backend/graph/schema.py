from .client import graph_client


CONSTRAINTS = [
    """
    CREATE INDEX FOR (n:Person) ON (n.id)
    """,
    """
    CREATE INDEX FOR (n:Team) ON (n.id)
    """,
    """
    CREATE INDEX FOR (n:Project) ON (n.id)
    """,
    """
    CREATE INDEX FOR (n:Service) ON (n.id)
    """,
    """
    CREATE INDEX FOR (n:Incident) ON (n.id)
    """,
    """
    CREATE INDEX FOR (n:Decision) ON (n.id)
    """,
    """
    CREATE INDEX FOR (n:Document) ON (n.id)
    """,
    """
    CREATE INDEX FOR (n:Ticket) ON (n.id)
    """,
]


def initialize_schema(graph_name: str = "novatech"):
    graph = graph_client.get_graph(graph_name)

    for query in CONSTRAINTS:
        try:
            graph.query(query)
        except Exception as exc:
            # Indexes may already exist.
            print(f"Schema setup notice: {exc}")

    return {
        "graph": graph_name,
        "status": "initialized",
    }