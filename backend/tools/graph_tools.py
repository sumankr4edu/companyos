from graph.queries import run_cypher


class GraphTools:
    """
    Controlled graph intelligence tools.

    These tools are the bridge between agents and FalkorDB.
    """

    def __init__(self, graph_name: str = "novatech"):
        self.graph_name = graph_name

    # ============================================================
    # SEARCH
    # ============================================================

    def search(self, text: str, limit: int = 10):
        """
        Search nodes by name, title, description, or content.
        """

        text = text.replace("\\", "\\\\").replace("'", "\\'")
        limit = max(1, min(int(limit), 100))

        query = f"""
        MATCH (n)
        WHERE
            toString(n.name) CONTAINS '{text}'
            OR toString(n.title) CONTAINS '{text}'
            OR toString(n.description) CONTAINS '{text}'
            OR toString(n.content) CONTAINS '{text}'
        RETURN
            labels(n) AS labels,
            n.name AS name,
            n.title AS title,
            n.description AS description
        LIMIT {limit}
        """

        return run_cypher(query, self.graph_name)

    # ============================================================
    # ENTITY
    # ============================================================

    def find_entity(self, name: str):
        """
        Find an entity and its immediate relationships.
        """

        name = name.replace("\\", "\\\\").replace("'", "\\'")

        query = f"""
        MATCH (n)
        WHERE n.name = '{name}'
        OPTIONAL MATCH (n)-[r]-(connected)
        RETURN
            labels(n) AS labels,
            n.name AS name,
            type(r) AS relationship,
            labels(connected) AS connected_labels,
            connected.name AS connected_name
        """

        return run_cypher(query, self.graph_name)

    # ============================================================
    # NEIGHBORS
    # ============================================================

    def neighbors(
        self,
        entity_name: str,
        relationship: str | None = None,
        limit: int = 50,
    ):
        """
        Retrieve entities directly connected to another entity.
        """

        entity_name = entity_name.replace("\\", "\\\\").replace("'", "\\'")
        limit = max(1, min(int(limit), 100))

        if relationship:
            relationship = relationship.upper()

            # Allow only valid relationship-name characters.
            if not relationship.replace("_", "").isalnum():
                raise ValueError("Invalid relationship type.")

            query = f"""
            MATCH (n {{name: '{entity_name}'}})
                  -[r:{relationship}]->
                  (connected)
            RETURN
                type(r) AS relationship,
                labels(connected) AS labels,
                connected.name AS name
            LIMIT {limit}
            """

        else:
            query = f"""
            MATCH (n {{name: '{entity_name}'}})
                  -[r]-
                  (connected)
            RETURN
                type(r) AS relationship,
                labels(connected) AS labels,
                connected.name AS name
            LIMIT {limit}
            """

        return run_cypher(query, self.graph_name)

    # ============================================================
    # DEPENDENCIES
    # ============================================================

    def dependencies(
        self,
        service_name: str,
        max_hops: int = 3,
    ):
        """
        Trace service dependencies through the company graph.
        """

        service_name = service_name.replace("\\", "\\\\").replace("'", "\\'")

        max_hops = max(
            1,
            min(int(max_hops), 8),
        )

        query = f"""
        MATCH path =
            (service {{name: '{service_name}'}})
            -[:DEPENDS_ON|CALLS|USES*1..{max_hops}]->
            (dependency)

        RETURN
            service.name AS source,
            dependency.name AS dependency,
            length(path) AS hops
        ORDER BY hops
        """

        return run_cypher(query, self.graph_name)

    # ============================================================
    # SHORTEST / BOUNDED PATH
    # ============================================================

    def shortest_path(
        self,
        source: str,
        target: str,
        max_hops: int = 8,
    ):
        """
        Find a bounded relationship path between two entities.

        We intentionally use a bounded variable-length traversal
        instead of shortestPath()/shortestPaths() because FalkorDB
        has restrictions around shortest-path expressions.
        """

        source = source.replace("\\", "\\\\").replace("'", "\\'")
        target = target.replace("\\", "\\\\").replace("'", "\\'")

        max_hops = max(
            1,
            min(int(max_hops), 20),
        )

        query = f"""
        MATCH p =
            (a {{name: '{source}'}})
            -[*1..{max_hops}]-
            (b {{name: '{target}'}})

        RETURN
            p
        LIMIT 1
        """

        return run_cypher(query, self.graph_name)

    # ============================================================
    # SUBGRAPH
    # ============================================================

    def subgraph(
        self,
        entity_name: str,
        depth: int = 2,
    ):
        """
        Retrieve a bounded subgraph around an entity.
        """

        entity_name = entity_name.replace("\\", "\\\\").replace("'", "\\'")

        depth = max(
            1,
            min(int(depth), 4),
        )

        query = f"""
        MATCH path =
            (root {{name: '{entity_name}'}})
            -[*1..{depth}]-
            (connected)

        UNWIND nodes(path) AS node

        WITH DISTINCT node

        RETURN
            labels(node) AS labels,
            node.name AS name,
            node.title AS title,
            node.description AS description
        """

        return run_cypher(query, self.graph_name)

    # ============================================================
    # OWNERSHIP
    # ============================================================

    def find_owner(self, entity_name: str):
        """
        Determine who owns an entity/system/project.
        """

        entity_name = entity_name.replace("\\", "\\\\").replace("'", "\\'")

        query = f"""
        MATCH
            (entity {{name: '{entity_name}'}})
            <-[:OWNS]-
            (owner)

        RETURN
            labels(owner) AS labels,
            owner.name AS owner
        """

        return run_cypher(query, self.graph_name)

    # ============================================================
    # RELATED PEOPLE
    # ============================================================

    def find_people_connected_to(
        self,
        entity_name: str,
    ):
        """
        Find people connected to an entity through
        ownership, work, contribution, authorship,
        assignment, or involvement.
        """

        entity_name = entity_name.replace("\\", "\\\\").replace("'", "\\'")

        query = f"""
        MATCH
            (entity {{name: '{entity_name}'}})
            -[r]-
            (person:Person)

        RETURN
            person.name AS person,
            type(r) AS relationship
        """

        return run_cypher(query, self.graph_name)