from typing import Any, Dict, Optional

from agents.coordination import AgentCoordinationStore


class AgentHandoff:
    """
    Persistent agent-to-agent communication.

    Every handoff is written to FalkorDB.
    """

    def __init__(self, graph_name: str = "novatech"):
        self.store = AgentCoordinationStore(graph_name)

    def handoff(
        self,
        run_id: str,
        from_agent: str,
        to_agent: str,
        message_type: str,
        payload: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None,
    ):
        return self.store.add_message(
            run_id=run_id,
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            payload=payload or {},
            task_id=task_id,
        )

    def graph_to_memory(
        self,
        run_id: str,
        payload: Dict[str, Any],
        task_id: Optional[str] = None,
    ):
        return self.handoff(
            run_id=run_id,
            from_agent="graph_agent",
            to_agent="memory_agent",
            message_type="GRAPH_CONTEXT",
            payload=payload,
            task_id=task_id,
        )

    def memory_to_analysis(
        self,
        run_id: str,
        payload: Dict[str, Any],
        task_id: Optional[str] = None,
    ):
        return self.handoff(
            run_id=run_id,
            from_agent="memory_agent",
            to_agent="analysis_agent",
            message_type="MEMORY_CONTEXT",
            payload=payload,
            task_id=task_id,
        )

    def analysis_to_action(
        self,
        run_id: str,
        payload: Dict[str, Any],
        task_id: Optional[str] = None,
    ):
        return self.handoff(
            run_id=run_id,
            from_agent="analysis_agent",
            to_agent="action_agent",
            message_type="ACTION_RECOMMENDATION",
            payload=payload,
            task_id=task_id,
        )