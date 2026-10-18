from typing import Any, Dict

from graph.client import graph_client


def _serialize_value(value: Any) -> Any:
    """
    Convert FalkorDB result values into JSON-safe Python structures.

    Important:
    FalkorDB Node and Relationship objects must be detected separately.
    Relationships are checked before generic node-like objects.
    """

    if value is None:
        return None

    # Primitive values
    if isinstance(value, (str, int, float, bool)):
        return value

    # Lists / tuples
    if isinstance(value, (list, tuple)):
        return [
            _serialize_value(item)
            for item in value
        ]

    # Dictionaries
    if isinstance(value, dict):
        return {
            str(key): _serialize_value(item)
            for key, item in value.items()
        }

    # ---------------------------------------------------------
    # RELATIONSHIP
    # ---------------------------------------------------------
    #
    # FalkorDB relationships expose relation/type information.
    # Check this BEFORE node detection.
    #
    if hasattr(value, "relation"):
        relationship_type = getattr(
            value,
            "relation",
            None,
        )

        properties = getattr(
            value,
            "properties",
            {},
        )

        relationship_id = getattr(
            value,
            "id",
            None,
        )

        return {
            "type": "relationship",
            "id": relationship_id,
            "relation": relationship_type,
            "properties": _serialize_value(
                properties
            ),
        }

    # ---------------------------------------------------------
    # NODE
    # ---------------------------------------------------------
    if hasattr(value, "properties") and hasattr(
        value,
        "id",
    ):
        properties = getattr(
            value,
            "properties",
            {},
        )

        result = {
            "type": "node",
            "id": getattr(
                value,
                "id",
                None,
            ),
            "properties": _serialize_value(
                properties
            ),
        }

        if hasattr(value, "labels"):
            result["labels"] = _serialize_value(
                getattr(
                    value,
                    "labels",
                    [],
                )
            )

        return result

    # ---------------------------------------------------------
    # PATH
    # ---------------------------------------------------------
    if hasattr(value, "nodes") and hasattr(
        value,
        "relationships",
    ):
        return {
            "type": "path",
            "nodes": _serialize_value(
                getattr(
                    value,
                    "nodes",
                    [],
                )
            ),
            "relationships": _serialize_value(
                getattr(
                    value,
                    "relationships",
                    [],
                )
            ),
        }

    # Generic object fallback
    if hasattr(value, "__dict__"):
        try:
            return {
                str(key): _serialize_value(item)
                for key, item in value.__dict__.items()
                if not str(key).startswith("_")
            }
        except Exception:
            pass

    return str(value)


def run_cypher(
    cypher: str,
    graph_name: str = "novatech",
) -> Dict[str, Any]:

    graph = graph_client.get_graph(
        graph_name
    )

    result = graph.query(cypher)

    return {
        "header": [
            str(column)
            for column in getattr(
                result,
                "header",
                [],
            )
        ],
        "rows": [
            [
                _serialize_value(value)
                for value in row
            ]
            for row in getattr(
                result,
                "result_set",
                [],
            )
        ],
    }