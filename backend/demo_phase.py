import json
from datetime import datetime
from pathlib import Path

import requests


BASE_URL = "http://127.0.0.1:8000"

HEADERS = {
    "X-User-ID": "suman",
    "Content-Type": "application/json",
}

OUTPUT_DIR = Path(__file__).resolve().parent / "demo_output"

QUESTIONS = [
    "Who knows the most about the payment system?",
    "Why was the payment architecture changed?",
    "What happens if Payment Service goes down?",
    "Who should investigate the checkout failures?",
    (
        "Checkout failures increased this week. "
        "What happened, who worked on the affected system before, "
        "what decision caused the current architecture, "
        "and who should investigate it?"
    ),
]


def print_section(title: str, output_lines: list[str]):
    separator = "=" * 80

    print()
    print(separator)
    print(title)
    print(separator)

    output_lines.append("")
    output_lines.append(separator)
    output_lines.append(title)
    output_lines.append(separator)


def record(line: str, output_lines: list[str]):
    print(line)
    output_lines.append(line)


def pretty_json(data):
    return json.dumps(data, indent=2, default=str)


def call_chat(question: str, output_lines: list[str], results: list[dict]):
    print_section(f"QUESTION\n{question}", output_lines)

    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            headers=HEADERS,
            json={
                "question": question,
            },
            timeout=60,
        )

        record(f"HTTP STATUS: {response.status_code}", output_lines)

        if response.status_code != 200:
            record("REQUEST FAILED", output_lines)
            record(response.text, output_lines)

            results.append(
                {
                    "question": question,
                    "success": False,
                    "status_code": response.status_code,
                    "error": response.text,
                }
            )
            return

        data = response.json()

        print_section("ANSWER", output_lines)
        record(str(data.get("answer", "")), output_lines)

        print_section("GRAPH-FIRST", output_lines)
        record(str(data.get("graph_first")), output_lines)

        print_section("GRAPH CONTEXT", output_lines)
        graph_context = data.get("graph_context", {})
        record(pretty_json(graph_context), output_lines)

        print_section("EVIDENCE", output_lines)
        evidence = data.get("evidence", [])
        record(pretty_json(evidence), output_lines)

        print_section("CONTRADICTIONS", output_lines)
        contradictions = data.get("contradictions", [])
        record(pretty_json(contradictions), output_lines)

        print_section("FRESHNESS", output_lines)
        freshness = data.get("freshness", {})
        record(pretty_json(freshness), output_lines)

        print_section("UNKNOWN / LIMITATIONS", output_lines)
        unknowns = data.get("unknowns", [])
        record(pretty_json(unknowns), output_lines)

        results.append(
            {
                "question": question,
                "success": True,
                "status_code": response.status_code,
                "response": data,
            }
        )

    except Exception as exc:
        record(f"ERROR: {exc}", output_lines)

        results.append(
            {
                "question": question,
                "success": False,
                "error": str(exc),
            }
        )


def save_outputs(output_lines: list[str], results: list[dict]):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().astimezone().isoformat()

    txt_path = OUTPUT_DIR / "phase30_demo_output.txt"
    json_path = OUTPUT_DIR / "phase30_demo_output.json"

    with txt_path.open("w", encoding="utf-8") as file:
        file.write("\n".join(output_lines))
        file.write("\n")

    payload = {
        "project": "CompanyOS",
        "phase": "Phase 30 — Judge Demo",
        "generated_at": timestamp,
        "base_url": BASE_URL,
        "user": "suman",
        "total_questions": len(QUESTIONS),
        "successful_questions": sum(
            1 for item in results if item.get("success") is True
        ),
        "failed_questions": sum(
            1 for item in results if item.get("success") is not True
        ),
        "results": results,
    }

    with json_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, default=str)

    print()
    print("=" * 80)
    print("DEMO OUTPUT SAVED")
    print("=" * 80)
    print(f"TXT : {txt_path}")
    print(f"JSON: {json_path}")
    print("=" * 80)


def main():
    output_lines = []
    results = []

    print_section(
        "COMPANYOS — GRAPH-NATIVE COMPANY BRAIN\nPHASE 30 JUDGE DEMO",
        output_lines,
    )

    record(
        f"Backend: {BASE_URL}",
        output_lines,
    )

    record(
        "Graph database: FalkorDB",
        output_lines,
    )

    record(
        "Authenticated user: suman",
        output_lines,
    )

    record(
        f"Demo questions: {len(QUESTIONS)}",
        output_lines,
    )

    for question in QUESTIONS:
        call_chat(
            question,
            output_lines,
            results,
        )

    print_section("DEMO SUMMARY", output_lines)

    successful = sum(
        1 for item in results if item.get("success") is True
    )

    failed = len(results) - successful

    record(
        f"Successful questions: {successful}/{len(results)}",
        output_lines,
    )

    record(
        f"Failed questions: {failed}/{len(results)}",
        output_lines,
    )

    if failed == 0:
        record("STATUS: PASS", output_lines)
    else:
        record("STATUS: PARTIAL / CHECK FAILURES", output_lines)

    save_outputs(
        output_lines,
        results,
    )


if __name__ == "__main__":
    main()