from datetime import datetime, timezone
from typing import Any


class ProvenanceManager:
    """
    Handles provenance metadata attached to graph entities
    and evidence records.
    """

    REQUIRED_FIELDS = [
        "source_id",
        "source_type",
        "source_url",
        "document_id",
        "author",
        "created_at",
        "updated_at",
        "confidence",
    ]

    def normalize(
        self,
        record: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Normalize a graph record into a predictable provenance shape.
        """

        result = dict(record)

        result.setdefault("source_id", None)
        result.setdefault("source_type", None)
        result.setdefault("source_url", None)
        result.setdefault("document_id", None)
        result.setdefault("author", None)
        result.setdefault("created_at", None)
        result.setdefault("updated_at", None)
        result.setdefault("confidence", 0.5)

        try:
            result["confidence"] = float(
                result["confidence"]
            )
        except (TypeError, ValueError):
            result["confidence"] = 0.5

        result["confidence"] = max(
            0.0,
            min(1.0, result["confidence"]),
        )

        return result

    def enrich(
        self,
        record: dict[str, Any],
        source_id: str,
        source_type: str,
        source_url: str | None = None,
        document_id: str | None = None,
        author: str | None = None,
        confidence: float = 0.8,
    ) -> dict[str, Any]:
        """
        Add provenance metadata to a record.
        """

        now = datetime.now(
            timezone.utc
        ).isoformat()

        enriched = dict(record)

        enriched.update(
            {
                "source_id": source_id,
                "source_type": source_type,
                "source_url": source_url,
                "document_id": document_id,
                "author": author,
                "created_at": enriched.get(
                    "created_at",
                    now,
                ),
                "updated_at": enriched.get(
                    "updated_at",
                    now,
                ),
                "confidence": max(
                    0.0,
                    min(1.0, float(confidence)),
                ),
            }
        )

        return enriched