from typing import Any, Dict, List


class ExplainabilityAgent:
    """
    Creates auditable explanations from CompanyOS graph evidence.

    This does NOT expose private chain-of-thought.

    It exposes:

    - Evidence
    - Graph path
    - Confidence
    - Provenance
    - Contradictions
    - Unknowns
    - Why this answer
    """

    def __init__(self):
        pass

    # =========================================================
    # Confidence
    # =========================================================

    def calculate_confidence(
        self,
        evidence: List[Dict[str, Any]],
        graph_path: List[Dict[str, Any]],
        contradictions: List[Any],
    ) -> float:

        score = 0.0

        # Evidence
        if evidence:
            score += min(
                0.45,
                len(evidence) * 0.05,
            )

        # Explicit graph path
        if graph_path:
            score += 0.30

        # Provenance
        provenance_count = 0

        for item in evidence:

            if not isinstance(item, dict):
                continue

            if item.get("provenance"):
                provenance_count += 1

        if provenance_count:
            score += min(
                0.15,
                provenance_count * 0.03,
            )

        # Contradictions reduce confidence
        if contradictions:
            score -= min(
                0.35,
                len(contradictions) * 0.08,
            )

        return round(
            max(
                0.0,
                min(1.0, score),
            ),
            2,
        )

    # =========================================================
    # Evidence cards
    # =========================================================

    def build_evidence_cards(
        self,
        evidence: List[Dict[str, Any]],
        limit: int = 20,
    ) -> List[Dict[str, Any]]:

        cards = []

        for index, item in enumerate(
            evidence[:limit],
            start=1,
        ):

            if not isinstance(item, dict):

                cards.append(
                    {
                        "id": f"E{index}",
                        "content": str(item),
                    }
                )

                continue

            cards.append(
                {
                    "id": f"E{index}",
                    "content": item,
                    "source": item.get(
                        "source",
                        item.get(
                            "source_url"
                        ),
                    ),
                    "source_type": item.get(
                        "source_type"
                    ),
                    "provenance": item.get(
                        "provenance"
                    ),
                    "freshness": item.get(
                        "freshness"
                    ),
                }
            )

        return cards

    # =========================================================
    # Unknowns
    # =========================================================

    def identify_unknowns(
        self,
        evidence: List[Dict[str, Any]],
        graph_path: List[Dict[str, Any]],
    ) -> List[str]:

        unknowns = []

        if not evidence:

            unknowns.append(
                "No supporting graph evidence was found."
            )

        if not graph_path:

            unknowns.append(
                "No explicit relationship path was established."
            )

        return unknowns

    # =========================================================
    # Main
    # =========================================================

    def build(
        self,
        evidence: List[Dict[str, Any]],
        graph_path: List[Dict[str, Any]],
        contradictions: List[Any],
        answer: str = "",
    ) -> Dict[str, Any]:

        evidence_cards = (
            self.build_evidence_cards(
                evidence
            )
        )

        confidence = (
            self.calculate_confidence(
                evidence=evidence,
                graph_path=graph_path,
                contradictions=contradictions,
            )
        )

        unknowns = self.identify_unknowns(
            evidence=evidence,
            graph_path=graph_path,
        )

        return {
            "answer": answer,

            "evidence": evidence_cards,

            "graph_path": graph_path,

            "confidence": confidence,

            "contradictions": contradictions,

            "unknowns": unknowns,

            "why_this_answer": {
                "graph_evidence_count": len(
                    evidence
                ),
                "path_count": len(
                    graph_path
                ),
                "contradiction_count": len(
                    contradictions
                ),
                "confidence": confidence,
            },
        }