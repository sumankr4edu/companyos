from __future__ import annotations

from typing import Any, Dict, List


class ContradictionAgent:
    """
    Detects conflicting or potentially stale facts in the company graph.

    This agent does not invent contradictions. It only reports conflicts
    that can be observed from FalkorDB evidence.
    """

    def detect(
        self,
        records: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        if not records:
            return []

        contradictions: List[Dict[str, Any]] = []

        # --------------------------------------------------------
        # Normalize records
        # --------------------------------------------------------

        normalized = []

        for record in records:
            if not isinstance(record, dict):
                continue

            clean = {}

            for key, value in record.items():
                clean[str(key).lower().strip()] = value

            normalized.append(clean)

        # --------------------------------------------------------
        # Detect conflicting scalar values
        # --------------------------------------------------------

        grouped: Dict[str, List[Any]] = {}

        for record in normalized:
            entity = (
                record.get("entity")
                or record.get("name")
                or record.get("person")
                or record.get("service")
                or record.get("project")
            )

            attribute = (
                record.get("attribute")
                or record.get("field")
                or record.get("property")
            )

            value = record.get("value")

            if entity and attribute and value is not None:
                key = f"{entity}|{attribute}"

                grouped.setdefault(
                    key,
                    [],
                ).append(value)

        for key, values in grouped.items():

            unique_values = []

            for value in values:
                if value not in unique_values:
                    unique_values.append(value)

            if len(unique_values) > 1:

                entity, attribute = key.split(
                    "|",
                    1,
                )

                contradictions.append(
                    {
                        "type": "conflicting_values",
                        "entity": entity,
                        "attribute": attribute,
                        "values": unique_values,
                        "severity": "medium",
                        "explanation": (
                            f"The graph contains multiple values for "
                            f"{attribute} on {entity}."
                        ),
                    }
                )

        # --------------------------------------------------------
        # Detect ownership conflicts
        # --------------------------------------------------------

        ownership: Dict[str, List[str]] = {}

        for record in normalized:

            relationship = str(
                record.get("relationship")
                or record.get("rel_type")
                or record.get("type")
                or ""
            ).upper()

            if relationship != "OWNS":
                continue

            service = (
                record.get("service")
                or record.get("entity")
                or record.get("target")
            )

            person = (
                record.get("person")
                or record.get("owner")
                or record.get("source")
            )

            if service and person:
                ownership.setdefault(
                    str(service),
                    [],
                ).append(str(person))

        for service, owners in ownership.items():

            unique_owners = list(dict.fromkeys(owners))

            if len(unique_owners) > 1:

                contradictions.append(
                    {
                        "type": "multiple_owners",
                        "entity": service,
                        "owners": unique_owners,
                        "severity": "high",
                        "explanation": (
                            f"{service} has multiple OWNS relationships "
                            f"in the retrieved graph evidence."
                        ),
                    }
                )

        return contradictions