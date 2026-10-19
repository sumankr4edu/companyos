# from datetime import datetime, timezone
# from typing import Any, Dict, Optional
# import uuid

# from graph.queries import run_cypher


# class ActionAgent:
#     """
#     Controlled action layer for CompanyOS.

#     IMPORTANT:
#     This agent does NOT expose arbitrary Cypher writes to the LLM.
#     Actions are converted into predefined graph mutations.
#     """

#     ALLOWED_ACTIONS = {
#         "create_investigation_task",
#         "assign_task",
#         "complete_task",
#         "add_discovery",
#     }

#     def __init__(self, graph_name: str = "novatech"):
#         self.graph_name = graph_name

#     def execute(
#         self,
#         action_type: str,
#         actor: str,
#         payload: Dict[str, Any],
#     ) -> Dict[str, Any]:

#         if action_type not in self.ALLOWED_ACTIONS:
#             raise ValueError(
#                 f"Unsupported action type: {action_type}"
#             )

#         if not actor:
#             raise ValueError("Actor is required.")

#         if not isinstance(payload, dict):
#             raise ValueError("Action payload must be an object.")

#         if action_type == "create_investigation_task":
#             return self._create_investigation_task(
#                 actor,
#                 payload,
#             )

#         if action_type == "assign_task":
#             return self._assign_task(
#                 actor,
#                 payload,
#             )

#         if action_type == "complete_task":
#             return self._complete_task(
#                 actor,
#                 payload,
#             )

#         if action_type == "add_discovery":
#             return self._add_discovery(
#                 actor,
#                 payload,
#             )

#         raise ValueError(
#             f"Action handler not implemented: {action_type}"
#         )

#     # ------------------------------------------------------------------
#     # CREATE INVESTIGATION TASK
#     # ------------------------------------------------------------------

#     def _create_investigation_task(
#         self,
#         actor: str,
#         payload: Dict[str, Any],
#     ) -> Dict[str, Any]:

#         title = self._required(payload, "title")
#         assignee = self._required(payload, "assignee")
#         target = self._required(payload, "target")

#         description = payload.get(
#             "description",
#             "Investigate the affected system and determine root cause.",
#         )

#         task_id = f"TASK-{uuid.uuid4().hex[:10].upper()}"
#         created_at = self._now()

#         title = self._escape(title)
#         assignee = self._escape(assignee)
#         target = self._escape(target)
#         description = self._escape(description)
#         actor = self._escape(actor)

#         query = f"""
#         MATCH (person:Person {{name: '{assignee}'}})
#         MATCH (target {{name: '{target}'}})

#         CREATE (task:Task {{
#             id: '{task_id}',
#             title: '{title}',
#             description: '{description}',
#             status: 'OPEN',
#             priority: 'HIGH',
#             created_at: '{created_at}',
#             updated_at: '{created_at}',
#             created_by: '{actor}'
#         }})

#         CREATE (task)-[:ASSIGNED_TO]->(person)
#         CREATE (task)-[:TARGETS]->(target)

#         RETURN
#             task.id AS task_id,
#             task.title AS title,
#             task.status AS status,
#             person.name AS assignee,
#             target.name AS target,
#             task.created_at AS created_at
#         """

#         result = run_cypher(
#             query,
#             self.graph_name,
#         )

#         audit = self._write_audit_event(
#             actor=actor,
#             action_type="create_investigation_task",
#             target=target,
#             action_id=task_id,
#             payload={
#                 "title": title,
#                 "assignee": assignee,
#                 "target": target,
#             },
#             result="SUCCESS",
#         )

#         return {
#             "success": True,
#             "action_type": "create_investigation_task",
#             "task_id": task_id,
#             "result": result,
#             "audit": audit,
#         }

#     # ------------------------------------------------------------------
#     # ASSIGN TASK
#     # ------------------------------------------------------------------

#     def _assign_task(
#         self,
#         actor: str,
#         payload: Dict[str, Any],
#     ) -> Dict[str, Any]:

#         task_id = self._required(payload, "task_id")
#         assignee = self._required(payload, "assignee")

#         actor = self._escape(actor)
#         task_id = self._escape(task_id)
#         assignee = self._escape(assignee)

#         query = f"""
#         MATCH (task:Task {{id: '{task_id}'}})
#         MATCH (person:Person {{name: '{assignee}'}})

#         OPTIONAL MATCH (task)-[old:ASSIGNED_TO]->(:Person)
#         DELETE old

#         CREATE (task)-[:ASSIGNED_TO]->(person)

#         SET task.updated_at = '{self._now()}'

#         RETURN
#             task.id AS task_id,
#             person.name AS assignee,
#             task.updated_at AS updated_at
#         """

#         result = run_cypher(
#             query,
#             self.graph_name,
#         )

#         audit = self._write_audit_event(
#             actor=actor,
#             action_type="assign_task",
#             target=task_id,
#             action_id=task_id,
#             payload={
#                 "assignee": assignee,
#             },
#             result="SUCCESS",
#         )

#         return {
#             "success": True,
#             "action_type": "assign_task",
#             "task_id": task_id,
#             "result": result,
#             "audit": audit,
#         }

#     # ------------------------------------------------------------------
#     # COMPLETE TASK
#     # ------------------------------------------------------------------

#     def _complete_task(
#         self,
#         actor: str,
#         payload: Dict[str, Any],
#     ) -> Dict[str, Any]:

#         task_id = self._required(payload, "task_id")
#         result_text = payload.get(
#             "result",
#             "Investigation completed.",
#         )

#         task_id = self._escape(task_id)
#         result_text = self._escape(result_text)
#         actor = self._escape(actor)
#         completed_at = self._now()

#         query = f"""
#         MATCH (task:Task {{id: '{task_id}'}})

#         SET
#             task.status = 'COMPLETED',
#             task.result = '{result_text}',
#             task.completed_at = '{completed_at}',
#             task.updated_at = '{completed_at}'

#         RETURN
#             task.id AS task_id,
#             task.status AS status,
#             task.result AS result,
#             task.completed_at AS completed_at
#         """

#         result = run_cypher(
#             query,
#             self.graph_name,
#         )

#         audit = self._write_audit_event(
#             actor=actor,
#             action_type="complete_task",
#             target=task_id,
#             action_id=task_id,
#             payload={
#                 "result": result_text,
#             },
#             result="SUCCESS",
#         )

#         return {
#             "success": True,
#             "action_type": "complete_task",
#             "task_id": task_id,
#             "result": result,
#             "audit": audit,
#         }

#     # ------------------------------------------------------------------
#     # ADD DISCOVERY
#     # ------------------------------------------------------------------

#     def _add_discovery(
#         self,
#         actor: str,
#         payload: Dict[str, Any],
#     ) -> Dict[str, Any]:

#         task_id = self._required(payload, "task_id")
#         discovery = self._required(payload, "discovery")

#         discovery_id = f"DISC-{uuid.uuid4().hex[:10].upper()}"
#         created_at = self._now()

#         task_id = self._escape(task_id)
#         discovery = self._escape(discovery)
#         actor = self._escape(actor)

#         query = f"""
#         MATCH (task:Task {{id: '{task_id}'}})

#         CREATE (d:Discovery {{
#             id: '{discovery_id}',
#             content: '{discovery}',
#             created_at: '{created_at}',
#             created_by: '{actor}'
#         }})

#         CREATE (task)-[:RESULTED_IN]->(d)

#         RETURN
#             d.id AS discovery_id,
#             d.content AS discovery,
#             d.created_at AS created_at,
#             task.id AS task_id
#         """

#         result = run_cypher(
#             query,
#             self.graph_name,
#         )

#         audit = self._write_audit_event(
#             actor=actor,
#             action_type="add_discovery",
#             target=task_id,
#             action_id=discovery_id,
#             payload={
#                 "discovery": discovery,
#             },
#             result="SUCCESS",
#         )

#         return {
#             "success": True,
#             "action_type": "add_discovery",
#             "discovery_id": discovery_id,
#             "result": result,
#             "audit": audit,
#         }

#     # ------------------------------------------------------------------
#     # AUDIT TRAIL
#     # ------------------------------------------------------------------

#     def _write_audit_event(
#         self,
#         actor: str,
#         action_type: str,
#         target: str,
#         action_id: str,
#         payload: Dict[str, Any],
#         result: str,
#     ) -> Dict[str, Any]:

#         audit_id = f"AUDIT-{uuid.uuid4().hex[:10].upper()}"
#         created_at = self._now()

#         actor = self._escape(actor)
#         action_type = self._escape(action_type)
#         target = self._escape(target)
#         action_id = self._escape(action_id)
#         result = self._escape(result)

#         query = f"""
#         CREATE (audit:AuditEvent {{
#             id: '{audit_id}',
#             action_type: '{action_type}',
#             actor: '{actor}',
#             target: '{target}',
#             action_id: '{action_id}',
#             result: '{result}',
#             created_at: '{created_at}'
#         }})

#         RETURN
#             audit.id AS audit_id,
#             audit.action_type AS action_type,
#             audit.actor AS actor,
#             audit.target AS target,
#             audit.result AS result,
#             audit.created_at AS created_at
#         """

#         return run_cypher(
#             query,
#             self.graph_name,
#         )

#     # ------------------------------------------------------------------
#     # HELPERS
#     # ------------------------------------------------------------------

#     @staticmethod
#     def _required(
#         payload: Dict[str, Any],
#         key: str,
#     ) -> str:

#         value = payload.get(key)

#         if value is None:
#             raise ValueError(
#                 f"Missing required field: {key}"
#             )

#         value = str(value).strip()

#         if not value:
#             raise ValueError(
#                 f"Field cannot be empty: {key}"
#             )

#         return value

#     @staticmethod
#     def _escape(value: str) -> str:
#         return (
#             str(value)
#             .replace("\\", "\\\\")
#             .replace("'", "\\'")
#             .replace("\n", " ")
#             .replace("\r", " ")
#         )

#     @staticmethod
#     def _now() -> str:
#         return datetime.now(
#             timezone.utc
#         ).isoformat()

from __future__ import annotations

from typing import Any, Dict, Optional

from actions.investigation_tasks import InvestigationTaskManager


class ActionAgent:
    """
    Performs controlled, auditable company actions.

    The action layer intentionally uses explicit operations rather
    than allowing the LLM to execute arbitrary Cypher.
    """

    ALLOWED_ACTIONS = {
        "create_investigation",
        "update_investigation_status",
        "assign_investigation",
    }

    def __init__(self, graph_name: str = "novatech"):
        self.graph_name = graph_name
        self.manager = InvestigationTaskManager(
            graph_name=graph_name
        )

    def execute(
        self,
        action: str,
        actor_id: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:

        if action not in self.ALLOWED_ACTIONS:
            return {
                "success": False,
                "error": f"Unsupported action: {action}",
            }

        if action == "create_investigation":

            return self.manager.create_task(
                title=payload["title"],
                description=payload["description"],
                actor_id=actor_id,
                service_name=payload.get(
                    "service_name"
                ),
                incident_title=payload.get(
                    "incident_title"
                ),
                assignee_name=payload.get(
                    "assignee_name"
                ),
                priority=payload.get(
                    "priority",
                    "medium",
                ),
            )

        if action == "update_investigation_status":

            return self.manager.update_status(
                task_id=payload["task_id"],
                status=payload["status"],
                actor_id=actor_id,
            )

        if action == "assign_investigation":

            return self.manager.assign_task(
                task_id=payload["task_id"],
                assignee_name=payload["assignee_name"],
                actor_id=actor_id,
            )

        return {
            "success": False,
            "error": "Action execution failed.",
        }