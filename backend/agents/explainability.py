from typing import Any, Dict, List


class ExplainabilityAgent:
    """
    Converts graph evidence into an auditable explanation.

    This agent does NOT expose private chain-of-thought.
    It only exposes observable evidence, graph relationships,
    confidence, contradictions, and known unknowns.
    """

    def build(
        self,
        answer: str,
        graph_result: Dict[str, Any],
        contradictions: List[Dict[str, Any]] | None = None,
        extra_unknowns: List[str] | None = None,
    ) -> Dict[str, Any]:

        contradictions = contradictions or []
        extra_unknowns = extra_unknowns or []

        evidence = graph_result.get("evidence", [])
        branches = graph_result.get("branches", [])
        confidence = graph_result.get("confidence", 0.0)

        unknowns = list(
            dict.fromkeys(
                graph_result.get("unknowns", []) + extra_unknowns
            )
        )

        evidence_cards = []

        for item in evidence:
            source = item.get("source", "Unknown")
            relationship = item.get(
                "relationship",
                "RELATED_TO",
            )
            target = item.get("target", "Unknown")

            evidence_cards.append(
                {
                    "source": source,
                    "relationship": relationship,
                    "target": target,
                    "statement": (
                        f"{source} -[{relationship}]-> {target}"
                    ),
                    "type": item.get("type", "graph_evidence"),
                }
            )

        graph_path = []

        for branch in branches:
            graph_path.append(
                {
                    "name": branch.get("name"),
                    "display": branch.get("display"),
                    "nodes": branch.get("nodes", []),
                }
            )

        return {
            "answer": answer,
            "evidence": evidence_cards,
            "graph_path": graph_path,
            "confidence": confidence,
            "contradictions": contradictions,
            "unknowns": unknowns,
            "why_this_answer": {
                "source": "FalkorDB graph evidence",
                "graph_evidence_count": len(evidence_cards),
                "path_count": len(graph_path),
                "contradiction_count": len(contradictions),
                "confidence": confidence,
                "explanation": (
                    "The answer is grounded in observable relationships "
                    "retrieved from the FalkorDB company graph. "
                    "Only relationships present in the graph are reported."
                ),
            },
        }

    def empty(
        self,
        answer: str = "",
        reason: str = "No sufficient graph evidence found.",
    ) -> Dict[str, Any]:

        return {
            "answer": answer,
            "evidence": [],
            "graph_path": [],
            "confidence": 0.0,
            "contradictions": [],
            "unknowns": [reason],
            "why_this_answer": {
                "source": "FalkorDB graph evidence",
                "graph_evidence_count": 0,
                "path_count": 0,
                "contradiction_count": 0,
                "confidence": 0.0,
                "explanation": reason,
            },
        }
