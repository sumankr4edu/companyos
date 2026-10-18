from fastapi import APIRouter, HTTPException

from graph.queries import run_cypher


router = APIRouter(
    prefix="/api/actions",
    tags=["action-history"],
)


@router.get("/history")
def action_history(limit: int = 50):

    limit = max(1, min(limit, 200))

    query = f"""
    MATCH (a:AuditEvent)
    RETURN
        a.id AS id,
        a.action_type AS action_type,
        a.actor AS actor,
        a.target AS target,
        a.action_id AS action_id,
        a.result AS result,
        a.created_at AS created_at
    ORDER BY a.created_at DESC
    LIMIT {limit}
    """

    return run_cypher(query)


@router.get("/task/{task_id}")
def task_history(task_id: str):

    escaped = (
        task_id
        .replace("\\", "\\\\")
        .replace("'", "\\'")
    )

    query = f"""
    MATCH (t:Task {{id: '{escaped}'}})
    OPTIONAL MATCH (t)-[:ASSIGNED_TO]->(p:Person)
    OPTIONAL MATCH (t)-[:TARGETS]->(target)
    OPTIONAL MATCH (t)-[:RESULTED_IN]->(d:Discovery)

    RETURN
        t.id AS task_id,
        t.title AS title,
        t.description AS description,
        t.status AS status,
        t.priority AS priority,
        t.created_at AS created_at,
        t.updated_at AS updated_at,
        t.completed_at AS completed_at,
        t.result AS result,
        p.name AS assignee,
        target.name AS target,
        collect(d.content) AS discoveries
    """

    return run_cypher(query)