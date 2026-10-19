from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from memory.conversation_store import ConversationStore


router = APIRouter(
    prefix="/api/conversations",
    tags=["conversations"],
)


def get_user_id(x_user_id: Optional[str]) -> str:
    return x_user_id or "suman"


class CreateConversationRequest(BaseModel):
    title: str = Field(
        default="New Investigation",
        min_length=1,
        max_length=200,
    )


class MessageRequest(BaseModel):
    role: str
    content: str
    metadata: dict = {}


@router.post("")
async def create_conversation(
    request: CreateConversationRequest,
    x_user_id: Optional[str] = Header(default=None),
):
    user_id = get_user_id(x_user_id)

    store = ConversationStore("novatech")

    return store.create_session(
        user_id=user_id,
        title=request.title,
    )


@router.get("")
async def list_conversations(
    x_user_id: Optional[str] = Header(default=None),
):
    user_id = get_user_id(x_user_id)

    store = ConversationStore("novatech")

    return {
        "success": True,
        "conversations": store.list_sessions(user_id),
    }


@router.get("/{session_id}")
async def get_conversation(
    session_id: str,
    x_user_id: Optional[str] = Header(default=None),
):
    user_id = get_user_id(x_user_id)

    store = ConversationStore("novatech")

    try:
        history = store.get_history(
            session_id=session_id,
            user_id=user_id,
        )
    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail="Conversation access denied",
        )

    return {
        "success": True,
        "session_id": session_id,
        "messages": history,
    }


@router.post("/{session_id}/messages")
async def add_message(
    session_id: str,
    request: MessageRequest,
    x_user_id: Optional[str] = Header(default=None),
):
    user_id = get_user_id(x_user_id)

    store = ConversationStore("novatech")

    try:
        message = store.add_message(
            session_id=session_id,
            user_id=user_id,
            role=request.role,
            content=request.content,
            metadata=request.metadata,
        )
    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail="Conversation access denied",
        )

    return {
        "success": True,
        "message": message,
    }


@router.delete("/{session_id}")
async def delete_conversation(
    session_id: str,
    x_user_id: Optional[str] = Header(default=None),
):
    user_id = get_user_id(x_user_id)

    store = ConversationStore("novatech")

    try:
        return store.delete_session(
            session_id=session_id,
            user_id=user_id,
        )
    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail="Conversation access denied",
        )