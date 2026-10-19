from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Header, HTTPException

from agents.orchestrator import Orchestrator
from security.context import get_current_user
from security.tenant import validate_graph_access


router = APIRouter(
    prefix="/api/mcp",
    tags=["MCP"],
)


_orchestrators: dict[
    str,
    Orchestrator,
] = {}


def _get_user(
    x_user_id: str | None,
):

    if not x_user_id:
        raise HTTPException(
            status_code=401,
            detail=(
                "X-User-ID authentication "
                "header is required."
            ),
        )

    try:

        return get_current_user(
            x_user_id.strip()
        )

    except Exception as exc:

        raise HTTPException(
            status_code=401,
            detail="Authentication failed.",
        ) from exc


def _get_orchestrator(
    graph_name: str,
) -> Orchestrator:

    if graph_name not in _orchestrators:

        _orchestrators[
            graph_name
        ] = Orchestrator(
            graph_name=graph_name
        )

    return _orchestrators[
        graph_name
    ]


@router.get(
    "/tools"
)
def list_mcp_tools(
    graph_name: str = "novatech",
    x_user_id: str | None = Header(
        default=None,
        alias="X-User-ID",
    ),
) -> Dict[str, Any]:

    user = _get_user(
        x_user_id
    )

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

    orchestrator = (
        _get_orchestrator(
            graph_name
        )
    )

    tools = (
        orchestrator.mcp_tools.list_tools()
    )

    return {
        "success": True,
        "graph_name": graph_name,
        "tools": tools,
    }


@router.post(
    "/select"
)
def select_mcp_tool(
    question: str,
    graph_name: str = "novatech",
    x_user_id: str | None = Header(
        default=None,
        alias="X-User-ID",
    ),
) -> Dict[str, Any]:

    user = _get_user(
        x_user_id
    )

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

    orchestrator = (
        _get_orchestrator(
            graph_name
        )
    )

    selection = (
        orchestrator.mcp_tools.select_tool(
            question=question
        )
    )

    return {
        "success": True,
        "graph_name": graph_name,
        "question": question,
        "selection": selection,
    }