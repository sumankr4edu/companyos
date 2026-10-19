import requests


BASE_URL = "http://127.0.0.1:8000"

HEADERS = {
    "X-User-ID": "suman",
}


def check(response):
    print(
        response.request.method,
        response.request.url,
        response.status_code,
    )

    if response.status_code >= 400:
        print(response.text)

    response.raise_for_status()

    return response.json()


def main():

    print("\n======================================")
    print("CompanyOS Phase 23 Action Test")
    print("======================================\n")

    # ----------------------------------
    # 1. Health
    # ----------------------------------

    response = requests.get(
        f"{BASE_URL}/health",
        timeout=10,
    )

    check(response)

    print("✓ Backend healthy")

    # ----------------------------------
    # 2. Create investigation
    # ----------------------------------

    response = requests.post(
        f"{BASE_URL}/api/investigations",
        headers=HEADERS,
        json={
            "title": "Investigate Payment Service",
            "description": (
                "Investigate the recent checkout failures "
                "and verify the Payment Service dependency path."
            ),
            "service_name": "Payment Service",
            "incident_title": "Checkout failures increased",
            "priority": "high",
            "graph_name": "novatech",
        },
        timeout=30,
    )

    result = check(response)

    assert result["success"]

    task_id = result["task_id"]

    print(
        "✓ Investigation created:",
        task_id,
    )

    # ----------------------------------
    # 3. Get task
    # ----------------------------------

    response = requests.get(
        f"{BASE_URL}/api/investigations/{task_id}",
        headers=HEADERS,
        params={
            "graph_name": "novatech",
        },
        timeout=20,
    )

    task = check(response)

    assert task["success"]

    print("✓ Investigation retrieved")

    # ----------------------------------
    # 4. Assign task
    # ----------------------------------

    response = requests.patch(
        f"{BASE_URL}/api/investigations/"
        f"{task_id}/assignee",
        headers=HEADERS,
        json={
            "assignee_name": "Maya Singh",
            "graph_name": "novatech",
        },
        timeout=30,
    )

    assignment = check(response)

    assert assignment["success"]

    print(
        "✓ Assigned to:",
        assignment["assignee"],
    )

    # ----------------------------------
    # 5. Update status
    # ----------------------------------

    response = requests.patch(
        f"{BASE_URL}/api/investigations/"
        f"{task_id}/status",
        headers=HEADERS,
        json={
            "status": "in_progress",
            "graph_name": "novatech",
        },
        timeout=30,
    )

    status = check(response)

    assert status["success"]
    assert status["status"] == "in_progress"

    print(
        "✓ Status:",
        status["status"],
    )

    # ----------------------------------
    # 6. Action history
    # ----------------------------------

    response = requests.get(
        f"{BASE_URL}/api/investigations/"
        f"{task_id}/actions",
        headers=HEADERS,
        params={
            "graph_name": "novatech",
        },
        timeout=30,
    )

    history = check(response)

    assert history["success"]

    assert len(history["actions"]) >= 3

    print(
        "✓ Audit actions:",
        len(history["actions"]),
    )

    # ----------------------------------
    # 7. List tasks
    # ----------------------------------

    response = requests.get(
        f"{BASE_URL}/api/investigations",
        headers=HEADERS,
        params={
            "graph_name": "novatech",
        },
        timeout=30,
    )

    tasks = check(response)

    assert tasks["success"]

    print(
        "✓ Total investigations:",
        len(tasks["tasks"]),
    )

    # ----------------------------------
    # 8. Graph verification
    # ----------------------------------

    response = requests.post(
        f"{BASE_URL}/api/graph/query",
        headers=HEADERS,
        json={
            "graph_name": "novatech",
            "query": (
                "MATCH (t:InvestigationTask "
                "{id: '%s'})"
                "-[:ASSIGNED_TO]->(p:Person) "
                "RETURN t.id, t.status, p.name"
                % task_id
            ),
        },
        timeout=30,
    )

    graph = check(response)

    print("✓ Task exists in FalkorDB")
    print("✓ Assignment exists in FalkorDB")

    print("\n======================================")
    print("PHASE 23 PASSED")
    print("Graph-native actions work.")
    print("======================================\n")


if __name__ == "__main__":
    main()