from graph.queries import run_cypher


queries = {
    "People": "MATCH (n:Person) RETURN count(n) AS count",
    "Teams": "MATCH (n:Team) RETURN count(n) AS count",
    "Projects": "MATCH (n:Project) RETURN count(n) AS count",
    "Services": "MATCH (n:Service) RETURN count(n) AS count",
    "Documents": "MATCH (n:Document) RETURN count(n) AS count",
    "Incidents": "MATCH (n:Incident) RETURN count(n) AS count",
    "Decisions": "MATCH (n:Decision) RETURN count(n) AS count",
    "Relationships": "MATCH ()-[r]->() RETURN count(r) AS count",
}


for name, query in queries.items():
    result = run_cypher(query)

    print(f"\n{name}")
    print(result)