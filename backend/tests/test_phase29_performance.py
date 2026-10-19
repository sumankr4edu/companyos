import time

import pytest
from fastapi.testclient import TestClient

from main import app
from graph.client import graph_client


client = TestClient(app)


# ============================================================
# Helpers
# ============================================================

def timed_call(fn):
    start = time.perf_counter()
    result = fn()
    elapsed = time.perf_counter() - start
    return result, elapsed


# ============================================================
# 1. FalkorDB connectivity latency
# ============================================================

def test_graph_query_latency():
    def query():
        return graph_client.query(
            """
            MATCH (s:Service)
            RETURN s.name AS name
            LIMIT 20
            """,
            "novatech",
        )

    result, elapsed = timed_call(query)

    assert result is not None
    assert elapsed < 2.0

    print(f"\nGraph query latency: {elapsed:.4f}s")


# ============================================================
# 2. Payment dependency query
# ============================================================

def test_payment_dependency_latency():
    def query():
        return graph_client.query(
            """
            MATCH (payment:Service)-[:DEPENDS_ON]->(checkout:Service)
            WHERE payment.name = 'Payment Service'
              AND checkout.name = 'Checkout Service'
            RETURN DISTINCT
                payment.name AS payment_service,
                checkout.name AS dependency
            LIMIT 5
            """,
            "novatech",
        )

    result, elapsed = timed_call(query)

    assert result is not None
    assert elapsed < 2.0

    print(f"\nPayment dependency latency: {elapsed:.4f}s")


# ============================================================
# 3. Ownership ranking latency
# ============================================================

def test_ownership_ranking_latency():
    def query():
        return graph_client.query(
            """
            MATCH (p:Person)-[:OWNS]->(s:Service)
            WHERE s.name = 'Payment Service'
            RETURN
                p.name AS person,
                count(*) AS ownership_count
            ORDER BY ownership_count DESC, person
            LIMIT 20
            """,
            "novatech",
        )

    result, elapsed = timed_call(query)

    assert result is not None
    assert elapsed < 2.0

    print(f"\nOwnership ranking latency: {elapsed:.4f}s")


# ============================================================
# 4. Bounded multi-hop traversal
# ============================================================

def test_bounded_multi_hop_latency():
    def query():
        return graph_client.query(
            """
            MATCH path =
                (s:Service)-[*1..3]->(target)
            WHERE s.name = 'Payment Service'
            RETURN path
            LIMIT 25
            """,
            "novatech",
        )

    result, elapsed = timed_call(query)

    assert result is not None
    assert elapsed < 3.0

    print(f"\nMulti-hop latency: {elapsed:.4f}s")


# ============================================================
# 5. Chat latency
# ============================================================

def test_chat_latency():
    def request():
        return client.post(
            "/api/chat",
            headers={
                "X-User-ID": "suman",
            },
            json={
                "question": "Who knows the most about the payment system?"
            },
        )

    response, elapsed = timed_call(request)

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert body["graph_first"] is True

    print(f"\nChat latency: {elapsed:.4f}s")


# ============================================================
# 6. Graph result bounding
# ============================================================

def test_graph_result_is_bounded():
    result = graph_client.query(
        """
        MATCH (s:Service)-[:DEPENDS_ON]->(target:Service)
        RETURN DISTINCT
            s.name AS source,
            target.name AS target
        LIMIT 50
        """,
        "novatech",
    )

    assert result is not None

    rows = getattr(result, "result_set", [])

    assert len(rows) <= 50

    print(f"\nBounded result rows: {len(rows)}")