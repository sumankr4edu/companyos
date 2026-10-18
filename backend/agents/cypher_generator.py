from agents.cypher_validator import CypherValidator


class CypherGenerator:

    def __init__(self, graph_name: str = "novatech"):
        self.graph_name = graph_name
        self.validator = CypherValidator()

    def generate(self, plan):

        intent = getattr(
            plan,
            "intent",
            None,
        )

        entities = getattr(
            plan,
            "entities",
            [],
        )

        entity_set = {
            str(entity).lower()
            for entity in entities
        }

        # -----------------------------------------------------
        # Dependency analysis
        # -----------------------------------------------------

        if intent == "dependency_analysis":

            service = (
                "Checkout Service"
                if "checkout service" in entity_set
                else "Payment Service"
            )

            query = f"""
            MATCH (s:Service {{name: '{service}'}})
            OPTIONAL MATCH path =
                (s)-[:DEPENDS_ON*1..4]->(dependency:Service)
            RETURN
                s.name AS service,
                dependency.name AS dependency
            LIMIT 50
            """

        # -----------------------------------------------------
        # Ownership / expertise
        # -----------------------------------------------------

        elif intent == "ownership_expertise":

            query = """
            MATCH (p:Person)-[r:OWNS|WORKED_ON|CONTRIBUTED_TO]->(e)
            RETURN
                p.name AS person,
                type(r) AS relationship,
                e.name AS entity
            LIMIT 100
            """

        # -----------------------------------------------------
        # Decision reasoning
        # -----------------------------------------------------

        elif intent == "decision_reason":

            query = """
            MATCH (d:Decision)
            OPTIONAL MATCH (d)-[:MADE_BY]->(p:Person)
            OPTIONAL MATCH (d)-[:IMPLEMENTED_BY]->(project:Project)

            RETURN
                d.name AS decision,
                d.status AS status,
                p.name AS decision_maker,
                project.name AS implementation
            LIMIT 100
            """

        # -----------------------------------------------------
        # Incident investigation
        # -----------------------------------------------------

        elif intent == "incident_investigation":

            query = """
            MATCH (i:Incident)
            OPTIONAL MATCH (i)-[:AFFECTS]->(s:Service)
            OPTIONAL MATCH (i)-[:INVOLVES]->(p:Person)

            RETURN
                i.name AS incident,
                i.title AS title,
                i.severity AS severity,
                i.status AS status,
                s.name AS affected_service,
                p.name AS involved_person
            LIMIT 100
            """

        # -----------------------------------------------------
        # General graph search
        # -----------------------------------------------------

        else:

            search_term = (
                entities[0]
                if entities
                else ""
            )

            safe_term = (
                str(search_term)
                .replace("\\", "\\\\")
                .replace("'", "\\'")
            )

            query = f"""
            MATCH (n)
            WHERE
                toLower(coalesce(n.name, ''))
                CONTAINS
                toLower('{safe_term}')
            RETURN
                labels(n) AS labels,
                n.name AS name,
                n.id AS id
            LIMIT 50
            """

        valid, message = self.validator.validate(
            query
        )

        if not valid:
            raise ValueError(
                f"Generated Cypher rejected: {message}"
            )

        return query