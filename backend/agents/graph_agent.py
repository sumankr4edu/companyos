from graph.queries import run_cypher
from tools.graph_tools import GraphTools

class GraphAgent:
    """
    Graph-first reasoning agent.

    The agent retrieves evidence from FalkorDB before
    any answer is generated.
    """

    def __init__(self, graph_name: str = "novatech"):
        self.graph_name = graph_name
        self.tools = GraphTools(graph_name)

    def search_people(self, name: str | None = None):
        if name:
            safe_name = name.replace("'", "\\'")
            query = f"""
            MATCH (p:Person)
            WHERE toLower(p.name) CONTAINS toLower('{safe_name}')
            RETURN p.id, p.name, p.role
            """
        else:
            query = """
            MATCH (p:Person)
            RETURN p.id, p.name, p.role
            """

        return run_cypher(query, self.graph_name)

    def search_services(self):
        query = """
        MATCH (s:Service)
        RETURN s.id, s.name, s.status
        """

        return run_cypher(query, self.graph_name)

    def find_incidents(self):
        query = """
        MATCH (i:Incident)
        RETURN i.id, i.title, i.severity, i.status
        """

        return run_cypher(query, self.graph_name)

    def trace_service_dependencies(self, service_name: str):
        safe_name = service_name.replace("'", "\\'")

        query = f"""
        MATCH path =
            (s:Service {{name: '{safe_name}'}})
            -[:DEPENDS_ON*1..5]->
            (dependency)
        RETURN path
        """

        return run_cypher(query, self.graph_name)

    def find_affected_systems(self, incident_title: str):
        safe_title = incident_title.replace("'", "\\'")

        query = f"""
        MATCH
            (i:Incident {{title: '{safe_title}'}})
            -[:AFFECTS|INVOLVES*1..3]->
            (entity)
        RETURN i.title, labels(entity), entity.name
        """

        return run_cypher(query, self.graph_name)

    def investigate_checkout_failure(self):
        query = """
        MATCH
            (checkout:Service {name: 'Checkout Service'})
            -[:DEPENDS_ON]->
            (payment:Service),
            (incident:Incident)-[:INVOLVES]->(payment),
            (alice:Person)-[:WORKED_ON]->(migration:Project),
            (migration)-[:PRODUCES]->(payment),
            (decision:Decision)-[:IMPLEMENTED_BY]->(migration),
            (decision)-[:MADE_BY]->(alice),
            (maya:Person)-[:OWNS]->(payment)

        RETURN
            checkout.name AS affected_service,
            payment.name AS dependency,
            incident.title AS incident,
            migration.name AS migration,
            decision.title AS decision,
            alice.name AS decision_maker,
            maya.name AS current_owner
        """

        return run_cypher(query, self.graph_name)

    def get_checkout_reasoning_path(self):
        """
        Returns the multi-hop reasoning path for the
        Checkout Service incident investigation.
        """

        query = """
        MATCH
            (checkout:Service {name: 'Checkout Service'})
            -[:DEPENDS_ON]->
            (payment:Service),
            (incident:Incident)-[:INVOLVES]->(payment),
            (alice:Person)-[:WORKED_ON]->(migration:Project),
            (migration)-[:PRODUCES]->(payment),
            (decision:Decision)-[:IMPLEMENTED_BY]->(migration),
            (decision)-[:MADE_BY]->(alice),
            (maya:Person)-[:OWNS]->(payment)

        RETURN
            checkout.name AS affected_service,
            payment.name AS dependency,
            incident.title AS incident,
            migration.name AS migration,
            decision.title AS decision,
            alice.name AS decision_maker,
            maya.name AS current_owner
        """

        return run_cypher(
            query,
            self.graph_name,
        )

        # ============================================================
    # PHASE 7 — GRAPH INTELLIGENCE TOOLS
    # ============================================================

    def search_graph(self, text: str, limit: int = 10):
        """
        Search the company graph for entities matching text.
        """
        return self.tools.search(text, limit)

    def find_entity(self, name: str):
        """
        Find an entity and its immediate relationships.
        """
        return self.tools.find_entity(name)

    def get_neighbors(
        self,
        entity_name: str,
        relationship: str | None = None,
        limit: int = 50,
    ):
        """
        Retrieve entities connected to an entity.
        """
        return self.tools.neighbors(
            entity_name,
            relationship,
            limit,
        )

    def get_dependencies(
        self,
        service_name: str,
        max_hops: int = 3,
    ):
        """
        Trace dependencies of a service.
        """
        return self.tools.dependencies(
            service_name,
            max_hops,
        )

    def get_shortest_path(
        self,
        source: str,
        target: str,
    ):
        """
        Find the shortest graph path between two entities.
        """
        return self.tools.shortest_path(
            source,
            target,
        )

    def get_subgraph(
        self,
        entity_name: str,
        depth: int = 2,
    ):
        """
        Retrieve a bounded subgraph around an entity.
        """
        return self.tools.subgraph(
            entity_name,
            depth,
        )

    def get_owner(self, entity_name: str):
        """
        Find the current owner of an entity.
        """
        return self.tools.find_owner(entity_name)

    def get_connected_people(self, entity_name: str):
        """
        Find people connected to an entity.
        """
        return self.tools.find_people_connected_to(entity_name)