import os
import uuid

import pytest
from fastapi.testclient import TestClient

from main import app
from graph.client import graph_client


client = TestClient(app)

USER_HEADERS = {
    "X-User-ID": "suman",
    "Content-Type": "application/json",
}


def api(method, path, **kwargs):
    response = client.request(
        method,
        path,
        headers=USER_HEADERS,
        **kwargs,
    )

    print(f"\n[{method}] {path}")
    print(f"STATUS: {response.status_code}")

    try:
        print(response.json())
    except Exception:
        print(response.text)

    return response


# ============================================================
# 1. Health
# ============================================================

def test_health():
    response = client.get("/health")

    assert response.status_code == 200


# ============================================================
# 2. Graph connectivity
# ============================================================

def test_graph_connectivity():
    result = graph_client.query(
        """
        MATCH (n)
        RETURN count(n) AS node_count
        """,
        graph_name="novatech",
    )

    rows = result.result_set

    assert rows
    assert rows[0][0] > 0


# ============================================================
# 3. Core NovaTech entities exist
# ============================================================

def test_novatech_core_graph():
    result = graph_client.query(
        """
        MATCH (p:Person)
        WITH count(p) AS people
        MATCH (s:Service)
        WITH people, count(s) AS services
        MATCH (i:Incident)
        WITH people, services, count(i) AS incidents
        MATCH (d:Decision)
        RETURN
            people,
            services,
            incidents,
            count(d) AS decisions
        """,
        graph_name="novatech",
    )

    row = result.result_set[0]

    people = row[0]
    services = row[1]
    incidents = row[2]
    decisions = row[3]

    assert people > 0
    assert services > 0
    assert incidents > 0
    assert decisions > 0


# ============================================================
# 4. Graph query API
# ============================================================

def test_graph_query():
    response = api(
        "POST",
        "/api/graph/query",
        json={
            "query": """
                MATCH (s:Service)
                RETURN s.name AS name
                LIMIT 5
            """
        },
    )

    assert response.status_code == 200


# ============================================================
# 5. Chat / Orchestrator
# ============================================================

def test_chat_orchestrator():
    response = api(
        "POST",
        "/api/chat",
        json={
            "question": (
                "Who knows the most about the payment system?"
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data is not None


# ============================================================
# 6. Multi-hop graph reasoning
# ============================================================

def test_payment_multi_hop_path():
    result = graph_client.query(
        """
        MATCH path =
            (checkout:Service)-[:DEPENDS_ON]->(payment:Service)
        WHERE checkout.name = 'Checkout Service'
          AND payment.name = 'Payment Service'
        RETURN path
        LIMIT 1
        """,
        graph_name="novatech",
    )

    assert result.result_set
# ============================================================
# 7. Canonical payment owner
# ============================================================

def test_payment_owner():
    result = graph_client.query(
        """
        MATCH (p:Person)-[:OWNS]->(s:Service)
        WHERE s.name = 'Payment Service'
        RETURN p.name AS owner
        """,
        graph_name="novatech",
    )

    owners = [row[0] for row in result.result_set]

    assert owners

    print("Payment Service owners:", owners)


# ============================================================
# 8. Agent coordination persistence
# ============================================================

def test_agent_run_creation():
    question = (
        "E2E coordination test "
        + uuid.uuid4().hex[:8]
    )

    response = api(
        "POST",
        "/api/agents/runs",
        json={
            "question": question,
            "metadata": {
                "source": "phase28-e2e",
            },
        },
    )

    assert response.status_code in (200, 201)

    data = response.json()

    assert data.get("success") is True

    run = data.get("run", {})

    assert run.get("id")

    run_id = run["id"]

    # Verify directly in FalkorDB.
    result = graph_client.query(
        f"""
        MATCH (r:AgentRun)
        WHERE r.id = '{run_id}'
        RETURN
            r.id AS id,
            r.status AS status,
            r.user_id AS user_id
        """,
        graph_name="novatech",
    )

    assert result.result_set

    row = result.result_set[0]

    assert row[0] == run_id
    assert row[2] == "suman"


# ============================================================
# 9. Memory endpoint
# ============================================================

def test_memory_endpoint():
    response = api(
        "GET",
        "/api/memory",
    )

    # Memory API implementations may expose different
    # status semantics, but must not return server failure.
    assert response.status_code < 500


# ============================================================
# 10. Actions endpoint
# ============================================================

def test_actions_endpoint():
    response = api(
        "GET",
        "/api/actions",
    )

    assert response.status_code < 500


# ============================================================
# 11. Tenant isolation
# ============================================================

def test_tenant_isolation():
    response = client.post(
        "/api/graph/query",
        headers=USER_HEADERS,
        json={
            "graph_name": "another_company",
            "query": """
                MATCH (n)
                RETURN n
                LIMIT 1
            """,
        },
    )

    assert response.status_code in (400, 403, 404)


# ============================================================
# 12. Cypher write protection
# ============================================================

def test_cypher_write_protection():
    response = client.post(
        "/api/graph/query",
        headers=USER_HEADERS,
        json={
            "query": """
                CREATE (n:SecurityTest {
                    name: 'should_not_exist'
                })
                RETURN n
            """,
        },
    )

    assert response.status_code in (400, 403)


# ============================================================
# 13. Multiple statement protection
# ============================================================

def test_multiple_statement_protection():
    response = client.post(
        "/api/graph/query",
        headers=USER_HEADERS,
        json={
            "query": """
                MATCH (n)
                RETURN n
                LIMIT 1;

                MATCH (x)
                RETURN x
                LIMIT 1
            """,
        },
    )

    assert response.status_code in (400, 403)


# ============================================================
# 14. Read-only user cannot create action
# ============================================================

def test_read_only_user_cannot_create_action():
    response = client.post(
        "/api/actions/tasks",
        headers={
            "X-User-ID": "raj",
            "Content-Type": "application/json",
        },
        json={
            "title": "Unauthorized E2E test",
            "description": "Should be rejected",
        },
    )

    assert response.status_code in (401, 403, 404)


# ============================================================
# 15. FalkorDB coordination graph structure
# ============================================================

def test_coordination_graph_structure():
    result = graph_client.query(
        """
        MATCH (r:AgentRun)
        OPTIONAL MATCH (r)-[rel]->(child)
        RETURN
            r.id AS run_id,
            type(rel) AS relationship,
            labels(child) AS labels
        LIMIT 50
        """,
        graph_name="novatech",
    )

    assert result.result_set

    print("\nCoordination graph:")

    for row in result.result_set:
        print(row)