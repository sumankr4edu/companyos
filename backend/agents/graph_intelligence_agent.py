from typing import Any, Dict

from graph.algorithms import GraphAlgorithms


class GraphIntelligenceAgent:
    """
    Routes a QueryPlan to the appropriate graph intelligence
    algorithm.

    This component executes graph operations BEFORE the LLM.
    """

    def __init__(
        self,
        graph_name: str = "novatech",
    ):
        self.graph_name = graph_name

        self.algorithms = GraphAlgorithms(
            graph_name=graph_name
        )

    # =========================================================
    # Main execution
    # =========================================================

    def execute(
        self,
        plan,
    ) -> Dict[str, Any]:

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

        max_hops = getattr(
            plan,
            "max_hops",
            4,
        )

        entity = (
            entities[0]
            if entities
            else None
        )

        # =====================================================
        # Expertise
        # =====================================================

        if intent == "ownership_expertise":

            if not entity:

                return {
                    "success": False,
                    "intent": intent,
                    "error": (
                        "No target entity "
                        "was identified."
                    ),
                }

            return {
                "success": True,
                "intent": intent,
                "algorithm": "expertise_ranking",
                "data": (
                    self.algorithms
                    .expertise_ranking(
                        entity_name=entity,
                        limit=10,
                    )
                ),
            }

        # =====================================================
        # Blast radius
        # =====================================================

        if intent == "blast_radius":

            if not entity:

                return {
                    "success": False,
                    "intent": intent,
                    "error": (
                        "No service was "
                        "identified."
                    ),
                }

            return {
                "success": True,
                "intent": intent,
                "algorithm": (
                    "dependency_blast_radius"
                ),
                "data": (
                    self.algorithms
                    .dependency_blast_radius(
                        service_name=entity,
                        max_hops=max_hops,
                        limit=100,
                    )
                ),
            }

        # =====================================================
        # Dependencies
        # =====================================================

        if intent == "dependency_analysis":

            if not entity:

                return {
                    "success": False,
                    "intent": intent,
                    "error": (
                        "No service was "
                        "identified."
                    ),
                }

            return {
                "success": True,
                "intent": intent,
                "algorithm": "dependencies",
                "data": (
                    self.algorithms
                    .dependencies(
                        service_name=entity,
                        max_hops=max_hops,
                        limit=100,
                    )
                ),
            }

        # =====================================================
        # Centrality
        # =====================================================

        if intent == "centrality":

            # If a person/service is supplied,
            # calculate entity centrality.
            if entity:

                return {
                    "success": True,
                    "intent": intent,
                    "algorithm": (
                        "degree_centrality"
                    ),
                    "data": (
                        self.algorithms
                        .degree_centrality(
                            entity_name=entity,
                        )
                    ),
                }

            # Otherwise return people centrality.
            return {
                "success": True,
                "intent": intent,
                "algorithm": (
                    "people_centrality"
                ),
                "data": (
                    self.algorithms
                    .people_centrality(
                        limit=10,
                    )
                ),
            }

        # =====================================================
        # Connected component
        # =====================================================

        if intent == "connected_component":

            if not entity:

                return {
                    "success": False,
                    "intent": intent,
                    "error": (
                        "No entity was "
                        "identified."
                    ),
                }

            return {
                "success": True,
                "intent": intent,
                "algorithm": (
                    "connected_component"
                ),
                "data": (
                    self.algorithms
                    .connected_component(
                        entity_name=entity,
                        max_hops=max_hops,
                        limit=100,
                    )
                ),
            }

        # =====================================================
        # No specialized algorithm
        # =====================================================

        return {
            "success": False,
            "intent": intent,
            "algorithm": None,
            "data": [],
            "message": (
                "No specialized graph "
                "algorithm selected."
            ),
        }