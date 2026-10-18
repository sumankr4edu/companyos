from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class QueryPlan:
    """
    Structured representation of a CompanyOS query.

    The plan determines which graph intelligence capability
    should be executed before LLM reasoning.
    """

    intent: str

    entities: List[str] = field(
        default_factory=list
    )

    relationships: List[str] = field(
        default_factory=list
    )

    max_hops: int = 4

    needs_path: bool = False

    needs_memory: bool = True

    needs_llm: bool = True

    confidence: float = 0.5

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


class QueryPlanner:

    KNOWN_ENTITIES = [
        "Checkout Service",
        "Payment Service",
        "Payment Database",
        "Payment Service Migration",
        "Alice Chen",
        "Raj Patel",
        "Maya Singh",
        "NovaTech",
    ]

    # =========================================================
    # Main planner
    # =========================================================

    def plan(
        self,
        question: str,
    ) -> QueryPlan:

        if not question or not question.strip():

            raise ValueError(
                "Question cannot be empty."
            )

        q = question.lower()

        entities = self._extract_entities(
            question
        )

        # =====================================================
        # Expertise / Who knows?
        # =====================================================

        if (
            "who knows" in q
            or "who should i ask" in q
            or "who should i contact" in q
            or "who has experience" in q
            or "most expertise" in q
            or "expert" in q
            or "knowledgeable" in q
        ):

            return QueryPlan(
                intent="ownership_expertise",
                entities=entities,
                relationships=[
                    "OWNS",
                    "WORKED_ON",
                    "CONTRIBUTED_TO",
                    "INVOLVES",
                    "AUTHORED",
                ],
                max_hops=3,
                needs_path=True,
                confidence=0.95,
                metadata={
                    "algorithm": "expertise_ranking"
                },
            )

        # =====================================================
        # Blast radius / What breaks?
        # =====================================================

        if (
            "blast radius" in q
            or "what breaks" in q
            or "what will break" in q
            or "what happens if" in q
            or "if it goes down" in q
            or "if it fails" in q
            or "dependencies affected" in q
            or "affected if" in q
        ):

            return QueryPlan(
                intent="blast_radius",
                entities=entities,
                relationships=[
                    "DEPENDS_ON"
                ],
                max_hops=4,
                needs_path=True,
                confidence=0.95,
                metadata={
                    "algorithm": "dependency_blast_radius"
                },
            )

        # =====================================================
        # Dependency analysis
        # =====================================================

        if (
            "dependency" in q
            or "depends on" in q
            or "depend on" in q
            or "dependencies" in q
        ):

            return QueryPlan(
                intent="dependency_analysis",
                entities=entities,
                relationships=[
                    "DEPENDS_ON"
                ],
                max_hops=4,
                needs_path=True,
                confidence=0.92,
                metadata={
                    "algorithm": "dependencies"
                },
            )

        # =====================================================
        # Centrality / most connected
        # =====================================================

        if (
            "most connected" in q
            or "most central" in q
            or "centrality" in q
            or "most connected person" in q
            or "most connected engineer" in q
            or "architectural hotspot" in q
            or "hotspot" in q
        ):

            return QueryPlan(
                intent="centrality",
                entities=entities,
                relationships=[],
                max_hops=2,
                needs_path=True,
                confidence=0.93,
                metadata={
                    "algorithm": "centrality"
                },
            )

        # =====================================================
        # Connected component
        # =====================================================

        if (
            "connected to" in q
            or "connected component" in q
            or "everything connected" in q
            or "related to" in q
            or "graph around" in q
        ):

            return QueryPlan(
                intent="connected_component",
                entities=entities,
                relationships=[],
                max_hops=4,
                needs_path=True,
                confidence=0.88,
                metadata={
                    "algorithm": "connected_component"
                },
            )

        # =====================================================
        # Decision reasoning
        # =====================================================

        if (
            "why was" in q
            or "why did we" in q
            or "why was the" in q
            or "decision" in q
            or "architecture changed" in q
            or "architectural decision" in q
        ):

            return QueryPlan(
                intent="decision_reason",
                entities=entities,
                relationships=[
                    "MADE_BY",
                    "IMPLEMENTED_BY",
                    "DOCUMENTS",
                    "AUTHORED",
                ],
                max_hops=5,
                needs_path=True,
                confidence=0.93,
                metadata={
                    "algorithm": "decision_reason"
                },
            )

        # =====================================================
        # Incident investigation
        # =====================================================

        if (
            "incident" in q
            or "failure" in q
            or "failed" in q
            or "outage" in q
            or "error" in q
            or "investigate" in q
        ):

            return QueryPlan(
                intent="incident_investigation",
                entities=entities,
                relationships=[
                    "AFFECTS",
                    "INVOLVES",
                    "RESOLVED",
                    "ASSIGNED_TO",
                ],
                max_hops=5,
                needs_path=True,
                confidence=0.90,
                metadata={
                    "algorithm": "incident_investigation"
                },
            )

        # =====================================================
        # General graph search
        # =====================================================

        return QueryPlan(
            intent="general_graph_search",
            entities=entities,
            relationships=[],
            max_hops=3,
            needs_path=False,
            confidence=0.60,
            metadata={
                "algorithm": "graph_search"
            },
        )

    # =========================================================
    # Entity extraction
    # =========================================================

    def _extract_entities(
        self,
        question: str,
    ) -> List[str]:

        q = question.lower()

        found = []

        for entity in self.KNOWN_ENTITIES:

            if entity.lower() in q:

                found.append(entity)

        # Common natural-language aliases

        aliases = {
            "payment system": "Payment Service",
            "payment service": "Payment Service",
            "checkout": "Checkout Service",
            "checkout service": "Checkout Service",
            "payment database": "Payment Database",
            "payment db": "Payment Database",
            "payment migration": "Payment Service Migration",
        }

        for alias, canonical in aliases.items():

            if alias in q and canonical not in found:

                found.append(canonical)

        return found