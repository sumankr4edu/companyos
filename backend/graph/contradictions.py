from collections import defaultdict
from typing import Any


class ContradictionDetector:
    """
    Detect potentially conflicting graph evidence.

    Detects:
    1. Explicit property conflicts on the same entity.
    2. Multiple owners for the same entity.
    3. Conflicting relationship targets.
    4. Duplicate relationship evidence without treating
       different relationship types as contradictions.
    """

    COMPARISON_FIELDS = [
        "status",
        "owner",
        "decision",
        "description",
        "state",
    ]

    OWNER_RELATIONSHIPS = {
        "OWNS",
        "OWNER",
    }

    RELATIONSHIP_FIELDS = {
        "relationship",
        "relation",
        "relationship_type",
        "type",
    }

    ENTITY_FIELDS = [
        "name",
        "entity",
        "title",
        "service",
        "project",
        "system",
    ]

    SUBJECT_FIELDS = [
        "person",
        "owner",
        "source",
        "subject",
        "from",
    ]

    TARGET_FIELDS = [
        "entity",
        "name",
        "service",
        "project",
        "system",
        "target",
        "to",
    ]

    def detect(
        self,
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        if not records:
            return []

        grouped = self._group_by_entity(records)

        contradictions = []

        # ---------------------------------------------------------
        # 1. Explicit property conflicts
        # ---------------------------------------------------------
        contradictions.extend(
            self._detect_property_conflicts(grouped)
        )

        # ---------------------------------------------------------
        # 2. Multiple owners
        # ---------------------------------------------------------
        contradictions.extend(
            self._detect_multiple_owners(records)
        )

        # ---------------------------------------------------------
        # 3. Conflicting relationship targets
        # ---------------------------------------------------------
        contradictions.extend(
            self._detect_relationship_conflicts(records)
        )

        return self._deduplicate_contradictions(
            contradictions
        )

    # =============================================================
    # Grouping
    # =============================================================

    def _group_by_entity(
        self,
        records: list[dict[str, Any]],
    ) -> dict[str, list[dict[str, Any]]]:
        grouped = defaultdict(list)

        for record in records:
            entity = self._extract_entity(record)

            if entity:
                grouped[entity].append(record)

        return grouped

    # =============================================================
    # Property contradictions
    # =============================================================

    def _detect_property_conflicts(
        self,
        grouped: dict[str, list[dict[str, Any]]],
    ) -> list[dict[str, Any]]:
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
                            "type": "property_conflict",
                        }
                    )

        return contradictions

    # =============================================================
    # Multiple owner detection
    # =============================================================

    def _detect_multiple_owners(
        self,
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Detect cases such as:

            Maya Singh --OWNS--> Payment Service
            Amit Chen  --OWNS--> Payment Service

        Different relationship types such as WORKED_ON and OWNS
        are intentionally not treated as contradictions.
        """

        ownership = defaultdict(set)

        for record in records:
            relationship = self._extract_relationship(
                record
            )

            if relationship not in self.OWNER_RELATIONSHIPS:
                continue

            target = self._extract_target(record)
            owner = self._extract_subject(record)

            if not target or not owner:
                continue

            ownership[target].add(owner)

        contradictions = []

        for entity, owners in ownership.items():
            if len(owners) <= 1:
                continue

            contradictions.append(
                {
                    "entity": entity,
                    "field": "owner",
                    "values": sorted(owners),
                    "severity": "high",
                    "type": "multiple_owners",
                }
            )

        return contradictions

    # =============================================================
    # Relationship conflict detection
    # =============================================================

    def _detect_relationship_conflicts(
        self,
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Detect conflicting relationship targets when records
        explicitly expose a relationship type and target.

        Example:

            Project X --OWNS--> Service A
            Project X --OWNS--> Service B

        This is reported as a potential relationship conflict.
        """

        grouped = defaultdict(set)

        for record in records:
            relationship = self._extract_relationship(
                record
            )

            if not relationship:
                continue

            subject = self._extract_subject(record)
            target = self._extract_target(record)

            if not subject or not target:
                continue

            key = (
                subject,
                relationship,
            )

            grouped[key].add(target)

        contradictions = []

        for (
            subject,
            relationship,
        ), targets in grouped.items():

            if len(targets) <= 1:
                continue

            contradictions.append(
                {
                    "entity": subject,
                    "field": relationship,
                    "values": sorted(targets),
                    "severity": self._relationship_severity(
                        relationship
                    ),
                    "type": "relationship_conflict",
                }
            )

        return contradictions

    # =============================================================
    # Extraction helpers
    # =============================================================

    @classmethod
    def _extract_entity(
        cls,
        record: dict[str, Any],
    ) -> str | None:
        for field in cls.ENTITY_FIELDS:
            value = record.get(field)

            if value is None:
                continue

            value = str(value).strip()

            if value:
                return value

        return None

    @classmethod
    def _extract_relationship(
        cls,
        record: dict[str, Any],
    ) -> str:
        for field in cls.RELATIONSHIP_FIELDS:
            value = record.get(field)

            if value is None:
                continue

            value = str(value).strip().upper()

            if value:
                return value

        return ""

    @classmethod
    def _extract_subject(
        cls,
        record: dict[str, Any],
    ) -> str | None:
        for field in cls.SUBJECT_FIELDS:
            value = record.get(field)

            if value is None:
                continue

            value = str(value).strip()

            if value:
                return value

        return None

    @classmethod
    def _extract_target(
        cls,
        record: dict[str, Any],
    ) -> str | None:
        for field in cls.TARGET_FIELDS:
            value = record.get(field)

            if value is None:
                continue

            value = str(value).strip()

            if value:
                return value

        return None

    # =============================================================
    # Severity
    # =============================================================

    def _severity(
        self,
        field: str,
    ) -> str:
        if field in {
            "status",
            "owner",
            "state",
        }:
            return "high"

        if field == "decision":
            return "medium"

        return "low"

    def _relationship_severity(
        self,
        relationship: str,
    ) -> str:
        if relationship in {
            "OWNS",
            "OWNER",
            "REPORTS_TO",
        }:
            return "high"

        if relationship in {
            "DEPENDS_ON",
            "AFFECTS",
            "IMPLEMENTS",
        }:
            return "medium"

        return "low"

    # =============================================================
    # Deduplication
    # =============================================================

    @staticmethod
    def _deduplicate_contradictions(
        contradictions: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        seen = set()
        result = []

        for contradiction in contradictions:
            key = (
                contradiction.get("type"),
                contradiction.get("entity"),
                contradiction.get("field"),
                tuple(
                    sorted(
                        str(value)
                        for value in contradiction.get(
                            "values",
                            [],
                        )
                    )
                ),
            )

            if key in seen:
                continue

            seen.add(key)
            result.append(contradiction)

        return result