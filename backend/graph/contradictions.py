from collections import defaultdict
from typing import Any


class ContradictionDetector:
    """
    Detect potentially conflicting graph evidence.

    The first implementation focuses on explicit property
    conflicts between records referring to the same entity.
    """

    COMPARISON_FIELDS = [
        "status",
        "owner",
        "decision",
        "description",
        "state",
    ]

    def detect(
        self,
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        grouped = defaultdict(list)

        for record in records:
            entity = (
                record.get("name")
                or record.get("entity")
                or record.get("title")
            )

            if entity:
                grouped[entity].append(record)

        contradictions = []

        for entity, items in grouped.items():
            for field in self.COMPARISON_FIELDS:

                values = []

                for item in items:
                    value = item.get(field)

                    if value is None:
                        continue

                    value = str(value).strip()

                    if value and value not in values:
                        values.append(value)

                if len(values) > 1:
                    contradictions.append(
                        {
                            "entity": entity,
                            "field": field,
                            "values": values,
                            "severity": self._severity(
                                field
                            ),
                        }
                    )

        return contradictions

    def _severity(self, field: str) -> str:
        if field in {
            "status",
            "owner",
            "state",
        }:
            return "high"

        if field == "decision":
            return "medium"

        return "low"