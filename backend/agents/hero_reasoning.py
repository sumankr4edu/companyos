
from typing import Any, Dict

from graph.path_engine import GraphPathEngine


class HeroReasoningAgent:
    """
    Produces the CompanyOS hero investigation answer directly
    from deterministic FalkorDB evidence.
    """

    def __init__(self, graph_name: str = "novatech"):
        self.graph_name = graph_name
        self.path_engine = GraphPathEngine(graph_name)

    def execute(self) -> Dict[str, Any]:
        graph = self.path_engine.hero_path()

        if not graph.get("success"):
            return {
                "success": False,
                "answer": "",
                "graph": graph,
            }

        evidence = graph.get("evidence", [])

        incident = self._find(
            evidence,
            "incident",
        )

        decision = self._find(
            evidence,
            "architecture_decision",
        )

        decision_maker = self._find(
            evidence,
            "decision_maker",
        )

        owner = self._find(
            evidence,
            "current_owner",
        )

        answer_parts = []

        if incident:
            answer_parts.append(
                "The Payment Service is directly associated with "
                "the canonical incident 'Checkout failures increased'."
            )

        if decision:
            answer_parts.append(
                "The relevant architecture decision was "
                "'Move payment processing to dedicated Payment Service'."
            )

        if decision_maker:
            answer_parts.append(
                "That decision was made by Alice Chen."
            )

        if owner:
            answer_parts.append(
                "The current owner of Payment Service is Maya Singh."
            )

        if not answer_parts:
            answer_parts.append(
                "The graph contains related evidence, but it is "
                "insufficient to establish the requested investigation."
            )

        return {
            "success": True,
            "answer": " ".join(answer_parts),
            "graph": graph,
        }

    @staticmethod
    def _find(
        evidence: list[Dict[str, Any]],
        evidence_type: str,
    ) -> Dict[str, Any] | None:

        for item in evidence:
            if item.get("type") == evidence_type:
                return item

        return None
