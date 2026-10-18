from graph.queries import run_cypher
from agents.cypher_validator import CypherValidator


class GraphQueryTool:
    """
    Controlled read-only gateway to FalkorDB.

    Responsibilities:
    1. Validate generated Cypher.
    2. Prevent dangerous/write queries.
    3. Execute approved queries against the tenant graph.
    """

    def __init__(self, graph_name: str = "novatech"):
        self.graph_name = graph_name
        self.validator = CypherValidator()

    def execute(self, cypher: str):
        if not cypher or not cypher.strip():
            raise ValueError("Cypher query cannot be empty.")

        # Security boundary
        valid, message = self.validator.validate(cypher)

        if not valid:
            raise ValueError(
                f"Cypher query rejected: {message}"
            )

        # Execute only validated read query
        return run_cypher(
            cypher,
            self.graph_name,
        )