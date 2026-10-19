from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from graph.client import graph_client


class ConversationStore:
    """
    Persistent conversation storage backed by FalkorDB.

    Graph model:

        (:Conversation)-[:HAS_TURN]->(:ConversationTurn)

    Conversation properties:
        id
        user_id
        title
        graph_name
        created_at
        updated_at
        turn_count

    ConversationTurn properties:
        id
        user_id
        question
        answer
        entities_json
        plan_json
        graph_path_summary
        evidence_count
        confidence
        retrieval_mode
        graph_name
        created_at
    """

    def __init__(self, graph_name: str = "novatech"):
        self.graph_name = graph_name

    # ========================================================
    # Basic Helpers
    # ========================================================

    @staticmethod
    def _escape(value: Any) -> str:
        """
        Safely escape a string for internal Cypher construction.

        These queries are generated internally and are not exposed
        as arbitrary user Cypher.
        """

        if value is None:
            return ""

        return (
            str(value)
            .replace("\\", "\\\\")
            .replace("'", "\\'")
            .replace("\n", "\\n")
            .replace("\r", "\\r")
        )

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _query(self, cypher: str):
        return graph_client.query(
            cypher,
            self.graph_name,
        )

    # ========================================================
    # FalkorDB Serialization
    # ========================================================

    @classmethod
    def _serialize(cls, value: Any) -> Any:
        """
        Convert FalkorDB / Redis / Python objects into
        JSON-safe Python primitives.

        This is important because FalkorDB result objects may
        expose properties through descriptors/properties that
        FastAPI's jsonable_encoder cannot serialize directly.
        """

        if value is None:
            return None

        # Primitive values
        if isinstance(
            value,
            (
                str,
                int,
                float,
                bool,
            ),
        ):
            return value

        # Bytes
        if isinstance(value, bytes):
            try:
                return value.decode("utf-8")
            except Exception:
                return str(value)

        # Dictionaries
        if isinstance(value, dict):
            return {
                str(cls._serialize(key)): cls._serialize(val)
                for key, val in value.items()
            }

        # Lists / tuples / sets
        if isinstance(
            value,
            (
                list,
                tuple,
                set,
            ),
        ):
            return [
                cls._serialize(item)
                for item in value
            ]

        # FalkorDB node-like objects
        labels = getattr(value, "labels", None)
        properties = getattr(value, "properties", None)

        if labels is not None or properties is not None:
            result: Dict[str, Any] = {}

            try:
                if labels is not None:
                    result["labels"] = cls._serialize(
                        list(labels)
                        if not isinstance(labels, str)
                        else [labels]
                    )
            except Exception:
                pass

            try:
                if properties is not None:
                    result["properties"] = cls._serialize(
                        properties
                    )
            except Exception:
                pass

            # Some FalkorDB objects expose an id property.
            try:
                object_id = getattr(value, "id", None)

                if object_id is not None and not callable(object_id):
                    result["id"] = cls._serialize(
                        object_id
                    )
            except Exception:
                pass

            if result:
                return result

        # FalkorDB relationship-like objects
        relation_type = getattr(
            value,
            "relation",
            None,
        )

        if relation_type is None:
            relation_type = getattr(
                value,
                "type",
                None,
            )

        if relation_type is not None:
            result = {}

            try:
                result["type"] = cls._serialize(
                    relation_type
                )
            except Exception:
                pass

            try:
                result["properties"] = cls._serialize(
                    getattr(
                        value,
                        "properties",
                        {},
                    )
                )
            except Exception:
                result["properties"] = {}

            try:
                start = getattr(
                    value,
                    "src_node",
                    None,
                )

                if start is not None:
                    result["source"] = cls._serialize(
                        start
                    )
            except Exception:
                pass

            try:
                end = getattr(
                    value,
                    "dest_node",
                    None,
                )

                if end is not None:
                    result["target"] = cls._serialize(
                        end
                    )
            except Exception:
                pass

            if result:
                return result

        # Generic objects with __dict__
        try:
            if hasattr(value, "__dict__"):
                return {
                    str(key): cls._serialize(val)
                    for key, val in vars(value).items()
                }
        except Exception:
            pass

        # JSON strings
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception:
                return value

        # Final safe representation
        return str(value)

    # ========================================================
    # Result Normalization
    # ========================================================

    @classmethod
    def _normalize_result(cls, result: Any) -> Dict[str, Any]:
        """
        Normalize FalkorDB ResultSet into JSON-safe Python dictionaries.

        FalkorDB can return headers in forms such as:

            ["conversation_id", "user_id"]

        or:

            [[1, "conversation_id"], [1, "user_id"]]

        The second form must be converted to the actual column names.
        """

        if result is None:
            return {
                "headers": [],
                "rows": [],
                "records": [],
            }

        headers: List[str] = []
        rows: List[List[Any]] = []

        # ========================================================
        # Headers
        # ========================================================

        try:
            raw_headers = getattr(
                result,
                "header",
                None,
            )

            if raw_headers is None:
                raw_headers = getattr(
                    result,
                    "headers",
                    None,
                )

            if raw_headers is not None:

                for header in raw_headers:

                    # FalkorDB may return:
                    #
                    # [1, "conversation_id"]
                    #
                    # where the second element is the actual
                    # column name.

                    if isinstance(
                        header,
                        (list, tuple),
                    ):
                        if len(header) >= 2:
                            header_name = header[-1]
                        elif len(header) == 1:
                            header_name = header[0]
                        else:
                            header_name = ""
                    else:
                        header_name = header

                    headers.append(
                        str(
                            cls._serialize(
                                header_name
                            )
                        )
                    )

        except Exception:
            headers = []

        # ========================================================
        # Rows
        # ========================================================

        try:
            raw_rows = getattr(
                result,
                "result_set",
                None,
            )

            if raw_rows is None:
                raw_rows = getattr(
                    result,
                    "rows",
                    None,
                )

            if raw_rows is not None:

                for row in raw_rows:

                    if isinstance(
                        row,
                        (list, tuple),
                    ):
                        rows.append([
                            cls._serialize(value)
                            for value in row
                        ])
                    else:
                        rows.append([
                            cls._serialize(row)
                        ])

        except Exception:
            rows = []

        # ========================================================
        # Convert rows → dictionaries
        # ========================================================

        records: List[Dict[str, Any]] = []

        for row in rows:

            record: Dict[str, Any] = {}

            for index, header in enumerate(headers):

                if index < len(row):
                    record[header] = row[index]
                else:
                    record[header] = None

            records.append(record)

        return {
            "headers": headers,
            "rows": rows,
            "records": records,
        }
    def ensure_conversation(
        self,
        conversation_id: str,
        user_id: str,
        title: str = "New Investigation",
    ) -> Dict[str, Any]:

        now = self._now()

        conversation_id = self._escape(
            conversation_id
        )

        user_id = self._escape(
            user_id
        )

        title = self._escape(
            title
        )

        graph_name = self._escape(
            self.graph_name
        )

        cypher = f"""
        MERGE (c:Conversation {{
            id: '{conversation_id}'
        }})

        ON CREATE SET
            c.user_id = '{user_id}',
            c.title = '{title}',
            c.graph_name = '{graph_name}',
            c.created_at = '{now}',
            c.updated_at = '{now}',
            c.turn_count = 0

        SET
            c.updated_at = '{now}'

        RETURN
            c.id AS conversation_id,
            c.user_id AS user_id,
            c.title AS title,
            c.graph_name AS graph_name,
            c.created_at AS created_at,
            c.updated_at AS updated_at,
            c.turn_count AS turn_count
        """

        result = self._query(cypher)

        normalized = self._normalize_result(
            result
        )

        if normalized["records"]:
            return normalized["records"][0]

        return {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "title": title,
            "graph_name": graph_name,
            "created_at": now,
            "updated_at": now,
            "turn_count": 0,
        }

    def create_conversation(
        self,
        user_id: str,
        title: str = "New Investigation",
    ) -> Dict[str, Any]:

        conversation_id = (
            f"conv_{uuid.uuid4().hex}"
        )

        return self.ensure_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            title=title,
        )

    # ========================================================
    # Save Conversation Turn
    # ========================================================

    def save_turn(
        self,
        conversation_id: str,
        user_id: str,
        question: str,
        answer: str,
        plan: Optional[Dict[str, Any]] = None,
        entities: Optional[List[Any]] = None,
        graph_path: Optional[Dict[str, Any]] = None,
        evidence_count: int = 0,
        confidence: float = 0.0,
        retrieval_mode: str = "graph_first",
    ) -> Dict[str, Any]:

        turn_id = (
            f"turn_{uuid.uuid4().hex}"
        )

        now = self._now()

        entities_json = json.dumps(
            self._serialize(
                entities or []
            ),
            ensure_ascii=False,
        )

        plan_json = json.dumps(
            self._serialize(
                plan or {}
            ),
            ensure_ascii=False,
        )

        graph_path_summary = self._build_path_summary(
            graph_path
        )

        cypher = f"""
        MATCH (c:Conversation {{
            id: '{self._escape(conversation_id)}'
        }})

        WHERE c.user_id = '{self._escape(user_id)}'

        CREATE (t:ConversationTurn {{
            id: '{self._escape(turn_id)}',
            user_id: '{self._escape(user_id)}',
            question: '{self._escape(question)}',
            answer: '{self._escape(answer)}',
            entities_json: '{self._escape(entities_json)}',
            plan_json: '{self._escape(plan_json)}',
            graph_path_summary: '{self._escape(graph_path_summary)}',
            evidence_count: {int(evidence_count)},
            confidence: {float(confidence)},
            retrieval_mode: '{self._escape(retrieval_mode)}',
            graph_name: '{self._escape(self.graph_name)}',
            created_at: '{self._escape(now)}'
        }})

        CREATE (c)-[:HAS_TURN]->(t)

        SET
            c.updated_at = '{self._escape(now)}',
            c.turn_count = coalesce(c.turn_count, 0) + 1

        RETURN
            t.id AS turn_id,
            c.id AS conversation_id,
            t.question AS question,
            t.answer AS answer,
            t.evidence_count AS evidence_count,
            t.confidence AS confidence,
            t.retrieval_mode AS retrieval_mode,
            t.created_at AS created_at,
            c.turn_count AS turn_count
        """

        result = self._query(cypher)

        normalized = self._normalize_result(
            result
        )

        if normalized["records"]:
            record = normalized["records"][0]

            return {
                "success": True,
                **record,
            }

        return {
            "success": False,
            "conversation_id": conversation_id,
            "turn_id": turn_id,
            "error": "Conversation was not found or turn could not be persisted.",
        }

    # ========================================================
    # Path Summary
    # ========================================================

    @classmethod
    def _build_path_summary(
        cls,
        graph_path: Optional[Dict[str, Any]],
    ) -> str:

        if not graph_path:
            return ""

        if not isinstance(
            graph_path,
            dict,
        ):
            return str(graph_path)

        display = graph_path.get(
            "display"
        )

        if display:
            return str(display)

        nodes = graph_path.get(
            "nodes",
            [],
        )

        names: List[str] = []

        if isinstance(nodes, list):
            for node in nodes:
                if isinstance(node, dict):
                    properties = node.get(
                        "properties",
                        node,
                    )

                    if isinstance(
                        properties,
                        dict,
                    ):
                        name = (
                            properties.get("name")
                            or properties.get("title")
                            or properties.get("id")
                        )

                        if name:
                            names.append(
                                str(name)
                            )

        return " -> ".join(names)

    # ========================================================
    # Get Conversation
    # ========================================================

    def get_conversation(
        self,
        conversation_id: str,
        user_id: str,
        include_turns: bool = True,
    ) -> Optional[Dict[str, Any]]:

        cypher = f"""
        MATCH (c:Conversation {{
            id: '{self._escape(conversation_id)}'
        }})

        WHERE c.user_id = '{self._escape(user_id)}'

        RETURN
            c.id AS conversation_id,
            c.user_id AS user_id,
            c.title AS title,
            c.graph_name AS graph_name,
            c.created_at AS created_at,
            c.updated_at AS updated_at,
            c.turn_count AS turn_count
        """

        result = self._query(cypher)

        normalized = self._normalize_result(
            result
        )

        if not normalized["records"]:
            return None

        conversation = normalized[
            "records"
        ][0]

        if include_turns:
            conversation["turns"] = self.recent_turns(
                conversation_id=conversation_id,
                user_id=user_id,
                limit=100,
            )

        return conversation

    # ========================================================
    # List Conversations
    # ========================================================

    def list_conversations(
        self,
        user_id: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:

        limit = max(
            1,
            min(
                int(limit),
                100,
            ),
        )

        cypher = f"""
        MATCH (c:Conversation)

        WHERE c.user_id = '{self._escape(user_id)}'

        RETURN
            c.id AS conversation_id,
            c.user_id AS user_id,
            c.title AS title,
            c.graph_name AS graph_name,
            c.created_at AS created_at,
            c.updated_at AS updated_at,
            c.turn_count AS turn_count

        ORDER BY c.updated_at DESC

        LIMIT {limit}
        """

        result = self._query(cypher)

        normalized = self._normalize_result(
            result
        )

        return normalized["records"]

    # ========================================================
    # Recent Turns
    # ========================================================

    def recent_turns(
        self,
        conversation_id: str,
        user_id: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:

        limit = max(
            1,
            min(
                int(limit),
                100,
            ),
        )

        cypher = f"""
        MATCH (
            c:Conversation {{
                id: '{self._escape(conversation_id)}'
            }}
        )-[:HAS_TURN]->(t:ConversationTurn)

        WHERE c.user_id = '{self._escape(user_id)}'

        RETURN
            t.id AS turn_id,
            c.id AS conversation_id,
            t.question AS question,
            t.answer AS answer,
            t.entities_json AS entities_json,
            t.plan_json AS plan_json,
            t.graph_path_summary AS graph_path_summary,
            t.evidence_count AS evidence_count,
            t.confidence AS confidence,
            t.retrieval_mode AS retrieval_mode,
            t.graph_name AS graph_name,
            t.created_at AS created_at

        ORDER BY t.created_at DESC

        LIMIT {limit}
        """

        result = self._query(cypher)

        normalized = self._normalize_result(
            result
        )

        turns = []

        for record in normalized["records"]:
            record = dict(record)

            # Decode JSON fields.
            try:
                record["entities"] = json.loads(
                    record.pop(
                        "entities_json",
                        "[]",
                    )
                )
            except Exception:
                record["entities"] = []

            try:
                record["plan"] = json.loads(
                    record.pop(
                        "plan_json",
                        "{}",
                    )
                )
            except Exception:
                record["plan"] = {}

            turns.append(record)

        return turns

    # ========================================================
    # Recent Alias
    # ========================================================

    def recent(
        self,
        conversation_id: str,
        user_id: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:

        return self.recent_turns(
            conversation_id=conversation_id,
            user_id=user_id,
            limit=limit,
        )

    # ========================================================
    # Search Conversation Memory
    # ========================================================

    def search_memory(
        self,
        question: str,
        user_id: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:

        limit = max(
            1,
            min(
                int(limit),
                20,
            ),
        )

        tokens = [
            token.strip().lower()
            for token in question.split()
            if len(token.strip()) >= 3
        ]

        if not tokens:
            return []

        conditions = []

        for token in tokens[:10]:
            escaped = self._escape(token)

            conditions.append(
                "("
                f"toLower(t.question) CONTAINS '{escaped}' "
                f"OR toLower(t.answer) CONTAINS '{escaped}' "
                f"OR toLower(t.graph_path_summary) CONTAINS '{escaped}'"
                ")"
            )

        where_clause = " OR ".join(
            conditions
        )

        cypher = f"""
        MATCH (c:Conversation)-[:HAS_TURN]->(t:ConversationTurn)

        WHERE c.user_id = '{self._escape(user_id)}'
          AND ({where_clause})

        RETURN
            t.id AS turn_id,
            c.id AS conversation_id,
            c.title AS conversation_title,
            t.question AS question,
            t.answer AS answer,
            t.graph_path_summary AS graph_path_summary,
            t.evidence_count AS evidence_count,
            t.confidence AS confidence,
            t.created_at AS created_at

        ORDER BY t.created_at DESC

        LIMIT {limit}
        """

        result = self._query(cypher)

        normalized = self._normalize_result(
            result
        )

        return normalized["records"]

    # ========================================================
    # Search Alias
    # ========================================================

    def search(
        self,
        question: str,
        user_id: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:

        return self.search_memory(
            question=question,
            user_id=user_id,
            limit=limit,
        )

    # ========================================================
    # Delete Conversation
    # ========================================================

    def delete_conversation(
        self,
        conversation_id: str,
        user_id: str,
    ) -> Dict[str, Any]:

        cypher = f"""
        MATCH (
            c:Conversation {{
                id: '{self._escape(conversation_id)}'
            }}
        )

        WHERE c.user_id = '{self._escape(user_id)}'

        OPTIONAL MATCH (
            c
        )-[:HAS_TURN]->(t:ConversationTurn)

        DETACH DELETE t, c

        RETURN count(c) AS deleted_count
        """

        result = self._query(cypher)

        normalized = self._normalize_result(
            result
        )

        deleted_count = 0

        if normalized["records"]:
            deleted_count = (
                normalized["records"][0]
                .get(
                    "deleted_count",
                    0,
                )
                or 0
            )

        return {
            "deleted": int(
                deleted_count
            ) > 0,
            "deleted_count": int(
                deleted_count
            ),
            "conversation_id": conversation_id,
        }