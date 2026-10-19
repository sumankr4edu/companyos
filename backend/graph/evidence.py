from typing import Any

from graph.contradictions import ContradictionDetector
from graph.freshness import FreshnessCalculator
from graph.provenance import ProvenanceManager


class EvidenceManager:
    """
    Converts raw FalkorDB results into structured,
    auditable evidence.

    Responsibilities:
    - Normalize provenance
    - Remove exact duplicate evidence
    - Preserve genuinely different relationships
    - Calculate freshness
    - Calculate evidence confidence
    - Detect contradictions
    - Bound the final evidence set
    """

    MAX_EVIDENCE = 20

    def __init__(self):
        self.provenance = ProvenanceManager()
        self.freshness = FreshnessCalculator()
        self.contradictions = ContradictionDetector()

    # =========================================================
    # Normalization helpers
    # =========================================================

    @staticmethod
    def _normalize_value(value: Any) -> Any:
        """
        Produce a stable representation for evidence comparison.
        """

        if value is None:
            return None

        if isinstance(value, str):
            return value.strip()

        if isinstance(value, (list, tuple)):
            return tuple(
                EvidenceManager._normalize_value(item)
                for item in value
            )

        if isinstance(value, dict):
            return tuple(
                sorted(
                    (
                        str(key),
                        EvidenceManager._normalize_value(val),
                    )
                    for key, val in value.items()
                )
            )

        return value

    @classmethod
    def _fingerprint(cls, record: dict) -> tuple:
        """
        Build a deterministic fingerprint.

        Every field participates so that two genuinely different
        graph facts are preserved.

        Example:

        Maya + OWNS + Payment Service
        !=
        Maya + WORKED_ON + Payment Service
        """

        return tuple(
            sorted(
                (
                    str(key),
                    cls._normalize_value(value),
                )
                for key, value in record.items()
                if key not in {
                    "freshness",
                    "evidence_score",
                }
            )
        )

    @classmethod
    def _deduplicate(
        cls,
        records: list[dict],
    ) -> list[dict]:
        """
        Remove exact duplicate evidence records.

        Important:
        We DO NOT deduplicate by person or entity alone.

        Therefore:

            Maya OWNS Payment Service
            Amit OWNS Payment Service

        remain separate records and can be detected as a
        contradiction later.
        """

        seen = set()
        unique = []

        for record in records:
            fingerprint = cls._fingerprint(record)

            if fingerprint in seen:
                continue

            seen.add(fingerprint)
            unique.append(record)

        return unique

    # =========================================================
    # Evidence processing
    # =========================================================

    def process(
        self,
        records: list[dict],
    ) -> dict:

        if not records:
            return {
                "evidence": [],
                "contradictions": [],
                "count": 0,
                "raw_count": 0,
                "deduplicated_count": 0,
            }

        raw_count = len(records)

        # -----------------------------------------------------
        # 1. Normalize provenance
        # -----------------------------------------------------

        normalized = [
            self.provenance.normalize(record)
            for record in records
            if isinstance(record, dict)
        ]

        # -----------------------------------------------------
        # 2. Remove exact duplicate records
        # -----------------------------------------------------

        normalized = self._deduplicate(normalized)

        deduplicated_count = len(normalized)

        # -----------------------------------------------------
        # 3. Calculate freshness + evidence score
        # -----------------------------------------------------

        for record in normalized:

            freshness_score = self.freshness.score(
                record.get("updated_at")
            )

            confidence = record.get(
                "confidence",
                0.0,
            )

            try:
                confidence = float(confidence)
            except (
                TypeError,
                ValueError,
            ):
                confidence = 0.0

            try:
                freshness_score = float(
                    freshness_score
                )
            except (
                TypeError,
                ValueError,
            ):
                freshness_score = 0.0

            record["freshness"] = round(
                freshness_score,
                3,
            )

            record["evidence_score"] = round(
                (
                    confidence
                    + freshness_score
                )
                / 2,
                3,
            )

        # -----------------------------------------------------
        # 4. Detect contradictions BEFORE bounding evidence
        # -----------------------------------------------------
        #
        # This is important.
        #
        # If we have:
        #
        # Maya Singh -> OWNS -> Payment Service
        # Amit Chen  -> OWNS -> Payment Service
        #
        # both must reach the contradiction detector.
        #

        contradictions = self.contradictions.detect(
            normalized
        )

        # -----------------------------------------------------
        # 5. Rank evidence
        # -----------------------------------------------------

        normalized.sort(
            key=lambda item: (
                item.get(
                    "evidence_score",
                    0.0,
                ),
                str(
                    item.get(
                        "updated_at",
                        "",
                    )
                ),
            ),
            reverse=True,
        )

        # -----------------------------------------------------
        # 6. Bound evidence sent downstream
        # -----------------------------------------------------

        bounded = normalized[
            : self.MAX_EVIDENCE
        ]

        return {
            "evidence": bounded,
            "contradictions": contradictions,
            "count": len(bounded),

            # Useful for observability / judge demo.
            "raw_count": raw_count,
            "deduplicated_count": deduplicated_count,
            "truncated": (
                len(normalized)
                > self.MAX_EVIDENCE
            ),
        }