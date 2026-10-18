from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from memory.memory_agent import MemoryAgent


router = APIRouter(
    prefix="/api/memory",
    tags=["memory"],
)


class MemoryRequest(BaseModel):
    content: str
    memory_type: str = "episodic"
    entity_name: str | None = None
    importance: float = 0.5
    company_id: str = "novatech"


class MemorySearchRequest(BaseModel):
    query: str
    memory_type: str | None = None
    limit: int = 10
    company_id: str = "novatech"


@router.post("")
async def create_memory(request: MemoryRequest):
    try:
        agent = MemoryAgent(request.company_id)

        return agent.remember(
            content=request.content,
            memory_type=request.memory_type,
            entity_name=request.entity_name,
            importance=request.importance,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.post("/search")
async def search_memory(request: MemorySearchRequest):
    try:
        agent = MemoryAgent(request.company_id)

        return agent.search(
            query_text=request.query,
            memory_type=request.memory_type,
            limit=request.limit,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.get("/recent")
async def recent_memory(
    company_id: str = "novatech",
    limit: int = 10,
):
    try:
        agent = MemoryAgent(company_id)

        return agent.recent(limit)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.get("/related/{entity_name}")
async def related_memory(
    entity_name: str,
    company_id: str = "novatech",
):
    try:
        agent = MemoryAgent(company_id)

        return agent.related_to(entity_name)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )