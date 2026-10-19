from typing import Any, List, Optional


class CypherGenerator:
    """
    Converts a validated QueryPlan into bounded, graph-grounded Cypher.

    Design goals:
    - FalkorDB remains the source of truth.
    - Queries are entity-constrained whenever possible.
    - Results are always bounded.
    - No write operations are generated.
    - Hero/demo questions should produce focused evidence instead
      of scanning the entire graph.
    """

    MAX_RESULTS = 25
    MAX_PATH_LENGTH = 8

    def __init__(self, graph_name: str = "novatech"):
        self.graph_name = graph_name

    # ============================================================
    # Public API
    # ============================================================

    def generate(self, plan: Any) -> str:
        intent = getattr(plan, "intent", "") or ""
        entities = getattr(plan, "entities", []) or []

        if intent == "ownership_expertise":
            return self._ownership(entities)

        if intent == "dependency_analysis":
            return self._dependencies(entities)

        if intent == "blast_radius":
            return self._blast_radius(entities)

        if intent == "decision_reason":
            return self._decision_reason(entities)

        if intent == "incident_investigation":
            return self._incident_investigation(entities)

        if intent == "centrality":
            return self._centrality(entities)

        if intent == "connected_component":
            return self._connected_component(entities)

        return self._general_search(entities)

    # ============================================================
    # Helpers
    # ============================================================

    @staticmethod
    def _escape(value: str) -> str:
        """
        Escape a value used inside a Cypher string literal.
        """
        return str(value).replace("\\", "\\\\").replace("'", "\\'")

    @staticmethod
    def _find(
        entities: List[str],
        target: str,
    ) -> Optional[str]:
        """
        Case-insensitive entity lookup.
        """
        target_lower = target.lower()

        for entity in entities:
            if str(entity).lower() == target_lower:
                return str(entity)

        return None

    @classmethod
    def _first_service(
        cls,
        entities: List[str],
    ) -> Optional[str]:
        """
        Prefer Payment Service when it exists.

        This is important for the CompanyOS hero question because
        the question may contain both Checkout Service and
        Payment Service. The architectural decision is associated
        with Payment Service.
        """

        payment_service = cls._find(
            entities,
            "Payment Service",
        )

        if payment_service:
            return payment_service

        for entity in entities:
            if "service" in str(entity).lower():
                return str(entity)

        return None

    @classmethod
    def _first_project(
        cls,
        entities: List[str],
    ) -> Optional[str]:
        for entity in entities:
            value = str(entity).lower()

            if (
                "migration" in value
                or "project" in value
            ):
                return str(entity)

        return None

    @classmethod
    def _first_person(
        cls,
        entities: List[str],
    ) -> Optional[str]:
        known_people = [
            "Maya Singh",
            "Amit Chen",
            "Alice Chen",
            "Raj Patel",
        ]

        for person in known_people:
            match = cls._find(entities, person)

            if match:
                return match

        return None

    # ============================================================
    # Ownership / Expertise
    # ============================================================

    def _ownership(
        self,
        entities: List[str],
    ) -> str:

        service = self._first_service(entities)

        if service:
            service = self._escape(service)

            return f"""
MATCH (service:Service {{name: '{service}'}})
OPTIONAL MATCH
    (person:Person)-[
        r:OWNS|WORKED_ON|CONTRIBUTED_TO
    ]->(service)
RETURN DISTINCT
    person.name AS person,
    type(r) AS relationship,
    service.name AS entity
LIMIT {self.MAX_RESULTS}
""".strip()

        return f"""
MATCH (person:Person)-[
    r:OWNS|WORKED_ON|CONTRIBUTED_TO
]->(entity)
RETURN DISTINCT
    person.name AS person,
    type(r) AS relationship,
    labels(entity) AS entity_labels,
    entity.name AS entity
LIMIT {self.MAX_RESULTS}
""".strip()

    # ============================================================
    # Dependencies
    # ============================================================

    def _dependencies(
        self,
        entities: List[str],
    ) -> str:

        service = self._first_service(entities)

        if service:
            service = self._escape(service)

            return f"""
MATCH (service:Service {{name: '{service}'}})
OPTIONAL MATCH
    (service)-[r:DEPENDS_ON]->(dependency)
RETURN DISTINCT
    service.name AS source,
    type(r) AS relationship,
    labels(dependency) AS target_labels,
    dependency.name AS target
LIMIT {self.MAX_RESULTS}
""".strip()

        return f"""
MATCH (source)-[r:DEPENDS_ON]->(target)
RETURN DISTINCT
    source.name AS source,
    type(r) AS relationship,
    labels(target) AS target_labels,
    target.name AS target
LIMIT {self.MAX_RESULTS}
""".strip()

    # ============================================================
    # Blast Radius
    # ============================================================

    def _blast_radius(
        self,
        entities: List[str],
    ) -> str:

        service = self._first_service(entities)

        if service:
            service = self._escape(service)

            return f"""
MATCH (service:Service {{name: '{service}'}})
OPTIONAL MATCH
    (affected)-[:DEPENDS_ON*1..3]->(service)
RETURN DISTINCT
    service.name AS service,
    labels(affected) AS affected_labels,
    affected.name AS affected_entity
LIMIT {self.MAX_RESULTS}
""".strip()

        return f"""
MATCH (affected)-[:DEPENDS_ON*1..3]->(target)
RETURN DISTINCT
    labels(affected) AS affected_labels,
    affected.name AS affected_entity,
    labels(target) AS target_labels,
    target.name AS target
LIMIT {self.MAX_RESULTS}
""".strip()

    # ============================================================
    # Decision Reason
    # ============================================================

    def _decision_reason(
        self,
        entities: List[str],
    ) -> str:

        service = self._first_service(entities)
        project = self._first_project(entities)

        # --------------------------------------------------------
        # Explicit migration/project
        # --------------------------------------------------------

        if project:
            project = self._escape(project)

            return f"""
MATCH (project:Project {{name: '{project}'}})
OPTIONAL MATCH
    (project)-[
        r1:IMPLEMENTED_BY|PRODUCES|AFFECTS|REFERENCES
    ]->(decision:Decision)
OPTIONAL MATCH
    (decision)-[
        r2:MADE_BY|AUTHORED|REFERENCES
    ]->(person:Person)
RETURN DISTINCT
    project.name AS project,
    decision.title AS decision_title,
    decision.name AS decision_name,
    type(r1) AS decision_relationship,
    person.name AS decision_maker
LIMIT {self.MAX_RESULTS}
""".strip()

        # --------------------------------------------------------
        # Service-constrained architecture reasoning
        # --------------------------------------------------------

        if service:
            service = self._escape(service)

            return f"""
MATCH (service:Service {{name: '{service}'}})

OPTIONAL MATCH
    (migration:Project)-[
        migration_rel:PRODUCES|IMPLEMENTS|AFFECTS
    ]->(service)

OPTIONAL MATCH
    (migration)-[
        decision_rel:IMPLEMENTED_BY|PRODUCES|AFFECTS
    ]->(decision:Decision)

OPTIONAL MATCH
    (decision)-[
        person_rel:MADE_BY|AUTHORED|REFERENCES
    ]->(person:Person)

OPTIONAL MATCH
    (direct_decision:Decision)-[
        direct_rel:REFERENCES|AFFECTS
    ]->(service)

RETURN DISTINCT
    service.name AS service,

    migration.name AS migration,
    type(migration_rel) AS migration_relationship,

    decision.title AS decision_title,
    decision.name AS decision_name,
    type(decision_rel) AS decision_relationship,

    person.name AS decision_maker,
    type(person_rel) AS person_relationship,

    direct_decision.title AS direct_decision_title,
    direct_decision.name AS direct_decision_name,
    type(direct_rel) AS direct_decision_relationship

LIMIT {self.MAX_RESULTS}
""".strip()

        # --------------------------------------------------------
        # Bounded fallback
        # --------------------------------------------------------

        return f"""
MATCH (decision:Decision)
OPTIONAL MATCH
    (decision)-[
        r:MADE_BY|AUTHORED|REFERENCES
    ]->(person:Person)
RETURN DISTINCT
    decision.title AS decision_title,
    decision.name AS decision_name,
    type(r) AS relationship,
    person.name AS person
LIMIT {self.MAX_RESULTS}
""".strip()

    # ============================================================
    # Incident Investigation
    # ============================================================

    def _incident_investigation(
        self,
        entities: List[str],
    ) -> str:

        service = self._first_service(entities)

        if service:
            service = self._escape(service)

            return f"""
MATCH (service:Service {{name: '{service}'}})

OPTIONAL MATCH
    (incident:Incident)-[
        r:AFFECTS|INVOLVES|RELATED_TO|IMPACTS
    ]->(service)

OPTIONAL MATCH
    (incident)-[
        person_rel:RESOLVED|ASSIGNED_TO|OWNED_BY|INVOLVES
    ]->(person:Person)

OPTIONAL MATCH
    (person)-[
        work_rel:WORKED_ON|CONTRIBUTED_TO|OWNS
    ]->(service)

RETURN DISTINCT
    service.name AS service,

    incident.title AS incident_title,
    incident.name AS incident_name,
    incident.description AS incident_description,
    type(r) AS incident_relationship,

    person.name AS person,
    type(person_rel) AS person_incident_relationship,
    type(work_rel) AS person_service_relationship

LIMIT {self.MAX_RESULTS}
""".strip()

        return f"""
MATCH (incident:Incident)
OPTIONAL MATCH
    (incident)-[
        r:AFFECTS|INVOLVES|RELATED_TO|IMPACTS
    ]->(entity)

OPTIONAL MATCH
    (incident)-[
        person_rel:RESOLVED|ASSIGNED_TO|OWNED_BY|INVOLVES
    ]->(person:Person)

RETURN DISTINCT
    incident.title AS incident_title,
    incident.name AS incident_name,
    incident.description AS incident_description,
    type(r) AS incident_relationship,
    entity.name AS affected_entity,
    person.name AS person,
    type(person_rel) AS person_relationship

LIMIT {self.MAX_RESULTS}
""".strip()

    # ============================================================
    # Centrality
    # ============================================================

    def _centrality(
        self,
        entities: List[str],
    ) -> str:

        service = self._first_service(entities)

        if service:
            service = self._escape(service)

            return f"""
MATCH (entity {{name: '{service}'}})
OPTIONAL MATCH (entity)-[r]-(neighbor)
WITH
    entity,
    count(r) AS relationship_count
RETURN
    labels(entity) AS labels,
    entity.name AS entity,
    relationship_count
ORDER BY relationship_count DESC
LIMIT {self.MAX_RESULTS}
""".strip()

        return f"""
MATCH (entity)
OPTIONAL MATCH (entity)-[r]-(neighbor)
WITH
    entity,
    count(r) AS relationship_count
RETURN
    labels(entity) AS labels,
    entity.name AS entity,
    relationship_count
ORDER BY relationship_count DESC
LIMIT {self.MAX_RESULTS}
""".strip()

    # ============================================================
    # Connected Component
    # ============================================================

    def _connected_component(
        self,
        entities: List[str],
    ) -> str:

        service = self._first_service(entities)

        if service:
            service = self._escape(service)

            return f"""
MATCH (service:Service {{name: '{service}'}})
OPTIONAL MATCH
    path=(service)-[*1..{self.MAX_PATH_LENGTH}]-(connected)
RETURN DISTINCT
    service.name AS root,
    labels(connected) AS connected_labels,
    connected.name AS connected_entity
LIMIT {self.MAX_RESULTS}
""".strip()

        return f"""
MATCH (root)
OPTIONAL MATCH
    path=(root)-[*1..{self.MAX_PATH_LENGTH}]-(connected)
RETURN DISTINCT
    labels(root) AS root_labels,
    root.name AS root,
    labels(connected) AS connected_labels,
    connected.name AS connected_entity
LIMIT {self.MAX_RESULTS}
""".strip()

    # ============================================================
    # General Search
    # ============================================================

    def _general_search(
        self,
        entities: List[str],
    ) -> str:

        if entities:
            escaped = [
                self._escape(entity)
                for entity in entities
            ]

            conditions = " OR ".join(
                [
                    f"toLower(coalesce(n.name, '')) = toLower('{entity}')"
                    for entity in escaped
                ]
            )

            return f"""
MATCH (n)
WHERE {conditions}
OPTIONAL MATCH (n)-[r]-(neighbor)
RETURN DISTINCT
    labels(n) AS labels,
    n.name AS entity,
    type(r) AS relationship,
    labels(neighbor) AS neighbor_labels,
    neighbor.name AS neighbor
LIMIT {self.MAX_RESULTS}
""".strip()

        return f"""
MATCH (n)
OPTIONAL MATCH (n)-[r]-(neighbor)
RETURN DISTINCT
    labels(n) AS labels,
    n.name AS entity,
    type(r) AS relationship,
    labels(neighbor) AS neighbor_labels,
    neighbor.name AS neighbor
LIMIT {self.MAX_RESULTS}
""".strip()

    # ============================================================
    # Diagnostics
    # ============================================================

    def describe(self):
        return {
            "graph_name": self.graph_name,
            "max_results": self.MAX_RESULTS,
            "max_path_length": self.MAX_PATH_LENGTH,
            "read_only": True,
        }

# """
# CompanyOS Cypher Generator
# ===========================

# Generates safe, read-only, bounded Cypher queries from QueryPlan objects.

# Design goals:
# - FalkorDB remains the source of truth.
# - Queries are entity-constrained whenever possible.
# - Results are bounded.
# - No graph writes are generated.
# - No arbitrary user Cypher is generated here.
# - Supports the CompanyOS demo questions:
#     * Who knows the most about the payment system?
#     * Why was the payment architecture changed?
#     * What happens if Payment Service goes down?
#     * Who should investigate the checkout failures?
#     * Hero multi-hop investigation question.
# """

# from __future__ import annotations

# from typing import Any, Dict, List, Optional


# class CypherGenerator:
#     """
#     Generate bounded, read-only Cypher queries for CompanyOS.

#     The generated queries are intentionally conservative:
#     - MATCH / OPTIONAL MATCH / RETURN / WITH / ORDER BY / LIMIT
#     - no CREATE
#     - no MERGE
#     - no DELETE
#     - no SET
#     - no arbitrary procedure calls
#     """

#     MAX_RESULTS = 25
#     MAX_PATH_LENGTH = 8

#     def __init__(
#         self,
#         graph_name: str = "novatech",
#     ):
#         self.graph_name = graph_name

#     # ============================================================
#     # Public API
#     # ============================================================

#     def generate(self, plan: Any) -> str:
#         """
#         Convert a QueryPlan into a read-only Cypher query.
#         """

#         intent = getattr(plan, "intent", None) or "general_graph_search"

#         if intent == "ownership_expertise":
#             return self._ownership(plan)

#         if intent == "dependency_analysis":
#             return self._dependencies(plan)

#         if intent == "blast_radius":
#             return self._blast_radius(plan)

#         if intent == "decision_reason":
#             return self._decision_reason(plan)

#         if intent == "incident_investigation":
#             return self._incident_investigation(plan)

#         if intent == "centrality":
#             return self._centrality(plan)

#         if intent == "connected_component":
#             return self._connected_component(plan)

#         return self._general_search(plan)

#     # ============================================================
#     # Helpers
#     # ============================================================

#     @staticmethod
#     def _escape(value: str) -> str:
#         """
#         Escape a string for a Cypher single-quoted literal.

#         This is not intended to be a replacement for the security
#         validator. It simply prevents malformed string literals.
#         """
#         return str(value).replace("\\", "\\\\").replace("'", "\\'")

#     @staticmethod
#     def _entities(plan: Any) -> List[str]:
#         entities = getattr(plan, "entities", None)

#         if not entities:
#             return []

#         if isinstance(entities, dict):
#             values: List[str] = []

#             for value in entities.values():
#                 if isinstance(value, list):
#                     values.extend(str(v) for v in value)
#                 elif value is not None:
#                     values.append(str(value))

#             return values

#         if isinstance(entities, (list, tuple, set)):
#             return [str(value) for value in entities]

#         return [str(entities)]

#     @classmethod
#     def _find_entity(
#         cls,
#         entities: List[str],
#         value: str,
#     ) -> Optional[str]:
#         value_lower = value.lower()

#         for entity in entities:
#             if entity.lower() == value_lower:
#                 return entity

#         return None

#     @classmethod
#     def _has_entity(
#         cls,
#         entities: List[str],
#         value: str,
#     ) -> bool:
#         return cls._find_entity(entities, value) is not None

#     @classmethod
#     def _first_service(
#         cls,
#         entities: List[str],
#     ) -> Optional[str]:
#         """
#         Prefer Payment Service when it is present because several
#         CompanyOS demo questions mention both Checkout Service and
#         Payment Service.

#         Otherwise return the first service-like entity.
#         """

#         payment = cls._find_entity(
#             entities,
#             "Payment Service",
#         )

#         if payment:
#             return payment

#         for entity in entities:
#             if "service" in entity.lower():
#                 return entity

#         return None

#     @classmethod
#     def _first_project(
#         cls,
#         entities: List[str],
#     ) -> Optional[str]:
#         for entity in entities:
#             lowered = entity.lower()

#             if (
#                 "migration" in lowered
#                 or "project" in lowered
#             ):
#                 return entity

#         return None

#     @classmethod
#     def _first_person(
#         cls,
#         entities: List[str],
#     ) -> Optional[str]:
#         known_people = {
#             "Alice Chen",
#             "Raj Patel",
#             "Maya Singh",
#             "Amit Chen",
#         }

#         for person in known_people:
#             match = cls._find_entity(entities, person)

#             if match:
#                 return match

#         return None

#     @classmethod
#     def _limit(cls) -> int:
#         return cls.MAX_RESULTS

#     # ============================================================
#     # Ownership / Expertise
#     # ============================================================

#     def _ownership(self, plan: Any) -> str:
#         entities = self._entities(plan)
#         service = self._first_service(entities)

#         if service:
#             service = self._escape(service)

#             return f"""
# MATCH (service:Service {{name: '{service}'}})
# OPTIONAL MATCH
#     (person:Person)-[
#         r:OWNS|WORKED_ON|CONTRIBUTED_TO
#     ]->(service)
# RETURN DISTINCT
#     person.name AS person,
#     type(r) AS relationship,
#     service.name AS entity
# LIMIT {self._limit()}
# """.strip()

#         return f"""
# MATCH (person:Person)-[
#     r:OWNS|WORKED_ON|CONTRIBUTED_TO
# ]->(entity)
# RETURN DISTINCT
#     person.name AS person,
#     type(r) AS relationship,
#     labels(entity) AS entity_labels,
#     entity.name AS entity
# LIMIT {self._limit()}
# """.strip()

#     # ============================================================
#     # Dependencies
#     # ============================================================

#     def _dependencies(self, plan: Any) -> str:
#         entities = self._entities(plan)
#         service = self._first_service(entities)

#         if service:
#             service = self._escape(service)

#             return f"""
# MATCH (service:Service {{name: '{service}'}})
# OPTIONAL MATCH
#     (service)-[r:DEPENDS_ON]->(dependency)
# RETURN DISTINCT
#     service.name AS source,
#     type(r) AS relationship,
#     labels(dependency) AS target_labels,
#     dependency.name AS target
# LIMIT {self._limit()}
# """.strip()

#         return f"""
# MATCH (source)-[r:DEPENDS_ON]->(target)
# RETURN DISTINCT
#     source.name AS source,
#     type(r) AS relationship,
#     labels(target) AS target_labels,
#     target.name AS target
# LIMIT {self._limit()}
# """.strip()

#     # ============================================================
#     # Blast Radius
#     # ============================================================

#     def _blast_radius(self, plan: Any) -> str:
#         entities = self._entities(plan)
#         service = self._first_service(entities)

#         if service:
#             service = self._escape(service)

#             return f"""
# MATCH (service:Service {{name: '{service}'}})
# OPTIONAL MATCH
#     (affected)-[:DEPENDS_ON*1..3]->(service)
# RETURN DISTINCT
#     service.name AS service,
#     labels(affected) AS affected_labels,
#     affected.name AS affected_entity
# LIMIT {self._limit()}
# """.strip()

#         return f"""
# MATCH (affected)-[:DEPENDS_ON*1..3]->(target)
# RETURN DISTINCT
#     labels(affected) AS affected_labels,
#     affected.name AS affected_entity,
#     labels(target) AS target_labels,
#     target.name AS target
# LIMIT {self._limit()}
# """.strip()

#     # ============================================================
#     # Decision Reason
#     # ============================================================

#     def _decision_reason(self, plan: Any) -> str:
#         """
#         Explain architectural decisions by connecting:

#             Service
#                 ↓
#             Migration / Project
#                 ↓
#             Decision
#                 ↓
#             Person

#         NovaTech canonical demo path:

#             Payment Service Migration
#                 -PRODUCES-> Payment Service
#                 -IMPLEMENTED_BY-> Decision
#                 -IMPLEMENTED_BY-> Person

#         We also support direct Decision relationships where present.
#         """

#         entities = self._entities(plan)

#         service = self._first_service(entities)
#         project = self._first_project(entities)

#         # --------------------------------------------------------
#         # Prefer the explicitly named migration/project.
#         # --------------------------------------------------------

#         if project:
#             project = self._escape(project)

#             return f"""
# MATCH (project:Project {{name: '{project}'}})
# OPTIONAL MATCH
#     (project)-[
#         r1:IMPLEMENTED_BY|PRODUCES|AFFECTS|REFERENCES
#     ]->(decision:Decision)
# OPTIONAL MATCH
#     (decision)-[
#         r2:MADE_BY|AUTHORED|REFERENCES
#     ]->(person:Person)
# RETURN DISTINCT
#     project.name AS project,
#     decision.title AS decision_title,
#     decision.name AS decision_name,
#     type(r1) AS decision_relationship,
#     person.name AS decision_maker
# LIMIT {self._limit()}
# """.strip()

#         # --------------------------------------------------------
#         # Service-constrained decision reasoning.
#         # --------------------------------------------------------

#         if service:
#             service = self._escape(service)

#             return f"""
# MATCH (service:Service {{name: '{service}'}})

# OPTIONAL MATCH
#     (migration:Project)-[
#         migration_rel:PRODUCES|IMPLEMENTS|AFFECTS
#     ]->(service)

# OPTIONAL MATCH
#     (migration)-[
#         decision_rel:IMPLEMENTED_BY|PRODUCES|AFFECTS
#     ]->(decision:Decision)

# OPTIONAL MATCH
#     (decision)-[
#         person_rel:MADE_BY|AUTHORED|REFERENCES
#     ]->(person:Person)

# OPTIONAL MATCH
#     (direct_decision:Decision)-[
#         direct_rel:REFERENCES|AFFECTS
#     ]->(service)

# RETURN DISTINCT
#     service.name AS service,

#     migration.name AS migration,
#     type(migration_rel) AS migration_relationship,

#     decision.title AS decision_title,
#     decision.name AS decision_name,
#     type(decision_rel) AS decision_relationship,

#     person.name AS decision_maker,
#     type(person_rel) AS person_relationship,

#     direct_decision.title AS direct_decision_title,
#     direct_decision.name AS direct_decision_name,
#     type(direct_rel) AS direct_decision_relationship

# LIMIT {self._limit()}
# """.strip()

#         # --------------------------------------------------------
#         # Bounded fallback.
#         # --------------------------------------------------------

#         return f"""
# MATCH (decision:Decision)
# OPTIONAL MATCH
#     (decision)-[
#         r:MADE_BY|AUTHORED|REFERENCES
#     ]->(person:Person)
# RETURN DISTINCT
#     decision.title AS decision_title,
#     decision.name AS decision_name,
#     type(r) AS relationship,
#     person.name AS person
# LIMIT {self._limit()}
# """.strip()

#     # ============================================================
#     # Incident Investigation
#     # ============================================================

#     def _incident_investigation(self, plan: Any) -> str:
#         entities = self._entities(plan)
#         service = self._first_service(entities)

#         if service:
#             service = self._escape(service)

#             return f"""
# MATCH (service:Service {{name: '{service}'}})

# OPTIONAL MATCH
#     (incident:Incident)-[
#         r:AFFECTS|INVOLVES|RELATED_TO|IMPACTS
#     ]->(service)

# OPTIONAL MATCH
#     (incident)-[
#         person_rel:RESOLVED|ASSIGNED_TO|OWNED_BY|INVOLVES
#     ]->(person:Person)

# OPTIONAL MATCH
#     (person)-[
#         work_rel:WORKED_ON|CONTRIBUTED_TO|OWNS
#     ]->(service)

# RETURN DISTINCT
#     service.name AS service,

#     incident.title AS incident_title,
#     incident.name AS incident_name,
#     incident.description AS incident_description,
#     type(r) AS incident_relationship,

#     person.name AS person,
#     type(person_rel) AS person_incident_relationship,
#     type(work_rel) AS person_service_relationship

# LIMIT {self._limit()}
# """.strip()

#         return f"""
# MATCH (incident:Incident)
# OPTIONAL MATCH
#     (incident)-[
#         r:AFFECTS|INVOLVES|RELATED_TO|IMPACTS
#     ]->(entity)

# OPTIONAL MATCH
#     (incident)-[
#         person_rel:RESOLVED|ASSIGNED_TO|OWNED_BY|INVOLVES
#     ]->(person:Person)

# RETURN DISTINCT
#     incident.title AS incident_title,
#     incident.name AS incident_name,
#     incident.description AS incident_description,
#     type(r) AS incident_relationship,
#     entity.name AS affected_entity,
#     person.name AS person,
#     type(person_rel) AS person_relationship

# LIMIT {self._limit()}
# """.strip()

#     # ============================================================
#     # Centrality
#     # ============================================================

#     def _centrality(self, plan: Any) -> str:
#         """
#         FalkorDB-native graph traversal fallback.

#         This returns bounded relationship-degree information.

#         Actual graph algorithm execution can be layered on top of
#         this query through the graph algorithm service.
#         """

#         return f"""
# MATCH (entity)
# OPTIONAL MATCH (entity)-[r]->(neighbor)
# WITH
#     entity,
#     count(r) AS outgoing_relationships
# RETURN
#     labels(entity) AS labels,
#     entity.name AS entity,
#     outgoing_relationships
# ORDER BY outgoing_relationships DESC
# LIMIT {self._limit()}
# """.strip()

#     # ============================================================
#     # Connected Component
#     # ============================================================

#     def _connected_component(self, plan: Any) -> str:
#         entities = self._entities(plan)
#         service = self._first_service(entities)

#         if service:
#             service = self._escape(service)

#             return f"""
# MATCH (service:Service {{name: '{service}'}})
# OPTIONAL MATCH path =
#     (service)-[*1..{self.MAX_PATH_LENGTH}]-(connected)
# RETURN DISTINCT
#     service.name AS root,
#     labels(connected) AS connected_labels,
#     connected.name AS connected_entity
# LIMIT {self._limit()}
# """.strip()

#         return f"""
# MATCH (root)
# OPTIONAL MATCH path =
#     (root)-[*1..{self.MAX_PATH_LENGTH}]-(connected)
# RETURN DISTINCT
#     labels(root) AS root_labels,
#     root.name AS root,
#     labels(connected) AS connected_labels,
#     connected.name AS connected_entity
# LIMIT {self._limit()}
# """.strip()

#     # ============================================================
#     # General Search
#     # ============================================================

#     def _general_search(self, plan: Any) -> str:
#         entities = self._entities(plan)

#         # --------------------------------------------------------
#         # Entity-specific search
#         # --------------------------------------------------------

#         if entities:
#             escaped_entities = [
#                 self._escape(entity)
#                 for entity in entities
#             ]

#             conditions = " OR ".join(
#                 [
#                     f"toLower(coalesce(n.name, '')) = toLower('{entity}')"
#                     for entity in escaped_entities
#                 ]
#             )

#             return f"""
# MATCH (n)
# WHERE {conditions}
# OPTIONAL MATCH (n)-[r]-(neighbor)
# RETURN DISTINCT
#     labels(n) AS labels,
#     n.name AS entity,
#     type(r) AS relationship,
#     labels(neighbor) AS neighbor_labels,
#     neighbor.name AS neighbor
# LIMIT {self._limit()}
# """.strip()

#         # --------------------------------------------------------
#         # Safe bounded fallback.
#         # --------------------------------------------------------

#         return f"""
# MATCH (n)
# OPTIONAL MATCH (n)-[r]-(neighbor)
# RETURN DISTINCT
#     labels(n) AS labels,
#     n.name AS entity,
#     type(r) AS relationship,
#     labels(neighbor) AS neighbor_labels,
#     neighbor.name AS neighbor
# LIMIT {self._limit()}
# """.strip()

#     # ============================================================
#     # Debug / Introspection
#     # ============================================================

#     def describe(self) -> Dict[str, Any]:
#         """
#         Useful for diagnostics and demo/debug endpoints.
#         """

#         return {
#             "graph_name": self.graph_name,
#             "max_results": self.MAX_RESULTS,
#             "max_path_length": self.MAX_PATH_LENGTH,
#             "read_only": True,
#             "supported_intents": [
#                 "ownership_expertise",
#                 "dependency_analysis",
#                 "blast_radius",
#                 "decision_reason",
#                 "incident_investigation",
#                 "centrality",
#                 "connected_component",
#                 "general_graph_search",
#             ],
#         }