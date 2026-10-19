from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from agents.orchestrator import Orchestrator
from memory.memory_agent import MemoryAgent
from security.context import get_current_user
from security.tenant import validate_graph_access


router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


# ============================================================
# Request / Response Models
# ============================================================

class ChatRequest(BaseModel):
    """
    Request payload for CompanyOS AI chat.

    A conversation_id allows multiple questions to belong
    to the same persistent investigation.
    """

    question: str = Field(
        min_length=1,
        max_length=5000,
        description="Question to ask CompanyOS",
    )

    graph_name: str = Field(
        default="novatech",
        min_length=1,
        max_length=100,
        description="FalkorDB graph to query",
    )

    conversation_id: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Persistent CompanyOS investigation conversation",
    )


class ChatResponse(BaseModel):
    """
    Complete auditable CompanyOS response.

    The API exposes graph evidence, paths, confidence,
    provenance, freshness and contradictions.

    Private chain-of-thought is never returned.
    """

    success: bool

    question: str

    answer: Any = ""

    # --------------------------------------------------------
    # Persistent conversation
    # --------------------------------------------------------

    conversation_id: Optional[str] = None

    conversation_persistence: Optional[Dict[str, Any]] = None

    # --------------------------------------------------------
    # Planning
    # --------------------------------------------------------

    plan: Dict[str, Any] = Field(
        default_factory=dict
    )

    cypher: Any = None

    entities: list[Any] = Field(
        default_factory=list
    )

    # --------------------------------------------------------
    # Graph
    # --------------------------------------------------------

    graph_name: str

    graph_evidence: list[Any] = Field(
        default_factory=list
    )

    graph_intelligence: Any = None

    graph_path: Any = Field(
        default_factory=dict
    )

    # --------------------------------------------------------
    # Explainability
    # --------------------------------------------------------

    explanation: Dict[str, Any] = Field(
        default_factory=dict
    )

    contradictions: list[Any] = Field(
        default_factory=list
    )

    confidence: float = 0.0

    evidence_count: int = 0

    # --------------------------------------------------------
    # Memory
    # --------------------------------------------------------

    memory: Any = Field(
        default_factory=dict
    )

    # --------------------------------------------------------
    # Provenance / Freshness
    # --------------------------------------------------------

    provenance: list[Any] = Field(
        default_factory=list
    )

    freshness: dict[str, Any] = Field(
        default_factory=dict
    )

    # --------------------------------------------------------
    # Execution metadata
    # --------------------------------------------------------

    retrieval_mode: str = "graph_first"

    graph_first: bool = True


# ============================================================
# Orchestrator Factory
# ============================================================

_orchestrators: dict[str, Orchestrator] = {}


def get_orchestrator(
    graph_name: str,
) -> Orchestrator:
    """
    Reuse one orchestrator instance per FalkorDB graph.

    This avoids rebuilding planners, graph tools and
    analysis agents for every request.
    """

    if graph_name not in _orchestrators:
        _orchestrators[graph_name] = Orchestrator(
            graph_name=graph_name
        )

    return _orchestrators[graph_name]


# ============================================================
# Memory Factory
# ============================================================

_memory_agents: dict[str, MemoryAgent] = {}


def get_memory_agent(
    graph_name: str,
) -> MemoryAgent:
    """
    Reuse one persistent MemoryAgent per graph.
    """

    if graph_name not in _memory_agents:
        _memory_agents[graph_name] = MemoryAgent(
            graph_name=graph_name
        )

    return _memory_agents[graph_name]


# ============================================================
# User Resolution
# ============================================================

def resolve_user(
    x_user_id: Optional[str],
):
    """
    Resolve the authenticated CompanyOS user context.
    """

    if not x_user_id or not x_user_id.strip():
        raise HTTPException(
            status_code=401,
            detail="X-User-ID authentication header is required.",
        )

    try:
        return get_current_user(
            x_user_id.strip()
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed.",
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=401,
            detail="Unable to resolve authenticated user.",
        ) from exc

# ============================================================
# Graph Validation
# ============================================================

def validate_chat_graph(
    user,
    graph_name: str,
) -> None:
    """
    Validate authenticated user access to the requested
    FalkorDB graph using the existing tenant security contract.
    """

    try:
        validate_graph_access(
            user,
            graph_name,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail="Graph access denied.",
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=403,
            detail="Graph access denied.",
        ) from exc

# ============================================================
# POST /api/chat
# ============================================================

@router.post(
    "",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
    x_user_id: Optional[str] = Header(
        default=None,
        alias="X-User-ID",
    ),
):
    """
    Execute the complete CompanyOS graph-first pipeline.

    Pipeline:

        User Question
             ↓
        Authentication
             ↓
        Tenant / Graph Validation
             ↓
        Persistent Conversation
             ↓
        Memory Recall
             ↓
        Query Planner
             ↓
        FalkorDB Graph
             ↓
        Graph Intelligence
             ↓
        Exact Graph Path
             ↓
        Evidence
             ↓
        Contradiction / Freshness Analysis
             ↓
        Explainability
             ↓
        Gemini Analysis
             ↓
        Persistent Investigation Turn
             ↓
        Auditable Response

    CompanyOS does not store or expose private chain-of-thought.
    """

    # ========================================================
    # 1. Validate question
    # ========================================================

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=422,
            detail="Question cannot be empty.",
        )

    # ========================================================
    # 2. Validate graph name
    # ========================================================

    graph_name = request.graph_name.strip()

    if not graph_name:
        raise HTTPException(
            status_code=422,
            detail="Graph name cannot be empty.",
        )

    # ========================================================
    # 3. Resolve authenticated user
    # ========================================================

    current_user = resolve_user(
        x_user_id
    )

    user_id = current_user.user_id

    validate_chat_graph(
        user=current_user,
        graph_name=graph_name,
    )

    # ========================================================
    # 5. Demo graph restriction
    # ========================================================
    #
    # CompanyOS currently operates against the NovaTech
    # demonstration tenant.
    #
    # This restriction can be removed when the graph registry
    # and full tenant provisioning system are enabled.
    # ========================================================

    if graph_name != "novatech":
        raise HTTPException(
            status_code=403,
            detail=(
                "Only the NovaTech demo graph is enabled "
                "for this CompanyOS build."
            ),
        )

    # ========================================================
    # 6. Get persistent memory agent
    # ========================================================

    memory_agent = get_memory_agent(
        graph_name=graph_name
    )

    # ========================================================
    # 7. Create / validate conversation
    # ========================================================

    conversation_id = request.conversation_id

    try:

        if conversation_id:

            conversation_id = conversation_id.strip()

            if not conversation_id:
                raise HTTPException(
                    status_code=422,
                    detail="conversation_id cannot be empty.",
                )

            memory_agent.ensure_conversation(
                conversation_id=conversation_id,
                user_id=user_id,
            )

        else:

            conversation = (
                memory_agent.create_conversation(
                    user_id=user_id,
                    title=question[:80],
                )
            )

            conversation_id = conversation.get(
                "conversation_id"
            )

            if not conversation_id:
                raise RuntimeError(
                    "Conversation ID was not created."
                )

    except HTTPException:
        raise

    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail="Conversation access denied.",
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Could not create or load "
                "investigation conversation."
            ),
        ) from exc

    # ========================================================
    # 8. Recall persistent memory
    # ========================================================

    try:

        memory_context = (
            memory_agent.build_context(
                question=question,
                user_id=user_id,
                conversation_id=conversation_id,
                limit=5,
            )
        )

    except Exception:

        # Memory retrieval should improve the investigation,
        # but a retrieval failure should not destroy the
        # graph-first investigation.
        memory_context = {
            "enabled": False,
            "conversation_id": conversation_id,
            "matches": [],
            "recent_turns": [],
        }

    # ========================================================
    # 9. Execute CompanyOS orchestrator
    # ========================================================

    try:

        orchestrator = get_orchestrator(
            graph_name=graph_name
        )

        result = orchestrator.run(
            question=question,
            user_id=user_id,
            conversation_id=conversation_id,
            memory_context=memory_context,
        )

    except TypeError as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "CompanyOS orchestrator execution failed: "
                f"{exc}"
            ),
        ) from exc

    except ValueError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        # Keep implementation details out of the API response.
        raise HTTPException(
            status_code=500,
            detail=(
                "CompanyOS could not complete "
                "the investigation."
            ),
        ) from exc

    # ========================================================
    # 10. Validate orchestrator result
    # ========================================================

    if not isinstance(result, dict):
        raise HTTPException(
            status_code=500,
            detail=(
                "CompanyOS returned an invalid "
                "investigation result."
            ),
        )

    # ========================================================
    # 11. Graph-first guarantee
    # ========================================================

    graph_first = bool(
        result.get(
            "graph_first",
            False,
        )
    )

    if not graph_first:
        raise HTTPException(
            status_code=500,
            detail=(
                "Graph-first execution guarantee "
                "was not satisfied."
            ),
        )

    # ========================================================
    # 12. Persist completed investigation turn
    # ========================================================

    persistence_result: Dict[str, Any] = {
        "success": False,
        "conversation_id": conversation_id,
    }

    try:

        persistence_result = (
            memory_agent.save_turn(
                conversation_id=conversation_id,
                user_id=user_id,
                question=question,
                answer=str(
                    result.get(
                        "answer",
                        "",
                    )
                ),
                plan=result.get(
                    "plan",
                    {},
                ),
                entities=result.get(
                    "entities",
                    [],
                ),
                graph_path=result.get(
                    "graph_path",
                    {},
                ),
                evidence_count=int(
                    result.get(
                        "evidence_count",
                        0,
                    )
                    or 0
                ),
                confidence=float(
                    result.get(
                        "confidence",
                        0.0,
                    )
                    or 0.0
                ),
                retrieval_mode=result.get(
                    "retrieval_mode",
                    "graph_first",
                ),
            )
        )

    except PermissionError as exc:

        raise HTTPException(
            status_code=403,
            detail="Conversation access denied.",
        ) from exc

    except Exception as exc:

        # Investigation succeeded but persistent state failed.
        # Persistence is part of the Phase 22 contract.
        raise HTTPException(
            status_code=500,
            detail=(
                "Investigation completed, but the "
                "conversation state could not be persisted."
            ),
        ) from exc

    # ========================================================
    # 13. Normalize confidence
    # ========================================================

    try:
        confidence = float(
            result.get(
                "confidence",
                0.0,
            )
            or 0.0
        )
    except (TypeError, ValueError):
        confidence = 0.0

    confidence = max(
        0.0,
        min(
            1.0,
            confidence,
        ),
    )

    # ========================================================
    # 14. Normalize evidence count
    # ========================================================

    try:
        evidence_count = int(
            result.get(
                "evidence_count",
                0,
            )
            or 0
        )
    except (TypeError, ValueError):
        evidence_count = 0

    # ========================================================
    # 15. Normalize list fields
    # ========================================================

    graph_evidence = result.get(
        "graph_evidence",
        [],
    )

    if graph_evidence is None:
        graph_evidence = []

    graph_path = result.get(
        "graph_path",
        {},
    )

    if graph_path is None:
        graph_path = {}

    entities = result.get(
        "entities",
        [],
    )

    if entities is None:
        entities = []

    provenance = result.get(
        "provenance",
        [],
    )

    if provenance is None:
        provenance = []

    freshness = result.get(
        "freshness",
        {},
    )

    if freshness is None:
        freshness = {}

    contradictions = result.get(
        "contradictions",
        [],
    )

    if contradictions is None:
        contradictions = []

    # ========================================================
    # 16. Return auditable CompanyOS response
    # ========================================================

    return ChatResponse(
        success=bool(
            result.get(
                "success",
                True,
            )
        ),

        question=result.get(
            "question",
            question,
        ),

        answer=result.get(
            "answer",
            "",
        ),

        # ----------------------------------------------------
        # Conversation
        # ----------------------------------------------------

        conversation_id=conversation_id,

        conversation_persistence=(
            persistence_result
        ),

        # ----------------------------------------------------
        # Planning
        # ----------------------------------------------------

        plan=result.get(
            "plan",
            {},
        ),

        cypher=result.get(
            "cypher",
        ),

        entities=entities,

        # ----------------------------------------------------
        # Graph
        # ----------------------------------------------------

        graph_name=result.get(
            "graph_name",
            graph_name,
        ),

        graph_evidence=graph_evidence,

        graph_intelligence=result.get(
            "graph_intelligence",
        ),

        graph_path=graph_path,

        # ----------------------------------------------------
        # Explainability
        # ----------------------------------------------------

        explanation=result.get(
            "explanation",
            {},
        ),

        contradictions=contradictions,

        confidence=confidence,

        evidence_count=evidence_count,

        # ----------------------------------------------------
        # Memory
        # ----------------------------------------------------

        memory=result.get(
            "memory",
            memory_context,
        ),

        # ----------------------------------------------------
        # Provenance / Freshness
        # ----------------------------------------------------

        provenance=provenance,

        freshness=freshness,

        # ----------------------------------------------------
        # Execution metadata
        # ----------------------------------------------------

        retrieval_mode=result.get(
            "retrieval_mode",
            "graph_first",
        ),

        graph_first=True,
    )


# ============================================================
# GET /api/chat/status
# ============================================================

@router.get(
    "/status",
    tags=["Chat"],
)
async def chat_status():
    """
    Lightweight frontend/backend readiness endpoint.
    """

    return {
        "status": "ready",

        "service": "companyos-chat",

        "graph_first": True,

        "graph": "novatech",

        "phase": 22,

        "capabilities": [
            "query_planning",
            "graph_intelligence",
            "multi_hop_reasoning",
            "exact_graph_path",
            "evidence",
            "explainability",
            "persistent_memory",
            "conversation_state",
            "memory_recall",
            "conversation_turn_persistence",
            "gemini_analysis",
        ],
    }