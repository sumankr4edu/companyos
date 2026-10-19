from agents.orchestrator import Orchestrator
import traceback

try:
    print("START")

    orchestrator = Orchestrator(
        graph_name="novatech"
    )

    result = orchestrator.run(
        "Who knows the most about the payment system?",
        user_id="suman",
    )

    print("RESULT:")
    print(result)

except Exception:
    print("\n===== REAL ORCHESTRATOR ERROR =====")
    traceback.print_exc()
