from datetime import datetime, timezone


class FreshnessCalculator:
    """
    Calculates evidence freshness.

    Freshness is intentionally deterministic so the LLM
    cannot arbitrarily decide whether information is recent.
    """

    def score(
        self,
        updated_at: str | None,
    ) -> float:
        if not updated_at:
            return 0.5

        try:
            timestamp = datetime.fromisoformat(
                updated_at.replace(
                    "Z",
                    "+00:00",
                )
            )

            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(
                    tzinfo=timezone.utc
                )

            now = datetime.now(timezone.utc)

            age_days = (
                now - timestamp
            ).total_seconds() / 86400

            if age_days <= 1:
                return 1.0

            if age_days <= 7:
                return 0.9

            if age_days <= 30:
                return 0.75

            if age_days <= 90:
                return 0.6

            if age_days <= 365:
                return 0.4

            return 0.2

        except (ValueError, TypeError):
            return 0.5