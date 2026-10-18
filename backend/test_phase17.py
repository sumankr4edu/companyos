from graph.path_engine import GraphPathEngine
from agents.explainability_agent import ExplainabilityAgent


print()
print("=" * 70)
print("COMPANYOS — PHASE 17 TEST")
print("=" * 70)


engine = GraphPathEngine(
    graph_name="novatech"
)

explainability = ExplainabilityAgent()


# =========================================================
# TEST 1
# =========================================================

print()
print("=" * 70)
print("TEST 1 — HERO PATH")
print("=" * 70)

hero_result = engine.hero_path(
    source="Checkout Service",
    max_hops=8,
)

print(hero_result)


hero_paths = engine.normalize_path(
    hero_result
)

print()
print("NORMALIZED PATH:")
print(hero_paths)


# =========================================================
# TEST 2
# =========================================================

print()
print("=" * 70)
print("TEST 2 — PAYMENT SERVICE")
print("=" * 70)

payment_result = engine.explore(
    entity_name="Payment Service",
    max_hops=4,
    limit=20,
)

print(payment_result)


# =========================================================
# TEST 3
# =========================================================

print()
print("=" * 70)
print("TEST 3 — EXPLAINABILITY")
print("=" * 70)

evidence = [
    {
        "service": "Payment Service",
        "relationship": "DEPENDS_ON",
        "dependency": "Payment Database",
        "source_type": "synthetic_company_data",
    },
    {
        "service": "Checkout Service",
        "relationship": "DEPENDS_ON",
        "dependency": "Payment Service",
        "source_type": "synthetic_company_data",
    },
]


explanation = explainability.build(
    evidence=evidence,
    graph_path=hero_paths,
    contradictions=[],
)

print(explanation)


# =========================================================
# DONE
# =========================================================

print()
print("=" * 70)
print("PHASE 17 TEST COMPLETE")
print("=" * 70)