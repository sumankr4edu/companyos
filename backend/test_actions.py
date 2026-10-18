from graph.queries import run_cypher
import json

query = """
MATCH (t:Task)-[:ASSIGNED_TO]->(p:Person)
RETURN t.id, t.title, p.name
"""

result = run_cypher(query)

print(json.dumps(result, indent=2))