from typing import Any, Dict, List, Optional

from graph.queries import run_cypher


class GraphPathEngine:
    """
    Deterministic graph-path and evidence engine.

    Phase 17:
    - Avoids broad [*1..N] traversal for the hero scenario.
    - Selects canonical entities where possible.
    - Preserves actual FalkorDB relationship types.
    - Builds semantic evidence branches rather than inventing
      relationships that do not exist in the graph.
    """

    def __init__(self, graph_name: str = "novatech"):
        self.graph_name = graph_name

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _escape(value: str) -> str:
        return str(value).replace("\\", "\\\\").replace("'", "\\'")

    @staticmethod
    def _node_label(node: Dict[str, Any]) -> str:
        if not node:
            return "Unknown"

        name = node.get("name")
        title = node.get("title")

        if name:
            return str(name)

        if title:
            return str(title)

        node_id = node.get("id")
        if node_id is not None:
            return str(node_id)

        return "Unknown"

    @classmethod
    def _format_relationship(
        cls,
        source: Dict[str, Any],
        relationship: Dict[str, Any],
        target: Dict[str, Any],
    ) -> str:
        source_name = cls._node_label(source)
        target_name = cls._node_label(target)
        rel_type = relationship.get("type", "RELATED_TO")

        return f"{source_name} -[{rel_type}]-> {target_name}"

    # ------------------------------------------------------------------
    # Generic path search
    # ------------------------------------------------------------------

    def find_paths(
        self,
        source_name: str,
        target_name: str,
        max_hops: int = 4,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Generic graph traversal.

        This remains available for normal graph exploration, but is NOT
        used for the deterministic Phase 17 hero path.
        """

        source = self._escape(source_name)
        target = self._escape(target_name)

        query = f"""
        MATCH p=(
            source {{name: '{source}'}}
        )-[*1..{int(max_hops)}]-(
            target {{name: '{target}'}}
        )
        WITH p,
             nodes(p) AS path_nodes,
             relationships(p) AS path_relationships
        RETURN path_nodes, path_relationships
        LIMIT {int(limit)}
        """

        result = run_cypher(query, self.graph_name)

        return self._normalize_rows(result)

    # ------------------------------------------------------------------
    # Normalize generic FalkorDB paths
    # ------------------------------------------------------------------

    def _normalize_rows(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        paths: List[Dict[str, Any]] = []

        for row in result.get("rows", []):
            if len(row) < 2:
                continue

            raw_nodes = row[0]
            raw_relationships = row[1]

            nodes = self._normalize_nodes(raw_nodes)
            relationships = self._normalize_relationships(raw_relationships)

            if not nodes:
                continue

            display_parts = []

            for index, node in enumerate(nodes):
                display_parts.append(self._node_label(node))

                if index < len(relationships):
                    display_parts.append(
                        f"-[{relationships[index].get('type', 'RELATED_TO')}]->"
                    )

            display = " ".join(display_parts)

            paths.append(
                {
                    "nodes": nodes,
                    "relationships": relationships,
                    "hops": max(len(nodes) - 1, 0),
                    "display": display,
                }
            )

        return paths

    @staticmethod
    def _normalize_nodes(value: Any) -> List[Dict[str, Any]]:
        if value is None:
            return []

        if isinstance(value, dict):
            return [value]

        if isinstance(value, (list, tuple)):
            nodes = []

            for item in value:
                if isinstance(item, dict):
                    nodes.append(item)
                else:
                    nodes.append(
                        {
                            "value": str(item),
                        }
                    )

            return nodes

        return [
            {
                "value": str(value),
            }
        ]

    @staticmethod
    def _normalize_relationships(value: Any) -> List[Dict[str, Any]]:
        if value is None:
            return []

        if isinstance(value, dict):
            return [value]

        if isinstance(value, (list, tuple)):
            relationships = []

            for item in value:
                if isinstance(item, dict):
                    relationships.append(item)
                else:
                    relationships.append(
                        {
                            "type": str(item),
                        }
                    )

            return relationships

        return [
            {
                "type": str(value),
            }
        ]

    # ------------------------------------------------------------------
    # Deterministic hero path
    # ------------------------------------------------------------------

    def hero_path(self) -> Dict[str, Any]:
        """
        Resolve the canonical NovaTech hero scenario.

        We intentionally return semantic evidence branches instead of
        pretending that every business concept is connected by a direct
        graph edge.

        Branch A:
            Checkout Service
                -> Payment Service
                -> Checkout failures increased

        Branch B:
            Payment Service
                -> Payment Service Migration
                -> canonical architecture Decision
                -> Alice Chen

        Branch C:
            Payment Service
                -> Maya Singh (current owner)
        """

        evidence: List[Dict[str, Any]] = []
        nodes_by_key: Dict[str, Dict[str, Any]] = {}
        relationships: List[Dict[str, Any]] = []

        # --------------------------------------------------------------
        # 1. Checkout Service -> Payment Service
        # --------------------------------------------------------------

        dependency_query = """
        MATCH (payment:Service)-[r:DEPENDS_ON]->(checkout:Service)
        WHERE payment.name = 'Payment Service'
          AND checkout.name = 'Checkout Service'
        RETURN
            payment,
            r,
            checkout
        LIMIT 1
        """

        dependency_result = run_cypher(
            dependency_query,
            self.graph_name,
        )

        dependency_rows = dependency_result.get("rows", [])

        if dependency_rows:
            row = dependency_rows[0]

            if len(row) >= 3:
                payment = self._as_node(row[0])
                relationship = self._as_relationship(row[1])
                checkout = self._as_node(row[2])

                nodes_by_key["payment"] = payment
                nodes_by_key["checkout"] = checkout

                relationships.append(
                    {
                        "source": self._node_label(payment),
                        "type": relationship.get(
                            "type",
                            "DEPENDS_ON",
                        ),
                        "target": self._node_label(checkout),
                    }
                )

                evidence.append(
                    {
                        "type": "dependency",
                        "source": self._node_label(payment),
                        "relationship": relationship.get(
                            "type",
                            "DEPENDS_ON",
                        ),
                        "target": self._node_label(checkout),
                    }
                )

        # --------------------------------------------------------------
        # 2. Payment Service -> canonical Incident
        # --------------------------------------------------------------

        incident_query = """
        MATCH (payment:Service)-[r:INVOLVES]->(incident:Incident)
        WHERE payment.name = 'Payment Service'
          AND incident.name IS NULL
          AND incident.title = 'Checkout failures increased'
        RETURN
            payment,
            r,
            incident
        LIMIT 1
        """

        incident_result = run_cypher(
            incident_query,
            self.graph_name,
        )

        incident_rows = incident_result.get("rows", [])

        if incident_rows:
            row = incident_rows[0]

            if len(row) >= 3:
                payment = self._as_node(row[0])
                relationship = self._as_relationship(row[1])
                incident = self._as_node(row[2])

                nodes_by_key["payment"] = payment
                nodes_by_key["incident"] = incident

                relationships.append(
                    {
                        "source": self._node_label(payment),
                        "type": relationship.get(
                            "type",
                            "INVOLVES",
                        ),
                        "target": self._node_label(incident),
                    }
                )

                evidence.append(
                    {
                        "type": "incident",
                        "source": self._node_label(payment),
                        "relationship": relationship.get(
                            "type",
                            "INVOLVES",
                        ),
                        "target": self._node_label(incident),
                    }
                )

        # --------------------------------------------------------------
        # 3. Payment Service -> Migration
        # --------------------------------------------------------------

        migration_query = """
        MATCH (migration:Project)-[r:PRODUCES]->(payment:Service)
        WHERE migration.name = 'Payment Service Migration'
          AND payment.name = 'Payment Service'
        RETURN
            migration,
            r,
            payment
        LIMIT 1
        """

        migration_result = run_cypher(
            migration_query,
            self.graph_name,
        )

        migration_rows = migration_result.get("rows", [])

        if migration_rows:
            row = migration_rows[0]

            if len(row) >= 3:
                migration = self._as_node(row[0])
                relationship = self._as_relationship(row[1])
                payment = self._as_node(row[2])

                nodes_by_key["migration"] = migration
                nodes_by_key["payment"] = payment

                relationships.append(
                    {
                        "source": self._node_label(migration),
                        "type": relationship.get(
                            "type",
                            "PRODUCES",
                        ),
                        "target": self._node_label(payment),
                    }
                )

                evidence.append(
                    {
                        "type": "architecture_project",
                        "source": self._node_label(migration),
                        "relationship": relationship.get(
                            "type",
                            "PRODUCES",
                        ),
                        "target": self._node_label(payment),
                    }
                )

        # --------------------------------------------------------------
        # 4. Canonical Decision -> Migration
        # --------------------------------------------------------------

        decision_query = """
        MATCH (migration:Project)-[r:IMPLEMENTED_BY]->(decision:Decision)
        WHERE migration.name = 'Payment Service Migration'
          AND decision.name IS NULL
          AND decision.title =
              'Move payment processing to dedicated Payment Service'
        RETURN
            migration,
            r,
            decision
        LIMIT 1
        """

        decision_result = run_cypher(
            decision_query,
            self.graph_name,
        )

        decision_rows = decision_result.get("rows", [])

        if decision_rows:
            row = decision_rows[0]

            if len(row) >= 3:
                migration = self._as_node(row[0])
                relationship = self._as_relationship(row[1])
                decision = self._as_node(row[2])

                nodes_by_key["migration"] = migration
                nodes_by_key["decision"] = decision

                relationships.append(
                    {
                        "source": self._node_label(migration),
                        "type": relationship.get(
                            "type",
                            "IMPLEMENTED_BY",
                        ),
                        "target": self._node_label(decision),
                    }
                )

                evidence.append(
                    {
                        "type": "architecture_decision",
                        "source": self._node_label(migration),
                        "relationship": relationship.get(
                            "type",
                            "IMPLEMENTED_BY",
                        ),
                        "target": self._node_label(decision),
                    }
                )

        # --------------------------------------------------------------
        # 5. Decision -> Alice Chen
        # --------------------------------------------------------------

        decision_owner_query = """
        MATCH (decision:Decision)-[r:MADE_BY]->(person:Person)
        WHERE decision.name IS NULL
          AND decision.title =
              'Move payment processing to dedicated Payment Service'
          AND person.name = 'Alice Chen'
        RETURN
            decision,
            r,
            person
        LIMIT 1
        """

        decision_owner_result = run_cypher(
            decision_owner_query,
            self.graph_name,
        )

        decision_owner_rows = decision_owner_result.get("rows", [])

        if decision_owner_rows:
            row = decision_owner_rows[0]

            if len(row) >= 3:
                decision = self._as_node(row[0])
                relationship = self._as_relationship(row[1])
                person = self._as_node(row[2])

                nodes_by_key["decision"] = decision
                nodes_by_key["decision_maker"] = person

                relationships.append(
                    {
                        "source": self._node_label(decision),
                        "type": relationship.get(
                            "type",
                            "MADE_BY",
                        ),
                        "target": self._node_label(person),
                    }
                )

                evidence.append(
                    {
                        "type": "decision_maker",
                        "source": self._node_label(decision),
                        "relationship": relationship.get(
                            "type",
                            "MADE_BY",
                        ),
                        "target": self._node_label(person),
                    }
                )

        # --------------------------------------------------------------
        # 6. Payment Service -> Maya Singh
        # --------------------------------------------------------------

        owner_query = """
        MATCH (person:Person)-[r:OWNS]->(payment:Service)
        WHERE person.name = 'Maya Singh'
          AND payment.name = 'Payment Service'
        RETURN
            person,
            r,
            payment
        LIMIT 1
        """

        owner_result = run_cypher(
            owner_query,
            self.graph_name,
        )

        owner_rows = owner_result.get("rows", [])

        if owner_rows:
            row = owner_rows[0]

            if len(row) >= 3:
                person = self._as_node(row[0])
                relationship = self._as_relationship(row[1])
                payment = self._as_node(row[2])

                nodes_by_key["owner"] = person
                nodes_by_key["payment"] = payment

                relationships.append(
                    {
                        "source": self._node_label(person),
                        "type": relationship.get(
                            "type",
                            "OWNS",
                        ),
                        "target": self._node_label(payment),
                    }
                )

                evidence.append(
                    {
                        "type": "current_owner",
                        "source": self._node_label(person),
                        "relationship": relationship.get(
                            "type",
                            "OWNS",
                        ),
                        "target": self._node_label(payment),
                    }
                )

        # --------------------------------------------------------------
        # Build human-readable evidence branches
        # --------------------------------------------------------------

        branches: List[Dict[str, Any]] = []

        if "checkout" in nodes_by_key and "payment" in nodes_by_key:
            branches.append(
                {
                    "name": "service_dependency",
                    "display": (
                        "Payment Service -[DEPENDS_ON]-> "
                        "Checkout Service"
                    ),
                    "nodes": [
                        nodes_by_key["payment"],
                        nodes_by_key["checkout"],
                    ],
                }
            )

        if "payment" in nodes_by_key and "incident" in nodes_by_key:
            branches.append(
                {
                    "name": "incident",
                    "display": (
                        "Payment Service -[INVOLVES]-> "
                        "Checkout failures increased"
                    ),
                    "nodes": [
                        nodes_by_key["payment"],
                        nodes_by_key["incident"],
                    ],
                }
            )

        if "migration" in nodes_by_key and "payment" in nodes_by_key:
            branches.append(
                {
                    "name": "migration",
                    "display": (
                        "Payment Service Migration -[PRODUCES]-> "
                        "Payment Service"
                    ),
                    "nodes": [
                        nodes_by_key["migration"],
                        nodes_by_key["payment"],
                    ],
                }
            )

        if "migration" in nodes_by_key and "decision" in nodes_by_key:
            branches.append(
                {
                    "name": "decision",
                    "display": (
                        "Payment Service Migration -[IMPLEMENTED_BY]-> "
                        "Move payment processing to dedicated Payment Service"
                    ),
                    "nodes": [
                        nodes_by_key["migration"],
                        nodes_by_key["decision"],
                    ],
                }
            )

        if "decision" in nodes_by_key and "decision_maker" in nodes_by_key:
            branches.append(
                {
                    "name": "decision_maker",
                    "display": (
                        "Move payment processing to dedicated Payment Service "
                        "-[MADE_BY]-> Alice Chen"
                    ),
                    "nodes": [
                        nodes_by_key["decision"],
                        nodes_by_key["decision_maker"],
                    ],
                }
            )

        if "owner" in nodes_by_key and "payment" in nodes_by_key:
            branches.append(
                {
                    "name": "current_owner",
                    "display": (
                        "Maya Singh -[OWNS]-> Payment Service"
                    ),
                    "nodes": [
                        nodes_by_key["owner"],
                        nodes_by_key["payment"],
                    ],
                }
            )

        # --------------------------------------------------------------
        # Deterministic confidence
        # --------------------------------------------------------------

        expected_evidence = 6
        evidence_count = len(evidence)

        confidence = round(
            min(evidence_count / expected_evidence, 1.0),
            2,
        )

        unknowns: List[str] = []

        if "incident" not in nodes_by_key:
            unknowns.append(
                "The canonical checkout failure incident could not be established."
            )

        if "decision" not in nodes_by_key:
            unknowns.append(
                "The canonical payment architecture decision could not be established."
            )

        if "decision_maker" not in nodes_by_key:
            unknowns.append(
                "The decision maker could not be established."
            )

        if "owner" not in nodes_by_key:
            unknowns.append(
                "The current Payment Service owner could not be established."
            )

        # There is intentionally no direct Incident -> Migration claim.
        unknowns.append(
            "No direct Incident-to-Migration relationship was established; "
            "the incident and architecture evidence are therefore represented "
            "as separate graph evidence branches."
        )

        return {
            "success": evidence_count > 0,
            "source": "falkordb",
            "graph_name": self.graph_name,
            "evidence": evidence,
            "branches": branches,
            "nodes": list(nodes_by_key.values()),
            "relationships": relationships,
            "path": branches,
            "path_count": len(branches),
            "evidence_count": evidence_count,
            "confidence": confidence,
            "unknowns": unknowns,
        }

    # ------------------------------------------------------------------
    # Generic exploration
    # ------------------------------------------------------------------

    def explore(
        self,
        entity_name: str,
        max_hops: int = 2,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        name = self._escape(entity_name)

        query = f"""
        MATCH p=(
            source {{name: '{name}'}}
        )-[*1..{int(max_hops)}]-(
            target
        )
        WITH p,
             nodes(p) AS path_nodes,
             relationships(p) AS path_relationships
        RETURN path_nodes, path_relationships
        LIMIT {int(limit)}
        """

        result = run_cypher(query, self.graph_name)

        return self._normalize_rows(result)

    # ------------------------------------------------------------------
    # Compatibility helpers
    # ------------------------------------------------------------------

    def normalize_path(self, path: Any) -> Dict[str, Any]:
        if isinstance(path, dict):
            nodes = self._normalize_nodes(path.get("nodes", []))
            relationships = self._normalize_relationships(
                path.get("relationships", [])
            )

            display_parts = []

            for index, node in enumerate(nodes):
                display_parts.append(self._node_label(node))

                if index < len(relationships):
                    display_parts.append(
                        f"-[{relationships[index].get('type', 'RELATED_TO')}]->"
                    )

            return {
                "nodes": nodes,
                "relationships": relationships,
                "hops": max(len(nodes) - 1, 0),
                "display": " ".join(display_parts),
            }

        return {
            "nodes": [],
            "relationships": [],
            "hops": 0,
            "display": str(path),
        }

    def format_path(self, path: Dict[str, Any]) -> str:
        normalized = self.normalize_path(path)

        if normalized.get("display"):
            return normalized["display"]

        return ""

    # ------------------------------------------------------------------
    # FalkorDB object adapters
    # ------------------------------------------------------------------

    @staticmethod
    def _as_node(value: Any) -> Dict[str, Any]:
        if isinstance(value, dict):
            return value

        if value is None:
            return {}

        result: Dict[str, Any] = {}

        try:
            result["id"] = getattr(value, "id", None)
        except Exception:
            pass

        try:
            result["labels"] = list(getattr(value, "labels", []))
        except Exception:
            result["labels"] = []

        try:
            properties = getattr(value, "properties", None)

            if isinstance(properties, dict):
                result.update(properties)
        except Exception:
            pass

        if not result:
            result["value"] = str(value)

        return result

    @staticmethod
    def _as_relationship(value: Any) -> Dict[str, Any]:
        if isinstance(value, dict):
            return value

        if value is None:
            return {}

        result: Dict[str, Any] = {}

        try:
            result["id"] = getattr(value, "id", None)
        except Exception:
            pass

        try:
            result["type"] = getattr(value, "type", None)
        except Exception:
            pass

        try:
            properties = getattr(value, "properties", None)

            if isinstance(properties, dict):
                result["properties"] = properties
        except Exception:
            pass

        if not result:
            result["type"] = str(value)

        return result