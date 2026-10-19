"""
CompanyOS MCP-style graph tool layer.

The tools in this package expose FalkorDB graph capabilities
to CompanyOS agents through a controlled tool registry.
"""

from mcp.registry import GraphToolRegistry
from mcp.tool_agent import GraphToolAgent

__all__ = [
    "GraphToolRegistry",
    "GraphToolAgent",
]