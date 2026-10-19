from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from graph.client import graph_client


class InvestigationTaskManager:
    """
    Graph-native investigation task manager.

    All durable task state is stored in FalkorDB.
    """

    def __init__(self, graph_name: str = "novatech"):
        self.graph_name = graph_name

    @staticmethod
    def _escape(value: Any) -> str:
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

    def create_task(
        self,
        title: str,
        description: str,
        actor_id: str,
        service_name: Optional[str] = None,
        incident_title: Optional[str] = None,
        assignee_name: Optional[str] = None,
        priority: str = "medium",
    ) -> Dict[str, Any]:

        task_id = f"task_{uuid.uuid4().hex}"
        action_id = f"action_{uuid.uuid4().hex}"
        now = self._now()

        task_id_e = self._escape(task_id)
        action_id_e = self._escape(action_id)
        title_e = self._escape(title)
        description_e = self._escape(description)
        actor_e = self._escape(actor_id)
        priority_e = self._escape(priority)
        service_e = self._escape(service_name)
        incident_e = self._escape(incident_title)
        assignee_e = self._escape(assignee_name)
        now_e = self._escape(now)

        cypher = f"""
        CREATE (t:InvestigationTask {{
            id: '{task_id_e}',
            title: '{title_e}',
            description: '{description_e}',
            status: 'open',
            priority: '{priority_e}',
            created_by: '{actor_e}',
            created_at: '{now_e}',
            updated_at: '{now_e}'
        }})

        CREATE (a:ActionAudit {{
            id: '{action_id_e}',
            action_type: 'CREATE_INVESTIGATION',
            actor_id: '{actor_e}',
            target_id: '{task_id_e}',
            created_at: '{now_e}',
            status: 'completed'
        }})

        CREATE (t)-[:HAS_ACTION]->(a)
        """

        if assignee_name:
            cypher += f"""
            WITH t, a
            OPTIONAL MATCH (p:Person {{name: '{assignee_e}'}})
            FOREACH (person IN CASE
                WHEN p IS NULL THEN []
                ELSE [p]
            END |
                CREATE (t)-[:ASSIGNED_TO]->(person)
            )
            """

        if service_name:
            cypher += f"""
            WITH t, a
            OPTIONAL MATCH (s:Service {{name: '{service_e}'}})
            FOREACH (service IN CASE
                WHEN s IS NULL THEN []
                ELSE [s]
            END |
                CREATE (t)-[:RELATED_TO]->(service)
            )
            """

        if incident_title:
            cypher += f"""
            WITH t, a
            OPTIONAL MATCH (i:Incident {{title: '{incident_e}'}})
            FOREACH (incident IN CASE
                WHEN i IS NULL THEN []
                ELSE [i]
            END |
                CREATE (t)-[:TRIGGERED_BY]->(incident)
            )
            """

        cypher += """
        WITH t, a
        RETURN
            t,
            a
        """

        result = self._query(cypher)

        return {
            "success": True,
            "task_id": task_id,
            "action_id": action_id,
            "status": "open",
            "raw": result,
        }

    def list_tasks(
        self,
        actor_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> Dict[str, Any]:

        limit = max(1, min(int(limit), 100))

        conditions = []

        if actor_id:
            conditions.append(
                f"t.created_by = '{self._escape(actor_id)}'"
            )

        if status:
            conditions.append(
                f"t.status = '{self._escape(status)}'"
            )

        where_clause = ""

        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        cypher = f"""
        MATCH (t:InvestigationTask)
        {where_clause}

        OPTIONAL MATCH (t)-[:ASSIGNED_TO]->(p:Person)
        OPTIONAL MATCH (t)-[:RELATED_TO]->(s:Service)
        OPTIONAL MATCH (t)-[:TRIGGERED_BY]->(i:Incident)

        RETURN
            t.id AS task_id,
            t.title AS title,
            t.description AS description,
            t.status AS status,
            t.priority AS priority,
            t.created_by AS created_by,
            t.created_at AS created_at,
            t.updated_at AS updated_at,
            p.name AS assignee,
            s.name AS service,
            i.title AS incident

        ORDER BY t.created_at DESC
        LIMIT {limit}
        """

        result = self._query(cypher)

        return {
            "success": True,
            "tasks": self._normalize(result),
        }

    def get_task(
        self,
        task_id: str,
    ) -> Dict[str, Any]:

        task_id = self._escape(task_id)

        cypher = f"""
        MATCH (t:InvestigationTask {{id: '{task_id}'}})

        OPTIONAL MATCH (t)-[:ASSIGNED_TO]->(p:Person)
        OPTIONAL MATCH (t)-[:RELATED_TO]->(s:Service)
        OPTIONAL MATCH (t)-[:TRIGGERED_BY]->(i:Incident)
        OPTIONAL MATCH (t)-[:HAS_ACTION]->(a:ActionAudit)

        RETURN
            t.id AS task_id,
            t.title AS title,
            t.description AS description,
            t.status AS status,
            t.priority AS priority,
            t.created_by AS created_by,
            t.created_at AS created_at,
            t.updated_at AS updated_at,
            p.name AS assignee,
            s.name AS service,
            i.title AS incident,
            collect(a) AS actions
        """

        result = self._query(cypher)

        return {
            "success": True,
            "task_id": task_id,
            "raw": result,
        }

    def update_status(
        self,
        task_id: str,
        status: str,
        actor_id: str,
    ) -> Dict[str, Any]:

        allowed_statuses = {
            "open",
            "in_progress",
            "blocked",
            "resolved",
            "cancelled",
        }

        if status not in allowed_statuses:
            raise ValueError(
                f"Invalid task status: {status}"
            )

        task_id_e = self._escape(task_id)
        status_e = self._escape(status)
        actor_e = self._escape(actor_id)

        action_id = f"action_{uuid.uuid4().hex}"
        action_id_e = self._escape(action_id)

        now = self._escape(self._now())

        cypher = f"""
        MATCH (t:InvestigationTask {{id: '{task_id_e}'}})

        SET
            t.status = '{status_e}',
            t.updated_at = '{now}'

        CREATE (a:ActionAudit {{
            id: '{action_id_e}',
            action_type: 'UPDATE_INVESTIGATION_STATUS',
            actor_id: '{actor_e}',
            target_id: '{task_id_e}',
            status: 'completed',
            created_at: '{now}',
            new_status: '{status_e}'
        }})

        CREATE (t)-[:HAS_ACTION]->(a)

        RETURN
            t.id AS task_id,
            t.status AS status,
            t.updated_at AS updated_at
        """

        result = self._query(cypher)

        return {
            "success": True,
            "task_id": task_id,
            "status": status,
            "action_id": action_id,
            "raw": result,
        }

    def assign_task(
        self,
        task_id: str,
        assignee_name: str,
        actor_id: str,
    ) -> Dict[str, Any]:

        task_id_e = self._escape(task_id)
        assignee_e = self._escape(assignee_name)
        actor_e = self._escape(actor_id)

        action_id = f"action_{uuid.uuid4().hex}"
        now = self._escape(self._now())

        cypher = f"""
        MATCH (t:InvestigationTask {{id: '{task_id_e}'}})
        MATCH (p:Person {{name: '{assignee_e}'}})

        OPTIONAL MATCH (t)-[old:ASSIGNED_TO]->(:Person)
        DELETE old

        CREATE (t)-[:ASSIGNED_TO]->(p)

        SET
            t.updated_at = '{now}',
            t.assignee = '{assignee_e}'

        CREATE (a:ActionAudit {{
            id: '{self._escape(action_id)}',
            action_type: 'ASSIGN_INVESTIGATION',
            actor_id: '{actor_e}',
            target_id: '{task_id_e}',
            target_person: '{assignee_e}',
            status: 'completed',
            created_at: '{now}'
        }})

        CREATE (t)-[:HAS_ACTION]->(a)

        RETURN
            t.id AS task_id,
            p.name AS assignee,
            t.updated_at AS updated_at
        """

        result = self._query(cypher)

        return {
            "success": True,
            "task_id": task_id,
            "assignee": assignee_name,
            "action_id": action_id,
            "raw": result,
        }

    def action_history(
        self,
        task_id: Optional[str] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:

        limit = max(1, min(int(limit), 200))

        if task_id:
            match = (
                f"MATCH (t:InvestigationTask "
                f"{{id: '{self._escape(task_id)}'}})"
                f"-[:HAS_ACTION]->(a:ActionAudit)"
            )
        else:
            match = (
                "MATCH (t:InvestigationTask)"
                "-[:HAS_ACTION]->(a:ActionAudit)"
            )

        cypher = f"""
        {match}

        RETURN
            t.id AS task_id,
            t.title AS task_title,
            a.id AS action_id,
            a.action_type AS action_type,
            a.actor_id AS actor_id,
            a.target_id AS target_id,
            a.target_person AS target_person,
            a.new_status AS new_status,
            a.status AS status,
            a.created_at AS created_at

        ORDER BY a.created_at DESC
        LIMIT {limit}
        """

        result = self._query(cypher)

        return {
            "success": True,
            "actions": self._normalize(result),
        }

    @staticmethod
    def _normalize(result):

        if result is None:
            return []

        rows = getattr(
            result,
            "result_set",
            None,
        )

        if rows is None:
            rows = getattr(
                result,
                "rows",
                None,
            )

        if not rows:
            return []

        headers = getattr(
            result,
            "header",
            None,
        )

        if headers is None:
            headers = getattr(
                result,
                "headers",
                None,
            )

        names = []

        if headers:
            for header in headers:
                if isinstance(header, (list, tuple)):
                    names.append(str(header[-1]))
                else:
                    names.append(str(header))

        output = []

        for row in rows:

            if isinstance(row, dict):
                output.append(dict(row))
                continue

            if not isinstance(row, (list, tuple)):
                continue

            item = {}

            for index, value in enumerate(row):
                key = (
                    names[index]
                    if index < len(names)
                    else f"column_{index}"
                )

                if hasattr(value, "properties"):
                    try:
                        item[key] = dict(value.properties)
                        continue
                    except Exception:
                        pass

                item[key] = value

            output.append(item)

        return output