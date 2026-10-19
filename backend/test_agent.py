from graph.client import graph_client
result = graph_client.query("""
MATCH (r:AgentRun)
OPTIONAL MATCH (r)-[rel]->(child)
RETURN
    r.id AS run_id,
    type(rel) AS relationship,
    labels(child) AS child_labels,
    child.id AS child_id
ORDER BY r.created_at DESC
LIMIT 50
""", graph_name="novatech")

print(result)