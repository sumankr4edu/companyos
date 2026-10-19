from __future__ import annotations

import re


class CypherValidator:
    """
    Security validator for Cypher queries.

    CompanyOS currently exposes graph reads through controlled Cypher.
    Destructive graph mutations are intentionally blocked here.

    Writes should go through explicit application-level action workflows
    such as InvestigationTaskManager / ActionAgent rather than arbitrary
    Cypher supplied by an API caller.
    """

    BLOCKED_PATTERNS = [
        r"\bCREATE\b",
        r"\bDELETE\b",
        r"\bDETACH\s+DELETE\b",
        r"\bSET\b",
        r"\bREMOVE\b",
        r"\bMERGE\b",
        r"\bDROP\b",
        r"\bLOAD\s+CSV\b",
        r"\bCALL\s+DBMS\b",
        r"\bCALL\s+DB\b",
        r"\bCALL\s+APOC\b",
        r"\bFOREACH\b",
        r"\bALTER\b",
        r"\bGRANT\b",
        r"\bREVOKE\b",
    ]

    COMMENT_PATTERNS = [
        r"//",
        r"/\*",
        r"\*/",
    ]

    def __init__(self, max_length: int = 10000):
        self.max_length = max_length

    def validate(self, cypher: str) -> str:
        """
        Validate a Cypher query.

        Returns the normalized query when valid.
        Raises ValueError when the query is unsafe.
        """

        if not isinstance(cypher, str):
            raise ValueError("Cypher query must be a string.")

        query = cypher.strip()

        if not query:
            raise ValueError("Cypher query cannot be empty.")

        if len(query) > self.max_length:
            raise ValueError(
                f"Cypher query exceeds maximum length of {self.max_length}."
            )

        # Reject multiple statements.
        if self._contains_multiple_statements(query):
            raise ValueError(
                "Multiple Cypher statements are not allowed."
            )

        # Reject comments to reduce query-obfuscation/injection surface.
        for pattern in self.COMMENT_PATTERNS:
            if re.search(pattern, query, flags=re.IGNORECASE):
                raise ValueError(
                    "Cypher comments are not allowed."
                )

        # Reject dangerous operations.
        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, query, flags=re.IGNORECASE):
                raise ValueError(
                    f"Unsafe Cypher operation detected: {pattern}"
                )

        # CompanyOS MCP tool is read-only.
        if not re.search(
            r"\b(MATCH|OPTIONAL\s+MATCH|WITH|UNWIND|RETURN|CALL)\b",
            query,
            flags=re.IGNORECASE,
        ):
            raise ValueError(
                "Only read-oriented Cypher queries are allowed."
            )

        return query

    @staticmethod
    def _contains_multiple_statements(query: str) -> bool:
        """
        Allow a single optional trailing semicolon.
        Reject additional statements.
        """

        stripped = query.strip()

        if ";" not in stripped:
            return False

        if stripped.endswith(";"):
            stripped = stripped[:-1].rstrip()

        return ";" in stripped