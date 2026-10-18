from typing import Any

from agents.cypher_validator import CypherValidator
from graph.queries import run_cypher
from tools.graph_tools import GraphTools


class CompanyOSGraphTools:
    """
    MCP-style interface over CompanyOS graph capabilities.

    These methods provide stable tool names that agents can invoke
    without knowing the underlying GraphTools implementation.
    """

    def __init__(self, graph_name: str = "novatech"):
        self.graph_name = graph_name
        self.graph = GraphTools(graph_name)
        self.validator = CypherValidator()

    # ============================================================
    # SEARCH
    # ============================================================

    def falkor_search(
        self,
        text: str,
        limit: int = 10,
    ) -> Any:
        return self.graph.search(
            text=text,
            limit=limit,
        )

    # ============================================================
    # TRAVERSE
    # ============================================================

    def falkor_traverse(
        self,
        entity_name: str,
        relationship: str | None = None,
        limit: int = 50,
    ) -> Any:
        return self.graph.neighbors(
            entity_name=entity_name,
            relationship=relationship,
            limit=limit,
        )

    # ============================================================
    # CYPHER
    # ============================================================

    def falkor_cypher(
        self,
        cypher: str,
    ) -> Any:
        valid, message = self.validator.validate(cypher)

        if not valid:
            raise ValueError(message)

        return run_cypher(
            cypher,
            self.graph_name,
        )

    # ============================================================
    # SHORTEST PATH
    # ============================================================

    def falkor_shortest_path(
        self,
        source: str,
        target: str,
        max_hops: int = 8,
    ) -> Any:
        return self.graph.shortest_path(
            source=source,
            target=target,
            max_hops=max_hops,
        )

    # ============================================================
    # NEIGHBORS
    # ============================================================

    def falkor_neighbors(
        self,
        entity_name: str,
        relationship: str | None = None,
        limit: int = 50,
    ) -> Any:
        return self.graph.neighbors(
            entity_name=entity_name,
            relationship=relationship,
            limit=limit,
        )

    # ============================================================
    # SUBGRAPH
    # ============================================================

    def falkor_subgraph(
        self,
        entity_name: str,
        depth: int = 2,
    ) -> Any:
        return self.graph.subgraph(
            entity_name=entity_name,
            depth=depth,
        )

    # ============================================================
    # WRITE
    # ============================================================

    def falkor_write(
        self,
        cypher: str,
    ) -> Any:
        """
        Controlled graph write.

        Writes are deliberately separated from falkor_cypher().
        This gives us a future authorization boundary for actions.
        """

        normalized = cypher.strip().upper()

        allowed = (
            normalized.startswith("CREATE"),
            normalized.startswith("MERGE"),
        )

        if not any(allowed):
            raise ValueError(
                "falkor_write only permits CREATE or MERGE operations."
            )

        return run_cypher(
            cypher,
            self.graph_name,
        )