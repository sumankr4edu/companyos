from typing import Any, Dict, List

from graph.queries import run_cypher


class GraphAlgorithms:
    """
    Graph intelligence algorithms for CompanyOS.

    These algorithms operate directly on FalkorDB and are used
    to answer graph-native questions such as:

        - Who knows the most about a system?
        - What breaks if a service goes down?
        - Who is most connected to a project?
        - What entities belong to the same graph component?
    """

    def __init__(self, graph_name: str = "novatech"):
        self.graph_name = graph_name

    # =========================================================
    # Basic centrality
    # =========================================================

    def degree_centrality(
        self,
        entity_name: str,
        limit: int = 20,
    ) -> Dict[str, Any]:

        safe_name = self._escape(entity_name)

        query = f"""
        MATCH (n {{name: '{safe_name}'}})
        OPTIONAL MATCH (n)-[r]-(connected)
        RETURN
            n.name AS entity,
            count(r) AS degree,
            collect(DISTINCT connected.name) AS connected_entities
        LIMIT 1
        """

        result = run_cypher(
            query,
            self.graph_name,
        )

        return {
            "entity": entity_name,
            "result": result,
        }

    # =========================================================
    # People centrality
    # =========================================================

    def people_centrality(
        self,
        limit: int = 20,
    ) -> Dict[str, Any]:

        limit = max(
            1,
            min(int(limit), 100),
        )

        query = f"""
        MATCH (p:Person)
        OPTIONAL MATCH (p)-[r]-(connected)
        WITH
            p,
            count(r) AS connections,
            collect(DISTINCT connected.name) AS related_entities
        RETURN
            p.name AS person,
            connections,
            related_entities
        ORDER BY connections DESC
        LIMIT {limit}
        """

        result = run_cypher(
            query,
            self.graph_name,
        )

        return {
            "type": "people_centrality",
            "result": result,
        }

    # =========================================================
    # System centrality
    # =========================================================

    def system_centrality(
        self,
        limit: int = 20,
    ) -> Dict[str, Any]:

        limit = max(
            1,
            min(int(limit), 100),
        )

        query = f"""
        MATCH (s:Service)
        OPTIONAL MATCH (s)-[r]-(connected)
        WITH
            s,
            count(r) AS connections,
            collect(DISTINCT connected.name) AS related_entities
        RETURN
            s.name AS service,
            connections,
            related_entities
        ORDER BY connections DESC
        LIMIT {limit}
        """

        result = run_cypher(
            query,
            self.graph_name,
        )

        return {
            "type": "system_centrality",
            "result": result,
        }

    # =========================================================
    # Expertise ranking
    # =========================================================

    def expertise_ranking(
        self,
        entity_name: str,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        Rank people based on their graph relationships to an entity.

        Signals:

        WORKED_ON       → strong expertise
        CONTRIBUTED_TO  → strong expertise
        OWNS            → strongest operational ownership
        INVOLVES        → incident experience
        AUTHORED        → documentation knowledge
        MEMBER_OF       → weak contextual relationship

        This is intentionally explainable rather than a black-box
        score.
        """

        safe_name = self._escape(entity_name)

        limit = max(
            1,
            min(int(limit), 50),
        )

        query = f"""
        MATCH (target {{name: '{safe_name}'}})
        MATCH (person:Person)-[r]-(target)

        WITH
            person,
            collect(DISTINCT type(r)) AS relationships

        WITH
            person,
            relationships,

            (
                CASE
                    WHEN 'OWNS' IN relationships
                    THEN 10
                    ELSE 0
                END
                +
                CASE
                    WHEN 'WORKED_ON' IN relationships
                    THEN 8
                    ELSE 0
                END
                +
                CASE
                    WHEN 'CONTRIBUTED_TO' IN relationships
                    THEN 7
                    ELSE 0
                END
                +
                CASE
                    WHEN 'INVOLVES' IN relationships
                    THEN 5
                    ELSE 0
                END
                +
                CASE
                    WHEN 'AUTHORED' IN relationships
                    THEN 4
                    ELSE 0
                END
                +
                CASE
                    WHEN 'MEMBER_OF' IN relationships
                    THEN 1
                    ELSE 0
                END
            ) AS expertise_score

        RETURN
            person.name AS person,
            expertise_score,
            relationships

        ORDER BY expertise_score DESC

        LIMIT {limit}
        """

        result = run_cypher(
            query,
            self.graph_name,
        )

        return {
            "type": "expertise_ranking",
            "entity": entity_name,
            "result": result,
        }

    # =========================================================
    # Dependency blast radius
    # =========================================================

    def dependency_blast_radius(
        self,
        service_name: str,
        max_hops: int = 4,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Find services that depend on the selected service.

        Example:

            Payment Service
                    ↑
              Checkout Service
                    ↑
               API Gateway

        If Payment Service fails, the reverse dependency traversal
        identifies potentially affected systems.
        """

        safe_name = self._escape(service_name)

        max_hops = max(
            1,
            min(int(max_hops), 8),
        )

        limit = max(
            1,
            min(int(limit), 200),
        )

        query = f"""
        MATCH (target:Service {{name: '{safe_name}'}})
        OPTIONAL MATCH path =
            (dependent:Service)
            -[:DEPENDS_ON*1..{max_hops}]->
            (target)

        WITH
            target,
            dependent,
            path

        WHERE dependent IS NOT NULL

        RETURN DISTINCT
            target.name AS target_service,
            dependent.name AS affected_service,
            length(path) AS hops

        ORDER BY hops ASC

        LIMIT {limit}
        """

        result = run_cypher(
            query,
            self.graph_name,
        )

        return {
            "type": "dependency_blast_radius",
            "service": service_name,
            "max_hops": max_hops,
            "result": result,
        }

    # =========================================================
    # Forward dependencies
    # =========================================================

    def dependencies(
        self,
        service_name: str,
        max_hops: int = 4,
        limit: int = 100,
    ) -> Dict[str, Any]:

        safe_name = self._escape(service_name)

        max_hops = max(
            1,
            min(int(max_hops), 8),
        )

        limit = max(
            1,
            min(int(limit), 200),
        )

        query = f"""
        MATCH (service:Service {{name: '{safe_name}'}})
        OPTIONAL MATCH path =
            (service)-[:DEPENDS_ON*1..{max_hops}]->
            (dependency:Service)

        WHERE dependency IS NOT NULL

        RETURN DISTINCT
            service.name AS service,
            dependency.name AS dependency,
            length(path) AS hops

        ORDER BY hops ASC

        LIMIT {limit}
        """

        result = run_cypher(
            query,
            self.graph_name,
        )

        return {
            "type": "dependencies",
            "service": service_name,
            "result": result,
        }

    # =========================================================
    # Connected component
    # =========================================================

    def connected_component(
        self,
        entity_name: str,
        max_hops: int = 6,
        limit: int = 100,
    ) -> Dict[str, Any]:

        safe_name = self._escape(entity_name)

        max_hops = max(
            1,
            min(int(max_hops), 8),
        )

        limit = max(
            1,
            min(int(limit), 200),
        )

        query = f"""
        MATCH (root {{name: '{safe_name}'}})
        OPTIONAL MATCH path =
            (root)-[*1..{max_hops}]-(connected)

        WHERE connected IS NOT NULL

        RETURN DISTINCT
            labels(connected) AS labels,
            connected.name AS entity,
            connected.id AS id

        LIMIT {limit}
        """

        result = run_cypher(
            query,
            self.graph_name,
        )

        return {
            "type": "connected_component",
            "root": entity_name,
            "result": result,
        }

    # =========================================================
    # Relationship counts
    # =========================================================

    def relationship_counts(
        self,
    ) -> Dict[str, Any]:

        query = """
        MATCH ()-[r]->()
        RETURN
            type(r) AS relationship,
            count(*) AS count
        ORDER BY count DESC
        """

        result = run_cypher(
            query,
            self.graph_name,
        )

        return {
            "type": "relationship_counts",
            "result": result,
        }

    # =========================================================
    # Utility
    # =========================================================

    @staticmethod
    def _escape(value: str) -> str:
        """
        Escape a value before inserting it into a controlled
        Cypher template.

        GraphAlgorithms only accepts internally generated queries.
        """

        return (
            str(value)
            .replace("\\", "\\\\")
            .replace("'", "\\'")
        )