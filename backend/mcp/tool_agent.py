from __future__ import annotations

from typing import Any, Dict, List, Optional

from mcp.graph_tools import FalkorGraphTools
from mcp.registry import GraphToolRegistry


class GraphToolAgent:
    """
    Selects the smallest appropriate FalkorDB tool
    for a graph-oriented request.

    This is intentionally deterministic.

    Gemini remains responsible for natural-language
    interpretation in the higher-level AnalysisAgent.

    This layer is responsible for safe graph execution.
    """

    def __init__(
        self,
        graph_name: str = "novatech",
    ) -> None:

        self.graph_name = graph_name

        self.tools = (
            FalkorGraphTools(
                graph_name=graph_name
            )
        )

        self.registry = (
            GraphToolRegistry()
        )

        self._register_tools()

    # =========================================================
    # Registration
    # =========================================================

    def _register_tools(
        self,
    ) -> None:

        self.registry.register(
            name="falkor_search",
            description=(
                "Search FalkorDB entities "
                "by name, title or id."
            ),
            handler=(
                self.tools.falkor_search
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                    },
                    "limit": {
                        "type": "integer",
                    },
                },
                "required": [
                    "query"
                ],
            },
        )

        self.registry.register(
            name="falkor_traverse",
            description=(
                "Traverse relationships "
                "around an entity."
            ),
            handler=(
                self.tools.falkor_traverse
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "entity_name": {
                        "type": "string",
                    },
                    "max_hops": {
                        "type": "integer",
                    },
                    "limit": {
                        "type": "integer",
                    },
                },
                "required": [
                    "entity_name"
                ],
            },
        )

        self.registry.register(
            name="falkor_cypher",
            description=(
                "Execute validated "
                "read-only Cypher."
            ),
            handler=(
                self.tools.falkor_cypher
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "cypher": {
                        "type": "string",
                    },
                },
                "required": [
                    "cypher"
                ],
            },
        )

        self.registry.register(
            name="falkor_shortest_path",
            description=(
                "Find the shortest graph "
                "path between two entities."
            ),
            handler=(
                self.tools.falkor_shortest_path
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                    },
                    "target": {
                        "type": "string",
                    },
                    "max_hops": {
                        "type": "integer",
                    },
                },
                "required": [
                    "source",
                    "target",
                ],
            },
        )

        self.registry.register(
            name="falkor_neighbors",
            description=(
                "Return immediate graph "
                "neighbors of an entity."
            ),
            handler=(
                self.tools.falkor_neighbors
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "entity_name": {
                        "type": "string",
                    },
                    "relationship_type": {
                        "type": "string",
                    },
                    "limit": {
                        "type": "integer",
                    },
                },
                "required": [
                    "entity_name"
                ],
            },
        )

        self.registry.register(
            name="falkor_subgraph",
            description=(
                "Retrieve a bounded subgraph "
                "around an entity."
            ),
            handler=(
                self.tools.falkor_subgraph
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "entity_name": {
                        "type": "string",
                    },
                    "max_hops": {
                        "type": "integer",
                    },
                    "limit": {
                        "type": "integer",
                    },
                },
                "required": [
                    "entity_name"
                ],
            },
        )

        self.registry.register(
            name="falkor_write",
            description=(
                "Perform an approved graph "
                "write on behalf of an authorized actor."
            ),
            handler=(
                self.tools.falkor_write
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "cypher": {
                        "type": "string",
                    },
                    "actor_id": {
                        "type": "string",
                    },
                },
                "required": [
                    "cypher",
                    "actor_id",
                ],
            },
        )

    # =========================================================
    # Tool list
    # =========================================================

    def list_tools(
        self,
    ) -> List[Dict[str, Any]]:

        return self.registry.list_tools()

    # =========================================================
    # Tool selection
    # =========================================================

    def select_tool(
        self,
        question: str,
        entity_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Select a graph tool based on the semantic intent
        already identified from the user question.

        The selection is deterministic and auditable.
        """

        text = (
            question
            .lower()
            .strip()
        )

        # -----------------------------------------------------
        # Shortest path
        # -----------------------------------------------------

        if any(
            phrase in text
            for phrase in (
                "shortest path",
                "how is",
                "relationship between",
                "connected from",
                "path between",
            )
        ):

            return {
                "tool": (
                    "falkor_shortest_path"
                ),
                "reason": (
                    "The question asks "
                    "for a relationship/path."
                ),
            }

        # -----------------------------------------------------
        # Neighbors
        # -----------------------------------------------------

        if any(
            phrase in text
            for phrase in (
                "who owns",
                "who works on",
                "neighbors",
                "directly connected",
                "direct dependencies",
                "what is connected",
            )
        ):

            return {
                "tool": (
                    "falkor_neighbors"
                ),
                "reason": (
                    "The question asks "
                    "for immediate relationships."
                ),
            }

        # -----------------------------------------------------
        # Subgraph
        # -----------------------------------------------------

        if any(
            phrase in text
            for phrase in (
                "graph around",
                "subgraph",
                "everything connected",
                "connected component",
            )
        ):

            return {
                "tool": (
                    "falkor_subgraph"
                ),
                "reason": (
                    "The question asks "
                    "for a bounded graph neighborhood."
                ),
            }

        # -----------------------------------------------------
        # Traversal
        # -----------------------------------------------------

        if any(
            phrase in text
            for phrase in (
                "traverse",
                "trace",
                "trace the",
                "what happens if",
                "blast radius",
                "depends on",
                "dependency",
            )
        ):

            return {
                "tool": (
                    "falkor_traverse"
                ),
                "reason": (
                    "The question requires "
                    "multi-hop graph traversal."
                ),
            }

        # -----------------------------------------------------
        # Search
        # -----------------------------------------------------

        if any(
            phrase in text
            for phrase in (
                "find",
                "search",
                "locate",
                "which person",
                "which service",
                "who is",
            )
        ):

            return {
                "tool": (
                    "falkor_search"
                ),
                "reason": (
                    "The question first "
                    "requires entity discovery."
                ),
            }

        # -----------------------------------------------------
        # Default
        # -----------------------------------------------------

        return {
            "tool": (
                "falkor_cypher"
            ),
            "reason": (
                "The question requires "
                "a controlled graph query."
            ),
        }

    # =========================================================
    # Execute
    # =========================================================

    def execute(
        self,
        tool_name: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:

        return self.registry.execute(
            tool_name,
            **kwargs,
        )

    # =========================================================
    # Question → Tool → Execution
    # =========================================================

    def answer_with_tool(
        self,
        question: str,
        entity_name: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:

        selection = (
            self.select_tool(
                question=question,
                entity_name=entity_name,
            )
        )

        tool_name = selection[
            "tool"
        ]

        result_kwargs = dict(
            kwargs
        )

        if (
            entity_name
            and tool_name
            in {
                "falkor_traverse",
                "falkor_neighbors",
                "falkor_subgraph",
            }
        ):

            result_kwargs.setdefault(
                "entity_name",
                entity_name,
            )

        result = self.execute(
            tool_name,
            **result_kwargs,
        )

        return {
            "success": bool(
                result.get(
                    "success",
                    False,
                )
            ),
            "question": question,
            "graph_name": (
                self.graph_name
            ),
            "tool_selection": selection,
            "result": result,
        }