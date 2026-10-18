
from typing import Any, Dict

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from agents.orchestrator import Orchestrator


router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


# ============================================================
# Request / Response Models
# ============================================================

class ChatRequest(BaseModel):
    question: str = Field(
        ...,
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


class ChatResponse(BaseModel):
    success: bool
    question: str
    answer: Any

    plan: Dict[str, Any] = Field(default_factory=dict)

    cypher: Any = None

    entities: list[Any] = Field(default_factory=list)

    graph_name: str

    graph_evidence: list[Any] = Field(default_factory=list)

    graph_intelligence: Any = None

    graph_path: Any = Field(default_factory=dict)

    explanation: Dict[str, Any] = Field(default_factory=dict)

    memory: list[Any] = Field(default_factory=list)

    provenance: list[Any] = Field(default_factory=list)

    freshness: list[Any] = Field(default_factory=list)

    contradictions: list[Any] = Field(default_factory=list)

    confidence: float = 0.0

    evidence_count: int = 0

    retrieval_mode: str = "unknown"

    graph_first: bool = True


# ============================================================
# Orchestrator Factory
# ============================================================

_orchestrators: dict[str, Orchestrator] = {}


def get_orchestrator(graph_name: str) -> Orchestrator:
    """
    Reuse one orchestrator instance per graph.

    This avoids reconstructing planners, graph tools,
    memory agents, and analysis agents for every request.
    """

    if graph_name not in _orchestrators:
        _orchestrators[graph_name] = Orchestrator(
            graph_name=graph_name
        )

    return _orchestrators[graph_name]


# ============================================================
# POST /api/chat
# ============================================================

@router.post(
    "",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
    x_user_id: str = Header(
        default="suman",
        alias="X-User-ID",
    ),
):
    """
    Execute the complete CompanyOS graph-first pipeline.

    Flow:

        User Question
             ↓
        Query Planner
             ↓
        FalkorDB Graph
             ↓
        Graph Intelligence
             ↓
        Exact Graph Path
             ↓
        Evidence + Explainability
             ↓
        Memory
             ↓
        Gemini Analysis
             ↓
        Auditable Answer
    """

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=422,
            detail="Question cannot be empty.",
        )

    # --------------------------------------------------------
    # Basic graph-name validation
    # --------------------------------------------------------

    graph_name = request.graph_name.strip()

    if not graph_name:
        raise HTTPException(
            status_code=422,
            detail="Graph name cannot be empty.",
        )

    # Demo tenant restriction.
    #
    # We currently expose NovaTech as the hackathon demo graph.
    # Additional tenant graphs can be enabled once the company
    # provisioning flow is connected.
    if graph_name != "novatech":
        raise HTTPException(
            status_code=403,
            detail="Graph access denied for this demo tenant.",
        )

    # --------------------------------------------------------
    # Normalize authenticated/demo user
    # --------------------------------------------------------

    user_id = (x_user_id or "suman").strip()

    if not user_id:
        user_id = "suman"

    # --------------------------------------------------------
    # Execute graph-first orchestration
    # --------------------------------------------------------

    try:
        orchestrator = get_orchestrator(graph_name)

        result = orchestrator.run(
            question=question,
            user_id=user_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        # Do not expose internal stack traces.
        raise HTTPException(
            status_code=500,
            detail="CompanyOS could not complete the investigation.",
        ) from exc

    # --------------------------------------------------------
    # Safety check:
    # API must never claim graph-first if orchestrator
    # accidentally returns otherwise.
    # --------------------------------------------------------

    if not result.get("graph_first", False):
        raise HTTPException(
            status_code=500,
            detail="Graph-first execution guarantee was not satisfied.",
        )

    return ChatResponse(
        success=bool(result.get("success", False)),
        question=result.get("question", question),
        answer=result.get("answer", ""),

        plan=result.get("plan", {}),

        cypher=result.get("cypher"),

        entities=result.get("entities", []),

        graph_name=result.get(
            "graph_name",
            graph_name,
        ),

        graph_evidence=result.get(
            "graph_evidence",
            [],
        ),

        graph_intelligence=result.get(
            "graph_intelligence",
        ),

        graph_path=result.get(
            "graph_path",
            {},
        ),

        explanation=result.get(
            "explanation",
            {},
        ),

        memory=result.get(
            "memory",
            [],
        ),

        provenance=result.get(
            "provenance",
            [],
        ),

        freshness=result.get(
            "freshness",
            [],
        ),

        contradictions=result.get(
            "contradictions",
            [],
        ),

        confidence=float(
            result.get(
                "confidence",
                0.0,
            ) or 0.0
        ),

        evidence_count=int(
            result.get(
                "evidence_count",
                0,
            ) or 0
        ),

        retrieval_mode=result.get(
            "retrieval_mode",
            "unknown",
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
    Lightweight endpoint for frontend readiness checks.
    """

    return {
        "status": "ready",
        "service": "companyos-chat",
        "graph_first": True,
        "graph": "novatech",
        "capabilities": [
            "query_planning",
            "graph_intelligence",
            "multi_hop_reasoning",
            "exact_graph_path",
            "evidence",
            "explainability",
            "persistent_memory",
            "gemini_analysis",
        ],
    }