from typing import Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from agents.coordination import AgentCoordinationStore
from security.context import get_current_user
from security.tenant import validate_graph_access


router = APIRouter(
    prefix="/api/agents",
    tags=["Agents"],
)


def _get_user(x_user_id: Optional[str]):
    if not x_user_id or not x_user_id.strip():
        raise HTTPException(
            status_code=401,
            detail="X-User-ID authentication header is required.",
        )

    try:
        return get_current_user(x_user_id.strip())
    except Exception as exc:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed.",
        ) from exc


def _validate(user, graph_name: str):
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


class CreateRunRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )

    graph_name: str = "novatech"

    conversation_id: Optional[str] = None


class CreateTaskRequest(BaseModel):
    agent: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    task_type: str = Field(
        ...,
        min_length=1,
        max_length=200,
    )

    input_data: dict = Field(
        default_factory=dict,
    )

    depends_on: Optional[str] = None


class EventRequest(BaseModel):
    event_type: str = Field(
        ...,
        min_length=1,
        max_length=200,
    )

    agent: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    payload: dict = Field(
        default_factory=dict,
    )

    task_id: Optional[str] = None


# ============================================================
# Runs
# ============================================================

@router.post("/runs")
def create_run(
    body: CreateRunRequest,
    x_user_id: Optional[str] = Header(default=None),
):
    user = _get_user(x_user_id)

    _validate(
        user,
        body.graph_name,
    )

    store = AgentCoordinationStore(
        body.graph_name,
    )

    run = store.create_run(
        user_id=user.user_id,
        question=body.question,
        conversation_id=body.conversation_id,
    )

    return {
        "success": True,
        "run": run,
    }


@router.get("/runs")
def list_runs(
    graph_name: str = "novatech",
    limit: int = 20,
    x_user_id: Optional[str] = Header(default=None),
):
    user = _get_user(x_user_id)

    _validate(
        user,
        graph_name,
    )

    store = AgentCoordinationStore(
        graph_name,
    )

    runs = store.list_runs(
        user_id=user.user_id,
        limit=limit,
    )

    return {
        "success": True,
        "count": len(runs),
        "runs": runs,
    }


@router.get("/runs/{run_id}")
def get_run(
    run_id: str,
    graph_name: str = "novatech",
    x_user_id: Optional[str] = Header(default=None),
):
    user = _get_user(x_user_id)

    _validate(
        user,
        graph_name,
    )

    store = AgentCoordinationStore(
        graph_name,
    )

    try:
        run = store.get_run(run_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    if run["user_id"] != user.user_id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this agent run.",
        )

    return {
        "success": True,
        "run": run,
    }


@router.get("/runs/{run_id}/tasks")
def get_tasks(
    run_id: str,
    graph_name: str = "novatech",
    x_user_id: Optional[str] = Header(default=None),
):
    user = _get_user(x_user_id)

    _validate(
        user,
        graph_name,
    )

    store = AgentCoordinationStore(
        graph_name,
    )

    try:
        run = store.get_run(run_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    if run["user_id"] != user.user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied.",
        )

    tasks = store.get_run_tasks(run_id)

    return {
        "success": True,
        "count": len(tasks),
        "tasks": tasks,
    }


@router.get("/runs/{run_id}/events")
def get_events(
    run_id: str,
    graph_name: str = "novatech",
    x_user_id: Optional[str] = Header(default=None),
):
    user = _get_user(x_user_id)

    _validate(
        user,
        graph_name,
    )

    store = AgentCoordinationStore(
        graph_name,
    )

    try:
        run = store.get_run(run_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    if run["user_id"] != user.user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied.",
        )

    events = store.get_run_events(run_id)

    return {
        "success": True,
        "count": len(events),
        "events": events,
    }


# ============================================================
# Tasks
# ============================================================

@router.post("/runs/{run_id}/tasks")
def create_task(
    run_id: str,
    body: CreateTaskRequest,
    graph_name: str = "novatech",
    x_user_id: Optional[str] = Header(default=None),
):
    user = _get_user(x_user_id)

    _validate(
        user,
        graph_name,
    )

    if user.user_id != "suman":
        raise HTTPException(
            status_code=403,
            detail="User is not authorized to create agent tasks.",
        )

    store = AgentCoordinationStore(
        graph_name,
    )

    try:
        run = store.get_run(run_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    if run["user_id"] != user.user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied.",
        )

    task = store.create_task(
        run_id=run_id,
        agent=body.agent,
        task_type=body.task_type,
        input_data=body.input_data,
        depends_on=body.depends_on,
    )

    return {
        "success": True,
        "task": task,
    }


@router.post("/runs/{run_id}/events")
def add_event(
    run_id: str,
    body: EventRequest,
    graph_name: str = "novatech",
    x_user_id: Optional[str] = Header(default=None),
):
    user = _get_user(x_user_id)

    _validate(
        user,
        graph_name,
    )

    store = AgentCoordinationStore(
        graph_name,
    )

    try:
        run = store.get_run(run_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    if run["user_id"] != user.user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied.",
        )

    event = store.add_event(
        run_id=run_id,
        event_type=body.event_type,
        agent=body.agent,
        payload=body.payload,
        task_id=body.task_id,
    )

    return {
        "success": True,
        "event": event,
    }


# ============================================================
# Resume
# ============================================================

@router.post("/runs/{run_id}/resume")
def resume_run(
    run_id: str,
    graph_name: str = "novatech",
    x_user_id: Optional[str] = Header(default=None),
):
    user = _get_user(x_user_id)

    _validate(
        user,
        graph_name,
    )

    store = AgentCoordinationStore(
        graph_name,
    )

    try:
        run = store.get_run(run_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    if run["user_id"] != user.user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied.",
        )

    resumed = store.resume_run(run_id)

    return {
        "success": True,
        "run": resumed,
    }