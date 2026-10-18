from graph.queries import run_cypher
import json

query = """
MATCH (a:AuditEvent)
RETURN
    a.id,
    a.action_type,
    a.actor,
    a.target,
    a.result,
    a.created_at
ORDER BY a.created_at DESC
LIMIT 10
"""

result = run_cypher(query)

print(json.dumps(result, indent=2))