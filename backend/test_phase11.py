from graph.queries import run_cypher
import json


queries = {
    "TASKS": """
        MATCH (t:Task)
        RETURN t.id, t.title, t.status, t.priority
    """,

    "ASSIGNMENTS": """
        MATCH (t:Task)-[:ASSIGNED_TO]->(p:Person)
        RETURN t.id, t.title, p.name
    """,

    "AUDIT EVENTS": """
        MATCH (a:AuditEvent)
        RETURN a.id, a.action_type, a.actor, a.target, a.result, a.created_at
        ORDER BY a.created_at DESC
        LIMIT 10
    """,

    "DISCOVERIES": """
        MATCH (t:Task)-[:RESULTED_IN]->(d:Discovery)
        RETURN t.id, d.id, d.content
    """
}


for name, query in queries.items():
    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)

    try:
        result = run_cypher(query)
        print(json.dumps(result, indent=2))
    except Exception as exc:
        print("ERROR:", exc)