from graph.client import graph_client

result = graph_client.query("""
MATCH (r:AgentRun)-[:HAS_TASK]->(t:AgentTask)
RETURN
    r.id AS run_id,
    r.status AS run_status,
    t.id AS task_id,
    t.agent AS agent,
    t.task_type AS task_type,
    t.status AS task_status
ORDER BY r.created_at DESC
LIMIT 20
""", graph_name="novatech")

print(result)