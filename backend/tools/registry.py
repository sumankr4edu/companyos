from tools.mcp_tools import CompanyOSGraphTools


class GraphToolRegistry:
    """
    Central registry of CompanyOS graph tools.
    """

    def __init__(self, graph_name: str = "novatech"):
        self.tools = CompanyOSGraphTools(graph_name)

    def list_tools(self):
        return [
            "falkor_search",
            "falkor_traverse",
            "falkor_cypher",
            "falkor_shortest_path",
            "falkor_neighbors",
            "falkor_subgraph",
            "falkor_write",
        ]

    def execute(self, tool_name: str, **kwargs):
        if tool_name not in self.list_tools():
            raise ValueError(
                f"Unknown graph tool: {tool_name}"
            )

        tool = getattr(
            self.tools,
            tool_name,
            None,
        )

        if tool is None:
            raise ValueError(
                f"Tool implementation missing: {tool_name}"
            )

        return tool(**kwargs)