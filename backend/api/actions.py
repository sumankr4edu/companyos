from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from agents.action_agent import ActionAgent

from security.context import (
    UserContext,
    get_current_user,
    require_permission,
)


router = APIRouter(
    prefix="/api/actions",
    tags=["actions"],
)

action_agent = ActionAgent()


class ActionRequest(BaseModel):
    action_type: str = Field(..., min_length=1)
    payload: Dict[str, Any] = Field(default_factory=dict)


class ActionResponse(BaseModel):
    success: bool
    action_type: str
    result: Dict[str, Any]


@router.post(
    "",
    response_model=ActionResponse,
)
def execute_action(
    request: ActionRequest,
    user: UserContext = Depends(get_current_user),
):
    # Authorization
    require_permission(
        user,
        "actions:create",
    )

    # Never trust actor supplied by the client.
    # The authenticated user becomes the actor.
    actor = user.user_id

    try:
        result = action_agent.execute(
            action_type=request.action_type,
            actor=actor,
            payload=request.payload,
        )

        return {
            "success": True,
            "action_type": request.action_type,
            "result": result,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Action execution failed: {exc}",
        )