from graph.algorithms import GraphAlgorithms


algorithms = GraphAlgorithms(
    graph_name="novatech"
)


def print_result(title, result):

    print()
    print("=" * 80)
    print(title)
    print("=" * 80)

    print(result)


# =========================================================
# 1. Who knows the most about Payment Service?
# =========================================================

print_result(
    "WHO KNOWS THE MOST ABOUT PAYMENT SERVICE?",
    algorithms.expertise_ranking(
        entity_name="Payment Service",
        limit=10,
    ),
)


# =========================================================
# 2. What breaks if Payment Service goes down?
# =========================================================

print_result(
    "PAYMENT SERVICE BLAST RADIUS",
    algorithms.dependency_blast_radius(
        service_name="Payment Service",
        max_hops=4,
        limit=50,
    ),
)


# =========================================================
# 3. Who are the most connected people?
# =========================================================

print_result(
    "PEOPLE CENTRALITY",
    algorithms.people_centrality(
        limit=10,
    ),
)


# =========================================================
# 4. Which systems are most connected?
# =========================================================

print_result(
    "SYSTEM CENTRALITY",
    algorithms.system_centrality(
        limit=10,
    ),
)


# =========================================================
# 5. What is connected to Payment Service?
# =========================================================

print_result(
    "PAYMENT SERVICE CONNECTED COMPONENT",
    algorithms.connected_component(
        entity_name="Payment Service",
        max_hops=4,
        limit=30,
    ),
)


# =========================================================
# 6. Relationship distribution
# =========================================================

print_result(
    "RELATIONSHIP COUNTS",
    algorithms.relationship_counts(),
)


print()
print("=" * 80)
print("PHASE 15 GRAPH INTELLIGENCE TEST COMPLETE")
print("=" * 80)