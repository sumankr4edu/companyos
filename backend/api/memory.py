from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel, Field

from memory.memory_agent import MemoryAgent
from security.context import get_current_user
from security.tenant import validate_graph_access


router = APIRouter(
    prefix="/api/memory",
    tags=["Memory"],
)


# ============================================================
# Request Models
# ============================================================


class ConversationCreateRequest(BaseModel):
    title: str = Field(
        default="New Investigation",
        min_length=1,
        max_length=200,
    )

    graph_name: str = Field(
        default="novatech",
        min_length=1,
        max_length=100,
    )


class MemorySearchRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )

    graph_name: str = Field(
        default="novatech",
        min_length=1,
        max_length=100,
    )

    limit: int = Field(
        default=5,
        ge=1,
        le=20,
    )


class MemoryContextRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )

    conversation_id: Optional[str] = None

    graph_name: str = Field(
        default="novatech",
        min_length=1,
        max_length=100,
    )

    limit: int = Field(
        default=5,
        ge=1,
        le=20,
    )


# ============================================================
# Security Helpers
# ============================================================


def resolve_user(x_user_id: Optional[str]):
    """
    Resolve the authenticated demo user.

    The security layer expects the user context object,
    not a plain string, when validating graph access.
    """

    return get_current_user(
        x_user_id or "suman"
    )


def validate_access(
    graph_name: str,
    user,
) -> None:
    """
    Validate that the authenticated user can access
    the requested FalkorDB graph.
    """

    try:
        validate_graph_access(
            user,
            graph_name,
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )


def get_memory_agent(
    graph_name: str,
    user,
) -> MemoryAgent:
    """
    Create a MemoryAgent only after tenant validation.
    """

    validate_access(
        graph_name=graph_name,
        user=user,
    )

    return MemoryAgent(
        graph_name=graph_name,
    )


# ============================================================
# CREATE CONVERSATION
# ============================================================


@router.post("/conversation")
async def create_conversation(
    request: ConversationCreateRequest,
    x_user_id: Optional[str] = Header(
        default=None,
        alias="X-User-ID",
    ),
):
    """
    Create a persistent CompanyOS investigation.

    Example:

    POST /api/memory/conversation

    {
        "title": "Payment Investigation",
        "graph_name": "novatech"
    }
    """

    user = resolve_user(x_user_id)

    agent = get_memory_agent(
        graph_name=request.graph_name,
        user=user,
    )

    try:
        result = agent.create_conversation(
            user_id=user.user_id,
            title=request.title,
        )

        return {
            "success": True,
            "conversation_id": result.get(
                "conversation_id"
            ),
            "conversation": result,
            "graph_name": request.graph_name,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ============================================================
# LIST CONVERSATIONS
# ============================================================


@router.get("/conversations")
async def list_conversations(
    graph_name: str = Query(
        default="novatech",
        min_length=1,
        max_length=100,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    x_user_id: Optional[str] = Header(
        default=None,
        alias="X-User-ID",
    ),
):
    """
    List persistent investigations belonging to
    the authenticated user.
    """

    user = resolve_user(x_user_id)

    agent = get_memory_agent(
        graph_name=graph_name,
        user=user,
    )

    try:
        conversations = agent.list_conversations(
            user_id=user.user_id,
            limit=limit,
        )

        return {
            "success": True,
            "conversations": conversations,
            "count": len(conversations),
            "graph_name": graph_name,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ============================================================
# GET CONVERSATION
# ============================================================


@router.get("/conversation/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    graph_name: str = Query(
        default="novatech",
        min_length=1,
        max_length=100,
    ),
    x_user_id: Optional[str] = Header(
        default=None,
        alias="X-User-ID",
    ),
):
    """
    Retrieve a persistent investigation and its turns.
    """

    user = resolve_user(x_user_id)

    agent = get_memory_agent(
        graph_name=graph_name,
        user=user,
    )

    try:
        result = agent.get_conversation(
            conversation_id=conversation_id,
            user_id=user.user_id,
            include_turns=True,
        )

        if not result:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found",
            )

        return {
            "success": True,
            "conversation": result,
            "conversation_id": conversation_id,
            "graph_name": graph_name,
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ============================================================
# GET CONVERSATION TURNS
# ============================================================


@router.get(
    "/conversation/{conversation_id}/turns"
)
async def get_conversation_turns(
    conversation_id: str,
    graph_name: str = Query(
        default="novatech",
        min_length=1,
        max_length=100,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    x_user_id: Optional[str] = Header(
        default=None,
        alias="X-User-ID",
    ),
):
    """
    Retrieve the individual turns belonging to
    a persistent conversation.
    """

    user = resolve_user(x_user_id)

    agent = get_memory_agent(
        graph_name=graph_name,
        user=user,
    )

    try:
        conversation = agent.get_conversation(
            conversation_id=conversation_id,
            user_id=user.user_id,
            include_turns=False,
        )

        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found",
            )

        turns = agent.recent(
            conversation_id=conversation_id,
            user_id=user.user_id,
            limit=limit,
        )

        return {
            "success": True,
            "conversation_id": conversation_id,
            "turns": turns,
            "count": len(turns),
            "graph_name": graph_name,
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ============================================================
# SEARCH MEMORY
# ============================================================


@router.post("/search")
async def search_memory(
    request: MemorySearchRequest,
    x_user_id: Optional[str] = Header(
        default=None,
        alias="X-User-ID",
    ),
):
    """
    Search persistent CompanyOS conversation memory.
    """

    user = resolve_user(x_user_id)

    agent = get_memory_agent(
        graph_name=request.graph_name,
        user=user,
    )

    try:
        results = agent.search(
            question=request.question,
            user_id=user.user_id,
            limit=request.limit,
        )

        return {
            "success": True,
            "question": request.question,
            "results": results,
            "graph_name": request.graph_name,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ============================================================
# BUILD MEMORY CONTEXT
# ============================================================


@router.post("/context")
async def build_memory_context(
    request: MemoryContextRequest,
    x_user_id: Optional[str] = Header(
        default=None,
        alias="X-User-ID",
    ),
):
    """
    Build the memory context that gets passed
    into the CompanyOS orchestrator.
    """

    user = resolve_user(x_user_id)

    agent = get_memory_agent(
        graph_name=request.graph_name,
        user=user,
    )

    try:
        context = agent.build_context(
            question=request.question,
            user_id=user.user_id,
            conversation_id=request.conversation_id,
            limit=request.limit,
        )

        return {
            "success": True,
            "context": context,
            "conversation_id": request.conversation_id,
            "graph_name": request.graph_name,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


# ============================================================
# DELETE CONVERSATION
# ============================================================


@router.delete(
    "/conversation/{conversation_id}"
)
async def delete_conversation(
    conversation_id: str,
    graph_name: str = Query(
        default="novatech",
        min_length=1,
        max_length=100,
    ),
    x_user_id: Optional[str] = Header(
        default=None,
        alias="X-User-ID",
    ),
):
    """
    Delete a conversation belonging to the
    authenticated user.
    """

    user = resolve_user(x_user_id)

    agent = get_memory_agent(
        graph_name=graph_name,
        user=user,
    )

    try:
        result = agent.delete_conversation(
            conversation_id=conversation_id,
            user_id=user.user_id,
        )

        return {
            "success": True,
            "conversation_id": conversation_id,
            "result": result,
            "graph_name": graph_name,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )