from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel, Field

from memory.memory_agent import MemoryAgent
from security.context import get_current_user
from security.tenant import validate_graph_access


router = APIRouter(
    prefix="/api/memory",
    tags=["memory"],
)


class ConversationCreateRequest(BaseModel):
    title: Optional[str] = Field(
        default="CompanyOS Conversation",
        max_length=200,
    )
    graph_name: str = "novatech"


class MemorySearchRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    graph_name: str = "novatech"
    limit: int = Field(default=5, ge=1, le=20)


class MemoryContextRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    conversation_id: Optional[str] = None
    graph_name: str = "novatech"
    limit: int = Field(default=5, ge=1, le=20)


def _user_id(
    x_user_id: Optional[str],
) -> str:

    return get_current_user(
        x_user_id or "suman"
    ).user_id


def _validate_graph(
    graph_name: str,
    user_id: str,
):
    validate_graph_access(
        graph_name=graph_name,
        user_id=user_id,
    )


@router.post("/conversation")
async def create_conversation(
    request: ConversationCreateRequest,
    x_user_id: Optional[str] = Header(default=None),
):

    user_id = _user_id(x_user_id)

    _validate_graph(
        request.graph_name,
        user_id,
    )

    memory = MemoryAgent(
        graph_name=request.graph_name,
    )

    return memory.create_conversation(
        user_id=user_id,
        title=request.title,
    )


@router.get("/conversations")
async def list_conversations(
    graph_name: str = Query(default="novatech"),
    limit: int = Query(default=20, ge=1, le=100),
    x_user_id: Optional[str] = Header(default=None),
):

    user_id = _user_id(x_user_id)

    _validate_graph(
        graph_name,
        user_id,
    )

    memory = MemoryAgent(graph_name)

    return memory.list_conversations(
        user_id=user_id,
        limit=limit,
    )


@router.get("/conversation/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    graph_name: str = Query(default="novatech"),
    limit: int = Query(default=50, ge=1, le=100),
    x_user_id: Optional[str] = Header(default=None),
):

    user_id = _user_id(x_user_id)

    _validate_graph(
        graph_name,
        user_id,
    )

    memory = MemoryAgent(graph_name)

    return memory.get_conversation(
        conversation_id=conversation_id,
        user_id=user_id,
        limit=limit,
    )


@router.get("/conversation/{conversation_id}/turns")
async def get_recent_turns(
    conversation_id: str,
    graph_name: str = Query(default="novatech"),
    limit: int = Query(default=10, ge=1, le=50),
    x_user_id: Optional[str] = Header(default=None),
):

    user_id = _user_id(x_user_id)

    _validate_graph(
        graph_name,
        user_id,
    )

    memory = MemoryAgent(graph_name)

    return memory.recent(
        conversation_id=conversation_id,
        user_id=user_id,
        limit=limit,
    )


@router.post("/search")
async def search_memory(
    request: MemorySearchRequest,
    x_user_id: Optional[str] = Header(default=None),
):

    user_id = _user_id(x_user_id)

    _validate_graph(
        request.graph_name,
        user_id,
    )

    memory = MemoryAgent(
        graph_name=request.graph_name,
    )

    return memory.search(
        question=request.question,
        limit=request.limit,
        user_id=user_id,
    )


@router.post("/context")
async def memory_context(
    request: MemoryContextRequest,
    x_user_id: Optional[str] = Header(default=None),
):

    user_id = _user_id(x_user_id)

    _validate_graph(
        request.graph_name,
        user_id,
    )

    memory = MemoryAgent(
        graph_name=request.graph_name,
    )

    return memory.build_context(
        question=request.question,
        user_id=user_id,
        conversation_id=request.conversation_id,
        limit=request.limit,
    )


@router.delete("/conversation/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    graph_name: str = Query(default="novatech"),
    x_user_id: Optional[str] = Header(default=None),
):

    user_id = _user_id(x_user_id)

    _validate_graph(
        graph_name,
        user_id,
    )

    memory = MemoryAgent(graph_name)

    return memory.delete_conversation(
        conversation_id=conversation_id,
        user_id=user_id,
    )