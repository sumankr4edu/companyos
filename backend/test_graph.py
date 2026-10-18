from graph.queries import run_cypher
import json

query = """
MATCH (t:Task)-[:RESULTED_IN]->(d:Discovery)
RETURN t.id, d.id, d.content
"""

result = run_cypher(query)

print(json.dumps(result, indent=2))