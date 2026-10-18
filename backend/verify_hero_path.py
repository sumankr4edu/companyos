# from graph.queries import run_cypher


# query = """
# MATCH p =
#     (checkout:Service {name: 'Checkout Service'})
#     -[*1..8]-
#     (owner:Person {name: 'Maya Singh'})
# RETURN p
# LIMIT 5
# """


# result = run_cypher(query)

# print("HERO GRAPH PATH")
# print(result)
from graph.queries import run_cypher


query = """
MATCH
    (checkout:Service {name: 'Checkout Service'}),
    (payment:Service {name: 'Payment Service'}),
    (incident:Incident),
    (migration:Project {name: 'Payment Service Migration'}),
    (decision:Decision),
    (alice:Person {name: 'Alice Chen'}),
    (maya:Person {name: 'Maya Singh'})

WHERE incident.title = 'Checkout failures increased'
  AND decision.title = 'Move payment processing to dedicated Payment Service'

RETURN
    checkout.name AS affected_service,
    payment.name AS dependency,
    incident.title AS incident,
    migration.name AS migration,
    decision.title AS decision,
    alice.name AS decision_maker,
    maya.name AS current_owner
LIMIT 5
"""


result = run_cypher(query)

print("\n=== NOVATECH HERO EVIDENCE ===")

for row in result["rows"]:
    print()
    for header, value in zip(result["header"], row):
        print(f"{header}: {value}")