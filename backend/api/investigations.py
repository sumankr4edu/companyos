from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel, Field

from actions.investigation_tasks import InvestigationTaskManager
from security.context import get_current_user
from security.tenant import validate_graph_access


router = APIRouter(
    prefix="/api/investigations",
    tags=["investigations"],
)


# ============================================================
# Request Models
# ============================================================

class CreateInvestigationRequest(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=200,
    )

    description: str = Field(
        min_length=3,
        max_length=5000,
    )

    service_name: Optional[str] = None
    incident_title: Optional[str] = None
    assignee_name: Optional[str] = None

    priority: str = Field(
        default="medium",
        pattern="^(low|medium|high|critical)$",
    )

    graph_name: str = "novatech"


class UpdateStatusRequest(BaseModel):
    status: str = Field(
        pattern="^(open|in_progress|blocked|resolved|cancelled)$"
    )

    graph_name: str = "novatech"


class AssignInvestigationRequest(BaseModel):
    assignee_name: str = Field(
        min_length=2,
        max_length=200,
    )

    graph_name: str = "novatech"


# ============================================================
# Authentication / Authorization Helpers
# ============================================================

def _get_user(
    x_user_id: Optional[str],
):
    """
    Resolve the authenticated user.

    The application currently uses X-User-ID for demo authentication.
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


def _validate(
    graph_name: str,
    user,
    write: bool = False,
):
    """
    Validate tenant/graph access and optional write permission.

    IMPORTANT:
    validate_graph_access() expects:
        validate_graph_access(user, requested_graph)

    Do NOT pass graph_name= or user_id= because that is not
    the current security helper signature.
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

    # Demo write authorization.
    # Only Suman currently has graph/action write permissions.
    if write and user.user_id != "suman":
        raise HTTPException(
            status_code=403,
            detail="User is not authorized to perform graph actions.",
        )


# ============================================================
# Create Investigation
# ============================================================

@router.post("")
async def create_investigation(
    request: CreateInvestigationRequest,
    x_user_id: Optional[str] = Header(default=None),
):
    user = _get_user(x_user_id)

    _validate(
        request.graph_name,
        user,
        write=True,
    )

    manager = InvestigationTaskManager(
        request.graph_name
    )

    return manager.create_task(
        title=request.title,
        description=request.description,
        actor_id=user.user_id,
        service_name=request.service_name,
        incident_title=request.incident_title,
        assignee_name=request.assignee_name,
        priority=request.priority,
    )


# ============================================================
# List Investigations
# ============================================================

@router.get("")
async def list_investigations(
    graph_name: str = Query(default="novatech"),
    status: Optional[str] = None,
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    x_user_id: Optional[str] = Header(default=None),
):
    user = _get_user(x_user_id)

    _validate(
        graph_name,
        user,
    )

    manager = InvestigationTaskManager(
        graph_name
    )

    return manager.list_tasks(
        actor_id=None,
        status=status,
        limit=limit,
    )


# ============================================================
# Get Investigation
# ============================================================

@router.get("/{task_id}")
async def get_investigation(
    task_id: str,
    graph_name: str = Query(default="novatech"),
    x_user_id: Optional[str] = Header(default=None),
):
    user = _get_user(x_user_id)

    _validate(
        graph_name,
        user,
    )

    manager = InvestigationTaskManager(
        graph_name
    )

    return manager.get_task(
        task_id
    )


# ============================================================
# Update Investigation Status
# ============================================================

@router.patch("/{task_id}/status")
async def update_investigation_status(
    task_id: str,
    request: UpdateStatusRequest,
    x_user_id: Optional[str] = Header(default=None),
):
    user = _get_user(x_user_id)

    _validate(
        request.graph_name,
        user,
        write=True,
    )

    manager = InvestigationTaskManager(
        request.graph_name
    )

    return manager.update_status(
        task_id=task_id,
        status=request.status,
        actor_id=user.user_id,
    )


# ============================================================
# Assign Investigation
# ============================================================

@router.patch("/{task_id}/assignee")
async def assign_investigation(
    task_id: str,
    request: AssignInvestigationRequest,
    x_user_id: Optional[str] = Header(default=None),
):
    user = _get_user(x_user_id)

    _validate(
        request.graph_name,
        user,
        write=True,
    )

    manager = InvestigationTaskManager(
        request.graph_name
    )

    return manager.assign_task(
        task_id=task_id,
        assignee_name=request.assignee_name,
        actor_id=user.user_id,
    )


# ============================================================
# Investigation Action History
# ============================================================

@router.get("/{task_id}/actions")
async def get_action_history(
    task_id: str,
    graph_name: str = Query(default="novatech"),
    limit: int = Query(
        default=100,
        ge=1,
        le=200,
    ),
    x_user_id: Optional[str] = Header(default=None),
):
    user = _get_user(x_user_id)

    _validate(
        graph_name,
        user,
    )

    manager = InvestigationTaskManager(
        graph_name
    )

    return manager.action_history(
        task_id=task_id,
        limit=limit,
    )


# ============================================================
# All Action History
# ============================================================

@router.get("/actions/history/all")
async def get_all_action_history(
    graph_name: str = Query(default="novatech"),
    limit: int = Query(
        default=100,
        ge=1,
        le=200,
    ),
    x_user_id: Optional[str] = Header(default=None),
):
    user = _get_user(x_user_id)

    _validate(
        graph_name,
        user,
    )

    manager = InvestigationTaskManager(
        graph_name
    )

    return manager.action_history(
        limit=limit,
    )