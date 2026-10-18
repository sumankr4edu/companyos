from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from graph.queries import run_cypher
from agents.cypher_validator import CypherValidator

from security.context import (
    UserContext,
    get_current_user,
    require_permission,
)
from security.tenant import validate_graph_access


router = APIRouter(prefix="/api/graph", tags=["graph"])

validator = CypherValidator()


class CypherRequest(BaseModel):
    query: str
    graph_name: str = "novatech"


@router.post("/query")
async def graph_query(
    request: CypherRequest,
    user: UserContext = Depends(get_current_user),
):
    # 1. Authorization
    require_permission(user, "graph:read")

    # 2. Tenant isolation
    graph_name = validate_graph_access(
        user,
        request.graph_name,
    )

    # 3. Cypher validation
    valid, message = validator.validate(request.query)

    if not valid:
        raise HTTPException(
            status_code=400,
            detail=message,
        )

    # 4. Execute only after all security checks
    try:
        return run_cypher(
            request.query,
            graph_name,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Graph query failed: {str(exc)}",
        )