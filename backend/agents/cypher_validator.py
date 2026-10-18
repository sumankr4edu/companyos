import re


class CypherValidator:
    """
    Security boundary for agent-generated Cypher.

    CompanyOS agents are allowed to perform read-only graph
    operations through this validator.
    """

    BLOCKED_KEYWORDS = [
        "CREATE",
        "DELETE",
        "DETACH",
        "SET",
        "REMOVE",
        "MERGE",
        "DROP",
        "LOAD CSV",
        "CALL dbms",
        "CALL db.",
        "FOREACH",
    ]

    ALLOWED_STARTS = (
        "MATCH",
        "OPTIONAL MATCH",
        "WITH",
        "UNWIND",
        "RETURN",
    )

    def validate(self, query: str) -> tuple[bool, str]:
        if not query or not query.strip():
            return False, "Cypher query is empty."

        normalized = re.sub(
            r"\s+",
            " ",
            query.strip(),
        ).upper()

        # --------------------------------------------------------
        # Block dangerous keywords
        # --------------------------------------------------------

        for keyword in self.BLOCKED_KEYWORDS:
            if keyword in normalized:
                return False, f"Blocked Cypher operation: {keyword}"

        # --------------------------------------------------------
        # Only allow read-oriented query starts
        # --------------------------------------------------------

        if not normalized.startswith(self.ALLOWED_STARTS):
            return False, (
                "Cypher query must start with a read-only clause: "
                "MATCH, OPTIONAL MATCH, WITH, UNWIND, or RETURN."
            )

        # --------------------------------------------------------
        # Block multiple statements
        # --------------------------------------------------------

        statements = [
            statement.strip()
            for statement in query.split(";")
            if statement.strip()
        ]

        if len(statements) > 1:
            return False, "Multiple Cypher statements are not allowed."

        # --------------------------------------------------------
        # Block comments
        # --------------------------------------------------------

        if "--" in query or "/*" in query or "*/" in query:
            return False, "Cypher comments are not allowed."

        # --------------------------------------------------------
        # Basic dangerous procedure detection
        # --------------------------------------------------------

        if re.search(
            r"\bCALL\s+(db|dbms|apoc)\.",
            normalized,
        ):
            return False, "Database procedures are not allowed."

        return True, "Cypher query validated."