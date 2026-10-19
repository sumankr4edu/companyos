from __future__ import annotations

from typing import Any, Dict, List, Optional

from agents.query_planner import QueryPlanner
from agents.cypher_generator import CypherGenerator
from agents.analysis_agent import AnalysisAgent
from agents.graph_intelligence_agent import GraphIntelligenceAgent
from agents.explainability import ExplainabilityAgent
from agents.hero_reasoning import HeroReasoningAgent
from agents.action_agent import ActionAgent
from agents.contradiction_agent import ContradictionAgent
from agents.freshness_agent import FreshnessAgent

from memory.conversation_store import ConversationStore
from memory.memory_agent import MemoryAgent

from graph.evidence import EvidenceManager
from graph.path_engine import GraphPathEngine

from tools.query_tools import GraphQueryTool

# Phase 25
from mcp.tool_agent import GraphToolAgent


class Orchestrator:
    """
    CompanyOS Graph-First Orchestrator.

    Architecture:

        User Question
              |
              v
        Query Planner
              |
              v
        Intent Detection
              |
        +-----+----------------------+
        |                            |
        v                            v
    Specialized                 Controlled
    Graph Intent                Cypher
        |                            |
        v                            v
    Graph Intelligence         Graph Query Tool
        |                            |
        +-------------+--------------+
                      |
                      v
                  FalkorDB
                      |
                      v
             Evidence Normalization
                      |
             +--------+---------+
             |                  |
             v                  v
       Contradiction        Freshness
       Detection            Analysis
             |                  |
             +--------+---------+
                      |
                      v
                Graph Path
                      |
                      v
              Gemini Analysis
                      |
                      v
             Persistent Memory
                      |
                      v
              Auditable Answer

    Phase 25:
        MCP-style FalkorDB graph tools are exposed through
        GraphToolAgent.

    FalkorDB remains the primary source of truth.
    """

    # =========================================================
    # Specialized Graph Intents
    # =========================================================

    SPECIALIZED_INTENTS = {
        "ownership_expertise",
        "blast_radius",
        "dependency_analysis",
        "centrality",
        "connected_component",
    }

    # =========================================================
    # Initialization
    # =========================================================

    def __init__(
        self,
        graph_name: str = "novatech",
    ):
        self.graph_name = graph_name

        # -----------------------------------------------------
        # Query / reasoning agents
        # -----------------------------------------------------

        self.planner = QueryPlanner()

        self.cypher_generator = CypherGenerator(
            graph_name=graph_name,
        )

        self.analysis_agent = AnalysisAgent()

        self.graph_intelligence = GraphIntelligenceAgent(
            graph_name=graph_name,
        )

        self.explainability = ExplainabilityAgent()

        self.hero_reasoning_agent = HeroReasoningAgent(
            graph_name=graph_name,
        )

        self.action_agent = ActionAgent(
            graph_name=graph_name,
        )

        # -----------------------------------------------------
        # Phase 24
        # -----------------------------------------------------

        self.contradiction_agent = ContradictionAgent()

        self.freshness_agent = FreshnessAgent(
            stale_after_days=180,
        )

        # -----------------------------------------------------
        # Graph infrastructure
        # -----------------------------------------------------

        self.graph_query = GraphQueryTool(
            graph_name=graph_name,
        )

        self.path_engine = GraphPathEngine(
            graph_name=graph_name,
        )

        self.evidence_manager = EvidenceManager()

        # -----------------------------------------------------
        # Phase 22
        # -----------------------------------------------------

        self.conversation_store = ConversationStore(
            graph_name=graph_name,
        )

        self.memory_agent = MemoryAgent(
            graph_name=graph_name,
        )

        # -----------------------------------------------------
        # Phase 25
        # -----------------------------------------------------

        self.mcp_tools = GraphToolAgent(
            graph_name=graph_name,
        )

    # =========================================================
    # Entity normalization
    # =========================================================

    @staticmethod
    def _entity_list(
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
    # Evidence normalization
    # =========================================================

    def _extract_records(
        self,
        evidence: Any,
    ) -> List[Dict[str, Any]]:

        if evidence is None:
            return []

        # -----------------------------------------------------
        # Already normalized list
        # -----------------------------------------------------

        if isinstance(evidence, list):

            if all(
                isinstance(item, dict)
                for item in evidence
            ):
                return evidence

            return [
                {
                    "value": item,
                }
                for item in evidence
            ]

        # -----------------------------------------------------
        # Primitive value
        # -----------------------------------------------------

        if not isinstance(
            evidence,
            dict,
        ):

            return [
                {
                    "value": evidence,
                }
            ]

        # -----------------------------------------------------
        # Nested FalkorDB result
        # -----------------------------------------------------

        nested_result = evidence.get(
            "result"
        )

        if isinstance(
            nested_result,
            dict,
        ):

            if isinstance(
                nested_result.get("rows"),
                list,
            ):

                return self._extract_records(
                    nested_result
                )

        # -----------------------------------------------------
        # Already normalized records
        # -----------------------------------------------------

        for key in (
            "records",
            "results",
            "data",
            "evidence",
        ):

            candidate = evidence.get(
                key
            )

            if isinstance(
                candidate,
                list,
            ):

                if all(
                    isinstance(
                        item,
                        dict,
                    )
                    for item in candidate
                ):

                    return candidate

        # -----------------------------------------------------
        # FalkorDB tabular response
        # -----------------------------------------------------

        header = evidence.get(
            "header",
            [],
        )

        rows = evidence.get(
            "rows",
            [],
        )

        clean_headers: List[str] = []

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

        records: List[
            Dict[str, Any]
        ] = []

        for row in rows:

            if not isinstance(
                row,
                (list, tuple),
            ):

                row = [row]

            record: Dict[str, Any] = {}

            for index, value in enumerate(row):

                if index < len(
                    clean_headers
                ):

                    key = clean_headers[
                        index
                    ]

                else:

                    key = (
                        f"column_{index}"
                    )

                record[key] = value

            records.append(
                record
            )

        return records

    # =========================================================
    # Plan formatting
    # =========================================================

    @staticmethod
    def _format_plan(
        plan: Any,
    ) -> Dict[str, Any]:

        if isinstance(
            plan,
            dict,
        ):
            return plan

        if hasattr(
            plan,
            "__dict__",
        ):

            return dict(
                plan.__dict__
            )

        return {
            "plan": str(plan)
        }

    # =========================================================
    # Intent
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
    # Specialized Graph Intelligence
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

            if isinstance(
                result,
                dict,
            ):

                return result

            return {
                "success": True,
                "result": result,
            }

        except Exception as exc:

            return {
                "success": False,
                "error": str(exc),
            }

    # =========================================================
    # Hero Investigation Detection
    # =========================================================

    @staticmethod
    def _is_hero_investigation(
        question: str,
    ) -> bool:

        text = question.lower()

        hero_terms = [
            "checkout failures increased",
            "what happened",
            "payment architecture",
            "who worked on the affected system",
            "who should investigate",
            "why was the architecture changed",
            "why was payment architecture changed",
        ]

        return any(
            term in text
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

        try:

            # -------------------------------------------------
            # Hero path
            # -------------------------------------------------

            if self._is_hero_investigation(
                question
            ):

                return (
                    self.path_engine.hero_path()
                )

            # -------------------------------------------------
            # Generic graph exploration
            # -------------------------------------------------

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

            result = (
                self.path_engine.explore(
                    entity_name=entities[0],
                    max_hops=4,
                    limit=20,
                )
            )

            if isinstance(
                result,
                dict,
            ):

                return result

            if isinstance(
                result,
                list,
            ):

                return {
                    "success": bool(
                        result
                    ),
                    "evidence": [],
                    "branches": result,
                    "nodes": [],
                    "relationships": [],
                    "path_count": len(
                        result
                    ),
                    "confidence": 0.0,
                    "unknowns": [],
                }

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
    # Conversation History
    # =========================================================

    def _load_conversation_history(
        self,
        session_id: Optional[str],
        user_id: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:

        if not session_id:
            return []

        try:

            return (
                self.conversation_store.get_history(
                    session_id=session_id,
                    user_id=user_id,
                    limit=limit,
                )
            )

        except Exception:

            return []

    # =========================================================
    # Conversation Context
    # =========================================================

    @staticmethod
    def _conversation_context(
        history: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:

        context: List[
            Dict[str, Any]
        ] = []

        for message in history:

            if not isinstance(
                message,
                dict,
            ):
                continue

            context.append(
                {
                    "role": message.get(
                        "role"
                    ),
                    "content": message.get(
                        "content"
                    ),
                    "created_at": message.get(
                        "created_at"
                    ),
                    "confidence": message.get(
                        "confidence"
                    ),
                    "graph_first": message.get(
                        "graph_first"
                    ),
                }
            )

        return context

    # =========================================================
    # Contradiction merge
    # =========================================================

    @staticmethod
    def _merge_contradictions(
        evidence_contradictions: Any,
        graph_contradictions: Any,
    ) -> List[Dict[str, Any]]:

        merged: List[
            Dict[str, Any]
        ] = []

        candidates: List[Any] = []

        if isinstance(
            evidence_contradictions,
            list,
        ):

            candidates.extend(
                evidence_contradictions
            )

        if isinstance(
            graph_contradictions,
            list,
        ):

            candidates.extend(
                graph_contradictions
            )

        for item in candidates:

            if not isinstance(
                item,
                dict,
            ):
                continue

            if item not in merged:

                merged.append(
                    item
                )

        return merged

    # =========================================================
    # MCP Tool Selection
    # =========================================================

    def _select_mcp_tool(
        self,
        question: str,
        entities: List[str],
    ) -> Dict[str, Any]:

        try:

            return (
                self.mcp_tools.select_tool(
                    question=question,
                    entity_name=(
                        entities[0]
                        if entities
                        else None
                    ),
                )
            )

        except Exception as exc:

            return {
                "tool": "falkor_cypher",
                "reason": (
                    "MCP tool selection "
                    f"failed: {exc}"
                ),
            }

    # =========================================================
    # MAIN RUN
    # =========================================================

    def run(
        self,
        question: str,
        user_id: str = "suman",
        session_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        memory_context: Optional[
            Dict[str, Any]
        ] = None,
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
        # 2. Conversation Context
        # =====================================================

        conversation_history = (
            self._load_conversation_history(
                session_id=session_id,
                user_id=user_id,
                limit=10,
            )
        )

        conversation_context = (
            self._conversation_context(
                conversation_history
            )
        )

        # =====================================================
        # 3. Query Planning
        # =====================================================

        plan = self.planner.plan(
            question
        )

        plan_data = (
            self._format_plan(
                plan
            )
        )

        entities = (
            self._entity_list(
                plan_data.get(
                    "entities"
                )
            )
        )

        intent = plan_data.get(
            "intent",
            "general_graph_search",
        )

        # =====================================================
        # 4. Phase 25 MCP Tool Selection
        # =====================================================

        mcp_selection = (
            self._select_mcp_tool(
                question=question,
                entities=entities,
            )
        )

        # =====================================================
        # 5. Graph Retrieval
        # =====================================================

        graph_intelligence: Dict[
            str,
            Any,
        ] = {}

        graph_evidence_raw: Any = None

        cypher: Optional[str] = None

        # =====================================================
        # 5A. Specialized Graph Intelligence
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
                        "result"
                    )
                    or graph_intelligence.get(
                        "evidence"
                    )
                    or graph_intelligence.get(
                        "data"
                    )
                    or graph_intelligence.get(
                        "rows"
                    )
                    or graph_intelligence.get(
                        "results"
                    )
                    or []
                )

            else:

                graph_evidence_raw = (
                    graph_intelligence
                )

            # -------------------------------------------------
            # Unwrap nested FalkorDB result
            # -------------------------------------------------

            if isinstance(
                graph_evidence_raw,
                dict,
            ):

                nested_result = (
                    graph_evidence_raw.get(
                        "result"
                    )
                )

                if (
                    isinstance(
                        nested_result,
                        dict,
                    )
                    and isinstance(
                        nested_result.get(
                            "rows"
                        ),
                        list,
                    )
                ):

                    graph_evidence_raw = (
                        nested_result
                    )

                elif isinstance(
                    graph_evidence_raw.get(
                        "rows"
                    ),
                    list,
                ):

                    graph_evidence_raw = (
                        graph_evidence_raw
                    )

        # =====================================================
        # 5B. Controlled Cypher
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
        # 6. Normalize Graph Evidence
        # =====================================================

        records = (
            self._extract_records(
                graph_evidence_raw
            )
        )

        # -----------------------------------------------------
        # Fallback
        # -----------------------------------------------------

        if (
            not records
            and isinstance(
                graph_intelligence,
                dict,
            )
        ):

            candidates = [
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

            for candidate in candidates:

                if candidate:

                    records = (
                        self._extract_records(
                            candidate
                        )
                    )

                    if records:
                        break

        # =====================================================
        # 7. Evidence Processing
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

        evidence_contradictions = (
            evidence_result.get(
                "contradictions",
                [],
            )
        )

        # =====================================================
        # 8. Phase 24 Contradiction Detection
        # =====================================================

        graph_contradictions = (
            self.contradiction_agent.detect(
                records
            )
        )

        contradictions = (
            self._merge_contradictions(
                evidence_contradictions,
                graph_contradictions,
            )
        )

        # =====================================================
        # 9. Semantic Memory
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

                memory = (
                    memory_result
                )

        except Exception:

            memory = []

        # =====================================================
        # 10. Provenance
        # =====================================================

        provenance = []

        for record in (
            processed_evidence
        ):

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

        # =====================================================
        # 11. Phase 24 Freshness
        # =====================================================

        freshness = (
            self.freshness_agent.analyze(
                records
            )
        )

        # =====================================================
        # 12. Exact Graph Path
        # =====================================================

        graph_path = (
            self._build_graph_path(
                question=question,
                entities=entities,
            )
        )

        # =====================================================
        # 13. Explainability
        # =====================================================

        try:

            explanation = (
                self.explainability.build(
                    answer="",
                    graph_result=graph_path,
                    contradictions=(
                        contradictions
                    ),
                )
            )

        except Exception:

            explanation = {
                "answer": "",
                "evidence": [],
                "graph_path": graph_path,
                "confidence": 0.0,
                "contradictions": (
                    contradictions
                ),
                "unknowns": [],
            }

        confidence = explanation.get(
            "confidence",
            0.0,
        )

        # =====================================================
        # 14. Hero Investigation
        # =====================================================

        is_hero = (
            self._is_hero_investigation(
                question
            )
        )

        if is_hero:

            try:

                hero_result = (
                    self.hero_reasoning_agent.execute()
                )

                if (
                    isinstance(
                        hero_result,
                        dict,
                    )
                    and hero_result.get(
                        "success"
                    )
                ):

                    graph_path = (
                        hero_result.get(
                            "graph",
                            graph_path,
                        )
                    )

                    explanation = (
                        self.explainability.build(
                            answer=hero_result.get(
                                "answer",
                                "",
                            ),
                            graph_result=(
                                graph_path
                            ),
                            contradictions=(
                                contradictions
                            ),
                        )
                    )

                    confidence = (
                        explanation.get(
                            "confidence",
                            0.0,
                        )
                    )

            except Exception:

                pass

        # =====================================================
        # 15. Retrieval Mode
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
        # 16. Graph Context For Gemini
        # =====================================================

        graph_context = {

            "question": question,

            "plan": plan_data,

            "entities": entities,

            "cypher": cypher,

            # Primary FalkorDB evidence
            "graph_evidence": (
                processed_evidence
            ),

            # Normalized raw graph records
            "graph_records": records,

            # Graph algorithms
            "graph_intelligence": (
                graph_intelligence
            ),

            # Exact path
            "graph_path": graph_path,

            # Explainability
            "explanation": explanation,

            # Semantic memory
            "memory": memory,

            # Conversation memory
            "conversation_history": (
                conversation_context
            ),

            "conversation_memory": (
                bool(
                    conversation_context
                )
            ),

            # External memory context
            "memory_context": (
                memory_context
            ),

            # Provenance
            "provenance": provenance,

            # Phase 24
            "freshness": freshness,

            # Phase 24
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

            # Phase 25
            "mcp": {
                "enabled": True,
                "selected_tool": (
                    mcp_selection.get(
                        "tool"
                    )
                ),
                "reason": (
                    mcp_selection.get(
                        "reason"
                    )
                ),
            },

            "hero_investigation": (
                is_hero
            ),

            "session_id": (
                session_id
            ),

            "conversation_id": (
                conversation_id
            ),
        }

        # =====================================================
        # 17. Gemini Analysis
        # =====================================================

        answer = (
            self.analysis_agent.analyze(
                question=question,
                graph_context=graph_context,
            )
        )

        # =====================================================
        # 18. Persistent Episodic Memory
        # =====================================================

        try:

            answer_text = str(
                answer
            )

            # -------------------------------------------------
            # Keep memory concise.
            # Never store private chain-of-thought.
            # -------------------------------------------------

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

                    "session_id": (
                        session_id
                    ),

                    "conversation_id": (
                        conversation_id
                    ),

                    "mcp_tool": (
                        mcp_selection.get(
                            "tool"
                        )
                    ),

                    "contradiction_count": (
                        len(
                            contradictions
                        )
                    ),

                    "stale_record_count": (
                        len(
                            freshness.get(
                                "stale_records",
                                [],
                            )
                        )
                        if isinstance(
                            freshness,
                            dict,
                        )
                        else 0
                    ),
                },
            )

        except Exception:

            # Memory failures should never
            # break the main graph answer.
            pass

        # =====================================================
        # 19. MCP Metadata
        # =====================================================

        try:

            available_tools = [
                tool["name"]
                for tool in (
                    self.mcp_tools.list_tools()
                )
            ]

        except Exception:

            available_tools = []

        mcp_metadata = {

            "enabled": True,

            "selected_tool": (
                mcp_selection.get(
                    "tool"
                )
            ),

            "reason": (
                mcp_selection.get(
                    "reason"
                )
            ),

            "available_tools": (
                available_tools
            ),
        }

        # =====================================================
        # 20. FINAL AUDITABLE RESULT
        # =====================================================

        return {

            "success": True,

            "question": question,

            "answer": answer,

            # -------------------------------------------------
            # Planning
            # -------------------------------------------------

            "plan": plan_data,

            "entities": entities,

            "cypher": cypher,

            # -------------------------------------------------
            # Graph
            # -------------------------------------------------

            "graph_name": (
                self.graph_name
            ),

            "graph_evidence": (
                processed_evidence
            ),

            "graph_records": records,

            "graph_intelligence": (
                graph_intelligence
            ),

            "graph_path": (
                graph_path
            ),

            # -------------------------------------------------
            # Explainability
            # -------------------------------------------------

            "explanation": (
                explanation
            ),

            "confidence": confidence,

            "evidence_count": len(
                processed_evidence
            ),

            # -------------------------------------------------
            # Memory
            # -------------------------------------------------

            "memory": memory,

            "session_id": (
                session_id
            ),

            "conversation_id": (
                conversation_id
            ),

            "conversation_history": (
                conversation_context
            ),

            "conversation_memory": (
                bool(
                    conversation_context
                )
            ),

            # -------------------------------------------------
            # Provenance
            # -------------------------------------------------

            "provenance": provenance,

            # -------------------------------------------------
            # Phase 24
            # -------------------------------------------------

            "freshness": freshness,

            "contradictions": (
                contradictions
            ),

            # -------------------------------------------------
            # Phase 25
            # -------------------------------------------------

            "mcp": mcp_metadata,

            # -------------------------------------------------
            # Retrieval
            # -------------------------------------------------

            "retrieval_mode": (
                retrieval_mode
            ),

            "graph_first": True,

            "hero_investigation": (
                is_hero
            ),
        }