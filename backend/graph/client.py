import os

from dotenv import load_dotenv
from falkordb import FalkorDB

load_dotenv()


class GraphClient:
    def __init__(self):
        self.host = os.getenv("FALKORDB_HOST", "localhost")
        self.port = int(os.getenv("FALKORDB_PORT", "6379"))
        self.username = os.getenv("FALKORDB_USERNAME") or None
        self.password = os.getenv("FALKORDB_PASSWORD") or None

        self.db = FalkorDB(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
        )

    def get_graph(self, graph_name: str = "novatech"):
        return self.db.select_graph(graph_name)

    def query(self, cypher: str, graph_name: str = "novatech"):
        graph = self.get_graph(graph_name)
        return graph.query(cypher)


graph_client = GraphClient()