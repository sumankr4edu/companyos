from graph.contradictions import ContradictionDetector
from graph.freshness import FreshnessCalculator
from graph.provenance import ProvenanceManager


class EvidenceManager:
    """
    Converts raw FalkorDB results into structured,
    auditable evidence.
    """

    def __init__(self):
        self.provenance = ProvenanceManager()
        self.freshness = FreshnessCalculator()
        self.contradictions = ContradictionDetector()

    def process(
        self,
        records: list[dict],
    ) -> dict:
        normalized = [
            self.provenance.normalize(record)
            for record in records
        ]

        for record in normalized:
            record["freshness"] = self.freshness.score(
                record.get("updated_at")
            )

            record["evidence_score"] = round(
                (
                    record["confidence"]
                    + record["freshness"]
                )
                / 2,
                3,
            )

        contradictions = self.contradictions.detect(
            normalized
        )

        normalized.sort(
            key=lambda item: item.get(
                "evidence_score",
                0,
            ),
            reverse=True,
        )

        return {
            "evidence": normalized,
            "contradictions": contradictions,
            "count": len(normalized),
        }