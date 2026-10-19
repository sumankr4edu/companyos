from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class FreshnessAgent:

    def __init__(
        self,
        stale_after_days: int = 180,
    ):
        self.stale_after_days = stale_after_days

    def analyze(
        self,
        records: List[Dict[str, Any]],
    ) -> Dict[str, Any]:

        now = datetime.now(timezone.utc)

        stale_records: List[Dict[str, Any]] = []
        fresh_records: List[Dict[str, Any]] = []
        unknown_records: List[Dict[str, Any]] = []

        for record in records:

            if not isinstance(record, dict):
                continue

            timestamp = self._extract_timestamp(
                record
            )

            if timestamp is None:

                unknown_records.append(
                    {
                        "record": record,
                        "reason": "No timestamp available.",
                    }
                )

                continue

            age_days = (
                now - timestamp
            ).total_seconds() / 86400

            enriched = {
                **record,
                "age_days": round(
                    age_days,
                    2,
                ),
            }

            if age_days > self.stale_after_days:

                stale_records.append(
                    enriched
                )

            else:

                fresh_records.append(
                    enriched
                )

        total = (
            len(stale_records)
            + len(fresh_records)
            + len(unknown_records)
        )

        if total == 0:
            freshness_score = None

        else:
            freshness_score = round(
                len(fresh_records) / total,
                2,
            )

        return {
            "stale_after_days": self.stale_after_days,
            "fresh_records": fresh_records,
            "stale_records": stale_records,
            "unknown_records": unknown_records,
            "freshness_score": freshness_score,
            "total_records": total,
        }

    # ========================================================
    # Timestamp Extraction
    # ========================================================

    def _extract_timestamp(
        self,
        record: Dict[str, Any],
    ) -> Optional[datetime]:

        candidates = (
            "updated_at",
            "updated",
            "modified_at",
            "created_at",
            "created",
            "timestamp",
        )

        for field in candidates:

            value = record.get(field)

            if value is None:
                continue

            parsed = self._parse_datetime(
                value
            )

            if parsed:
                return parsed

        return None

    # ========================================================
    # Date Parsing
    # ========================================================

    def _parse_datetime(
        self,
        value: Any,
    ) -> Optional[datetime]:

        if isinstance(
            value,
            datetime,
        ):

            dt = value

        else:

            text = str(value).strip()

            if not text:
                return None

            try:
                dt = datetime.fromisoformat(
                    text.replace(
                        "Z",
                        "+00:00",
                    )
                )

            except ValueError:
                return None

        if dt.tzinfo is None:
            dt = dt.replace(
                tzinfo=timezone.utc
            )

        return dt.astimezone(
            timezone.utc
        )