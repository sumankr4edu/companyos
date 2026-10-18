from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from graph.evidence import EvidenceManager


router = APIRouter(
    prefix="/api/evidence",
    tags=["evidence"],
)


class EvidenceRequest(BaseModel):
    records: list[dict]


@router.post("/process")
async def process_evidence(
    request: EvidenceRequest,
):
    try:
        manager = EvidenceManager()

        return manager.process(
            request.records
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )