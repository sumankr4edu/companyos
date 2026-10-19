from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from graph.client import graph_client


class AgentCoordinationStore:
    """
    FalkorDB-backed shared state for multi-agent coordination.

    Agent runs, tasks, events, and messages are persisted in FalkorDB.
    """

    def __init__(self, graph_name: str = "novatech"):
        self.graph_name = graph_name

    # ============================================================
    # Helpers
    # ============================================================

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _id(prefix: str) -> str:
        return f"{prefix}_{uuid.uuid4().hex[:12]}"

    @staticmethod
    def _safe_json(value: Any) -> str:
        try:
            return json.dumps(value, default=str)
        except Exception:
            return json.dumps(str(value))

    @staticmethod
    def _decode(value: Any) -> Any:
        if value is None:
            return None

        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception:
                return value

        return value

    @staticmethod
    def _escape(value: Any) -> str:
        return (
            str(value)
            .replace("\\", "\\\\")
            .replace("'", "\\'")
            .replace("\n", "\\n")
            .replace("\r", "\\r")
        )

    @staticmethod
    def _rows(result: Any) -> List[Dict[str, Any]]:
        """
        Normalize FalkorDB query results.

        The important rule here is that all queries in this store
        explicitly RETURN properties rather than RETURN node objects.
        """

        if result is None:
            return []

        # Some wrappers expose rows/header directly.
        if isinstance(result, dict):
            rows = result.get("rows")

            if isinstance(rows, list):
                header = result.get("header", [])

                headers: List[str] = []

                for item in header:
                    text = str(item)

                    if "'" in text:
                        try:
                            headers.append(text.split("'")[1])
                        except Exception:
                            headers.append(text)
                    else:
                        headers.append(text)

                output: List[Dict[str, Any]] = []

                for row in rows:
                    record: Dict[str, Any] = {}

                    for index, value in enumerate(row):
                        key = (
                            headers[index]
                            if index < len(headers)
                            else f"column_{index}"
                        )
                        record[key] = value

                    output.append(record)

                return output

            return [result]

        # FalkorDB QueryResult commonly exposes .result_set.
        result_set = getattr(result, "result_set", None)

        if result_set is not None:
            header = getattr(result, "header", None)

            if header is None:
                header = getattr(result, "columns", None)

            headers: List[str] = []

            if header:
                for item in header:
                    text = str(item)

                    if "'" in text:
                        try:
                            headers.append(text.split("'")[1])
                        except Exception:
                            headers.append(text)
                    else:
                        headers.append(text)

            output: List[Dict[str, Any]] = []

            for row in result_set:
                record: Dict[str, Any] = {}

                for index, value in enumerate(row):
                    key = (
                        headers[index]
                        if index < len(headers)
                        else f"column_{index}"
                    )
                    record[key] = value

                output.append(record)

            return output

        return []

    def _query(self, cypher: str):
        return graph_client.query(
            cypher,
            graph_name=self.graph_name,
        )

    # ============================================================
    # Agent Run
    # ============================================================

    def create_run(
        self,
        user_id: str,
        question: str,
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        run_id = self._id("run")
        now = self._now()

        metadata_json = self._safe_json(metadata or {})

        query = f"""
        CREATE (r:AgentRun {{
            id: '{self._escape(run_id)}',
            user_id: '{self._escape(user_id)}',
            question: '{self._escape(question)}',
            conversation_id: '{self._escape(conversation_id or "")}',
            status: 'created',
            metadata_json: '{self._escape(metadata_json)}',
            error: '',
            created_at: '{self._escape(now)}',
            updated_at: '{self._escape(now)}'
        }})
        RETURN
            r.id AS id,
            r.user_id AS user_id,
            r.question AS question,
            r.conversation_id AS conversation_id,
            r.status AS status,
            r.metadata_json AS metadata_json,
            r.error AS error,
            r.created_at AS created_at,
            r.updated_at AS updated_at
        """

        result = self._query(query)
        rows = self._rows(result)

        # Fail immediately if FalkorDB did not create the run.
        if not rows:
            raise RuntimeError(
                f"FalkorDB did not return the created AgentRun: {run_id}"
            )

        self.add_event(
            run_id=run_id,
            event_type="RUN_CREATED",
            agent="orchestrator",
            payload={
                "question": question,
                "conversation_id": conversation_id,
            },
        )

        return self.get_run(run_id)

    # ============================================================
    # Tasks
    # ============================================================

    def create_task(
        self,
        run_id: str,
        agent: str,
        task_type: str,
        input_data: Optional[Dict[str, Any]] = None,
        depends_on: Optional[str] = None,
    ) -> Dict[str, Any]:

        task_id = self._id("task")
        now = self._now()

        input_json = self._safe_json(input_data or {})

        query = f"""
        MATCH (r:AgentRun {{id: '{self._escape(run_id)}'}})

        CREATE (t:AgentTask {{
            id: '{self._escape(task_id)}',
            run_id: '{self._escape(run_id)}',
            agent: '{self._escape(agent)}',
            task_type: '{self._escape(task_type)}',
            status: 'pending',
            input_json: '{self._escape(input_json)}',
            output_json: '',
            error: '',
            retry_count: 0,
            depends_on: '{self._escape(depends_on or "")}',
            created_at: '{self._escape(now)}',
            updated_at: '{self._escape(now)}'
        }})

        CREATE (r)-[:HAS_TASK]->(t)

        RETURN
            t.id AS id,
            t.run_id AS run_id,
            t.agent AS agent,
            t.task_type AS task_type,
            t.status AS status,
            t.input_json AS input_json,
            t.output_json AS output_json,
            t.error AS error,
            t.retry_count AS retry_count,
            t.depends_on AS depends_on,
            t.created_at AS created_at,
            t.updated_at AS updated_at
        """

        result = self._query(query)
        rows = self._rows(result)

        self.add_event(
            run_id=run_id,
            event_type="TASK_CREATED",
            agent=agent,
            task_id=task_id,
            payload={
                "task_type": task_type,
            },
        )

        if rows:
            return self._normalize_task(rows[0])

        return {
            "id": task_id,
            "run_id": run_id,
            "agent": agent,
            "task_type": task_type,
            "status": "pending",
            "input": input_data or {},
        }

    def update_task(
        self,
        task_id: str,
        status: str,
        output_data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        retry_count: Optional[int] = None,
    ) -> Dict[str, Any]:

        allowed = {
            "pending",
            "running",
            "waiting",
            "completed",
            "failed",
            "cancelled",
        }

        if status not in allowed:
            raise ValueError(f"Invalid task status: {status}")

        now = self._now()

        assignments = [
            f"t.status = '{self._escape(status)}'",
            f"t.updated_at = '{self._escape(now)}'",
        ]

        if output_data is not None:
            output_json = self._safe_json(output_data)

            assignments.append(
                f"t.output_json = '{self._escape(output_json)}'"
            )

        if error is not None:
            assignments.append(
                f"t.error = '{self._escape(error)}'"
            )

        if retry_count is not None:
            assignments.append(
                f"t.retry_count = {int(retry_count)}"
            )

        query = f"""
        MATCH (t:AgentTask {{id: '{self._escape(task_id)}'}})

        SET {", ".join(assignments)}

        RETURN
            t.id AS id,
            t.run_id AS run_id,
            t.agent AS agent,
            t.task_type AS task_type,
            t.status AS status,
            t.input_json AS input_json,
            t.output_json AS output_json,
            t.error AS error,
            t.retry_count AS retry_count,
            t.depends_on AS depends_on,
            t.created_at AS created_at,
            t.updated_at AS updated_at
        """

        result = self._query(query)
        rows = self._rows(result)

        if not rows:
            raise ValueError("Agent task not found")

        task = self._normalize_task(rows[0])

        self.add_event(
            run_id=task["run_id"],
            event_type="TASK_UPDATED",
            agent=task["agent"],
            task_id=task_id,
            payload={
                "status": status,
                "error": error,
            },
        )

        return task

    # ============================================================
    # Agent Messages
    # ============================================================

    def add_message(
        self,
        run_id: str,
        from_agent: str,
        to_agent: str,
        message_type: str,
        payload: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        message_id = self._id("msg")
        now = self._now()

        payload_json = self._safe_json(payload or {})

        query = f"""
        MATCH (r:AgentRun {{id: '{self._escape(run_id)}'}})

        CREATE (m:AgentMessage {{
            id: '{self._escape(message_id)}',
            run_id: '{self._escape(run_id)}',
            from_agent: '{self._escape(from_agent)}',
            to_agent: '{self._escape(to_agent)}',
            message_type: '{self._escape(message_type)}',
            task_id: '{self._escape(task_id or "")}',
            payload_json: '{self._escape(payload_json)}',
            created_at: '{self._escape(now)}'
        }})

        CREATE (r)-[:HAS_MESSAGE]->(m)

        RETURN
            m.id AS id,
            m.run_id AS run_id,
            m.from_agent AS from_agent,
            m.to_agent AS to_agent,
            m.message_type AS message_type,
            m.task_id AS task_id,
            m.payload_json AS payload_json,
            m.created_at AS created_at
        """

        result = self._query(query)
        rows = self._rows(result)

        self.add_event(
            run_id=run_id,
            event_type="AGENT_HANDOFF",
            agent=from_agent,
            task_id=task_id,
            payload={
                "to_agent": to_agent,
                "message_type": message_type,
                "message_id": message_id,
            },
        )

        if rows:
            return self._normalize_message(rows[0])

        return {
            "id": message_id,
            "run_id": run_id,
            "from_agent": from_agent,
            "to_agent": to_agent,
            "message_type": message_type,
            "task_id": task_id,
            "payload": payload or {},
            "created_at": now,
        }

    # ============================================================
    # Events
    # ============================================================

    def add_event(
        self,
        run_id: str,
        event_type: str,
        agent: str,
        payload: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        event_id = self._id("event")
        now = self._now()

        payload_json = self._safe_json(payload or {})

        query = f"""
        MATCH (r:AgentRun {{id: '{self._escape(run_id)}'}})

        CREATE (e:AgentEvent {{
            id: '{self._escape(event_id)}',
            run_id: '{self._escape(run_id)}',
            event_type: '{self._escape(event_type)}',
            from_agent: '{self._escape(agent)}',
            task_id: '{self._escape(task_id or "")}',
            payload_json: '{self._escape(payload_json)}',
            created_at: '{self._escape(now)}'
        }})

        CREATE (r)-[:HAS_EVENT]->(e)

        RETURN
            e.id AS id,
            e.run_id AS run_id,
            e.event_type AS event_type,
            e.from_agent AS from_agent,
            e.task_id AS task_id,
            e.payload_json AS payload_json,
            e.created_at AS created_at
        """

        result = self._query(query)
        rows = self._rows(result)

        if rows:
            return self._normalize_message(rows[0])

        return {
            "id": event_id,
            "run_id": run_id,
            "event_type": event_type,
            "from_agent": agent,
            "task_id": task_id,
            "payload": payload or {},
            "created_at": now,
        }

    # ============================================================
    # Run State
    # ============================================================

    def update_run(
        self,
        run_id: str,
        status: str,
        error: Optional[str] = None,
    ) -> Dict[str, Any]:

        allowed = {
            "created",
            "running",
            "waiting",
            "completed",
            "failed",
            "cancelled",
        }

        if status not in allowed:
            raise ValueError(f"Invalid run status: {status}")

        now = self._now()

        assignments = [
            f"r.status = '{self._escape(status)}'",
            f"r.updated_at = '{self._escape(now)}'",
        ]

        if error is not None:
            assignments.append(
                f"r.error = '{self._escape(error)}'"
            )

        query = f"""
        MATCH (r:AgentRun {{id: '{self._escape(run_id)}'}})

        SET {", ".join(assignments)}

        RETURN
            r.id AS id,
            r.user_id AS user_id,
            r.question AS question,
            r.conversation_id AS conversation_id,
            r.status AS status,
            r.metadata_json AS metadata_json,
            r.error AS error,
            r.created_at AS created_at,
            r.updated_at AS updated_at
        """

        result = self._query(query)
        rows = self._rows(result)

        if not rows:
            raise ValueError("Agent run not found")

        run = self._normalize_run(rows[0])

        self.add_event(
            run_id=run_id,
            event_type="RUN_STATUS_CHANGED",
            agent="orchestrator",
            payload={
                "status": status,
                "error": error,
            },
        )

        return run

    # ============================================================
    # Run Queries
    # ============================================================

    def get_run(
        self,
        run_id: str,
    ) -> Dict[str, Any]:

        query = f"""
        MATCH (r:AgentRun {{id: '{self._escape(run_id)}'}})

        RETURN
            r.id AS id,
            r.user_id AS user_id,
            r.question AS question,
            r.conversation_id AS conversation_id,
            r.status AS status,
            r.metadata_json AS metadata_json,
            r.error AS error,
            r.created_at AS created_at,
            r.updated_at AS updated_at
        """

        result = self._query(query)
        rows = self._rows(result)

        if not rows:
            raise ValueError(
                f"Agent run not found: {run_id}"
            )

        return self._normalize_run(rows[0])

    def list_runs(
        self,
        user_id: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:

        limit = max(1, min(int(limit), 100))

        where = ""

        if user_id:
            where = (
                f"WHERE r.user_id = '{self._escape(user_id)}'"
            )

        query = f"""
        MATCH (r:AgentRun)
        {where}

        RETURN
            r.id AS id,
            r.user_id AS user_id,
            r.question AS question,
            r.conversation_id AS conversation_id,
            r.status AS status,
            r.metadata_json AS metadata_json,
            r.error AS error,
            r.created_at AS created_at,
            r.updated_at AS updated_at

        ORDER BY r.created_at DESC
        LIMIT {limit}
        """

        return [
            self._normalize_run(row)
            for row in self._rows(self._query(query))
        ]

    # ============================================================
    # Task Queries
    # ============================================================

    def get_run_tasks(
        self,
        run_id: str,
    ) -> List[Dict[str, Any]]:

        query = f"""
        MATCH (r:AgentRun {{id: '{self._escape(run_id)}'}})
              -[:HAS_TASK]->
              (t:AgentTask)

        RETURN
            t.id AS id,
            t.run_id AS run_id,
            t.agent AS agent,
            t.task_type AS task_type,
            t.status AS status,
            t.input_json AS input_json,
            t.output_json AS output_json,
            t.error AS error,
            t.retry_count AS retry_count,
            t.depends_on AS depends_on,
            t.created_at AS created_at,
            t.updated_at AS updated_at

        ORDER BY t.created_at ASC
        """

        return [
            self._normalize_task(row)
            for row in self._rows(self._query(query))
        ]

    def get_run_events(
        self,
        run_id: str,
    ) -> List[Dict[str, Any]]:

        query = f"""
        MATCH (r:AgentRun {{id: '{self._escape(run_id)}'}})
              -[:HAS_EVENT]->
              (e:AgentEvent)

        RETURN
            e.id AS id,
            e.run_id AS run_id,
            e.event_type AS event_type,
            e.from_agent AS from_agent,
            e.task_id AS task_id,
            e.payload_json AS payload_json,
            e.created_at AS created_at

        ORDER BY e.created_at ASC
        """

        return [
            self._normalize_message(row)
            for row in self._rows(self._query(query))
        ]

    def get_pending_tasks(
        self,
        run_id: str,
    ) -> List[Dict[str, Any]]:

        query = f"""
        MATCH (r:AgentRun {{id: '{self._escape(run_id)}'}})
              -[:HAS_TASK]->
              (t:AgentTask)

        WHERE t.status IN ['pending', 'failed']

        RETURN
            t.id AS id,
            t.run_id AS run_id,
            t.agent AS agent,
            t.task_type AS task_type,
            t.status AS status,
            t.input_json AS input_json,
            t.output_json AS output_json,
            t.error AS error,
            t.retry_count AS retry_count,
            t.depends_on AS depends_on,
            t.created_at AS created_at,
            t.updated_at AS updated_at

        ORDER BY t.created_at ASC
        """

        return [
            self._normalize_task(row)
            for row in self._rows(self._query(query))
        ]

    # ============================================================
    # Resume
    # ============================================================

    def resume_run(
        self,
        run_id: str,
    ) -> Dict[str, Any]:

        run = self.get_run(run_id)

        if run["status"] not in {
            "failed",
            "waiting",
        }:
            return run

        pending = self.get_pending_tasks(run_id)

        self.update_run(
            run_id,
            "running",
        )

        self.add_event(
            run_id=run_id,
            event_type="RUN_RESUMED",
            agent="orchestrator",
            payload={
                "pending_tasks": len(pending),
            },
        )

        return self.get_run(run_id)

    # ============================================================
    # Normalization
    # ============================================================

    def _normalize_run(
        self,
        row: Dict[str, Any],
    ) -> Dict[str, Any]:

        return {
            "id": row.get("id"),
            "user_id": row.get("user_id"),
            "question": row.get("question"),
            "conversation_id": row.get("conversation_id"),
            "status": row.get("status"),
            "metadata": self._decode(
                row.get("metadata_json", "{}")
            ),
            "error": row.get("error"),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        }

    def _normalize_task(
        self,
        row: Dict[str, Any],
    ) -> Dict[str, Any]:

        return {
            "id": row.get("id"),
            "run_id": row.get("run_id"),
            "agent": row.get("agent"),
            "task_type": row.get("task_type"),
            "status": row.get("status"),
            "input": self._decode(
                row.get("input_json", "{}")
            ),
            "output": self._decode(
                row.get("output_json", "{}")
            ),
            "error": row.get("error"),
            "retry_count": row.get("retry_count", 0),
            "depends_on": row.get("depends_on"),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        }

    def _normalize_message(
        self,
        row: Dict[str, Any],
    ) -> Dict[str, Any]:

        return {
            "id": row.get("id"),
            "run_id": row.get("run_id"),
            "event_type": row.get("event_type"),
            "from_agent": row.get("from_agent"),
            "to_agent": row.get("to_agent"),
            "message_type": row.get("message_type"),
            "task_id": row.get("task_id"),
            "payload": self._decode(
                row.get("payload_json", "{}")
            ),
            "created_at": row.get("created_at"),
        }


__all__ = ["AgentCoordinationStore"]