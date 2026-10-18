from agents.llm import llm_service


SYSTEM_PROMPT = """
You are the Analysis Agent for CompanyOS.

CompanyOS is a graph-native company intelligence system.

IMPORTANT RULES:

1. FalkorDB graph evidence is the primary source of truth.
2. Never invent company facts.
3. Clearly distinguish evidence from inference.
4. Prefer explicit graph relationships over assumptions.
5. Prefer fresher evidence when sources conflict.
6. Explicitly report contradictions.
7. Explicitly report unknown information.
8. Never reveal private chain-of-thought.
9. Provide concise, auditable reasoning based on graph evidence.
10. Use the supplied graph path when explaining relationships.
11. Never claim a relationship unless it is supported by graph evidence.
12. If evidence is insufficient, say so.

Your response MUST use this structure:

ANSWER:
<direct answer>

EVIDENCE:
<important supporting evidence>

GRAPH PATH:
<relevant relationship path>

WHY THIS ANSWER:
<short auditable explanation based only on graph evidence>

CONTRADICTIONS:
<conflicting evidence, or "None identified">

CONFIDENCE:
<0.0 - 1.0>

UNKNOWNS:
<information that cannot be established from the graph>
"""


class AnalysisAgent:

    def analyze(
        self,
        question: str,
        graph_context: dict,
    ):

        user_prompt = f"""
USER QUESTION:
{question}


==================================================
GRAPH EVIDENCE
==================================================

{graph_context.get("graph_evidence", [])}


==================================================
GRAPH INTELLIGENCE
==================================================

{graph_context.get("graph_intelligence", {})}


==================================================
EXACT GRAPH PATH
==================================================

{graph_context.get("graph_path", [])}


==================================================
EXPLAINABILITY
==================================================

{graph_context.get("explanation", {})}


==================================================
PERSISTENT MEMORY
==================================================

{graph_context.get("memory", [])}


==================================================
PROVENANCE
==================================================

{graph_context.get("provenance", [])}


==================================================
FRESHNESS
==================================================

{graph_context.get("freshness", [])}


==================================================
CONTRADICTIONS
==================================================

{graph_context.get("contradictions", [])}


==================================================
RETRIEVAL MODE
==================================================

{graph_context.get("retrieval_mode", "unknown")}


==================================================
CONFIDENCE
==================================================

{graph_context.get("confidence", 0.0)}


Answer ONLY from the supplied CompanyOS context.

Do not invent people, teams, services, incidents,
decisions, ownership, or relationships.

If the graph does not establish something,
put it under UNKNOWNS.
"""

        return llm_service.generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )