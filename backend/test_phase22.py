import requests
import uuid


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
    print("CompanyOS Phase 22 Memory Test")
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
    # 2. Create conversation
    # ----------------------------------

    response = requests.post(
        f"{BASE_URL}/api/memory/conversation",
        headers=HEADERS,
        json={
            "title": "Phase 22 Investigation",
            "graph_name": "novatech",
        },
        timeout=20,
    )

    conversation = check(response)

    assert conversation["success"]

    conversation_id = conversation["conversation_id"]

    print(
        "✓ Conversation created:",
        conversation_id,
    )

    # ----------------------------------
    # 3. Chat with conversation
    # ----------------------------------

    question = (
        "Who owns the Payment Service and "
        "why was the payment architecture changed?"
    )

    response = requests.post(
        f"{BASE_URL}/api/chat",
        headers=HEADERS,
        json={
            "question": question,
            "graph_name": "novatech",
            "conversation_id": conversation_id,
        },
        timeout=120,
    )

    result = check(response)

    assert result["success"]
    assert result["graph_first"] is True
    assert result["conversation_id"] == conversation_id

    print("✓ Chat executed")
    print("✓ Graph-first:", result["graph_first"])
    print("✓ Answer:", result["answer"][:200])

    # ----------------------------------
    # 4. Verify persistence
    # ----------------------------------

    response = requests.get(
        f"{BASE_URL}/api/memory/conversation/{conversation_id}",
        headers=HEADERS,
        params={
            "graph_name": "novatech",
        },
        timeout=20,
    )

    stored = check(response)

    assert stored["success"]

    print("✓ Conversation retrieved from FalkorDB")

    # ----------------------------------
    # 5. Recent turns
    # ----------------------------------

    response = requests.get(
        f"{BASE_URL}/api/memory/conversation/"
        f"{conversation_id}/turns",
        headers=HEADERS,
        params={
            "graph_name": "novatech",
            "limit": 10,
        },
        timeout=20,
    )

    turns = check(response)

    assert turns["success"]
    assert len(turns["turns"]) >= 1

    print(
        "✓ Persistent turns:",
        len(turns["turns"]),
    )

    # ----------------------------------
    # 6. Memory search
    # ----------------------------------

    response = requests.post(
        f"{BASE_URL}/api/memory/search",
        headers=HEADERS,
        json={
            "question": "Payment Service architecture",
            "graph_name": "novatech",
            "limit": 5,
        },
        timeout=20,
    )

    memory = check(response)

    assert memory["success"]

    print(
        "✓ Memory matches:",
        len(memory["matches"]),
    )

    # ----------------------------------
    # 7. Context endpoint
    # ----------------------------------

    response = requests.post(
        f"{BASE_URL}/api/memory/context",
        headers=HEADERS,
        json={
            "question": "What did we discuss about payment?",
            "conversation_id": conversation_id,
            "graph_name": "novatech",
            "limit": 5,
        },
        timeout=20,
    )

    context = check(response)

    assert context["success"]

    print(
        "✓ Context recent turns:",
        len(context["recent_turns"]),
    )

    print("\n======================================")
    print("PHASE 22 PASSED")
    print("Persistent FalkorDB memory works.")
    print("======================================\n")


if __name__ == "__main__":
    main()