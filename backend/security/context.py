from dataclasses import dataclass
from typing import Set

from fastapi import Header, HTTPException


@dataclass
class UserContext:
    user_id: str
    company_id: str
    graph_name: str
    permissions: Set[str]


DEMO_USERS = {
    "suman": UserContext(
        user_id="suman",
        company_id="novatech",
        graph_name="novatech",
        permissions={
            "graph:read",
            "graph:write",
            "memory:read",
            "memory:write",
            "actions:create",
            "actions:read",
        },
    ),
    "raj": UserContext(
        user_id="raj",
        company_id="novatech",
        graph_name="novatech",
        permissions={
            "graph:read",
            "memory:read",
            "actions:read",
        },
    ),
}


def get_current_user(
    x_user_id: str = Header(default="suman"),
) -> UserContext:

    user = DEMO_USERS.get(x_user_id.lower())

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Unknown user.",
        )

    return user


def require_permission(
    user: UserContext,
    permission: str,
) -> None:

    if permission not in user.permissions:
        raise HTTPException(
            status_code=403,
            detail=f"Missing permission: {permission}",
        )