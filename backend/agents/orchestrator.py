from typing import Any, Dict, List

from agents.query_planner import QueryPlanner
from agents.cypher_generator import CypherGenerator
from agents.analysis_agent import AnalysisAgent
from agents.graph_intelligence_agent import GraphIntelligenceAgent

from memory.memory_agent import MemoryAgent
from graph.evidence import EvidenceManager
from graph.path_engine import GraphPathEngine

from tools.query_tools import GraphQueryTool
from agents.explainability import ExplainabilityAgent
from agents.hero_reasoning import HeroReasoningAgent


class Orchestrator:
    """
    Graph-first CompanyOS orchestrator.

    Architecture:

        User Question
             ↓
        Query Planner
             ↓
        Intent Detection
             ↓
        ┌──────────────────────────────┐
        │ Specialized graph intent?    │
        │                              │
        │ YES → Graph Intelligence     │
        │ NO  → Controlled Cypher      │
        └──────────────────────────────┘
             ↓
        FalkorDB
             ↓
        Exact Graph Path
             ↓
        Evidence + Explainability
             ↓
        Persistent Memory
             ↓
        Gemini Analysis
             ↓
        Auditable Answer

    FalkorDB is the primary context layer.

    The LLM never directly queries FalkorDB.
    """

    SPECIALIZED_INTENTS = {
        "ownership_expertise",
        "blast_radius",
        "dependency_analysis",
        "centrality",
        "connected_component",
    }

    def __init__(
        self,
        graph_name: str = "novatech",
    ):
        self.graph_name = graph_name

        # =====================================================
        # Core agents
        # =====================================================

        self.planner = QueryPlanner()

        self.graph_intelligence = GraphIntelligenceAgent(
            graph_name=graph_name
        )

        self.path_engine = GraphPathEngine(
            graph_name=graph_name
        )

        self.explainability = ExplainabilityAgent()

        self.hero_reasoning_agent = HeroReasoningAgent(
            graph_name=graph_name
        )

        self.cypher_generator = CypherGenerator(
            graph_name=graph_name
        )

        self.graph_query = GraphQueryTool(
            graph_name=graph_name
        )

        self.memory_agent = MemoryAgent(
            graph_name=graph_name
        )

        self.evidence_manager = EvidenceManager()

        self.analysis_agent = AnalysisAgent()

    # =========================================================
    # Helpers
    # =========================================================

    def _entity_list(
        self,
        entities: Any,
    ) -> List[str]:

        if entities is None:
            return []

        if isinstance(entities, list):
            return [
                str(item)
                for item in entities
                if item
            ]

        if isinstance(entities, tuple):
            return [
                str(item)
                for item in entities
                if item
            ]

        if isinstance(entities, dict):
            return [
                str(value)
                for value in entities.values()
                if value
            ]

        if isinstance(entities, str):
            return [entities]

        return [str(entities)]

    # =========================================================

    def _extract_records(
        self,
        evidence: Any,
    ) -> List[Dict[str, Any]]:

        if evidence is None:
            return []

        # Already a list
        if isinstance(evidence, list):

            if all(
                isinstance(item, dict)
                for item in evidence
            ):
                return evidence

            return [
                {
                    "value": item
                }
                for item in evidence
            ]

        # Unexpected object
        if not isinstance(evidence, dict):
            return [
                {
                    "value": evidence
                }
            ]

        header = evidence.get(
            "header",
            [],
        )

        rows = evidence.get(
            "rows",
            [],
        )

        # =====================================================
        # Clean FalkorDB headers
        # =====================================================

        clean_headers = []

        for item in header:

            text = str(item)

            if "'" in text:

                try:
                    clean_headers.append(
                        text.split("'")[1]
                    )

                except Exception:
                    clean_headers.append(
                        text
                    )

            else:
                clean_headers.append(
                    text
                )

        # =====================================================
        # Rows → dictionaries
        # =====================================================

        records = []

        for row in rows:

            record = {}

            for index, value in enumerate(row):

                if index < len(clean_headers):
                    key = clean_headers[index]
                else:
                    key = f"column_{index}"

                record[key] = value

            records.append(record)

        return records

    # =========================================================

    def _format_plan(
        self,
        plan: Any,
    ) -> Dict[str, Any]:

        if hasattr(plan, "__dict__"):
            return dict(plan.__dict__)

        if isinstance(plan, dict):
            return plan

        return {
            "plan": str(plan)
        }

    # =========================================================

    def _is_specialized_intent(
        self,
        intent: str,
    ) -> bool:

        return (
            intent
            in self.SPECIALIZED_INTENTS
        )

    # =========================================================

    def _run_specialized_graph_intelligence(
        self,
        plan: Any,
    ) -> Dict[str, Any]:

        try:

            result = (
                self.graph_intelligence.execute(
                    plan
                )
            )

            if not isinstance(
                result,
                dict,
            ):
                return {
                    "success": True,
                    "result": result,
                }

            return result

        except Exception as exc:

            return {
                "success": False,
                "error": str(exc),
            }

    # =========================================================
    # Hero Detection
    # =========================================================

    @staticmethod
    def _is_hero_investigation(
        question: str,
    ) -> bool:

        question_lower = question.lower()

        hero_terms = [
            "checkout failures increased",
            "what happened",
            "payment architecture",
            "who worked on the affected system",
            "who should investigate",
            "why was the architecture changed",
        ]

        return any(
            term in question_lower
            for term in hero_terms
        )

    # =========================================================
    # Graph Path
    # =========================================================

    def _build_graph_path(
        self,
        question: str,
        entities: List[str],
    ) -> Dict[str, Any]:
        """
        Build an auditable graph path.

        Hero investigations use the deterministic semantic resolver.

        Other questions use normal graph exploration.
        """

        try:

            if self._is_hero_investigation(
                question
            ):
                return self.path_engine.hero_path()

            if not entities:
                return {
                    "success": False,
                    "evidence": [],
                    "branches": [],
                    "nodes": [],
                    "relationships": [],
                    "path_count": 0,
                    "confidence": 0.0,
                    "unknowns": [],
                }

            paths = self.path_engine.explore(
                entity_name=entities[0],
                max_hops=4,
                limit=20,
            )

            return {
                "success": bool(paths),
                "evidence": [],
                "branches": paths,
                "nodes": [],
                "relationships": [],
                "path_count": len(paths),
                "confidence": 0.0,
                "unknowns": [],
            }

        except Exception:
            return {
                "success": False,
                "evidence": [],
                "branches": [],
                "nodes": [],
                "relationships": [],
                "path_count": 0,
                "confidence": 0.0,
                "unknowns": [],
            }

    # =========================================================
    # MAIN
    # =========================================================

    def run(
        self,
        question: str,
        user_id: str = "suman",
    ) -> Dict[str, Any]:

        # =====================================================
        # 1. Validate
        # =====================================================

        if not question or not question.strip():
            raise ValueError(
                "Question cannot be empty."
            )

        question = question.strip()

        # =====================================================
        # 2. Query planning
        # =====================================================

        plan = self.planner.plan(
            question
        )

        plan_data = self._format_plan(
            plan
        )

        entities = self._entity_list(
            plan_data.get(
                "entities"
            )
        )

        intent = plan_data.get(
            "intent",
            "general_graph_search",
        )

        # =====================================================
        # 3. GRAPH RETRIEVAL
        # =====================================================

        graph_intelligence = {}

        graph_evidence_raw = None

        cypher = None

        # =====================================================
        # Specialized graph algorithm
        # =====================================================

        if self._is_specialized_intent(
            intent
        ):

            graph_intelligence = (
                self._run_specialized_graph_intelligence(
                    plan
                )
            )

            if isinstance(
                graph_intelligence,
                dict,
            ):

                graph_evidence_raw = (
                    graph_intelligence.get(
                        "result",
                        graph_intelligence.get(
                            "evidence",
                            [],
                        ),
                    )
                )

            else:

                graph_evidence_raw = (
                    graph_intelligence
                )

        # =====================================================
        # Standard Cypher
        # =====================================================

        else:

            cypher = (
                self.cypher_generator.generate(
                    plan
                )
            )

            graph_evidence_raw = (
                self.graph_query.execute(
                    cypher
                )
            )

        # =====================================================
        # 4. Normalize graph evidence
        # =====================================================

        records = self._extract_records(
            graph_evidence_raw
        )

        # =====================================================
        # Fallback extraction
        # =====================================================

        if (
            not records
            and isinstance(
                graph_intelligence,
                dict,
            )
        ):

            possible_values = [

                graph_intelligence.get(
                    "rows"
                ),

                graph_intelligence.get(
                    "data"
                ),

                graph_intelligence.get(
                    "results"
                ),

                graph_intelligence.get(
                    "evidence"
                ),
            ]

            for candidate in possible_values:

                if candidate:

                    records = (
                        self._extract_records(
                            candidate
                        )
                    )

                    if records:
                        break

        # =====================================================
        # 5. Evidence processing
        # =====================================================

        evidence_result = (
            self.evidence_manager.process(
                records
            )
        )

        processed_evidence = (
            evidence_result.get(
                "evidence",
                [],
            )
        )

        contradictions = (
            evidence_result.get(
                "contradictions",
                [],
            )
        )

        # =====================================================
        # 6. Persistent memory
        # =====================================================

        memory = []

        try:

            memory_result = (
                self.memory_agent.search(
                    question=question,
                    limit=5,
                )
            )

            if memory_result:
                memory = memory_result

        except Exception:
            memory = []

        # =====================================================
        # 7. Provenance / freshness
        # =====================================================

        provenance = []

        freshness = []

        for record in processed_evidence:

            if not isinstance(
                record,
                dict,
            ):
                continue

            if record.get(
                "provenance"
            ):

                provenance.append(
                    record.get(
                        "provenance"
                    )
                )

            if record.get(
                "freshness"
            ) is not None:

                freshness.append(
                    record.get(
                        "freshness"
                    )
                )

        # =====================================================
        # 8. EXACT GRAPH PATH
        # =====================================================

        graph_path = self._build_graph_path(
            question=question,
            entities=entities,
        )

        # =====================================================
        # 9. INITIAL EXPLAINABILITY
        # =====================================================

        if graph_path.get("evidence"):

            explanation = self.explainability.build(
                answer="",
                graph_result=graph_path,
                contradictions=contradictions,
            )

        else:

            explanation = self.explainability.empty(
                answer="",
                reason=(
                    "No deterministic graph-path "
                    "evidence was found."
                ),
            )

        confidence = explanation.get(
            "confidence",
            0.0,
        )

        # =====================================================
        # 10. HERO INVESTIGATION
        # =====================================================

        is_hero = self._is_hero_investigation(
            question
        )

        if is_hero:

            hero_result = (
                self.hero_reasoning_agent.execute()
            )

            if hero_result.get("success"):

                graph_path = (
                    hero_result["graph"]
                )

                explanation = (
                    self.explainability.build(
                        answer=hero_result.get(
                            "answer",
                            "",
                        ),
                        graph_result=graph_path,
                        contradictions=contradictions,
                    )
                )

                confidence = explanation.get(
                    "confidence",
                    0.0,
                )

        # =====================================================
        # 11. Retrieval mode
        # =====================================================

        if self._is_specialized_intent(
            intent
        ):

            retrieval_mode = (
                "graph_algorithm"
            )

        else:

            retrieval_mode = (
                "controlled_cypher"
            )

        # =====================================================
        # 12. GRAPH-FIRST CONTEXT
        # =====================================================

        graph_context = {

            "question": question,

            "plan": plan_data,

            "entities": entities,

            "cypher": cypher,

            # PRIMARY SOURCE
            "graph_evidence": (
                processed_evidence
            ),

            # Graph algorithm result
            "graph_intelligence": (
                graph_intelligence
            ),

            # EXACT MULTI-HOP PATH
            "graph_path": graph_path,

            # Explainability
            "explanation": explanation,

            # Memory
            "memory": memory,

            # Provenance
            "provenance": provenance,

            # Freshness
            "freshness": freshness,

            # Contradictions
            "contradictions": (
                contradictions
            ),

            "confidence": confidence,

            "evidence_count": len(
                processed_evidence
            ),

            "graph_name": (
                self.graph_name
            ),

            "graph_first": True,

            "retrieval_mode": (
                retrieval_mode
            ),

            "hero_investigation": is_hero,
        }

        # =====================================================
        # 13. Gemini reasoning
        # =====================================================

        answer = (
            self.analysis_agent.analyze(
                question=question,
                graph_context=graph_context,
            )
        )

        # =====================================================
        # 14. Store episodic memory
        # =====================================================

        try:

            answer_text = str(
                answer
            )

            self.memory_agent.store(

                memory_type="episodic",

                content=(
                    f"Question: {question}\n"
                    f"Answer: "
                    f"{answer_text[:1500]}"
                ),

                entity_name=(
                    entities[0]
                    if entities
                    else None
                ),

                metadata={

                    "user_id": user_id,

                    "graph_name": (
                        self.graph_name
                    ),

                    "intent": intent,

                    "retrieval_mode": (
                        retrieval_mode
                    ),

                    "confidence": (
                        confidence
                    ),
                },
            )

        except Exception:
            pass

        # =====================================================
        # 15. FINAL AUDITABLE RESULT
        # =====================================================

        return {

            "success": True,

            "question": question,

            "answer": answer,

            "plan": plan_data,

            "cypher": cypher,

            "entities": entities,

            "graph_name": (
                self.graph_name
            ),

            "graph_evidence": (
                processed_evidence
            ),

            "graph_intelligence": (
                graph_intelligence
            ),

            "graph_path": (
                graph_path
            ),

            "explanation": (
                explanation
            ),

            "memory": memory,

            "provenance": provenance,

            "freshness": freshness,

            "contradictions": (
                contradictions
            ),

            "confidence": confidence,

            "evidence_count": len(
                processed_evidence
            ),

            "retrieval_mode": (
                retrieval_mode
            ),

            "graph_first": True,

            "hero_investigation": is_hero,
        }