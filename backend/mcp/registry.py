from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional


class GraphToolRegistry:
    """
    Registry for CompanyOS graph tools.

    This is intentionally lightweight.

    The registry provides the MCP-style tool abstraction while
    keeping FalkorDB as the actual graph execution layer.
    """

    def __init__(self) -> None:

        self._tools: Dict[
            str,
            Dict[str, Any],
        ] = {}

    # =========================================================
    # Register
    # =========================================================

    def register(
        self,
        name: str,
        description: str,
        handler: Callable[..., Any],
        input_schema: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        if not name:
            raise ValueError(
                "Tool name cannot be empty."
            )

        if not callable(handler):
            raise TypeError(
                f"Handler for '{name}' must be callable."
            )

        self._tools[name] = {
            "name": name,
            "description": description,
            "handler": handler,
            "input_schema": (
                input_schema
                or {}
            ),
        }

    # =========================================================
    # Get
    # =========================================================

    def get(
        self,
        name: str,
    ) -> Dict[str, Any]:

        tool = self._tools.get(name)

        if tool is None:
            raise KeyError(
                f"Unknown graph tool: {name}"
            )

        return tool

    # =========================================================
    # Execute
    # =========================================================

    def execute(
        self,
        name: str,
        **kwargs: Any,
    ) -> Any:

        tool = self.get(name)

        handler = tool["handler"]

        return handler(
            **kwargs
        )

    # =========================================================
    # List
    # =========================================================

    def list_tools(
        self,
    ) -> List[Dict[str, Any]]:

        return [
            {
                "name": tool["name"],
                "description": tool[
                    "description"
                ],
                "input_schema": tool[
                    "input_schema"
                ],
            }
            for tool in self._tools.values()
        ]

    # =========================================================
    # Has
    # =========================================================

    def has(
        self,
        name: str,
    ) -> bool:

        return name in self._tools
    