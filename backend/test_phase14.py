from agents.orchestrator import Orchestrator


def run_test(question):

    print("\n" + "=" * 80)
    print(f"QUESTION: {question}")
    print("=" * 80)

    orchestrator = Orchestrator(
        graph_name="novatech"
    )

    result = orchestrator.run(
        question=question,
        user_id="suman",
    )

    print("\nINTENT:")
    print(
        result["plan"].get(
            "intent"
        )
    )

    print("\nENTITIES:")
    print(
        result["entities"]
    )

    print("\nGENERATED CYPHER:")
    print(
        result["cypher"]
    )

    print("\nEVIDENCE COUNT:")
    print(
        result["evidence_count"]
    )

    print("\nANSWER:")
    print(
        result["answer"]
    )


if __name__ == "__main__":

    run_test(
        "Why was the payment architecture changed?"
    )

    run_test(
        "What systems does Checkout Service depend on?"
    )

    run_test(
        "Who knows the most about the payment system?"
    )