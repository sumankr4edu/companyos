from __future__ import annotations

from typing import Any, Dict, List, Optional

from graph.client import graph_client
from security.cypher_validator import CypherValidator


class FalkorGraphTools:
    """
    Controlled MCP-style tools for FalkorDB.

    All tools operate directly against FalkorDB.

    Read operations:
        falkor_search
        falkor_traverse
        falkor_cypher
        falkor_shortest_path
        falkor_neighbors
        falkor_subgraph

    Write operation:
        falkor_write

    Security:
        - graph name is explicit
        - read Cypher is validated
        - writes are restricted
        - user identity is passed into writes
    """

    def __init__(
        self,
        graph_name: str = "novatech",
    ) -> None:

        self.graph_name = graph_name

        self.validator = (
            CypherValidator()
        )

    # =========================================================
    # Internal query
    # =========================================================

    def _query(
        self,
        cypher: str,
    ) -> Any:

        return graph_client.query(
            cypher,
            graph_name=self.graph_name,
        )

    # =========================================================
    # Result normalization
    # =========================================================

    @staticmethod
    def _serialize(
        value: Any,
    ) -> Any:

        if value is None:
            return None

        if isinstance(
            value,
            (
                str,
                int,
                float,
                bool,
            ),
        ):
            return value

        if isinstance(
            value,
            list,
        ):
            return [
                FalkorGraphTools._serialize(
                    item
                )
                for item in value
            ]

        if isinstance(
            value,
            tuple,
        ):
            return [
                FalkorGraphTools._serialize(
                    item
                )
                for item in value
            ]

        if isinstance(
            value,
            dict,
        ):
            return {
                str(key): (
                    FalkorGraphTools._serialize(
                        item
                    )
                )
                for key, item in value.items()
            }

        # -----------------------------------------------------
        # FalkorDB node
        # -----------------------------------------------------

        if hasattr(
            value,
            "properties",
        ):

            return {
                "id": getattr(
                    value,
                    "id",
                    None,
                ),
                "label": getattr(
                    value,
                    "label",
                    None,
                ),
                "properties": (
                    FalkorGraphTools._serialize(
                        getattr(
                            value,
                            "properties",
                            {},
                        )
                    )
                ),
            }

        # -----------------------------------------------------
        # FalkorDB relationship
        # -----------------------------------------------------

        if hasattr(
            value,
            "relation",
        ):

            return {
                "id": getattr(
                    value,
                    "id",
                    None,
                ),
                "type": getattr(
                    value,
                    "relation",
                    None,
                ),
                "properties": (
                    FalkorGraphTools._serialize(
                        getattr(
                            value,
                            "properties",
                            {},
                        )
                    )
                ),
            }

        return str(value)

    # =========================================================
    # 1. falkor_search
    # =========================================================

    def falkor_search(
        self,
        query: str,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        Search entities by name/title.

        This is intentionally graph-native rather than a
        separate document/vector search.
        """

        if not query or not query.strip():

            return {
                "success": False,
                "tool": "falkor_search",
                "error": "Search query is required.",
            }

        limit = max(
            1,
            min(
                int(limit),
                100,
            ),
        )

        safe_query = (
            query.strip()
            .replace(
                "\\",
                "\\\\",
            )
            .replace(
                "'",
                "\\'",
            )
        )

        cypher = f"""
        MATCH (n)
        WHERE
            toString(n.name) CONTAINS '{safe_query}'
            OR toString(n.title) CONTAINS '{safe_query}'
            OR toString(n.id) CONTAINS '{safe_query}'
        RETURN
            labels(n) AS labels,
            n.name AS name,
            n.title AS title,
            n.id AS id
        LIMIT {limit}
        """

        try:

            result = self._query(
                cypher
            )

            return {
                "success": True,
                "tool": "falkor_search",
                "query": query,
                "results": self._serialize(
                    result
                ),
            }

        except Exception as exc:

            return {
                "success": False,
                "tool": "falkor_search",
                "query": query,
                "error": str(exc),
            }

    # =========================================================
    # 2. falkor_traverse
    # =========================================================

    def falkor_traverse(
        self,
        entity_name: str,
        max_hops: int = 2,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        Traverse the graph around an entity.
        """

        if not entity_name:

            return {
                "success": False,
                "tool": "falkor_traverse",
                "error": (
                    "entity_name is required."
                ),
            }

        max_hops = max(
            1,
            min(
                int(max_hops),
                6,
            ),
        )

        limit = max(
            1,
            min(
                int(limit),
                200,
            ),
        )

        safe_name = (
            entity_name
            .strip()
            .replace(
                "\\",
                "\\\\",
            )
            .replace(
                "'",
                "\\'",
            )
        )

        cypher = f"""
        MATCH (start)
        WHERE
            start.name = '{safe_name}'
            OR start.title = '{safe_name}'
            OR start.id = '{safe_name}'

        MATCH path =
            (start)-[*1..{max_hops}]-(related)

        RETURN path
        LIMIT {limit}
        """

        try:

            result = self._query(
                cypher
            )

            return {
                "success": True,
                "tool": "falkor_traverse",
                "entity": entity_name,
                "max_hops": max_hops,
                "results": self._serialize(
                    result
                ),
            }

        except Exception as exc:

            return {
                "success": False,
                "tool": "falkor_traverse",
                "entity": entity_name,
                "error": str(exc),
            }

    # =========================================================
    # 3. falkor_cypher
    # =========================================================

    def falkor_cypher(
        self,
        cypher: str,
    ):
        query = self.validator.validate(cypher)

        result = graph_client.query(
            query,
            graph_name=self.graph_name,
        )

        return {
            "success": True,
            "tool": "falkor_cypher",
            "graph_name": self.graph_name,
            "cypher": query,
            "result": result,
        }

        try:

            # -------------------------------------------------
            # Existing CompanyOS security contract
            # -------------------------------------------------

            self.validator.validate(
                cypher
            )

            result = self._query(
                cypher
            )

            return {
                "success": True,
                "tool": "falkor_cypher",
                "results": self._serialize(
                    result
                ),
            }

        except Exception as exc:

            return {
                "success": False,
                "tool": "falkor_cypher",
                "error": str(exc),
            }

    # =========================================================
    # 4. falkor_shortest_path
    # =========================================================

    def falkor_shortest_path(
        self,
        source: str,
        target: str,
        max_hops: int = 8,
    ) -> Dict[str, Any]:
        """
        Find a shortest relationship path between two entities.
        """

        if not source or not target:

            return {
                "success": False,
                "tool": "falkor_shortest_path",
                "error": (
                    "source and target are required."
                ),
            }

        max_hops = max(
            1,
            min(
                int(max_hops),
                12,
            ),
        )

        safe_source = (
            source
            .strip()
            .replace(
                "\\",
                "\\\\",
            )
            .replace(
                "'",
                "\\'",
            )
        )

        safe_target = (
            target
            .strip()
            .replace(
                "\\",
                "\\\\",
            )
            .replace(
                "'",
                "\\'",
            )
        )

        cypher = f"""
        MATCH (source)
        WHERE
            source.name = '{safe_source}'
            OR source.title = '{safe_source}'
            OR source.id = '{safe_source}'

        MATCH (target)
        WHERE
            target.name = '{safe_target}'
            OR target.title = '{safe_target}'
            OR target.id = '{safe_target}'

        MATCH path =
            shortestPath(
                (source)-[*..{max_hops}]-(target)
            )

        RETURN path
        LIMIT 1
        """

        try:

            result = self._query(
                cypher
            )

            return {
                "success": True,
                "tool": (
                    "falkor_shortest_path"
                ),
                "source": source,
                "target": target,
                "results": self._serialize(
                    result
                ),
            }

        except Exception as exc:

            return {
                "success": False,
                "tool": (
                    "falkor_shortest_path"
                ),
                "source": source,
                "target": target,
                "error": str(exc),
            }

    # =========================================================
    # 5. falkor_neighbors
    # =========================================================

    def falkor_neighbors(
        self,
        entity_name: str,
        relationship_type: Optional[
            str
        ] = None,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """
        Return immediate neighbors of an entity.
        """

        if not entity_name:

            return {
                "success": False,
                "tool": "falkor_neighbors",
                "error": (
                    "entity_name is required."
                ),
            }

        limit = max(
            1,
            min(
                int(limit),
                200,
            ),
        )

        safe_name = (
            entity_name
            .strip()
            .replace(
                "\\",
                "\\\\",
            )
            .replace(
                "'",
                "\\'",
            )
        )

        relationship_clause = ""

        if relationship_type:

            safe_relationship = (
                relationship_type
                .strip()
                .replace(
                    "`",
                    "",
                )
                .replace(
                    "'",
                    "",
                )
                .replace(
                    " ",
                    "_",
                )
            )

            relationship_clause = (
                f":`{safe_relationship}`"
            )

        cypher = f"""
        MATCH (source)
        WHERE
            source.name = '{safe_name}'
            OR source.title = '{safe_name}'
            OR source.id = '{safe_name}'

        MATCH (source)-[r{relationship_clause}]-(neighbor)

        RETURN
            labels(neighbor) AS labels,
            neighbor.name AS name,
            neighbor.title AS title,
            neighbor.id AS id,
            type(r) AS relationship
        LIMIT {limit}
        """

        try:

            result = self._query(
                cypher
            )

            return {
                "success": True,
                "tool": "falkor_neighbors",
                "entity": entity_name,
                "relationship_type": (
                    relationship_type
                ),
                "results": self._serialize(
                    result
                ),
            }

        except Exception as exc:

            return {
                "success": False,
                "tool": "falkor_neighbors",
                "entity": entity_name,
                "error": str(exc),
            }

    # =========================================================
    # 6. falkor_subgraph
    # =========================================================

    def falkor_subgraph(
        self,
        entity_name: str,
        max_hops: int = 2,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Retrieve a bounded subgraph around an entity.
        """

        if not entity_name:

            return {
                "success": False,
                "tool": "falkor_subgraph",
                "error": (
                    "entity_name is required."
                ),
            }

        max_hops = max(
            1,
            min(
                int(max_hops),
                5,
            ),
        )

        limit = max(
            1,
            min(
                int(limit),
                300,
            ),
        )

        safe_name = (
            entity_name
            .strip()
            .replace(
                "\\",
                "\\\\",
            )
            .replace(
                "'",
                "\\'",
            )
        )

        cypher = f"""
        MATCH (center)
        WHERE
            center.name = '{safe_name}'
            OR center.title = '{safe_name}'
            OR center.id = '{safe_name}'

        MATCH path =
            (center)-[*1..{max_hops}]-(related)

        WITH center, related, path
        LIMIT {limit}

        RETURN
            center,
            related,
            path
        """

        try:

            result = self._query(
                cypher
            )

            return {
                "success": True,
                "tool": "falkor_subgraph",
                "entity": entity_name,
                "max_hops": max_hops,
                "results": self._serialize(
                    result
                ),
            }

        except Exception as exc:

            return {
                "success": False,
                "tool": "falkor_subgraph",
                "entity": entity_name,
                "error": str(exc),
            }

    # =========================================================
    # 7. falkor_write
    # =========================================================

    def falkor_write(
        self,
        cypher: str,
        actor_id: str,
    ) -> Dict[str, Any]:
        """
        Controlled graph write.

        Writes are intentionally separated from read-only
        falkor_cypher.

        This tool is intended for approved agent actions,
        not arbitrary user-generated Cypher.
        """

        if not actor_id:

            return {
                "success": False,
                "tool": "falkor_write",
                "error": (
                    "actor_id is required."
                ),
            }

        if actor_id != "suman":

            return {
                "success": False,
                "tool": "falkor_write",
                "error": (
                    "Actor is not authorized "
                    "for graph writes."
                ),
            }

        if not cypher or not cypher.strip():

            return {
                "success": False,
                "tool": "falkor_write",
                "error": (
                    "Cypher write query is required."
                ),
            }

        # -----------------------------------------------------
        # Only explicitly supported write operations.
        #
        # This prevents the MCP layer from becoming an
        # unrestricted database console.
        # -----------------------------------------------------

        normalized = (
            cypher
            .strip()
            .upper()
        )

        allowed_prefixes = (
            "CREATE ",
            "CREATE(",
            "MATCH ",
            "MATCH(",
        )

        if not normalized.startswith(
            allowed_prefixes
        ):

            return {
                "success": False,
                "tool": "falkor_write",
                "error": (
                    "Unsupported write query. "
                    "Use an approved graph action."
                ),
            }

        blocked_tokens = [
            "DROP ",
            "DELETE ",
            "DETACH ",
            "LOAD CSV",
            "CALL DBMS",
            "CALL DB.",
            "CALL APOC",
            "--",
            "/*",
            "*/",
        ]

        for token in blocked_tokens:

            if token in normalized:

                return {
                    "success": False,
                    "tool": "falkor_write",
                    "error": (
                        f"Blocked Cypher token: "
                        f"{token.strip()}"
                    ),
                }

        try:

            result = self._query(
                cypher
            )

            return {
                "success": True,
                "tool": "falkor_write",
                "actor_id": actor_id,
                "results": self._serialize(
                    result
                ),
            }

        except Exception as exc:

            return {
                "success": False,
                "tool": "falkor_write",
                "error": str(exc),
            }